
import fitz
import cv2
import numpy as np


def detect_page_orientation(page, dpi=100):
    # Render the page at low resolution for speed
    pix = page.get_pixmap(
        dpi=dpi,
        colorspace=fitz.csGRAY,
        alpha=False
    )

    image = np.frombuffer(
        pix.samples, dtype=np.uint8
    ).reshape(pix.height, pix.width)

    best_angle = 0
    best_score = -1

    for angle in (0, 90, 180, 270):
        rotated = np.rot90(image, k=angle // 90)

        binary = cv2.threshold(
            rotated, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        # Emphasize horizontal text lines
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (15, 1)
        )
        lines = cv2.morphologyEx(
            binary, cv2.MORPH_CLOSE, kernel
        )

        projection = np.sum(lines > 0, axis=1)
        score = np.sum(projection.astype(np.float64) ** 2)

        if score > best_score:
            best_score = score
            best_angle = angle

    return best_angle


pdf_path = "input.pdf"

with fitz.open(pdf_path) as doc:
    for i, page in enumerate(doc):
        angle = detect_page_orientation(page)
        print(
            f"Page {i + 1}: "
            f"metadata={page.rotation}°, "
            f"detected correction={angle}°"
        )
