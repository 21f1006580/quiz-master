# 📧 Email Setup Guide for Quiz Master

## 🎯 Goal
Send actual emails to `21f1006580@ds.study.iitm.ac.in` through Celery tasks.

## ✅ Current Status
- ✅ Email sending is **ENABLED**
- ✅ All emails configured for your IITM address
- ✅ Celery tasks are working
- ⚠️ Need to configure Gmail credentials

## 🔧 Setup Steps

### 1. Gmail App Password Setup
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-factor authentication** if not already enabled
3. Go to **"App passwords"** (under 2-Step Verification)
4. Select **"Mail"** and generate a password
5. Copy the **16-character password**

### 2. Update Email Configuration
Edit `email_config.py` and update these lines:

```python
# Update with your Gmail address
SENDER_EMAIL = "your-email@gmail.com"

# Update with your 16-character app password
SENDER_PASSWORD = "your-16-char-app-password"
```

### 3. Test Email Sending
```bash
python3 test_email.py
```

### 4. Trigger Celery Tasks
1. Start the application: `python3 app.py`
2. Start Celery worker: `python3 celery_worker.py`
3. Go to: `http://localhost:8080/admin/dashboard`
4. Click **"Trigger All Tasks"** or individual task buttons

## 📧 Email Types You'll Receive

### Daily Reminders
- **Subject**: Quiz Master - Daily Reminder
- **Content**: List of available quizzes and recent additions
- **Schedule**: Daily at 6:00 PM UTC

### Monthly Reports
- **Subject**: Quiz Master - Monthly Report (July 2025)
- **Content**: HTML report with performance statistics
- **Schedule**: 1st of each month at 9:00 AM UTC

### CSV Exports
- **Subject**: Quiz Master - CSV Export (filename.csv)
- **Content**: CSV file with quiz performance data
- **Trigger**: Manual from admin dashboard

### Admin Reports
- **Subject**: Quiz Master - Admin CSV Export
- **Content**: CSV file with all user performance data
- **Trigger**: Manual from admin dashboard

## 🧪 Testing

### Quick Test
```bash
python3 test_email.py
```

### Manual Task Trigger
1. Access admin dashboard: `http://localhost:8080/admin/dashboard`
2. Login with: `admin@gmail.com` / `admin123`
3. Click **"Trigger All Tasks"** button
4. Check your email: `21f1006580@ds.study.iitm.ac.in`

## 🔍 Troubleshooting

### Common Issues
1. **"Authentication failed"** - Check your app password
2. **"Less secure app access"** - Use app password, not regular password
3. **"Connection refused"** - Check internet connection
4. **"No emails received"** - Check spam folder

### Debug Steps
1. Run test script: `python3 test_email.py`
2. Check Celery worker logs
3. Verify Gmail app password
4. Ensure 2-factor authentication is enabled

## 📱 Email Examples

### Daily Reminder Email
```
Subject: Quiz Master - Daily Reminder

Hello [User Name],

This is your daily reminder from Quiz Master!

You have 5 quizzes available to take:
- Algebra Basics (Mathematics)
- Physics Fundamentals (Physics)
- Shakespeare Quiz (Literature)
- Chemistry Test (Science)
- History Quiz (History)

2 new quizzes have been added recently!

Login to Quiz Master to take your quizzes!
```

### Monthly Report Email
```
Subject: Quiz Master - Monthly Report (July 2025)

[HTML Report with statistics, charts, and performance data]
```

### CSV Export Email
```
Subject: Quiz Master - CSV Export (user_quiz_data.csv)

Hello [User Name],

Please find attached your CSV export: user_quiz_data.csv

This file contains your quiz performance data.

Best regards,
Quiz Master Team
```

## 🎯 Success Criteria
- ✅ Receive test email from `python3 test_email.py`
- ✅ Receive daily reminder emails at 6:00 PM UTC
- ✅ Receive monthly reports on 1st of each month
- ✅ Receive CSV exports when triggered from admin dashboard
- ✅ All emails sent to `21f1006580@ds.study.iitm.ac.in`

## 📞 Support
If you encounter issues:
1. Check the troubleshooting section above
2. Verify Gmail app password setup
3. Test with the provided test script
4. Check Celery worker logs for errors 