import cv2
import os

from src.detect_cars import CarDetector
from src.occupancy import OccupancyDetector
from src.slot_utils import load_slots
from src.visualize import draw_results
from src.analytics_db import save_frame_data

# Initialize YOLO once
car_detector = CarDetector("models/yolov8n.pt")


def process_video(path):

    filename = os.path.basename(path).split('.')[0]
    slot_path = f"data/slots/{filename}.json"

    # fallback
    if not os.path.exists(slot_path):
        slot_path = "data/slots/frame.json"

    slots = load_slots(slot_path)
    occupancy_detector = OccupancyDetector(slots)

    cap = cv2.VideoCapture(path)

    frame_id = 0
    results = []

    frame_skip = 10
    max_frames = 200

    output_dir = "static/frames"
    os.makedirs(output_dir, exist_ok=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % frame_skip != 0:
            frame_id += 1
            continue

        if frame_id > max_frames:
            break

        # 🔥 IMPORTANT: DO NOT RESIZE (to match slots)
        # frame = cv2.resize(frame, (640, 480))

        boxes = car_detector.detect(frame)
        predictions = occupancy_detector.predict(boxes)

        total = len(predictions)
        occupied = sum(predictions.values())
        available = total - occupied

        # save analytics
        save_frame_data(frame_id, available)

        # draw output
        output_frame = draw_results(frame, slots, predictions)

        frame_path = f"{output_dir}/frame_{frame_id}.jpg"
        cv2.imwrite(frame_path, output_frame)

        results.append({
            "frame": frame_id,
            "available": available,
            "image": frame_path
        })

        frame_id += 1

    cap.release()

    # return sampled frames only
    sample_frames = results[::20]

    return results, sample_frames