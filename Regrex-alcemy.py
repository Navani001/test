def evaluate_content_bounding_box(
    ground_truth,
    ocr_output,
    min_spatial_coverage=0.5,
    min_text_similarity=0.5,
):
    total_boxes = 0
    covered_boxes = 0
    text_matched_boxes = 0
    total_spatial_coverage = 0.0
    uncovered_indices = []

    for index, item in enumerate(ground_truth):
        text = item.get("content", "")

        if not normalize_text(text):
            continue

        total_boxes += 1

        match = find_best_match(
            item,
            ocr_output,
            min_spatial_coverage=min_spatial_coverage,
            min_text_similarity=min_text_similarity,
        )

        if not match:
            uncovered_indices.append(index)
            continue

        covered_boxes += 1
        total_spatial_coverage += match["spatial_coverage"]

        if (
            match["text_contained"]
            or match["text_similarity"] >= min_text_similarity
        ):
            text_matched_boxes += 1

    return {
        "textract_boxes": total_boxes,
        "covered_boxes": covered_boxes,
        "uncovered_boxes": total_boxes - covered_boxes,
        "coverage_percentage": round(
            covered_boxes / total_boxes * 100, 2
        ) if total_boxes else 0.0,
        "average_spatial_coverage": round(
            total_spatial_coverage / covered_boxes * 100, 2
        ) if covered_boxes else 0.0,
        "text_matched_boxes": text_matched_boxes,
        "text_match_percentage": round(
            text_matched_boxes / covered_boxes * 100, 2
        ) if covered_boxes else 0.0,
        "uncovered_indices": uncovered_indices,
    }
