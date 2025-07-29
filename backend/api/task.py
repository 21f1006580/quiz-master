from datetime import datetime, timedelta
from backend.models.models import db, Quiz
from app import create_app
from app import celery

app = create_app()

@celery.task
def lock_expired_quizzes():
    with app.app_context():
        now = datetime.utcnow()
        active_quizzes = Quiz.query.filter_by(is_active=True).all()

        for quiz in active_quizzes:
            quiz_end = quiz.date_of_quiz + timedelta(minutes=quiz.time_duration)
            if now > quiz_end:
                quiz.is_active = False

        db.session.commit()
