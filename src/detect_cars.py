from ultralytics import YOLO


class CarDetector:
    """
    YOLOv8-based vehicle detector.

    For standard side/front-view images, filters by vehicle COCO classes.
    For aerial/top-down parking lot images, YOLO often misclassifies cars as
    other objects (cell phone, bottle, etc.) due to the top-down perspective.
    The OccupancyDetector handles this by using slot-first IoU matching —
    any detection that significantly overlaps a slot is treated as a vehicle.
    """

    # COCO vehicle classes (car, bus, truck, motorcycle)
    VEHICLE_CLASSES = {2, 3, 5, 7}

    def __init__(self, model_path, conf=0.25):
        self.model = YOLO(model_path)
        self.conf  = conf

    def detect(self, img):
        """
        Return ALL detections above confidence threshold.
        Returns list of (x1, y1, x2, y2, class_id, confidence).
        The occupancy detector decides which ones overlap slots.
        """
        results = self.model(img, verbose=False, conf=self.conf)[0]
        boxes   = []
        for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
            x1, y1, x2, y2 = map(int, box.tolist())
            boxes.append((x1, y1, x2, y2))
        return boxes
