#!/usr/bin/env python3
"""
Smart Career Portal Setup Script
Automates the initial setup and installation process
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"[SETUP] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("[CHECK] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"[ERROR] Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("   Minimum required: Python 3.8")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("[INSTALL] Installing dependencies...")

    # Try to install from requirements.txt first
    if os.path.exists("requirements.txt"):
        success = run_command("pip install -r requirements.txt", "Installing from requirements.txt")
        if success:
            return True

    # Fallback to manual installation
    packages = [
        "flask",
        "joblib",
        "scikit-learn",
        "pandas",
        "numpy",
        "reportlab"
    ]

    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False

    return True

def setup_database():
    """Initialize and populate the database"""
    print("[DB] Setting up database...")

    if not os.path.exists("populate_data.py"):
        print("[ERROR] populate_data.py not found")
        return False

    return run_command("python populate_data.py", "Populating database with sample data")

def check_ml_models():
    """Verify ML model files exist"""
    print("[ML] Checking ML model files...")

    required_files = ["career_model.pkl", "tfidf_vectorizer.pkl"]
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"[WARNING] Missing ML model files: {', '.join(missing_files)}")
        print("   AI job recommendations will not work without these files")
        print("   You can still use the application for basic functionality")
        return True  # Don't fail setup, just warn

    print("[OK] ML model files found")
    return True

def main():
    """Main setup function"""
    print("SMART CAREER PORTAL SETUP")
    print("=" * 40)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check for required files
    if not os.path.exists("1.py"):
        print("[ERROR] Main application file '1.py' not found")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("[ERROR] Failed to install dependencies")
        sys.exit(1)

    # Check ML models
    if not check_ml_models():
        print("[ERROR] ML model files missing")
        sys.exit(1)

    # Setup database
    if not setup_database():
        print("[ERROR] Failed to setup database")
        sys.exit(1)

    print("\n" + "=" * 40)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("\nTo start the application:")
    print("   python 1.py")
    print("\nThen visit: http://127.0.0.1:5007")
    print("\nAdmin login: admin / admin1234")
    print("\nSee README.md for full documentation")
    print("=" * 40)

if __name__ == "__main__":
    main()
