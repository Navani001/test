import re
from collections import Counter


def evaluate_bag_of_words(ground_truth: str, prediction: str) -> dict:
    def tokenize(text):
        return re.findall(r"\b\w+\b", text.casefold())

    gt_words = Counter(tokenize(ground_truth))
    pred_words = Counter(tokenize(prediction))

    matched = sum((gt_words & pred_words).values())
    gt_total = sum(gt_words.values())
    pred_total = sum(pred_words.values())

    precision = matched / pred_total if pred_total else 0.0
    recall = matched / gt_total if gt_total else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "ground_truth_word_count": gt_total,
        "prediction_word_count": pred_total,
        "matched_word_count": matched,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "missing_words": dict(gt_words - pred_words),
        "extra_words": dict(pred_words - gt_words),
        "missing_word_occurrences": sum((gt_words - pred_words).values()),
        "extra_word_occurrences": sum((pred_words - gt_words).values()),
    }
