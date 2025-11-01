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


# Create a singleton instance
db = SupabaseService()
