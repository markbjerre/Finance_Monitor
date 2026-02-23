# Services Module

## Overview
Business logic layer for external API integrations and data processing. All services follow cache-first strategy to minimize API calls.

## Files

### `stock_service.py`
Stock market data via yfinance API.

**Key Functions:**
- `get_stock_info(ticker)` - Main entry point; cache-first company info retrieval
- `parse_company_info_from_yfinance(info_dict, ticker)` - Extract/format company metadata
- `get_stock_price(ticker)` - Real-time price data
- `get_stock_chart_data(ticker, period)` - Historical price chart data

**Cache Strategy:**
- Company info cached 24 hours in `company_info` table
- Uses `is_company_info_fresh()` to check cache validity
- Gracefully handles missing fields with `.get()` defaults

**API Details:**
- Library: yfinance (no API key needed)
- Rate limits: None officially, but cache reduces load
- Data source: Yahoo Finance

### `news_service.py`
Financial news from NewsAPI.org.

**Key Functions:**
- `get_news_with_cache(category, limit, max_age_minutes)` - Main entry point; cache-first news retrieval
- `fetch_financial_news(category, limit)` - Routes to appropriate API source
- `_fetch_from_newsapi(category, limit)` - NewsAPI.org integration
- `parse_news_article(raw_article, source)` - Normalize article format with AI-ready structure

**AI-Ready Data Structure:**
Each article includes `ai_context` field combining title + summary for LLM consumption:
```python
{
    'title': str,
    'summary': str,
    'url': str,
    'source': str,
    'published_at': str (ISO 8601),
    'ai_context': f"Title: {title}\nSummary: {summary}"
}
```

**Cache Strategy:**
- News cached 1 hour in `news` table
- Uses `get_cached_news()` with `max_age_minutes` parameter
- Unique URL constraint prevents duplicates

**API Details:**
- Service: NewsAPI.org
- Endpoint: `/v2/top-headlines`
- Rate limit: 100 requests/day (free tier)
- Config: `NEWS_API_KEY`, `NEWS_API_SOURCE` in `.env`
- Categories: business, technology

**Error Handling:**
- Handles null title/description: `(field or '').strip()`
- Timezone-aware datetime for cache comparison: `datetime.now(fetched_at.tzinfo)`
- Logs duplicate URL errors (expected behavior)

### `api_utils.py`
Shared utilities for API integrations.

**Key Functions:**
- `make_api_request(url, params, headers, timeout)` - Standardized HTTP requests with error handling
- `is_api_error_retryable(status_code)` - Determines if retry logic should apply

**Features:**
- Automatic retries for 5xx errors
- Request timeout handling (default 10s)
- Consistent error logging
- Returns tuple: `(data, error_message)`

## Design Patterns

**Cache-First Flow:**
```
1. Check database for fresh data
2. If fresh: return cached data
3. If stale/missing: fetch from API
4. Save to database
5. Return fresh data
```

**Error Handling:**
- All API calls wrapped in try/except
- Log errors with full context
- Return empty/None on failure (graceful degradation)
- Never crash the app due to external API issues

**Type Safety:**
- All functions have type hints
- Return types clearly defined
- Optional fields handled with `Optional[T]`

## Testing

**Stock Service:**
```powershell
.\venv\Scripts\python.exe -m pytest tests/test_company_info_cache.py -v
```
Tests: cache flow, freshness checks, multiple tickers, database storage

**News Service:**
```powershell
.\venv\Scripts\python.exe -m pytest tests/test_news_service.py -v
```
Tests: API config, fetch news, caching, article structure, database storage

## Configuration

All API credentials in `.env`:
```
NEWS_API_KEY=your_newsapi_key_here
NEWS_API_SOURCE=newsapi
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Integration

Services imported in `app.py`:
```python
from services.stock_service import get_stock_info, get_stock_chart_data
from services.news_service import get_news_with_cache
```

Used in dashboard route:
```python
stock_info = get_stock_info(ticker)
news_articles = get_news_with_cache(category='business', limit=10, max_age_minutes=60)
```
