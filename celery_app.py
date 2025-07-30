# celery_app.py - Create this file in your project root

from celery import Celery
from celery.schedules import crontab
import os

def make_celery(app):
    """Create Celery instance"""
    celery = Celery(
        app.import_name,
        backend=app.config.get('result_backend', 'redis://localhost:6379/0'),
        broker=app.config.get('broker_url', 'redis://localhost:6379/0'),
        include=['backend.api.quiz_tasks', 'backend.api.notification_tasks']  # Include our task modules
    )
    
    # Update configuration from Flask app
    celery.conf.update(app.config)
    
    # Configure periodic tasks
    celery.conf.beat_schedule = {
        # Check for expired quizzes every 2 minutes
        'check-quiz-expiry': {
            'task': 'backend.api.quiz_tasks.check_and_expire_quizzes',
            'schedule': crontab(minute='*/2'),
        },
        # Send expiry warnings every 5 minutes
        'quiz-expiry-warnings': {
            'task': 'backend.api.quiz_tasks.send_expiry_warnings',
            'schedule': crontab(minute='*/5'),
        },
        # Daily cleanup at 2 AM
        'daily-quiz-cleanup': {
            'task': 'backend.api.quiz_tasks.daily_cleanup',
            'schedule': crontab(hour=2, minute=0),
        },
        # Daily reminders at 6 PM
        'daily-reminders': {
            'task': 'backend.api.notification_tasks.send_daily_reminders',
            'schedule': crontab(hour=18, minute=0),  # 6 PM
        },
        # Monthly reports on 1st of every month at 9 AM
        'monthly-reports': {
            'task': 'backend.api.notification_tasks.generate_monthly_report',
            'schedule': crontab(day_of_month=1, hour=9, minute=0),
        }
    }
    
    celery.conf.timezone = 'UTC'
    
    # Bind Flask app context to Celery tasks
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery