@echo off
setlocal enabledelayedexpansion

REM Quiz Master Startup Script for Windows

echo 🚀 Starting Quiz Master Application...

REM Function to check if command exists
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is required but not installed.
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm is required but not installed.
    echo Please install Node.js 16+ which includes npm
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo 📦 Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

REM Seed database if it doesn't exist
if not exist "quizmaster.db" (
    echo 🌱 Seeding database with sample data...
    python seed_data.py
)

REM Start Flask backend in background
echo 🐍 Starting Flask backend...
start "Flask Backend" cmd /c "call venv\Scripts\activate.bat && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Check if Node modules exist
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Node.js dependencies
        pause
        exit /b 1
    )
)

REM Start Vue frontend
echo ⚡ Starting Vue frontend...
start "Vue Frontend" cmd /c "npm run serve"

echo ✅ Quiz Master is starting up!
echo 📱 Frontend: http://localhost:8080
echo 🔧 Backend: http://localhost:5000
echo 👤 Admin Login: admin@gmail.com / admin123
echo.
echo Both servers are running in separate windows.
echo Close those windows or press Ctrl+C in them to stop the servers.
echo.
echo Press any key to exit this startup script...
pause >nul
