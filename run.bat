@echo off
REM Server Startup Script for PDF Table Extractor

echo.
echo ====================================
echo  PDF Table Extractor - Server
echo ====================================
echo.

REM Activate virtual environment
if not exist "venv" (
    echo Error: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Activating virtual environment... OK
echo.
echo Starting FastAPI server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
cd backend
python main.py

if errorlevel 1 (
    echo.
    echo Error: Failed to start server
    echo Please check that port 8000 is not already in use
    pause
    exit /b 1
)
