@echo off
REM Quiz Master Startup Script for Windows

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

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is required but not installed.
    echo Please install Node.js 16+ which includes npm
    pause
    exit /b 1
)

REM Check if Redis is available (optional for background tasks)
where redis-cli >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis not found. Background tasks will be disabled.
    echo To enable background tasks, install Redis from https://redis.io
    set REDIS_AVAILABLE=false
) else (
    redis-cli ping >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Redis is installed but not running. Background tasks will be disabled.
        echo To enable background tasks, start Redis server
        set REDIS_AVAILABLE=false
    ) else (
        echo ✅ Redis is running
        set REDIS_AVAILABLE=true
    )
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

REM Start Flask backend in background
echo 🐍 Starting Flask backend...
call venv\Scripts\activate.bat
start /B python app.py
set BACKEND_PID=%ERRORLEVEL%

REM Wait a moment for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start Celery worker if Redis is available
if "%REDIS_AVAILABLE%"=="true" (
    echo 🔧 Starting Celery worker...
    call venv\Scripts\activate.bat
    start /B python celery_worker.py
    set WORKER_PID=%ERRORLEVEL%
    
    echo ⏰ Starting Celery Beat scheduler...
    call venv\Scripts\activate.bat
    start /B python celery_beat.py
    set BEAT_PID=%ERRORLEVEL%
) else (
    set WORKER_PID=
    set BEAT_PID=
)

REM Check if Node modules exist
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
)

REM Start Vue frontend
echo ⚡ Starting Vue frontend...
start /B npm run serve
set FRONTEND_PID=%ERRORLEVEL%

echo ✅ Quiz Master is starting up!
echo 📱 Frontend: http://localhost:8080
echo 🔧 Backend: http://localhost:5001
if "%REDIS_AVAILABLE%"=="true" (
    echo 🔧 Celery Worker: Running
    echo ⏰ Celery Beat: Running
) else (
    echo ⚠️  Background tasks: Disabled (Redis not available)
)
echo 👤 Admin Login: admin@gmail.com / admin123
echo.
echo Press Ctrl+C to stop all servers

REM Wait for user input
pause
