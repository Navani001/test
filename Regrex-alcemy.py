
import json
import re
from pathlib import Path
from difflib import SequenceMatcher


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def normalize(text):
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def get_max_tokens(filename):
    match = re.search(r"tokens-(\d+)", filename, re.IGNORECASE)
    return int(match.group(1)) if match else None


def detect_loop(content, min_words=8, min_repeats=3):
    """
    Detect consecutive repetitions of the same word sequence.
    This is a heuristic and may need threshold calibration.
    """
    words = normalize(content).split()

    if len(words) < min_words * min_repeats:
        return {
            "detected": False,
            "repeated_text": None,
            "repetitions": 0
        }

    max_size = min(80, len(words) // min_repeats)

    for size in range(min_words, max_size + 1):
        for start in range(len(words) - size * min_repeats + 1):
            chunk = words[start:start + size]

            # Avoid flagging repeated single-word patterns.
            if len(set(chunk)) < 3:
                continue

            repetitions = 1
            pos = start + size

            while (
                pos + size <= len(words)
                and words[pos:pos + size] == chunk
            ):
                repetitions += 1
                pos += size

            if repetitions >= min_repeats:
                return {
                    "detected": True,
                    "repeated_text": " ".join(chunk),
                    "repetitions": repetitions
                }

    return {
        "detected": False,
        "repeated_text": None,
        "repetitions": 0
    }


def text_similarity(text1, text2):
    """Normalized character-sequence similarity, for diagnostics."""
    text1 = normalize(text1)
    text2 = normalize(text2)

    if not text1 or not text2:
        return None

    return round(
        SequenceMatcher(None, text1, text2).ratio() * 100,
        2
    )


def extract_textract_data_df(page_no, filename=None):
    """
    Retrieve a Textract row from the existing DataFrame `df`.
    Assumes pdf_page_no and file_name identify the reference.
    """
    temp = df[df["pdf_page_no"] == page_no]

    if filename is not None:
        temp = temp[temp["file_name"] == filename]

    if temp.empty:
        return None

    return temp.iloc[0]


def split_content(content):
    """Split using the explicit PAGE marker."""
    return [
        part.strip()
        for part in re.split(
            r"<\s*PAGE\s*>",
            content,
            flags=re.IGNORECASE
        )
        if part.strip()
    ]


# --------------------------------------------------
# Main evaluation
# --------------------------------------------------

file_path = (
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "batch-inference/report/experiments/"
)

file_name = (
    "run-001-batch-2-ngram-10-window-1024-"
    "image-1024-tokens-8192-dpi-300"
)

with open(
    f"{file_path}{file_name}.json",
    "r",
    encoding="utf-8"
) as f:
    datas = json.load(f)


result = []
total_failed = 0

for data in datas:
    pages_list = data["pages"]
    content = data.get("content", "")
    filename = data["filename"]

    expected_pages = len(pages_list)

    # Configured maximum extracted from the experiment filename.
    max_tokens = get_max_tokens(file_name)

    # Check whether the explicit separator exists.
    has_separator = bool(
        re.search(r"<\s*PAGE\s*>", content, re.IGNORECASE)
    )

    separator_status = (
        "present" if has_separator else "missing"
    )

    # Split content without modifying the original content.
    content_list = split_content(content)

    # Detect loops in the complete output, including when
    # the PAGE separator is missing.
    loop_info = detect_loop(content)

    # --------------------------------------------------
    # Compare with Textract page-level references
    # --------------------------------------------------

    textract_scores = []

    for idx, page in enumerate(pages_list):
        page_no = (
            page.get("page_no", idx + 1)
            if isinstance(page, dict)
            else idx + 1
        )

        textract_data = extract_textract_data_df(
            page_no=page_no,
            filename=filename
        )

        if (
            textract_data is not None
            and idx < len(content_list)
        ):
            score = text_similarity(
                content_list[idx],
                textract_data["content"]
            )
        else:
            score = None

        textract_scores.append(score)

    # --------------------------------------------------
    # Structural validation
    # --------------------------------------------------

    failure_reason = None

    if not content.strip():
        failure_reason = "empty_output"

    elif expected_pages > 1 and not has_separator:
        failure_reason = "missing_page_separator"

    elif len(content_list) != expected_pages:
        failure_reason = "page_count_mismatch"

    # Preserve your existing meaning of `failed`:
    # structural failure, not merely a loop warning.
    failed = failure_reason is not None

    if failed:
        total_failed += 1
        print(
            f"Structural failure: {filename} - "
            f"{failure_reason}"
        )

    if loop_info["detected"]:
        print(
            f"Possible loop: {filename} - "
            f"{loop_info['repeated_text']}"
        )

    # --------------------------------------------------
    # Append results with original fields preserved
    # --------------------------------------------------

    for idx, page in enumerate(pages_list):
        page_content = (
            content_list[idx]
            if not failed and idx < len(content_list)
            else "failed"
        )

        result.append({
            # Original fields
            "filename": filename,
            "time_seconds": (
                data["time_seconds"] / expected_pages
                if expected_pages else 0
            ),
            "token_usage": data["token_usage"],
            "content": page_content,
            "page": page,
            "failed": failed,

            # Additional diagnostic fields
            "max_tokens": max_tokens,
            "page_separator": separator_status,
            "expected_pages": expected_pages,
            "detected_segments": len(content_list),
            "failure_reason": failure_reason,
            "loop_detected": loop_info["detected"],
            "loop_details": loop_info,
            "textract_similarity": textract_scores[idx]
        })


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("Total documents:", len(datas))
print("Total failed documents:", total_failed)
print("Total page records:", len(result))

# Save the output without changing the existing schema.
output_path = (
    "/home/nlpdevintern1/ocrResearch/baidu/"
    "evaluation/formatted-inference/"
    f"{file_name}-formatted.json"
)

Path(output_path).parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

print("Saved:", output_path)
