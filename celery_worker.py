#!/usr/bin/env python3
"""
Celery Worker Startup Script for Quiz Master
Run this script to start the Celery worker for background tasks
"""

import os
import sys
from celery import Celery
from celery.schedules import crontab

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from backend.api.quiz_tasks import check_and_expire_quizzes, send_expiry_warnings, daily_cleanup, expire_single_quiz

def create_celery_worker():
    """Create and configure Celery worker"""
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
    print("🚀 Starting Celery Worker for Quiz Master...")
    print("📋 Available tasks:")
    print("   - check_and_expire_quizzes")
    print("   - send_expiry_warnings") 
    print("   - daily_cleanup")
    print("   - expire_single_quiz")
    print("")
    print("⏰ Scheduled tasks:")
    print("   - Quiz expiry check: Every 2 minutes")
    print("   - Expiry warnings: Every 5 minutes")
    print("   - Daily cleanup: 2:00 AM UTC")
    print("")
    
    celery = create_celery_worker()
    
    # Start the worker
    celery.worker_main(['worker', '--loglevel=info']) 