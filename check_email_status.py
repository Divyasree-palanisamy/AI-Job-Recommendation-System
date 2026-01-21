#!/usr/bin/env python3
"""
Check Email Configuration Status
Shows what's configured and what needs to be fixed.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_email_status():
    """Check current email configuration status"""

    print("=== Email Configuration Status Check ===\n")

    # Check environment variables
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = os.getenv('MAIL_PORT')
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')

    print("Current Configuration:")
    print(f"- MAIL_SERVER: {mail_server or 'Not set'}")
    print(f"- MAIL_PORT: {mail_port or 'Not set'}")
    print(f"- MAIL_USERNAME: {mail_username or 'Not set'}")
    print(f"- MAIL_PASSWORD: {'Set' if mail_password else 'Not set'}")

    # Analyze configuration
    issues = []
    recommendations = []

    if not mail_server:
        issues.append("MAIL_SERVER is not configured")
        recommendations.append("Set MAIL_SERVER=smtp.gmail.com")

    if not mail_port:
        issues.append("MAIL_PORT is not configured")
        recommendations.append("Set MAIL_PORT=587")

    if not mail_username:
        issues.append("MAIL_USERNAME is not configured")
        recommendations.append("Set your Gmail address")
    elif mail_username == 'demo@example.com':
        issues.append("Using demo email address")
        recommendations.append("Replace with your real Gmail address")

    if not mail_password:
        issues.append("MAIL_PASSWORD is not configured")
        recommendations.append("Set your Gmail App Password")
    elif mail_password == 'demo_password_123':
        issues.append("Using demo password")
        recommendations.append("Replace with your real Gmail App Password")

    print(f"\nStatus: {'CONFIGURED' if not issues else 'NOT CONFIGURED'}")

    if issues:
        print(f"\nIssues Found ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")

        print("\nRecommendations:")
        for rec in recommendations:
            print(f"- {rec}")

        print("\nTo fix:")
        print("1. Run: python setup_email.py")
        print("2. Follow the Gmail App Password setup")
        print("3. Restart your Flask app")

    else:
        print("\n[SUCCESS] Email appears to be configured!")
        print("Try the password reset feature now.")

        # Test Flask-Mail configuration
        try:
            from flask import Flask
            from flask_mail import Mail

            app = Flask(__name__)
            app.config['MAIL_SERVER'] = mail_server
            app.config['MAIL_PORT'] = int(mail_port)
            app.config['MAIL_USE_TLS'] = True
            app.config['MAIL_USERNAME'] = mail_username
            app.config['MAIL_PASSWORD'] = mail_password

            mail = Mail(app)

            with app.app_context():
                print("[SUCCESS] Flask-Mail configured successfully!")

        except Exception as e:
            print(f"[WARNING] Flask-Mail configuration issue: {e}")

if __name__ == "__main__":
    check_email_status()
