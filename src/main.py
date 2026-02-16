import cv2
from .detect_cars import CarDetector
from .occupancy import OccupancyDetector
from .slot_utils import load_slots
from .visualize import draw_results

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "models", "yolov8n.pt")
IMAGE_PATH = os.path.join(BASE_DIR, "data", "UFPR04", "images", "2012-12-07_16_42_25.jpg")
SLOTS_PATH = os.path.join(BASE_DIR, "data", "UFPR04", "slots.json")


def main():
    img = cv2.imread(IMAGE_PATH)

    # Load model
    detector = CarDetector(MODEL_PATH)
    car_centers = detector.detect(img)

    # Load slots
    slots = load_slots(SLOTS_PATH)

    # Predict occupancy
    occupancy_detector = OccupancyDetector(slots)
    predictions = occupancy_detector.predict(car_centers)
    total = len(predictions)
    occupied = sum(predictions.values())
    vacant = total - occupied

    print(f"Total Slots: {total}")
    print(f"Occupied: {occupied}")
    print(f"Vacant: {vacant}")
    print("Image shape:", img.shape)


    # Draw results
    output = draw_results(img, slots, predictions)

    cv2.imshow("Smart Parking Detection", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
