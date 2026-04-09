"""
Evaluation module: runs YOLO detection on a sample of PKLot images,
compares predictions against XML ground truth labels using IoU,
and computes Accuracy, Precision, Recall, F1.
"""

import os
import cv2
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon

XML_DIR   = "data/UFPR04/xml"
IMAGE_DIR = "data/UFPR04/images"


def _parse_xml_slots(xml_path):
    """
    Returns list of (slot_id, polygon, occupied_gt) from a PKLot XML file.
    Uses the contour points as the slot polygon.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    slots = []
    for space in root.findall(".//space"):
        sid = space.attrib.get("id")
        occ = int(space.attrib.get("occupied", 0))
        pts = [
            (int(p.attrib["x"]), int(p.attrib["y"]))
            for p in space.findall(".//contour/point")
        ]
        if len(pts) >= 3:
            slots.append((sid, Polygon(pts), occ))
    return slots


def _iou(poly_a, poly_b):
    inter = poly_a.intersection(poly_b).area
    if inter == 0:
        return 0.0
    return inter / poly_a.union(poly_b).area


def run_evaluation(detector, iou_threshold=0.3, sample_step=38):
    """
    Evaluate YOLO detector against PKLot XML ground truth.

    Args:
        detector:      CarDetector instance
        iou_threshold: IoU threshold to mark a slot occupied
        sample_step:   evaluate every Nth file (38 ≈ 100 images from 3791)

    Returns:
        dict with overall metrics and per-slot stats
    """
    xml_files = sorted(f for f in os.listdir(XML_DIR) if f.endswith(".xml"))
    sample    = xml_files[::sample_step]

    tp = fp = tn = fn = 0
    slot_stats = {}   # slot_id -> {tp, fp, tn, fn}
    processed  = 0
    errors     = 0

    for fname in sample:
        xml_path = os.path.join(XML_DIR, fname)
        img_path = os.path.join(IMAGE_DIR, fname.replace(".xml", ".jpg"))

        if not os.path.exists(img_path):
            errors += 1
            continue

        img = cv2.imread(img_path)
        if img is None:
            errors += 1
            continue

        # YOLO detection
        boxes = detector.detect(img)
        car_polys = [
            Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
            for (x1, y1, x2, y2) in boxes
        ]

        # Ground truth from XML
        gt_slots = _parse_xml_slots(xml_path)

        for sid, slot_poly, gt_occ in gt_slots:
            # Predict: occupied if any car has IoU >= threshold with this slot
            pred_occ = int(any(
                _iou(slot_poly, cp) >= iou_threshold for cp in car_polys
            ))

            if sid not in slot_stats:
                slot_stats[sid] = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}

            if pred_occ == 1 and gt_occ == 1:
                tp += 1; slot_stats[sid]["tp"] += 1
            elif pred_occ == 1 and gt_occ == 0:
                fp += 1; slot_stats[sid]["fp"] += 1
            elif pred_occ == 0 and gt_occ == 0:
                tn += 1; slot_stats[sid]["tn"] += 1
            else:
                fn += 1; slot_stats[sid]["fn"] += 1

        processed += 1

    total = tp + fp + tn + fn

    def safe_div(a, b):
        return round(a / b * 100, 2) if b else 0.0

    precision = safe_div(tp, tp + fp)
    recall    = safe_div(tp, tp + fn)
    accuracy  = safe_div(tp + tn, total)
    f1 = round(
        2 * precision * recall / (precision + recall), 2
    ) if (precision + recall) else 0.0

    # Per-slot summary
    per_slot = []
    for sid, s in sorted(slot_stats.items(), key=lambda x: int(x[0])):
        s_total = s["tp"] + s["fp"] + s["tn"] + s["fn"]
        per_slot.append({
            "slot_id":   sid,
            "accuracy":  safe_div(s["tp"] + s["tn"], s_total),
            "tp": s["tp"], "fp": s["fp"],
            "tn": s["tn"], "fn": s["fn"],
            "gt_occupied_pct": safe_div(s["tp"] + s["fn"], s_total),
        })

    return {
        "images_evaluated": processed,
        "total_predictions": total,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "accuracy":  accuracy,
        "precision": precision,
        "recall":    recall,
        "f1_score":  f1,
        "per_slot":  per_slot,
        "errors":    errors,
    }
