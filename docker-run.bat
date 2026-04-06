@echo off
REM Docker Quick Start Script for PDF Table Extractor

echo.
echo ====================================
echo  PDF Table Extractor - Docker
echo ====================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed or not in PATH
    echo.
    echo Please install Docker Desktop:
    echo Windows: https://www.docker.com/products/docker-desktop
    echo.
    echo After installation, restart this script.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker Compose is not installed
    echo Please ensure Docker Desktop includes Docker Compose
    pause
    exit /b 1
)

echo [✓] Docker found: %DOCKER_VERSION%
echo.

echo Building image and starting container...
echo This may take 5-10 minutes on first run (downloading dependencies)...
echo.

docker-compose up --build

if errorlevel 1 (
    echo.
    echo Error: Failed to start Docker container
    echo Please check Docker is running and try again
    pause
    exit /b 1
)
