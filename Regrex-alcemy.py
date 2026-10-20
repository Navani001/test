import fitz
import cv2
import numpy as np
import indra_ocr


def pdf_to_ocr(pdf_path, dpi=200, threads=4):
    conv = indra_ocr.load(threads=threads)
    scale = dpi / 72

    with fitz.open(pdf_path) as pdf:
        for page_num, pdf_page in enumerate(pdf, start=1):

            # Render PDF page directly into memory
            pix = pdf_page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                alpha=False
            )

            # Convert pixel buffer to NumPy array (no image file saved)
            image = np.frombuffer(
                pix.samples, dtype=np.uint8
            ).reshape(pix.height, pix.width, pix.n)

            # Convert RGB to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Run Indra OCR on the in-memory image
            result = conv.ocr(gray)

            print(f"\n--- Page {page_num} ---")
            print(result.markdown)


pdf_to_ocr("input.pdf", dpi=200, threads=4)
