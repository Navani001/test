def generate_summary(page_results):
    def get_dict(data, key):
        value = data.get(key, {})
        return value if isinstance(value, dict) else {}

    def get_int(data, key):
        try:
            return int(data.get(key) or 0)
        except (TypeError, ValueError):
            return 0

    def get_float(data, key):
        try:
            return float(data.get(key) or 0)
        except (TypeError, ValueError):
            return 0.0

    def ratio(numerator, denominator):
        return round(numerator / denominator, 4) if denominator else 0.0

    def percentage(numerator, denominator):
        return round(numerator / denominator * 100, 2) if denominator else 0.0

    pages = page_results if isinstance(page_results, list) else []
    successful_pages = [
        page for page in pages if not page.get("failure_reason")
    ]
    failed_pages = [
        page for page in pages if page.get("failure_reason")
    ]

    def section_total(section, key):
        return sum(
            get_int(get_dict(page, section), key)
            for page in successful_pages
        )

    gt_words = section_total("bag_of_words", "ground_truth_word_count")
    pred_words = section_total("bag_of_words", "prediction_word_count")
    matched_words = section_total("bag_of_words", "matched_word_count")

    error_totals = {
        "character_errors": sum(
            get_int(get_dict(get_dict(page, "error_rate_evaluation"), "cer"),
                    "character_errors")
            for page in successful_pages
        ),
        "ground_truth_characters": sum(
            get_int(get_dict(get_dict(page, "error_rate_evaluation"), "cer"),
                    "ground_truth_characters")
            for page in successful_pages
        ),
        "word_errors": sum(
            get_int(get_dict(get_dict(page, "error_rate_evaluation"), "wer"),
                    "word_errors")
            for page in successful_pages
        ),
        "ground_truth_words": sum(
            get_int(get_dict(get_dict(page, "error_rate_evaluation"), "wer"),
                    "ground_truth_words")
            for page in successful_pages
        ),
    }

    gt_numbers = section_total(
        "number_accuracy", "ground_truth_number_count"
    )
    pred_numbers = section_total(
        "number_accuracy", "prediction_number_count"
    )
    matched_numbers = section_total(
        "number_accuracy", "matched_number_count"
    )

    gt_boxes = section_total(
        "bounding_box_evaluation", "total_textract_boxes"
    )
    matched_boxes = section_total(
        "bounding_box_evaluation", "matched_boxes"
    )
    unmatched_boxes = section_total(
        "bounding_box_evaluation", "unmatched_boxes"
    )

    total_time = sum(
        get_float(page, "time_seconds") for page in pages
    )
    prompt_tokens = sum(
        get_int(get_dict(page, "token_usage"), "prompt_tokens")
        for page in pages
    )
    completion_tokens = sum(
        get_int(get_dict(page, "token_usage"), "completion_tokens")
        for page in pages
    )
    total_tokens = sum(
        get_int(get_dict(page, "token_usage"), "total_tokens")
        for page in pages
    )

    prediction_loop_pages = sum(
        bool(get_dict(page, "loop_evaluation").get(
            "prediction_loop_detected", False
        ))
        for page in pages
    )
    ground_truth_loop_pages = sum(
        bool(get_dict(page, "loop_evaluation").get(
            "ground_truth_loop_detected", False
        ))
        for page in pages
    )

    summary = {
        "document_summary": {
            "total_pages": len(pages),
            "successful_pages": len(successful_pages),
            "failed_pages": len(failed_pages),
            "failed_page_details": [
                {
                    "page": page.get("page", index),
                    "failure_reason": page.get("failure_reason"),
                }
                for index, page in enumerate(pages)
                if page.get("failure_reason")
            ],
        },
        "bag_of_words": {
            "ground_truth_word_count": gt_words,
            "prediction_word_count": pred_words,
            "matched_word_count": matched_words,
            "missing_word_occurrences": section_total(
                "bag_of_words", "missing_word_occurrences"
            ),
            "extra_word_occurrences": section_total(
                "bag_of_words", "extra_word_occurrences"
            ),
            "precision": ratio(matched_words, pred_words),
            "recall": ratio(matched_words, gt_words),
            "f1_score": ratio(
                2 * matched_words, pred_words + gt_words
            ),
        },
        "error_rate_evaluation": {
            "cer": {
                "character_errors": error_totals["character_errors"],
                "ground_truth_characters": error_totals[
                    "ground_truth_characters"
                ],
                "cer": ratio(
                    error_totals["character_errors"],
                    error_totals["ground_truth_characters"],
                ),
            },
            "wer": {
                "word_errors": error_totals["word_errors"],
                "ground_truth_words": error_totals["ground_truth_words"],
                "wer": ratio(
                    error_totals["word_errors"],
                    error_totals["ground_truth_words"],
                ),
            },
        },
        "number_accuracy": {
            "ground_truth_number_count": gt_numbers,
            "prediction_number_count": pred_numbers,
            "matched_number_count": matched_numbers,
            "missing_number_count": max(gt_numbers - matched_numbers, 0),
            "extra_number_count": max(pred_numbers - matched_numbers, 0),
            "precision": ratio(matched_numbers, pred_numbers),
            "recall": ratio(matched_numbers, gt_numbers),
            "f1_score": ratio(
                2 * matched_numbers, pred_numbers + gt_numbers
            ),
        },
        "bounding_box_evaluation": {
            "total_textract_boxes": gt_boxes,
            "matched_boxes": matched_boxes,
            "unmatched_boxes": unmatched_boxes,
            "match_percentage": percentage(matched_boxes, gt_boxes),
        },
        "loop_evaluation": {
            "pages_with_ground_truth_loops": ground_truth_loop_pages,
            "pages_with_prediction_loops": prediction_loop_pages,
            "total_prediction_loop_count": sum(
                get_int(get_dict(page, "loop_evaluation"),
                        "prediction_loop_count")
                for page in pages
            ),
            "total_prediction_excess_words": sum(
                get_int(get_dict(page, "loop_evaluation"),
                        "prediction_excess_words")
                for page in pages
            ),
        },
        "performance": {
            "total_time_seconds": round(total_time, 2),
            "average_time_per_page_seconds": round(
                total_time / len(pages), 2
            ) if pages else 0,
            "total_prompt_tokens": prompt_tokens,
            "total_completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "average_tokens_per_page": round(
                total_tokens / len(pages), 2
            ) if pages else 0,
        },
    }

    return summary
