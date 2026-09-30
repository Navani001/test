import re
import html
from rapidfuzz.fuzz import ratio


# ============================================================
# CONFIGURATION
# ============================================================

MIN_SPATIAL_COVERAGE = 0.90
MIN_TEXT_COVERAGE = 0.90

# For fuzzy matching individual words
WORD_SIMILARITY_THRESHOLD = 0.85


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize OCR text for comparison.

    Important:
    HTML/XML tags are replaced with spaces, NOT simply removed.

    Example:

        <td>Name</td><td>John</td>

    becomes:

        name john
    """

    if text is None:
        return ""

    text = str(text)

    # Decode HTML entities
    #
    # &amp;   -> &
    # &lt;    -> <
    # &#39;   -> '
    #
    text = html.unescape(text)

    # Replace HTML/XML tags with spaces
    #
    # <table>
    # <tr>
    # <td>
    # </td>
    #
    # all become spaces.
    text = re.sub(r"<[^>]*>", " ", text)

    # Lowercase
    text = text.lower()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove unnecessary spaces before punctuation
    text = re.sub(r"\s+([,.:;!?])", r"\1", text)

    return text.strip()


# ============================================================
# TABLE DETECTION
# ============================================================

def is_table_content(text):
    """
    Detect whether a Baidu OCR block contains table markup.
    """

    if not text:
        return False

    text = str(text).lower()

    return (
        "<table" in text
        or "</table>" in text
    )


# ============================================================
# BOUNDING BOX FUNCTIONS
# ============================================================

def bbox_area(box):
    """
    box format:

        [x1, y1, x2, y2]
    """

    if not box or len(box) != 4:
        return 0

    x1, y1, x2, y2 = box

    return max(0, x2 - x1) * max(0, y2 - y1)


def intersection_area(box1, box2):
    """
    Calculate intersection area of two bounding boxes.
    """

    if not box1 or not box2:
        return 0

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    if x2 <= x1 or y2 <= y1:
        return 0

    return (x2 - x1) * (y2 - y1)


def textract_coverage(textract_box, baidu_box):
    """
    Calculate how much of the Textract box is covered
    by the Baidu box.

    This is intentionally NOT IoU.

    Example:

        Textract:
        ┌─────────┐
        │         │
        └─────────┘

        Baidu:
        ┌───────────────────────┐
        │   ┌─────────┐         │
        │   │Textract │         │
        │   └─────────┘         │
        └───────────────────────┘

    Result = 1.0 if Textract is completely covered.
    """

    textract_area = bbox_area(textract_box)

    if textract_area == 0:
        return 0.0

    overlap = intersection_area(
        textract_box,
        baidu_box
    )

    return overlap / textract_area


# ============================================================
# TEXT COVERAGE
# ============================================================

def text_coverage(textract_text, baidu_text):
    """
    Calculate how much of Textract's text is represented
    inside the Baidu text.

    Because Baidu can contain a complete paragraph while
    Textract contains individual lines, exact substring
    matching is attempted first.
    """

    textract_text = normalize_text(textract_text)
    baidu_text = normalize_text(baidu_text)

    if not textract_text:
        return 0.0

    if not baidu_text:
        return 0.0

    # --------------------------------------------------------
    # Best case:
    #
    # Entire Textract line exists in Baidu paragraph.
    # --------------------------------------------------------

    if textract_text in baidu_text:
        return 1.0

    # --------------------------------------------------------
    # Token-level fuzzy matching
    # --------------------------------------------------------

    textract_words = textract_text.split()
    baidu_words = baidu_text.split()

    if not textract_words:
        return 0.0

    matched_words = 0

    for textract_word in textract_words:

        best_score = 0.0

        for baidu_word in baidu_words:

            score = ratio(
                textract_word,
                baidu_word
            ) / 100.0

            if score > best_score:
                best_score = score

        if best_score >= WORD_SIMILARITY_THRESHOLD:
            matched_words += 1

    return matched_words / len(textract_words)


# ============================================================
# FIND BEST BAIDU MATCH
# ============================================================

def find_best_match(
    textract_item,
    baidu_data,
    min_spatial=MIN_SPATIAL_COVERAGE,
    min_text=MIN_TEXT_COVERAGE
):
    """
    Find the Baidu block that best represents a Textract item.

    Multiple Textract lines are allowed to match the same
    Baidu block.
    """

    textract_text = textract_item.get(
        "content",
        ""
    )

    textract_box = textract_item.get(
        "coor"
    )

    candidates = []

    for baidu_index, baidu_item in enumerate(baidu_data):

        baidu_text = baidu_item.get(
            "content",
            ""
        )

        baidu_box = baidu_item.get(
            "coor"
        )

        # ----------------------------------------------------
        # Spatial coverage
        # ----------------------------------------------------

        spatial = textract_coverage(
            textract_box,
            baidu_box
        )

        # Completely unrelated spatial region
        if spatial < min_spatial:
            continue

        # ----------------------------------------------------
        # Text coverage
        # ----------------------------------------------------

        text_score = text_coverage(
            textract_text,
            baidu_text
        )

        # ----------------------------------------------------
        # Combined score
        # ----------------------------------------------------

        combined_score = (
            0.6 * text_score
            +
            0.4 * spatial
        )

        candidates.append({
            "baidu_index": baidu_index,
            "spatial_coverage": spatial,
            "text_coverage": text_score,
            "combined_score": combined_score,
        })

    if not candidates:
        return None

    # Best candidate
    candidates.sort(
        key=lambda x: x["combined_score"],
        reverse=True
    )

    best = candidates[0]

    # Final match condition
    best["matched"] = (
        best["spatial_coverage"] >= min_spatial
        and
        best["text_coverage"] >= min_text
    )

    return best


# ============================================================
# COMPLETE EVALUATOR
# ============================================================

def evaluate_ocr(
    textract_data,
    baidu_data
):
    """
    Main evaluation function.

    Input format:

    Textract:
    [
        {
            "content": "...",
            "coor": [x1, y1, x2, y2]
        }
    ]

    Baidu:
    [
        {
            "content": "...",
            "coor": [x1, y1, x2, y2]
        }
    ]
    """

    results = []

    for textract_index, textract_item in enumerate(
        textract_data
    ):

        content = textract_item.get(
            "content",
            ""
        )

        # Ignore empty OCR elements
        if not normalize_text(content):
            continue

        # Ignore explicit NO TEXT
        if normalize_text(content) == "no text":
            continue

        match = find_best_match(
            textract_item,
            baidu_data
        )

        # ----------------------------------------------------
        # No match
        # ----------------------------------------------------

        if match is None:

            results.append({

                "textract_index":
                    textract_index,

                "textract_content":
                    content,

                "textract_coor":
                    textract_item.get("coor"),

                "baidu_index":
                    None,

                "baidu_content":
                    None,

                "baidu_coor":
                    None,

                "baidu_is_table":
                    False,

                "spatial_coverage":
                    0.0,

                "text_coverage":
                    0.0,

                "combined_score":
                    0.0,

                "matched":
                    False
            })

            continue

        # ----------------------------------------------------
        # Matched Baidu item
        # ----------------------------------------------------

        baidu_index = match["baidu_index"]

        matched_baidu = baidu_data[
            baidu_index
        ]

        results.append({

            "textract_index":
                textract_index,

            "textract_content":
                content,

            "textract_coor":
                textract_item.get("coor"),

            "baidu_index":
                baidu_index,

            "baidu_content":
                matched_baidu.get("content"),

            "baidu_coor":
                matched_baidu.get("coor"),

            "baidu_is_table":
                is_table_content(
                    matched_baidu.get("content")
                ),

            "spatial_coverage":
                match["spatial_coverage"],

            "text_coverage":
                match["text_coverage"],

            "combined_score":
                match["combined_score"],

            "matched":
                match["matched"]
        })

    # ========================================================
    # SUMMARY
    # ========================================================

    total = len(results)

    matched = sum(
        1
        for result in results
        if result["matched"]
    )

    missing = total - matched

    if total:
        match_percentage = (
            matched / total
        ) * 100
    else:
        match_percentage = 0.0

    # --------------------------------------------------------
    # Average spatial coverage
    # --------------------------------------------------------

    if results:

        average_spatial = (
            sum(
                result["spatial_coverage"]
                for result in results
            )
            / len(results)
        )

    else:

        average_spatial = 0.0

    # --------------------------------------------------------
    # Average text coverage
    # --------------------------------------------------------

    if results:

        average_text = (
            sum(
                result["text_coverage"]
                for result in results
            )
            / len(results)
        )

    else:

        average_text = 0.0

    # --------------------------------------------------------
    # Table-specific statistics
    # --------------------------------------------------------

    table_results = [
        result
        for result in results
        if result["baidu_is_table"]
    ]

    table_matched = sum(
        1
        for result in table_results
        if result["matched"]
    )

    if table_results:

        table_match_percentage = (
            table_matched
            /
            len(table_results)
        ) * 100

    else:

        table_match_percentage = 0.0

    summary = {

        "total_textract_items":
            total,

        "matched_items":
            matched,

        "missing_items":
            missing,

        "content_spatial_match_percentage":
            round(match_percentage, 2),

        "average_spatial_coverage":
            round(
                average_spatial * 100,
                2
            ),

        "average_text_coverage":
            round(
                average_text * 100,
                2
            ),

        "table_related_textract_items":
            len(table_results),

        "table_matched_items":
            table_matched,

        "table_match_percentage":
            round(
                table_match_percentage,
                2
            )
    }

    return summary, results


# ============================================================
# PRINT RESULTS
# ============================================================

def print_evaluation(summary, results):

    print()
    print("=" * 70)
    print("OCR EVALUATION SUMMARY")
    print("=" * 70)

    for key, value in summary.items():

        print(
            f"{key:40} : {value}"
        )

    print()
    print("=" * 70)
    print("DETAILED RESULTS")
    print("=" * 70)

    for result in results:

        print()
        print(
            f"Textract [{result['textract_index']}]"
        )

        print(
            f"  Text      : "
            f"{result['textract_content']}"
        )

        print(
            f"  Baidu     : "
            f"{result['baidu_content']}"
        )

        print(
            f"  Spatial   : "
            f"{result['spatial_coverage']:.2%}"
        )

        print(
            f"  Text      : "
            f"{result['text_coverage']:.2%}"
        )

        print(
            f"  Table     : "
            f"{result['baidu_is_table']}"
        )

        print(
            f"  MATCHED   : "
            f"{result['matched']}"
        )


# ============================================================
# TEST DATA
# ============================================================

def create_test_data():

    # --------------------------------------------------------
    # TEXTRACT
    #
    # Textract produces lines.
    # --------------------------------------------------------

    textract = [

        # ----------------------------------------------------
        # TEST 1
        # Normal paragraph
        # ----------------------------------------------------

        {
            "content":
                "Patient Name: John Smith",

            "coor":
                [100, 100, 400, 125]
        },

        {
            "content":
                "Date of Birth: 01/01/1985",

            "coor":
                [100, 130, 400, 155]
        },

        # ----------------------------------------------------
        # TEST 2
        # Multiple Textract lines that belong to
        # one Baidu paragraph.
        # ----------------------------------------------------

        {
            "content":
                "The patient visited the hospital",

            "coor":
                [100, 200, 500, 225]
        },

        {
            "content":
                "for a routine medical examination.",

            "coor":
                [100, 230, 500, 255]
        },

        {
            "content":
                "No abnormal findings were reported.",

            "coor":
                [100, 260, 500, 285]
        },

        # ----------------------------------------------------
        # TEST 3
        # Table content
        # ----------------------------------------------------

        {
            "content":
                "Name",

            "coor":
                [100, 350, 200, 375]
        },

        {
            "content":
                "John Smith",

            "coor":
                [200, 350, 400, 375]
        },

        {
            "content":
                "DOB",

            "coor":
                [100, 380, 200, 405]
        },

        {
            "content":
                "01/01/1985",

            "coor":
                [200, 380, 400, 405]
        },

        # ----------------------------------------------------
        # TEST 4
        # OCR typo
        # ----------------------------------------------------

        {
            "content":
                "Healthcare",

            "coor":
                [100, 450, 300, 475]
        },

        # ----------------------------------------------------
        # TEST 5
        # This should be MISSING
        # ----------------------------------------------------

        {
            "content":
                "This content does not exist in Baidu.",

            "coor":
                [100, 550, 500, 575]
        }
    ]

    # --------------------------------------------------------
    # BAIDU
    #
    # Baidu produces larger complete blocks.
    # --------------------------------------------------------

    baidu = [

        # ----------------------------------------------------
        # Paragraph block
        # Contains two Textract lines.
        # ----------------------------------------------------

        {
            "content":
                """
                Patient Name: John Smith
                Date of Birth: 01/01/1985
                """,

            "coor":
                [90, 90, 550, 175]
        },

        # ----------------------------------------------------
        # One Baidu block containing THREE Textract lines.
        # ----------------------------------------------------

        {
            "content":
                """
                The patient visited the hospital
                for a routine medical examination.
                No abnormal findings were reported.
                """,

            "coor":
                [90, 190, 550, 300]
        },

        # ----------------------------------------------------
        # TABLE
        #
        # This tests <table>...</table>
        # ----------------------------------------------------

        {
            "content":
                """
                <table>
                    <tr>
                        <td>Name</td>
                        <td>John Smith</td>
                    </tr>
                    <tr>
                        <td>DOB</td>
                        <td>01/01/1985</td>
                    </tr>
                </table>
                """,

            "coor":
                [90, 340, 450, 420]
        },

        # ----------------------------------------------------
        # OCR typo
        #
        # Textract:
        # Healthcare
        #
        # Baidu:
        # Healthcar
        # ----------------------------------------------------

        {
            "content":
                "Healthcar",

            "coor":
                [95, 445, 320, 480]
        }

        # No block for the final Textract item.
    ]

    return textract, baidu


# ============================================================
# TESTS
# ============================================================

def run_tests():

    print()
    print("=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)

    textract, baidu = create_test_data()

    summary, results = evaluate_ocr(
        textract,
        baidu
    )

    # ========================================================
    # TEST 1
    # Normal text
    # ========================================================

    result = results[0]

    assert result["matched"] is True, (
        "TEST 1 FAILED: Patient Name should match"
    )

    assert result["text_coverage"] == 1.0, (
        "TEST 1 FAILED: text should be exact"
    )

    assert result["spatial_coverage"] >= 0.90, (
        "TEST 1 FAILED: spatial coverage too low"
    )

    print("TEST 1 PASSED - normal text")

    # ========================================================
    # TEST 2
    # Date
    # ========================================================

    result = results[1]

    assert result["matched"] is True, (
        "TEST 2 FAILED: DOB should match"
    )

    print("TEST 2 PASSED - second line inside same Baidu block")

    # ========================================================
    # TEST 3
    # Multiple Textract lines -> one Baidu paragraph
    # ========================================================

    result = results[2]

    assert result["matched"] is True

    result = results[3]

    assert result["matched"] is True

    result = results[4]

    assert result["matched"] is True

    # All three should point to the same Baidu block
    assert (
        results[2]["baidu_index"]
        ==
        results[3]["baidu_index"]
        ==
        results[4]["baidu_index"]
    )

    print(
        "TEST 3 PASSED - multiple Textract lines "
        "matched to one Baidu paragraph"
    )

    # ========================================================
    # TEST 4
    # Table
    # ========================================================

    table_results = results[5:9]

    for result in table_results:

        assert result["matched"] is True, (
            "TABLE TEST FAILED"
        )

        assert result["baidu_is_table"] is True, (
            "TABLE TEST FAILED: table not detected"
        )

    print(
        "TEST 4 PASSED - <table> content"
    )

    # ========================================================
    # TEST 5
    # Fuzzy OCR typo
    # ========================================================

    result = results[9]

    assert result["matched"] is True, (
        "TEST 5 FAILED: Healthcare/Healthcar "
        "should fuzzy-match"
    )

    assert result["text_coverage"] >= 0.85

    print(
        "TEST 5 PASSED - fuzzy OCR matching"
    )

    # ========================================================
    # TEST 6
    # Missing content
    # ========================================================

    result = results[10]

    assert result["matched"] is False, (
        "TEST 6 FAILED: missing content "
        "should not match"
    )

    print(
        "TEST 6 PASSED - missing content detection"
    )

    # ========================================================
    # Final summary
    # ========================================================

    print()
    print("=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)

    print()
    print("Evaluation summary:")
    print(summary)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # Run synthetic tests
    run_tests()

    # --------------------------------------------------------
    # Also print the complete evaluation
    # --------------------------------------------------------

    textract, baidu = create_test_data()

    summary, results = evaluate_ocr(
        textract,
        baidu
    )

    print_evaluation(
        summary,
        results
    )
