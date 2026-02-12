import cv2
from ultralytics import YOLO

model = YOLO("runs/detect/train/weights/best.pt")


def run():
    IMAGE_PATH = "data/UFPR04/images/2013-01-29_19_31_22.jpg"
    img = cv2.imread(IMAGE_PATH)

    results = model(img)[0]

    for box, cls, conf in zip(results.boxes.xyxy,
                              results.boxes.cls,
                              results.boxes.conf):

        if model.names[int(cls)] != "car":
            continue

        x1, y1, x2, y2 = map(int, box.tolist())

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            img,
            f"car {float(conf):.2f}",
            (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    cv2.imshow("Detection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
