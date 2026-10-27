def rotated_to_target_bbox(
    bbox,
    original_width,
    original_height,
    target_width,
    target_height
):
    x0, y0, x1, y1 = bbox

    # Undo -90° rotation
    x0_original = y0
    y0_original = original_height - x1
    x1_original = y1
    y1_original = original_height - x0

    # Scale to target dimensions
    scale_x = target_width / original_width
    scale_y = target_height / original_height

    return (
        x0_original * scale_x,
        y0_original * scale_y,
        x1_original * scale_x,
        y1_original * scale_y,
    )


bbox_rotated = [229.2, 340.0, 510.6, 355.8]

bbox_target = rotated_to_target_bbox(
    bbox_rotated,
    original_width=2550,
    original_height=3300,
    target_width=1224,
    target_height=1584,
)

print(bbox_target)
