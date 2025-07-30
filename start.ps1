# Quiz Master Startup Script for Windows PowerShell

Write-Host "🚀 Starting Quiz Master Application..." -ForegroundColor Green

# Check for required tools
Write-Host "Checking required tools..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python is required but not installed." -ForegroundColor Red
        Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Python is required but not installed." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Node.js is required but not installed." -ForegroundColor Red
        Write-Host "Please install Node.js 16+ from https://nodejs.org" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ Node.js is required but not installed." -ForegroundColor Red
    Write-Host "Please install Node.js 16+ from https://nodejs.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ npm found: $npmVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ npm is required but not installed." -ForegroundColor Red
        Write-Host "Please install Node.js 16+ which includes npm" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "❌ npm is required but not installed." -ForegroundColor Red
    Write-Host "Please install Node.js 16+ which includes npm" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Redis is available (optional for background tasks)
try {
    $redisTest = redis-cli ping 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Redis is running" -ForegroundColor Green
        $REDIS_AVAILABLE = $true
    } else {
        Write-Host "⚠️  Redis not found. Background tasks will be disabled." -ForegroundColor Yellow
        Write-Host "To enable background tasks, install Redis from https://redis.io" -ForegroundColor Yellow
        $REDIS_AVAILABLE = $false
    }
} catch {
    Write-Host "⚠️  Redis not found. Background tasks will be disabled." -ForegroundColor Yellow
    Write-Host "To enable background tasks, install Redis from https://redis.io" -ForegroundColor Yellow
    $REDIS_AVAILABLE = $false
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment and install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
python init_db.py

# Set environment variables
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:PYTHONPATH = (Get-Location).Path

# Start Flask backend in background
Write-Host "🐍 Starting Flask backend..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Start-Process python -ArgumentList "app.py" -WindowStyle Hidden
$BACKEND_PID = $LASTEXITCODE

# Wait a moment for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend health
Write-Host "🔍 Testing backend health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:5001/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Backend is responding" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend might not be ready yet, continuing..." -ForegroundColor Yellow
}

# Start Celery worker if Redis is available
if ($REDIS_AVAILABLE) {
    Write-Host "🔧 Starting Celery worker..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    Start-Process python -ArgumentList "celery_worker.py" -WindowStyle Hidden
    $WORKER_PID = $LASTEXITCODE
    
    Write-Host "⏰ Starting Celery Beat scheduler..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    Start-Process python -ArgumentList "celery_beat.py" -WindowStyle Hidden
    $BEAT_PID = $LASTEXITCODE
} else {
    $WORKER_PID = $null
    $BEAT_PID = $null
}

# Check if Node modules exist
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
}

# Start Vue frontend
Write-Host "⚡ Starting Vue frontend..." -ForegroundColor Yellow
Start-Process npm -ArgumentList "run", "serve" -WindowStyle Hidden
$FRONTEND_PID = $LASTEXITCODE

Write-Host "✅ Quiz Master is starting up!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:8080" -ForegroundColor Cyan
Write-Host "🔧 Backend: http://localhost:5001" -ForegroundColor Cyan
if ($REDIS_AVAILABLE) {
    Write-Host "🔧 Celery Worker: Running" -ForegroundColor Green
    Write-Host "⏰ Celery Beat: Running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Background tasks: Disabled (Redis not available)" -ForegroundColor Yellow
}
Write-Host "👤 Admin Login: admin@gmail.com / admin123" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 To debug JWT issues, run: python debug_jwt.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Red

# Function to cleanup processes
function Cleanup-Processes {
    Write-Host "🛑 Shutting down servers..." -ForegroundColor Yellow
    
    # Stop Flask backend
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force
    
    # Stop Node.js processes
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
    
    Write-Host "✅ Servers stopped successfully!" -ForegroundColor Green
}

# Register cleanup function for Ctrl+C
Register-EngineEvent PowerShell.Exiting -Action { Cleanup-Processes }

# Wait for user input
Write-Host "Press any key to stop all servers..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

# Cleanup on exit
Cleanup-Processes 