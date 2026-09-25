import pandas as pd
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import io


# ============================================================
# CONFIG
# ============================================================

PARQUET_FILE = "parse.parquet"
PDF_FILE = "your.pdf"

ROW_INDEX = 0

PAGE_COLUMN = "page"
WORD_COORD_COLUMN = "word_coord"
LINE_COORD_COLUMN = "line_coord"


# ============================================================
# PARSE COORDINATES
# ============================================================

def parse_coordinates(value):
    """
    Coordinate format:

        x1,y1,x2,y2|x1,y1,x2,y2|...

    Example:

        0.069413,0.133669,0.112734,0.227936|
        0.582439,0.638174,0.630340,0.698704
    """

    if pd.isna(value):
        return []

    value = str(value).strip()

    if not value:
        return []

    coordinates = []

    for item in value.split("|"):

        item = item.strip()

        if not item:
            continue

        try:

            values = [
                float(x.strip())
                for x in item.split(",")
            ]

            if len(values) != 4:
                print(
                    "Skipping invalid coordinate:",
                    item
                )
                continue

            x1, y1, x2, y2 = values

            coordinates.append(
                (x1, y1, x2, y2)
            )

        except ValueError:

            print(
                "Could not parse:",
                item
            )

    return coordinates


# ============================================================
# DRAW BOX
# ============================================================

def draw_box(
    ax,
    coordinate,
    image_width,
    image_height,
    edge_color,
    linewidth,
    label=None
):
    """
    Coordinate format:

        x1,y1,x2,y2

    Coordinates are normalized between 0 and 1.
    """

    x1, y1, x2, y2 = coordinate

    # --------------------------------------------------------
    # Convert normalized coordinates to image coordinates
    # --------------------------------------------------------

    x1 = x1 * image_width
    y1 = y1 * image_height

    x2 = x2 * image_width
    y2 = y2 * image_height

    # --------------------------------------------------------
    # Width and height
    # --------------------------------------------------------

    width = x2 - x1
    height = y2 - y1

    # --------------------------------------------------------
    # Draw rectangle
    # --------------------------------------------------------

    rectangle = patches.Rectangle(
        (x1, y1),
        width,
        height,
        linewidth=linewidth,
        edgecolor=edge_color,
        facecolor="none"
    )

    ax.add_patch(rectangle)

    # --------------------------------------------------------
    # Label
    # --------------------------------------------------------

    if label is not None:

        ax.text(
            x1,
            max(0, y1 - 2),
            label,
            fontsize=7,
            color=edge_color,
            backgroundcolor="white"
        )


# ============================================================
# MAIN
# ============================================================

def visualize_row(
    parquet_file,
    pdf_file,
    row_index=0
):

    # ========================================================
    # 1. READ PARQUET
    # ========================================================

    df = pd.read_parquet(
        parquet_file
    )

    print(
        "Total parquet rows:",
        len(df)
    )

    # Select ONE row
    row = df.iloc[row_index]

    print(
        "\nSelected row:",
        row_index
    )

    # ========================================================
    # 2. GET PAGE NUMBER
    # ========================================================

    page_number = int(
        row[PAGE_COLUMN]
    )

    print(
        "PDF page:",
        page_number
    )

    # ========================================================
    # 3. GET WORD COORDINATES
    # ========================================================

    word_coordinates = parse_coordinates(
        row[WORD_COORD_COLUMN]
    )

    # ========================================================
    # 4. GET LINE COORDINATES
    # ========================================================

    line_coordinates = parse_coordinates(
        row[LINE_COORD_COLUMN]
    )

    print(
        "Word boxes:",
        len(word_coordinates)
    )

    print(
        "Line boxes:",
        len(line_coordinates)
    )

    # ========================================================
    # 5. OPEN PDF
    # ========================================================

    pdf = fitz.open(
        pdf_file
    )

    if page_number < 1 or page_number > len(pdf):

        raise ValueError(
            f"Page {page_number} does not exist. "
            f"PDF contains {len(pdf)} pages."
        )

    # PDF pages are zero-indexed
    page = pdf[
        page_number - 1
    ]

    # ========================================================
    # 6. GET PDF PAGE SIZE
    # ========================================================

    pdf_width = page.rect.width
    pdf_height = page.rect.height

    print(
        f"PDF page size: "
        f"{pdf_width:.2f} x "
        f"{pdf_height:.2f} points"
    )

    # ========================================================
    # 7. RENDER PAGE
    # ========================================================

    zoom = 2

    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(
            zoom,
            zoom
        ),
        alpha=False
    )

    image = Image.open(
        io.BytesIO(
            pixmap.tobytes("png")
        )
    )

    image_width, image_height = image.size

    print(
        f"Rendered image size: "
        f"{image_width} x "
        f"{image_height}"
    )

    # ========================================================
    # 8. CREATE FIGURE
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(14, 18)
    )

    ax.imshow(image)

    # ========================================================
    # 9. DRAW LINE BOXES
    # ========================================================

    for index, coordinate in enumerate(
        line_coordinates,
        start=1
    ):

        draw_box(
            ax=ax,
            coordinate=coordinate,
            image_width=image_width,
            image_height=image_height,
            edge_color="blue",
            linewidth=2,
            label=f"L{index}"
        )

    # ========================================================
    # 10. DRAW WORD BOXES
    # ========================================================

    for index, coordinate in enumerate(
        word_coordinates,
        start=1
    ):

        draw_box(
            ax=ax,
            coordinate=coordinate,
            image_width=image_width,
            image_height=image_height,
            edge_color="red",
            linewidth=1,
            label=f"W{index}"
        )

    # ========================================================
    # 11. DISPLAY
    # ========================================================

    ax.set_xlim(
        0,
        image_width
    )

    ax.set_ylim(
        image_height,
        0
    )

    ax.axis("off")

    ax.set_title(
        f"PDF Page {page_number} | "
        f"Parquet Row {row_index}\n"
        f"Words: {len(word_coordinates)} | "
        f"Lines: {len(line_coordinates)}"
    )

    plt.tight_layout()

    plt.show()

    # ========================================================
    # 12. CLOSE PDF
    # ========================================================

    pdf.close()


# ============================================================
# RUN
# ============================================================

visualize_row(
    parquet_file=PARQUET_FILE,
    pdf_file=PDF_FILE,
    row_index=ROW_INDEX
)
