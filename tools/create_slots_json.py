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
        print(f"Point: {x}, {y}")

        if len(points) == 4:
            ordered = order_points(points)
            slots[slot_id] = ordered
            print(f"✅ Slot {slot_id} saved")
            slot_id += 1
            points.clear()

# ── INPUT IMAGE ─────────────────────────────

image_path = input("Enter image path: ").strip()

img = cv2.imread(image_path)

if img is None:
    print("❌ Error: Image not found")
    exit()

# ── RESIZE FOR SCREEN (FIX ZOOM ISSUE) ─────

scale = 50  # adjust if needed
width = int(img.shape[1] * scale / 100)
height = int(img.shape[0] * scale / 100)

img = cv2.resize(img, (width, height))
clone = img.copy()

# ── WINDOW ────────────────────────────────

cv2.namedWindow("Define Slots", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Define Slots", click_event)

print("""
Instructions:
- Click 4 points per slot
- Press 's' to SAVE
- Press 'r' to RESET
- Press 'q' to QUIT
""")

while True:
    cv2.imshow("Define Slots", img)
    key = cv2.waitKey(1)

    if key == ord('s'):
        break

    elif key == ord('r'):
        img = clone.copy()
        slots.clear()
        print("🔄 Reset all slots")

    elif key == ord('q'):
        print("❌ Exiting without saving")
        exit()

cv2.destroyAllWindows()

# ── SAVE JSON ─────────────────────────────

filename = os.path.basename(image_path).split('.')[0]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(BASE_DIR, "data", "slots")
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, f"{filename}.json")

with open(output_path, "w") as f:
    json.dump(slots, f, indent=4)

print(f"✅ slots saved at: {output_path}")