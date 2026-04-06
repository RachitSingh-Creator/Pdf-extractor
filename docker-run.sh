#!/bin/bash

# Docker Quick Start Script for PDF Table Extractor

echo ""
echo "===================================="
echo "  PDF Table Extractor - Docker"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    echo ""
    echo "Please install Docker Desktop:"
    echo "macOS: https://www.docker.com/products/docker-desktop"
    echo "Linux: https://docs.docker.com/engine/install/"
    echo ""
    echo "After installation, restart this script."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please ensure Docker Desktop includes Docker Compose"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo "[✓] Docker found: $DOCKER_VERSION"
echo ""

echo "Building image and starting container..."
echo "This may take 5-10 minutes on first run (downloading dependencies)..."
echo ""

docker-compose up --build

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to start Docker container"
    echo "Please check Docker is running and try again"
    exit 1
fi
