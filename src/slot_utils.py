import json


def load_slots(path):
    """
    Load slot polygons from JSON. Handles both:
    - dict format: {"1": [[x,y],...], ...}
    - list format: [[[x,y],...], ...]  (from browser annotation)
    Returns dict mapping int/str slot_id -> list of [x,y] points.
    """
    with open(path, 'r') as f:
        data = json.load(f)

    if isinstance(data, list):
        # Browser saves as list of polygons — convert to 1-indexed dict
        return {i + 1: slot for i, slot in enumerate(data)}

    # Already a dict — normalise keys to int
    return {int(k): v for k, v in data.items()}


def save_slots(path, slots_list):
    """Save a list of polygon point-lists to JSON."""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(slots_list, f)
