# Quiz Master Startup Script for Windows PowerShell

Write-Host "🚀 Starting Quiz Master Application..." -ForegroundColor Green

# Function to check if command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check Python
if (-not (Test-Command "python")) {
    Write-Host "❌ Python is required but not installed." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
if (-not (Test-Command "node")) {
    Write-Host "❌ Node.js is required but not installed." -ForegroundColor Red
    Write-Host "Please install Node.js 16+ from https://nodejs.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check npm
if (-not (Test-Command "npm")) {
    Write-Host "❌ npm is required but not installed." -ForegroundColor Red
    Write-Host "Please install Node.js 16+ which includes npm" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment and install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Seed database if it doesn't exist
if (-not (Test-Path "quizmaster.db")) {
    Write-Host "🌱 Seeding database with sample data..." -ForegroundColor Cyan
    python seed_data.py
}

# Start Flask backend in background
Write-Host "🐍 Starting Flask backend..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "call venv\Scripts\activate.bat && python app.py" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Check if Node modules exist
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Node.js dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Start Vue frontend
Write-Host "⚡ Starting Vue frontend..." -ForegroundColor Cyan
Start-Process -FilePath "cmd" -ArgumentList "/c", "npm run serve" -WindowStyle Normal

Write-Host "✅ Quiz Master is starting up!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:8080" -ForegroundColor Yellow
Write-Host "🔧 Backend: http://localhost:5000" -ForegroundColor Yellow
Write-Host "👤 Admin Login: admin@gmail.com / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "Both servers are running in separate windows." -ForegroundColor Cyan
Write-Host "Close those windows or press Ctrl+C in them to stop the servers." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit this startup script" 