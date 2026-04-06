"""
FastAPI backend for PDF Table Extraction using PaddleOCR
"""
import numpy as np
from pathlib import Path
from statistics import median
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openpyxl import Workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import PatternFill, Alignment, Font
import tempfile
import shutil
import traceback
import threading
import re

# PDF and image processing
from pdf2image import convert_from_path

# PaddleOCR
OCR_IMPORT_ERROR: Optional[str] = None
OCR_INIT_ERROR: Optional[str] = None

try:
    from paddleocr import PaddleOCR
except ImportError as e:
    OCR_IMPORT_ERROR = f"{type(e).__name__}: {e}"
    print(f"Warning: Failed to import PaddleOCR: {OCR_IMPORT_ERROR}")
    PaddleOCR = None

# Initialize FastAPI app
app = FastAPI(title="PDF Table Extractor")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize PaddleOCR
ocr = None
OCR_INIT_STARTED = False
ocr_lock = threading.Lock()


def get_ocr():
    """
    Lazily initialize PaddleOCR so the web server can start immediately even if
    model downloads take time on first use.
    """
    global ocr, OCR_INIT_ERROR, OCR_INIT_STARTED

    if ocr is not None:
        return ocr

    if PaddleOCR is None:
        return None

    with ocr_lock:
        if ocr is not None:
            return ocr

        OCR_INIT_STARTED = True
        OCR_INIT_ERROR = None
        try:
            ocr = PaddleOCR(use_angle_cls=True, lang='en')
        except Exception as e:
            OCR_INIT_ERROR = f"{type(e).__name__}: {e}"
            print(f"Error initializing PaddleOCR: {OCR_INIT_ERROR}")
            traceback.print_exc()
            ocr = None

    return ocr


class TableDetector:
    """
    Detects and extracts tables from OCR results using clustering heuristic.
    Groups OCR results into rows/columns using Y-axis clustering and X-axis sorting.
    """
    
    def __init__(self, y_threshold=15, x_threshold=10, table_gap_multiplier=2.4):
        """
        Args:
            y_threshold: Vertical distance threshold for same row
            x_threshold: Horizontal distance threshold (not critical, used for spacing)
        """
        self.y_threshold = y_threshold
        self.x_threshold = x_threshold
        self.table_gap_multiplier = table_gap_multiplier

    def _extract_items(self, ocr_result):
        items = []
        for item in ocr_result:
            bbox, (text, confidence) = item
            text = text.strip()
            if not text:
                continue

            y_coords = [point[1] for point in bbox]
            x_coords = [point[0] for point in bbox]

            items.append({
                "text": text,
                "center_y": (min(y_coords) + max(y_coords)) / 2,
                "center_x": (min(x_coords) + max(x_coords)) / 2,
                "min_y": min(y_coords),
                "max_y": max(y_coords),
                "x": min(x_coords),
                "max_x": max(x_coords),
                "bbox": bbox,
                "confidence": confidence,
                "height": max(y_coords) - min(y_coords),
                "width": max(x_coords) - min(x_coords),
            })
        return items

    def _cluster_rows(self, items):
        items_sorted_by_y = sorted(items, key=lambda item: item["center_y"])
        rows = []
        current_row = [items_sorted_by_y[0]]

        for item in items_sorted_by_y[1:]:
            if abs(item["center_y"] - current_row[0]["center_y"]) <= self.y_threshold:
                current_row.append(item)
            else:
                rows.append(self._build_row(current_row))
                current_row = [item]

        rows.append(self._build_row(current_row))
        return rows

    def _build_row(self, row_items):
        row_items.sort(key=lambda item: item["x"])
        return {
            "cells": [item["text"] for item in row_items],
            "items": row_items,
            "item_count": len(row_items),
            "min_y": min(item["min_y"] for item in row_items),
            "max_y": max(item["max_y"] for item in row_items),
            "height": max(item["max_y"] for item in row_items) - min(item["min_y"] for item in row_items),
            "min_x": min(item["x"] for item in row_items),
            "max_x": max(item["max_x"] for item in row_items),
        }

    def _table_gap_threshold(self, rows):
        heights = [row["height"] for row in rows if row["height"] > 0]
        base_height = median(heights) if heights else self.y_threshold
        return max(self.y_threshold * 2, base_height * self.table_gap_multiplier)

    def _rows_belong_to_same_table(self, previous_row, current_row, gap_threshold):
        gap = current_row["min_y"] - previous_row["max_y"]
        horizontal_overlap = min(previous_row["max_x"], current_row["max_x"]) - max(previous_row["min_x"], current_row["min_x"])

        if gap <= gap_threshold:
            return True

        if horizontal_overlap > 0 and gap <= gap_threshold * 1.35:
            return True

        return False

    def _is_probable_table(self, table_rows):
        if len(table_rows) < 2:
            return False

        max_columns = max(row["item_count"] for row in table_rows)
        multi_cell_rows = sum(1 for row in table_rows if row["item_count"] >= 2)

        return max_columns >= 2 and multi_cell_rows >= 2

    def _split_tables(self, rows):
        if not rows:
            return []

        gap_threshold = self._table_gap_threshold(rows)
        table_groups = []
        current_group = [rows[0]]

        for row in rows[1:]:
            previous_row = current_group[-1]
            if self._rows_belong_to_same_table(previous_row, row, gap_threshold):
                current_group.append(row)
            else:
                if self._is_probable_table(current_group):
                    table_groups.append(current_group)
                current_group = [row]

        if self._is_probable_table(current_group):
            table_groups.append(current_group)

        return table_groups

    def _trim_non_table_rows(self, rows):
        trimmed_rows = list(rows)

        while len(trimmed_rows) > 1 and trimmed_rows[0]["item_count"] <= 1:
            later_multi_cell_rows = any(row["item_count"] >= 2 for row in trimmed_rows[1:])
            if not later_multi_cell_rows:
                break
            trimmed_rows.pop(0)

        while len(trimmed_rows) > 1 and trimmed_rows[-1]["item_count"] <= 1:
            earlier_multi_cell_rows = any(row["item_count"] >= 2 for row in trimmed_rows[:-1])
            if not earlier_multi_cell_rows:
                break
            trimmed_rows.pop()

        return trimmed_rows

    def _cluster_positions(self, values, threshold):
        if not values:
            return []

        sorted_values = sorted(values)
        clusters = [[sorted_values[0]]]
        for value in sorted_values[1:]:
            if abs(value - median(clusters[-1])) <= threshold:
                clusters[-1].append(value)
            else:
                clusters.append([value])
        return [median(cluster) for cluster in clusters]

    def _infer_column_centers(self, rows):
        items = [item for row in rows for item in row["items"]]
        if not items:
            return []

        widths = [item["width"] for item in items if item["width"] > 0]
        median_width = median(widths) if widths else 0
        threshold = max(self.x_threshold * 3, median_width * 0.7 if median_width else 0)
        centers = [item["center_x"] for item in items]
        return self._cluster_positions(centers, threshold)

    def _find_column_index(self, item, column_centers, used_indexes):
        ranked_indexes = sorted(
            range(len(column_centers)),
            key=lambda idx: abs(column_centers[idx] - item["center_x"])
        )
        for idx in ranked_indexes:
            if idx not in used_indexes:
                return idx
        return ranked_indexes[0] if ranked_indexes else 0

    def _build_matrix(self, rows):
        column_centers = self._infer_column_centers(rows)
        if not column_centers:
            return [], []

        matrix_rows = []
        merges = []

        for row_idx, row in enumerate(rows):
            values = [""] * len(column_centers)
            used_indexes = set()
            row_spans = []

            for item in row["items"]:
                column_idx = self._find_column_index(item, column_centers, used_indexes)
                values[column_idx] = item["text"]
                used_indexes.add(column_idx)

                covered_indexes = [
                    idx for idx, center in enumerate(column_centers)
                    if item["x"] - self.x_threshold <= center <= item["max_x"] + self.x_threshold
                ]
                if len(covered_indexes) >= 2:
                    row_spans.append((min(covered_indexes), max(covered_indexes)))

            matrix_rows.append(values)
            for start_idx, end_idx in row_spans:
                merges.append({
                    "row": row_idx,
                    "start_col": start_idx,
                    "end_col": end_idx,
                })

        non_empty_columns = [
            col_idx for col_idx in range(len(column_centers))
            if any(row[col_idx].strip() for row in matrix_rows)
        ]

        if not non_empty_columns:
            return [], []

        index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(non_empty_columns)}
        normalized_rows = [
            [row[col_idx] for col_idx in non_empty_columns]
            for row in matrix_rows
        ]
        normalized_merges = []
        for merge in merges:
            covered = [
                index_map[idx]
                for idx in range(merge["start_col"], merge["end_col"] + 1)
                if idx in index_map
            ]
            if len(covered) >= 2:
                normalized_merges.append({
                    "row": merge["row"],
                    "start_col": min(covered),
                    "end_col": max(covered),
                })

        return normalized_rows, normalized_merges

    def _looks_numeric(self, value):
        compact = value.replace(",", "").replace("%", "").replace("(", "").replace(")", "").strip()
        return bool(compact) and bool(re.fullmatch(r"[-+]?\d+(?:\.\d+)?", compact))

    def _infer_header_row_count(self, matrix_rows):
        if not matrix_rows:
            return 0

        for row_idx, row in enumerate(matrix_rows):
            non_empty_cells = [cell.strip() for cell in row if cell and cell.strip()]
            if not non_empty_cells:
                continue

            numeric_cells = sum(1 for cell in non_empty_cells if self._looks_numeric(cell))
            first_cell = non_empty_cells[0]
            starts_like_data = first_cell.isdigit() or numeric_cells >= max(2, len(non_empty_cells) // 2)

            if starts_like_data:
                return max(1, row_idx)

        return min(len(matrix_rows), 2)

    def _normalize_table(self, rows):
        trimmed_rows = self._trim_non_table_rows(rows)
        if not trimmed_rows:
            return None

        matrix_rows, merges = self._build_matrix(trimmed_rows)
        if not matrix_rows:
            return None

        header_row_count = self._infer_header_row_count(matrix_rows)
        return {
            "rows": matrix_rows,
            "header_row_count": header_row_count,
            "merges": merges,
        }
    
    def detect_tables(self, ocr_result):
        """
        Extract tables from OCR result.
        
        Args:
            ocr_result: List of [bbox, text, confidence] from PaddleOCR
            
        Returns:
            List of tables, each table is list of rows, each row is list of cell strings
        """
        if not ocr_result:
            return []

        items = self._extract_items(ocr_result)
        if not items:
            return []

        rows = self._cluster_rows(items)
        table_groups = self._split_tables(rows)
        normalized_tables = []
        for table_rows in table_groups:
            table = self._normalize_table(table_rows)
            if table:
                normalized_tables.append(table)

        return normalized_tables


def normalize_ocr_result(ocr_result):
    """
    PaddleOCR returns a nested list per input image. For a single image we want
    the list of text boxes for that page.
    """
    if not ocr_result:
        return []

    if (
        isinstance(ocr_result, list)
        and ocr_result
        and isinstance(ocr_result[0], list)
        and ocr_result[0]
        and isinstance(ocr_result[0][0], list)
    ):
        return ocr_result[0]

    return ocr_result


def looks_numeric(value):
    if not isinstance(value, str):
        return isinstance(value, (int, float))

    compact = value.replace(",", "").replace("%", "").replace("(", "").replace(")", "").strip()
    return bool(compact) and bool(re.fullmatch(r"[-+]?\d+(?:\.\d+)?", compact))


@app.get("/")
async def root():
    """Serve the main page"""
    return FileResponse(FRONTEND_DIR / "index.html", media_type="text/html")


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    Extract tables from all pages using PaddleOCR.
    
    Returns JSON with structure:
    {
        "status": "success",
        "pages": [
            {
                "page_number": 1,
                "tables": [
                    [["cell1", "cell2"], ["cell3", "cell4"]]
                ]
            }
        ]
    }
    """
    
    ocr_instance = get_ocr()
    if not ocr_instance:
        detail = OCR_INIT_ERROR or OCR_IMPORT_ERROR or "PaddleOCR not initialized"
        raise HTTPException(status_code=500, detail=detail)
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    temp_dir = None
    try:
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        file_path = Path(temp_dir) / file.filename
        
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Convert PDF pages to images
        images = convert_from_path(str(file_path), dpi=150)
        
        # Process each page
        pages_data = []
        detector = TableDetector(y_threshold=15)
        
        for page_num, image in enumerate(images, 1):
            # Convert PIL Image to numpy array for PaddleOCR
            image_np = np.array(image)
            
            # Run OCR on the page
            ocr_results = ocr_instance.ocr(image_np, cls=True)
            page_ocr = normalize_ocr_result(ocr_results)
            
            # Detect tables from OCR results
            if page_ocr:
                tables = detector.detect_tables(page_ocr)
            else:
                tables = []
            
            pages_data.append({
                "page_number": page_num,
                "tables": tables
            })
        
        return {
            "status": "success",
            "pages": pages_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.post("/download")
async def download_excel(data: dict):
    """
    Convert extracted table JSON to Excel and return as file download.
    
    Expected input:
    {
        "tables": [table1, table2, ...],
        "filename": "output.xlsx" (optional)
    }
    """
    try:
        tables = data.get("tables", [])
        filename = data.get("filename", "extracted_tables.xlsx")
        
        if not tables:
            raise HTTPException(status_code=400, detail="No tables provided")
        
        wb = Workbook()
        default_sheet = wb.active
        header_fill = PatternFill(start_color="C9A84C", end_color="C9A84C", fill_type="solid")
        bold_font = Font(bold=True)

        for table_idx, table_entry in enumerate(tables, 1):
            if isinstance(table_entry, dict):
                table = table_entry.get("rows", [])
                page_number = table_entry.get("page_number")
                table_number = table_entry.get("table_number", table_idx)
                header_row_count = table_entry.get("header_row_count", 1)
                merges = table_entry.get("merges", [])
            else:
                table = table_entry
                page_number = None
                table_number = table_idx
                header_row_count = 1
                merges = []

            if not table:
                continue

            sheet_title = f"P{page_number or 1}_T{table_number}"
            ws = default_sheet if table_idx == 1 else wb.create_sheet()
            ws.title = sheet_title[:31]

            for row_idx, row in enumerate(table):
                for col_idx, cell_value in enumerate(row, 1):
                    cell = ws.cell(row=row_idx + 1, column=col_idx)
                    cell.value = cell_value
                    is_header = row_idx < header_row_count
                    is_numeric = looks_numeric(cell_value)

                    if is_header:
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        cell.fill = header_fill
                        cell.font = bold_font
                    else:
                        cell.alignment = Alignment(
                            horizontal="right" if is_numeric else "left",
                            vertical="center"
                        )

            for merge in merges:
                merge_row = merge["row"] + 1
                start_col = merge["start_col"] + 1
                end_col = merge["end_col"] + 1
                if merge_row <= header_row_count and end_col > start_col:
                    ws.merge_cells(
                        start_row=merge_row,
                        start_column=start_col,
                        end_row=merge_row,
                        end_column=end_col,
                    )

            for column in ws.columns:
                max_length = 0
                first_real_cell = next((cell for cell in column if not isinstance(cell, MergedCell)), None)
                if first_real_cell is None:
                    continue
                column_letter = first_real_cell.column_letter
                for cell in column:
                    if isinstance(cell, MergedCell):
                        continue
                    try:
                        value_length = len(str(cell.value)) if cell.value is not None else 0
                        if value_length > max_length:
                            max_length = value_length
                    except:
                        pass
                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

        if len(wb.sheetnames) > 1 and default_sheet.title == "Sheet" and default_sheet.max_row == 1 and default_sheet["A1"].value is None:
            wb.remove(default_sheet)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        wb.save(temp_file.name)
        temp_file.close()
        
        return FileResponse(
            temp_file.name,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if ocr:
        ocr_status = "initialized"
    elif OCR_INIT_STARTED:
        ocr_status = "not_initialized"
    else:
        ocr_status = "not_initialized"

    response = {
        "status": "ok",
        "ocr_status": ocr_status
    }
    if OCR_IMPORT_ERROR:
        response["ocr_import_error"] = OCR_IMPORT_ERROR
    if OCR_INIT_ERROR:
        response["ocr_init_error"] = OCR_INIT_ERROR
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
