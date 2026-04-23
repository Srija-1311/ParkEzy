from ultralytics import YOLO


class CarDetector:
    """
    YOLO11x-based vehicle detector with high-resolution inference.

    Uses imgsz=1920 to preserve detail in aerial/top-down parking lot images
    where cars appear small relative to the full frame. Returns ALL detections
    regardless of class — the OccupancyDetector uses slot-IoU to decide
    occupancy, which handles aerial misclassification (cars detected as
    cell phones, bottles, etc.) automatically.
    """

    def __init__(self, model_path, conf=0.1, imgsz=1920):
        self.model = YOLO(model_path)
        self.conf  = conf
        self.imgsz = imgsz

    def detect(self, img):
        """
        Run inference and return all bounding boxes above confidence threshold.

        Args:
            img: numpy array (BGR)

        Returns:
            list of (x1, y1, x2, y2) int tuples
        """
        results = self.model(img, verbose=False, conf=self.conf, imgsz=self.imgsz)[0]
        return [tuple(map(int, box.tolist())) for box in results.boxes.xyxy]
