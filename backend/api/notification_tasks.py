# backend/api/notification_tasks.py - Notification and Report Tasks

from celery_app import celery
from datetime import datetime, timedelta
from backend.models.models import db, User, Quiz, Score, Subject, Chapter
import smtplib
import csv
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task(bind=True)
def send_daily_reminders(self):
    """
    Daily reminder task - sends reminders to users who haven't visited or for new quizzes
    Runs daily at 6 PM
    """
    try:
        logger.info(f"[{datetime.now()}] Starting daily reminder task...")
        
        # Get all regular users (non-admin)
        users = User.query.filter_by(is_admin=False).all()
        
        # Get recent quizzes (created in last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_quizzes = Quiz.query.filter(
            Quiz.created_at >= week_ago
        ).all()
        
        reminders_sent = 0
        
        for user in users:
            # Check if user has been inactive (no login in last 3 days)
            # For demo purposes, we'll send reminders to all users
            # In production, you'd check last login time
            
            # Check if user has unvisited quizzes
            user_attempts = Score.query.filter_by(user_id=user.user_id).all()
            attempted_quiz_ids = [score.quiz_id for score in user_attempts]
            
            available_quizzes = Quiz.query.filter(
                Quiz.is_active == True,
                Quiz.date_of_quiz <= datetime.utcnow()
            ).all()
            
            unvisited_quizzes = [quiz for quiz in available_quizzes if quiz.quiz_id not in attempted_quiz_ids]
            
            if unvisited_quizzes or recent_quizzes:
                # Send reminder email
                send_reminder_email(user, unvisited_quizzes, recent_quizzes)
                reminders_sent += 1
                logger.info(f"Sent reminder to user: {user.user_name}")
        
        logger.info(f"Daily reminders completed. Sent {reminders_sent} reminders.")
        
        return {
            'success': True,
            'reminders_sent': reminders_sent,
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error in daily reminder task: {str(e)}")
        
        if self.request.retries < 3:
            raise self.retry(countdown=300, max_retries=3)
        
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }

@celery.task(bind=True)
def generate_monthly_report(self):
    """
    Monthly activity report task
    Runs on the first day of every month
    """
    try:
        logger.info(f"[{datetime.now()}] Starting monthly report generation...")
        
        # Get last month's data
        now = datetime.utcnow()
        if now.month == 1:
            last_month = now.replace(year=now.year-1, month=12)
        else:
            last_month = now.replace(month=now.month-1)
        
        start_date = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        
        # Get all users
        users = User.query.filter_by(is_admin=False).all()
        reports_sent = 0
        
        for user in users:
            # Get user's quiz attempts for last month
            scores = Score.query.filter(
                Score.user_id == user.user_id,
                Score.attempt_datetime >= start_date,
                Score.attempt_datetime <= end_date
            ).all()
            
            if scores:
                # Generate report
                report_html = generate_user_report_html(user, scores, start_date, end_date)
                send_monthly_report_email(user, report_html, start_date)
                reports_sent += 1
                logger.info(f"Sent monthly report to user: {user.user_name}")
        
        logger.info(f"Monthly reports completed. Sent {reports_sent} reports.")
        
        return {
            'success': True,
            'reports_sent': reports_sent,
            'period': f"{start_date.strftime('%B %Y')}",
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error in monthly report task: {str(e)}")
        
        if self.request.retries < 2:
            raise self.retry(countdown=600, max_retries=2)
        
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }

@celery.task(bind=True)
def export_user_quiz_csv(self, user_id):
    """
    Export user's quiz data as CSV
    User-triggered async job
    """
    try:
        logger.info(f"[{datetime.now()}] Starting CSV export for user {user_id}...")
        
        user = User.query.get(user_id)
        if not user:
            return {
                'success': False,
                'error': 'User not found'
            }
        
        # Get user's quiz scores with details
        scores = db.session.query(Score, Quiz, Chapter, Subject).join(
            Quiz, Score.quiz_id == Quiz.quiz_id
        ).join(
            Chapter, Quiz.chapter_id == Chapter.chapter_id
        ).join(
            Subject, Chapter.subject_id == Subject.subject_id
        ).filter(
            Score.user_id == user_id
        ).order_by(Score.attempt_datetime.desc()).all()
        
        # Create CSV
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        
        # Write header
        csv_writer.writerow([
            'Quiz ID', 'Quiz Title', 'Subject', 'Chapter', 
            'Date of Quiz', 'Attempt Date', 'Score (%)', 
            'Correct Answers', 'Total Questions', 'Time Taken (seconds)'
        ])
        
        # Write data
        for score, quiz, chapter, subject in scores:
            csv_writer.writerow([
                quiz.quiz_id,
                quiz.title,
                subject.name,
                chapter.name,
                quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M') if quiz.date_of_quiz else '',
                score.attempt_datetime.strftime('%Y-%m-%d %H:%M'),
                score.total_score,
                score.correct_answers,
                score.total_questions,
                score.time_taken or 0
            ])
        
        # Send email with CSV attachment
        send_csv_export_email(user, csv_data.getvalue(), 'user_quiz_data.csv')
        
        logger.info(f"CSV export completed for user {user_id}")
        
        return {
            'success': True,
            'user_id': user_id,
            'records_exported': len(scores),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error in CSV export task: {str(e)}")
        
        if self.request.retries < 2:
            raise self.retry(countdown=120, max_retries=2)
        
        return {
            'success': False,
            'error': str(e),
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }

@celery.task(bind=True)
def export_admin_user_csv(self):
    """
    Export all user performance data as CSV for admin
    Admin-triggered async job
    """
    try:
        logger.info(f"[{datetime.now()}] Starting admin CSV export...")
        
        # Get all users with their performance data
        users = User.query.filter_by(is_admin=False).all()
        
        # Create CSV
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        
        # Write header
        csv_writer.writerow([
            'User ID', 'Username', 'Full Name', 'Email',
            'Quizzes Taken', 'Average Score (%)', 'Best Score (%)',
            'Total Time Spent (minutes)', 'Last Activity'
        ])
        
        # Write data
        for user in users:
            scores = Score.query.filter_by(user_id=user.user_id).all()
            
            if scores:
                total_quizzes = len(scores)
                avg_score = sum(s.total_score for s in scores) / total_quizzes
                best_score = max(s.total_score for s in scores)
                total_time = sum(s.time_taken or 0 for s in scores) / 60  # Convert to minutes
                last_activity = max(s.attempt_datetime for s in scores)
            else:
                total_quizzes = 0
                avg_score = 0
                best_score = 0
                total_time = 0
                last_activity = None
            
            csv_writer.writerow([
                user.user_id,
                user.user_name,
                user.full_name,
                user.user_name,  # Email is same as username
                total_quizzes,
                round(avg_score, 2),
                best_score,
                round(total_time, 2),
                last_activity.strftime('%Y-%m-%d %H:%M') if last_activity else 'Never'
            ])
        
        # Send email with CSV attachment to admin
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            send_csv_export_email(admin, csv_data.getvalue(), 'admin_user_performance.csv')
        
        logger.info(f"Admin CSV export completed")
        
        return {
            'success': True,
            'users_exported': len(users),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }
        
    except Exception as e:
        logger.error(f"Error in admin CSV export task: {str(e)}")
        
        if self.request.retries < 2:
            raise self.retry(countdown=120, max_retries=2)
        
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }

# Helper functions for email sending
def send_reminder_email(user, unvisited_quizzes, recent_quizzes):
    """Send reminder email to user"""
    try:
        # For demo purposes, we'll just log the email
        # In production, you'd use SMTP or email service
        logger.info(f"Would send reminder email to {user.user_name}")
        logger.info(f"Unvisited quizzes: {len(unvisited_quizzes)}")
        logger.info(f"Recent quizzes: {len(recent_quizzes)}")
        
        # Example email content
        subject = "Quiz Master - Daily Reminder"
        body = f"""
        Hello {user.full_name},
        
        You have {len(unvisited_quizzes)} quizzes available to take!
        {len(recent_quizzes)} new quizzes have been added recently.
        
        Visit Quiz Master to take your quizzes!
        
        Best regards,
        Quiz Master Team
        """
        
        # Send to the provided email address for testing
        test_email = "21f1006580@ds.study.iitm.ac.in"
        logger.info(f"Email would be sent to: {test_email}")
        logger.info(f"Email content: {subject}\n{body}")
        
    except Exception as e:
        logger.error(f"Error sending reminder email: {e}")

def generate_user_report_html(user, scores, start_date, end_date):
    """Generate HTML report for user"""
    total_quizzes = len(scores)
    avg_score = sum(s.total_score for s in scores) / total_quizzes if scores else 0
    best_score = max(s.total_score for s in scores) if scores else 0
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat {{ text-align: center; padding: 10px; background: #e8f4fd; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Quiz Master - Monthly Activity Report</h1>
            <p>Report for: {start_date.strftime('%B %Y')}</p>
            <p>User: {user.full_name} ({user.user_name})</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <h3>{total_quizzes}</h3>
                <p>Quizzes Taken</p>
            </div>
            <div class="stat">
                <h3>{avg_score:.1f}%</h3>
                <p>Average Score</p>
            </div>
            <div class="stat">
                <h3>{best_score:.1f}%</h3>
                <p>Best Score</p>
            </div>
        </div>
        
        <h2>Quiz Details</h2>
        <table>
            <tr>
                <th>Quiz</th>
                <th>Subject</th>
                <th>Score</th>
                <th>Date</th>
            </tr>
    """
    
    for score in scores:
        quiz = score.quiz
        chapter = quiz.chapter
        subject = chapter.subject
        
        html += f"""
            <tr>
                <td>{quiz.title}</td>
                <td>{subject.name} - {chapter.name}</td>
                <td>{score.total_score:.1f}%</td>
                <td>{score.attempt_datetime.strftime('%Y-%m-%d')}</td>
            </tr>
        """
    
    html += """
        </table>
        
        <p>Thank you for using Quiz Master!</p>
    </body>
    </html>
    """
    
    return html

def send_monthly_report_email(user, report_html, report_date):
    """Send monthly report email to user"""
    try:
        # For demo purposes, we'll just log the email
        logger.info(f"Would send monthly report to {user.user_name}")
        logger.info(f"Report period: {report_date.strftime('%B %Y')}")
        
        # Send to the provided email address for testing
        test_email = "21f1006580@ds.study.iitm.ac.in"
        logger.info(f"Email would be sent to: {test_email}")
        
        # In production, send actual email here
        subject = f"Quiz Master - Monthly Report ({report_date.strftime('%B %Y')})"
        
        logger.info(f"Email subject: {subject}")
        logger.info(f"Email content length: {len(report_html)} characters")
        
    except Exception as e:
        logger.error(f"Error sending monthly report email: {e}")

def send_csv_export_email(user, csv_content, filename):
    """Send CSV export email to user"""
    try:
        # For demo purposes, we'll just log the email
        logger.info(f"Would send CSV export to {user.user_name}")
        logger.info(f"Filename: {filename}")
        logger.info(f"CSV content length: {len(csv_content)} characters")
        
        # Send to the provided email address for testing
        test_email = "21f1006580@ds.study.iitm.ac.in"
        logger.info(f"Email would be sent to: {test_email}")
        
        # In production, send actual email with CSV attachment here
        subject = f"Quiz Master - CSV Export ({filename})"
        
        logger.info(f"Email subject: {subject}")
        
    except Exception as e:
        logger.error(f"Error sending CSV export email: {e}") 