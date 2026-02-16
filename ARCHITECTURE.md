# System Architecture

Visual overview of the Smart Parking System architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                      (Web Browser)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Request
                         │ (Upload Image)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK WEB SERVER                          │
│                       (app.py)                               │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │  Validation  │  │ Error Handler│     │
│  │   GET /      │  │  File Type   │  │   JSON API   │     │
│  │   POST /detect│  │  File Size   │  │   Responses  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Process Image
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  PROCESSING PIPELINE                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Load Image (OpenCV)                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  2. Detect Cars (YOLOv8)                             │  │
│  │     - CarDetector class                              │  │
│  │     - Returns bounding boxes                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  3. Check Occupancy (Shapely)                        │  │
│  │     - OccupancyDetector class                        │  │
│  │     - Intersection analysis                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  4. Visualize Results (OpenCV)                       │  │
│  │     - Draw polygons                                  │  │
│  │     - Color coding                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  5. Calculate Statistics                             │  │
│  │     - Total, Occupied, Vacant                        │  │
│  │     - Occupancy Rate                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ JSON Response
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSE TO USER                          │
│                                                              │
│  {                                                           │
│    "success": true,                                          │
│    "image_path": "static/uploads/result.jpg",               │
│    "total_slots": 100,                                       │
│    "occupied": 45,                                           │
│    "vacant": 55,                                             │
│    "occupancy_rate": 45.0                                    │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  app.py                                                      │
│  ├── Flask Application                                       │
│  ├── Route Handlers                                          │
│  ├── Request Validation                                      │
│  └── Response Formatting                                     │
│                                                              │
│  config.py                                                   │
│  ├── Configuration Management                                │
│  ├── Environment Variables                                   │
│  └── Settings                                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  src/detect_cars.py                                          │
│  └── CarDetector                                             │
│      ├── Load YOLOv8 Model                                   │
│      ├── Detect Vehicles                                     │
│      └── Return Bounding Boxes                               │
│                                                              │
│  src/occupancy.py                                            │
│  └── OccupancyDetector                                       │
│      ├── Load Slot Polygons                                  │
│      ├── Calculate Intersections                             │
│      └── Determine Occupancy                                 │
│                                                              │
│  src/visualize.py                                            │
│  └── draw_results()                                          │
│      ├── Draw Polygons                                       │
│      ├── Apply Colors                                        │
│      └── Add Labels                                          │
│                                                              │
│  src/slot_utils.py                                           │
│  └── load_slots()                                            │
│      ├── Read JSON File                                      │
│      └── Parse Coordinates                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  models/yolov8n.pt                                           │
│  └── Pre-trained YOLOv8 Model                                │
│                                                              │
│  data/UFPR04/slots.json                                      │
│  └── Parking Slot Coordinates                                │
│                                                              │
│  static/uploads/                                             │
│  └── Uploaded & Processed Images                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────┐
│  Image   │
│  Upload  │
└────┬─────┘
     │
     ▼
┌─────────────────┐
│  File           │
│  Validation     │
│  - Type check   │
│  - Size check   │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Save to        │
│  static/uploads │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Load Image     │
│  (OpenCV)       │
└────┬────────────┘
     │
     ▼
┌─────────────────┐      ┌──────────────┐
│  YOLOv8         │◄─────┤ Model File   │
│  Detection      │      │ yolov8n.pt   │
└────┬────────────┘      └──────────────┘
     │
     │ Bounding Boxes
     ▼
┌─────────────────┐      ┌──────────────┐
│  Occupancy      │◄─────┤ Slots JSON   │
│  Analysis       │      │ slots.json   │
└────┬────────────┘      └──────────────┘
     │
     │ Predictions
     ▼
┌─────────────────┐
│  Visualization  │
│  - Draw slots   │
│  - Color code   │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Save Result    │
│  Image          │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Calculate      │
│  Statistics     │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  JSON Response  │
│  to Client      │
└─────────────────┘
```

## Class Diagram

```
┌─────────────────────────┐
│    CarDetector          │
├─────────────────────────┤
│ - model: YOLO           │
│ - CAR_CLASS: int        │
├─────────────────────────┤
│ + __init__(model_path)  │
│ + detect(img) → boxes   │
└─────────────────────────┘
            │
            │ uses
            ▼
┌─────────────────────────┐
│  OccupancyDetector      │
├─────────────────────────┤
│ - slots: dict           │
├─────────────────────────┤
│ + __init__(slots)       │
│ + predict(boxes) → dict │
└─────────────────────────┘
            │
            │ uses
            ▼
┌─────────────────────────┐
│    Visualization        │
├─────────────────────────┤
│ + draw_results()        │
│   - img                 │
│   - slots               │
│   - predictions         │
│   → annotated_img       │
└─────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND                                │
├─────────────────────────────────────────────────────────────┤
│  HTML5  │  CSS3  │  JavaScript (Vanilla)                    │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND                                 │
├─────────────────────────────────────────────────────────────┤
│  Python 3.8+  │  Flask 3.0  │  Werkzeug                     │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI/ML                                   │
├─────────────────────────────────────────────────────────────┤
│  YOLOv8 (Ultralytics)  │  PyTorch (backend)                 │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      COMPUTER VISION                         │
├─────────────────────────────────────────────────────────────┤
│  OpenCV  │  NumPy  │  Shapely (Geometry)                    │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PRODUCTION                              │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Internet   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Nginx      │  ← Reverse Proxy
│   (Port 80)  │     SSL/TLS
└──────┬───────┘     Static Files
       │
       ▼
┌──────────────┐
│  Gunicorn    │  ← WSGI Server
│  (4 workers) │     Load Balancing
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Flask App   │  ← Application
│  (app.py)    │     Business Logic
└──────┬───────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌──────────┐  ┌──────────┐
│  Models  │  │   Data   │
│  YOLOv8  │  │  Slots   │
└──────────┘  └──────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                         │
└─────────────────────────────────────────────────────────────┘

Layer 1: Network
├── HTTPS/SSL
├── Firewall Rules
└── Rate Limiting

Layer 2: Application
├── File Type Validation
├── File Size Limits
├── Secure Filename Handling
└── Error Message Sanitization

Layer 3: Data
├── Input Validation
├── Path Traversal Prevention
└── Temporary File Cleanup

Layer 4: Configuration
├── Environment Variables
├── Secret Key Management
└── Debug Mode Control
```

## Performance Considerations

```
┌─────────────────────────────────────────────────────────────┐
│                      OPTIMIZATION                            │
└─────────────────────────────────────────────────────────────┘

Model Loading
└── Loaded once at startup (singleton pattern)

Slots Data
└── Cached in memory after first load

Image Processing
├── Resize large images
├── Optimize YOLO inference
└── Efficient polygon operations

Concurrency
├── Multiple Gunicorn workers
├── Async processing (future)
└── Request queuing (future)
```

## Scalability

```
Current: Single Server
├── 1 Flask instance
├── 4 Gunicorn workers
└── ~10-20 concurrent users

Future: Horizontal Scaling
├── Load Balancer
├── Multiple App Servers
├── Shared Storage (S3/NFS)
└── Redis Cache
└── Database for results
```

## Monitoring Points

```
Application Metrics
├── Request count
├── Response time
├── Error rate
└── Upload size

System Metrics
├── CPU usage
├── Memory usage
├── Disk space
└── Network I/O

Business Metrics
├── Detection accuracy
├── Processing time
├── User activity
└── Occupancy trends
```

---

This architecture provides a solid foundation for a production-ready parking detection system with room for future enhancements and scaling.
