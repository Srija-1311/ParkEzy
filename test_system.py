"""
Test script to verify Smart Parking System components
"""
import os
import sys
import cv2

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import flask
        import cv2
        import numpy
        from ultralytics import YOLO
        from shapely.geometry import Polygon
        print("✓ All packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_model():
    """Test if YOLOv8 model can be loaded"""
    print("\nTesting model loading...")
    model_path = "models/yolov8n.pt"
    
    if not os.path.exists(model_path):
        print(f"✗ Model not found at {model_path}")
        return False
    
    try:
        from ultralytics import YOLO
        model = YOLO(model_path)
        print(f"✓ Model loaded successfully from {model_path}")
        return True
    except Exception as e:
        print(f"✗ Model loading error: {e}")
        return False


def test_slots():
    """Test if slots JSON can be loaded"""
    print("\nTesting slots loading...")
    slots_path = "data/UFPR04/slots.json"
    
    if not os.path.exists(slots_path):
        print(f"✗ Slots file not found at {slots_path}")
        return False
    
    try:
        from src.slot_utils import load_slots
        slots = load_slots(slots_path)
        print(f"✓ Loaded {len(slots)} parking slots")
        return True
    except Exception as e:
        print(f"✗ Slots loading error: {e}")
        return False


def test_detection():
    """Test car detection on a sample image"""
    print("\nTesting car detection...")
    
    # Find a sample image
    images_dir = "data/UFPR04/images"
    if not os.path.exists(images_dir):
        print(f"✗ Images directory not found at {images_dir}")
        return False
    
    images = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
    if not images:
        print("✗ No sample images found")
        return False
    
    sample_image = os.path.join(images_dir, images[0])
    
    try:
        from src.detect_cars import CarDetector
        
        img = cv2.imread(sample_image)
        if img is None:
            print(f"✗ Failed to read image: {sample_image}")
            return False
        
        detector = CarDetector("models/yolov8n.pt")
        boxes = detector.detect(img)
        
        print(f"✓ Detected {len(boxes)} cars in sample image")
        return True
    except Exception as e:
        print(f"✗ Detection error: {e}")
        return False


def test_occupancy():
    """Test occupancy detection"""
    print("\nTesting occupancy detection...")
    
    try:
        from src.slot_utils import load_slots
        from src.occupancy import OccupancyDetector
        
        slots = load_slots("data/UFPR04/slots.json")
        detector = OccupancyDetector(slots)
        
        # Test with dummy boxes
        dummy_boxes = [(100, 100, 200, 200), (300, 300, 400, 400)]
        predictions = detector.predict(dummy_boxes)
        
        print(f"✓ Occupancy detection working ({len(predictions)} slots processed)")
        return True
    except Exception as e:
        print(f"✗ Occupancy detection error: {e}")
        return False


def test_visualization():
    """Test visualization functions"""
    print("\nTesting visualization...")
    
    try:
        import numpy as np
        from src.visualize import draw_results
        from src.slot_utils import load_slots
        
        # Create dummy image
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        
        slots = load_slots("data/UFPR04/slots.json")
        predictions = {slot_id: False for slot_id in slots.keys()}
        
        result = draw_results(img, slots, predictions)
        
        print("✓ Visualization working")
        return True
    except Exception as e:
        print(f"✗ Visualization error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Smart Parking System - Component Tests")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Model Loading", test_model),
        ("Slots Loading", test_slots),
        ("Car Detection", test_detection),
        ("Occupancy Detection", test_occupancy),
        ("Visualization", test_visualization)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nRun: python app.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
