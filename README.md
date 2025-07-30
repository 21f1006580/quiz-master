# Quiz Master Application

A comprehensive quiz management system built with Flask (Python) and Vue.js, featuring role-based access control, real-time quiz taking, and automated background tasks.

## 🚀 Features

### Core Functionalities
- **Admin/User Authentication**: JWT-based login with role-based access control
- **Subject/Chapter Management**: Hierarchical organization of educational content
- **Quiz Creation & Management**: MCQ-based quizzes with scheduling and auto-expiry
- **Real-time Quiz Taking**: Timer-based quiz interface with instant feedback
- **Score Tracking**: Comprehensive performance analytics and history

### Advanced Features
- **Background Tasks**: Automated quiz expiry, daily reminders, and monthly reports
- **CSV Export**: User and admin data export functionality
- **Caching System**: Redis-based performance optimization
- **Search Functionality**: Admin search across users, subjects, and quizzes
- **Responsive Design**: Modern UI with mobile-friendly interface

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **JWT**: Authentication and authorization
- **Celery**: Background task processing
- **Redis**: Caching and message broker
- **SQLite**: Database (production-ready alternatives available)

### Frontend
- **Vue.js 2.7**: Progressive JavaScript framework
- **Vuex**: State management
- **Vue Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **CSS3**: Modern styling with gradients and animations

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Redis (optional, for background tasks)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/21f1006580/quiz-master.git
cd quiz-master
```

### 2. Start the Application

**Option A: Using Startup Scripts**
```bash
# Mac/Linux
./start.sh

# Windows
start.bat
```

**Option B: Manual Start**
```bash
# Backend
source venv/bin/activate
python3 app.py

# Frontend (new terminal)
npm run serve
```

### 3. Access the Application
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5001
- **Admin Login**: admin@gmail.com / admin123

## 📁 Project Structure

```
quiz-master/
├── app.py                      # Flask application entry point
├── celery_app.py              # Celery configuration
├── backend/
│   ├── api/
│   │   ├── quiz_tasks.py      # Quiz-related background tasks
│   │   └── notification_tasks.py # Email/notification tasks
│   ├── cache.py               # Redis caching system
│   ├── models/
│   │   └── models.py          # Database models
│   └── routes/
│       ├── admin_routes.py    # Admin API endpoints
│       ├── auth_routes.py     # Authentication endpoints
│       └── user_routes.py     # User API endpoints
├── src/
│   ├── components/
│   │   ├── Admin/            # Admin dashboard components
│   │   └── Navigation.vue    # Navigation component
│   ├── services/
│   │   └── api.js           # API service layer
│   ├── store/
│   │   ├── auth.js          # Authentication state
│   │   └── index.js         # Vuex store
│   ├── views/               # Vue.js page components
│   ├── App.vue              # Root component
│   ├── main.js              # Vue application entry
│   └── router/
│       └── index.js         # Vue Router configuration
├── start.sh                 # Mac/Linux startup script
├── start.bat               # Windows startup script
└── requirements.txt         # Python dependencies
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/profile` - Get user profile

### Admin Routes
- `GET /api/admin/subjects` - List subjects
- `POST /api/admin/subjects` - Create subject
- `GET /api/admin/chapters` - List chapters
- `POST /api/admin/chapters` - Create chapter
- `GET /api/admin/quizzes` - List quizzes
- `POST /api/admin/quizzes` - Create quiz
- `GET /api/admin/questions` - List questions
- `POST /api/admin/questions` - Create question
- `GET /api/admin/users` - List users
- `GET /api/admin/search` - Search functionality
- `POST /api/admin/export/csv` - Export user data
- `GET /api/admin/stats` - Dashboard statistics

### User Routes
- `GET /api/user/dashboard` - User dashboard
- `GET /api/user/subjects` - Available subjects
- `GET /api/user/subjects/{id}/quizzes` - Subject quizzes
- `GET /api/user/quiz/{id}/take` - Start quiz
- `POST /api/user/quiz/{id}/submit` - Submit quiz
- `GET /api/user/scores` - User scores
- `GET /api/user/stats` - User statistics
- `POST /api/user/export/csv` - Export personal data

## 🎯 Background Tasks

### Scheduled Jobs
- **Daily Reminders**: Sent at 6 PM to inactive users
- **Monthly Reports**: Generated on 1st of every month at 9 AM
- **Quiz Expiry**: Automatic quiz locking and cleanup

### Async Jobs
- **CSV Export**: User and admin data export
- **Quiz Processing**: Score calculation and result generation

## 🔐 Security Features

- JWT-based authentication
- Role-based access control (Admin/User)
- CORS configuration
- Input validation and sanitization
- SQL injection protection via SQLAlchemy

## 📊 Performance Features

- Redis caching for dashboard statistics
- Database query optimization
- Frontend code splitting and lazy loading
- API response compression

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
pip install gunicorn

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app

# Build frontend for production
npm run build
```

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export REDIS_URL=redis://localhost:6379
```

## 🐛 Troubleshooting

### Common Issues

**Error: Port 8080 or 5001 already in use**
```bash
# Kill existing processes
lsof -ti:8080 | xargs kill -9
lsof -ti:5001 | xargs kill -9
```

**Error: Redis connection failed**
```bash
# Install Redis
brew install redis  # Mac
sudo apt-get install redis-server  # Ubuntu

# Start Redis
redis-server
```

**Error: Module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt
npm install
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Quiz Master Team**
- **Contact**: admin@quizmaster.com

---

**🎉 Ready for production use with comprehensive testing and documentation!**

