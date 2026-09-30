def box_match_probability(textract_box, baidu_box, buffer=10):
    tx1, ty1, tx2, ty2 = textract_box
    bx1, by1, bx2, by2 = baidu_box

    tw = max(0, tx2 - tx1)
    th = max(0, ty2 - ty1)

    bw = max(0, bx2 - bx1)
    bh = max(0, by2 - by1)

    if min(tw, th, bw, bh) <= 0:
        return 0.0

    # Intersection
    iw = max(0, min(tx2, bx2) - max(tx1, bx1))
    ih = max(0, min(ty2, by2) - max(ty1, by1))

    # Coverage of Textract box
    coverage = (iw * ih) / (tw * th)

    # Axis overlap
    x_overlap = iw / min(tw, bw)
    y_overlap = ih / min(th, bh)

    # Distance between boxes
    gap_x = max(bx1 - tx2, tx1 - bx2, 0)
    gap_y = max(by1 - ty2, ty1 - by2, 0)

    distance = math.sqrt(gap_x ** 2 + gap_y ** 2)

    # Distance relative to Textract box size
    reference = math.sqrt(tw ** 2 + th ** 2)

    normalized_distance = distance / max(reference, 1)

    distance_score = math.exp(-3 * normalized_distance)

    # --------------------------------------------------
    # Final probability
    # --------------------------------------------------

    probability = (
        0.45 * coverage +
        0.20 * x_overlap +
        0.20 * y_overlap +
        0.15 * distance_score
    )

    return round(min(max(probability, 0), 1), 4)
