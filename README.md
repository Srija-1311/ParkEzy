# 🅿 ParkEzy — Smart Parking System

AI-powered parking space detection using YOLOv8 + IoU-based occupancy analysis. Supports both **images** and **videos** with frame-by-frame analytics.

---

## ✨ Features

### 🚗 Live Detection
- **Image Upload**: Detect occupied/vacant slots in a single parking lot image
- **Video Upload**: Process videos frame-by-frame with occupancy trends over time
- **Browser-Based Slot Annotation**: Define parking slot boundaries by clicking 4 corners per slot — no desktop tools needed
- **Multi-Lot Support**: Save and reuse slot layouts for different parking lots

### 📊 Analytics Dashboard
- **Peak Hours**: Average occupancy by hour of day
- **Weather Impact**: Occupancy comparison across Sunny/Cloudy/Rainy conditions
- **Daily Trends**: Occupancy rate over time
- **Date Range Filtering**: Analyze specific time periods
- **CSV Export**: Download occupancy logs for reporting

### 🎯 Model Evaluation
- **Accuracy Metrics**: Precision, Recall, F1, Accuracy
- **Confusion Matrix**: TP/FP/TN/FN breakdown
- **Per-Slot Analysis**: Which slots are detected most accurately
- **Slot Utilization**: Ground truth occupancy frequency per slot

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER UPLOADS                            │
│              Image (.jpg, .png) or Video (.mp4)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SLOT DEFINITION                             │
│  • Existing lot: Load slots from data/slots/{name}.json     │
│  • New lot: User draws polygons in browser → saves JSON     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  YOLO DETECTION                              │
│  • YOLOv8n detects vehicles (class 2 = car)                 │
│  • Returns bounding boxes [(x1,y1,x2,y2), ...]              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  IoU OCCUPANCY LOGIC                         │
│  • For each slot polygon:                                   │
│    - Calculate IoU with each detected car bbox              │
│    - If IoU ≥ 0.3 → slot is OCCUPIED                        │
│    - Else → slot is VACANT                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  VISUALIZATION                               │
│  • Draw slot polygons: Green = Vacant, Red = Occupied       │
│  • Add slot ID labels                                       │
│  • Semi-transparent overlay                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ANALYTICS LOGGING                           │
│  • Save to SQLite: timestamp, occupied, vacant, rate        │
│  • Video: per-frame data for trend charts                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
python app.py
```

### 3. Open Browser

Navigate to **http://localhost:5000**

---

## 📖 Usage Guide

### Image Detection

1. **Upload an image** (drag & drop or click to browse)
2. If it's a **new parking lot**:
   - Check "New Parking Lot?"
   - Enter a lot name (e.g., `mall_roof`)
   - Click 4 corners of each slot to draw polygons
   - Click **Save Slots**
3. Click **Detect Parking Spaces**
4. View results: Total/Occupied/Vacant stats + annotated image

### Video Detection

1. **Upload a video** (.mp4, .avi, .mov)
2. If it's a **new parking lot**, define slots as above
3. Click **Detect Parking Spaces**
4. View results:
   - Average occupancy stats
   - Occupancy rate chart over time
   - Frame-by-frame gallery (click to enlarge)

### Slot Annotation Tips

- Click corners in order: **top-left → top-right → bottom-right → bottom-left**
- Slot closes automatically after 4 clicks
- Use **Undo Last** to remove the most recent slot
- Use **Clear All** to start over
- Slots are saved at **original image resolution** (not canvas display size)

---

## 📂 Project Structure

```
ParkEzy/
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
│
├── src/
│   ├── detect_cars.py          # YOLOv8 car detection
│   ├── occupancy.py            # IoU-based occupancy logic
│   ├── visualize.py            # Draw results on images
│   ├── video_processor.py      # Frame-by-frame video processing
│   ├── slot_utils.py           # Load/save slot JSON files
│   ├── analytics_db.py         # SQLite logging
│   └── evaluate.py             # Model evaluation against PKLot ground truth
│
├── templates/
│   ├── index.html              # Live detection page
│   ├── dashboard.html          # Analytics dashboard
│   └── evaluation.html         # Model evaluation page
│
├── data/
│   ├── slots/                  # Saved slot layouts (JSON)
│   ├── analytics.db            # SQLite database
│   └── UFPR04/                 # PKLot dataset (for evaluation)
│       ├── images/
│       ├── xml/
│       └── slots.json
│
├── models/
│   └── yolov8n.pt              # YOLOv8 Nano model
│
└── static/
    ├── uploads/                # Uploaded images/videos
    └── frames/                 # Processed video frames
```

---

## 🔧 Configuration

### Video Processing

Edit `src/video_processor.py`:

```python
def process_video(video_path, slot_path, frame_skip=10, max_frames=100):
```

- `frame_skip`: Process every Nth frame (10 = every 10th frame)
- `max_frames`: Stop after processing this many frames

### IoU Threshold

Edit `src/occupancy.py`:

```python
class OccupancyDetector:
    def __init__(self, slots, iou_threshold=0.3):
```

- `iou_threshold`: Minimum IoU to mark a slot as occupied (0.3 = 30% overlap)

---

## 📊 Analytics Dashboard

Access at **http://localhost:5000/dashboard**

### Features

- **Live Stats**: Latest occupancy snapshot
- **Peak Hours**: Bar chart showing busiest hours
- **Weather Impact**: Occupancy by weather condition
- **Daily Trend**: Line chart of occupancy over time
- **Date Range Filter**: Analyze specific periods
- **CSV Export**: Download filtered data

### Data Source

Analytics are powered by the **PKLot UFPR04 dataset** (3791 images with XML ground truth labels). The `tools/preprocess_pklot.py` script parses all XML files and populates the SQLite database with historical occupancy data.

---

## 🎯 Model Evaluation

Access at **http://localhost:5000/evaluation**

### What It Does

Runs YOLOv8 detection on ~100 sampled PKLot images, compares predictions against XML ground truth using IoU ≥ 0.3, and computes:

- **Accuracy**: (TP + TN) / Total
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: Harmonic mean of Precision & Recall

### Per-Slot Analysis

Shows which specific slots are detected most accurately, and which slots are most frequently occupied in the ground truth data.

---

## 🛠️ API Endpoints

### Detection

- `POST /upload` — Upload image/video for detection
- `POST /save_slots` — Save slot polygons for a parking lot
- `GET /get_slots/<lot_name>` — Retrieve saved slots

### Analytics

- `GET /api/current_status` — Latest occupancy snapshot
- `GET /api/hourly_avg?from=YYYY-MM-DD&to=YYYY-MM-DD` — Peak hours
- `GET /api/daily_trend?from=YYYY-MM-DD&to=YYYY-MM-DD` — Daily trend
- `GET /api/weather_stats?from=YYYY-MM-DD&to=YYYY-MM-DD` — Weather impact
- `GET /api/export_csv?from=YYYY-MM-DD&to=YYYY-MM-DD` — Download CSV

### Evaluation

- `GET /api/run_evaluation` — Run model evaluation
- `GET /api/slot_utilization` — Per-slot utilization stats

---

## 🐛 Troubleshooting

### "Wrong predictions" / "All slots vacant"

**Cause**: Slot coordinates don't match the image resolution.

**Solution**: When defining a new parking lot, ensure you:
1. Check "New Parking Lot?"
2. Draw slots on the **uploaded image** (not a different image)
3. Click **Save Slots** before detecting

The system saves slots at the original image resolution, so they must be drawn on the same image you're detecting.

### Video processing is slow

**Cause**: Large video files (4K resolution, long duration).

**Solution**:
- Reduce `frame_skip` (process fewer frames)
- Reduce `max_frames` (stop earlier)
- Use lower resolution videos (1080p or 720p)

### Model not loading

**Cause**: Missing `models/yolov8n.pt` file.

**Solution**:
```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # Downloads automatically
```
Then move the downloaded file to `models/` directory.

---

## 📝 License

MIT License

---

## 🙏 Credits

- **YOLOv8**: [Ultralytics](https://github.com/ultralytics/ultralytics)
- **PKLot Dataset**: [UFPR Parking Lot Database](http://web.inf.ufpr.br/vri/databases/parking-lot-database/)
- **Flask**: [Pallets Projects](https://flask.palletsprojects.com/)

---

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ for smarter parking management**
