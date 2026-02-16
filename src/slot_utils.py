import json

def load_slots(json_path):
    """
    Load parking slot polygons from JSON file
    
    Args:
        json_path: Path to slots JSON file
    
    Returns:
        Dictionary mapping slot_id (int) to list of polygon coordinates
    """
    with open(json_path, "r") as f:
        slots = json.load(f)

    # Convert string keys to integers
    return {int(k): v for k, v in slots.items()}
