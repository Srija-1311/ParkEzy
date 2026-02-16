from shapely.geometry import Polygon

class OccupancyDetector:
    def __init__(self, slots):
        """
        Initialize occupancy detector with parking slot polygons
        
        Args:
            slots: Dictionary mapping slot_id to list of polygon coordinates
        """
        self.slots = {}

        for slot_id, polygon in slots.items():
            poly = Polygon(polygon)
            self.slots[slot_id] = poly

    def predict(self, boxes):
        """
        Predict occupancy status for each parking slot
        
        Args:
            boxes: List of car bounding boxes [(x1, y1, x2, y2), ...]
        
        Returns:
            Dictionary mapping slot_id to occupancy status (True/False)
        """
        predictions = {}

        for slot_id, slot_poly in self.slots.items():
            occupied = False

            for (x1, y1, x2, y2) in boxes:
                # Create polygon from bounding box
                car_poly = Polygon([
                    (x1, y1),
                    (x2, y1),
                    (x2, y2),
                    (x1, y2)
                ])

                # Check if there's any intersection
                if slot_poly.intersection(car_poly).area > 0:
                    occupied = True
                    break

            predictions[slot_id] = occupied

        return predictions
