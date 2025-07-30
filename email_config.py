# email_config.py - Email Configuration for Quiz Master

# Email Configuration
# Update these settings to enable actual email sending

# SMTP Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Sender Email (Using IITM email address)
SENDER_EMAIL = "21f1006580@ds.study.iitm.ac.in"

# Sender Password (Update this to your app password)
SENDER_PASSWORD = "your-app-password"

# Test Email (All emails will be sent to this address for testing)
TEST_EMAIL = "21f1006580@ds.study.iitm.ac.in"

# Email Settings
ENABLE_ACTUAL_EMAIL_SENDING = True  # Set to True to send actual emails

# Instructions:
# 1. Set ENABLE_ACTUAL_EMAIL_SENDING = True
# 2. SENDER_EMAIL is set to your IITM address (21f1006580@ds.study.iitm.ac.in)
# 3. Update SENDER_PASSWORD to your Google app password
# 4. All emails will be sent to TEST_EMAIL (21f1006580@ds.study.iitm.ac.in)
# 5. Both sender and recipient are the same IITM address

# Google App Password Setup for IITM Email:
# 1. Go to your Google Account settings (for 21f1006580@ds.study.iitm.ac.in)
# 2. Enable 2-factor authentication
# 3. Generate an app password for "Mail"
# 4. Use that password as SENDER_PASSWORD
# 5. IITM emails use Gmail's SMTP server 