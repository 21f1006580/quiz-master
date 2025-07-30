# backend/models/models.py - FIXED VERSION

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
            'id': self.user_id,  # Use 'id' for frontend consistency
            'user_id': self.user_id,
            'username': self.user_name,  # Map user_name to username for frontend
            'email': self.user_name,     # Since user_name is email in your schema
            'user_name': self.user_name,
            'full_name': self.full_name,
            'qualification': self.qualification,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'dob': self.date_of_birth.isoformat() if self.date_of_birth else None,  # Alternative field name
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
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
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.subject_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Subject {self.name}>'


class Chapter(db.Model):
    __tablename__ = 'chapters'

    chapter_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")

    # Combination of name and subject_id must be unique
    __table_args__ = (db.UniqueConstraint('name', 'subject_id', name='unique_chapter_name_per_subject'),)

    def to_dict(self):
        return {
            'id': self.chapter_id,
            'name': self.name,
            'description': self.description,
            'subject_id': self.subject_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# FIXED Quiz model - corrected foreign key reference
class Quiz(db.Model):
    __tablename__ = 'quizzes'  # CHANGED: Use consistent table name
    
    quiz_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    # FIXED: Reference the correct table name
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    
    # ENHANCED SCHEDULING FIELDS
    date_of_quiz = db.Column(db.DateTime, nullable=False)  # Quiz start time
    end_date_time = db.Column(db.DateTime, nullable=True)  # Quiz end time (optional)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    
    # NEW SCHEDULING FIELDS
    is_active = db.Column(db.Boolean, default=True)
    allow_multiple_attempts = db.Column(db.Boolean, default=False)
    show_results_immediately = db.Column(db.Boolean, default=True)
    auto_start = db.Column(db.Boolean, default=True)  # Auto available at start time
    auto_end = db.Column(db.Boolean, default=True)    # Auto lock at end time
    
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - FIXED: No need to redefine backref since it's defined in Chapter
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy=True)

    def to_dict(self):
        return {
            'id': self.quiz_id,
            'quiz_id': self.quiz_id,
            'title': self.title,
            'chapter_id': self.chapter_id,
            'date_of_quiz': self.date_of_quiz.isoformat() if self.date_of_quiz else None,
            'end_date_time': self.end_date_time.isoformat() if self.end_date_time else None,
            'time_duration': self.time_duration,
            'is_active': self.is_active,
            'allow_multiple_attempts': self.allow_multiple_attempts,
            'show_results_immediately': self.show_results_immediately,
            'auto_start': self.auto_start,
            'auto_end': self.auto_end,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question_count': len(self.questions) if self.questions else 0,
            'status': self.get_status(),
            'is_available': self.is_available_now(),
            'time_remaining': self.get_time_remaining()
        }
    
    def get_status(self):
        """Get current quiz status"""
        now = datetime.utcnow()
        
        if not self.is_active:
            return 'inactive'
        
        if now < self.date_of_quiz:
            return 'upcoming'
        
        # Check if quiz has ended
        if self.end_date_time and now > self.end_date_time:
            return 'expired'
        elif not self.end_date_time:
            # If no end time set, quiz is always available once started
            return 'active'
        else:
            return 'active'
    
    def is_available_now(self):
        """Check if quiz is currently available for attempts"""
        if not self.is_active:
            return False
            
        now = datetime.utcnow()
        
        # Check if quiz has started
        if now < self.date_of_quiz:
            return False
        
        # Check if quiz has ended
        if self.end_date_time and now > self.end_date_time:
            return False
            
        return True
    
    def get_time_remaining(self):
        """Get time remaining until quiz ends (in minutes)"""
        if not self.end_date_time:
            return None
            
        now = datetime.utcnow()
        if now > self.end_date_time:
            return 0
            
        diff = self.end_date_time - now
        return int(diff.total_seconds() / 60)
    
    def can_user_attempt(self, user_id):
        """Check if a specific user can attempt this quiz"""
        if not self.is_available_now():
            return False, "Quiz is not currently available"
        
        # Check if user has already attempted
        if not self.allow_multiple_attempts:
            existing_attempt = Score.query.filter_by(
                quiz_id=self.quiz_id, 
                user_id=user_id
            ).first()
            
            if existing_attempt:
                return False, "You have already attempted this quiz"
        
        return True, "Quiz is available"


class Question(db.Model):
    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.Text, nullable=False)
    option2 = db.Column(db.Text, nullable=False)
    option3 = db.Column(db.Text, nullable=True)
    option4 = db.Column(db.Text, nullable=True)
    correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.question_id,
            'quiz_id': self.quiz_id,
            'question_statement': self.question_statement,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correct_option': self.correct_option,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

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
    
    # Ensure one attempt per user per quiz (unless multiple attempts allowed)
    __table_args__ = (db.UniqueConstraint('user_id', 'quiz_id', name='unique_user_quiz_attempt'),)

    def to_dict(self):
        return {
            'id': self.score_id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'total_score': self.total_score,
            'time_taken': self.time_taken,
            'attempt_datetime': self.attempt_datetime.isoformat() if self.attempt_datetime else None
        }