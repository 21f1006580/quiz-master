# Quiz Master

A full-stack quiz application built with Flask (Python) backend and Vue.js frontend.

## Features

- User authentication and authorization
- Admin dashboard for managing subjects, chapters, quizzes, and questions
- User registration and login
- JWT-based authentication
- Responsive design

## Prerequisites

- Python 3.12+
- Node.js 16+
- npm

## Installation and Setup

### Backend Setup

1. Create a virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask backend:
   ```bash
   source venv/bin/activate
   python app.py
   ```
   The backend will run on http://localhost:5000

### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Start the Vue development server:
   ```bash
   npm run serve
   ```
   The frontend will run on http://localhost:8080

## Default Admin Credentials

- Email: admin@gmail.com
- Password: admin123

## API Endpoints

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/admin/subjects` - Get all subjects (admin only)
- `POST /api/admin/subjects` - Create new subject (admin only)
- And more...

## Project Structure

```
quiz-master/
├── app.py                 # Flask application entry point
├── backend/              # Backend code
│   ├── models/          # Database models
│   ├── routes/          # API routes
│   └── api/             # Background tasks
├── src/                 # Vue.js frontend
│   ├── components/      # Vue components
│   ├── views/          # Vue pages
│   └── router/         # Vue router
└── requirements.txt     # Python dependencies
```

## Development

The application uses:
- **Backend**: Flask with SQLAlchemy, JWT authentication
- **Frontend**: Vue.js 2 with Vue Router
- **Database**: SQLite (development)
- **Proxy**: Vue dev server proxies API calls to Flask backend


It is a multi-user app (one requires an administrator and other users) that acts as an exam preparation site for multiple courses.

