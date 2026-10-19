import re
from collections import Counter
from rapidfuzz.distance import Levenshtein


def normalize_words(text):
    return re.findall(r"\b\w+\b", text.casefold())


def intersection_area(a, b):
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])

    if x2 <= x1 or y2 <= y1:
        return 0.0

    return (x2 - x1) * (y2 - y1)


def word_overlap_ratio(word_box, block_box):
    word_area = (
        (word_box[2] - word_box[0])
        * (word_box[3] - word_box[1])
    )

    if word_area <= 0:
        return 0.0

    return intersection_area(word_box, block_box) / word_area


def evaluate_bbox_text(
    textract_words,
    baidu_blocks,
    overlap_threshold=0.5,
):
    block_results = []
    word_assignments = Counter()

    total_reference_words = 0
    total_matched_words = 0
    total_predicted_words = 0

    for block_index, block in enumerate(baidu_blocks):
        bbox = block["bbox"]
        prediction = block.get("text", "")

        assigned = []

        for word_index, word in enumerate(textract_words):
            ratio = word_overlap_ratio(word["bbox"], bbox)

            if ratio >= overlap_threshold:
                assigned.append((word_index, word))

        assigned.sort(
            key=lambda item: (
                (item[1]["bbox"][1] + item[1]["bbox"][3]) / 2,
                item[1]["bbox"][0],
            )
        )

        reference = " ".join(
            word["text"] for _, word in assigned
        )

        for word_index, _ in assigned:
            word_assignments[word_index] += 1

        gt_words = normalize_words(reference)
        pred_words = normalize_words(prediction)

        gt_counts = Counter(gt_words)
        pred_counts = Counter(pred_words)

        matched = sum((gt_counts & pred_counts).values())
        missing = gt_counts - pred_counts
        extra = pred_counts - gt_counts

        precision = (
            matched / len(pred_words) if pred_words else 0.0
        )
        recall = (
            matched / len(gt_words) if gt_words else 0.0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )

        gt_chars = reference.casefold()
        pred_chars = prediction.casefold()

        cer = (
            Levenshtein.distance(gt_chars, pred_chars) / len(gt_chars)
            if gt_chars else (0.0 if not pred_chars else 1.0)
        )

        wer = (
            Levenshtein.distance(gt_words, pred_words) / len(gt_words)
            if gt_words else (0.0 if not pred_words else 1.0)
        )

        block_results.append({
            "block_index": block_index,
            "reference_text": reference,
            "predicted_text": prediction,
            "reference_word_count": len(gt_words),
            "predicted_word_count": len(pred_words),
            "matched_word_count": matched,
            "text_precision": round(precision, 4),
            "text_recall": round(recall, 4),
            "text_f1": round(f1, 4),
            "cer": round(cer, 4),
            "wer": round(wer, 4),
            "missing_words": dict(missing),
            "extra_words": dict(extra),
        })

        total_reference_words += len(gt_words)
        total_matched_words += matched
        total_predicted_words += len(pred_words)

    unassigned = [
        i for i in range(len(textract_words))
        if word_assignments[i] == 0
    ]

    multiply_assigned = [
        i for i in range(len(textract_words))
        if word_assignments[i] > 1
    ]

    precision = (
        total_matched_words / total_predicted_words
        if total_predicted_words else 0.0
    )
    recall = (
        total_matched_words / total_reference_words
        if total_reference_words else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "block_results": block_results,
        "overlap_threshold": overlap_threshold,
        "overall_text_precision": round(precision, 4),
        "overall_text_recall": round(recall, 4),
        "overall_text_f1": round(f1, 4),
        "unassigned_textract_word_indices": unassigned,
        "multiply_assigned_textract_word_indices": multiply_assigned,
        "unassigned_word_count": len(unassigned),
        "multiply_assigned_word_count": len(multiply_assigned),
    }
