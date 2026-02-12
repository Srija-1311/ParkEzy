import xml.etree.ElementTree as ET


def parse_slots_from_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    slots = []

    for space in root.findall('space'):
        slot_id = int(space.attrib['id'])
        occupied = space.attrib.get('occupied')

        if occupied is not None:
            occupied = int(occupied)

        contour = space.find('contour')
        points = []

        for pt in contour.findall('point'):
            x = int(pt.attrib['x'])
            y = int(pt.attrib['y'])
            points.append((x, y))

        slots.append({
            "id": slot_id,
            "polygon": points,
            "gt_occupied": occupied
        })

    return slots


# Optional testing block
if __name__ == "__main__":
    import cv2
    import numpy as np

    img_path = "data/UFPR04/images/2013-01-29_19_31_22.jpg"
    xml_path = "data/UFPR04/xml/2013-01-29_19_31_22.xml"

    img = cv2.imread(img_path)
    slots = parse_slots_from_xml(xml_path)

    for slot in slots:
        color = (0, 0, 255) if slot["gt_occupied"] == 1 else (0, 255, 0)
        cv2.polylines(img, [np.array(slot["polygon"])], True, color, 2)

    cv2.imshow("Slots", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
