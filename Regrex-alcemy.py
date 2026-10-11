from collections import Counter
import re


def extract_number(text):
    pattern = r"\b\d+(?:[.,]\d+)*%?\b"
    return re.findall(pattern, text)


def number_accuracy(ground_truth, ocr_output):
    gt_numbers = extract_number(ground_truth)
    ocr_numbers = extract_number(ocr_output)

    gt_counts = Counter(gt_numbers)
    ocr_counts = Counter(ocr_numbers)

    # Match each occurrence at most once
    correct = sum(
        (gt_counts & ocr_counts).values()
    )

    tp = correct
    fp = sum(ocr_counts.values()) - tp
    fn = sum(gt_counts.values()) - tp

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    # For extraction, report reference-number coverage as accuracy.
    accuracy = recall

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "ground_truth_numbers": gt_numbers,
        "ocr_numbers": ocr_numbers,
        "correct": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "f1": f1,
    }
