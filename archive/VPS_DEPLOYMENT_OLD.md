# VPS Deployment Guide for n8n Integration

## Overview
This guide helps you deploy the Finance Dashboard with n8n AI integration on your Hostinger VPS (ai-vearkstedet.cloud).

## Prerequisites
- SSH access to your VPS
- Git installed on VPS
- Python 3.x installed
- n8n already running on VPS
- Supabase credentials

## Step 1: SSH into Your VPS

```bash
ssh your-username@ai-vearkstedet.cloud
# Or use your VPS IP address
```

## Step 2: Clone/Update Repository

### If First Time:
```bash
cd /var/www  # or your preferred directory
git clone https://github.com/markbjerre/Finance-dashboard.git
cd Finance-dashboard
```

### If Already Cloned:
```bash
cd /var/www/Finance-dashboard  # adjust path
git pull origin main
```

## Step 3: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables

```bash
# Create .env file
nano .env
```

**Add these values:**
```
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
HOST=0.0.0.0
PORT=5002

# Supabase Configuration
SUPABASE_URL=https://zoxzxvyqbqfhlzayfhmc.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# External API Keys
NEWS_API_KEY=your-newsapi-key-here
NEWS_API_SOURCE=newsapi
OPENAI_API_KEY=your-openai-api-key-here

# n8n Integration
N8N_API_KEY=your-n8n-api-key-here

# Refresh Intervals (seconds)
STOCK_REFRESH_INTERVAL=300
NEWS_REFRESH_INTERVAL=3600
AI_REFRESH_INTERVAL=86400

# Cache Settings
CACHE_TIMEOUT=300
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

## Step 5: Update Supabase Schema

```bash
# The ai_insights table needs new columns
# Go to Supabase Dashboard → SQL Editor and run:
```

```sql
-- Add new columns to ai_insights (if not already there)
ALTER TABLE ai_insights 
ADD COLUMN IF NOT EXISTS ticker VARCHAR(10) NOT NULL DEFAULT 'META',
ADD COLUMN IF NOT EXISTS sentiment VARCHAR(20),
ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_ai_insights_ticker ON ai_insights(ticker);
CREATE INDEX IF NOT EXISTS idx_ai_insights_ticker_generated ON ai_insights(ticker, generated_at DESC);
```

## Step 6: Test Flask App

```bash
# Activate venv if not already
source venv/bin/activate

# Test run
python app.py

# Press Ctrl+C to stop
```

**Test endpoints:**
```bash
# From another terminal or browser
curl http://localhost:5002/health
curl http://localhost:5002/api/analysis-data?ticker=META
```

## Step 7: Set Up Systemd Service (Production)

```bash
# Create service file
sudo nano /etc/systemd/system/finance-dashboard.service
```

**Add this configuration:**
```ini
[Unit]
Description=Finance Dashboard Flask App
After=network.target

[Service]
User=your-username
Group=www-data
WorkingDirectory=/var/www/Finance-dashboard
Environment="PATH=/var/www/Finance-dashboard/venv/bin"
ExecStart=/var/www/Finance-dashboard/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable finance-dashboard
sudo systemctl start finance-dashboard
sudo systemctl status finance-dashboard
```

## Step 8: Configure n8n Workflow

### A. Get Your VPS Internal/External URL

**If n8n and Flask are on same VPS:**
```
http://localhost:5002/api/analysis-data
```

**If accessing externally:**
```
http://ai-vearkstedet.cloud:5002/api/analysis-data
# Or with reverse proxy:
https://ai-vearkstedet.cloud/api/analysis-data
```

### B. Create n8n Workflow

Follow `N8N_WORKFLOW_SETUP.md` with these adjustments:

**Step 2: Schedule Trigger**
- Trigger Interval: **Day**
- Trigger at Hour: **9** (9 AM)
- Trigger at Minute: **0**

**Step 3: HTTP Request Node**
- URL: `http://localhost:5002/api/analysis-data`
- Method: GET
- Query Parameters:
  - ticker: `META`
  - news_limit: `5`

**Step 5: OpenAI Node**
- Credentials: Add your OpenAI API key
- Model: `gpt-4o-mini`
- Response Format: JSON Object

**Step 7: Supabase Node**
- Credentials: Add your Supabase URL and service role key
- Table: `ai_insights`
- Operation: Insert

### C. Test Workflow

1. Click "Execute Workflow" (manual test)
2. Check each node output
3. Verify in Supabase:
   ```sql
   SELECT * FROM ai_insights ORDER BY generated_at DESC LIMIT 1;
   ```

## Step 9: Set Up Nginx Reverse Proxy (Optional)

If you want to access via domain without port:

```bash
sudo nano /etc/nginx/sites-available/finance-dashboard
```

```nginx
server {
    listen 80;
    server_name finance.ai-vearkstedet.cloud;

    location / {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/finance-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 10: Verify Everything Works

### Check Flask App
```bash
curl http://localhost:5002/health
# Should return: {"status":"ok"}

curl http://localhost:5002/api/analysis-data?ticker=META
# Should return JSON with stock and news data
```

### Check n8n Workflow
1. Log into n8n
2. Open your workflow
3. Click "Execute Workflow"
4. Verify all nodes execute successfully

### Check Database
```bash
# In Supabase SQL Editor:
SELECT * FROM ai_insights ORDER BY generated_at DESC LIMIT 5;
```

### Check Dashboard
Visit: `http://ai-vearkstedet.cloud:5002`
(Or your configured domain)

## Troubleshooting

### Flask won't start
```bash
# Check logs
sudo journalctl -u finance-dashboard -f

# Check if port is in use
sudo lsof -i :5002

# Check Python environment
source venv/bin/activate
python -c "import flask; print(flask.__version__)"
```

### n8n can't reach Flask API
```bash
# Test from VPS terminal
curl http://localhost:5002/api/analysis-data

# Check firewall
sudo ufw status

# If needed, allow port
sudo ufw allow 5002
```

### OpenAI API errors
- Verify API key is correct in n8n credentials
- Check API usage limits at platform.openai.com
- Try gpt-3.5-turbo if gpt-4o-mini fails

### Supabase connection fails
- Verify SUPABASE_URL and keys in .env
- Test connection from Python:
  ```python
  python -c "from database.supabase_service import db; print('Connected!')"
  ```

## Daily Operation

### View Logs
```bash
# Flask app logs
sudo journalctl -u finance-dashboard -f

# n8n logs
# Check in n8n UI → Executions tab
```

### Manual Workflow Trigger
```bash
# In n8n UI:
# 1. Open workflow
# 2. Click "Execute Workflow"
```

### Check AI Insights
```sql
-- In Supabase SQL Editor
SELECT 
    ticker,
    sentiment,
    risk_level,
    generated_at,
    LEFT(content, 100) as preview
FROM ai_insights
ORDER BY generated_at DESC
LIMIT 10;
```

## Cost Tracking

**Monthly estimates:**
- OpenAI (1 analysis/day): ~$0.06/month
- VPS: Already paid
- n8n: Self-hosted (free)
- **Total new cost: ~$0.06/month**

## Next Steps

After successful deployment:
1. ✅ Verify n8n workflow runs daily at 9 AM
2. ✅ Check AI insights appear in database
3. ⏳ Update dashboard UI to display insights
4. ⏳ Add email alerts for high-risk assessments
5. ⏳ Implement multi-ticker analysis

## Support Files

- `N8N_WORKFLOW_SETUP.md` - Detailed n8n setup
- `N8N_QUICKSTART.md` - Quick reference
- `DEPLOYMENT.md` - General deployment guide
- `database/CLAUDE.md` - Database documentation
- `services/CLAUDE.md` - Services documentation
