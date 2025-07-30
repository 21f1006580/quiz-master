@echo off
REM Simple Quiz Master Startup Script for Windows

echo 🚀 Starting Quiz Master Application...

REM Check for required tools
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo 📦 Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Initialize database
echo 🗄️  Initializing database...
python init_db.py

REM Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set PYTHONPATH=%CD%

REM Start Flask backend
echo 🐍 Starting Flask backend...
call venv\Scripts\activate.bat
start "Flask Backend" python app.py

REM Wait a moment for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Check if Node modules exist
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
)

REM Start Vue frontend
echo ⚡ Starting Vue frontend...
start "Vue Frontend" npm run serve

echo ✅ Quiz Master is starting up!
echo 📱 Frontend: http://localhost:8080
echo 🔧 Backend: http://localhost:5001
echo 👤 Admin Login: admin@gmail.com / admin123
echo.
echo 🎉 Application started successfully!
echo The browser should open automatically.
echo.
echo To stop the application, close the command prompt windows.
pause 