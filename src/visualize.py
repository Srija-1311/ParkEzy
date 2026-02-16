import cv2
import numpy as np

def draw_results(img, slots, predictions):
    """
    Draw parking slot polygons on image with color coding
    
    Args:
        img: Input image (numpy array)
        slots: Dictionary mapping slot_id to polygon coordinates
        predictions: Dictionary mapping slot_id to occupancy status
    
    Returns:
        Image with drawn parking slots
    """
    output = img.copy()
    
    for slot_id, polygon in slots.items():
        # Red for occupied, Green for vacant
        color = (0, 0, 255) if predictions[slot_id] else (0, 255, 0)
        
        pts = np.array(polygon, np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        # Draw filled polygon with transparency
        overlay = output.copy()
        cv2.fillPoly(overlay, [pts], color)
        cv2.addWeighted(overlay, 0.3, output, 0.7, 0, output)
        
        # Draw polygon border
        cv2.polylines(output, [pts], True, color, 2)
        
        # Add slot ID label
        centroid = pts.mean(axis=0).astype(int).flatten()
        cv2.putText(output, str(slot_id), tuple(centroid), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return output
