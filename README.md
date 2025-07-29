# 🎯 Quiz Master - Professional Quiz Application

A comprehensive, full-stack quiz application built with **Flask (Python)** backend and **Vue.js** frontend. Perfect for educational institutions, training centers, or any organization that needs a robust quiz system.

## ✨ Features

### 🎓 **User Features**
- **Interactive Dashboard** - View subjects, recent scores, and performance analytics
- **Quiz Taking Interface** - Real-time timer, progress tracking, and question navigation
- **Score Tracking** - Detailed performance analysis and attempt history
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile

### 👨‍💼 **Admin Features**
- **Comprehensive Dashboard** - Statistics overview and quick actions
- **Subject Management** - Create, edit, and organize subjects
- **Chapter Management** - Organize content hierarchically
- **Quiz Management** - Schedule and configure quizzes
- **Question Management** - Add multiple-choice questions
- **User Management** - View and manage user accounts

### 🔐 **Security & Authentication**
- **JWT Authentication** - Secure token-based authentication
- **Role-based Access** - Admin and user permissions
- **Password Hashing** - Secure password storage
- **CORS Protection** - Cross-origin request handling

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Python 3.9+ recommended)
- **Node.js 16+** (Node.js 18+ recommended)
- **npm** (included with Node.js)

### One-Command Setup

#### For Mac/Linux:
```bash
# Clone and setup everything
git clone <repository-url>
cd quiz-master
chmod +x start.sh
./start.sh
```

#### For Windows:

**Option 1: Using Command Prompt (Recommended)**
```cmd
REM Clone and setup everything
git clone <repository-url>
cd quiz-master
start.bat
```

**Option 2: Using PowerShell**
```powershell
# Clone and setup everything
git clone <repository-url>
cd quiz-master
.\start.ps1
```

**Note**: If you get a PowerShell execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Note**: The startup scripts will automatically:
- ✅ Check for required dependencies (Python, Node.js, npm)
- ✅ Create Python virtual environment
- ✅ Install Python dependencies
- ✅ Install Node.js dependencies
- ✅ Seed the database with sample data
- ✅ Start both backend and frontend servers

### Manual Setup

#### 1. Backend Setup
```bash
# Create virtual environment
python3.12 -m venv venv
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

## 🔑 Default Credentials

### Admin Access
- **Email**: `admin@gmail.com`
- **Password**: `admin123`

## 📊 Sample Data

The application comes pre-loaded with:
- **4 Subjects**: Mathematics, Physics, Computer Science, English Literature
- **12 Chapters**: Organized by subject
- **12 Quizzes**: Scheduled for different dates
- **30 Questions**: Multiple-choice questions across all subjects

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### User Routes
- `GET /api/user/dashboard` - User dashboard with subjects
- `GET /api/user/quizzes/<subject_id>` - Get quizzes for subject
- `GET /api/user/quiz/<quiz_id>` - Get quiz details
- `POST /api/user/quiz/submit` - Submit quiz answers
- `GET /api/user/scores` - Get user score history
- `GET /api/user/quiz-summary/<quiz_id>` - Get quiz summary
- `GET /api/user/score-summary` - Get performance analytics

### Admin Routes
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/subjects` - Get all subjects
- `POST /api/admin/subjects` - Create subject
- `PUT /api/admin/subjects/<id>` - Update subject
- `DELETE /api/admin/subjects/<id>` - Delete subject
- `GET /api/admin/chapters` - Get chapters
- `POST /api/admin/chapters` - Create chapter
- `GET /api/admin/quizzes` - Get quizzes
- `POST /api/admin/quizzes` - Create quiz
- `GET /api/admin/questions` - Get questions
- `POST /api/admin/questions` - Create question
- `GET /api/admin/users` - Get all users

## 🏗️ Project Structure

```
quiz-master/
├── app.py                    # Flask application entry point
├── seed_data.py             # Database seeding script
├── start.sh                 # Mac/Linux startup script
├── start.bat                # Windows Command Prompt startup script
├── start.ps1                # Windows PowerShell startup script
├── requirements.txt          # Python dependencies
├── package.json             # Node.js dependencies
├── vue.config.js            # Vue.js configuration
├── backend/                 # Backend code
│   ├── models/
│   │   └── models.py        # Database models (User, Subject, Chapter, Quiz, Question, Score)
│   ├── routes/
│   │   ├── auth_routes.py   # Authentication routes
│   │   ├── admin_routes.py  # Admin management routes
│   │   └── user_routes.py   # User quiz routes
│   └── api/
│       ├── celery.py        # Background task configuration
│       └── task.py          # Background tasks
├── src/                     # Vue.js frontend
│   ├── components/
│   │   └── Navigation.vue   # Navigation component
│   ├── views/
│   │   ├── Login.vue        # Login page
│   │   ├── Register.vue     # Registration page
│   │   ├── UserDashboard.vue # User dashboard
│   │   ├── SubjectQuizzes.vue # Subject quiz listing
│   │   ├── QuizTaking.vue   # Quiz taking interface
│   │   ├── QuizSummary.vue  # Quiz results
│   │   ├── ScoresPage.vue   # Score history
│   │   └── AdminDashboard.vue # Admin dashboard
│   └── router/
│       └── index.js         # Vue router configuration
└── public/                  # Static files
```

## 🎨 Frontend Components

### User Interface
- **UserDashboard.vue** - Main dashboard with statistics and subject browsing
- **SubjectQuizzes.vue** - Quiz listing with status indicators
- **QuizTaking.vue** - Interactive quiz interface with timer
- **QuizSummary.vue** - Detailed results and performance analysis
- **ScoresPage.vue** - Complete score history and analytics

### Admin Interface
- **AdminDashboard.vue** - Statistics overview and quick actions
- **Navigation.vue** - Role-based navigation component

## 🗄️ Database Schema

### Core Models
- **User** - User accounts with role-based permissions
- **Subject** - Educational subjects/categories
- **Chapter** - Subject subdivisions
- **Quiz** - Scheduled assessments
- **Question** - Multiple-choice questions
- **Score** - User quiz attempts and results

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0** - Web framework
- **SQLAlchemy 2.0.27** - ORM
- **Flask-JWT-Extended 4.6.0** - JWT authentication
- **Flask-CORS 4.0.0** - Cross-origin support
- **SQLite** - Database (development)

### Frontend
- **Vue.js 2.7.16** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Modern CSS** - Responsive design with gradients and animations

## 🚀 Deployment

### Development
```bash
# Backend (Terminal 1)
source venv/bin/activate
python app.py

# Frontend (Terminal 2)
npm run serve
```

### Production
```bash
# Build frontend
npm run build

# Deploy backend with WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🎯 Key Features

### Real-time Quiz Experience
- **Timer with warnings** - Visual countdown with color changes
- **Progress tracking** - Question indicators and completion status
- **Navigation** - Previous/next buttons and question jumping
- **Auto-submission** - Automatic submission when time expires

### Professional UI/UX
- **Modern design** - Beautiful gradients and smooth animations
- **Responsive layout** - Works on all device sizes
- **Loading states** - Professional loading indicators
- **Error handling** - User-friendly error messages

### Comprehensive Analytics
- **Performance metrics** - Success rates and score distributions
- **Attempt history** - Detailed quiz attempt records
- **Progress tracking** - Visual progress indicators
- **Score summaries** - Overall performance analytics

## 🔧 Configuration

### Environment Variables
```bash
# Flask configuration
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
SQLALCHEMY_DATABASE_URI=sqlite:///quizmaster.db

# CORS settings
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

### Database
The application uses SQLite for development. For production, consider:
- **PostgreSQL** - For better performance and concurrency
- **MySQL** - For compatibility with existing infrastructure
- **MongoDB** - For document-based data storage

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Node.js Version Issues**
```bash
# Error: Unexpected token {
# Solution: Update Node.js to version 16+

# Check current version
node --version

# Update using homebrew (Mac)
brew install node

# Update using nvm (Mac/Linux)
nvm install --lts
nvm use --lts

# Update on Windows: Download from nodejs.org
```

#### 2. **Python Virtual Environment Issues**
```bash
# Error: Command 'python3' not found
# Solution: Install Python or use correct command

# Try different Python commands
python --version
python3 --version
python3.9 --version

# Create venv with specific version
python3.9 -m venv venv
```

#### 3. **Port Already in Use**
```bash
# Error: Port 8080 or 5000 already in use
# Solution: Kill processes or use different ports

# Find process using port
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

#### 4. **Permission Issues (Mac/Linux)**
```bash
# Error: Permission denied
# Solution: Make script executable
chmod +x start.sh

# Or run with bash
bash start.sh
```

#### 5. **Database Not Found**
```bash
# Error: Database file not found
# Solution: Run the seeding script
python seed_data.py
```

#### 6. **Windows PowerShell Issues**
```powershell
# Error: start.bat is not recognized as a cmdlet
# Solution: Use the correct method for your shell

# In PowerShell, use:
.\start.ps1

# Or in Command Prompt, use:
start.bat

# If you get execution policy error in PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

---

**🎉 Ready to deploy!** Your Quiz Master application is now fully functional with professional-grade features, beautiful UI, and comprehensive functionality.


It is a multi-user app (one requires an administrator and other users) that acts as an exam preparation site for multiple courses.

