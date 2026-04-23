"""
Video processor: runs YOLO11x + IoU occupancy detection frame-by-frame.
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

car_detector = CarDetector("models/yolo11x.pt")

FRAMES_DIR = "static/frames"


def process_video_stream(video_path, slot_path):
    """
    Generator that processes a video frame-by-frame and yields SSE events.

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

    # Aim for ~20 processed frames regardless of video length
    frame_skip = max(1, total_frames // 20)

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

        # YOLO11x with imgsz=1920 handles high-res frames internally
        boxes       = car_detector.detect(frame)
        predictions = occupancy_detector.predict(boxes)

        occupied = sum(predictions.values())
        vacant   = total_slots - occupied
        rate     = round((occupied / total_slots) * 100, 1) if total_slots else 0

        annotated  = draw_results(frame, slots, predictions)
        frame_file = f"frame_{processed:04d}.jpg"
        cv2.imwrite(os.path.join(FRAMES_DIR, frame_file), annotated)

        save_frame_data(processed, vacant)

        yield f'data: {json.dumps({"type":"frame","frame":processed,"occupied":occupied,"vacant":vacant,"total":total_slots,"occupancy_rate":rate,"image_url":f"/static/frames/{frame_file}"})}\n\n'

        frame_num += 1
        processed += 1

    cap.release()
    yield f'data: {json.dumps({"type":"done","processed":processed})}\n\n'
