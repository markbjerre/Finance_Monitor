"""
Stock Service - Fetch and manage stock market data
Uses yfinance library to get real-time stock prices and historical data.

IMPLEMENTATION PLAN:
===================

Phase 1: Basic Stock Data Fetching
----------------------------------
[ ] Install yfinance library
[ ] Create function: get_current_price(ticker) -> Dict
    - Fetch current price, change %, high, low, volume
    - Return formatted dict
[ ] Create function: get_historical_data(ticker, period='7d') -> List[Dict]
    - Fetch historical prices for charting
    - Return list of {date, price} dicts
[ ] Add error handling for invalid tickers

Phase 2: Database Integration
------------------------------
[ ] Create function: fetch_and_cache_stock(ticker) -> Dict
    - Get stock data from yfinance
    - Save to Supabase using db.insert_stock_data()
    - Return the data
[ ] Create function: get_stock_with_cache(ticker, max_age=300) -> Dict
    - Check if cached data is fresh (< 5 minutes old)
    - If fresh: return cached data from Supabase
    - If stale: fetch new data and cache it
    - This reduces API calls and improves performance

Phase 3: Multiple Stocks & Utility Functions
---------------------------------------------
[ ] Create function: fetch_multiple_stocks(tickers: List[str]) -> Dict
    - Fetch data for multiple tickers at once
    - Return dict of {ticker: data}
[ ] Create function: get_stock_info(ticker) -> Dict
    - Get additional info: company name, sector, market cap
[ ] Add data validation and formatting helpers

Phase 4: Testing
----------------
[ ] Create test_stock_service.py
[ ] Test fetching real stock data (AAPL, MSFT, GOOGL)
[ ] Test caching mechanism
[ ] Test error handling

USAGE EXAMPLE:
==============
from services.stock_service import get_current_price, fetch_and_cache_stock

# Get current price
data = get_current_price('AAPL')
print(f"AAPL: ${data['price']} ({data['change_percent']}%)")

# Fetch and cache in database
cached_data = fetch_and_cache_stock('AAPL')

# Get with smart caching (uses cache if fresh, otherwise fetches new)
smart_data = get_stock_with_cache('AAPL', max_age=300)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

import yfinance as yf

from database import db
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============= PHASE 1: BASIC STOCK DATA FETCHING =============

def get_current_price(ticker: str) -> Dict[str, Any]:
    """
    Fetch current stock price and basic info.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        
    Returns:
        Dict with keys: ticker, price, change_percent, high, low, volume
        
    Example:
        >>> data = get_current_price('AAPL')
        >>> print(data['price'])
        150.25
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get current price and daily stats
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', current_price)
        
        # Calculate percent change
        if previous_close and previous_close > 0:
            change_percent = ((current_price - previous_close) / previous_close) * 100
        else:
            change_percent = 0.0
        
        # Get high, low, volume
        day_high = info.get('dayHigh') or info.get('regularMarketDayHigh', current_price)
        day_low = info.get('dayLow') or info.get('regularMarketDayLow', current_price)
        volume = info.get('volume') or info.get('regularMarketVolume', 0)
        
        # Format and return data
        return format_stock_data(
            ticker=ticker,
            price=current_price,
            change_percent=change_percent,
            high=day_high,
            low=day_low,
            volume=volume
        )
        
    except Exception as e:
        logger.error(f"Error fetching stock data for {ticker}: {e}")
        return {'error': f'Failed to fetch data for {ticker}', 'ticker': ticker}


def get_historical_data(ticker: str, period: str = '7d') -> List[Dict[str, Any]]:
    """
    Fetch historical stock prices for charting.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period ('1d', '5d', '1mo', '3mo', '1y')
        
    Returns:
        List of dicts with keys: date, price
        
    Example:
        >>> history = get_historical_data('AAPL', period='7d')
        >>> for point in history:
        ...     print(f"{point['date']}: ${point['price']}")
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        # Convert DataFrame to list of dicts
        history_data = []
        for date, row in hist.iterrows():
            history_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(row['Close'], 2),
                'open': round(row['Open'], 2),
                'high': round(row['High'], 2),
                'low': round(row['Low'], 2),
                'volume': int(row['Volume'])
            })
        
        logger.info(f"Fetched {len(history_data)} historical data points for {ticker}")
        return history_data
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")
        return []


# ============= PHASE 2: DATABASE INTEGRATION =============

def fetch_and_cache_stock(ticker: str) -> Dict[str, Any]:
    """
    Fetch stock data and save to database cache.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Stock data dict (same as get_current_price)
    """
    # TODO: 
    # 1. Get data using get_current_price()
    # 2. Save to database using db.insert_stock_data()
    # 3. Return the data
    pass


def get_stock_with_cache(ticker: str, max_age_seconds: int = 300) -> Optional[Dict[str, Any]]:
    """
    Get stock data with intelligent caching.
    Uses cached data if fresh, otherwise fetches new data.
    
    Args:
        ticker: Stock ticker symbol
        max_age_seconds: Maximum age of cached data in seconds (default: 5 minutes)
        
    Returns:
        Stock data dict or None if error
    """
    try:
        # Get latest cached data from database
        cached_data = db.get_stock_data(ticker)
        
        if cached_data:
            # Check if cache is fresh
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            age = (datetime.utcnow() - cached_time).total_seconds()
            
            if age < max_age_seconds:
                logger.info(f"Using cached data for {ticker} (age: {age}s)")
                return cached_data
        
        # Fetch new data and cache it
        data = get_current_price(ticker)
        if 'error' not in data:
            db.insert_stock_data(ticker, data)
        return data
        
    except Exception as e:
        logger.error(f"Error getting stock with cache for {ticker}: {e}")
        return None


# ============= PHASE 3: MULTIPLE STOCKS & UTILITIES =============

def fetch_multiple_stocks(tickers: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch data for multiple stocks at once.
    
    Args:
        tickers: List of stock ticker symbols
        
    Returns:
        Dict mapping ticker -> stock data
        
    Example:
        >>> stocks = fetch_multiple_stocks(['AAPL', 'MSFT', 'GOOGL'])
        >>> print(stocks['AAPL']['price'])
    """
    result = {}
    for ticker in tickers:
        result[ticker] = get_current_price(ticker)
    return result


def parse_company_info_from_yfinance(info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and format company information from yfinance Ticker.info dictionary.
    Maps yfinance field names to our database field names.
    
    Args:
        info: The .info dictionary from yfinance Ticker object
        
    Returns:
        Dict with keys matching our database schema:
            - company_name: str
            - sector: str
            - industry: str
            - market_cap: int
            - pe_ratio: float
            - description: str
            - website: str
    
    Example:
        >>> stock = yf.Ticker('META')
        >>> parsed = parse_company_info_from_yfinance(stock.info)
        >>> print(parsed['company_name'])
        'Meta Platforms Inc'
    
    Field Mapping (yfinance -> our database):
        - longName -> company_name
        - sector -> sector
        - industry -> industry
        - marketCap -> market_cap
        - trailingPE -> pe_ratio
        - longBusinessSummary -> description
        - website -> website
    """
    return {
        'company_name': info.get('longName', 'N/A'),
        'sector': info.get('sector', 'N/A'),
        'industry': info.get('industry', 'N/A'),
        'market_cap': int(info.get('marketCap', 0)) if info.get('marketCap') else 0,
        'pe_ratio': float(info.get('trailingPE', 0)) if info.get('trailingPE') else 0.0,
        'description': info.get('longBusinessSummary', 'N/A'),
        'website': info.get('website', 'N/A')
    }
    # 4. Make sure field types match database (str, int, float)
    pass


def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Get additional stock information with intelligent caching.
    Uses cache-first strategy to reduce API calls (24hr TTL).
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dict with company info including ticker, name, sector, industry, 
        market_cap, pe_ratio, description, website
    """
    try:
        # Step 1: Check if cached data is fresh (< 24 hours old)
        if db.is_company_info_fresh(ticker, max_age_hours=24):
            logger.info(f"Using cached company info for {ticker}")
            cached_data = db.get_company_info(ticker)
            if cached_data:
                return cached_data
        
        # Step 2: Fetch fresh data from yfinance API
        logger.info(f"Fetching fresh company info for {ticker} from yfinance")
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Step 3: Parse the data using our helper function
        parsed_data = parse_company_info_from_yfinance(info)
        
        # Step 4: Save to database for future use
        db.insert_company_info(ticker, parsed_data)
        logger.info(f"Cached company info for {ticker}")
        
        # Step 5: Return the fresh data
        return {
            'ticker': ticker.upper(),
            **parsed_data
        }
        
    except Exception as e:
        logger.error(f"Error fetching info for {ticker}: {e}")
        # Try to return stale cache as fallback
        cached_data = db.get_company_info(ticker)
        if cached_data:
            logger.info(f"Returning stale cached data for {ticker} due to API error")
            return cached_data
        return {'error': f'Failed to fetch info for {ticker}', 'ticker': ticker}


def validate_ticker(ticker: str) -> bool:
    """
    Check if a ticker symbol is valid.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('regularMarketPrice') is not None
    except Exception:
        return False


# ============= HELPER FUNCTIONS =============

def format_stock_data(ticker: str, price: float, change_percent: float,
                     high: float, low: float, volume: int) -> Dict[str, Any]:
    """Format stock data into consistent structure."""
    return {
        'ticker': ticker.upper(),
        'price': round(price, 2),
        'change_percent': round(change_percent, 2),
        'high': round(high, 2),
        'low': round(low, 2),
        'volume': volume,
        'timestamp': datetime.utcnow().isoformat()
    }
