#!/bin/bash

echo "========================================"
echo "Smart Parking System - Startup Script"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo ""

# Run validation
echo "Validating setup..."
python utils.py
echo ""

# Start the application
echo "Starting Smart Parking System..."
echo ""
echo "Application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""
python app.py
