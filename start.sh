#!/bin/bash

# Quiz Master Startup Script

echo "🚀 Starting Quiz Master Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3.12 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

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

# Wait for user to stop
wait 