# Installation Guide

Complete installation instructions for the Smart Parking System.

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 2GB available
- **Disk Space**: 2GB free
- **Internet**: Required for initial setup

### Recommended Requirements
- **Python**: 3.9 or 3.10
- **RAM**: 4GB available
- **Disk Space**: 5GB free
- **GPU**: Optional, for faster processing

## Installation Methods

### Method 1: Quick Start (Recommended)

#### Windows
```bash
# Double-click start.bat or run:
start.bat
```

#### Linux/Mac
```bash
# Make script executable
chmod +x start.sh

# Run script
./start.sh
```

### Method 2: Manual Installation

#### Step 1: Install Python

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run installer
3. Check "Add Python to PATH"
4. Complete installation

**macOS:**
```bash
# Using Homebrew
brew install python@3.9
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

#### Step 2: Clone or Download Repository

**Using Git:**
```bash
git clone <repository-url>
cd smart-parking-system
```

**Or download ZIP:**
1. Download ZIP file
2. Extract to desired location
3. Open terminal in extracted folder

#### Step 3: Create Virtual Environment

```bash
# Windows
python -m venv venv

# Linux/Mac
python3 -m venv venv
```

#### Step 4: Activate Virtual Environment

**Windows (CMD):**
```bash
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Ultralytics (YOLOv8)
- OpenCV (image processing)
- NumPy (numerical operations)
- Shapely (geometry operations)
- Werkzeug (utilities)

#### Step 6: Verify Installation

```bash
python utils.py
```

Expected output:
```
==================================================
Smart Parking System - Setup Validation
==================================================
✓ All required files and directories found!
✓ Parking slots loaded: [number] slots
✓ Sample images available: [number]
✓ System is ready to run!
```

#### Step 7: Run Tests (Optional)

```bash
python test_system.py
```

All tests should pass.

#### Step 8: Start Application

```bash
python app.py
```

Or:
```bash
python run.py
```

#### Step 9: Access Application

Open browser and navigate to:
```
http://localhost:5000
```

## Troubleshooting

### Python Not Found

**Windows:**
- Reinstall Python with "Add to PATH" checked
- Or add Python to PATH manually

**Linux/Mac:**
- Use `python3` instead of `python`
- Install Python: `sudo apt install python3`

### Permission Denied (Linux/Mac)

```bash
chmod +x start.sh
sudo chown -R $USER:$USER .
```

### pip Not Found

```bash
# Windows
python -m ensurepip --upgrade

# Linux/Mac
sudo apt install python3-pip
```

### Virtual Environment Activation Failed

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Module Not Found Errors

```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port 5000 Already in Use

**Option 1: Change port**
```bash
export PORT=8080
python run.py
```

**Option 2: Kill process using port 5000**

Windows:
```bash
netstat -ano | findstr :5000
taskkill /PID [PID] /F
```

Linux/Mac:
```bash
lsof -ti:5000 | xargs kill -9
```

### Model File Not Found

The YOLOv8 model should be at `models/yolov8n.pt`. If missing:

```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # Will download automatically
```

Then move the downloaded file to `models/` directory.

### Slots JSON Not Found

Ensure `data/UFPR04/slots.json` exists. If missing, you may need to:
1. Extract from data.zip
2. Or create using `tools/create_slots_json.py`

### OpenCV Import Error (Linux)

```bash
sudo apt-get install libgl1-mesa-glx
sudo apt-get install libglib2.0-0
```

### Memory Error

- Close other applications
- Use smaller images
- Reduce number of Gunicorn workers

## Verification Checklist

After installation, verify:

- [ ] Python version 3.8+ (`python --version`)
- [ ] Virtual environment activated (prompt shows `(venv)`)
- [ ] All dependencies installed (`pip list`)
- [ ] Model file exists (`models/yolov8n.pt`)
- [ ] Slots file exists (`data/UFPR04/slots.json`)
- [ ] Application starts without errors
- [ ] Web interface accessible at http://localhost:5000
- [ ] Can upload and process images

## Uninstallation

To remove the application:

1. Deactivate virtual environment:
```bash
deactivate
```

2. Delete project folder:
```bash
# Windows
rmdir /s smart-parking-system

# Linux/Mac
rm -rf smart-parking-system
```

## Updating

To update to a new version:

```bash
# Pull latest changes (if using Git)
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
python app.py
```

## Docker Installation (Alternative)

If you prefer Docker:

```bash
# Build image
docker build -t smart-parking .

# Run container
docker run -p 5000:5000 smart-parking
```

## Next Steps

After successful installation:

1. Read [QUICKSTART.md](QUICKSTART.md) for usage guide
2. Review [README.md](README.md) for detailed documentation
3. Check [API.md](API.md) for API integration
4. See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Support

If you encounter issues:

1. Check this troubleshooting section
2. Run `python test_system.py` for diagnostics
3. Review error messages carefully
4. Check GitHub Issues for similar problems
5. Create new issue with error details

## Additional Resources

- Python Documentation: https://docs.python.org/3/
- Flask Documentation: https://flask.palletsprojects.com/
- YOLOv8 Documentation: https://docs.ultralytics.com/
- OpenCV Documentation: https://docs.opencv.org/

---

**Installation complete!** You're ready to use the Smart Parking System. 🎉
