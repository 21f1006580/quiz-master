# Quiz Master Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm (included with Node.js)

### One-Command Setup

#### For Mac/Linux:
```bash
git clone https://github.com/21f1006580/quiz-master.git
cd quiz-master
chmod +x start.sh
./start.sh
```

#### For Windows:
```cmd
git clone https://github.com/21f1006580/quiz-master.git
cd quiz-master
start.bat
```

## 📋 Manual Setup

### 1. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate.bat  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Seed database with sample data
python seed_data.py

# Start Flask backend
python app.py
```

### 2. Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Start Vue.js development server
npm run serve
```

## 🌐 Access URLs

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5001
- **Admin Login**: admin@gmail.com / admin123

## 🔧 Configuration

### Environment Variables
```bash
export FLASK_ENV=development
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret
export REDIS_URL=redis://localhost:6379
```

### Database
The application uses SQLite by default. The database file `quizmaster.db` will be created automatically when you run `seed_data.py`.

## 🐛 Troubleshooting

### Common Issues

**Error: Port 8080 or 5001 already in use**
```bash
# Find and kill processes using the ports
lsof -ti:8080 | xargs kill -9
lsof -ti:5001 | xargs kill -9
```

**Error: Python command not found**
```bash
# Try different Python commands
python --version
python3 --version
python3.9 --version

# Install Python if needed
# Mac: brew install python
# Ubuntu: sudo apt-get install python3
```

**Error: Node.js not found**
```bash
# Install Node.js
# Mac: brew install node
# Ubuntu: curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
# Windows: Download from https://nodejs.org
```

**Error: Database not found**
```bash
# Run the seeding script
python seed_data.py
```

**Error: Module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt
npm install
```

## 🎯 Background Tasks (Optional)

### Redis Setup
```bash
# Mac
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis-server

# Windows
# Download from https://redis.io/download
```

### Celery Workers
```bash
# Start Celery worker
celery -A celery_app worker --loglevel=info

# Start Celery Beat scheduler
celery -A celery_app beat --loglevel=info
```

## 📊 Sample Data

The application comes pre-loaded with:
- **4 Subjects**: Mathematics, Physics, Computer Science, English Literature
- **12 Chapters**: Organized by subject
- **12 Quizzes**: Scheduled for different dates
- **30 Questions**: Multiple-choice questions across all subjects

## 🔐 Security

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- CORS protection
- Input validation

## 🚀 Production Deployment

### Backend
```bash
# Install production dependencies
pip install gunicorn

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Frontend
```bash
# Build for production
npm run build

# Serve static files with nginx or Apache
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in the terminal
3. Check the browser console for frontend errors
4. Verify all services are running on correct ports

---

**🎉 Your Quiz Master application is now ready to use!** 