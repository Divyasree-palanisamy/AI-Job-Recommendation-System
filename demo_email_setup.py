#!/usr/bin/env python3
"""
Demo Email Setup for Career Portal
This creates a demo .env file with test credentials.
Run this to test the email functionality without real Gmail setup.
"""

import os
from pathlib import Path

def create_demo_env():
    """Create a demo .env file with test settings"""

    print("=== Career Portal - Demo Email Setup ===\n")

    print("This will create a demo .env file with test email settings.")
    print("NOTE: This uses placeholder credentials and won't send real emails.")
    print("For real email sending, run: python setup_email.py\n")

    # Check if .env already exists
    env_file = Path('.env')
    if env_file.exists():
        response = input("A .env file already exists. Overwrite? (y/N): ").lower().strip()
        if response != 'y':
            print("Demo setup cancelled.")
            return

    # Create demo .env content
    demo_env = """# Demo Email Configuration (won't send real emails)
# This is for testing the email functionality only
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=demo@example.com
MAIL_PASSWORD=demo_password_123
MAIL_DEFAULT_SENDER=demo@careerguidance.com

# OAuth Configuration (leave as-is if not configured)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
"""

    with open('.env', 'w') as f:
        f.write(demo_env)

    print("Demo .env file created successfully!")
    print("\nWhat's next:")
    print("1. The app will now show better error messages")
    print("2. For real emails, run: python setup_email.py")
    print("3. Follow the Gmail App Password setup instructions")
    print("\nDemo credentials:")
    print("- Email: demo@example.com")
    print("- Password: demo_password_123")
    print("- These won't send real emails, just test the code path")

if __name__ == "__main__":
    try:
        create_demo_env()
    except Exception as e:
        print(f"Error: {e}")
