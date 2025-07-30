#!/bin/bash
# Quiz Master Startup Script for Mac/Linux

echo "🚀 Starting Quiz Master Application..."

# Check for required tools
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    echo "Please install Node.js 16+ which includes npm"
    exit 1
fi

# Check if Redis is running (required for Celery)
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis not found. Please install Redis for background tasks."
    echo "On Mac: brew install redis"
    echo "On Ubuntu: sudo apt-get install redis-server"
    echo "Starting without background tasks..."
    REDIS_AVAILABLE=false
else
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
        REDIS_AVAILABLE=true
    else
        echo "⚠️  Redis is not running. Starting without background tasks..."
        REDIS_AVAILABLE=false
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python3 init_db.py

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export PYTHONPATH=$(pwd)

# Start Flask backend in background
echo "🐍 Starting Flask backend..."
source venv/bin/activate
python3 app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start Celery worker if Redis is available
if [ "$REDIS_AVAILABLE" = true ]; then
    echo "🔧 Starting Celery worker..."
    source venv/bin/activate
    python3 celery_worker.py &
    WORKER_PID=$!
    
    echo "⏰ Starting Celery Beat scheduler..."
    source venv/bin/activate
    python3 celery_beat.py &
    BEAT_PID=$!
else
    WORKER_PID=""
    BEAT_PID=""
fi

# Check if Node modules exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start Vue frontend
echo "⚡ Starting Vue frontend..."
npm run serve &
FRONTEND_PID=$!

echo "✅ Quiz Master is starting up!"
echo "📱 Frontend: http://localhost:8080"
echo "🔧 Backend: http://localhost:5001"
if [ "$REDIS_AVAILABLE" = true ]; then
    echo "🔧 Celery Worker: Running"
    echo "⏰ Celery Beat: Running"
else
    echo "⚠️  Background tasks: Disabled (Redis not available)"
fi
echo "👤 Admin Login: admin@gmail.com / admin123"
echo ""
echo "Press Ctrl+C to stop all servers"

cleanup() {
    echo "\n🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    if [ ! -z "$WORKER_PID" ]; then
        kill $WORKER_PID 2>/dev/null
    fi
    if [ ! -z "$BEAT_PID" ]; then
        kill $BEAT_PID 2>/dev/null
    fi
    echo "✅ Servers stopped successfully!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait
