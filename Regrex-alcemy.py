import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import re


# ============================================================
# CONFIG
# ============================================================

CSV_FILE = "parse.csv"

# Change this to the row/page you want to inspect
ROW_INDEX = 0

# Size of visualization
FIG_WIDTH = 12
FIG_HEIGHT = 16


# ============================================================
# PARSE COORDINATES
# ============================================================

def parse_coordinates(value):
    """
    Parse:

        x1,y1,x2,y2|x1,y1,x2,y2|...

    into:

        [
            (x1, y1, x2, y2),
            ...
        ]
    """

    if pd.isna(value):
        return []

    value = str(value).strip()

    if not value:
        return []

    boxes = []

    for part in value.split("|"):

        numbers = re.findall(
            r"-?\d+(?:\.\d+)?",
            part
        )

        if len(numbers) < 4:
            continue

        x1, y1, x2, y2 = map(
            float,
            numbers[:4]
        )

        boxes.append(
            (x1, y1, x2, y2)
        )

    return boxes


# ============================================================
# GET WORDS
# ============================================================

def extract_words(content):

    if pd.isna(content):
        return []

    content = str(content)

    content = content.replace(
        "\\n",
        "\n"
    )

    return re.findall(
        r"\S+",
        content
    )


# ============================================================
# WORD → LINE OVERLAP
# ============================================================

def vertical_overlap(word, line):

    wx1, wy1, wx2, wy2 = word
    lx1, ly1, lx2, ly2 = line

    overlap_top = max(
        wy1,
        ly1
    )

    overlap_bottom = min(
        wy2,
        ly2
    )

    overlap = max(
        0,
        overlap_bottom - overlap_top
    )

    word_height = wy2 - wy1

    if word_height <= 0:
        return 0

    return overlap / word_height


# ============================================================
# FIND LINE FOR WORD
# ============================================================

def find_word_line(word, line_boxes):

    best_line = None
    best_overlap = 0

    for line_index, line in enumerate(line_boxes):

        overlap = vertical_overlap(
            word,
            line
        )

        if overlap > best_overlap:

            best_overlap = overlap
            best_line = line_index

    # Require at least 50% vertical overlap
    if best_overlap >= 0.5:
        return best_line

    return None


# ============================================================
# VISUALIZE
# ============================================================

def visualize(row):

    word_boxes = parse_coordinates(
        row["word_coord"]
    )

    line_boxes = parse_coordinates(
        row["line_coord"]
    )

    words = extract_words(
        row["content"]
    )

    print()
    print("=" * 70)

    print(
        f"File : {row['file_name']}"
    )

    print(
        f"Page : {row['page']}"
    )

    print(
        f"Words: {len(word_boxes)}"
    )

    print(
        f"Lines: {len(line_boxes)}"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Find line for every word
    # --------------------------------------------------------

    line_words = {
        i: []
        for i in range(len(line_boxes))
    }

    unassigned_words = []

    for word_index, word_box in enumerate(word_boxes):

        line_index = find_word_line(
            word_box,
            line_boxes
        )

        if line_index is None:

            unassigned_words.append(
                word_index
            )

        else:

            line_words[line_index].append(
                word_index
            )

    # --------------------------------------------------------
    # Print relationship in terminal
    # --------------------------------------------------------

    print("\nWORD → LINE MAPPING\n")

    for line_index in range(
        len(line_boxes)
    ):

        indexes = line_words[
            line_index
        ]

        words_in_line = []

        for index in indexes:

            if index < len(words):
                words_in_line.append(
                    words[index]
                )
            else:
                words_in_line.append(
                    f"W{index}"
                )

        print(
            f"Line {line_index}: "
            f"{indexes}"
        )

        print(
            f"          {' '.join(words_in_line)}"
        )

    if unassigned_words:

        print(
            "\nWords not assigned to a line:",
            unassigned_words
        )

    # --------------------------------------------------------
    # Create plot
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(
            FIG_WIDTH,
            FIG_HEIGHT
        )
    )

    # --------------------------------------------------------
    # Draw line boxes
    # --------------------------------------------------------

    for line_index, box in enumerate(
        line_boxes
    ):

        x1, y1, x2, y2 = box

        width = x2 - x1
        height = y2 - y1

        rect = patches.Rectangle(
            (x1, y1),
            width,
            height,
            fill=False,
            edgecolor="blue",
            linewidth=2.5
        )

        ax.add_patch(rect)

        # Line label
        ax.text(
            x1,
            y1 - 0.005,
            f"L{line_index}",
            fontsize=10,
            fontweight="bold"
        )

    # --------------------------------------------------------
    # Draw word boxes
    # --------------------------------------------------------

    for word_index, box in enumerate(
        word_boxes
    ):

        x1, y1, x2, y2 = box

        width = x2 - x1
        height = y2 - y1

        # Check whether assigned to a line
        line_index = find_word_line(
            box,
            line_boxes
        )

        rect = patches.Rectangle(
            (x1, y1),
            width,
            height,
            fill=False,
            edgecolor="red",
            linewidth=1
        )

        ax.add_patch(rect)

        # Word text
        if word_index < len(words):

            word = words[word_index]

            # Keep labels readable
            if len(word) > 20:
                word = word[:17] + "..."

        else:

            word = f"W{word_index}"

        # Label
        label = f"W{word_index}: {word}"

        ax.text(
            x1,
            y1 + height / 2,
            label,
            fontsize=7,
            verticalalignment="center"
        )

    # --------------------------------------------------------
    # Page configuration
    # --------------------------------------------------------

    ax.set_xlim(
        0,
        1
    )

    ax.set_ylim(
        1,
        0
    )

    ax.set_aspect(
        "equal"
    )

    ax.set_xlabel(
        "Normalized X"
    )

    ax.set_ylabel(
        "Normalized Y"
    )

    ax.set_title(
        f"OCR Coordinate Analysis\n"
        f"Page {row['page']} | "
        f"Words: {len(word_boxes)} | "
        f"Lines: {len(line_boxes)}"
    )

    ax.grid(
        True,
        alpha=0.2
    )

    plt.tight_layout()

    # IMPORTANT:
    # Only display. Nothing is saved.
    plt.show()


# ============================================================
# MAIN
# ============================================================

df = pd.read_csv(
    CSV_FILE
)

if ROW_INDEX >= len(df):

    raise IndexError(
        f"ROW_INDEX {ROW_INDEX} is outside "
        f"CSV. Total rows: {len(df)}"
    )

row = df.iloc[
    ROW_INDEX
]

visualize(
    row
)
