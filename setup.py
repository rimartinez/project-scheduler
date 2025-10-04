#!/usr/bin/env python
"""
Setup script for the Employee-Client Scheduling Service
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Employee-Client Scheduling Service...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Step 1: Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Step 2: Install Node.js dependencies
    if not run_command("npm install", "Installing Node.js dependencies"):
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)
    
    # Step 3: Build CSS
    if not run_command("npm run build-css-prod", "Building Tailwind CSS"):
        print("❌ Failed to build CSS")
        sys.exit(1)
    
    # Step 4: Create database migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        print("❌ Failed to create migrations")
        sys.exit(1)
    
    # Step 5: Apply migrations
    if not run_command("python manage.py migrate", "Applying database migrations"):
        print("❌ Failed to apply migrations")
        sys.exit(1)
    
    # Step 6: Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("❌ Failed to collect static files")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Start the development server: python manage.py runserver")
    print("\nVisit http://localhost:8000 to see your application!")

if __name__ == "__main__":
    main()
