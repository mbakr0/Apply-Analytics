#!/usr/bin/env python3
"""Smoke tests for the Apply Analytics application."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_classifier():
    from app import classify_keywords

    cases = {
        "Unfortunately, we are not moving forward with your application.": "Rejected",
        "We would like to schedule an interview and discuss next steps.": "Interview",
        "Congratulations! We are pleased to offer you the position.": "Offer",
        "Thank you for applying. We received your application.": "Other",
    }

    for text, expected in cases.items():
        actual, confidence = classify_keywords(text)
        assert actual == expected, f"Expected {expected}, got {actual}"
        assert 0 <= confidence <= 1, "Confidence must be between 0 and 1"


def test_required_structure():
    with open("app.py", "r", encoding="utf-8") as file:
        content = file.read()

    required = [
        "def main()",
        "def sync_inbox",
        "def classify_keywords",
        "def classify_openai",
        "CREATE TABLE IF NOT EXISTS applications",
        "st.data_editor",
        "st.download_button",
    ]
    for item in required:
        assert item in content, f"Missing application component: {item}"


if __name__ == "__main__":
    test_classifier()
    test_required_structure()
    print("All Apply Analytics smoke tests passed.")
