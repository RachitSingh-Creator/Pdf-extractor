#!/bin/bash

# Quick Start Script for PDF Table Extractor on macOS/Linux

echo ""
echo "===================================="
echo "  PDF Table Extractor - Setup"
echo "===================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[1/4] Python version check... OK (Python $PYTHON_VERSION)"
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    echo "      Virtual environment created!"
else
    echo "[2/4] Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "[3/4] Activating virtual environment..."
source venv/bin/activate

echo ""

# Install dependencies
echo "[4/4] Installing Python dependencies..."
echo "      This may take several minutes..."
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo ""
echo "===================================="
echo "  Setup Complete!"
echo "===================================="
echo ""
echo "To start the server, run:"
echo "  ./run.sh"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:8000"
echo ""
