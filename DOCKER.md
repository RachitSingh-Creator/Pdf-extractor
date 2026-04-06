# Docker Setup Guide - PDF Table Extractor

This guide explains how to run the PDF Table Extractor using Docker. With Docker, you don't need to install Poppler or any other system dependencies manually.

## What Do You Need to Install?

### 1. **Docker** (Required)

Docker is a containerization platform that packages the application with all dependencies.

#### **Windows**
- Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Requires Windows 10/11 Pro, Enterprise, or Education edition
- During installation, enable WSL 2 (Windows Subsystem for Linux 2)
- Requires 4GB+ RAM allocated to Docker

#### **macOS**
- Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
- Intel or Apple Silicon (M1/M2/M3) versions available
- Requires 4GB+ RAM allocated to Docker

#### **Linux (Ubuntu/Debian)**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

### 2. **Verify Installation**

After installing Docker, verify it's working:

```bash
docker --version
docker-compose --version
```

You should see version numbers for both commands.

---

## How to Run the Application

### **Option 1: Docker Compose (Recommended - Easiest)**

Docker Compose automatically builds and runs your application with one command.

#### Step 1: Navigate to Project Directory
```bash
cd d:\Pdfconverter
```

#### Step 2: Build and Start the Container
```bash
docker-compose up --build
```

**What this does:**
- Builds the Docker image from the Dockerfile
- Starts the container with all services
- Maps port 8000 to your local machine
- Sets up volumes for persistent uploads

#### Step 3: Access the Application
Open your browser and go to:
```
http://localhost:8000
```

#### Step 4: Stop the Container
Press `Ctrl+C` in the terminal, or run:
```bash
docker-compose down
```

---

### **Option 2: Manual Docker Commands**

If you prefer more control or don't want to use Docker Compose:

#### Step 1: Build the Docker Image
```bash
docker build -t pdf-extractor:latest .
```

**What this does:**
- Creates a Docker image named `pdf-extractor` with tag `latest`
- Takes 5-10 minutes (first time includes downloading PaddleOCR models)

#### Step 2: Run the Container
```bash
docker run -d \
  --name pdf-extractor \
  -p 8000:8000 \
  -v %cd%\uploads:/app/uploads \
  pdf-extractor:latest
```

**Windows PowerShell** (use `$PWD` instead):
```powershell
docker run -d `
  --name pdf-extractor `
  -p 8000:8000 `
  -v ${PWD}\uploads:/app/uploads `
  pdf-extractor:latest
```

#### Step 3: Check if Container is Running
```bash
docker ps
```

You should see `pdf-table-extractor` in the list.

#### Step 4: View Logs
```bash
docker logs pdf-extractor
```

#### Step 5: Access the Application
Open your browser to:
```
http://localhost:8000
```

#### Step 6: Stop the Container
```bash
docker stop pdf-extractor
docker rm pdf-extractor
```

---

## Common Docker Commands

### **View Running Containers**
```bash
docker ps                 # Running containers
docker ps -a             # All containers (including stopped)
```

### **View Container Logs**
```bash
docker logs pdf-extractor      # View logs
docker logs -f pdf-extractor   # Follow logs (live output)
docker logs --tail 50 pdf-extractor  # Last 50 lines
```

### **Stop and Remove**
```bash
docker-compose down           # Stop with compose
docker stop pdf-extractor     # Stop container
docker rm pdf-extractor       # Remove container
docker rmi pdf-extractor:latest  # Remove image
```

### **Execute Commands in Container**
```bash
docker exec -it pdf-extractor bash  # Open bash shell
docker exec pdf-extractor python -c "import paddleocr; print('OK')"
```

### **View Container Details**
```bash
docker inspect pdf-extractor
docker stats pdf-extractor    # CPU, Memory usage
```

---

## Troubleshooting Docker

### **Issue: "Cannot connect to Docker daemon"**
- **Windows**: Start Docker Desktop application
- **Linux**: `sudo systemctl start docker`
- **Mac**: Start Docker Desktop application

### **Issue: "Port 8000 already in use"**

Change the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

Then access: `http://localhost:8001`

Or with manual Docker:
```bash
docker run -d -p 8001:8000 pdf-extractor:latest
```

### **Issue: "Out of memory" errors**

Increase Docker's memory allocation:
- **Windows/Mac**: Docker Desktop Settings → Resources → Memory (increase to 8GB+)
- **Linux**: Edit `/etc/docker/daemon.json`:
  ```json
  {
    "memory": 8589934592
  }
  ```

### **Issue: First run takes very long**

PaddleOCR downloads pre-trained models (~200MB) on first run. This is normal. Subsequent runs are much faster.

### **Issue: Container exits immediately**

Check the logs:
```bash
docker logs pdf-extractor
```

Common causes:
- Missing files in volume
- Port already in use
- Python dependency errors

### **Issue: Uploaded files not persisting**

Make sure the uploads volume is properly mounted. Check with:
```bash
docker inspect pdf-extractor | grep Mounts -A 10
```

---

## Performance Optimization

### **Set Memory and CPU Limits**

Edit `docker-compose.yml`:
```yaml
services:
  pdf-extractor:
    # ... other settings ...
    deploy:
      resources:
        limits:
          cpus: '2'              # Max 2 CPU cores
          memory: 4G             # Max 4GB RAM
        reservations:
          cpus: '1'              # Reserve 1 CPU core
          memory: 2G             # Reserve 2GB RAM
```

### **Use Docker Buildkit for Faster Builds**

```bash
DOCKER_BUILDKIT=1 docker build -t pdf-extractor:latest .
```

### **Pre-warm PaddleOCR Models**

Models are downloaded on first PDF upload. To pre-download:
```bash
docker exec pdf-extractor python -c \
  "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='en')"
```

---

## Docker File Structure

```
Dockerfile              # Build instructions
docker-compose.yml      # Multi-container orchestration
.dockerignore          # Files to exclude from build
```

### **Dockerfile Breakdown**
```dockerfile
FROM python:3.10-slim   # Base image: Lightweight Python 3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \      # PDF to image conversion
    libsm6 \            # OpenCV dependencies
    libxext6 \
    libxrender-dev \
    libgomp1            # OpenMP library for PaddlePaddle
    && rm -rf /var/lib/apt/lists/*  # Cleanup to reduce image size

WORKDIR /app            # Set working directory

COPY requirements.txt .  # Copy dependency list
RUN pip install --no-cache-dir -r requirements.txt  # Install Python packages

COPY . .                # Copy entire project

EXPOSE 8000             # Document port (informational)

CMD ["python", "backend/main.py"]  # Run the server
```

---

## Advanced Docker Configurations

### **Multi-stage Build (Smaller Images)**

Create advanced `Dockerfile.multi`:
```dockerfile
# Build stage
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "backend/main.py"]
```

### **Using with Nginx Reverse Proxy**

Create a more advanced `docker-compose.yml` with Nginx:
```yaml
version: '3.8'

services:
  pdf-extractor:
    build: .
    container_name: pdf-extractor
    expose:
      - "8000"
    volumes:
      - ./uploads:/app/uploads

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - pdf-extractor
```

---

## Deployment to Cloud

### **Docker Hub**

1. Create account at [docker.com](https://www.docker.com)
2. Build and push image:
```bash
docker build -t your-username/pdf-extractor:latest .
docker push your-username/pdf-extractor:latest
```

3. Pull and run anywhere:
```bash
docker pull your-username/pdf-extractor:latest
docker run -p 8000:8000 your-username/pdf-extractor:latest
```

### **Deployment Platforms**

- **Heroku**: `heroku container:push web`
- **AWS ECS**: Use Docker image with ECS task definition
- **Google Cloud Run**: `gcloud run deploy pdf-extractor --source .`
- **Azure Container Instances**: Upload to Azure Registry and deploy
- **Render**: Connect GitHub repo with Dockerfile

---

## Docker Cheat Sheet

| Command | Purpose |
|---------|---------|
| `docker-compose up --build` | Build and start containers |
| `docker-compose down` | Stop and remove containers |
| `docker build -t name:tag .` | Build image |
| `docker run -d --name app -p 8000:8000 image:tag` | Run container |
| `docker ps` | List running containers |
| `docker logs container-name` | View logs |
| `docker exec -it container-name bash` | Open shell |
| `docker stop container-name` | Stop container |
| `docker rm container-name` | Remove container |
| `docker images` | List images |
| `docker rmi image:tag` | Delete image |

---

## Why Use Docker?

✅ **No System Dependencies** - No need to install Poppler separately
✅ **Consistency** - Works the same on Windows, Mac, and Linux
✅ **Isolation** - Doesn't interfere with your system Python
✅ **Easy Deployment** - One command to run anywhere
✅ **Easy Cleanup** - Just delete the container, system stays clean
✅ **Scalability** - Run multiple instances easily
✅ **Version Control** - Dockerfile defines exact environment

---

## Still Prefer Local Installation?

If you don't want Docker, follow the original README.md instructions for native installation. Docker is optional but recommended!

---

**Need Help?**

Run `docker --help` or visit [Docker Documentation](https://docs.docker.com/)
