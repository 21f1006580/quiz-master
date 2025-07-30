# 🎯 Quiz Master - Setup Guide

This guide will help you set up and run the Quiz Master application with all its features including background task scheduling.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (Python 3.9+ recommended)
- **Node.js 16+** (Node.js 18+ recommended)
- **npm** (included with Node.js)

### Optional (for background tasks)
- **Redis** (for Celery background tasks)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

#### For Mac/Linux:
```bash
# Clone the repository
git clone <repository-url>
cd quiz-master

# Make startup script executable
chmod +x start.sh

# Run the startup script
./start.sh
```

#### For Windows:
```cmd
REM Clone the repository
git clone <repository-url>
cd quiz-master

REM Run the startup script
start.bat
```

### Option 2: Manual Setup

#### 1. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed sample data
python seed_data.py

# Start backend
python app.py
```

#### 2. Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm run serve
```

#### 3. Background Tasks (Optional)
```bash
# Install Redis (if not already installed)
# On Mac: brew install redis
# On Ubuntu: sudo apt-get install redis-server
# On Windows: Download from https://redis.io

# Start Redis
redis-server

# In a new terminal, start Celery worker
source venv/bin/activate
python celery_worker.py

# In another terminal, start Celery Beat scheduler
source venv/bin/activate
python celery_beat.py
```

## 🔧 Configuration

### Environment Variables
The application uses default configurations. For production, consider setting these environment variables:

```bash
# Flask configuration
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret
export SQLALCHEMY_DATABASE_URI=sqlite:///quizmaster.db

# CORS settings
export CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

# Celery configuration
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🗄️ Database

The application uses SQLite for development. The database file (`quizmaster.db`) will be created automatically when you run the application for the first time.

### Sample Data
The application comes pre-loaded with:
- **4 Subjects**: Mathematics, Physics, Computer Science, English Literature
- **12 Chapters**: Organized by subject
- **12 Quizzes**: Scheduled for different dates
- **30 Questions**: Multiple-choice questions across all subjects

### Admin Credentials
- **Email**: `admin@gmail.com`
- **Password**: `admin123`

## 🔄 Background Tasks

### Celery Tasks
The application includes several background tasks:

1. **Quiz Expiry Check** (Every 2 minutes)
   - Automatically expires quizzes that have passed their end time
   - Updates quiz status to inactive

2. **Expiry Warnings** (Every 5 minutes)
   - Sends warnings for quizzes expiring soon
   - Logs expiry notifications

3. **Daily Cleanup** (2:00 AM UTC)
   - Archives old quiz data
   - Cleans up expired task results

### Manual Task Triggers
Admins can manually trigger tasks via API:
- `POST /api/admin/quiz/expire-check` - Manually check for expired quizzes
- `POST /api/admin/quiz/expire/<quiz_id>` - Manually expire a specific quiz
- `GET /api/admin/celery/status` - Check Celery worker status
- `GET /api/admin/celery/tasks` - List available tasks

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Redis Connection Error**
```
Error: Redis connection failed
Solution: Install and start Redis server
```
```bash
# Install Redis
# On Mac: brew install redis
# On Ubuntu: sudo apt-get install redis-server

# Start Redis
redis-server
```

#### 2. **Celery Worker Not Starting**
```
Error: No module named 'backend.api.quiz_tasks'
Solution: Ensure you're in the project root directory
```
```bash
# Make sure you're in the project root
cd /path/to/quiz-master

# Activate virtual environment
source venv/bin/activate

# Start worker
python celery_worker.py
```

#### 3. **Database Issues**
```
Error: Database file not found
Solution: Run the seeding script
```
```bash
python seed_data.py
```

#### 4. **Port Already in Use**
```
Error: Port 8080 or 5000 already in use
Solution: Kill existing processes or use different ports
```
```bash
# Find process using port
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

#### 5. **Node.js Version Issues**
```
Error: Unexpected token {
Solution: Update Node.js to version 16+
```
```bash
# Check current version
node --version

# Update using nvm (Mac/Linux)
nvm install --lts
nvm use --lts
```

### Platform-Specific Notes

#### **Windows**
- Use `start.bat` instead of `start.sh`
- Virtual environment activation: `venv\Scripts\activate.bat`
- Use Command Prompt or PowerShell
- Ensure Python is added to PATH during installation

#### **Mac**
- Use `start.sh`
- Virtual environment activation: `source venv/bin/activate`
- May need to install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for package management

#### **Linux**
- Use `start.sh`
- Virtual environment activation: `source venv/bin/activate`
- Install Python dev headers: `sudo apt-get install python3-dev` (Ubuntu/Debian)
- Install build essentials: `sudo apt-get install build-essential`

## 📊 Monitoring

### Application Health
- **Backend**: http://localhost:5000/api/admin/celery/status
- **Frontend**: http://localhost:8080
- **Database**: SQLite file in project root

### Celery Monitoring
- **Worker Status**: Check `/api/admin/celery/status`
- **Task List**: Check `/api/admin/celery/tasks`
- **Task Status**: Check `/api/admin/task/<task_id>/status`

## 🚀 Production Deployment

For production deployment, consider:

1. **Database**: Use PostgreSQL or MySQL instead of SQLite
2. **Web Server**: Use Gunicorn or uWSGI with Nginx
3. **Redis**: Use Redis Cloud or AWS ElastiCache
4. **Environment Variables**: Set proper secret keys and database URLs
5. **SSL**: Configure HTTPS with proper certificates
6. **Monitoring**: Set up logging and monitoring tools

## 📝 API Documentation

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/admin-login` - Admin login

### User Routes
- `GET /api/user/dashboard` - User dashboard
- `GET /api/user/subjects/<id>/quizzes` - Get quizzes by subject
- `GET /api/user/quiz/<id>/take` - Start quiz
- `POST /api/user/quiz/<id>/submit` - Submit quiz
- `GET /api/user/scores` - Get user scores

### Admin Routes
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/subjects` - Get all subjects
- `POST /api/admin/subjects` - Create subject
- `GET /api/admin/chapters` - Get all chapters
- `POST /api/admin/quizzes` - Create quiz
- `POST /api/admin/questions` - Create question

## 🤝 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check the application logs
4. Ensure Redis is running (for background tasks)
5. Verify database file exists and is accessible

## 📄 License

This project is licensed under the MIT License. 