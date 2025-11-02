# Company Info Caching Implementation Guide

## Overview
We'll implement a smart caching system for company information to reduce API calls and improve performance. Company data (name, sector, industry, etc.) changes rarely, so we can cache it for 24+ hours.

---

## Step 1: Update Database Schema

**File:** `database/schema.sql`

**What to add:**
```sql
-- Company information table (cached from yfinance)
CREATE TABLE IF NOT EXISTS company_info (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    pe_ratio DECIMAL(10, 2),
    description TEXT,
    website VARCHAR(255),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient lookup
CREATE INDEX IF NOT EXISTS idx_company_info_last_updated ON company_info(last_updated);

-- Helper function to check if company info is stale (older than 24 hours)
CREATE OR REPLACE FUNCTION is_company_info_stale(ticker_symbol VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    last_update TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT last_updated INTO last_update
    FROM company_info
    WHERE ticker = ticker_symbol;
    
    IF last_update IS NULL THEN
        RETURN TRUE;  -- No data exists, considered stale
    END IF;
    
    RETURN (CURRENT_TIMESTAMP - last_update) > INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;
```

**Learning Points:**
- `PRIMARY KEY` on ticker ensures no duplicates
- `BIGINT` for market_cap (can be very large numbers)
- `DECIMAL(10,2)` for P/E ratio (precise decimal values)
- `TIMESTAMP WITH TIME ZONE` tracks when data was cached
- Helper function encapsulates staleness logic in database

**Your Task:**
1. Add this SQL to `database/schema.sql` at the end (before closing comments)
2. Run it in Supabase SQL Editor to create the table

---

## Step 2: Add Database Service Functions

**File:** `database/supabase_service.py`

**What to add:**

### Function 1: `insert_company_info()`
```python
def insert_company_info(ticker, company_data):
    """
    Insert or update company information in the database.
    
    Args:
        ticker (str): Stock ticker symbol
        company_data (dict): Company information with keys:
            - company_name, sector, industry, market_cap, 
            - pe_ratio, description, website
    
    Returns:
        dict: Inserted data or None if failed
    """
    # TODO: Implement this function
    # Hint: Use supabase.table('company_info').upsert()
    # upsert = update if exists, insert if not
    pass
```

### Function 2: `get_company_info()`
```python
def get_company_info(ticker):
    """
    Get company information from database.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        dict: Company info or None if not found
    """
    # TODO: Implement this function
    # Hint: Use supabase.table('company_info').select()
    pass
```

### Function 3: `is_company_info_fresh()`
```python
def is_company_info_fresh(ticker, max_age_hours=24):
    """
    Check if cached company info is still fresh.
    
    Args:
        ticker (str): Stock ticker symbol
        max_age_hours (int): Maximum age in hours (default 24)
    
    Returns:
        bool: True if fresh, False if stale or missing
    """
    # TODO: Implement this function
    # Hint: Get company_info, check last_updated timestamp
    # Compare with current time
    pass
```

**Learning Points:**
- `upsert()` = "update or insert" - smart function that updates existing or creates new
- Timestamp comparison to check freshness
- Separation of concerns: database logic separate from business logic

**Your Task:**
1. Add these three function signatures to `supabase_service.py`
2. We'll implement them together step by step

---

## Step 3: Update Stock Service

**File:** `services/stock_service.py`

**What to modify:**

### Update `get_stock_info()` function
Currently it fetches from yfinance every time. We'll add caching:

```python
def get_stock_info(ticker):
    """
    Get company information with intelligent caching.
    
    BEFORE: Always fetches from yfinance
    AFTER: 
        1. Check if we have cached data in database
        2. If cached data is fresh (<24hrs), return it
        3. If stale or missing, fetch from yfinance
        4. Save to database for next time
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        dict: Company information
    """
    # TODO: Implement caching logic
    pass
```

**Pseudocode Logic:**
```
1. Check database: is_company_info_fresh(ticker)?
2. IF fresh:
     - Get from database: get_company_info(ticker)
     - Return cached data (fast!)
3. ELSE (stale or missing):
     - Fetch from yfinance API (slow)
     - Parse the response
     - Save to database: insert_company_info(ticker, data)
     - Return fresh data
```

**Learning Points:**
- Cache-first strategy: always try cache before API
- Fallback pattern: if cache fails, fetch from source
- Write-through cache: update cache after fetching new data

**Your Task:**
1. We'll refactor the existing `get_stock_info()` function together
2. Add the caching logic step by step

---

## Step 4: Add Helper Functions

**File:** `services/stock_service.py`

### New helper: `parse_company_info_from_yfinance()`
```python
def parse_company_info_from_yfinance(ticker_obj):
    """
    Extract relevant company info from yfinance Ticker object.
    
    Args:
        ticker_obj: yfinance.Ticker object
    
    Returns:
        dict: Parsed company information
    """
    # TODO: Extract and format company data
    # Hint: ticker_obj.info contains all data as dictionary
    # Handle missing fields gracefully (some tickers lack data)
    pass
```

**Learning Points:**
- Data transformation: raw API → clean format
- Error handling: not all fields exist for all stocks
- `.get(key, default)` safely retrieves values

**Your Task:**
1. We'll implement this parser together
2. Handle edge cases (missing fields, None values)

---

## Step 5: Testing

**File:** `tests/test_company_info_cache.py` (new file)

**What to create:**
```python
"""
Tests for company info caching functionality.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_company_info_cache():
    """Test company info is cached and reused."""
    # TODO: Test the caching flow
    pass

def test_company_info_freshness():
    """Test freshness check logic."""
    # TODO: Test staleness detection
    pass

def test_company_info_fallback():
    """Test fallback to API when cache is empty."""
    # TODO: Test API fallback
    pass

if __name__ == '__main__':
    print("Running company info cache tests...")
    # Run tests
```

**Your Task:**
1. Create test file
2. We'll write tests together after implementation

---

## Implementation Order

We'll code these in order:

1. ✅ **Database Schema** (SQL in Supabase) - Foundation
2. **Database Functions** (`supabase_service.py`) - Data layer
   - Start with `insert_company_info()`
   - Then `get_company_info()`
   - Finally `is_company_info_fresh()`
3. **Parser** (`stock_service.py`) - Data transformation
4. **Caching Logic** (`stock_service.py`) - Business logic
5. **Testing** - Verification

---

## Expected Benefits

After implementation:
- ✅ **95% fewer API calls** for company info (24hr cache)
- ✅ **Faster page loads** (database lookup vs API call)
- ✅ **Better reliability** (cached data available if API down)
- ✅ **Cleaner code** (separation of concerns)

---

## Questions to Consider

1. **What if yfinance API fails?** Should we return stale cache?
2. **What if ticker doesn't exist?** How do we handle bad symbols?
3. **Should cache time be configurable?** Environment variable?

We'll address these as we code!

---

Ready to start? Let's begin with Step 1: Adding the SQL schema to your database.
