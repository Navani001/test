
import fitz
import indra_ocr
import tempfile
from pathlib import Path

def pdf_to_ocr(pdf_path, dpi=300, threads=4):
    conv = indra_ocr.load(threads=threads)
    scale = dpi / 72

    with fitz.open(pdf_path) as pdf:
        for page_num, pdf_page in enumerate(pdf, start=1):
            pix = pdf_page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                alpha=False
            )

            # Temporary image file; automatically removed
            with tempfile.NamedTemporaryFile(suffix=".png") as image_file:
                pix.save(image_file.name)

                # Send image path directly to Indra
                result = conv.convert(image_file.name)

                print(f"Page {page_num}")
                print(result)

pdf_to_ocr("input.pdf", dpi=300)
