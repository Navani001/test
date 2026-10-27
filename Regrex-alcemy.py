
import os
import fitz
import indra_ocr

from file import append_to_json_file


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Folder newly created at path: {path}")
    else:
        print(f"Folder already exists at path: {path}")


def normalize_pdf_orientation(input_path, output_path):
    with fitz.open(input_path) as doc:
        for page_no, page in enumerate(doc):
            if page.rotation != 0:
                print(
                    f"Page {page_no + 1}: "
                    f"{page.rotation} -> 0 degrees"
                )
                page.remove_rotation()
            else:
                print(
                    f"Page {page_no + 1}: "
                    "Already at 0 degrees"
                )

        doc.save(output_path, garbage=4, deflate=True)

    return output_path


# Configuration
PDF_PATH = (
    "/home/nlpdevintern1/ocrResearch/sample-test-pdf/"
    "conflict-pages/test-data-100.pdf"
)

OUT_FOLDER_PATH = (
    "/home/nlpdevintern1/ocrResearch/indra/"
    "indra-data/data/run11/"
)

ensure_folder(OUT_FOLDER_PATH)

FURNITURE = True
DPI = 300
MATH = False
mode = "ocr"

CORRECTED_PDF_PATH = os.path.join(
    OUT_FOLDER_PATH, "corrected_orientation.pdf"
)

OUTPUT_JSON_PATH = os.path.join(
    OUT_FOLDER_PATH,
    f"extraction-furniture-{FURNITURE}"
    f"-DPI-{DPI}-MATH-{MATH}.json"
)

# Step 1: Normalize PDF rotation metadata
normalize_pdf_orientation(
    PDF_PATH,
    CORRECTED_PDF_PATH
)

# Step 2: Initialize Indra OCR
conv = indra_ocr.load(
    threads=4,
    furniture=FURNITURE,
    dpi=DPI,
    mode=mode,
    image_ocr=True
)

# Step 3: Extract and save OCR results
for page_no, page in enumerate(
    conv.convert(CORRECTED_PDF_PATH)
):
    print(f"Processing page {page_no + 1}")

    append_to_json_file(
        OUTPUT_JSON_PATH,
        {
            "page_no": page_no,
            "file_path": PDF_PATH,
            "file_name": os.path.basename(PDF_PATH),
            "time_ms": page.timings["total_ms"],
            "text": str(page.text),
            "lines": str(page.lines),
            "markdown": page.markdown,
            "blocks": page.blocks,
            "note": page.note,
        }
    )

print("OCR extraction completed.")
print(f"Results saved to: {OUTPUT_JSON_PATH}")
