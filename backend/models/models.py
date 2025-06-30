from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    ___tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False, unique=True) #email
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    scores = db.Relationship('Score', backref='user', lazy=True,cascade="all, delete-orphan")


def create_admin_user():
    admin = User.query.filter_by(user_name="admin@gmail.com").first()
    if admin :
        admin = User(user_name="admin@gmail.com", password="admin123", full_name="Quiz Master Admin", is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")


class Subject(db.Model):
    __tablename__ = 'subjects'

    subject_id = db.Column(db.Integer,primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False, unique=True)
    subject_description = db.Column(db.Text, nullable=True)
    
    chapaters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

class Chapter(db.Model):
    __tablename__ = 'chapters'

    chapter_id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(100), nullable=False)
    chapter_description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id'), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")

    #    combination of chapter_name and subject_id must be unique.
    __table_args__ = (db.UniqueConstraint('chapter_name','subject_id',name='unique_chapter_name_per_subject'),)

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    quiz_id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer,db.ForeignKey('chapters.chapter_id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, default=datetime.utcnow,nullable=False)
    time_duration = db.Column(db.Time , nullable=False)
    quiz_remarks = db.Column(db.Text, nullable=True)

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
    correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4 for the correct option

class Score(db.Model):
    __tablename__ = 'scores'

    score_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer , db.ForeignKey("quizzes.quiz_id"), nullable=False)
    user_id = db.Column(db.Integer , db.ForeignKey("users.user_id"),nullable=False)
    timestamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)