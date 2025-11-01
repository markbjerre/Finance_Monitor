"""
Configuration Management
Handles environment variables and application settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""
    
    # Flask Settings
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST: str = os.getenv('HOST', '127.0.0.1')
    PORT: int = int(os.getenv('PORT', '5002'))
    
    # Supabase Settings
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY: str = os.getenv('SUPABASE_KEY', '')
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv('SUPABASE_SERVICE_KEY', None)
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    NEWS_API_KEY: str = os.getenv('NEWS_API_KEY', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Data Refresh Intervals (in seconds)
    STOCK_REFRESH_INTERVAL: int = int(os.getenv('STOCK_REFRESH_INTERVAL', '300'))  # 5 minutes
    NEWS_REFRESH_INTERVAL: int = int(os.getenv('NEWS_REFRESH_INTERVAL', '3600'))   # 1 hour
    AI_REFRESH_INTERVAL: int = int(os.getenv('AI_REFRESH_INTERVAL', '86400'))      # 1 day
    
    # Stock Settings
    DEFAULT_TICKERS: list[str] = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'SPY']
    
    # Cache Settings
    CACHE_TIMEOUT: int = int(os.getenv('CACHE_TIMEOUT', '300'))  # 5 minutes
    
    @classmethod
    def validate_config(cls) -> list[str]:
        """
        Validate required configuration values.
        
        Returns:
            List of missing configuration keys.
        """
        missing = []
        
        if not cls.SUPABASE_URL:
            missing.append('SUPABASE_URL')
        if not cls.SUPABASE_KEY:
            missing.append('SUPABASE_KEY')
            
        return missing
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if all required configuration is present."""
        return len(cls.validate_config()) == 0


# Create a default config instance
config = Config()
