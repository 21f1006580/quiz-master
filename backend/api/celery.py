from celery import Celery
from datetime import timedelta

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    
    # Update configuration from Flask app config
    celery.conf.update(app.config)
    
    # Configure periodic tasks
    celery.conf.beat_schedule = {
        'daily-quiz-reminders': {
            'task': 'backend.tasks.send_daily_reminders',
            'schedule': timedelta(hours=24),  # Run daily
            # 'schedule': crontab(hour=18, minute=0),  # Run at 6 PM daily
        },
        'monthly-activity-reports': {
            'task': 'backend.tasks.send_monthly_reports',
            'schedule': timedelta(days=30),  # Run monthly
            # 'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st day of month at 9 AM
        },
    }
    
    celery.conf.timezone = 'UTC'
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
