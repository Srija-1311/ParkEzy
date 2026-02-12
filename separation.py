import os
import shutil

SOURCE_ROOT = r"C:/Users/srija/Downloads/PKLot/PKLot/PKLot/UFPR04"
TARGET_ROOT = r"data/UFPR04"

IMAGE_DIR = os.path.join(TARGET_ROOT, "images")
XML_DIR = os.path.join(TARGET_ROOT, "xml")


def run():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(XML_DIR, exist_ok=True)

    count_img = 0
    count_xml = 0

    for climate in os.listdir(SOURCE_ROOT):
        climate_path = os.path.join(SOURCE_ROOT, climate)
        if not os.path.isdir(climate_path):
            continue

        for date in os.listdir(climate_path):
            date_path = os.path.join(climate_path, date)
            if not os.path.isdir(date_path):
                continue

            for file in os.listdir(date_path):
                src_file = os.path.join(date_path, file)

                if file.endswith(".jpg"):
                    shutil.copy(src_file, IMAGE_DIR)
                    count_img += 1

                elif file.endswith(".xml"):
                    shutil.copy(src_file, XML_DIR)
                    count_xml += 1

    print(f"Images copied: {count_img}")
    print(f"XML files copied: {count_xml}")


if __name__ == "__main__":
    run()
