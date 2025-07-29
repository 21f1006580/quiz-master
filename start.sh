#!/bin/bash

# Quiz Master Startup Script for Mac/Linux

echo "🚀 Starting Quiz Master Application..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    echo "Please install Node.js 16+ which includes npm"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    # Try different Python versions
    if command_exists python3.12; then
        python3.12 -m venv venv
    elif command_exists python3.11; then
        python3.11 -m venv venv
    elif command_exists python3.10; then
        python3.10 -m venv venv
    elif command_exists python3.9; then
        python3.9 -m venv venv
    else
        python3 -m venv venv
    fi
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Seed database if it doesn't exist
if [ ! -f "quizmaster.db" ]; then
    echo "🌱 Seeding database with sample data..."
    python seed_data.py
fi

# Start Flask backend in background
echo "🐍 Starting Flask backend..."
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

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
echo "🔧 Backend: http://localhost:5000"
echo "👤 Admin Login: admin@gmail.com / admin123"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup background processes
cleanup() {
    echo "\n🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped successfully!"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
