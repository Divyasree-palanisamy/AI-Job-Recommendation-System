#!/usr/bin/env python3
"""
Test Password Reset Functionality
Shows how the demo mode works with working reset links.
"""

from dotenv import load_dotenv
load_dotenv()

import app

def test_password_reset():
    """Test the password reset functionality"""
    print("=== Testing Password Reset Functionality ===\n")

    with app.app.app_context():
        from app import send_password_reset_email

        # Test email
        test_email = "test@example.com"
        test_reset_url = "http://127.0.0.1:5007/reset/test-token-123"

        print("Testing password reset email sending...")
        print(f"To: {test_email}")
        print(f"Reset URL: {test_reset_url}")
        print()

        result = send_password_reset_email(test_email, test_reset_url)

        print(f"Result: {'SUCCESS' if result else 'FAILED'}")
        print()

        if result:
            print("✅ Password reset functionality is working!")
            print("\nIn demo mode, the reset link is displayed in the console.")
            print("In production with real Gmail credentials, it would be emailed.")
            print()
            print("To test the complete flow:")
            print("1. Start the app: python app.py")
            print("2. Go to: http://127.0.0.1:5007/login")
            print("3. Click 'Forgot Password?'")
            print("4. Enter any email")
            print("5. Copy the reset link from the success message")
            print("6. Paste it in your browser to test password reset")
        else:
            print("❌ Password reset functionality has issues")
            print("Check the Flask console for error details")

if __name__ == "__main__":
    test_password_reset()
