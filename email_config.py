# email_config.py - Email Configuration for Quiz Master

# Email Configuration
# Update these settings to enable actual email sending

# SMTP Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Sender Email (Update this to your email)
SENDER_EMAIL = "quizmaster.app@gmail.com"

# Sender Password (Update this to your app password)
SENDER_PASSWORD = "your-app-password"

# Test Email (All emails will be sent to this address for testing)
TEST_EMAIL = "21f1006580@ds.study.iitm.ac.in"

# Email Settings
ENABLE_ACTUAL_EMAIL_SENDING = True  # Set to True to send actual emails

# Instructions:
# 1. Set ENABLE_ACTUAL_EMAIL_SENDING = True
# 2. Update SENDER_EMAIL to your Gmail address
# 3. Update SENDER_PASSWORD to your Gmail app password
# 4. All emails will be sent to TEST_EMAIL (21f1006580@ds.study.iitm.ac.in)
# 5. Uncomment the SMTP code in notification_tasks.py

# Gmail App Password Setup:
# 1. Go to your Google Account settings
# 2. Enable 2-factor authentication
# 3. Generate an app password for "Mail"
# 4. Use that password as SENDER_PASSWORD 