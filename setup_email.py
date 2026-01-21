#!/usr/bin/env python3
"""
Email Setup Script for Career Portal
This script helps you configure Gmail for password reset emails.
"""

import os
import re
from pathlib import Path

def setup_email_config():
    """Interactive email setup"""
    print("=== Career Portal Email Setup ===\n")

    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        print("Found existing .env file.")
        overwrite = input("Do you want to update the email configuration? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return

    print("\n=== Gmail Setup Instructions ===")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification if not already enabled")
    print("3. Go to: https://myaccount.google.com/apppasswords")
    print("4. Select 'Mail' → 'Other (custom name)' → Enter 'Career Portal'")
    print("5. Copy the 16-character password\n")

    # Get Gmail credentials
    while True:
        gmail = input("Enter your Gmail address: ").strip()
        if re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', gmail):
            break
        print("Please enter a valid Gmail address (e.g., yourname@gmail.com)")

    while True:
        app_password = input("Enter your Gmail App Password (16 characters): ").strip().replace(' ', '')
        if len(app_password) == 16:
            break
        print("App Password should be exactly 16 characters (no spaces)")

    # Create/update .env file
    env_content = f"""# Email Configuration for Password Reset
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME={gmail}
MAIL_PASSWORD={app_password}
MAIL_DEFAULT_SENDER=noreply@careerguidance.com

# OAuth Configuration (leave as-is if not configured)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
"""

    with open('.env', 'w') as f:
        f.write(env_content)

        print("\n[SUCCESS] Email configuration saved to .env file!")
        print(f"Email: {gmail}")
        print("App Password: [configured]")

    # Test the configuration
    print("\n=== Testing Configuration ===")
    try:
        from dotenv import load_dotenv
        load_dotenv()

        from flask import Flask
        from flask_mail import Mail

        app = Flask(__name__)
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

        mail = Mail(app)

        with app.app_context():
            print("[SUCCESS] Flask-Mail configured successfully!")

        print("\n=== Setup Complete! ===")
        print("SUCCESS: Your Career Portal is now configured to send password reset emails!")
        print("\nNext steps:")
        print("1. Restart your Flask app: python app.py")
        print("2. Test password reset at: http://127.0.0.1:5007/login")
        print("3. Click 'Forgot Password?' and enter an email")
        print("4. Check your Gmail inbox (and spam folder)")

    except Exception as e:
        print(f"ERROR: Configuration test failed: {e}")
        print("Please check your credentials and try again.")

if __name__ == "__main__":
    try:
        setup_email_config()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nERROR: An error occurred: {e}")
        print("Please try again or check the manual setup instructions.")
