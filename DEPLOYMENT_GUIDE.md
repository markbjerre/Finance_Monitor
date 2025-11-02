# Deployment Guide for ai-vaerksted.cloud

**Purpose:** Consolidated deployment instructions for all services on ai-vaerksted.cloud  
**Target:** LLM orchestration and multi-service management  
**Last Updated:** November 2, 2025

---

## INFRASTRUCTURE

### VPS Configuration
- **Host:** 72.61.179.126 (Hostinger VPS)
- **OS:** Ubuntu 24.04.3 LTS
- **Domain:** ai-vaerksted.cloud
- **SSL:** Let's Encrypt (auto-renewing via Traefik)
- **Auth:** SSH with ed25519 key (git@github.com)

### Architecture
- Multi-service containerized deployment
- Path-based routing (single domain, multiple services)
- Traefik reverse proxy for SSL + routing
- Docker Compose orchestration
- GitHub as source of truth (SSH cloning)

---

## DIRECTORY STRUCTURE

```
/root/
└── docker-compose.yml          # Master orchestration file

/opt/ai-vaerksted/
├── .git/                       # Front-page repo
├── app/                        # Front-page Flask app
├── Dockerfile                  # Front-page container
├── requirements.txt            # Front-page dependencies
├── CLAUDE.md                   # Project documentation
├── CHILD_REPO_CONFIG.md        # Template for new services
│
├── Danish-Housing-Market-Search/   # Housing project repo
│   ├── webapp/                 # Housing Flask app (in subdirectory)
│   ├── Dockerfile
│   └── requirements.txt
│
├── Finance_Monitor/            # Finance project repo
│   ├── app.py                  # Finance Flask app (at root)
│   ├── Dockerfile
│   └── requirements.txt
│
└── Finnish-Learning/           # Finnish Learning project (future)
    ├── backend/                # Backend Flask app (in subdirectory)
    ├── Dockerfile
    └── requirements.txt
```

---

## DEPLOYED SERVICES

| Service | URL Path | Status | Container | Build Path | Port | Database |
|---------|----------|--------|-----------|------------|------|----------|
| Front-page | `/` | ✅ LIVE | ai-vaerksted-app | /opt/ai-vaerksted | 8000 | None |
| Housing | `/housing` | ✅ LIVE | ai-vaerksted-housing | Danish-Housing-Market-Search | 8000 | PostgreSQL 15 |
| Finance | `/finance-monitor` | ✅ LIVE | ai-vaerksted-finance | Finance_Monitor | 8000 | Supabase |
| Finnish | `/finnish` | ⏳ PENDING | ai-vaerksted-finnish | Finnish-Learning/backend | 8000 | OpenAI API |
| Traefik | 80/443 | ✅ LIVE | root_traefik_1 | traefik:latest | N/A | N/A |

---

## QUICK START - NEW SERVICE

### 1. Prepare Repository
```bash
# Ensure Flask app structure exists
# - app.py or app/__init__.py at root or in subdirectory
# - /health endpoint for status checks

# Create Dockerfile if missing:
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
EOF

# Ensure requirements.txt has:
# flask==2.3.3
# werkzeug==2.3.7
# gunicorn==21.2.0

# Push to GitHub with SSH
git push origin main
```

### 2. Clone to VPS
```bash
ssh root@72.61.179.126
cd /opt/ai-vaerksted
git clone git@github.com:markbjerre/Project-Name.git
```

### 3. Add to docker-compose.yml
Edit `/root/docker-compose.yml`, add:
```yaml
  ai-vaerksted-projectname:
    build: /opt/ai-vaerksted/Project-Name
    container_name: ai-vaerksted-projectname
    networks:
      - default
    environment:
      - FLASK_ENV=production
      # Add env vars here
    labels:
      - traefik.enable=true
      - 'traefik.http.routers.projectname.rule=Host(`ai-vaerksted.cloud`) && PathPrefix(`/projectname`)'
      - traefik.http.routers.projectname.entrypoints=websecure
      - traefik.http.routers.projectname.tls.certresolver=mytlschallenge
      - 'traefik.http.middlewares.projectname-strip.stripprefix.prefixes=/projectname'
      - traefik.http.routers.projectname.middlewares=projectname-strip
      - traefik.http.services.projectname.loadbalancer.server.port=8000
```

### 4. Deploy
```bash
cd /root
docker-compose up -d ai-vaerksted-projectname

# Verify
docker ps | grep ai-vaerksted-projectname
docker logs ai-vaerksted-projectname
curl https://ai-vaerksted.cloud/projectname/health
```

---

## KEY CONCEPTS

### Flask App Structure
- **At root:** `app.py` or `app/__init__.py` at `/app/` in container
- **In subdirectory:** `webapp/app.py` requires `WORKDIR /app/webapp` in Dockerfile
- **Entry point:** `CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]`

### Traefik Routing
- **User request:** `https://ai-vaerksted.cloud/finance-monitor/dashboard`
- **Router rule matches:** `PathPrefix(/finance-monitor)`
- **Middleware strips:** `/finance-monitor` prefix
- **Flask receives:** `/dashboard` (NOT the full path)
- **Flask routes:** Don't include the path prefix

### Environment Variables
**Discovery:**
```bash
grep -r "os.getenv\|os.environ" /opt/ai-vaerksted/Project-Name/ --include="*.py"
```

**Application:**
- Add to docker-compose.yml `environment` section, OR
- Use `docker run -e VAR_NAME=value` for specific deployments

### Database Patterns

**PostgreSQL (internal):**
```yaml
  project-db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=projectdb
      - POSTGRES_USER=projectuser
      - POSTGRES_PASSWORD=secure_password_2024
    volumes:
      - project_db_data:/var/lib/postgresql/data

  ai-vaerksted-projectname:
    depends_on:
      project-db:
        condition: service_healthy
    environment:
      - DB_HOST=project-db
      - DB_PORT=5432
      - DB_NAME=projectdb
      - DB_USER=projectuser
      - DB_PASSWORD=secure_password_2024
```

**Supabase (external):**
```yaml
  ai-vaerksted-projectname:
    environment:
      - SUPABASE_URL=https://your-project.supabase.co
      - SUPABASE_KEY=your_anon_key
      - SUPABASE_SERVICE_KEY=your_service_key
```

---

## COMMON ISSUES & FIXES

### "Build path does not exist"
```bash
# Check actual directory name
ls -la /opt/ai-vaerksted/
# Update docker-compose.yml build path to match exactly
```

### "ValueError: [ENV_VAR] not configured"
```bash
# Find required env vars
grep -r "os.getenv" /opt/ai-vaerksted/Project-Name/ | grep -v ".pyc"
# Add to docker-compose.yml or use docker run -e flags
```

### "Worker failed to boot" / Import errors
```bash
# Verify Flask app location matches WORKDIR
ls -la /opt/ai-vaerksted/Project-Name/
# If app in subdirectory, update Dockerfile WORKDIR and CMD
```

### "404 page not found" after deployment
```bash
# Check container is running
docker ps | grep projectname
# Check Traefik routing
docker logs root_traefik_1 | grep projectname
# Check app logs for errors
docker logs ai-vaerksted-projectname
```

### "docker-compose ContainerConfig error"
**Error:** `KeyError: 'ContainerConfig'` when running `docker-compose up -d`

**Root Cause:** docker-compose v1.29.2 bug when recreating containers. It reads old container metadata to preserve volumes/settings, but the old metadata is corrupted/incomplete (missing ContainerConfig field).

**Solution:** Use `docker run` instead (creates fresh container, doesn't read old metadata):
```bash
# Remove old container
docker rm -f ai-vaerksted-projectname

# Build image if needed
docker build -t ai-vaerksted-projectname:latest /path/to/project

# Run with docker run directly
docker run -d \
  --name ai-vaerksted-projectname \
  --network root_default \
  -e ENV_VAR=value \
  -l traefik.enable=true \
  -l 'traefik.http.routers.projectname.rule=Host(`ai-vaerksted.cloud`) && PathPrefix(`/projectname`)' \
  -l traefik.http.routers.projectname.entrypoints=websecure \
  -l traefik.http.routers.projectname.tls.certresolver=mytlschallenge \
  -l 'traefik.http.middlewares.projectname-strip.stripprefix.prefixes=/projectname' \
  -l traefik.http.routers.projectname.middlewares=projectname-strip \
  -l traefik.http.services.projectname.loadbalancer.server.port=8000 \
  ai-vaerksted-projectname:latest
```

**Why docker run works:** It bypasses old metadata entirely and creates a completely fresh container from the image.

**When this happens:** After rebuilding an image with `docker build` and trying to restart with `docker-compose up -d` on services that already have running containers.

### Flask 2.0.1 + Werkzeug compatibility
**Error:** `cannot import name 'url_quote' from 'werkzeug.urls'`
**Fix:** Update requirements.txt:
```
flask==2.3.3
werkzeug==2.3.7
```

---

## MANAGING SERVICES

### Update Code
```bash
cd /opt/ai-vaerksted/Project-Name
git pull origin main
docker build -t ai-vaerksted-projectname:latest .
docker stop ai-vaerksted-projectname
docker rm ai-vaerksted-projectname
cd /root
docker-compose up -d ai-vaerksted-projectname
```

### Update Environment Variables
```bash
nano /root/docker-compose.yml
# Edit environment section
docker stop ai-vaerksted-projectname
docker rm ai-vaerksted-projectname
docker-compose up -d ai-vaerksted-projectname
```

### View Logs
```bash
docker logs ai-vaerksted-projectname --tail 50
docker logs -f ai-vaerksted-projectname  # Follow in real-time
```

### Rollback
```bash
cd /opt/ai-vaerksted/Project-Name
git checkout <commit-hash>
docker build -t ai-vaerksted-projectname:latest .
docker stop ai-vaerksted-projectname
docker rm ai-vaerksted-projectname
cd /root
docker-compose up -d ai-vaerksted-projectname
```

---

## SERVICE-SPECIFIC NOTES

### Front-Page Service
- **Type:** Main website
- **Location:** `/opt/ai-vaerksted/app/`
- **URL:** https://ai-vaerksted.cloud/
- **Database:** None
- **Key Files:** app.py, requirements.txt, Dockerfile

### Housing Service
- **Type:** Danish real estate market search
- **Location:** `/opt/ai-vaerksted/Danish-Housing-Market-Search/`
- **URL:** https://ai-vaerksted.cloud/housing
- **App Location:** `webapp/` subdirectory (requires WORKDIR /app/webapp)
- **Database:** PostgreSQL 15 (internal, housing-db)
- **Key Files:** webapp/app.py, requirements.txt, Dockerfile

### Finance Service
- **Type:** Stock portfolio tracking with news service and n8n integration
- **Location:** `/opt/ai-vaerksted/Finance_Monitor/`
- **URL:** https://ai-vaerksted.cloud/finance-monitor
- **Status:** ✅ LIVE (updated Nov 2, 2025)
- **App Location:** Root (app.py at root)
- **Database:** Supabase (external)
- **Env Vars:** SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY (optional)
- **Key Files:** app.py, config.py, requirements.txt, Dockerfile, services/, database/, tests/
- **Latest Updates:** News service, company info caching, n8n AI integration, database schema
- **Deployment Note:** Use `docker run` for updates (docker-compose has ContainerConfig bug - see Common Issues)
- **Health Check:** `curl https://ai-vaerksted.cloud/finance-monitor/health`

### Finnish Learning Service
- **Type:** Language learning with AI
- **Location:** `/opt/ai-vaerksted/Finnish-Learning/`
- **URL:** https://ai-vaerksted.cloud/finnish
- **App Location:** `backend/` subdirectory (requires WORKDIR /app/backend)
- **Database:** OpenAI API (external)
- **Frontend:** Lovable platform (separate deployment)
- **Env Vars:** OPENAI_API_KEY
- **Key Files:** backend/app.py, cache.py, requirements.txt, Dockerfile
- **Note:** Automatic caching (20-60x speedup for cached words)

---

## DOCKER COMMANDS

### Containers
```bash
docker ps                           # List running
docker ps -a                        # List all
docker logs container-name          # View logs
docker logs -f container-name       # Follow logs
docker stop container-name          # Stop
docker rm container-name            # Remove
docker rm -f container-name         # Force remove
docker exec -it container-name bash # Shell access
```

### Images
```bash
docker images                       # List
docker build -t name:tag path      # Build
docker rmi image-name:tag          # Remove
docker image prune                 # Clean unused
```

### docker-compose
```bash
docker-compose up -d                           # Start all
docker-compose up -d service-name              # Start specific
docker-compose up -d --build service-name      # Rebuild + start
docker-compose down                            # Stop all
docker-compose config                          # Validate
docker-compose logs service-name               # View logs
```

---

## CRITICAL RULES

### ✅ DO:
1. Use SSH for GitHub on VPS: `git@github.com:user/repo.git`
2. Keep Flask 2.3.3 + Werkzeug 2.3.7 aligned
3. Include gunicorn==21.2.0 in requirements.txt
4. Set WORKDIR to match Flask app location
5. Test with curl after deployment
6. Use docker logs for debugging
7. Keep credentials in environment variables
8. Use internal Docker network for databases

### ❌ DO NOT:
1. Use HTTPS git clone (GitHub disabled password auth)
2. Mix Flask 2.0.1 with newer Werkzeug
3. Forget gunicorn in requirements.txt
4. Expose database ports externally
5. Include path prefix in Flask routes
6. Hardcode credentials in code
7. Commit .env files to git

---

## VERIFICATION CHECKLIST

Deployment is successful when:
- ✅ Container shows in `docker ps`
- ✅ Logs show "Starting gunicorn" and "Booting worker with pid: X"
- ✅ `curl https://ai-vaerksted.cloud/{path}` returns 200 OK
- ✅ `curl https://ai-vaerksted.cloud/{path}/health` returns `{"status":"ok"}`
- ✅ No errors in `docker logs container-name`
- ✅ Traefik routing working (no 404)

---

## FILE TEMPLATES

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
```

### requirements.txt
```
flask==2.3.3
werkzeug==2.3.7
gunicorn==21.2.0
flask-cors==4.0.0
```

### Flask App with /health
```python
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return "Service Home"

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=False)
```

---

## CONTACT POINTS

- **VPS:** root@72.61.179.126
- **Domain:** ai-vaerksted.cloud
- **GitHub Org:** markbjerre
- **Main Repos:**
  - Front-page: https://github.com/markbjerre/ai_vearksted-front-page
  - Housing: https://github.com/markbjerre/Danish-Housing-Market-Search
  - Finance: https://github.com/markbjerre/Finance_Monitor
  - Finnish: https://github.com/markbjerre/learning_finnish

---

*Consolidated deployment guide for automated LLM orchestration - November 2, 2025*
