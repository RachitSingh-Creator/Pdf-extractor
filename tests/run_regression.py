import json
import sys
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "regression_fixtures.json"
UPLOAD_URL = "http://127.0.0.1:8000/upload"


def upload_pdf(pdf_path: Path):
    boundary = "----PdfConverterRegressionBoundary"
    data = pdf_path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{pdf_path.name}"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8") + data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = request.Request(
        UPLOAD_URL,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with request.urlopen(req, timeout=900) as response:
        return json.loads(response.read().decode("utf-8"))


def row_contains_all(row, fragments):
    joined = " ".join(str(cell) for cell in row)
    return all(fragment in joined for fragment in fragments)


def check_expectation(result, expectation):
    page = next((entry for entry in result.get("pages", []) if entry.get("page_number") == expectation["page"]), None)
    if page is None:
        return False, f"missing page {expectation['page']}"

    table_index = expectation["table"] - 1
    tables = page.get("tables", [])
    if table_index >= len(tables):
        return False, f"missing table {expectation['table']} on page {expectation['page']}"

    table = tables[table_index]
    rows = table.get("rows", table)
    if not rows:
        return False, f"table {expectation['table']} on page {expectation['page']} is empty"

    if "column_count" in expectation and table.get("column_count") != expectation["column_count"]:
        return False, f"expected column_count={expectation['column_count']} got {table.get('column_count')}"

    header = rows[0]
    if "header_row" in expectation and header != expectation["header_row"]:
        return False, f"expected header {expectation['header_row']} got {header}"

    if "header_row_contains" in expectation:
        joined = " ".join(str(cell) for cell in header)
        missing = [fragment for fragment in expectation["header_row_contains"] if fragment not in joined]
        if missing:
            return False, f"header missing fragments {missing}"

    if "contains_row_fragment" in expectation:
        found = any(row_contains_all(row, expectation["contains_row_fragment"]) for row in rows)
        if not found:
            return False, f"missing row containing fragments {expectation['contains_row_fragment']}"

    return True, "ok"


def main():
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures = []

    for file_entry in fixtures["files"]:
        pdf_path = ROOT / file_entry["pdf"]
        result = upload_pdf(pdf_path)
        for expectation in file_entry["expectations"]:
            ok, message = check_expectation(result, expectation)
            label = f"{pdf_path.name} page {expectation['page']} table {expectation['table']}"
            if ok:
                print(f"PASS {label}")
            else:
                print(f"FAIL {label}: {message}")
                failures.append(label)

    if failures:
        print(f"\nRegression failures: {len(failures)}")
        sys.exit(1)

    print("\nAll regression checks passed.")


if __name__ == "__main__":
    main()
