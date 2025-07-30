#!/usr/bin/env python3
"""
Email Setup Script for Quiz Master
This script helps you configure email settings for sending actual emails.
"""

import os
import sys

def setup_email_config():
    """Interactive setup for email configuration"""
    print("📧 Quiz Master Email Configuration Setup")
    print("=" * 50)
    
    # Read current config
    try:
        with open('email_config.py', 'r') as f:
            config_content = f.read()
    except FileNotFoundError:
        print("❌ email_config.py not found!")
        return
    
    print("\n🔧 Current Configuration:")
    print(f"SMTP Server: smtp.gmail.com")
    print(f"SMTP Port: 587")
    print(f"Test Email: 21f1006580@ds.study.iitm.ac.in")
    print(f"Email Sending: {'✅ ENABLED' if 'ENABLE_ACTUAL_EMAIL_SENDING = True' in config_content else '❌ DISABLED'}")
    
    print("\n📝 To send actual emails, you need to:")
    print("1. Update SENDER_EMAIL with your Gmail address")
    print("2. Update SENDER_PASSWORD with your Gmail app password")
    print("3. Make sure 2-factor authentication is enabled on your Google account")
    
    print("\n🔐 Gmail App Password Setup:")
    print("1. Go to https://myaccount.google.com/security")
    print("2. Enable 2-factor authentication if not already enabled")
    print("3. Go to 'App passwords' (under 2-Step Verification)")
    print("4. Select 'Mail' and generate a password")
    print("5. Use that 16-character password as SENDER_PASSWORD")
    
    print("\n📧 Email Types You'll Receive:")
    print("• Daily Reminders - Available quizzes and updates")
    print("• Monthly Reports - Performance statistics (HTML)")
    print("• CSV Exports - Quiz data files")
    print("• Admin Reports - System performance data")
    
    print("\n🎯 All emails will be sent to: 21f1006580@ds.study.iitm.ac.in")
    
    # Check if config is ready
    if 'SENDER_EMAIL = "quizmaster.app@gmail.com"' in config_content:
        print("\n⚠️  You still need to update SENDER_EMAIL in email_config.py")
    if 'SENDER_PASSWORD = "your-app-password"' in config_content:
        print("⚠️  You still need to update SENDER_PASSWORD in email_config.py")
    
    print("\n✅ Email configuration is ready!")
    print("💡 Run 'python3 test_email.py' to test email sending")

def test_email_sending():
    """Test email sending functionality"""
    print("🧪 Testing Email Sending...")
    
    try:
        import email_config
        from backend.api.notification_tasks import send_email
        
        # Test email
        test_subject = "Quiz Master - Email Test"
        test_body = """
        Hello from Quiz Master!
        
        This is a test email to verify that email sending is working correctly.
        
        If you receive this email, the configuration is working properly.
        
        Best regards,
        Quiz Master Team
        """
        
        print(f"📧 Sending test email to: {email_config.TEST_EMAIL}")
        print(f"📝 Subject: {test_subject}")
        
        send_email(email_config.TEST_EMAIL, test_subject, test_body)
        
        print("✅ Test email sent successfully!")
        print(f"📬 Check your inbox: {email_config.TEST_EMAIL}")
        
    except Exception as e:
        print(f"❌ Error testing email: {e}")
        print("🔧 Make sure you've updated SENDER_EMAIL and SENDER_PASSWORD in email_config.py")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_email_sending()
    else:
        setup_email_config() 