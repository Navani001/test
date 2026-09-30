def bbox_area(box):
    x1, y1, x2, y2 = box
    return max(0, x2 - x1) * max(0, y2 - y1)


def expand_box(box, buffer=5):
    """
    Add a pixel buffer around the box.
    """
    x1, y1, x2, y2 = box

    return [
        x1 - buffer,
        y1 - buffer,
        x2 + buffer,
        y2 + buffer
    ]


def overlap_metrics(textract_box, baidu_box, buffer=5):
    """
    Compare two OCR bounding boxes.

    textract_box: [x1, y1, x2, y2]
    baidu_box:    [x1, y1, x2, y2]

    Returns:
        intersection_area
        IoU
        textract_coverage
        baidu_coverage
        overlap
    """

    # Add buffer to Baidu box
    baidu_box = expand_box(
        baidu_box,
        buffer
    )

    tx1, ty1, tx2, ty2 = textract_box
    bx1, by1, bx2, by2 = baidu_box

    # Intersection
    ix1 = max(tx1, bx1)
    iy1 = max(ty1, by1)

    ix2 = min(tx2, bx2)
    iy2 = min(ty2, by2)

    # No overlap
    if ix2 <= ix1 or iy2 <= iy1:
        return {
            "overlap": False,
            "intersection_area": 0,
            "iou": 0.0,
            "textract_coverage": 0.0,
            "baidu_coverage": 0.0
        }

    intersection_area = (
        (ix2 - ix1) *
        (iy2 - iy1)
    )

    textract_area = bbox_area(
        textract_box
    )

    baidu_area = bbox_area(
        baidu_box
    )

    # --------------------------------------------------------
    # IoU
    # --------------------------------------------------------

    union_area = (
        textract_area
        + baidu_area
        - intersection_area
    )

    iou = (
        intersection_area / union_area
        if union_area > 0
        else 0
    )

    # --------------------------------------------------------
    # How much of Textract is covered by Baidu
    # --------------------------------------------------------

    textract_coverage = (
        intersection_area / textract_area
        if textract_area > 0
        else 0
    )

    # --------------------------------------------------------
    # How much of Baidu is covered by Textract
    # --------------------------------------------------------

    baidu_coverage = (
        intersection_area / baidu_area
        if baidu_area > 0
        else 0
    )

    return {
        "overlap": True,
        "intersection_area": intersection_area,
        "iou": iou,
        "textract_coverage": textract_coverage,
        "baidu_coverage": baidu_coverage
    }
