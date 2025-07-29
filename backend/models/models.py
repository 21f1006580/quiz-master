from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False, unique=True)  # email
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    scores = db.relationship('Score', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'full_name': self.full_name,
            'qualification': self.qualification,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

def create_admin_user():
    """Create admin user if doesn't exist"""
    admin = User.query.filter_by(user_name="admin@gmail.com").first()
    if not admin:
        admin = User(
            user_name="admin@gmail.com",
            full_name="Quiz Master Admin",
            is_admin=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")

class Subject(db.Model):
    __tablename__ = 'subjects'

    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False, unique=True)
    subject_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.subject_id,
            'name': self.subject_name,
            'description': self.subject_description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
          
        }
    
    def __repr__(self):
        return f'<Subject {self.name}>'


class Chapter(db.Model):
    __tablename__ = 'chapters'

    chapter_id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(100), nullable=False)
    chapter_description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")

    # Combination of chapter_name and subject_id must be unique
    __table_args__ = (db.UniqueConstraint('chapter_name', 'subject_id', name='unique_chapter_name_per_subject'),)

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    quiz_id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    quiz_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)  # Duration in minutes
    quiz_remarks = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete-orphan")
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")



class Question(db.Model):
    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.Text, nullable=False)
    option_2 = db.Column(db.Text, nullable=False)
    option_3 = db.Column(db.Text, nullable=False)
    option_4 = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4

class Score(db.Model):
    __tablename__ = 'scores'

    score_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.quiz_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    total_score = db.Column(db.Float, nullable=False)  # Percentage score
    time_taken = db.Column(db.Integer, nullable=True)  # Time taken in seconds
    attempt_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one attempt per user per quiz
    __table_args__ = (db.UniqueConstraint('user_id', 'quiz_id', name='unique_user_quiz_attempt'),)