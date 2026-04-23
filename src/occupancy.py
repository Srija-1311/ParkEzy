from shapely.geometry import Polygon


class OccupancyDetector:
    """
    Slot-first IoU occupancy detector.

    For each parking slot polygon, checks whether any detected bounding box
    has sufficient overlap (IoU >= threshold). This works for both:
    - Standard side-view images: YOLO correctly classifies cars
    - Aerial/top-down images: YOLO may misclassify cars as other objects,
      but the slot-first approach still works because the bounding box
      position and size are correct regardless of the predicted class label.
    """

    def __init__(self, slots, iou_threshold=0.3):
        """
        Args:
            slots: dict mapping slot_id -> list of [x, y] polygon points
            iou_threshold: minimum IoU to mark a slot as occupied
        """
        self.iou_threshold = iou_threshold
        self.slots = {slot_id: Polygon(coords) for slot_id, coords in slots.items()}

    def _iou(self, slot_poly, car_poly):
        inter = slot_poly.intersection(car_poly).area
        if inter == 0:
            return 0.0
        return inter / slot_poly.union(car_poly).area

    def predict(self, boxes):
        """
        Args:
            boxes: list of (x1, y1, x2, y2) from CarDetector

        Returns:
            dict mapping slot_id -> True (occupied) / False (vacant)
        """
        car_polys = [
            Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
            for (x1, y1, x2, y2) in boxes
        ]

        predictions = {}
        for slot_id, slot_poly in self.slots.items():
            occupied = any(
                self._iou(slot_poly, cp) >= self.iou_threshold
                for cp in car_polys
            )
            predictions[slot_id] = occupied

        return predictions
