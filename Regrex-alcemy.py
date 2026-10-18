import re
from rapidfuzz.distance import Levenshtein


def normalize_text(text: str) -> str:
    text = text.casefold()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def calculate_cer(ground_truth: str, prediction: str) -> dict:
    gt = normalize_text(ground_truth)
    pred = normalize_text(prediction)

    errors = Levenshtein.distance(gt, pred)

    return {
        "character_errors": errors,
        "ground_truth_characters": len(gt),
        "cer": errors / len(gt) if gt else (0.0 if not pred else float("inf")),
    }


def calculate_wer(ground_truth: str, prediction: str) -> dict:
    gt_words = normalize_text(ground_truth).split()
    pred_words = normalize_text(prediction).split()

    errors = Levenshtein.distance(gt_words, pred_words)

    return {
        "word_errors": errors,
        "ground_truth_words": len(gt_words),
        "wer": errors / len(gt_words)
        if gt_words
        else (0.0 if not pred_words else float("inf")),
    }


def evaluate_ocr(ground_truth: str, prediction: str) -> dict:
    return {
        **calculate_cer(ground_truth, prediction),
        **calculate_wer(ground_truth, prediction),
    }


# Example
textract_text = "Patient Name John Smith Total Amount 500"
baidu_text = "Patient Name John Smit Total Amount 500"

print(evaluate_ocr(textract_text, baidu_text))
