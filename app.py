import os
import io
import csv
import json
import sqlite3

import cv2
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from werkzeug.utils import secure_filename

from src.analytics_db import (
    init_db, log_occupancy, save_frame_data, clear_frame_data,
    save_slot_utilization, get_slot_utilization
)
from src.detect_cars import CarDetector
from src.occupancy import OccupancyDetector
from src.slot_utils import load_slots, save_slots
from src.visualize import draw_results
from src.video_processor import process_video_stream
from src.evaluate import run_evaluation

# ── Bootstrap ─────────────────────────────────────────────────────────────────

init_db()

app = Flask(__name__)
app.config['UPLOAD_FOLDER']      = "static/uploads"
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024   # 500 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("data/slots", exist_ok=True)
os.makedirs("static/frames", exist_ok=True)

car_detector = CarDetector("models/yolo11x.pt")

ALLOWED_IMAGE = {'png', 'jpg', 'jpeg'}
ALLOWED_VIDEO = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_ALL   = ALLOWED_IMAGE | ALLOWED_VIDEO

DEFAULT_SLOTS = "data/UFPR04/slots.json"

_eval_cache = None


def file_ext(filename):
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def normalise_name(name):
    """Normalise a lot/file name: strip, lowercase, replace spaces with underscores."""
    return name.strip().lower().replace(' ', '_')


def slot_path_for(stem):
    return f"data/slots/{stem}.json"


def find_slot_file(name):
    """
    Robustly find a slot JSON file for a given name.
    Tries: exact name, normalised name, original-filename stem.
    Returns the path if found, else None.
    """
    candidates = [
        slot_path_for(name),
        slot_path_for(normalise_name(name)),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def get_db():
    return sqlite3.connect("data/analytics.db")


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/evaluation")
def evaluation_page():
    return render_template("evaluation.html")


# ── Slot annotation ───────────────────────────────────────────────────────────

@app.route("/save_slots", methods=["POST"])
def save_slots_route():
    data     = request.get_json()
    lot_name = (data.get("lot_name") or "").strip()
    polygons = data.get("slots", [])

    if not lot_name:
        return jsonify({"success": False, "error": "lot_name is required"}), 400
    if not polygons:
        return jsonify({"success": False, "error": "No slots provided"}), 400

    # Normalise: spaces → underscores so filenames always match
    lot_name = normalise_name(lot_name)
    path = slot_path_for(lot_name)
    save_slots(path, polygons)
    return jsonify({"success": True, "saved": len(polygons), "path": path, "lot_name": lot_name})


@app.route("/get_slots/<lot_name>")
def get_slots_route(lot_name):
    path = slot_path_for(lot_name)
    if not os.path.exists(path):
        return jsonify({"slots": []})
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = list(data.values())
    return jsonify({"slots": data})


# ── Image upload & detect ─────────────────────────────────────────────────────

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")
        if not file or file.filename == "":
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        original_filename = file.filename                        # preserve before save
        filename = secure_filename(original_filename)
        ext      = file_ext(filename)

        if ext not in ALLOWED_ALL:
            return jsonify({"success": False, "error": "Unsupported file type"}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # lot_name is sent by the frontend when the user typed a name in the
        # "New Parking Lot" field.  If absent, fall back to the image stem.
        lot_name = (request.form.get("lot_name") or "").strip()
        stem          = filename.rsplit('.', 1)[0]           # secure stem
        original_stem = original_filename.rsplit('.', 1)[0]  # original stem (may have spaces)

        # Priority: explicit lot_name → secure stem → original stem → UFPR04 default
        # find_slot_file tries both exact and normalised (spaces→underscores) variants
        if lot_name:
            use_slots = find_slot_file(lot_name) or DEFAULT_SLOTS
        else:
            use_slots = (
                find_slot_file(stem) or
                find_slot_file(original_stem) or
                DEFAULT_SLOTS
            )

        if ext in ALLOWED_IMAGE:
            return _detect_image(filepath, use_slots)

        # Video: pass slot path so SSE stream can use it
        return jsonify({
            "success":    True,
            "mode":       "video",
            "filepath":   filepath,
            "filename":   filename,
            "slot_path":  use_slots
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


def _read_image(filepath):
    """
    Read an image file robustly.
    cv2.imread handles JPEG/PNG/BMP/TIFF.
    Falls back to PIL for modern formats like AVIF, HEIC, WebP.
    Always returns a BGR numpy array, or None on failure.
    """
    import cv2
    import numpy as np

    img = cv2.imread(filepath)
    if img is not None:
        return img

    # cv2 failed — try PIL (handles AVIF, HEIC, WebP, etc.)
    try:
        from PIL import Image
        img_pil = Image.open(filepath).convert('RGB')
        img_np  = np.array(img_pil)
        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    except Exception:
        return None


def _detect_image(filepath, slot_path):
    img = _read_image(filepath)
    if img is None:
        return jsonify({"success": False, "error": "Cannot read image — unsupported format or corrupted file"}), 400

    slots              = load_slots(slot_path)
    occupancy_detector = OccupancyDetector(slots)

    boxes       = car_detector.detect(img)
    predictions = occupancy_detector.predict(boxes)

    total    = len(predictions)
    occupied = sum(predictions.values())
    vacant   = total - occupied
    rate     = round((occupied / total) * 100, 1) if total else 0

    log_occupancy(occupied, vacant)

    output   = draw_results(img, slots, predictions)
    out_path = os.path.join(app.config['UPLOAD_FOLDER'], "output.jpg")
    cv2.imwrite(out_path, output)

    # Human-readable slot source label — show the lot name, not the full path
    if slot_path == DEFAULT_SLOTS:
        slots_used = "UFPR04 (default)"
    else:
        slots_used = os.path.basename(slot_path).replace(".json", "")

    return jsonify({
        "success":        True,
        "mode":           "image",
        "image_url":      "/" + out_path.replace("\\", "/"),
        "total_slots":    total,
        "occupied":       occupied,
        "vacant":         vacant,
        "occupancy_rate": rate,
        "slots_used":     slots_used
    })


# ── Video SSE stream ──────────────────────────────────────────────────────────

@app.route("/stream_video")
def stream_video():
    """
    SSE endpoint. Browser connects here after uploading a video.
    Streams one JSON event per processed frame.
    """
    filepath  = request.args.get("filepath", "")
    filename  = request.args.get("filename", "")
    slot_path = request.args.get("slot_path", "")

    if not filepath or not os.path.exists(filepath):
        def err():
            yield f'data: {json.dumps({"error":"File not found"})}\n\n'
        return Response(stream_with_context(err()), mimetype="text/event-stream")

    # Use the slot_path passed from /upload if valid, otherwise resolve here
    if slot_path and os.path.exists(slot_path):
        use_slots = slot_path
    else:
        stem      = filename.rsplit('.', 1)[0] if '.' in filename else filename
        lot_name  = request.args.get("lot_name", "").strip()
        if lot_name and os.path.exists(slot_path_for(lot_name)):
            use_slots = slot_path_for(lot_name)
        elif os.path.exists(slot_path_for(stem)):
            use_slots = slot_path_for(stem)
        else:
            use_slots = DEFAULT_SLOTS

    clear_frame_data()

    return Response(
        stream_with_context(process_video_stream(filepath, use_slots)),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


# ── Analytics APIs ────────────────────────────────────────────────────────────

@app.route("/api/saved_lots")
def saved_lots():
    """Return list of saved parking lot names (slot JSON files in data/slots/)."""
    files = [
        f.replace(".json", "")
        for f in os.listdir("data/slots")
        if f.endswith(".json")
    ]
    return jsonify(sorted(files))


@app.route("/api/current_status")
def current_status():
    conn = get_db()
    row  = conn.execute("""
        SELECT occupied, vacant, total, occupancy_rate
        FROM occupancy_logs ORDER BY id DESC LIMIT 1
    """).fetchone()
    conn.close()
    if not row:
        return jsonify({})
    return jsonify({
        "occupied": row[0], "vacant": row[1],
        "total": row[2],
        "occupancy_rate": round(row[3] * 100, 1)
    })


@app.route("/api/hourly_avg")
def hourly_avg():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    conn   = get_db()
    q      = "SELECT hour, ROUND(AVG(occupancy_rate)*100,1) FROM occupancy_logs WHERE 1=1"
    p      = []
    if date_from: q += " AND date >= ?"; p.append(date_from)
    if date_to:   q += " AND date <= ?"; p.append(date_to)
    q += " GROUP BY hour ORDER BY hour"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return jsonify([{"hour": r[0], "avg_rate": r[1]} for r in rows])


@app.route("/api/daily_trend")
def daily_trend():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    conn   = get_db()
    q      = "SELECT date, ROUND(AVG(occupancy_rate)*100,1) FROM occupancy_logs WHERE 1=1"
    p      = []
    if date_from: q += " AND date >= ?"; p.append(date_from)
    if date_to:   q += " AND date <= ?"; p.append(date_to)
    q += " GROUP BY date ORDER BY date"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return jsonify([{"date": r[0], "avg_rate": r[1]} for r in rows])


@app.route("/api/weather_stats")
def weather_stats():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    conn   = get_db()
    q      = "SELECT weather, ROUND(AVG(occupancy_rate)*100,1), COUNT(*) FROM occupancy_logs WHERE weather != 'Unknown'"
    p      = []
    if date_from: q += " AND date >= ?"; p.append(date_from)
    if date_to:   q += " AND date <= ?"; p.append(date_to)
    q += " GROUP BY weather ORDER BY weather"
    rows = conn.execute(q, p).fetchall()
    conn.close()
    return jsonify([{"weather": r[0], "avg_rate": r[1], "count": r[2]} for r in rows])


@app.route("/api/export_csv")
def export_csv():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    conn   = get_db()
    q      = "SELECT timestamp, date, hour, weather, occupied, vacant, total, occupancy_rate FROM occupancy_logs WHERE 1=1"
    p      = []
    if date_from: q += " AND date >= ?"; p.append(date_from)
    if date_to:   q += " AND date <= ?"; p.append(date_to)
    q += " ORDER BY timestamp"
    rows = conn.execute(q, p).fetchall()
    conn.close()

    out = io.StringIO()
    w   = csv.writer(out)
    w.writerow(['Timestamp','Date','Hour','Weather','Occupied','Vacant','Total','Occupancy Rate (%)'])
    for row in rows:
        w.writerow([*row[:7], round(row[7] * 100, 2)])
    out.seek(0)
    return Response(out.getvalue(), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=occupancy_report.csv'})


# ── Evaluation ────────────────────────────────────────────────────────────────

@app.route("/api/run_evaluation")
def run_eval():
    global _eval_cache
    if _eval_cache is not None:
        return jsonify(_eval_cache)
    result      = run_evaluation(car_detector, iou_threshold=0.1, sample_step=38)
    save_slot_utilization(result['per_slot'])
    _eval_cache = result
    return jsonify(_eval_cache)


@app.route("/api/slot_utilization")
def slot_utilization():
    return jsonify(get_slot_utilization())


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    return jsonify({"success": False, "error": "File too large (max 500 MB)"}), 413


if __name__ == "__main__":
    # threaded=True is required for SSE to work alongside other requests
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
