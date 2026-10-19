import re
from difflib import SequenceMatcher


def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)

    return text.strip()


def get_text(item):
    return str(item.get("text") or item.get("str") or "").strip()


def get_coord(item):
    return item.get("coord")


def box_match_probability(gt_box, baidu_box):
    if not gt_box or not baidu_box:
        return 0.0

    if len(gt_box) != 4 or len(baidu_box) != 4:
        return 0.0

    gx1, gy1, gx2, gy2 = map(float, gt_box)
    bx1, by1, bx2, by2 = map(float, baidu_box)

    gx1, gx2 = min(gx1, gx2), max(gx1, gx2)
    gy1, gy2 = min(gy1, gy2), max(gy1, gy2)
    bx1, bx2 = min(bx1, bx2), max(bx1, bx2)
    by1, by2 = min(by1, by2), max(by1, by2)

    ix1 = max(gx1, bx1)
    iy1 = max(gy1, by1)
    ix2 = min(gx2, bx2)
    iy2 = min(gy2, by2)

    intersection_area = (
        max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    )

    gt_area = (gx2 - gx1) * (gy2 - gy1)

    if gt_area <= 0:
        return 0.0

    return intersection_area / gt_area


def match_text(gt_text, baidu_text, similarity_threshold=0.90):
    gt = normalize_text(gt_text)
    baidu = normalize_text(baidu_text)

    if not gt or not baidu:
        return False

    if gt == baidu or gt in baidu:
        return True

    if len(gt) < 4:
        return False

    if len(baidu) <= len(gt):
        similarity = SequenceMatcher(None, gt, baidu).ratio()
        return similarity >= similarity_threshold

    window_size = len(gt)

    for start in range(len(baidu) - window_size + 1):
        candidate = baidu[start:start + window_size]

        similarity = SequenceMatcher(
            None, gt, candidate
        ).ratio()

        if similarity >= similarity_threshold:
            return True

    return False


def evaluate_textract_in_baidu(
    ground_truth,
    baidu_output,
    min_spatial_coverage=0.5,
    similarity_threshold=0.90,
):
    total_textract_boxes = 0
    matched_boxes = 0

    for gt in ground_truth:
        gt_text = get_text(gt)
        gt_box = get_coord(gt)

        if not gt_text or not gt_box:
            continue

        total_textract_boxes += 1
        found_match = False

        for baidu in baidu_output:
            baidu_text = get_text(baidu)
            baidu_box = get_coord(baidu)

            if not baidu_text or not baidu_box:
                continue

            coverage = box_match_probability(gt_box, baidu_box)

            if coverage < min_spatial_coverage:
                continue

            if match_text(
                gt_text,
                baidu_text,
                similarity_threshold,
            ):
                found_match = True
                break

        if found_match:
            matched_boxes += 1

    unmatched_boxes = total_textract_boxes - matched_boxes

    match_percentage = (
        matched_boxes / total_textract_boxes * 100
        if total_textract_boxes
        else 0.0
    )

    return {
        "total_textract_boxes": total_textract_boxes,
        "matched_boxes": matched_boxes,
        "unmatched_boxes": unmatched_boxes,
        "match_percentage": round(match_percentage, 2),
    }


if __name__ == "__main__":
    ground_truth = [
        {"text": "Invoice Number", "coord": [100, 100, 250, 130]},
        {"str": "INV12345", "coord": [260, 100, 360, 130]},
        {"text": "Total Amount", "coord": [100, 200, 250, 230]},
    ]

    baidu_output = [
        {
            "text": "Invoice Number INV12345",
            "coord": [95, 95, 370, 135],
        },
        {
            "str": "Total Amount",
            "coord": [100, 200, 250, 230],
        },
    ]

    results = evaluate_textract_in_baidu(
        ground_truth,
        baidu_output,
        min_spatial_coverage=0.5,
        similarity_threshold=0.90,
    )

    print(results)
