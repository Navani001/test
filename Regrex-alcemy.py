import json
import pandas as pd
from pathlib import Path


def divide(a, b):
    return a / b if b else 0.0


def analyze_ocr_results(json_path, output_dir="ocr_analysis"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    if isinstance(results, dict):
        results = [results]

    if not results:
        raise ValueError("The JSON array is empty")

    # Flatten nested JSON into one row per page
    df = pd.json_normalize(results)

    def get_col(name):
        if name not in df.columns:
            return pd.Series(0, index=df.index, dtype=float)
        return pd.to_numeric(df[name], errors="coerce").fillna(0)

    # Bounding-box counts
    expected = get_col("count_bounding_box.textract_items")
    matched = get_col("count_bounding_box.matched_items")
    missing = get_col("count_bounding_box.missing_items")

    df["bbox_match_rate"] = matched.div(expected.where(expected != 0))
    df["bbox_missing_rate"] = missing.div(expected.where(expected != 0))

    # Page-level metrics
    df["number_error_rate"] = 1 - get_col(
        "number_accuracy.accuracy"
    )
    df["bow_error_rate"] = 1 - get_col(
        "bow_evaluation.f1"
    )

    # Replace undefined page-level rates
    df[["bbox_match_rate", "bbox_missing_rate"]] = (
        df[["bbox_match_rate", "bbox_missing_rate"]].fillna(0)
    )

    # Overall bounding-box counts
    total_expected = expected.sum()
    total_matched = matched.sum()
    total_missing = missing.sum()

    # Aggregate page-level precision/recall using a weighted mean.
    # Exact micro-averages require TP/FP/FN counts from each page.
    number_precision = get_col("number_accuracy.precision")
    number_recall = get_col("number_accuracy.recall")
    number_weights = get_col("number_accuracy.correct").clip(lower=0)

    bow_precision = get_col("bow_evaluation.precision")
    bow_recall = get_col("bow_evaluation.recall")
    bow_weights = get_col("bow_evaluation.correct").clip(lower=0)

    def weighted_average(values, weights):
        valid = weights > 0
        if valid.any():
            return (values[valid] * weights[valid]).sum() / weights[valid].sum()
        return values.mean() if len(values) else 0.0

    np_ = weighted_average(number_precision, number_weights)
    nr_ = weighted_average(number_recall, number_weights)
    bp = weighted_average(bow_precision, bow_weights)
    br = weighted_average(bow_recall, bow_weights)

    # Processing and token totals
    time = get_col("time_seconds")
    prompt = get_col("token_usage.prompt_tokens")
    completion = get_col("token_usage.completion_tokens")
    tokens = get_col("token_usage.total_tokens")

    summary = {
        "total_pages": len(df),

        "bounding_boxes": {
            "expected": int(total_expected),
            "matched": int(total_matched),
            "missing": int(total_missing),
            "match_rate": divide(total_matched, total_expected),
            "missing_rate": divide(total_missing, total_expected),
        },

        "number_accuracy": {
            "mean_page_precision": float(np_),
            "mean_page_recall": float(nr_),
            "derived_f1": divide(2 * np_ * nr_, np_ + nr_),
        },

        "bow_evaluation": {
            "mean_page_precision": float(bp),
            "mean_page_recall": float(br),
            "derived_f1": divide(2 * bp * br, bp + br),
        },

        "wer_cer": {
            "mean_page_wer": float(get_col("wer_cer.wer").mean()),
            "mean_page_cer": float(get_col("wer_cer.cer").mean()),
        },

        "processing": {
            "total_seconds": float(time.sum()),
            "average_seconds_per_page": float(time.mean()),
        },

        "token_usage": {
            "prompt_tokens": int(prompt.sum()),
            "completion_tokens": int(completion.sum()),
            "total_tokens": int(tokens.sum()),
        },
    }

    # Rank pages by multiple error indicators
    df["combined_error_score"] = (
        df["bbox_missing_rate"]
        + df["number_error_rate"]
        + df["bow_error_rate"]
        + get_col("wer_cer.wer")
        + get_col("wer_cer.cer")
    )

    # Save outputs
    df.to_csv(output_dir / "page_level_analysis.csv", index=False)

    worst_columns = [
        c for c in [
            "filename",
            "page",
            "combined_error_score",
            "bbox_missing_rate",
            "number_error_rate",
            "bow_error_rate",
            "wer_cer.wer",
            "wer_cer.cer",
        ]
        if c in df.columns
    ]

    df.sort_values(
        "combined_error_score", ascending=False
    )[worst_columns].to_csv(
        output_dir / "worst_pages.csv", index=False
    )

    with open(
        output_dir / "overall_summary.json", "w", encoding="utf-8"
    ) as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))
    print(f"\nReports saved to: {output_dir.resolve()}")

    return summary, df


# Usage
# summary, page_df = analyze_ocr_results("results.json")
