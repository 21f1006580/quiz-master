# tasks/quiz_tasks.py - Create this folder and file

from celery_app import celery
from datetime import datetime, timedelta
from backend.models.models import db, Quiz, User, Score
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task(bind=True)
def check_and_expire_quizzes(self):
    """
    Background task to automatically expire quizzes
    Runs every 2 minutes via Celery Beat
    """
    try:
        logger.info(f"[{datetime.now()}] Starting quiz expiry check...")
        
        # Find all active quizzes that should be expired
        now = datetime.utcnow()
        
        # Get quizzes that should be expired
        expired_quizzes = Quiz.query.filter(
            Quiz.is_active == True,
            Quiz.auto_expire == True,
            Quiz.end_date_time.isnot(None),
            Quiz.end_date_time <= now
        ).all()
        
        expired_count = 0
        locked_quizzes = []
        
        for quiz in expired_quizzes:
            # Double-check expiry with model method
            if quiz.is_expired():
                quiz.is_active = False
                quiz.updated_at = now
                expired_count += 1
                
                locked_quizzes.append({
                    'quiz_id': quiz.quiz_id,
                    'title': quiz.title,
                    'expired_at': quiz.end_date_time.isoformat(),
                    'chapter_id': quiz.chapter_id
                })
                
                logger.info(f" Locked expired quiz: {quiz.title} (ID: {quiz.quiz_id})")
        
        # Commit all changes
        if expired_count > 0:
            db.session.commit()
            logger.info(f"  📊 Total quizzes auto-locked: {expired_count}")
        else:
            logger.info("  ℹ️  No quizzes needed to be expired")
        
        # Return task result
        return {
            'success': True,
            'expired_count': expired_count,
            'locked_quizzes': locked_quizzes,
            'timestamp': now.isoformat(),
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error in quiz expiry check: {str(e)}")
        db.session.rollback()
        
        # Retry task on failure (max 3 retries)
        if self.request.retries < 3:
            logger.info(f" Retrying task in 60 seconds (attempt {self.request.retries + 1}/3)")
            raise self.retry(countdown=60, max_retries=3)
        
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }

@celery.task(bind=True)
def send_expiry_warnings(self):
    """
    Send warnings for quizzes expiring soon
    Runs every 5 minutes
    """
    try:
        logger.info(f"[{datetime.now()}] Checking for quizzes needing expiry warnings...")
        
        now = datetime.utcnow()
        warning_time = now + timedelta(minutes=30)  # Warn 30 minutes before expiry
        
        # Find quizzes expiring in the next 30 minutes
        soon_to_expire = Quiz.query.filter(
            Quiz.is_active == True,
            Quiz.auto_expire == True,
            Quiz.end_date_time.isnot(None),
            Quiz.end_date_time <= warning_time,
            Quiz.end_date_time > now
        ).all()
        
        warnings_sent = 0
        warned_quizzes = []
        
        for quiz in soon_to_expire:
            time_remaining = quiz.get_time_remaining()
            
            # You can add actual notification logic here (email, SMS, etc.)
            logger.info(f"Quiz '{quiz.title}' expires in {time_remaining} minutes")
            
            # Example: Send notification to users with ongoing attempts
            ongoing_users = get_users_with_ongoing_attempts(quiz.quiz_id)
            for user in ongoing_users:
                # Here you would send actual notifications
                logger.info(f" Would notify user {user.user_name} about quiz expiry")
            
            warnings_sent += 1
            warned_quizzes.append({
                'quiz_id': quiz.quiz_id,
                'title': quiz.title,
                'time_remaining': time_remaining,
                'expires_at': quiz.end_date_time.isoformat()
            })
        
        if warnings_sent > 0:
            logger.info(f" Sent {warnings_sent} expiry warnings")
        else:
            logger.info("  ℹ️  No expiry warnings needed")
        
        return {
            'success': True,
            'warnings_sent': warnings_sent,
            'warned_quizzes': warned_quizzes,
            'timestamp': now.isoformat(),
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f" Error sending expiry warnings: {str(e)}")
        
        if self.request.retries < 2:
            raise self.retry(countdown=120, max_retries=2)
        
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }

@celery.task
def daily_cleanup():
    """
    Daily maintenance task for quiz system
    Runs at 2 AM every day
    """
    try:
        logger.info(f"[{datetime.now()}] Running daily quiz cleanup...")
        
        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=30)  # Clean up quizzes older than 30 days
        
        # Find very old expired quizzes
        old_quizzes = Quiz.query.filter(
            Quiz.is_active == False,
            Quiz.end_date_time.isnot(None),
            Quiz.end_date_time < cutoff_date
        ).all()
        
        # Log old quizzes (you could archive them instead of just logging)
        archived_count = 0
        for quiz in old_quizzes:
            logger.info(f"  Old expired quiz: {quiz.title} (expired {quiz.end_date_time})")
            # Here you could move to archive table or mark as archived
            archived_count += 1
        
        # Clean up task results older than 7 days (optional)
        # This helps keep your Redis/database clean
        
        logger.info(f"  Daily cleanup completed. Found {archived_count} old quizzes")
        
        return {
            'success': True,
            'old_quizzes_found': archived_count,
            'cleanup_date': cutoff_date.isoformat(),
            'timestamp': now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"   Error in daily cleanup: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@celery.task
def expire_single_quiz(quiz_id):
    """
    Manually expire a specific quiz
    Can be called from admin interface
    """
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {
                'success': False,
                'error': f'Quiz {quiz_id} not found'
            }
        
        if quiz.auto_lock_if_expired():
            db.session.commit()
            logger.info(f" Manually expired quiz: {quiz.title} (ID: {quiz_id})")
            
            return {
                'success': True,
                'message': f'Quiz "{quiz.title}" has been expired',
                'quiz_id': quiz_id,
                'expired_at': datetime.utcnow().isoformat()
            }
        else:
            return {
                'success': False,
                'message': f'Quiz "{quiz.title}" is not eligible for expiry',
                'quiz_id': quiz_id
            }
            
    except Exception as e:
        db.session.rollback()
        logger.error(f" Error expiring quiz {quiz_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'quiz_id': quiz_id
        }

def get_users_with_ongoing_attempts(quiz_id):
    """
    Helper function to find users who might have ongoing quiz attempts
    This is a placeholder - you could track active sessions in Redis
    """
    # For now, return empty list - you could implement session tracking
    # to find users who started but haven't submitted the quiz
    return []

# Additional utility tasks

@celery.task
def generate_quiz_report():
    """
    Generate daily quiz activity report
    """
    try:
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get today's quiz statistics
        active_quizzes = Quiz.query.filter(Quiz.is_active == True).count()
        expired_today = Quiz.query.filter(
            Quiz.end_date_time >= today,
            Quiz.end_date_time < today + timedelta(days=1),
            Quiz.is_active == False
        ).count()
        
        # Get submission statistics
        submissions_today = Score.query.filter(
            Score.attempt_datetime >= today
        ).count()
        
        report = {
            'date': today.isoformat(),
            'active_quizzes': active_quizzes,
            'expired_today': expired_today,
            'submissions_today': submissions_today,
            'generated_at': now.isoformat()
        }
        
        logger.info(f"Daily Report: {active_quizzes} active, {expired_today} expired, {submissions_today} submissions")
        
        return report
        
    except Exception as e:
        logger.error(f" Error generating quiz report: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }   