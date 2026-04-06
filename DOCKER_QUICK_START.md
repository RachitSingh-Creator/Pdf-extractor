# Docker Quick Reference

## What You Need to Install

1. **Docker Desktop** - Download from https://www.docker.com/products/docker-desktop
   - Windows 10/11 Pro or Linux/Mac
   - 4GB+ RAM
   - That's it!

## How to Run (Pick One)

### **Option A: Easiest - Double Click Script**

**Windows:**
```
Double-click: docker-run.bat
```

**macOS/Linux:**
```bash
chmod +x docker-run.sh
./docker-run.sh
```

### **Option B: One Command**

```bash
docker-compose up --build
```

### **Option C: Individual Commands**

```bash
# Build image (first time only)
docker build -t pdf-extractor:latest .

# Run container
docker run -d -p 8000:8000 -v uploads:/app/uploads pdf-extractor:latest

# View logs
docker logs -f pdf-extractor
```

## Access Application

Open browser to: **http://localhost:8000**

## Stop Application

```bash
docker-compose down
```

OR

```bash
docker stop pdf-extractor
```

## Verify Docker is Running

```bash
docker ps
```

Should show `pdf-table-extractor` container

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| "Cannot connect to Docker daemon" | Start Docker Desktop app |
| "Port 8000 already in use" | Change port in `docker-compose.yml` |
| "Out of memory" | Increase Docker memory: Settings → Resources → 8GB+ |
| Takes 10+ min first time | Normal - downloading dependencies |
| PaddleOCR models downloading? | Normal - happens once on first upload |

## First Time Takes Longer

- **First build: 5-10 min** (downloads 1GB of dependencies + models)
- **Subsequent runs: 10-30 seconds** (just starts container)

## View Real-time Logs

```bash
docker logs -f pdf-extractor
```

## Open Shell Inside Container

```bash
docker exec -it pdf-extractor bash
```

## Delete Everything and Start Fresh

```bash
docker-compose down
docker rmi pdf-extractor:latest
docker system prune
docker-compose up --build
```

## Performance Issues?

If slow on large PDFs:

1. Increase Docker memory: Settings → 8GB or more
2. Check logs: `docker logs -f pdf-extractor`
3. Monitor resource usage: `docker stats`

---

**For detailed info**, see [DOCKER.md](DOCKER.md)
