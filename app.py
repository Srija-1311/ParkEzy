import os
import cv2
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from src.detect_cars import CarDetector
from src.occupancy import OccupancyDetector
from src.slot_utils import load_slots
from src.visualize import draw_results

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Paths
MODEL_PATH = "models/yolov8n.pt"
SLOTS_PATH = "data/UFPR04/slots.json"

# Initialize components
car_detector = CarDetector(MODEL_PATH)
slots = load_slots(SLOTS_PATH)
occupancy_detector = OccupancyDetector(slots)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def index():
    """Render main page"""
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():
    """Process uploaded image and detect parking occupancy"""
    try:
        # Validate file upload
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read image
        img = cv2.imread(filepath)
        
        if img is None:
            return jsonify({'error': 'Failed to read image'}), 400
        
        # Detect cars
        car_boxes = car_detector.detect(img)
        
        # Predict occupancy
        predictions = occupancy_detector.predict(car_boxes)
        
        # Calculate statistics
        total_slots = len(predictions)
        occupied_count = sum(predictions.values())
        vacant_count = total_slots - occupied_count
        
        # Draw results on image
        output_img = draw_results(img, slots, predictions)
        
        # Save processed image
        cv2.imwrite(filepath, output_img)
        
        # Return results
        return jsonify({
            'success': True,
            'image_path': filepath,
            'total_slots': total_slots,
            'occupied': occupied_count,
            'vacant': vacant_count,
            'occupancy_rate': round((occupied_count / total_slots) * 100, 1) if total_slots > 0 else 0
        })
    
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
