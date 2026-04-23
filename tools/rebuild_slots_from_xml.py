"""
Rebuild data/UFPR04/slots.json from the XML ground truth contours.
The XML files contain the correct 4-corner polygons for each slot.
Run once: python tools/rebuild_slots_from_xml.py
"""

import xml.etree.ElementTree as ET
import json

# Use any XML file - all have the same slot layout (only occupancy changes)
XML_PATH = "data/UFPR04/xml/2012-12-07_16_42_25.xml"
OUTPUT   = "data/UFPR04/slots.json"

tree = ET.parse(XML_PATH)
root = tree.getroot()

slots = {}
for space in root.findall(".//space"):
    slot_id = space.attrib.get("id")
    points  = [
        [int(p.attrib["x"]), int(p.attrib["y"])]
        for p in space.findall(".//contour/point")
    ]
    if len(points) == 4:
        slots[slot_id] = points

with open(OUTPUT, "w") as f:
    json.dump(slots, f, indent=2)

print(f"Rebuilt {OUTPUT} with {len(slots)} slots from XML ground truth.")
