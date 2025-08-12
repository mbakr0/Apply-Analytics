#!/usr/bin/env python3
"""
Test imports step by step to identify the issue.
"""

import sys
import traceback

def test_import(module_name, import_statement):
    """Test a specific import."""
    print(f"Testing {module_name}...")
    try:
        exec(import_statement)
        print(f"✅ {module_name} imported successfully")
        return True
    except Exception as e:
        print(f"❌ {module_name} failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Test all imports step by step."""
    print("🧪 Testing imports step by step")
    print("=" * 50)
    
    tests = [
        ("streamlit", "import streamlit as st"),
        ("pandas", "import pandas as pd"),
        ("plotly", "import plotly.express as px"),
        ("datetime", "from datetime import datetime, timedelta"),
        ("os", "import os"),
        ("json", "import json"),
        ("time", "import time"),
        ("typing", "from typing import List, Dict, Optional, Tuple"),
        ("re", "import re"),
        ("pathlib", "from pathlib import Path"),
        ("imap_tools", "from imap_tools import MailBox, AND"),
        ("BeautifulSoup", "from bs4 import BeautifulSoup"),
        ("openai", "import openai"),
        ("transformers", "from transformers import pipeline"),
        ("torch", "import torch"),
        ("dotenv", "from dotenv import load_dotenv"),
    ]
    
    failed_imports = []
    
    for module_name, import_statement in tests:
        if not test_import(module_name, import_statement):
            failed_imports.append(module_name)
        print()
    
    print("=" * 50)
    print("📊 Results:")
    
    if failed_imports:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
        print("\nThese imports are causing the app to fail.")
    else:
        print("✅ All imports successful!")
        print("\nThe issue might be in the app logic itself.")

if __name__ == "__main__":
    main()
