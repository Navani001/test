import re
import csv
from rapidfuzz.fuzz import ratio


# ---------------------------------------------------------
# 1. TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize_text(text):
    """
    Normalize OCR text so that differences in:
    - case
    - whitespace
    - newlines
    - repeated spaces
    don't affect comparison.
    """
    text = str(text).lower()

    # Replace newlines/tabs with spaces
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


# ---------------------------------------------------------
# 2. BBOX FUNCTIONS
# ---------------------------------------------------------

def bbox_area(box):
    x1, y1, x2, y2 = box

    width = max(0, x2 - x1)
    height = max(0, y2 - y1)

    return width * height


def intersection(box1, box2):
    """
    Returns intersection rectangle.
    """

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    if x2 <= x1 or y2 <= y1:
        return None

    return [x1, y1, x2, y2]


def intersection_area(box1, box2):

    inter = intersection(box1, box2)

    if inter is None:
        return 0

    return bbox_area(inter)


def containment(textract_box, baidu_box):
    """
    Percentage of the Textract box covered by Baidu box.

    This is NOT IoU.

    If Textract box is completely inside Baidu box:
        containment = 1.0
    """

    textract_area = bbox_area(textract_box)

    if textract_area == 0:
        return 0

    inter_area = intersection_area(
        textract_box,
        baidu_box
    )

    return inter_area / textract_area


# ---------------------------------------------------------
# 3. TEXT MATCHING
# ---------------------------------------------------------

def text_similarity(textract_text, baidu_text):
    """
    Basic fuzzy similarity.
    """

    a = normalize_text(textract_text)
    b = normalize_text(baidu_text)

    if not a or not b:
        return 0

    return ratio(a, b) / 100.0


def text_is_contained(textract_text, baidu_text):
    """
    Checks whether Textract's text occurs inside
    the Baidu block.

    This is particularly useful because:

        Textract = individual line
        Baidu    = complete paragraph
    """

    a = normalize_text(textract_text)
    b = normalize_text(baidu_text)

    return a in b


# ---------------------------------------------------------
# 4. FIND BEST BAIDU MATCH
# ---------------------------------------------------------

def find_best_match(
    textract_item,
    baidu_items,
    min_spatial_coverage=0.80,
    min_text_similarity=0.80
):

    textract_text = textract_item["text"]
    textract_box = textract_item["bbox"]

    candidates = []

    for idx, baidu_item in enumerate(baidu_items):

        baidu_box = baidu_item["bbox"]
        baidu_text = baidu_item["text"]

        # -----------------------------
        # Spatial coverage
        # -----------------------------

        coverage = containment(
            textract_box,
            baidu_box
        )

        if coverage < min_spatial_coverage:
            continue

        # -----------------------------
        # Text containment
        # -----------------------------

        exact_contained = text_is_contained(
            textract_text,
            baidu_text
        )

        # -----------------------------
        # Fuzzy similarity
        # -----------------------------

        similarity = text_similarity(
            textract_text,
            baidu_text
        )

        # If exact text occurs in the larger
        # Baidu paragraph, give it maximum text score.
        if exact_contained:
            similarity = 1.0

        if similarity < min_text_similarity:
            continue

        candidates.append({
            "baidu_index": idx,
            "spatial_coverage": coverage,
            "text_similarity": similarity,
            "text_contained": exact_contained
        })

    if not candidates:
        return None

    # -----------------------------------------------------
    # Select the best candidate.
    #
    # Prioritize text similarity and spatial coverage.
    # -----------------------------------------------------

    candidates.sort(
        key=lambda x: (
            x["text_similarity"],
            x["spatial_coverage"]
        ),
        reverse=True
    )

    return candidates[0]


# ---------------------------------------------------------
# 5. EVALUATE
# ---------------------------------------------------------

def evaluate(textract_items, baidu_items):

    results = []

    matched_count = 0

    total_spatial_coverage = 0
    total_text_similarity = 0

    for textract_index, textract_item in enumerate(textract_items):

        match = find_best_match(
            textract_item,
            baidu_items
        )

        if match:

            matched = True

            matched_count += 1

            total_spatial_coverage += (
                match["spatial_coverage"]
            )

            total_text_similarity += (
                match["text_similarity"]
            )

            results.append({
                "textract_index": textract_index,
                "textract_text": textract_item["text"],
                "textract_bbox": textract_item["bbox"],

                "baidu_index": match["baidu_index"],

                "spatial_coverage":
                    match["spatial_coverage"],

                "text_similarity":
                    match["text_similarity"],

                "text_contained":
                    match["text_contained"],

                "matched": True
            })

        else:

            results.append({
                "textract_index": textract_index,
                "textract_text": textract_item["text"],
                "textract_bbox": textract_item["bbox"],

                "baidu_index": None,

                "spatial_coverage": 0,

                "text_similarity": 0,

                "text_contained": False,

                "matched": False
            })

    total = len(textract_items)

    if total > 0:

        coverage_percentage = (
            matched_count / total
        ) * 100

    else:

        coverage_percentage = 0

    matched_items = [
        r for r in results
        if r["matched"]
    ]

    if matched_items:

        avg_spatial_coverage = (
            sum(
                r["spatial_coverage"]
                for r in matched_items
            )
            / len(matched_items)
        )

        avg_text_similarity = (
            sum(
                r["text_similarity"]
                for r in matched_items
            )
            / len(matched_items)
        )

    else:

        avg_spatial_coverage = 0
        avg_text_similarity = 0

    summary = {

        "textract_items": total,

        "matched_items": matched_count,

        "missing_items":
            total - matched_count,

        "coverage_percentage":
            coverage_percentage,

        "average_spatial_coverage":
            avg_spatial_coverage * 100,

        "average_text_similarity":
            avg_text_similarity * 100
    }

    return summary, results


# ---------------------------------------------------------
# 6. SAVE DETAILS TO CSV
# ---------------------------------------------------------

def save_results_csv(results, filename):

    fieldnames = [
        "textract_index",
        "textract_text",
        "textract_bbox",
        "baidu_index",
        "spatial_coverage",
        "text_similarity",
        "text_contained",
        "matched"
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(results)


# =========================================================
# EXAMPLE
# =========================================================

if __name__ == "__main__":

    textract = [

        {
            "text": "Patient Name: John Smith",
            "bbox": [100, 100, 400, 130]
        },

        {
            "text": "DOB: 01/01/1985",
            "bbox": [100, 140, 300, 170]
        },

        {
            "text": "Address: Chennai",
            "bbox": [100, 180, 300, 210]
        }
    ]

    baidu = [

        {
            "text": """
            Patient Name: John Smith
            DOB: 01/01/1985
            Address: Chennai
            """,

            "bbox": [90, 90, 500, 230]
        }
    ]

    summary, results = evaluate(
        textract,
        baidu
    )

    print("\n========== SUMMARY ==========\n")

    for key, value in summary.items():

        print(
            f"{key}: {value}"
        )

    print("\n========== DETAILS ==========\n")

    for result in results:

        print(result)

    save_results_csv(
        results,
        "ocr_comparison.csv"
    )

    print(
        "\nSaved: ocr_comparison.csv"
    )
