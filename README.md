# 🅿 ParkEzy — Smart Parking Detection System

> AI-powered parking occupancy detection using **YOLO11x** object detection and **spatial IoU polygon mapping** — supports images, videos, auto-detected slot boundaries, and historical analytics.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Flow](#project-flow)
- [Slot Definition — Academic Context](#slot-definition--academic-context)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Pages & Routes](#pages--routes)
- [Auto-Detect Slots](#auto-detect-slots--how-it-works)
- [Model Details](#model-details)
- [Analytics Data Source](#analytics-data-source)
- [Authentication](#authentication)
- [Tech Stack](#tech-stack)

---

## Overview

ParkEzy is a full-stack web application that determines which parking slots are **occupied** or **vacant** from a fixed-camera aerial image or video. It combines:

- **YOLO11x** (latest Ultralytics model) for vehicle detection at high resolution
- **Shapely polygon IoU** for spatial slot-occupancy matching
- **Three slot definition modes** — auto-detect, manual draw, or reuse saved layouts
- **Real-time SSE video streaming** for frame-by-frame analysis
- **Historical analytics** powered by the PKLot UFPR04 dataset (3,791 annotated images)
- **User authentication** with bcrypt + Flask-Login

---

## Features

| Feature | Description |
|---|---|
| 🤖 **Auto-Detect Slots** | YOLO11x detects vehicles, clusters them into rows, fills gaps between cars to infer empty slots, and generates polygon boundaries for the full parking grid — no manual clicking needed for standard layouts |
| ✏️ **Manual Slot Editor** | Browser-based canvas editor — click 4 corners per slot, slots saved at original image resolution and reused automatically for every future upload from the same camera |
| 📋 **Reuse Saved Layouts** | Once a lot is annotated, select it from a dropdown — the system matches by filename or explicit lot name |
| 🎬 **Video Processing** | Frame-by-frame analysis with real-time SSE streaming, occupancy-over-time chart, and a scrollable frame gallery with click-to-enlarge lightbox |
| 📐 **Spatial IoU Mapping** | Each slot is a quadrilateral polygon. Occupancy = IoU ≥ 0.3 between any YOLO bounding box and the slot polygon. Works for any camera angle and irregular slot shapes |
| 📊 **Analytics Dashboard** | Peak hours bar chart, weather impact comparison (Sunny/Cloudy/Rainy), daily occupancy trend line chart. Date range filter + CSV export |
| 📈 **Model Evaluation** | Accuracy, Precision, Recall, F1 against PKLot XML ground truth. Confusion matrix + per-slot accuracy breakdown with utilization badges |
| 🔐 **Authentication** | Register/Login/Logout with bcrypt password hashing. All detection and analytics routes are protected |
| 🌐 **Multi-format Support** | JPG, PNG, AVIF, WebP images + MP4, AVI, MOV videos. PIL fallback handles modern formats OpenCV cannot read |
| 🏠 **Home Dashboard** | Landing page showing live occupancy stats, feature overview, and step-by-step how-it-works guide |

---

## Project Flow

```
                        ┌─────────────────────┐
                        │   User Registers /   │
                        │   Logs In            │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  Upload Image/Video  │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │         SLOT DEFINITION (one-time)       │
              │                                          │
              │  Mode 1 ── Use Saved Layout              │
              │            └─► Load JSON from data/slots │
              │                                          │
              │  Mode 2 ── Auto-Detect                   │
              │            └─► YOLO detects vehicles     │
              │                └─► Row clustering        │
              │                    └─► Gap fill          │
              │                        └─► Polygons      │
              │                                          │
              │  Mode 3 ── Draw Manually                 │
              │            └─► 4-click canvas editor     │
              │                └─► Save to data/slots    │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │       YOLO11x DETECTION (imgsz=1920)     │
              │  • All detections returned (conf ≥ 0.1)  │
              │  • No class filter — slot-IoU decides    │
              │  • Handles aerial misclassification       │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │          IoU OCCUPANCY LOGIC             │
              │  For each slot polygon:                  │
              │    max IoU with any bbox ≥ 0.3           │
              │      → OCCUPIED  (red overlay)           │
              │    otherwise                             │
              │      → VACANT    (green overlay)         │
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────▼────────────────────┐
              │               RESULTS                    │
              │  Image  → annotated output + stats       │
              │  Video  → SSE stream + chart + gallery   │
              │  Both   → logged to SQLite analytics DB  │
              └─────────────────────────────────────────┘
```

---

## Slot Definition — Academic Context

Defining parking slot boundaries is a **one-time setup step required by every published parking detection system**. This is not a limitation — it is the accepted standard across the entire field:

| System / Paper | Slot Definition Method |
|---|---|
| **PKLot dataset** (de Almeida et al., 2015) — the dataset used in this project | XML files with manually annotated polygon contours. Took researchers weeks to annotate 3 parking lots |
| **CNRPark** (Amato et al., 2016) | Manual bounding boxes drawn once per camera view |
| **UNICAMP YOLO11 paper** (arxiv:2412.01983, 2024) | "Existing methods still rely on **fixed polygonal ROI selections**" — their own words |
| **OcpDet / PakSta** (arxiv:2208.08220, 2022) | "Traditional methods use the classification backbone to predict spots from a **manually labeled grid**" |
| **APSD-OC** (arxiv:2308.08192, 2023) — closest to ParkEzy's auto-detect | Clusters YOLO detections over **50–100 frames** to infer slots; requires a video series with varying occupancy |
| **Geometric line detection** (ResearchGate, 2018) | Detects painted parking lines using LSD + Hough transforms — only works on near-empty lots with visible markings |

**ParkEzy's approach:** Auto-detect applies the same row-clustering idea as APSD-OC but on a **single frame**, making it faster and simpler. When auto-detect is insufficient (irregular layouts, low occupancy, occluded lines), the **manual draw mode** provides a reliable fallback — consistent with how every major published system handles this problem.

---

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### 1. Clone and install
```bash
git clone https://github.com/Srija-1311/ParkEzy.git
cd ParkEzy
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Download YOLO11x model
```python
# Run once — downloads automatically from Ultralytics
from ultralytics import YOLO
YOLO('yolo11x.pt')
```
Then move `yolo11x.pt` → `models/yolo11x.pt`

### 3. Populate the analytics database
```bash
# Parses all 3,791 PKLot XML files into SQLite
python tools/preprocess_pklot.py
```

### 4. Run the app
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```
Register an account → Login → Start detecting.

---

## Project Structure

```
ParkEzy/
│
├── app.py                        # Flask application — all routes, auth, detection pipeline
├── requirements.txt              # Python dependencies
├── README.md
│
├── src/
│   ├── detect_cars.py            # YOLO11x wrapper (imgsz=1920, conf=0.1, all classes)
│   ├── occupancy.py              # Slot-first IoU occupancy detector (threshold=0.3)
│   ├── auto_slots.py             # Auto-detect slot polygons via row clustering + gap fill
│   ├── visualize.py              # Draw colored polygon overlays on images/frames
│   ├── video_processor.py        # SSE generator for frame-by-frame video streaming
│   ├── slot_utils.py             # Load/save slot JSON (handles list and dict formats)
│   ├── analytics_db.py           # SQLite: users, occupancy_logs, slot_utilization, frame_data
│   └── evaluate.py               # PKLot XML ground truth evaluation (Accuracy/Precision/Recall/F1)
│
├── templates/
│   ├── auth_base.html            # Shared layout for login/register pages
│   ├── login.html                # Login form
│   ├── register.html             # Registration form
│   ├── home.html                 # Landing page — live stats, features, how-it-works
│   ├── index.html                # Detection page — upload, slot definition, results
│   ├── dashboard.html            # Analytics dashboard — charts, filter, CSV export
│   └── evaluation.html           # Model evaluation — metrics, confusion matrix, slot table
│
├── data/
│   ├── slots/                    # Saved slot layouts (one JSON file per parking lot)
│   │   ├── parking_1.json
│   │   ├── parking_video_1.json
│   │   └── ...
│   ├── analytics.db              # SQLite database (gitignored — generated at runtime)
│   └── UFPR04/
│       ├── images/               # 3,791 parking lot images (gitignored)
│       ├── xml/                  # Ground truth XML annotations (gitignored)
│       └── slots.json            # Slot polygons rebuilt from XML contours
│
├── models/
│   └── yolo11x.pt                # YOLO11x weights (gitignored — download separately)
│
├── static/
│   ├── uploads/                  # Uploaded images and videos
│   └── frames/                   # Processed video frames (gitignored)
│
└── tools/
    ├── preprocess_pklot.py       # Parse PKLot XML → SQLite with weather mapping
    ├── rebuild_slots_from_xml.py # Rebuild UFPR04/slots.json from XML contour points
    └── create_slots_json.py      # Legacy desktop annotation tool (OpenCV window)
```

---

## Pages & Routes

### Web Pages

| Route | Page | Auth Required |
|---|---|---|
| `/` | Redirects to `/home` or `/login` | — |
| `/login` | Login form | No |
| `/register` | Registration form | No |
| `/logout` | Clears session, redirects to login | Yes |
| `/home` | Landing page with live stats and feature overview | Yes |
| `/detect` | Upload image/video, define slots, view results | Yes |
| `/dashboard` | Analytics: peak hours, weather impact, daily trend | Yes |
| `/evaluation` | Model accuracy evaluation against PKLot ground truth | Yes |

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/upload` | POST | Upload image/video; returns detection result or video filepath for SSE |
| `/stream_video` | GET (SSE) | Stream frame-by-frame video results as Server-Sent Events |
| `/save_slots` | POST | Save slot polygon array for a named parking lot |
| `/get_slots/<name>` | GET | Retrieve saved slot polygons for a lot |
| `/api/auto_detect_slots` | POST | Run YOLO + row clustering to auto-generate slot candidates |
| `/api/saved_lots` | GET | List all saved parking lot names |
| `/api/current_status` | GET | Latest occupancy snapshot from the database |
| `/api/hourly_avg` | GET | Average occupancy by hour of day (filterable by date range) |
| `/api/daily_trend` | GET | Average occupancy per date (filterable by date range) |
| `/api/weather_stats` | GET | Average occupancy by weather condition |
| `/api/export_csv` | GET | Download occupancy logs as CSV (filterable by date range) |
| `/api/run_evaluation` | GET | Run YOLO11x evaluation against PKLot XML ground truth |
| `/api/slot_utilization` | GET | Per-slot utilization stats from last evaluation run |

---

## Auto-Detect Slots — How It Works

For large parking lots, manually clicking 4 corners per slot is impractical. The auto-detect pipeline infers slot boundaries from YOLO vehicle detections:

```
YOLO11x detects vehicles
         │
         ▼
Row clustering (DBSCAN by Y-coordinate)
  • Groups bboxes within median_height × 0.6 of each other
  • Each cluster = one row of parking spaces
         │
         ▼
Gap filling (per row)
  • Sort cars by X within each row
  • Compute median slot width from detected cars
  • For each gap between consecutive cars:
      gap / median_width - 1 = number of empty slots to insert
  • Extend row left and right by 1 slot if space allows
         │
         ▼
Overlap removal
  • Remove polygons with IoU > 0.5 against each other
  • Keep the larger polygon when duplicates exist
         │
         ▼
Returns: polygons for ALL slots (occupied + vacant)
```

**Why this matters:** Without gap filling, only occupied slots are generated (every auto-detected slot has a car in it by definition), resulting in 0 vacant slots reported. Gap filling solves this by extrapolating the full row grid.

**When to use manual mode instead:**
- Irregular or diagonal parking layouts
- Very low occupancy (few cars to cluster from)
- Lots where painted lines are the primary reference
- Any case where auto-detect produces misaligned polygons

---

## Model Details

| Property | Value | Reason |
|---|---|---|
| Model | YOLO11x (109 MB) | Largest/most accurate YOLO11 variant |
| Input size (`imgsz`) | 1920 px | Preserves detail in 4K aerial footage; cars are ~150px at native resolution, ~25px at 640px |
| Confidence threshold | 0.1 | Low threshold — slot-IoU decides occupancy, not class confidence |
| Class filtering | None (all classes) | Aerial cars are often misclassified as cell phones, bottles etc. by COCO-trained models; slot-IoU handles this automatically |
| Occupancy IoU threshold | 0.3 | Minimum overlap between a YOLO bbox and a slot polygon to mark the slot occupied |

---

## Analytics Data Source

The analytics dashboard is powered by the **PKLot UFPR04 dataset**:

- **3,791 images** of a university parking lot captured over 30 days
- Each image has an XML file with per-slot occupancy ground truth (`occupied="1"` or `occupied="0"`)
- Weather conditions (Sunny / Cloudy / Rainy) mapped from known date ranges in the dataset documentation
- Run `tools/preprocess_pklot.py` once to parse all XML files into the SQLite `occupancy_logs` table

The analytics data is **ground truth labels from the dataset**, not YOLO predictions — this gives accurate historical patterns for peak hours, weather impact, and daily trends.

---

## Authentication

| Component | Implementation |
|---|---|
| Password hashing | bcrypt via Flask-Bcrypt |
| Session management | Flask-Login with `remember=True` |
| Protected routes | `@login_required` decorator on all detection/analytics/evaluation routes |
| User storage | SQLite `users` table (id, username, email, password_hash, created) |

Register at `/register` → Login at `/login` → All features unlocked.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10, Flask 3.0 |
| Object Detection | YOLO11x (Ultralytics 8.4.41) |
| Computer Vision | OpenCV 4.9, PIL/Pillow |
| Geometry | Shapely 2.0 |
| Database | SQLite (via Python stdlib) |
| Auth | Flask-Login 0.6, Flask-Bcrypt 1.0 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js 4.4 |
| Video Streaming | Server-Sent Events (SSE) |

---

## Dataset

**PKLot — Parking Lot Database**
- Source: Federal University of Paraná (UFPR), Brazil
- Subset used: UFPR04 (one parking lot, 3,791 images)
- Annotations: XML files with rotated rectangle + 4-point contour per slot
- Reference: de Almeida et al., "PKLot — A robust dataset for parking lot classification", *Expert Systems with Applications*, 2015

---

## License

MIT License — free for academic and commercial use.

---

*ParkEzy · Built with Flask · YOLO11x · OpenCV · Shapely · SQLite · Chart.js*
