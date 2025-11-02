"""
News Service - Fetch and manage financial news
Fetches financial news from APIs and caches them in the database.

NEWS API OPTIONS:
=================
1. NewsAPI.org (https://newsapi.org)
   - Free tier: 100 requests/day
   - Endpoints: top-headlines, everything
   - Categories: business, technology
   
2. Alpha Vantage (https://www.alphavantage.co)
   - Free tier: 25 requests/day
   - Endpoint: NEWS_SENTIMENT
   - Stock-specific news with sentiment analysis
   
3. Finnhub (https://finnhub.io)
   - Free tier: 60 requests/minute
   - Endpoint: /news
   - Market news and company-specific news

RECOMMENDED: Start with NewsAPI.org for general financial news
Get API key from: https://newsapi.org/register

IMPLEMENTATION PLAN:
====================
Step 1: Set up API credentials in .env
Step 2: Implement fetch_financial_news() - get news from API
Step 3: Implement parse_news_articles() - format news data
Step 4: Implement cache logic - store in database with db.insert_news()
Step 5: Implement get_news_with_cache() - cache-first strategy (refresh every 1 hour)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from services.api_utils import APIClient
from database import db
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============= CONFIGURATION =============

# Add to your .env file:
# NEWS_API_KEY=your_newsapi_key_here
# NEWS_API_SOURCE=newsapi  # or 'alphavantage' or 'finnhub'

NEWS_API_KEY = config.NEWS_API_KEY if hasattr(config, 'NEWS_API_KEY') else None
NEWS_API_SOURCE = getattr(config, 'NEWS_API_SOURCE', 'newsapi')

# API Base URLs
NEWS_API_URLS = {
    'newsapi': 'https://newsapi.org/v2',
    'alphavantage': 'https://www.alphavantage.co/query',
    'finnhub': 'https://finnhub.io/api/v1'
}


# ============= MAIN FUNCTIONS =============

def fetch_financial_news(category: str = 'business', limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch financial news from API.
    
    Args:
        category: News category (e.g., 'business', 'technology')
        limit: Number of articles to fetch (default 10)
        
    Returns:
        List of AI-ready news article dictionaries with clean, structured data
        
    Example:
        >>> news = fetch_financial_news(category='business', limit=5)
        >>> for article in news:
        ...     print(article['title'])
    """
    try:
        # Check if API is configured
        if not validate_news_api_config():
            logger.error("News API not configured")
            return []
        
        # Fetch based on configured source
        if NEWS_API_SOURCE == 'newsapi':
            raw_articles = _fetch_from_newsapi(category, limit)
        elif NEWS_API_SOURCE == 'alphavantage':
            raw_articles = _fetch_from_alphavantage(limit=limit)
        elif NEWS_API_SOURCE == 'finnhub':
            raw_articles = _fetch_from_finnhub(category, limit)
        else:
            logger.error(f"Unknown news source: {NEWS_API_SOURCE}")
            return []
        
        # Parse and format articles for AI consumption
        parsed_articles = []
        for raw_article in raw_articles:
            parsed = parse_news_article(raw_article, NEWS_API_SOURCE)
            if parsed:
                parsed_articles.append(parsed)
        
        logger.info(f"Fetched {len(parsed_articles)} news articles from {NEWS_API_SOURCE}")
        return parsed_articles
        
    except Exception as e:
        logger.error(f"Error fetching financial news: {e}")
        return []


def parse_news_article(raw_article: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
    """
    Parse and format a news article from API response into AI-ready format.
    Cleans text, structures data, and prepares for AI analysis.
    
    Args:
        raw_article: Raw article data from API
        source: API source ('newsapi', 'alphavantage', 'finnhub')
        
    Returns:
        Formatted article dictionary with keys:
            - title: str (clean text)
            - summary: str (clean text, AI-ready)
            - url: str
            - source: str (news outlet name)
            - published_at: str (ISO format timestamp)
            - ai_context: str (combined title + summary for AI bot)
    """
    try:
        if source == 'newsapi':
            # NewsAPI format - handle None values
            title = (raw_article.get('title') or '').strip()
            summary = (raw_article.get('description') or '').strip()
            url = raw_article.get('url', '')
            source_name = raw_article.get('source', {}).get('name', 'Unknown')
            published_at = raw_article.get('publishedAt', datetime.utcnow().isoformat())
            
        elif source == 'alphavantage':
            # Alpha Vantage format
            title = raw_article.get('title', '').strip()
            summary = raw_article.get('summary', '').strip()
            url = raw_article.get('url', '')
            source_name = raw_article.get('source', 'Alpha Vantage')
            published_at = raw_article.get('time_published', datetime.utcnow().isoformat())
            
        elif source == 'finnhub':
            # Finnhub format
            title = raw_article.get('headline', '').strip()
            summary = raw_article.get('summary', '').strip()
            url = raw_article.get('url', '')
            source_name = raw_article.get('source', 'Finnhub')
            published_at = datetime.fromtimestamp(raw_article.get('datetime', 0)).isoformat()
            
        else:
            return None
        
        # Skip articles with missing critical fields
        if not title or not url:
            return None
        
        # Create AI-ready context (combined text for analysis)
        ai_context = f"{title}. {summary}" if summary else title
        
        return {
            'title': title,
            'summary': summary or 'No summary available',
            'url': url,
            'source': source_name,
            'published_at': published_at,
            'ai_context': ai_context  # Perfect for feeding to AI bot
        }
        
    except Exception as e:
        logger.error(f"Error parsing news article: {e}")
        return None


def get_news_with_cache(category: str = 'business', limit: int = 10, 
                       max_age_minutes: int = 60) -> List[Dict[str, Any]]:
    """
    Get financial news with intelligent caching (cache-first strategy).
    Checks database first, fetches from API only if cache is stale or empty.
    Returns AI-ready news articles.
    
    Args:
        category: News category
        limit: Number of articles to return
        max_age_minutes: Maximum age of cached news in minutes. 
                        Use 0 to always fetch fresh, -1 to use cache regardless of age
        
    Returns:
        List of AI-ready news articles (from cache or fresh from API)
    """
    try:
        # If max_age_minutes is -1, use any cached news regardless of age
        use_any_cache = max_age_minutes == -1
        force_fresh = max_age_minutes == 0
        
        # Step 1: Try to get cached news from database
        cached_news = db.get_recent_news(limit)
        
        if cached_news and len(cached_news) > 0 and not force_fresh:
            # Step 2: Check if cache is fresh
            most_recent = cached_news[0]
            fetched_at_str = most_recent.get('fetched_at', '')
            # Handle timezone-aware timestamps from Supabase
            fetched_at = datetime.fromisoformat(fetched_at_str.replace('Z', '+00:00'))
            # Make datetime timezone-aware for comparison
            now = datetime.now(fetched_at.tzinfo)
            age_minutes = (now - fetched_at).total_seconds() / 60
            
            if use_any_cache or age_minutes < max_age_minutes:
                logger.info(f"Using cached news ({len(cached_news)} articles, age: {age_minutes:.1f} min)")
                return cached_news
        
        # Step 3: Cache is stale or empty, fetch fresh news from API
        logger.info(f"Fetching fresh news from API (force_fresh={force_fresh}, cached_available={bool(cached_news)})")
        fresh_news = fetch_financial_news(category, limit)
        
        if not fresh_news:
            logger.warning(f"No fresh news fetched from API")
            if cached_news:
                logger.warning(f"Returning {len(cached_news)} cached articles as fallback")
                return cached_news
            return []
        
        # Step 4: Save fresh news to database for future use
        for article in fresh_news:
            try:
                db.insert_news(
                    title=article['title'],
                    summary=article['summary'],
                    url=article['url'],
                    source=article['source'],
                    published_at=article['published_at']
                )
            except Exception as e:
                logger.error(f"Error caching news article: {e}")
                continue
        
        logger.info(f"Fetched and cached {len(fresh_news)} fresh news articles")
        return fresh_news
        
    except Exception as e:
        logger.error(f"Error in get_news_with_cache: {e}")
        # Return cached news as fallback
        return db.get_recent_news(limit) if db.get_recent_news(limit) else []


def fetch_stock_specific_news(ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch news specific to a stock ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'META')
        limit: Number of articles to fetch
        
    Returns:
        List of news articles related to the stock
    """
    # TODO: Implement this function
    # This is useful for showing company-specific news on the dashboard
    # Use Alpha Vantage or Finnhub for ticker-specific news
    pass


# ============= HELPER FUNCTIONS (API-SPECIFIC) =============

def _fetch_from_newsapi(category: str = 'business', limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch news from NewsAPI.org.
    
    API Docs: https://newsapi.org/docs/endpoints/top-headlines
    """
    try:
        base_url = NEWS_API_URLS['newsapi']
        endpoint = f"{base_url}/top-headlines"
        
        params = {
            'category': category,
            'country': 'us',
            'pageSize': limit,
            'apiKey': NEWS_API_KEY
        }
        
        client = APIClient(base_url=base_url)
        response = client.get('/top-headlines', params=params)
        
        if response and response.get('status') == 'ok':
            articles = response.get('articles', [])
            logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            return articles
        else:
            logger.error(f"NewsAPI error: {response.get('message', 'Unknown error')}")
            return []
            
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {e}")
        return []


def _fetch_from_alphavantage(ticker: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch news from Alpha Vantage.
    
    API Docs: https://www.alphavantage.co/documentation/#news-sentiment
    """
    # TODO: Implement Alpha Vantage fetching
    # Endpoint: function=NEWS_SENTIMENT
    # Parameters:
    #   - tickers: ticker (optional, for stock-specific news)
    #   - limit: limit
    #   - apikey: NEWS_API_KEY
    pass


def _fetch_from_finnhub(category: str = 'general', limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch news from Finnhub.
    
    API Docs: https://finnhub.io/docs/api/market-news
    """
    # TODO: Implement Finnhub fetching
    # Endpoint: GET /news
    # Parameters:
    #   - category: general or forex or crypto or merger
    #   - token: NEWS_API_KEY
    pass


def validate_news_api_config() -> bool:
    """
    Validate that news API is properly configured.
    
    Returns:
        True if configured, False otherwise
    """
    if not NEWS_API_KEY:
        logger.error("NEWS_API_KEY not configured in .env file")
        return False
    
    if NEWS_API_SOURCE not in NEWS_API_URLS:
        logger.error(f"Invalid NEWS_API_SOURCE: {NEWS_API_SOURCE}")
        return False
    
    logger.info(f"News API configured: {NEWS_API_SOURCE}")
    return True


# ============= USAGE EXAMPLE =============
"""
# 1. Add to .env:
NEWS_API_KEY=your_api_key_here
NEWS_API_SOURCE=newsapi

# 2. In app.py:
from services.news_service import get_news_with_cache

@app.route('/')
def dashboard():
    # ... existing code ...
    
    # Fetch news with 1-hour cache
    news_articles = get_news_with_cache(category='business', limit=10, max_age_minutes=60)
    
    context = {
        # ... existing context ...
        'news': news_articles
    }
    return render_template('dashboard.html', **context)

# 3. In dashboard.html:
{% for article in news %}
    <div class="news-item">
        <h5>{{ article.title }}</h5>
        <p>{{ article.summary }}</p>
        <small>{{ article.source }} - {{ article.published_at }}</small>
        <a href="{{ article.url }}" target="_blank">Read more</a>
    </div>
{% endfor %}
"""
