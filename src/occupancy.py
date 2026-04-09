from shapely.geometry import Polygon


class OccupancyDetector:
    """
    Determines parking slot occupancy using IoU between
    detected vehicle bounding boxes and slot polygons.
    """

    def __init__(self, slots, iou_threshold=0.3):
        """
        Args:
            slots: dict mapping slot_id -> list of polygon coordinates
            iou_threshold: minimum IoU to mark a slot as occupied
        """
        self.iou_threshold = iou_threshold
        self.slots = {slot_id: Polygon(coords) for slot_id, coords in slots.items()}

    def _iou(self, slot_poly, car_poly):
        """Compute IoU between slot polygon and car bounding box polygon."""
        intersection = slot_poly.intersection(car_poly).area
        if intersection == 0:
            return 0.0
        union = slot_poly.union(car_poly).area
        return intersection / union if union > 0 else 0.0

    def predict(self, boxes):
        """
        Args:
            boxes: list of (x1, y1, x2, y2) bounding boxes from YOLO

        Returns:
            dict mapping slot_id -> True (occupied) / False (vacant)
        """
        predictions = {}

        for slot_id, slot_poly in self.slots.items():
            occupied = False

            for (x1, y1, x2, y2) in boxes:
                car_poly = Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
                if self._iou(slot_poly, car_poly) >= self.iou_threshold:
                    occupied = True
                    break

            predictions[slot_id] = occupied

        return predictions
