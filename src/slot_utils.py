import json

def load_slots(path):
    with open(path, 'r') as f:
        slots = json.load(f)

    # 🔥 UNIVERSAL FIX
    if isinstance(slots, list):
        slots = {i: s for i, s in enumerate(slots)}

    return slots