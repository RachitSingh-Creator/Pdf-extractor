#!/bin/bash

# Server Startup Script for PDF Table Extractor

echo ""
echo "===================================="
echo "  PDF Table Extractor - Server"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "Activating virtual environment... OK"
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
cd backend
python main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to start server"
    echo "Please check that port 8000 is not already in use"
    exit 1
fi
