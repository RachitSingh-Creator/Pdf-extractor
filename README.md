# PDF Table Extractor

A full-stack web application that extracts tables from PDF files using PaddleOCR and displays them in an elegant, interactive UI.

## Features

✨ **Smart Table Detection** - Uses PaddleOCR for accurate text detection and clustering heuristics for table extraction
📊 **Multi-page Support** - Processes all pages in a PDF and extracts tables from each
💾 **Easy Exports** - Download extracted tables as Excel (.xlsx) or view in the elegant web interface
📱 **Responsive Design** - Works beautifully on desktop, tablet, and mobile
🎨 **Editorial Aesthetic** - Clean, luxury document-processing design with gold accents and elegant typography

## Tech Stack

**Backend:**
- FastAPI - Modern Python REST API framework
- PaddleOCR - Advanced text detection and recognition
- PaddlePaddle - Deep learning framework
- pdf2image - PDF to image conversion
- pandas & openpyxl - Excel file generation

**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- Responsive design with Flexbox/Grid
- Drag-and-drop file upload
- Real-time table rendering

## Quick Start (Recommended: Docker)

### Prerequisites

- **Docker Desktop** ([download here](https://www.docker.com/products/docker-desktop))
  - Includes both Docker and Docker Compose
  - Works on Windows, macOS, and Linux
  - Simplest setup (no system dependencies needed!)

### Run with Docker - 3 Steps

**Windows (PowerShell):**
```powershell
cd d:\Pdfconverter
.\docker-run.bat
```

**macOS/Linux:**
```bash
cd d:\Pdfconverter
chmod +x docker-run.sh
./docker-run.sh
```

**Or manually with Docker Compose:**
```bash
docker-compose up --build
```

Then open your browser to: **http://localhost:8000**

✅ Done! That's it. No other dependencies needed.

---

## Alternative: Native Installation (Without Docker)

If you prefer native installation without Docker:

### System Requirements

- **Python 3.8+**
- **Poppler** (required for PDF to image conversion)
- **8GB+ RAM** (recommended for PaddleOCR)
- Modern web browser

### Step 1: Install System Dependencies

#### Windows
```powershell
# Using Chocolatey (recommended)
choco install poppler

# OR download from: https://github.com/oschwartz10612/poppler-windows/releases/
# Extract to a folder and add to PATH
```

#### macOS
```bash
brew install poppler
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install poppler-utils
```

### Step 2: Install Application

```bash
cd d:\Pdfconverter
./setup.bat    # Windows
./setup.sh     # macOS/Linux
```

### Step 3: Run the Application

```bash
./run.bat      # Windows
./run.sh       # macOS/Linux
```

Then open your browser to: **http://localhost:8000**

---

## Docker Documentation

For detailed Docker instructions, advanced configurations, and troubleshooting, see [DOCKER.md](DOCKER.md).

**Key Docker Commands:**
```bash
docker-compose up --build          # Start (builds image first time)
docker-compose down                # Stop
docker logs -f pdf-extractor       # View logs
docker exec -it pdf-extractor bash # Open shell inside container
```

## Usage

1. **Upload PDF** - Drag and drop a PDF file onto the upload area, or click to select
2. **Processing** - Wait for the PDF to be processed (spinner will show progress)
3. **View Tables** - Extracted tables will appear with page numbers and table indices
4. **Download** - Click "Download as Excel" on any table to export as .xlsx file
5. **Multiple Tables** - The app automatically detects multiple tables per page

## Project Structure

```
d:\Pdfconverter/
├── backend/
│   └── main.py              # FastAPI server with table extraction logic
├── frontend/
│   └── index.html           # Single-page web application
├── uploads/                 # Temporary storage for uploaded PDFs
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

### POST /upload
Uploads and processes a PDF file.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: PDF file

**Response:**
```json
{
  "status": "success",
  "pages": [
    {
      "page_number": 1,
      "tables": [
        [
          ["Header 1", "Header 2"],
          ["Cell 1", "Cell 2"],
          ["Cell 3", "Cell 4"]
        ]
      ]
    }
  ]
}
```

### POST /download
Converts extracted tables to Excel and returns the file.

**Request:**
```json
{
  "tables": [[[...table data...]]],
  "filename": "output.xlsx"
}
```

**Response:** Binary Excel file

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "ocr_status": "initialized"
}
```

## Configuration

### Adjust Table Detection Sensitivity

Edit `backend/main.py`, line ~105:
```python
detector = TableDetector(y_threshold=15)  # Lower = more rows, Higher = fewer rows
```

### Change Server Port

Edit the last line of `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8080)  # Change 8000 to desired port
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'poppler'"
**Solution:** Install system-level Poppler (see Installation section)

### Issue: "PaddleOCR not initialized"
**Solution:** Check that all dependencies are installed: `pip install -r requirements.txt`

### Issue: "CUDA not found" warning
**Solution:** This is normal. The app uses CPU by default. Ignore or install GPU support if needed.

### Issue: Large PDF takes very long to process
**Solution:** This is expected for large PDFs with many tables. Processing time depends on:
- PDF complexity (large images, many tables)
- System RAM and CPU
- Number of pages

### Issue: Frontend won't load
**Solution:** 
- Check backend is running: `curl http://localhost:8000/health`
- Check browser console for errors (F12)
- Ensure browser supports modern JavaScript (ES6+)

## Performance Tips

1. **Optimize PDFs** - Use smaller DPI PDFs for faster processing
2. **Split Large PDFs** - Process large PDFs in smaller chunks
3. **Use CPU Efficiently** - Close other heavy applications while processing
4. **Increase RAM** - More RAM = faster PaddleOCR performance

## Limitations

- Works best with clear, well-structured tables
- Handwritten text detection is limited
- Very complex nested tables may not extract perfectly
- Maximum recommended PDF size: 100 pages (depends on system)

## Design Details

### Color Palette
- Background: #FAFAF7 (Cream white)
- Text: #1a2744 (Deep navy)
- Accent: #C9A84C (Gold)

### Typography
- Headings: Playfair Display (serif, 700-800 weight)
- Body: DM Sans (sans-serif, 400-600 weight)

### Animations
- Smooth fade-in for tables
- Hover effects on interactive elements
- Spinner animation during processing

## License

This project is provided as-is for educational and commercial use.

## Support & Contributions

For issues or improvements, check:
- Backend logs in terminal
- Browser console (F12) for frontend errors
- Verify PDF format and quality

## Future Enhancements

- [ ] Batch PDF processing
- [ ] Custom table detection parameters UI
- [ ] Column type detection (numeric, date, text)
- [ ] Data validation and cleaning
- [ ] CSV export option
- [ ] PDF annotation/highlighting
- [ ] Database storage for extracted tables
- [ ] API authentication

---

Happy table extracting! 📊✨
