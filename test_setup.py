#!/usr/bin/env python3
"""
Test script to verify the Job Application Analytics Dashboard setup.
Run this script to check if all dependencies are properly installed.
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    required_packages = [
        'streamlit',
        'pandas',
        'plotly',
        'imap_tools',
        'beautifulsoup4',
        'python_dotenv',
        'lxml'
    ]
    
    optional_packages = [
        'openai',
        'transformers',
        'torch',
        'sentencepiece',
        'streamlit_aggrid'
    ]
    
    print("🔍 Testing required package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    print("\n🔍 Testing optional package imports...")
    for package in optional_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package} (optional)")
        except ImportError as e:
            print(f"⚠️  {package}: {e} (optional)")
    
    return failed_imports

def test_files():
    """Test if required files exist."""
    required_files = [
        'app.py',
        'requirements.txt',
        'env_example.txt',
        'README.md'
    ]
    
    print("\n📁 Testing file structure...")
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (missing)")
            missing_files.append(file)
    
    return missing_files

def test_environment():
    """Test environment variable loading."""
    print("\n🔧 Testing environment configuration...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        # Check if .env file exists
        if Path('.env').exists():
            load_dotenv()
            print("✅ .env file found and loaded")
        else:
            print("⚠️  .env file not found (copy from env_example.txt)")
        
        # Check for required environment variables
        required_vars = [
            'GMAIL_EMAIL',
            'GMAIL_APP_PASSWORD'
        ]
        
        optional_vars = [
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if os.getenv(var):
                print(f"✅ {var} is set")
            else:
                print(f"⚠️  {var} is not set")
                missing_vars.append(var)
        
        print("\n🔧 Testing optional environment variables...")
        for var in optional_vars:
            if os.getenv(var):
                print(f"✅ {var} is set (optional)")
            else:
                print(f"⚠️  {var} is not set (optional)")
        
        return missing_vars
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return ['environment_error']

def test_app_import():
    """Test if the main app can be imported."""
    print("\n🚀 Testing app import...")
    
    try:
        # Test basic app structure without running it
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key components
        checks = [
            ('import streamlit', 'Streamlit import'),
            ('def main():', 'Main function'),
            ('EMAIL_CATEGORIES', 'Email categories'),
            ('connect_gmail', 'Gmail connection'),
            ('classify_email_ai', 'AI classification')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} (missing)")
        
        print("✅ App structure looks good")
        return []
        
    except Exception as e:
        print(f"❌ App import test failed: {e}")
        return ['app_import_error']

def main():
    """Run all tests."""
    print("🧪 Job Application Analytics Dashboard - Setup Test")
    print("=" * 60)
    
    # Run tests
    failed_imports = test_imports()
    missing_files = test_files()
    missing_vars = test_environment()
    app_errors = test_app_import()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    if not failed_imports and not missing_files and not app_errors:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo start the dashboard:")
        print("1. Copy env_example.txt to .env and configure your credentials")
        print("2. Run: streamlit run app.py")
        print("3. Open http://localhost:8501 in your browser")
    else:
        print("⚠️  Some issues found:")
        
        if failed_imports:
            print(f"❌ Missing packages: {', '.join(failed_imports)}")
            print("   Run: pip install -r requirements.txt")
        
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
            print("   Copy env_example.txt to .env and configure your credentials")
        
        if app_errors:
            print(f"❌ App errors: {', '.join(app_errors)}")
    
    print("\n📚 For detailed setup instructions, see README.md")

if __name__ == "__main__":
    main()
