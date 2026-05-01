"""
Auto-slot detection: infers ALL parking slot polygons from YOLO vehicle detections,
including EMPTY spaces by extrapolating the parking row/column grid.

Algorithm:
1. Run YOLO → get vehicle bounding boxes (occupied slots only)
2. Cluster bboxes into rows using DBSCAN on Y-coordinate
3. Within each row, sort by X and compute median slot width + gap
4. Extrapolate the full row: fill gaps between detected cars with empty slots
5. Return all slot polygons (occupied + vacant) for user review

This is the key fix: without extrapolation, only occupied slots are generated
and the system reports 0 vacant slots.
"""

import numpy as np
from shapely.geometry import Polygon


# ── Geometry helpers ──────────────────────────────────────────────────────────

def _center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def _box_to_poly(cx, cy, w, h, padding=0.05):
    """Build a slot polygon centred at (cx, cy) with given size."""
    hw = w / 2 * (1 + padding)
    hh = h / 2 * (1 + padding)
    return [
        [int(cx - hw), int(cy - hh)],
        [int(cx + hw), int(cy - hh)],
        [int(cx + hw), int(cy + hh)],
        [int(cx - hw), int(cy + hh)],
    ]


def _remove_overlapping(slots, thresh=0.5):
    """Remove heavily overlapping slot polygons, keeping the larger one."""
    if not slots:
        return slots
    polys = [Polygon(s) for s in slots]
    keep  = [True] * len(slots)
    for i in range(len(slots)):
        if not keep[i]:
            continue
        for j in range(i + 1, len(slots)):
            if not keep[j]:
                continue
            inter = polys[i].intersection(polys[j]).area
            smaller = min(polys[i].area, polys[j].area)
            if smaller > 0 and inter / smaller > thresh:
                if polys[i].area >= polys[j].area:
                    keep[j] = False
                else:
                    keep[i] = False
                    break
    return [s for s, k in zip(slots, keep) if k]


# ── Row clustering ────────────────────────────────────────────────────────────

def _cluster_into_rows(boxes, row_tolerance_factor=0.6):
    """
    Group bounding boxes into rows by Y-coordinate proximity.
    row_tolerance_factor: fraction of median box height to use as row merge threshold.
    Returns list of lists of boxes.
    """
    if not boxes:
        return []

    boxes = list(boxes)
    heights = [b[3] - b[1] for b in boxes]
    med_h   = float(np.median(heights))
    tol     = med_h * row_tolerance_factor

    # Sort by Y center
    centers_y = [_center(b)[1] for b in boxes]
    order     = np.argsort(centers_y)
    sorted_boxes = [boxes[i] for i in order]
    sorted_cy    = [centers_y[i] for i in order]

    rows = []
    current_row = [sorted_boxes[0]]
    current_cy  = sorted_cy[0]

    for i in range(1, len(sorted_boxes)):
        if abs(sorted_cy[i] - current_cy) <= tol:
            current_row.append(sorted_boxes[i])
            current_cy = np.mean([_center(b)[1] for b in current_row])
        else:
            rows.append(current_row)
            current_row = [sorted_boxes[i]]
            current_cy  = sorted_cy[i]
    rows.append(current_row)
    return rows


# ── Gap filling ───────────────────────────────────────────────────────────────

def _fill_row_gaps(row_boxes, img_w, img_h, max_gap_slots=3, padding=0.06):
    """
    Given detected cars in one row, generate slot polygons for the full row
    including empty spaces between and around the detected cars.

    Strategy:
    - Compute median slot width and height from detected cars
    - Sort cars by X center
    - For each gap between consecutive cars, insert empty slot polygons
    - Optionally extend the row left/right by 1 slot if there's room
    """
    if not row_boxes:
        return []

    # Median dimensions
    widths  = [b[2] - b[0] for b in row_boxes]
    heights = [b[3] - b[1] for b in row_boxes]
    med_w   = float(np.median(widths))
    med_h   = float(np.median(heights))

    # Sort by X center
    sorted_row = sorted(row_boxes, key=lambda b: _center(b)[0])
    centers_x  = [_center(b)[0] for b in sorted_row]
    row_cy     = float(np.mean([_center(b)[1] for b in sorted_row]))

    slots = []

    # Add slot for each detected car
    for box in sorted_row:
        cx, cy = _center(box)
        slots.append(_box_to_poly(cx, cy, med_w, med_h, padding))

    # Fill gaps between consecutive cars
    for i in range(len(sorted_row) - 1):
        cx_left  = centers_x[i]
        cx_right = centers_x[i + 1]
        gap      = cx_right - cx_left

        # How many empty slots fit in this gap?
        n_empty = int(round(gap / med_w)) - 1
        if 1 <= n_empty <= max_gap_slots:
            step = gap / (n_empty + 1)
            for k in range(1, n_empty + 1):
                cx_empty = cx_left + step * k
                slots.append(_box_to_poly(cx_empty, row_cy, med_w, med_h, padding))

    # Extend row left by 1 slot if there's room
    leftmost_cx = centers_x[0]
    if leftmost_cx - med_w > 0:
        slots.append(_box_to_poly(leftmost_cx - med_w, row_cy, med_w, med_h, padding))

    # Extend row right by 1 slot if there's room
    rightmost_cx = centers_x[-1]
    if rightmost_cx + med_w < img_w:
        slots.append(_box_to_poly(rightmost_cx + med_w, row_cy, med_w, med_h, padding))

    return slots


# ── Main entry point ──────────────────────────────────────────────────────────

def auto_detect_slots(boxes, img_shape, padding=0.06):
    """
    Given YOLO bounding boxes (occupied slots only), infer ALL slot polygons
    including empty spaces by extrapolating the parking row grid.

    Args:
        boxes:     list of (x1, y1, x2, y2) from CarDetector
        img_shape: (height, width[, channels]) of the source image
        padding:   fraction to expand each slot polygon outward

    Returns:
        list of slot polygons [[x,y],[x,y],[x,y],[x,y]] in original image coords
    """
    if not boxes:
        return []

    h, w = img_shape[:2]

    # Cluster into rows
    rows = _cluster_into_rows(boxes)

    all_slots = []
    for row in rows:
        if not row:
            continue
        row_slots = _fill_row_gaps(row, w, h, max_gap_slots=4, padding=padding)
        all_slots.extend(row_slots)

    # Clip to image bounds
    clipped = []
    for slot in all_slots:
        cs = [[max(0, min(w - 1, p[0])), max(0, min(h - 1, p[1]))] for p in slot]
        clipped.append(cs)

    # Remove heavy overlaps
    clipped = _remove_overlapping(clipped, thresh=0.5)

    return clipped
