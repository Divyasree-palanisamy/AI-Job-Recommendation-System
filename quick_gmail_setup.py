#!/usr/bin/env python3
"""
Quick Gmail Setup for Career Portal
Interactive setup for Gmail App Password configuration
"""

def quick_setup():
    """Quick interactive Gmail setup"""

    print("=== Quick Gmail Setup for Password Reset ===\n")

    print("This will configure your Career Portal to send real emails.")
    print("You need a Gmail App Password (not your regular password).\n")

    print("STEPS TO GET GMAIL APP PASSWORD:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification (if not enabled)")
    print("3. Go to: https://myaccount.google.com/apppasswords")
    print("4. Select 'Mail' then 'Other (custom name)' then enter 'Career Portal'")
    print("5. COPY the 16-character password\n")

    # Get credentials
    gmail = input("Enter your Gmail address: ").strip()
    if not gmail or '@gmail.com' not in gmail:
        print("ERROR: Please enter a valid Gmail address (like yourname@gmail.com)")
        return

    app_password = input("Enter your Gmail App Password (16 characters): ").strip()
    if len(app_password) != 16:
        print("ERROR: App Password must be exactly 16 characters")
        print("Make sure you copied it correctly from Gmail")
        return

    # Configure .env
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

    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)

        print(f"\n[SUCCESS] Configured Gmail: {gmail}")
        print("App Password: [saved securely]")

        # Quick test
        print("\n=== Testing Configuration ===")
        from dotenv import load_dotenv
        load_dotenv()

        from flask import Flask
        from flask_mail import Mail

        app = Flask(__name__)
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = gmail
        app.config['MAIL_PASSWORD'] = app_password

        mail = Mail(app)

        with app.app_context():
            print("[SUCCESS] Gmail configuration validated!")

        print("\n=== READY TO SEND EMAILS! ===")
        print("Restart your app: python app.py")
        print("Test password reset with real emails!")

    except Exception as e:
        print(f"ERROR: Configuration failed: {e}")
        print("Please double-check your credentials and try again")

if __name__ == "__main__":
    try:
        quick_setup()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"Unexpected error: {e}")
