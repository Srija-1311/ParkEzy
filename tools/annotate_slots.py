import cv2
import json

slots = []
current = []


def annotate(image_path):
    import cv2, json

    img = cv2.imread(image_path)

    # Resize for screen
    scale = 50
    w = int(img.shape[1] * scale / 100)
    h = int(img.shape[0] * scale / 100)
    img = cv2.resize(img, (w, h))

    clone = img.copy()

    slots = []
    current = []

    def click(event, x, y, flags, param):
        nonlocal current, img

        if event == cv2.EVENT_LBUTTONDOWN:
            current.append((x, y))
            cv2.circle(img, (x,y), 5, (0,0,255), -1)

            if len(current) > 1:
                cv2.line(img, current[-2], current[-1], (255,0,0), 2)

            if len(current) == 4:
                slots.append(current.copy())
                cv2.line(img, current[3], current[0], (255,0,0), 2)
                print(f"Slot {len(slots)} saved")
                current.clear()

    cv2.namedWindow("Annotate", cv2.WINDOW_NORMAL)
    cv2.imshow("Annotate", img)
    cv2.setMouseCallback("Annotate", click)

    print("""
    Controls:
    - Click 4 points per slot
    - Press 's' to SAVE
    - Press 'r' to RESET
    - Press 'q' to QUIT
    """)

    while True:
        cv2.imshow("Annotate", img)
        key = cv2.waitKey(1)

        if key == ord('s'):
            import os
            filename = os.path.basename(image_path).split('.')[0]
            save_path = f"data/slots/{filename}.json"

            with open(save_path, "w") as f:
                json.dump(slots, f)

            print(f"Saved to {save_path}")
            break

            

        elif key == ord('r'):
            img = clone.copy()
            slots.clear()
            current.clear()
            print("Reset")

        elif key == ord('q'):
            break

    cv2.destroyAllWindows()