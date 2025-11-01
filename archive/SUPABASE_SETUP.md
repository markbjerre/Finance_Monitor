# Supabase Setup Instructions

## Step 1: Create Tables in Supabase

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Copy the entire contents of `database/schema.sql`
4. Paste it into the SQL Editor
5. Click **Run** to create all tables and functions

## Step 2: Get Your Supabase Credentials

1. In your Supabase dashboard, go to **Settings** (gear icon) > **API**
2. Copy the following values:
   - **Project URL** (at the top under "Project URL")
   - **anon** / **public** key (under "Project API keys" - it might be labeled as just "anon" or "public")
   - **service_role** key (optional, for admin operations - below the anon key)
   
Note: The key you need is usually called "anon key" or "public key" - it's the first one listed under Project API keys.

https://zoxzxvyqbqfhlzayfhmc.supabase.co

## Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```powershell
   cp .env.example .env
   ```

2. Edit `.env` and add your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-public-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   ```

## Step 4: Test the Connection

Run this test script to verify the connection:

```python
from database import db

# Test health check
health = db.health_check()
print(health)

# Test inserting sample data
result = db.insert_stock_data(
    ticker='AAPL',
    price=150.25,
    change_percent=2.5,
    high=152.00,
    low=149.00,
    volume=50000000
)
print(result)

# Test retrieving data
latest = db.get_latest_stock_data('AAPL')
print(latest)
```

## Tables Created

### stocks
- Stores historical stock price data
- Fields: ticker, price, change_percent, high, low, volume, timestamp

### news
- Stores financial news articles
- Fields: title, summary, url, source, published_at, fetched_at

### ai_insights
- Stores AI-generated market insights
- Fields: content, insight_type, generated_at

## Next Steps

After setting up Supabase:
1. Install dependencies: `pip install -r requirements.txt`
2. Test the database connection
3. Start building the stock service to populate data
