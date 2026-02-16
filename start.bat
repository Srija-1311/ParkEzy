@echo off
echo ========================================
echo Smart Parking System - Startup Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.

REM Run validation
echo Validating setup...
python utils.py
echo.

REM Start the application
echo Starting Smart Parking System...
echo.
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
