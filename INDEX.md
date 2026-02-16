# Smart Parking System - Documentation Index

Welcome to the Smart Parking System! This index will help you find the right documentation for your needs.

## 🚀 Getting Started

**New to the project? Start here:**

1. **[INSTALL.md](INSTALL.md)** - Complete installation instructions
2. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
3. **[CHECKLIST.md](CHECKLIST.md)** - Verify your setup

**Quick Start Commands:**
```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh && ./start.sh
```

## 📚 Documentation

### Core Documentation

| Document | Description | When to Read |
|----------|-------------|--------------|
| [README.md](README.md) | Complete project overview and features | First time setup |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Technical summary and architecture | Understanding the system |
| [INSTALL.md](INSTALL.md) | Detailed installation guide | Installation issues |
| [QUICKSTART.md](QUICKSTART.md) | Fast setup guide | Quick start |

### Technical Documentation

| Document | Description | When to Read |
|----------|-------------|--------------|
| [API.md](API.md) | REST API reference | API integration |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide | Going to production |
| [CHECKLIST.md](CHECKLIST.md) | Setup verification checklist | After installation |

### Configuration Files

| File | Purpose |
|------|---------|
| `config.py` | Application configuration |
| `.env.example` | Environment variables template |
| `requirements.txt` | Python dependencies |

## 🎯 Use Cases

### I want to...

**...install the system**
→ Read [INSTALL.md](INSTALL.md)

**...run it quickly**
→ Use `start.bat` (Windows) or `start.sh` (Linux/Mac)

**...understand how it works**
→ Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**...integrate with my app**
→ Read [API.md](API.md)

**...deploy to production**
→ Read [DEPLOYMENT.md](DEPLOYMENT.md)

**...verify my setup**
→ Use [CHECKLIST.md](CHECKLIST.md)

**...troubleshoot issues**
→ Check [INSTALL.md](INSTALL.md) troubleshooting section

## 🏗️ Project Structure

```
smart-parking-system/
│
├── 📄 Documentation
│   ├── INDEX.md              ← You are here
│   ├── README.md             ← Start here
│   ├── INSTALL.md            ← Installation guide
│   ├── QUICKSTART.md         ← Quick start
│   ├── API.md                ← API reference
│   ├── DEPLOYMENT.md         ← Deployment guide
│   ├── PROJECT_SUMMARY.md    ← Technical overview
│   └── CHECKLIST.md          ← Setup checklist
│
├── 🚀 Application
│   ├── app.py                ← Main Flask app
│   ├── run.py                ← Entry point
│   ├── config.py             ← Configuration
│   └── requirements.txt      ← Dependencies
│
├── 🔧 Utilities
│   ├── utils.py              ← Utility functions
│   ├── test_system.py        ← System tests
│   ├── start.bat             ← Windows startup
│   └── start.sh              ← Linux/Mac startup
│
├── 📦 Source Code
│   └── src/
│       ├── detect_cars.py    ← Car detection
│       ├── occupancy.py      ← Occupancy logic
│       ├── visualize.py      ← Visualization
│       └── slot_utils.py     ← Slot utilities
│
├── 🎨 Frontend
│   └── templates/
│       └── index.html        ← Web interface
│
├── 📊 Data & Models
│   ├── models/
│   │   └── yolov8n.pt       ← YOLOv8 model
│   └── data/
│       └── UFPR04/
│           ├── slots.json    ← Slot coordinates
│           └── images/       ← Sample images
│
└── 📁 Static Files
    └── static/
        └── uploads/          ← Uploaded images
```

## 🔍 Quick Reference

### Installation
```bash
pip install -r requirements.txt
python app.py
```

### Testing
```bash
python test_system.py
python utils.py
```

### Running
```bash
# Development
python app.py

# Production
gunicorn -w 4 app:app
```

### API Usage
```bash
curl -X POST -F "image=@parking.jpg" http://localhost:5000/detect
```

## 📖 Reading Order

### For Developers

1. [README.md](README.md) - Overview
2. [INSTALL.md](INSTALL.md) - Setup
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture
4. [API.md](API.md) - API details
5. Source code in `src/`

### For Users

1. [QUICKSTART.md](QUICKSTART.md) - Quick setup
2. [CHECKLIST.md](CHECKLIST.md) - Verify setup
3. Use the web interface
4. [API.md](API.md) - If integrating

### For DevOps

1. [INSTALL.md](INSTALL.md) - Installation
2. [DEPLOYMENT.md](DEPLOYMENT.md) - Production setup
3. [API.md](API.md) - Monitoring endpoints
4. `config.py` - Configuration options

## 🛠️ Key Features

- ✅ Real-time parking detection
- ✅ YOLOv8 AI model
- ✅ Modern web interface
- ✅ RESTful API
- ✅ Production-ready
- ✅ Fully documented
- ✅ Easy to deploy

## 🔗 External Resources

- **YOLOv8**: https://docs.ultralytics.com/
- **Flask**: https://flask.palletsprojects.com/
- **OpenCV**: https://docs.opencv.org/
- **Python**: https://docs.python.org/3/

## 💡 Tips

- Run `python utils.py` to validate setup
- Run `python test_system.py` to test components
- Check `CHECKLIST.md` after installation
- Use `start.bat` or `start.sh` for easy startup
- Read error messages carefully
- Check logs for debugging

## 🆘 Getting Help

1. **Installation issues**: See [INSTALL.md](INSTALL.md) troubleshooting
2. **API questions**: Check [API.md](API.md)
3. **Deployment help**: Read [DEPLOYMENT.md](DEPLOYMENT.md)
4. **General questions**: See [README.md](README.md)

## 📝 Contributing

Contributions welcome! Please:
1. Read the documentation
2. Test your changes
3. Update relevant docs
4. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 🎉 Ready to Start?

Choose your path:

**Quick Start** → Run `start.bat` or `start.sh`

**Learn First** → Read [README.md](README.md)

**Install Manually** → Follow [INSTALL.md](INSTALL.md)

**Deploy to Production** → Read [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Welcome to Smart Parking System!** 🚗 Happy parking detection! 🎯
