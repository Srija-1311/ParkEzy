"""
Video processor: runs YOLO + IoU occupancy detection frame-by-frame.
Yields results as a generator so Flask can stream them via SSE.
"""

import cv2
import os
import json

from src.detect_cars import CarDetector
from src.occupancy import OccupancyDetector
from src.slot_utils import load_slots
from src.visualize import draw_results
from src.analytics_db import save_frame_data

car_detector = CarDetector("models/yolov8n.pt")

FRAMES_DIR = "static/frames"
MAX_DIM    = 1280   # resize longest side to this before YOLO (keeps aspect ratio)


def _resize_for_inference(frame):
    """Resize frame so longest side = MAX_DIM, preserving aspect ratio."""
    h, w = frame.shape[:2]
    if max(h, w) <= MAX_DIM:
        return frame, 1.0
    scale = MAX_DIM / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(frame, (new_w, new_h)), scale


def _scale_boxes(boxes, scale):
    """Scale bounding boxes back to original frame coordinates."""
    if scale == 1.0:
        return boxes
    inv = 1.0 / scale
    return [(int(x1*inv), int(y1*inv), int(x2*inv), int(y2*inv))
            for (x1, y1, x2, y2) in boxes]


def process_video_stream(video_path, slot_path):
    """
    Generator that processes a video frame-by-frame and yields SSE events.
    Each yield is a JSON string with one frame's result.

    Yields:
        str — SSE-formatted data line, e.g. 'data: {...}\\n\\n'
    """
    os.makedirs(FRAMES_DIR, exist_ok=True)

    # Clear old frames
    for f in os.listdir(FRAMES_DIR):
        if f.endswith('.jpg'):
            os.remove(os.path.join(FRAMES_DIR, f))

    slots              = load_slots(slot_path)
    occupancy_detector = OccupancyDetector(slots)
    total_slots        = len(slots)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        yield f'data: {json.dumps({"error": "Cannot open video"})}\n\n'
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS) or 30

    # Adaptive frame_skip: aim for ~20 processed frames regardless of video length
    frame_skip = max(1, total_frames // 20)

    # Send metadata first
    yield f'data: {json.dumps({"type":"meta","total_frames":total_frames,"fps":fps,"frame_skip":frame_skip,"total_slots":total_slots})}\n\n'

    frame_num = 0
    processed = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_num % frame_skip != 0:
            frame_num += 1
            continue

        # Resize for fast YOLO inference
        small, scale = _resize_for_inference(frame)
        boxes_small  = car_detector.detect(small)
        boxes        = _scale_boxes(boxes_small, scale)

        predictions = occupancy_detector.predict(boxes)
        occupied    = sum(predictions.values())
        vacant      = total_slots - occupied
        rate        = round((occupied / total_slots) * 100, 1) if total_slots else 0

        # Draw on original-size frame
        annotated  = draw_results(frame, slots, predictions)
        frame_file = f"frame_{processed:04d}.jpg"
        frame_path = os.path.join(FRAMES_DIR, frame_file)
        cv2.imwrite(frame_path, annotated)

        save_frame_data(processed, vacant)

        result = {
            "type":           "frame",
            "frame":          processed,
            "occupied":       occupied,
            "vacant":         vacant,
            "total":          total_slots,
            "occupancy_rate": rate,
            "image_url":      f"/static/frames/{frame_file}"
        }
        yield f'data: {json.dumps(result)}\n\n'

        frame_num += 1
        processed += 1

    cap.release()

    # Send done signal
    yield f'data: {json.dumps({"type":"done","processed":processed})}\n\n'
