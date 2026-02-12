import os
import cv2
from sklearn.metrics import accuracy_score

from detect_cars import detect_cars
from occupancy import predict_occupancy
from parse_slots import parse_slots_from_xml


IMG_DIR = "data/UFPR04/images"
XML_DIR = "data/UFPR04/xml"


def run():
    all_true = []
    all_pred = []

    for img_file in os.listdir(IMG_DIR):
        if not img_file.endswith(".jpg"):
            continue

        img_path = os.path.join(IMG_DIR, img_file)
        xml_path = os.path.join(XML_DIR, img_file.replace(".jpg", ".xml"))

        if not os.path.exists(xml_path):
            continue

        img = cv2.imread(img_path)
        slots = parse_slots_from_xml(xml_path)

        car_centers = detect_cars(img)
        preds = predict_occupancy(slots, car_centers)

        for slot, pred in zip(slots, preds):
            if slot["gt_occupied"] is None:
                continue

            all_true.append(slot["gt_occupied"])
            all_pred.append(int(pred))

    acc = accuracy_score(all_true, all_pred)
    print("Final Accuracy:", acc)


if __name__ == "__main__":
    run()
