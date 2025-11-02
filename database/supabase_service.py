"""
Supabase Database Service
Handles all Supabase database operations for the finance dashboard.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseService:
    """Service class for Supabase database operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not config.SUPABASE_URL or not config.SUPABASE_KEY:
            raise ValueError("Supabase credentials not configured. Check your .env file.")
        
        self.client: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    
    # ============= STOCK DATA OPERATIONS =============
    
    def insert_stock_data(self, ticker: str, price: float, change_percent: float, 
                         high: float, low: float, volume: int) -> Dict[str, Any]:
        """
        Insert stock data into the database.
        
        Args:
            ticker: Stock ticker symbol
            price: Current stock price
            change_percent: Percentage change
            high: Day's high price
            low: Day's low price
            volume: Trading volume
            
        Returns:
            Inserted data or error dict
        """
        try:
            data = {
                'ticker': ticker.upper(),
                'price': price,
                'change_percent': change_percent,
                'high': high,
                'low': low,
                'volume': volume,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('stocks').insert(data).execute()
            logger.info(f"Stock data inserted for {ticker}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Error inserting stock data: {e}")
            return {'error': str(e)}
    
    def get_latest_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent stock data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Latest stock data or None
        """
        try:
            response = self.client.table('stocks')\
                .select('*')\
                .eq('ticker', ticker.upper())\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error getting stock data: {e}")
            return None
    
    def get_stock_history(self, ticker: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get historical stock data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days of history to retrieve
            
        Returns:
            List of stock data entries
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = self.client.table('stocks')\
                .select('*')\
                .eq('ticker', ticker.upper())\
                .gte('timestamp', cutoff_date)\
                .order('timestamp', desc=False)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting stock history: {e}")
            return []
    
    # ============= NEWS OPERATIONS =============
    
    def insert_news(self, title: str, summary: str, url: str, source: str, 
                    published_at: str) -> Dict[str, Any]:
        """
        Insert news article into the database.
        
        Args:
            title: Article title
            summary: Article summary/description
            url: Article URL
            source: News source
            published_at: Publication timestamp
            
        Returns:
            Inserted data or error dict
        """
        try:
            data = {
                'title': title,
                'summary': summary,
                'url': url,
                'source': source,
                'published_at': published_at,
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('news').insert(data).execute()
            logger.info(f"News article inserted: {title[:50]}...")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Error inserting news: {e}")
            return {'error': str(e)}
    
    def get_recent_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent news articles.
        
        Args:
            limit: Number of articles to retrieve
            
        Returns:
            List of news articles
        """
        try:
            response = self.client.table('news')\
                .select('*')\
                .order('published_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error getting news: {e}")
            return []
    
    def delete_old_news(self, days: int = 7) -> int:
        """
        Delete news articles older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of deleted records
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            response = self.client.table('news')\
                .delete()\
                .lt('published_at', cutoff_date)\
                .execute()
            
            deleted_count = len(response.data) if response.data else 0
            logger.info(f"Deleted {deleted_count} old news articles")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting old news: {e}")
            return 0
    
    # ============= AI INSIGHTS OPERATIONS =============
    
    def insert_ai_insight(self, content: str, insight_type: str = 'daily') -> Dict[str, Any]:
        """
        Insert AI-generated insight into the database.
        
        Args:
            content: AI-generated commentary text
            insight_type: Type of insight (daily, weekly, etc.)
            
        Returns:
            Inserted data or error dict
        """
        try:
            data = {
                'content': content,
                'insight_type': insight_type,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('ai_insights').insert(data).execute()
            logger.info(f"AI insight inserted: {insight_type}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Error inserting AI insight: {e}")
            return {'error': str(e)}
    
    def get_latest_ai_insight(self, insight_type: str = 'daily') -> Optional[Dict[str, Any]]:
        """
        Get the most recent AI insight.
        
        Args:
            insight_type: Type of insight to retrieve
            
        Returns:
            Latest AI insight or None
        """
        try:
            response = self.client.table('ai_insights')\
                .select('*')\
                .eq('insight_type', insight_type)\
                .order('generated_at', desc=True)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error getting AI insight: {e}")
            return None
    
    # ============= UTILITY OPERATIONS =============
    
    def check_data_freshness(self, table: str, max_age_seconds: int) -> bool:
        """
        Check if data in a table is fresh enough.
        
        Args:
            table: Table name to check
            max_age_seconds: Maximum age in seconds
            
        Returns:
            True if data is fresh, False otherwise
        """
        try:
            cutoff_time = (datetime.utcnow() - timedelta(seconds=max_age_seconds)).isoformat()
            
            timestamp_field = 'timestamp' if table == 'stocks' else 'generated_at' if table == 'ai_insights' else 'fetched_at'
            
            response = self.client.table(table)\
                .select('*')\
                .gte(timestamp_field, cutoff_time)\
                .limit(1)\
                .execute()
            
            return len(response.data) > 0 if response.data else False
            
        except Exception as e:
            logger.error(f"Error checking data freshness: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the Supabase connection.
        
        Returns:
            Health status dictionary
        """
        try:
            # Try to query a table
            response = self.client.table('stocks').select('count').limit(1).execute()
            return {
                'status': 'healthy',
                'connected': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    # ============= COMPANY INFO OPERATIONS =============
    
    def insert_company_info(self, ticker: str, company_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Insert or update company information in the database.
        Uses upsert to update if exists, insert if not.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'META', 'AAPL')
            company_data: Dictionary with keys:
            - company_name: str
            - sector: str
            - industry: str
            - market_cap: int
            - pe_ratio: float
            - description: str
            - website: str
        
        Returns:
            Inserted/updated data or None if failed
        
        Example:
            company_data = {
            'company_name': 'Meta Platforms Inc',
            'sector': 'Technology',
            'industry': 'Internet Content & Information',
            'market_cap': 1200000000000,
            'pe_ratio': 25.5,
            'description': 'Social media company...',
            'website': 'https://meta.com'
            }
            db.insert_company_info('META', company_data)
        """
        try:
            data = {
            'ticker': ticker.upper(),
            **company_data,
            'last_updated': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('company_info').upsert(data).execute()
            logger.info(f"Company info upserted for {ticker}")
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error inserting company info: {e}")
            return None
    
    def get_company_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get company information from database.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Company info dictionary or None if not found
        
        Example return:
            {
            'ticker': 'META',
            'company_name': 'Meta Platforms Inc',
            'sector': 'Technology',
            'industry': 'Internet Content & Information',
            'market_cap': 1200000000000,
            'pe_ratio': 25.5,
            'description': 'Social media company...',
            'website': 'https://meta.com',
            'last_updated': '2025-11-02T10:30:00',
            'created_at': '2025-11-01T08:00:00'
            }
        """
        try:
            response = self.client.table('company_info')\
            .select('*')\
            .eq('ticker', ticker.upper())\
            .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error getting company info: {e}")
            return None
    
    def is_company_info_fresh(self, ticker: str, max_age_hours: int = 24) -> bool:
        """
        Check if cached company info is still fresh (not stale).

        Args:
            ticker: Stock ticker symbol
            max_age_hours: Maximum age in hours (default 24)

        Returns:
            True if data exists and is fresh, False if stale or missing

        Logic:
            - Get company_info for ticker
            - If not found, return False (needs fetching)
            - Compare last_updated with current time
            - If age > max_age_hours, return False (stale)
            - Otherwise return True (fresh)
        """
        try:
            company_info = self.get_company_info(ticker)
            
            if not company_info:
                return False
            
            last_updated = datetime.fromisoformat(company_info['last_updated'])
            age = datetime.utcnow() - last_updated
            max_age = timedelta(hours=max_age_hours)
            
            return age <= max_age
            
        except Exception as e:
            logger.error(f"Error checking company info freshness: {e}")
            return False
    
    # ============= AI INSIGHTS OPERATIONS =============
    
    def insert_ai_insight(self, ticker: str, content: str, sentiment: str = None, 
                         risk_level: str = None, insight_type: str = 'daily') -> Optional[Dict[str, Any]]:
        """
        Insert AI-generated insight into database.
        
        Args:
            ticker: Stock ticker symbol
            content: AI-generated analysis content
            sentiment: Overall sentiment (bullish/bearish/neutral)
            risk_level: Risk assessment (low/medium/high)
            insight_type: Type of insight (default: 'daily')
            
        Returns:
            Inserted data or None on error
        """
        try:
            data = {
                'ticker': ticker.upper(),
                'content': content,
                'sentiment': sentiment,
                'risk_level': risk_level,
                'insight_type': insight_type
            }
            
            result = self.client.table('ai_insights').insert(data).execute()
            logger.info(f"AI insight inserted for {ticker}")
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error inserting AI insight for {ticker}: {e}")
            return None
    
    def get_latest_ai_insight(self, ticker: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve most recent AI insight.
        
        Args:
            ticker: Optional stock ticker to filter by
            
        Returns:
            Latest AI insight dict or None
        """
        try:
            query = self.client.table('ai_insights').select('*').order('generated_at', desc=True)
            
            if ticker:
                query = query.eq('ticker', ticker.upper())
            
            result = query.limit(1).execute()
            
            if result.data:
                logger.info(f"Retrieved latest AI insight for {ticker if ticker else 'all'}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching AI insight: {e}")
            return None
    
    def get_ai_insights_history(self, ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get historical AI insights for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of insights to retrieve
            
        Returns:
            List of AI insight dicts
        """
        try:
            result = self.client.table('ai_insights')\
                .select('*')\
                .eq('ticker', ticker.upper())\
                .order('generated_at', desc=True)\
                .limit(limit)\
                .execute()
            
            logger.info(f"Retrieved {len(result.data)} AI insights for {ticker}")
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error fetching AI insights history for {ticker}: {e}")
            return []


# Create a singleton instance
db = SupabaseService()
