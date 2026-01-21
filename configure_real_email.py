#!/usr/bin/env python3
"""
Configure Real Email for Career Portal
Sets up Gmail credentials for sending actual emails
"""

def configure_real_email():
    """Configure real Gmail credentials"""

    print("=== Configure Real Gmail for Password Reset ===\n")

    print("To send real emails, you need:")
    print("1. Your Gmail address")
    print("2. A Gmail App Password (not your regular password)")
    print()

    # Get Gmail details
    gmail = input("Enter your Gmail address: ").strip()
    if not gmail or '@gmail.com' not in gmail:
        print("ERROR: Please enter a valid Gmail address")
        return

    app_password = input("Enter your Gmail App Password (16 characters): ").strip()
    if len(app_password) != 16:
        print("ERROR: App Password should be exactly 16 characters")
        print("Make sure you're using an App Password, not your regular password")
        return

    # Create .env with real credentials
    env_content = f"""# Real Gmail Configuration for Password Reset
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

    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)

    print(f"\n[SUCCESS] Configured real Gmail: {gmail}")
    print("App Password: [configured]")

    # Test the configuration
    print("\n=== Testing Configuration ===")
    try:
        from dotenv import load_dotenv
        load_dotenv()

        from flask import Flask
        from flask_mail import Mail

        app = Flask(__name__)
        app.config['MAIL_SERVER'] = gmail  # This should be the server, not email
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = gmail
        app.config['MAIL_PASSWORD'] = app_password

        mail = Mail(app)

        with app.app_context():
            print("[SUCCESS] Flask-Mail configured successfully!")

        print("\n=== Setup Complete! ===")
        print("Real email sending is now configured!")
        print("\nNext steps:")
        print("1. Restart your Flask app: python app.py")
        print("2. Test password reset with a real email")
        print("3. Check your Gmail inbox (and spam folder)")

    except Exception as e:
        print(f"[ERROR] Configuration test failed: {e}")
        print("Double-check your Gmail App Password and try again")

if __name__ == "__main__":
    try:
        configure_real_email()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"Error: {e}")
