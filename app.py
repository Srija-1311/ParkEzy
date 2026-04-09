import os
import io
import csv
import sqlite3
from flask import Flask, render_template, request, jsonify, Response
import cv2
from werkzeug.utils import secure_filename

from src.analytics_db import init_db, log_occupancy, save_slot_utilization, get_slot_utilization
from src.detect_cars import CarDetector
from src.occupancy import OccupancyDetector
from src.slot_utils import load_slots
from src.visualize import draw_results
from src.evaluate import run_evaluation

# ── Init ──────────────────────────────────────────────────────────────────────

init_db()

app = Flask(__name__)
app.config['UPLOAD_FOLDER']      = "static/uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

car_detector      = CarDetector("models/yolov8n.pt")
slots             = load_slots("data/UFPR04/slots.json")
occupancy_detector = OccupancyDetector(slots)

ALLOWED = {'png', 'jpg', 'jpeg'}

# Cache evaluation result so re-visiting the page doesn't re-run YOLO
_eval_cache = None


def allowed_file(f):
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED


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


# ── Detection ─────────────────────────────────────────────────────────────────

@app.route("/detect", methods=["POST"])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    img = cv2.imread(filepath)
    if img is None:
        return jsonify({'error': 'Cannot read image'}), 400

    boxes       = car_detector.detect(img)
    predictions = occupancy_detector.predict(boxes)

    total    = len(predictions)
    occupied = sum(predictions.values())
    vacant   = total - occupied
    rate     = round((occupied / total) * 100, 1) if total else 0

    log_occupancy(occupied, vacant)

    output = draw_results(img, slots, predictions)
    cv2.imwrite(filepath, output)

    return jsonify({
        'success': True,
        'image_path': filepath,
        'total_slots': total,
        'occupied': occupied,
        'vacant': vacant,
        'occupancy_rate': rate
    })


# ── Analytics APIs ────────────────────────────────────────────────────────────

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
        'occupied': row[0], 'vacant': row[1],
        'total': row[2],
        'occupancy_rate': round(row[3] * 100, 1)
    })


@app.route("/api/hourly_avg")
def hourly_avg():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    conn = get_db()
    query = """
        SELECT hour, ROUND(AVG(occupancy_rate) * 100, 1)
        FROM occupancy_logs
        WHERE 1=1
    """
    params = []
    if date_from:
        query += " AND date >= ?"; params.append(date_from)
    if date_to:
        query += " AND date <= ?"; params.append(date_to)
    query += " GROUP BY hour ORDER BY hour"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([{'hour': r[0], 'avg_rate': r[1]} for r in rows])


@app.route("/api/daily_trend")
def daily_trend():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    conn  = get_db()
    query = """
        SELECT date, ROUND(AVG(occupancy_rate) * 100, 1)
        FROM occupancy_logs WHERE 1=1
    """
    params = []
    if date_from:
        query += " AND date >= ?"; params.append(date_from)
    if date_to:
        query += " AND date <= ?"; params.append(date_to)
    query += " GROUP BY date ORDER BY date"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([{'date': r[0], 'avg_rate': r[1]} for r in rows])


@app.route("/api/weather_stats")
def weather_stats():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    conn  = get_db()
    query = """
        SELECT weather, ROUND(AVG(occupancy_rate) * 100, 1), COUNT(*)
        FROM occupancy_logs
        WHERE weather != 'Unknown'
    """
    params = []
    if date_from:
        query += " AND date >= ?"; params.append(date_from)
    if date_to:
        query += " AND date <= ?"; params.append(date_to)
    query += " GROUP BY weather ORDER BY weather"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([{'weather': r[0], 'avg_rate': r[1], 'count': r[2]} for r in rows])


# ── Export CSV ────────────────────────────────────────────────────────────────

@app.route("/api/export_csv")
def export_csv():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    conn  = get_db()
    query = "SELECT timestamp, date, hour, weather, occupied, vacant, total, occupancy_rate FROM occupancy_logs WHERE 1=1"
    params = []
    if date_from:
        query += " AND date >= ?"; params.append(date_from)
    if date_to:
        query += " AND date <= ?"; params.append(date_to)
    query += " ORDER BY timestamp"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Date', 'Hour', 'Weather',
                     'Occupied', 'Vacant', 'Total', 'Occupancy Rate (%)'])
    for row in rows:
        writer.writerow([*row[:7], round(row[7] * 100, 2)])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=occupancy_report.csv'}
    )


# ── Evaluation ────────────────────────────────────────────────────────────────

@app.route("/api/run_evaluation")
def run_eval():
    global _eval_cache
    if _eval_cache is not None:
        return jsonify(_eval_cache)

    result = run_evaluation(car_detector, iou_threshold=0.3, sample_step=38)

    # Persist slot utilization to DB
    save_slot_utilization(result['per_slot'])

    # Remove per_slot from cache response (served separately)
    _eval_cache = {k: v for k, v in result.items() if k != 'per_slot'}
    _eval_cache['per_slot'] = result['per_slot']
    return jsonify(_eval_cache)


@app.route("/api/slot_utilization")
def slot_utilization():
    rows = get_slot_utilization()
    return jsonify(rows)


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large (max 16 MB)'}), 413


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
