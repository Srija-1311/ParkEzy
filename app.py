import os
import io
import csv
import sqlite3
import cv2

from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename

from src.analytics_db import init_db, log_occupancy, get_slot_utilization
from src.detect_cars import CarDetector
from src.occupancy import OccupancyDetector
from src.slot_utils import load_slots
from src.visualize import draw_results
from tools.annotate_slots import annotate
from src.video_processor import process_video

init_db()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/uploads"
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

car_detector = CarDetector("models/yolov8n.pt")

ALLOWED = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


def get_db():
    return sqlite3.connect("data/analytics.db")


# ── IMAGE ───────────────────────────────────────

def process_image_api(path, new_lot):
    filename = os.path.basename(path).split('.')[0]
    slot_path = f"data/slots/{filename}.json"

    if new_lot:
        annotate(path)

    if not os.path.exists(slot_path):
        slot_path = "data/slots/frame.json"

    slots = load_slots(slot_path)
    occupancy_detector = OccupancyDetector(slots)

    frame = cv2.imread(path)

    boxes = car_detector.detect(frame)
    predictions = occupancy_detector.predict(boxes)

    total = len(predictions)
    occupied = sum(predictions.values())
    vacant = total - occupied
    rate = round((occupied / total) * 100, 2) if total else 0

    log_occupancy(occupied, vacant)

    output = draw_results(frame, slots, predictions)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], "output.jpg")
    cv2.imwrite(output_path, output)

    return jsonify({
        "success": True,
        "image_path": output_path,
        "total_slots": total,
        "vacant": vacant,
        "occupied": occupied,
        "occupancy_rate": rate
    })


# ── VIDEO ───────────────────────────────────────

def process_video_api(path, new_lot):
    filename = os.path.basename(path).split('.')[0]
    from src.analytics_db import clear_frame_data

    clear_frame_data()
    slot_path = f"data/slots/{filename}.json"

    cap = cv2.VideoCapture(path)

    ret, frame = cap.read()
    if not ret:
        return jsonify({"success": False, "error": "Cannot read video"})

    temp_frame = "static/frame.jpg"
    cv2.imwrite(temp_frame, frame)

    if new_lot:
        annotate(temp_frame)

    cap.release()

    if not os.path.exists(slot_path):
        slot_path = "data/slots/frame.json"

    results, sample_frames = process_video(path)

    if len(results) > 0:
        avg_available = sum([r["available"] for r in results]) // len(results)
    else:
        avg_available = 0

    return jsonify({
        "success": True,
        "total_slots": "Video Mode",
        "vacant": avg_available,
        "occupied": "Processed",
        "occupancy_rate": "Frame-wise",
        "frames": sample_frames
    })


# ── ROUTES ───────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")

        if not file or file.filename == "":
            return jsonify({"success": False, "error": "No file uploaded"})

        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Unsupported file type"})

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        ext = filename.rsplit('.', 1)[1].lower()
        new_lot = request.form.get("new_lot")

        if ext in ["jpg", "jpeg", "png"]:
            return process_image_api(filepath, new_lot)

        elif ext in ["mp4", "avi", "mov"]:
            return process_video_api(filepath, new_lot)

        else:
            return jsonify({"success": False, "error": "Invalid file type"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ── ANALYTICS GRAPH ─────────────────────────────

@app.route("/analytics-data")
def analytics_data():
    conn = sqlite3.connect("data/analytics.db")   # ✅ FIX
    rows = conn.execute("SELECT frame, available FROM frame_data").fetchall()
    conn.close()

    frames = [r[0] for r in rows]
    values = [r[1] for r in rows]

    return jsonify({
        "frames": frames,
        "values": values
    })


# ── RUN ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)