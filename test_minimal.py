#!/usr/bin/env python3
"""
Minimal test to check if the app can start without crashing.
"""

import sys
import os

def test_basic_imports():
    """Test if basic imports work."""
    print("Testing basic imports...")
    
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
    
    return True

def test_app_structure():
    """Test if app.py has basic structure."""
    print("\nTesting app structure...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential components
        essential_checks = [
            ('import streamlit', 'Streamlit import'),
            ('def main():', 'Main function'),
            ('if __name__ == "__main__":', 'Main execution')
        ]
        
        for check, description in essential_checks:
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
    """Run minimal tests."""
    print("🧪 Minimal App Test")
    print("=" * 40)
    
    if not test_basic_imports():
        print("\n❌ Basic imports failed")
        return False
    
    if not test_app_structure():
        print("\n❌ App structure test failed")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Basic tests passed! App should start.")
    print("\nTo run the app:")
    print("streamlit run app.py")
    
    return True

if __name__ == "__main__":
    main()

