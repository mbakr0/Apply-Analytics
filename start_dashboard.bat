@echo off
echo 🚀 Starting Job Application Analytics Dashboard...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 📦 Checking dependencies...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install requirements
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found
    if exist env_example.txt (
        echo Creating .env file from template...
        copy env_example.txt .env >nul
        echo ✅ Created .env file
        echo ⚠️  Please edit .env file with your credentials
    ) else (
        echo ❌ env_example.txt not found
        pause
        exit /b 1
    )
)

echo 🎉 Starting dashboard...
echo 📱 Opening http://localhost:8501 in your browser
echo ⏹️  Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
