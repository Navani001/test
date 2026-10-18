import re


def evaluate_looping(text: str, min_ngram: int = 5) -> dict:
    words = re.findall(r"\b[\w'-]+\b", text.casefold())
    n = len(words)

    repeated_sequences = []
    total_excess_words = 0

    for size in range(min_ngram, n // 2 + 1):
        i = 0

        while i + 2 * size <= n:
            sequence = words[i:i + size]
            repetitions = 1

            while (
                i + (repetitions + 1) * size <= n
                and words[
                    i + repetitions * size:
                    i + (repetitions + 1) * size
                ] == sequence
            ):
                repetitions += 1

            if repetitions >= 2:
                excess = (repetitions - 1) * size

                repeated_sequences.append({
                    "text": " ".join(sequence),
                    "repetitions": repetitions,
                    "excess_words": excess,
                    "start_word_index": i,
                })

                total_excess_words += excess
                i += repetitions * size
            else:
                i += 1

    unique = {}
    for item in repeated_sequences:
        key = (item["start_word_index"], item["text"])
        unique[key] = item

    repeated_sequences = list(unique.values())

    return {
        "total_words": n,
        "loop_detected": bool(repeated_sequences),
        "loop_count": len(repeated_sequences),
        "estimated_excess_words": total_excess_words,
        "loop_details": repeated_sequences,
    }


def compare_looping(ground_truth: str, prediction: str) -> dict:
    gt_result = evaluate_looping(ground_truth)
    pred_result = evaluate_looping(prediction)

    return {
        "ground_truth_loop_detected": gt_result["loop_detected"],
        "prediction_loop_detected": pred_result["loop_detected"],
        "prediction_loop_count": pred_result["loop_count"],
        "prediction_excess_words": pred_result["estimated_excess_words"],
        "ground_truth_loops": gt_result["loop_details"],
        "prediction_loops": pred_result["loop_details"],
    }
