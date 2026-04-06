# Docker Commands & Examples

## Essential Commands

### Start Application
```bash
# Recommended: Build image and start
docker-compose up --build

# Or just start (if image already exists)
docker-compose up

# Start in background (detached mode)
docker-compose up -d
```

### Stop Application
```bash
# Stop and remove containers
docker-compose down

# Or stop just the container
docker-compose stop

# List running containers
docker ps
```

### View Logs
```bash
# Show logs
docker logs pdf-extractor

# Follow logs in real-time (Ctrl+C to exit)
docker logs -f pdf-extractor

# Last 50 lines
docker logs --tail 50 pdf-extractor

# Show timestamps
docker logs -t pdf-extractor
```

---

## Container Management

### Check Container Status
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Show container details
docker inspect pdf-extractor

# Show resource usage (CPU, Memory)
docker stats pdf-extractor
```

### Access Container Shell
```bash
# Open interactive bash shell
docker exec -it pdf-extractor bash

# Run Python command
docker exec pdf-extractor python --version

# Check if PaddleOCR is working
docker exec pdf-extractor python -c "from paddleocr import PaddleOCR; print('OK')"
```

### Remove and Cleanup
```bash
# Stop and remove everything
docker-compose down

# Remove just the container
docker rm pdf-extractor

# Remove the image
docker rmi pdf-extractor:latest

# Remove all unused images/containers
docker system prune

# Force remove (use with caution)
docker rm -f pdf-extractor
```

---

## Manual Docker Build & Run

### Build Image
```bash
# Build image with tag
docker build -t pdf-extractor:latest .

# With custom tag
docker build -t myregistry/pdf-extractor:v1.0 .

# Show build progress
docker build --progress=plain -t pdf-extractor:latest .
```

### Run Container
```bash
# Basic run
docker run -d -p 8000:8000 pdf-extractor:latest

# With volume (persist uploads)
docker run -d \
  -p 8000:8000 \
  -v /path/to/uploads:/app/uploads \
  pdf-extractor:latest

# With name
docker run -d \
  --name pdf-extractor \
  -p 8000:8000 \
  pdf-extractor:latest

# With environment variables
docker run -d \
  --name pdf-extractor \
  -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  pdf-extractor:latest

# With memory limit
docker run -d \
  --name pdf-extractor \
  -p 8000:8000 \
  -m 4g \
  pdf-extractor:latest

# With CPU limit
docker run -d \
  --name pdf-extractor \
  -p 8000:8000 \
  --cpus 2 \
  pdf-extractor:latest

# Full example (Windows PowerShell)
docker run -d `
  --name pdf-extractor `
  -p 8000:8000 `
  -v ${PWD}\uploads:/app/uploads `
  -m 4g `
  --cpus 2 `
  pdf-extractor:latest
```

---

## Port Mapping

### Use Different Port
```bash
# Access on localhost:8001 but container runs 8000
docker run -d -p 8001:8000 pdf-extractor:latest

# Listen on specific network interface
docker run -d -p 127.0.0.1:8000:8000 pdf-extractor:latest

# Random host port
docker run -d -p ::8000 pdf-extractor:latest
```

---

## Volume Mounting

### Persist Data
```bash
# Mount uploads folder (Linux/Mac)
docker run -d \
  -v /home/user/pdf-uploads:/app/uploads \
  pdf-extractor:latest

# Mount uploads folder (Windows PowerShell)
docker run -d `
  -v ${PWD}\uploads:/app/uploads `
  pdf-extractor:latest

# Read-only volume
docker run -d \
  -v /path/to/uploads:/app/uploads:ro \
  pdf-extractor:latest

# Named volume
docker volume create pdf-uploads
docker run -d \
  -v pdf-uploads:/app/uploads \
  pdf-extractor:latest
```

---

## Docker Compose Advanced

### Override Settings
```bash
# Override port
docker-compose run -p 8001:8000 pdf-extractor

# Override environment
docker-compose run -e PYTHONUNBUFFERED=1 pdf-extractor

# Use different compose file
docker-compose -f docker-compose.prod.yml up
```

### View Services
```bash
# List all services in compose file
docker-compose ps

# View service logs
docker-compose logs pdf-extractor

# View all logs
docker-compose logs
```

### Scale Services
```bash
# Run multiple instances
docker-compose up --scale pdf-extractor=3
```

---

## Network Configuration

### Connect to Host Network
```bash
# Use host network (Linux only)
docker run --network host pdf-extractor:latest
```

### Create Custom Network
```bash
# Create network
docker network create pdf-network

# Run on network
docker run -d \
  --network pdf-network \
  --name pdf-extractor \
  -p 8000:8000 \
  pdf-extractor:latest
```

---

## Performance Tuning

### Resource Limits
```bash
# Limit memory to 4GB
docker run -d -m 4g pdf-extractor:latest

# Limit CPU to 2 cores
docker run -d --cpus 2 pdf-extractor:latest

# Memory + CPU limits
docker run -d -m 4g --cpus 2 pdf-extractor:latest

# Memory swap limit
docker run -d -m 4g --memory-swap 8g pdf-extractor:latest
```

### Monitor Resources
```bash
# Watch resource usage
docker stats pdf-extractor

# View container memory usage
docker stats --no-stream pdf-extractor

# Show all stats
docker stats
```

---

## Troubleshooting Commands

### Check Container Health
```bash
# Get container ID
docker ps | grep pdf-extractor

# Inspect container
docker inspect pdf-extractor | grep -A 10 "State"

# Check process inside container
docker top pdf-extractor

# Get container IP
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pdf-extractor
```

### Test Connectivity
```bash
# Test from host to container
curl http://localhost:8000

# Test from inside container
docker exec pdf-extractor curl http://localhost:8000

# Check if port is listening
docker exec pdf-extractor netstat -tlnp | grep 8000
```

### View Image History
```bash
# Show layers
docker history pdf-extractor:latest

# Show image details
docker inspect pdf-extractor:latest
```

---

## Pushing to Registry

### Docker Hub
```bash
# Login to Docker Hub
docker login

# Tag image for Docker Hub
docker tag pdf-extractor:latest username/pdf-extractor:latest

# Push to Docker Hub
docker push username/pdf-extractor:latest

# Pull from Docker Hub
docker pull username/pdf-extractor:latest
```

### Private Registry
```bash
# Tag for private registry
docker tag pdf-extractor:latest myregistry.azurecr.io/pdf-extractor:latest

# Push to private registry
docker push myregistry.azurecr.io/pdf-extractor:latest

# Pull from private registry
docker pull myregistry.azurecr.io/pdf-extractor:latest
```

---

## Useful Aliases

Add these to your shell profile for faster commands:

```bash
# Windows PowerShell $PROFILE
Set-Alias -Name dcup -Value { docker-compose up --build }
Set-Alias -Name dcdown -Value { docker-compose down }
Set-Alias -Name dclogs -Value { docker-compose logs -f }

# macOS/Linux ~/.bash_profile or ~/.zshrc
alias dcup='docker-compose up --build'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dps='docker ps'
alias di='docker images'
```

---

## Debugging Inside Container

```bash
# Open interactive shell
docker exec -it pdf-extractor bash

# Run Python in interactive mode
docker exec -it pdf-extractor python

# Check system info
docker exec pdf-extractor uname -a

# List files in uploads
docker exec pdf-extractor ls -la /app/uploads

# Check disk usage
docker exec pdf-extractor df -h

# View installed packages
docker exec pdf-extractor pip list
```

---

## Docker Compose File Override

Create `docker-compose.override.yml` for local development:

```yaml
version: '3.8'

services:
  pdf-extractor:
    environment:
      - DEBUG=1
    ports:
      - "8001:8000"  # Different port for local dev
    volumes:
      - ./backend:/app/backend  # Hot-reload Python code
```

Then just run:
```bash
docker-compose up
```

It will automatically merge both compose files!

---

## Health Checks

Add to `docker-compose.yml`:

```yaml
services:
  pdf-extractor:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 30s
```

Check status:
```bash
docker ps
# Shows "(healthy)", "(unhealthy)", or "(starting)"
```

---

## Common Docker Commands Cheat Sheet

```bash
docker ps                      # List running containers
docker logs -f <container>     # View live logs
docker exec -it <container> bash  # Open shell
docker build -t <name> .       # Build image
docker run -d <image>          # Run container
docker stop <container>        # Stop container
docker rm <container>          # Remove container
docker rmi <image>             # Remove image
docker-compose up --build      # Start with compose
docker-compose down            # Stop with compose
```

---

**Need more help?** Run `docker --help` or `docker-compose --help`
