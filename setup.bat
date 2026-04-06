@echo off
REM Quick Start Script for PDF Table Extractor on Windows

echo.
echo ====================================
echo  PDF Table Extractor - Setup
echo ====================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/4] Python version check... OK
echo.

REM Check virtual environment
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    echo       Virtual environment created!
) else (
    echo [2/4] Virtual environment already exists
)

echo.

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.

REM Install dependencies
echo [4/4] Installing Python dependencies...
echo       This may take several minutes...
pip install -q -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ====================================
echo  Setup Complete!
echo ====================================
echo.
echo To start the server, run:
echo   run.bat
echo.
echo Then open your browser to:
echo   http://localhost:8000
echo.
pause
