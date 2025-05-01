@echo off
echo Starting Smart Attendance System...

REM Check if Python is installed
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import flask, opencv-python, numpy" 2>nul
if %errorLevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Run the application
echo Starting the application...
python run_web_app.py

if %errorLevel% neq 0 (
    echo Failed to start the application.
    echo Please check the error messages above.
    pause
)

REM Check if port 8080 is available
netstat -ano | findstr :8080 