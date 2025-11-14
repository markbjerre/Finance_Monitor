# Deployment Guide - Finance Dashboard

This document describes how to deploy the Finance Dashboard to ai-vaerksted.cloud using Docker and Traefik.

## Prerequisites

- VPS running Docker and Traefik reverse proxy
- GitHub repository: Finance-dashboard
- Domain: ai-vaerksted.cloud

## Deployment URL

The dashboard will be accessible at:
```
https://ai-vaerksted.cloud/finance
```

## Docker Configuration

### 1. Add Service to docker-compose.yml on VPS

Add this service definition to `/root/docker-compose.yml`:

```yaml
ai-vaerksted-finance:
  build: /opt/ai-vaerksted/Finance-Dashboard
  image: ai-vaerksted-finance:latest
  container_name: ai-vaerksted-finance
  restart: unless-stopped
  networks:
    - default
  environment:
    - FLASK_ENV=production
    - SUPABASE_URL=${FINANCE_SUPABASE_URL}
    - SUPABASE_KEY=${FINANCE_SUPABASE_KEY}
    - SUPABASE_SERVICE_KEY=${FINANCE_SUPABASE_SERVICE_KEY}
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.finance.rule=Host(`ai-vaerksted.cloud`) && PathPrefix(`/finance`)"
    - "traefik.http.routers.finance.entrypoints=websecure"
    - "traefik.http.routers.finance.tls.certresolver=myresolver"
    - "traefik.http.services.finance.loadbalancer.server.port=8000"
    - "traefik.http.middlewares.finance-stripprefix.stripprefix.prefixes=/finance"
    - "traefik.http.routers.finance.middlewares=finance-stripprefix"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### 2. Environment Variables

Add these environment variables to VPS (e.g., in `/root/.env`):

```env
FINANCE_SUPABASE_URL=https://zoxzxvyqbqfhlzayfhmc.supabase.co
FINANCE_SUPABASE_KEY=your_supabase_anon_key
FINANCE_SUPABASE_SERVICE_KEY=your_supabase_service_key
```

**Note:** Replace with your actual Supabase credentials from `.env` file.

## Deployment Steps

### Step 1: Clone/Update Repository on VPS

```bash
# First time setup
cd /opt/ai-vaerksted
git clone https://github.com/YourUsername/Finance-Dashboard.git

# Or update existing
cd /opt/ai-vaerksted/Finance-Dashboard
git pull origin main
```

### Step 2: Build Docker Image

```bash
cd /opt/ai-vaerksted/Finance-Dashboard
docker build -t ai-vaerksted-finance:latest .
```

### Step 3: Start Service

```bash
cd /root
docker-compose up -d ai-vaerksted-finance
```

### Step 4: Verify Deployment

Check that the service is running:

```bash
# Check container status
docker-compose ps ai-vaerksted-finance

# Check container logs
docker-compose logs -f ai-vaerksted-finance

# Test health endpoint locally
curl http://localhost:8000/health

# Test via Traefik (should return HTTP 200)
curl https://ai-vaerksted.cloud/finance/health

# Test full dashboard
curl https://ai-vaerksted.cloud/finance
```

## Architecture

- **Web Server**: Gunicorn with 2 workers
- **Port**: 8000 (internal container port)
- **Reverse Proxy**: Traefik handles HTTPS and routing
- **Path Prefix**: `/finance` is stripped by Traefik before reaching Flask
- **Database**: Supabase PostgreSQL (external, cloud-hosted)
- **SSL**: Automatic via Let's Encrypt (handled by Traefik)

## Flask Application Notes

- Flask routes should NOT include `/finance` prefix - Traefik strips it
- The `/health` endpoint returns `{"status": "ok"}` for monitoring
- Production mode uses `FLASK_ENV=production`
- Gunicorn runs with 2 workers for concurrent request handling

## Updating the Application

To deploy updates:

```bash
# On local machine: commit and push changes
git add .
git commit -m "Update finance dashboard"
git push origin main

# On VPS: pull changes and rebuild
cd /opt/ai-vaerksted/Finance-Dashboard
git pull origin main
docker build -t ai-vaerksted-finance:latest .
cd /root
docker-compose up -d ai-vaerksted-finance
```

## Troubleshooting

### Container won't start
Check logs: `docker-compose logs ai-vaerksted-finance`

### 502 Bad Gateway
- Verify container is running: `docker-compose ps`
- Check health endpoint: `curl http://localhost:8000/health` from VPS
- Verify Traefik labels in docker-compose.yml

### Database connection issues
- Verify environment variables are set correctly
- Check Supabase credentials in VPS `.env` file
- Test Supabase connection from container: `docker exec -it ai-vaerksted-finance python -c "from database.supabase_service import health_check; print(health_check())"`

### SSL/HTTPS issues
- Traefik handles SSL automatically
- Verify certresolver is configured in Traefik
- Check Traefik logs: `docker-compose logs traefik`

## Production Checklist

- [ ] `.env` file excluded from git (check `.gitignore`)
- [ ] Environment variables configured on VPS
- [ ] Docker image builds successfully
- [ ] `/health` endpoint returns 200 OK
- [ ] Dashboard accessible at https://ai-vaerksted.cloud/finance
- [ ] Supabase connection working in production
- [ ] Stock data displays correctly
- [ ] Chart.js rendering properly

## Technical Stack

| Component | Version |
|-----------|---------|
| Python | 3.11-slim |
| Flask | 2.3.3 |
| Werkzeug | 2.3.7 |
| Gunicorn | 21.2.0 |
| Supabase | 2.9.0 |
| yfinance | 0.2.48+ |
| Chart.js | 4.4.0 |
| Bootstrap | 5.3.0 |
