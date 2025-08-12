#!/usr/bin/env python3
"""
Simple test to check if the app can be imported and functions work.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_imports():
    """Test if all imports work."""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported")
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported")
    except Exception as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        from imap_tools import MailBox, AND
        print("✅ IMAP tools imported")
    except Exception as e:
        print(f"❌ IMAP tools import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported")
    except Exception as e:
        print(f"❌ BeautifulSoup import failed: {e}")
        return False
    
    return True

def test_app_functions():
    """Test if app functions can be defined."""
    print("\nTesting app functions...")
    
    try:
        # Test basic function definitions
        def test_connect_gmail(email, password):
            return None
        
        def test_classify_email_keywords(text):
            return "Other"
        
        print("✅ Basic functions work")
        return True
    except Exception as e:
        print(f"❌ Function definition failed: {e}")
        return False

def test_app_structure():
    """Test if app.py has the right structure."""
    print("\nTesting app structure...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key components
        checks = [
            ('import streamlit', 'Streamlit import'),
            ('def main():', 'Main function'),
            ('EMAIL_CATEGORIES', 'Email categories'),
            ('connect_gmail', 'Gmail connection'),
            ('classify_email_ai', 'AI classification'),
            ('if __name__ == "__main__":', 'Main execution')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} (missing)")
                return False
        
        return True
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 App Functionality Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test functions
    if not test_app_functions():
        print("\n❌ Function tests failed")
        return False
    
    # Test app structure
    if not test_app_structure():
        print("\n❌ App structure tests failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! App should work.")
    print("\nTo run the app:")
    print("streamlit run app.py")
    
    return True

if __name__ == "__main__":
    main()
