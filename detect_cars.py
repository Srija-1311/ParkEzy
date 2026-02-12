from ultralytics import YOLO

# Load once globally
model = YOLO("yolov8n.pt")
CAR_CLASS_ID = 2


def detect_cars(img):
    results = model(img)[0]
    centers = []

    for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
        if int(cls) != CAR_CLASS_ID:
            continue

        x1, y1, x2, y2 = box.tolist()
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        centers.append((cx, cy))

    return centers
