# backend/models/models.py - FIXED VERSION

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta

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

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    quiz_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.chapter_id'), nullable=False)
    
    # Scheduling fields
    date_of_quiz = db.Column(db.DateTime, nullable=False)  # Start time
    end_date_time = db.Column(db.DateTime, nullable=True)  # End time (optional)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    
    # Anytime quiz feature
    is_anytime_quiz = db.Column(db.Boolean, default=False)  # Can be taken anytime
    
    # Auto-expiry settings
    is_active = db.Column(db.Boolean, default=True)
    auto_expire = db.Column(db.Boolean, default=True)  # Auto-lock after expiry
    grace_period = db.Column(db.Integer, default=0)    # Extra minutes after end time
    
    # Other fields
    allow_multiple_attempts = db.Column(db.Boolean, default=False)
    show_results_immediately = db.Column(db.Boolean, default=True)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy=True)

    def get_effective_end_time(self):
        """Calculate when quiz should actually expire"""
        if self.end_date_time:
            # If explicit end time is set, use it
            end_time = self.end_date_time
        else:
            # If no end time, quiz runs indefinitely (or until manually stopped)
            return None
        
        # Add grace period if specified
        if self.grace_period and self.grace_period > 0:
            end_time = end_time + timedelta(minutes=self.grace_period)
        
        return end_time

    def is_expired(self):
        """Check if quiz has expired"""
        if not self.auto_expire:
            return False
            
        effective_end = self.get_effective_end_time()
        if not effective_end:
            return False
            
        return datetime.utcnow() > effective_end

    def should_auto_lock(self):
        """Check if quiz should be automatically locked"""
        return self.auto_expire and self.is_expired()

    def get_status(self):
        """Get current quiz status with auto-expiry logic"""
        now = datetime.utcnow()
        
        # Check if manually deactivated
        if not self.is_active:
            return 'inactive'
        
        # For anytime quizzes, only check if active
        if self.is_anytime_quiz:
            return 'active'
        
        # Check if quiz hasn't started yet
        if now < self.date_of_quiz:
            return 'upcoming'
        
        # Check if quiz has expired
        if self.is_expired():
            return 'expired'
        
        # Check if quiz is ending soon (within 30 minutes)
        effective_end = self.get_effective_end_time()
        if effective_end:
            time_to_end = (effective_end - now).total_seconds() / 60
            if 0 < time_to_end <= 30:
                return 'ending_soon'
        
        return 'active'

    def auto_lock_if_expired(self):
        """Automatically lock quiz if it has expired"""
        if self.should_auto_lock() and self.is_active:
            self.is_active = False
            self.updated_at = datetime.utcnow()
            return True
        return False

    def is_available_for_attempt(self, user_id=None):
        """Check if quiz is available for attempts (with auto-expiry check)"""
        # Auto-lock if expired
        was_locked = self.auto_lock_if_expired()
        if was_locked:
            db.session.commit()  # Save the auto-lock
        
        # Check basic availability
        if not self.is_active:
            return False, "Quiz is not active"
        
        now = datetime.utcnow()
        
        # For anytime quizzes, skip time-based checks
        if self.is_anytime_quiz:
            # Only check if quiz is active and user hasn't attempted (if multiple attempts not allowed)
            if user_id and not self.allow_multiple_attempts:
                existing_attempt = Score.query.filter_by(
                    quiz_id=self.quiz_id, 
                    user_id=user_id
                ).first()
                
                if existing_attempt:
                    return False, "You have already attempted this quiz"
            
            return True, "Quiz is available anytime"
        
        # For scheduled quizzes, check time constraints
        # Check if quiz has started
        if now < self.date_of_quiz:
            return False, "Quiz has not started yet"
        
        # Check if quiz has expired
        if self.is_expired():
            return False, "Quiz has expired"
        
        # Check multiple attempts if user specified
        if user_id and not self.allow_multiple_attempts:
            existing_attempt = Score.query.filter_by(
                quiz_id=self.quiz_id, 
                user_id=user_id
            ).first()
            
            if existing_attempt:
                return False, "You have already attempted this quiz"
        
        return True, "Quiz is available"

    def get_time_remaining(self):
        """Get time remaining until quiz expires (in minutes)"""
        effective_end = self.get_effective_end_time()
        if not effective_end:
            return None
            
        now = datetime.utcnow()
        if now > effective_end:
            return 0
            
        diff = effective_end - now
        return int(diff.total_seconds() / 60)

    def to_dict(self):
        return {
            'id': self.quiz_id,
            'quiz_id': self.quiz_id,
            'title': self.title,
            'chapter_id': self.chapter_id,
            'date_of_quiz': self.date_of_quiz.isoformat() if self.date_of_quiz else None,
            'end_date_time': self.end_date_time.isoformat() if self.end_date_time else None,
            'effective_end_time': self.get_effective_end_time().isoformat() if self.get_effective_end_time() else None,
            'time_duration': self.time_duration,
            'is_anytime_quiz': self.is_anytime_quiz,
            'is_active': self.is_active,
            'auto_expire': self.auto_expire,
            'grace_period': self.grace_period,
            'allow_multiple_attempts': self.allow_multiple_attempts,
            'show_results_immediately': self.show_results_immediately,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question_count': len(self.questions) if self.questions else 0,
            'status': self.get_status(),
            'time_remaining': self.get_time_remaining(),
            'is_expired': self.is_expired(),
            'is_available': self.is_available_for_attempt()[0]
        }

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