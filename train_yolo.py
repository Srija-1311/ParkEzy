from ultralytics import YOLO


def run():
    model = YOLO("yolov8n.pt")

    model.train(
        data="data.yaml",
        epochs=50,
        imgsz=640
    )


if __name__ == "__main__":
    run()
