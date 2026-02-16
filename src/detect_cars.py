import os
import torch
from ultralytics import YOLO

# Monkey patch torch.load to use weights_only=False for compatibility
_original_torch_load = torch.load

def _patched_torch_load(f, *args, **kwargs):
    """Patched torch.load that sets weights_only=False for compatibility"""
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(f, *args, **kwargs)

torch.load = _patched_torch_load


class CarDetector:
    """YOLOv8-based car detector"""
    
    def __init__(self, model_path):
        """
        Initialize car detector with YOLOv8 model
        
        Args:
            model_path: Path to YOLOv8 model file
        """
        self.model = YOLO(model_path)
        self.CAR_CLASS = 2  # COCO dataset car class ID

    def detect(self, img):
        """
        Detect cars in image
        
        Args:
            img: Input image (numpy array)
        
        Returns:
            List of bounding boxes [(x1, y1, x2, y2), ...]
        """
        results = self.model(img, verbose=False)[0]
        boxes = []

        for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
            if int(cls) != self.CAR_CLASS:
                continue

            x1, y1, x2, y2 = map(int, box.tolist())
            boxes.append((x1, y1, x2, y2))

        return boxes
