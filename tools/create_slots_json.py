import cv2
import json
import numpy as np
import os

points = []
slots = {}
slot_id = 1

def order_points(pts):
    pts = np.array(pts)
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect.tolist()

def click_event(event, x, y, flags, param):
    global points, slot_id

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(x, y)

        if len(points) == 4:
            ordered = order_points(points)
            slots[slot_id] = ordered
            print(f"Slot {slot_id} saved")
            slot_id += 1
            points.clear()

image_path = "C:/Users/srija/OneDrive/Desktop/ParkEzy/data/UFPR04/images/2012-12-07_16_42_25.jpg"
img = cv2.imread(image_path)

cv2.imshow("Define Slots", img)
cv2.setMouseCallback("Define Slots", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(BASE_DIR, "data", "UFPR04", "slots.json")

with open(output_path, "w") as f:
    json.dump(slots, f, indent=4)

print("slots.json created at:", output_path)
