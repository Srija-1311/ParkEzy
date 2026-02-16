# Quick Start Guide

Get the Smart Parking System up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Files

Make sure these files exist:
- `models/yolov8n.pt` - YOLOv8 model file
- `data/UFPR04/slots.json` - Parking slot coordinates

### 3. Run the Application

```bash
python app.py
```

Or use the run script:

```bash
python run.py
```

### 4. Open Browser

Navigate to: `http://localhost:5000`

### 5. Test the System

1. Click "Choose Image" button
2. Select a parking lot image from `data/UFPR04/images/`
3. Click "Detect Parking Spaces"
4. View the results!

## Troubleshooting

### Port Already in Use
If port 5000 is busy, change it:
```bash
export PORT=8080
python run.py
```

### Model Not Found
Download YOLOv8n model:
```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
```

### Slots JSON Missing
Use the tool to create slots.json:
```bash
python tools/create_slots_json.py
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize settings in `config.py`
- Add your own parking lot images and slot definitions

## Support

For issues or questions, please open an issue on GitHub.
