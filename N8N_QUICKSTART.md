# n8n Integration - Quick Start Guide

## ✅ What We've Done

### 1. Created API Endpoint
**URL**: `http://127.0.0.1:5002/api/analysis-data`

**Test it:**
```powershell
curl http://127.0.0.1:5002/api/analysis-data?ticker=META
```

**Response includes:**
- Stock info (price, company name, sector, market cap)
- Recent news articles (5 articles with AI-ready context)
- Pre-built AI prompt template

### 2. Updated Database Schema
Added to `ai_insights` table:
- `ticker` - Stock symbol
- `sentiment` - bullish/bearish/neutral
- `risk_level` - low/medium/high
- Indexes for fast queries

**To apply schema changes:**
1. Go to Supabase Dashboard
2. SQL Editor
3. Run the updated `database/schema.sql` (lines 42-56)

### 3. Added Database Functions
In `database/supabase_service.py`:
- `insert_ai_insight()` - Save AI analysis to database
- `get_latest_ai_insight(ticker)` - Retrieve most recent insight
- `get_ai_insights_history(ticker, limit)` - Get historical insights

### 4. Configured n8n API Key
Added to `.env`:
```
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmMTJiNjRiOS02ZTE1LTQyNTEtYjZkZi1iNWY5ZDk4Mzc5YjMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYyMTE0NjYyfQ.AkRCnGoGM2LZyh579UYhMOWq95whurRtpx5GF8kU_aA
```

## 🚀 Next Steps

### Step 1: Update Supabase Schema
Run this SQL in your Supabase SQL Editor:
```sql
-- Add new columns to ai_insights table
ALTER TABLE ai_insights 
ADD COLUMN IF NOT EXISTS ticker VARCHAR(10) NOT NULL DEFAULT 'META',
ADD COLUMN IF NOT EXISTS sentiment VARCHAR(20),
ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_ai_insights_ticker ON ai_insights(ticker);
CREATE INDEX IF NOT EXISTS idx_ai_insights_ticker_generated ON ai_insights(ticker, generated_at DESC);
```

### Step 2: Set Up n8n Workflow
Follow the detailed guide in `N8N_WORKFLOW_SETUP.md`

**Quick Summary:**
1. **Schedule Trigger** - Run every hour
2. **HTTP Request** - Fetch data from `http://127.0.0.1:5002/api/analysis-data?ticker=META`
3. **Code Node** - Format the AI prompt with news context
4. **OpenAI Node** - Generate analysis (use gpt-4o-mini)
5. **Code Node** - Parse AI response
6. **Supabase Node** - Insert into `ai_insights` table

### Step 3: Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-proj-...
   ```
4. Add to n8n OpenAI node credentials

### Step 4: Test the Workflow
1. In n8n, click "Execute Workflow" (manual test)
2. Check each node's output
3. Verify data in Supabase:
   ```sql
   SELECT * FROM ai_insights ORDER BY generated_at DESC LIMIT 1;
   ```

### Step 5: Display AI Insights on Dashboard
(Next todo - we'll add this to the dashboard UI)

## 📊 What the AI Will Analyze

**Input Data:**
- Company info (META, sector, industry)
- Current stock price and change
- 5 recent news articles

**AI Output (JSON):**
```json
{
  "sentiment": "bullish",
  "key_factors": [
    "Strong earnings report",
    "Positive analyst coverage"
  ],
  "outlook": "Short-term momentum expected to continue",
  "risk_level": "medium"
}
```

## 💰 Cost Estimate

**OpenAI gpt-4o-mini:**
- ~$0.002 per analysis
- 24 analyses/day = ~$0.05/day
- **~$1.50/month**

**n8n Cloud:**
- Starter: $20/month (5000 executions)
- 720 executions/month for hourly schedule

## 🔧 Troubleshooting

**Flask server not running?**
```powershell
.\venv\Scripts\python.exe app.py
```

**Can't access API endpoint?**
```powershell
curl http://127.0.0.1:5002/health
```

**Supabase errors?**
- Check credentials in `.env`
- Verify table schema updated
- Check service role key permissions

## 📚 Documentation Files

- `N8N_WORKFLOW_SETUP.md` - Complete n8n workflow guide
- `database/CLAUDE.md` - Database schema documentation
- `services/CLAUDE.md` - Services documentation

## Ready to proceed?

1. Update Supabase schema (SQL above)
2. Open n8n and follow `N8N_WORKFLOW_SETUP.md`
3. Test manually in n8n
4. Let it run hourly
5. We'll add UI next!
