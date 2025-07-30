#!/usr/bin/env python3
"""
Celery Beat Scheduler for Quiz Master
Run this script to start the Celery Beat scheduler for periodic tasks
"""

import os
import sys
from celery import Celery
from celery.schedules import crontab

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def create_celery_beat():
    """Create and configure Celery Beat scheduler"""
    app = create_app()
    
    # Create Celery instance
    celery = Celery(
        'quiz_master',
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        include=['backend.api.quiz_tasks']
    )
    
    # Update configuration from Flask app
    celery.conf.update(app.config)
    
    # Configure periodic tasks
    celery.conf.beat_schedule = {
        'check-quiz-expiry': {
            'task': 'backend.api.quiz_tasks.check_and_expire_quizzes',
            'schedule': crontab(minute='*/2'),
        },
        'quiz-expiry-warnings': {
            'task': 'backend.api.quiz_tasks.send_expiry_warnings',
            'schedule': crontab(minute='*/5'),
        },
        'daily-quiz-cleanup': {
            'task': 'backend.api.quiz_tasks.daily_cleanup',
            'schedule': crontab(hour=2, minute=0),
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

if __name__ == '__main__':
    print("⏰ Starting Celery Beat Scheduler for Quiz Master...")
    print("📅 Scheduled tasks:")
    print("   - Quiz expiry check: Every 2 minutes")
    print("   - Expiry warnings: Every 5 minutes")
    print("   - Daily cleanup: 2:00 AM UTC")
    print("")
    
    celery = create_celery_beat()
    
    # Start the beat scheduler
    celery.worker_main(['beat', '--loglevel=info']) 