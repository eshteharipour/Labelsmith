# Installation & Deployment Guide

## Prerequisites

### Required
- Python 3.8 or higher
- pip (Python package manager)
- Node.js 16+ and npm (for frontend development)

### Optional
- PostgreSQL (for Shop module database features)
- Git (for version control)
- Docker (for containerized deployment)

## Installation

### Method 1: Quick Install (Recommended)

```bash
# 1. Download/clone the project
cd /path/to/project

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment template
cp .env.example .env

# 6. Start the application
python start.py
```

### Method 2: Step-by-Step Install

#### Step 1: Set Up Python Environment

```bash
# Check Python version (must be 3.8+)
python --version

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Verify activation (should show venv path)
which python
```

#### Step 2: Install Python Dependencies

```bash
# Install core dependencies
pip install fastapi uvicorn python-dotenv pandas pydantic httpx

# Or install all at once
pip install -r requirements.txt

# Optional: Install database support
pip install sqlalchemy psycopg2-binary

# Optional: Install development tools
pip install black ruff pytest pytest-asyncio
```

#### Step 3: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit configuration (optional)
nano .env  # or use your preferred editor
```

Key settings to configure:
```bash
# Server
PORT=8000
HOST=0.0.0.0

# Text Labeler
LABELER_JSONL_FILE=dataset.jsonl
LABELER_IMAGE_BASE_PATH=/path/to/images

# Database (if using Shop module)
DB_URL_CORE=postgresql://user:password@localhost/database
```

#### Step 4: Prepare Frontend

If you have the Vue.js frontend source:

```bash
cd cleaner

# Install dependencies
npm install

# Build for production
npm run build

# Return to project root
cd ..
```

The built frontend will be in `cleaner/dist/`

If you only have the pre-built frontend, ensure `cleaner/dist/` exists and contains the built files.

#### Step 5: Prepare Data

For the Text Labeler module:

```bash
# Create your JSONL dataset
echo '{"image": "path/to/image1.jpg", "text": ""}' > dataset.jsonl
echo '{"image": "path/to/image2.jpg", "text": ""}' >> dataset.jsonl

# Or use the sample
cp dataset_sample.jsonl dataset.jsonl
```

#### Step 6: Start the Application

```bash
# Using the startup script (recommended)
python start.py

# Or directly with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# With auto-reload for development
python start.py --reload
```

## Verification

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "modules": ["classifier", "matcher", "viewer", "cluster", "shop", "text_labeler"]
}
```

### 2. Access Frontend

Open your browser to:
- http://localhost:8000/ (Classifier)
- http://localhost:8000/labeler (Text Labeler)
- etc.

### 3. Check Logs

The application logs to stdout. You should see:
```
Starting Image Dataset Management System...
Available endpoints:
  - /classifier
  - /matcher
  - /viewer
  - /cluster
  - /shop
  - /labeler
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Deployment

### Development Deployment

```bash
# Run with auto-reload
python start.py --reload

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment

#### Option 1: Direct Production Run

```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Option 2: Systemd Service (Linux)

Create `/etc/systemd/system/dataset-manager.service`:

```ini
[Unit]
Description=Image Dataset Management System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/project/venv/bin"
ExecStart=/path/to/project/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable dataset-manager
sudo systemctl start dataset-manager
sudo systemctl status dataset-manager
```

#### Option 3: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./cleaner/dist:/app/cleaner/dist
    environment:
      - LABELER_JSONL_FILE=/app/data/dataset.jsonl
      - LABELER_IMAGE_BASE_PATH=/app/data/images
    restart: unless-stopped
```

Build and run:
```bash
docker-compose up -d
```

#### Option 4: Nginx Reverse Proxy

Install Nginx:
```bash
sudo apt install nginx  # Ubuntu/Debian
```

Create `/etc/nginx/sites-available/dataset-manager`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/dataset-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Security Considerations

### Production Checklist

- [ ] Change CORS settings in `main.py` to restrict origins
- [ ] Add authentication middleware
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Set up firewall rules
- [ ] Use environment variables for secrets (never commit .env)
- [ ] Limit file upload sizes
- [ ] Enable rate limiting
- [ ] Regular security updates

### Example: Restrict CORS

Edit `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specific domain
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

### Example: Add API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "your-secret-key")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Apply to routes
@router.get("/protected", dependencies=[Depends(verify_api_key)])
async def protected_route():
    return {"message": "Protected"}
```

## Monitoring

### Log Files

```bash
# Redirect to file
python start.py > app.log 2>&1

# With log rotation
python start.py 2>&1 | tee -a app.log
```

### Health Monitoring

Set up a cron job or monitoring service to check health:

```bash
# Crontab entry (check every 5 minutes)
*/5 * * * * curl -f http://localhost:8000/api/health || echo "Service down" | mail -s "Alert" admin@example.com
```

### Metrics

Consider adding:
- Prometheus metrics
- Application performance monitoring (APM)
- Error tracking (Sentry)

## Backup and Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Backup state files
tar -czf backup-$(date +%Y%m%d).tar.gz state*.json

# Backup datasets
tar -czf datasets-$(date +%Y%m%d).tar.gz *.jsonl

# Move to backup location
mv backup-*.tar.gz /path/to/backups/
```

Schedule with cron:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

### Recovery

```bash
# Extract backup
tar -xzf backup-20260213.tar.gz

# Restart service
sudo systemctl restart dataset-manager
```

## Scaling

### Vertical Scaling

Increase resources:
```bash
# More workers
gunicorn main:app --workers 8 --worker-class uvicorn.workers.UvicornWorker
```

### Horizontal Scaling

Use load balancer with multiple instances:

```nginx
# Nginx load balancer
upstream dataset_manager {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://dataset_manager;
    }
}
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill it
kill -9 <PID>

# Or use different port
python start.py --port 8080
```

**Permission denied:**
```bash
# Fix file permissions
chmod +x start.py
chmod -R 755 handlers/ utils/
```

**Module not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Frontend not loading:**
```bash
# Check if dist exists
ls cleaner/dist/

# Rebuild if needed
cd cleaner && npm run build
```

## Updating

### Update Application

```bash
# Pull latest code (if using git)
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Rebuild frontend if changed
cd cleaner && npm install && npm run build

# Restart service
sudo systemctl restart dataset-manager
```

### Database Migrations

If using database features:
```bash
# Backup first!
pg_dump database_name > backup.sql

# Run migrations (if you add them)
# alembic upgrade head
```

## Performance Tuning

### Python Optimization

```bash
# Use PyPy for better performance
pypy3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Optimization

```python
# Connection pooling
engine = create_engine(
    db_url,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

### Caching

Consider adding Redis for caching:
```bash
pip install redis aioredis
```

## Support

- Documentation: See all .md files
- Issues: Create an issue on GitHub
- Community: Join discussions

## Next Steps

1. ✅ Install and verify
2. ✅ Configure for your use case
3. ✅ Deploy to production
4. ✅ Set up monitoring
5. ✅ Configure backups
6. ✅ Add security measures
7. ✅ Scale as needed

Good luck with your deployment! 🚀
