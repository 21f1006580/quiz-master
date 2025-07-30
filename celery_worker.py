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
from celery_app import make_celery

def create_celery_worker():
    """Create and configure Celery worker"""
    app = create_app()
    
    # Use the same Celery configuration as the Flask app
    celery = make_celery(app)
    
    return celery

if __name__ == '__main__':
    print("🚀 Starting Celery Worker for Quiz Master...")
    print("📋 Available tasks:")
    print("   - check_and_expire_quizzes")
    print("   - send_expiry_warnings") 
    print("   - daily_cleanup")
    print("   - expire_single_quiz")
    print("   - send_daily_reminders")
    print("   - generate_monthly_report")
    print("   - export_user_quiz_csv")
    print("   - export_admin_user_csv")
    print("")
    print("⏰ Scheduled tasks:")
    print("   - Quiz expiry check: Every 2 minutes")
    print("   - Expiry warnings: Every 5 minutes")
    print("   - Daily cleanup: 2:00 AM UTC")
    print("   - Daily reminders: 6:00 PM UTC")
    print("   - Monthly reports: 1st of month, 9:00 AM UTC")
    print("")
    
    celery = create_celery_worker()
    
    # Start the worker
    celery.worker_main(['worker', '--loglevel=info']) 