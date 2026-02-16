"""
Utility functions for the Smart Parking System
"""
import os
import cv2
import json
from pathlib import Path


def validate_setup():
    """
    Validate that all required files and directories exist
    
    Returns:
        tuple: (bool, list) - Success status and list of missing items
    """
    required_items = [
        ('models/yolov8n.pt', 'file'),
        ('data/UFPR04/slots.json', 'file'),
        ('static/uploads', 'dir'),
        ('templates/index.html', 'file')
    ]
    
    missing = []
    
    for item, item_type in required_items:
        if item_type == 'file' and not os.path.isfile(item):
            missing.append(f"File: {item}")
        elif item_type == 'dir' and not os.path.isdir(item):
            missing.append(f"Directory: {item}")
    
    return len(missing) == 0, missing


def get_sample_images(limit=5):
    """
    Get list of sample images from the dataset
    
    Args:
        limit: Maximum number of images to return
    
    Returns:
        list: Paths to sample images
    """
    images_dir = Path('data/UFPR04/images')
    
    if not images_dir.exists():
        return []
    
    images = list(images_dir.glob('*.jpg'))[:limit]
    return [str(img) for img in images]


def get_slot_statistics(slots_path='data/UFPR04/slots.json'):
    """
    Get statistics about parking slots
    
    Args:
        slots_path: Path to slots JSON file
    
    Returns:
        dict: Statistics about slots
    """
    try:
        with open(slots_path, 'r') as f:
            slots = json.load(f)
        
        return {
            'total_slots': len(slots),
            'slot_ids': list(slots.keys())
        }
    except Exception as e:
        return {'error': str(e)}


def clear_uploads(uploads_dir='static/uploads'):
    """
    Clear all uploaded files (useful for cleanup)
    
    Args:
        uploads_dir: Path to uploads directory
    
    Returns:
        int: Number of files deleted
    """
    count = 0
    uploads_path = Path(uploads_dir)
    
    if not uploads_path.exists():
        return count
    
    for file in uploads_path.glob('*'):
        if file.is_file() and file.name != '.gitkeep':
            file.unlink()
            count += 1
    
    return count


def check_image_validity(image_path):
    """
    Check if an image file is valid and readable
    
    Args:
        image_path: Path to image file
    
    Returns:
        tuple: (bool, str) - Validity status and message
    """
    if not os.path.exists(image_path):
        return False, "File does not exist"
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Failed to read image"
        
        height, width = img.shape[:2]
        if height < 100 or width < 100:
            return False, "Image too small"
        
        return True, f"Valid image ({width}x{height})"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


if __name__ == "__main__":
    # Run validation when script is executed directly
    print("=" * 50)
    print("Smart Parking System - Setup Validation")
    print("=" * 50)
    
    success, missing = validate_setup()
    
    if success:
        print("✓ All required files and directories found!")
        
        # Show slot statistics
        stats = get_slot_statistics()
        if 'error' not in stats:
            print(f"\n✓ Parking slots loaded: {stats['total_slots']} slots")
        
        # Show sample images
        samples = get_sample_images(3)
        if samples:
            print(f"\n✓ Sample images available: {len(samples)}")
            for img in samples:
                print(f"  - {img}")
        
        print("\n✓ System is ready to run!")
        print("\nRun: python app.py")
    else:
        print("✗ Setup incomplete. Missing items:")
        for item in missing:
            print(f"  - {item}")
        print("\nPlease ensure all required files are in place.")
