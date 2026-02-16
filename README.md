# 🚗 Smart Parking System

An AI-powered web application for real-time parking space detection using YOLOv8 and computer vision.

## Features

- **Real-time Detection**: Upload parking lot images and get instant occupancy analysis
- **Visual Feedback**: Color-coded parking slots (green for vacant, red for occupied)
- **Statistics Dashboard**: View total slots, occupied, vacant, and occupancy rate
- **Modern UI**: Responsive, clean interface that works on all devices
- **Production-Ready**: Modular architecture with error handling and validation

## Technology Stack

- **Backend**: Python Flask
- **AI Model**: YOLOv8 (Ultralytics)
- **Computer Vision**: OpenCV
- **Geometry Processing**: Shapely
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## Project Structure

```
smart-parking-system/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── models/
│   └── yolov8n.pt        # YOLOv8 model
├── data/
│   └── UFPR04/
│       ├── slots.json    # Parking slot coordinates
│       └── images/       # Sample images
├── src/
│   ├── detect_cars.py    # Car detection module
│   ├── occupancy.py      # Occupancy detection logic
│   ├── slot_utils.py     # Slot loading utilities
│   └── visualize.py      # Visualization functions
├── templates/
│   └── index.html        # Frontend UI
└── static/
    └── uploads/          # Uploaded images storage
```

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd smart-parking-system
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Verify model and data**
- Ensure `models/yolov8n.pt` exists
- Ensure `data/UFPR04/slots.json` exists

## Usage

1. **Start the application**
```bash
python app.py
```

2. **Open browser**
Navigate to `http://localhost:5000`

3. **Upload image**
- Click "Choose Image" button
- Select a parking lot image
- Click "Detect Parking Spaces"

4. **View results**
- See color-coded parking slots
- Check occupancy statistics
- Analyze occupancy rate

## API Endpoints

### GET /
Returns the main web interface

### POST /detect
Processes uploaded image and returns detection results

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: image file

**Response:**
```json
{
  "success": true,
  "image_path": "static/uploads/image.jpg",
  "total_slots": 100,
  "occupied": 45,
  "vacant": 55,
  "occupancy_rate": 45.0
}
```

## Configuration

Edit `config.py` to customize:
- File upload limits
- Allowed file extensions
- Model paths
- Detection thresholds

## Development

### Running in Development Mode
```bash
python app.py
```

### Running in Production Mode
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
python app.py
```

## How It Works

1. **Image Upload**: User uploads parking lot image
2. **Car Detection**: YOLOv8 detects vehicles in the image
3. **Intersection Analysis**: System checks if detected cars intersect with parking slot polygons
4. **Occupancy Calculation**: Slots with car intersections are marked as occupied
5. **Visualization**: Results are drawn on the image with color coding
6. **Statistics**: Occupancy metrics are calculated and displayed

## Modules

### detect_cars.py
- Loads YOLOv8 model
- Detects cars in images
- Returns bounding boxes

### occupancy.py
- Manages parking slot polygons
- Calculates intersection between cars and slots
- Determines occupancy status

### visualize.py
- Draws parking slot polygons
- Color codes based on occupancy
- Adds slot ID labels

### slot_utils.py
- Loads parking slot coordinates from JSON
- Handles data format conversion

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
