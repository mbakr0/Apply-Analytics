#!/usr/bin/env python3
"""
Quick Start Script for Job Application Analytics Dashboard
This script helps users set up and run the dashboard quickly.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_environment():
    """Set up environment file."""
    env_file = Path('.env')
    env_example = Path('env_example.txt')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env_example.txt not found")
        return False
    
    try:
        # Copy env_example.txt to .env
        with open(env_example, 'r') as src:
            content = src.read()
        
        with open(env_file, 'w') as dst:
            dst.write(content)
        
        print("✅ Created .env file from env_example.txt")
        print("⚠️  Please edit .env file with your credentials before running the app")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_tests():
    """Run setup tests."""
    print("🧪 Running setup tests...")
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def start_dashboard():
    """Start the Streamlit dashboard."""
    print("🚀 Starting the dashboard...")
    print("📱 The dashboard will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")

def main():
    """Main quick start function."""
    print("🚀 Job Application Analytics Dashboard - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed. Please install requirements manually:")
        print("   pip install -r requirements.txt")
        return
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return
    
    # Run tests
    if not run_tests():
        print("⚠️  Some tests failed, but you can still try to run the dashboard")
    
    print("\n" + "=" * 60)
    print("🎉 Setup complete!")
    print("=" * 60)
    
    # Ask user if they want to start the dashboard
    response = input("\nWould you like to start the dashboard now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        start_dashboard()
    else:
        print("\nTo start the dashboard later, run:")
        print("   streamlit run app.py")
        print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
