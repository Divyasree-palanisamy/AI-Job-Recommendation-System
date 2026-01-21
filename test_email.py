#!/usr/bin/env python3
"""
Email Configuration Test Script
Run this to test if your email settings are working.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_config():
    """Test email configuration"""
    print("Testing Email Configuration...\n")

    # Check environment variables
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = os.getenv('MAIL_PORT')
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')

    print(f"MAIL_SERVER: {mail_server}")
    print(f"MAIL_PORT: {mail_port}")
    print(f"MAIL_USERNAME: {mail_username}")
    print(f"MAIL_PASSWORD: {'*' * len(mail_password) if mail_password else 'Not set'}")

    # Check if credentials are configured
    if not all([mail_server, mail_port, mail_username, mail_password]):
        print("\nERROR: Email configuration incomplete!")
        print("Please check your .env file and ensure all MAIL_* variables are set.")
        return False

    # Check for placeholder values
    if mail_username == 'your_email@gmail.com' or mail_password == 'your_gmail_app_password':
        print("\nERROR: Using placeholder credentials!")
        print("Please replace placeholder values with your real Gmail credentials.")
        return False

    # Check Gmail App Password format
    if len(mail_password) != 16:
        print("\nWARNING: Gmail App Password should be 16 characters.")
        print("Make sure you're using an App Password, not your regular password.")

    print("\nEmail configuration looks good!")

    # Test Flask-Mail import and basic setup
    try:
        from flask import Flask
        from flask_mail import Mail

        app = Flask(__name__)
        app.config['MAIL_SERVER'] = mail_server
        app.config['MAIL_PORT'] = int(mail_port)
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = mail_username
        app.config['MAIL_PASSWORD'] = mail_password
        app.config['MAIL_DEFAULT_SENDER'] = 'test@careerguidance.com'

        mail = Mail(app)

        with app.app_context():
            print("Flask-Mail configured successfully!")
            return True

    except Exception as e:
        print(f"\nERROR: Failed to configure Flask-Mail: {e}")
        return False

if __name__ == "__main__":
    success = test_email_config()

    if success:
        print("\nEmail configuration is ready!")
        print("You can now test password reset functionality in your app.")
    else:
        print("\nNext steps:")
        print("1. Follow the Gmail App Password setup instructions")
        print("2. Update your .env file with real credentials")
        print("3. Run this script again to verify")
        print("4. Restart your Flask app: python app.py")
