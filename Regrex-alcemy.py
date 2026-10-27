
import fitz
import pytesseract
from PIL import Image
from io import BytesIO


def detect_pdf_orientation(pdf_path, dpi=100):
    results = []

    with fitz.open(pdf_path) as doc:
        for page_no, page in enumerate(doc):
            # Render at low resolution for speed
            pix = page.get_pixmap(
                dpi=dpi,
                colorspace=fitz.csGRAY,
                alpha=False
            )

            image = Image.open(
                BytesIO(pix.tobytes("png"))
            )

            try:
                osd = pytesseract.image_to_osd(
                    image,
                    config="--psm 0"
                )

                rotation = int(
                    next(
                        line.split(":")[1].strip()
                        for line in osd.splitlines()
                        if line.startswith("Rotate:")
                    )
                )

                results.append({
                    "page": page_no + 1,
                    "rotation": rotation
                })

            except Exception as e:
                results.append({
                    "page": page_no + 1,
                    "rotation": None,
                    "error": str(e)
                })

    return results


for result in detect_pdf_orientation("input.pdf"):
    print(result)
