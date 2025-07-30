#!/usr/bin/env python3
"""
Test Email Script for Quiz Master
This script tests the email sending functionality.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_email():
    """Test email sending"""
    print("🧪 Testing Quiz Master Email Sending")
    print("=" * 40)
    
    try:
        # Import email functions
        from email_config import *
        from backend.api.notification_tasks import send_email
        
        print(f"📧 Target Email: {TEST_EMAIL}")
        print(f"🔧 SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"📤 Sender Email: {SENDER_EMAIL}")
        print(f"✅ Email Sending: {'ENABLED' if ENABLE_ACTUAL_EMAIL_SENDING else 'DISABLED'}")
        
        if not ENABLE_ACTUAL_EMAIL_SENDING:
            print("\n⚠️  Email sending is disabled!")
            print("💡 Set ENABLE_ACTUAL_EMAIL_SENDING = True in email_config.py")
            return
        
        if SENDER_EMAIL == "quizmaster.app@gmail.com":
            print("\n⚠️  SENDER_EMAIL is already set to your IITM address")
            return
            
        if SENDER_PASSWORD == "your-app-password":
            print("\n⚠️  Please update SENDER_PASSWORD in email_config.py")
            return
        
        # Send test email
        subject = "Quiz Master - Email Test"
        body = f"""
        Hello from Quiz Master!
        
        This is a test email to verify that email sending is working correctly.
        
        Configuration Details:
        - SMTP Server: {SMTP_SERVER}:{SMTP_PORT}
        - Sender: {SENDER_EMAIL}
        - Recipient: {TEST_EMAIL}
        
        If you receive this email, the configuration is working properly!
        
        Best regards,
        Quiz Master Team
        """
        
        print(f"\n📤 Sending test email...")
        print(f"📝 Subject: {subject}")
        
        send_email(TEST_EMAIL, subject, body)
        
        print("✅ Test email sent successfully!")
        print(f"📬 Check your inbox: {TEST_EMAIL}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you've updated SENDER_EMAIL and SENDER_PASSWORD")
        print("2. Verify your Gmail app password is correct")
        print("3. Check that 2-factor authentication is enabled")
        print("4. Ensure the app password is for 'Mail'")

if __name__ == "__main__":
    test_email() 