def box_match_probability(textract_box, baidu_box):
    """
    Percentage of the Textract box covered by the Baidu box.
    Boxes use [x1, y1, x2, y2].
    """

    if not textract_box or not baidu_box:
        return 0.0

    x1, y1, x2, y2 = map(float, textract_box)
    bx1, by1, bx2, by2 = map(float, baidu_box)

    textract_area = (x2 - x1) * (y2 - y1)

    if textract_area <= 0:
        return 0.0

    ix1 = max(x1, bx1)
    iy1 = max(y1, by1)
    ix2 = min(x2, bx2)
    iy2 = min(y2, by2)

    intersection = (
        max(0.0, ix2 - ix1)
        * max(0.0, iy2 - iy1)
    )

    return intersection / textract_area


def find_best_match(
    ground_truth_item,
    ocr_output,
    min_spatial_coverage=0.5,
    min_text_similarity=0.5,
    flag=False,
):
    gt_text = ground_truth_item.get("content", "")
    gt_box = ground_truth_item.get("coord")

    candidates = []

    for idx, ocr_item in enumerate(ocr_output):
        ocr_text = ocr_item.get("content", "")
        ocr_box = ocr_item.get("coord")

        if not gt_box or not ocr_box:
            continue

        # Spatial coverage is independent of text similarity.
        coverage = box_match_probability(gt_box, ocr_box)

        if coverage < min_spatial_coverage:
            continue

        exact_contained = text_is_contained(
            gt_text, ocr_text
        )

        similarity = text_similarity(gt_text, ocr_text)

        if exact_contained:
            similarity = 1.0

        candidates.append({
            "baidu_index": idx,
            "spatial_coverage": coverage,
            "text_similarity": similarity,
            "text_contained": exact_contained,
            "baidu_text": ocr_text,
            "baidu_bbox": ocr_box,
        })

    if not candidates:
        return None

    # Prefer spatial coverage first, then text similarity.
    candidates.sort(
        key=lambda item: (
            item["spatial_coverage"],
            item["text_similarity"],
        ),
        reverse=True,
    )

    best = candidates[0]

    # Spatial match and text match are separate outcomes.
    best["spatially_matched"] = True
    best["text_matched"] = (
        best["text_contained"]
        or best["text_similarity"] >= min_text_similarity
    )

    if flag and not best["text_matched"]:
        print(
            "Spatial match, text mismatch:",
            gt_text,
            "vs",
            best["baidu_text"],
        )

    return best


def evaluate_content_bounding_box(
    ground_truth,
    ocr_output,
    min_spatial_coverage=0.5,
    min_text_similarity=0.5,
    debug=False,
):
    results = []

    total = len(ground_truth)
    spatially_covered_count = 0
    text_matched_count = 0

    total_spatial_coverage = 0.0
    total_text_similarity = 0.0

    for ground_index, ground_item in enumerate(ground_truth):
        content = ground_item.get("content", "")

        if not normalize_text(content):
            continue

        match = find_best_match(
            ground_item,
            ocr_output,
            min_spatial_coverage,
            min_text_similarity,
            debug,
        )

        if match:
            spatially_covered_count += 1
            total_spatial_coverage += match["spatial_coverage"]
            total_text_similarity += match["text_similarity"]

            if match["text_matched"]:
                text_matched_count += 1

            results.append({
                "textract_index": ground_index,
                "textract_text": content,
                "textract_bbox": ground_item.get("coord"),
                "baidu_index": match["baidu_index"],
                "baidu_text": match["baidu_text"],
                "baidu_bbox": match["baidu_bbox"],
                "spatial_coverage": round(
                    match["spatial_coverage"], 4
                ),
                "text_similarity": round(
                    match["text_similarity"], 4
                ),
                "text_contained": match["text_contained"],
                "spatially_matched": True,
                "text_matched": match["text_matched"],
                "matched": match["text_matched"],
            })

        else:
            results.append({
                "textract_index": ground_index,
                "textract_text": content,
                "textract_bbox": ground_item.get("coord"),
                "baidu_index": None,
                "baidu_text": None,
                "baidu_bbox": None,
                "spatial_coverage": 0.0,
                "text_similarity": 0.0,
                "text_contained": False,
                "spatially_matched": False,
                "text_matched": False,
                "matched": False,
            })

    valid_count = sum(
        1 for item in ground_truth
        if normalize_text(item.get("content", ""))
    )

    summary = {
        "textract_items": valid_count,
        "spatially_covered_items": spatially_covered_count,
        "spatially_uncovered_items": (
            valid_count - spatially_covered_count
        ),
        "spatial_coverage_percentage": round(
            spatially_covered_count / valid_count * 100, 2
        ) if valid_count else 0.0,
        "text_matched_items": text_matched_count,
        "text_match_percentage": round(
            text_matched_count / valid_count * 100, 2
        ) if valid_count else 0.0,
        "average_spatial_coverage": round(
            total_spatial_coverage / spatially_covered_count * 100,
            2,
        ) if spatially_covered_count else 0.0,
        "average_text_similarity": round(
            total_text_similarity / spatially_covered_count * 100,
            2,
        ) if spatially_covered_count else 0.0,
    }

    return {
        "summary": summary,
        "results": results,
    }
