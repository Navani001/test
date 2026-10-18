import re
from collections import Counter


def evaluate_number_accuracy(ground_truth: str, prediction: str) -> dict:
    pattern = r"(?<!\w)[+-]?\d[\d,]*(?:\.\d+)?%?(?!\w)"

    def extract_numbers(text):
        return [
            number.replace(",", "")
            for number in re.findall(pattern, text)
        ]

    gt_numbers = Counter(extract_numbers(ground_truth))
    pred_numbers = Counter(extract_numbers(prediction))

    matched = sum((gt_numbers & pred_numbers).values())
    gt_total = sum(gt_numbers.values())
    pred_total = sum(pred_numbers.values())

    precision = matched / pred_total if pred_total else 0.0
    recall = matched / gt_total if gt_total else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "ground_truth_number_count": gt_total,
        "prediction_number_count": pred_total,
        "matched_number_count": matched,
        "number_precision": round(precision, 4),
        "number_recall": round(recall, 4),
        "number_f1_score": round(f1, 4),
        "missing_numbers": dict(gt_numbers - pred_numbers),
        "extra_numbers": dict(pred_numbers - gt_numbers),
    }


textract_text = "Invoice 12345 Total Amount 1,500.00 Tax 18%"
baidu_text = "Invoice 12345 Total Amount 1500.00 Tax 8%"

result = evaluate_number_accuracy(textract_text, baidu_text)
print(result)
