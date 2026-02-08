"""
AI Insights Service - Generate AI-powered market commentary and analysis

This service integrates with n8n for AI analysis and local fallback commentary
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json
import os

from services.api_utils import APIClient
from services.stock_service import get_stock_info, get_current_price
from services.news_service import fetch_stock_specific_news
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
N8N_WEBHOOK_URL = getattr(config, 'N8N_WEBHOOK_URL', os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678'))
USE_N8N = getattr(config, 'USE_N8N', False)  # Enable/disable n8n integration


def get_market_insights(ticker: str = 'META', use_ai: bool = False) -> Dict[str, Any]:
    """
    Get AI-powered market insights for a stock.
    
    Falls back to local commentary if n8n is unavailable or disabled.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'META')
        use_ai: Force use of n8n AI (if available)
        
    Returns:
        Dictionary with sentiment, key_factors, outlook, risk_level, and commentary
    """
    try:
        # Fetch stock data for context
        stock_info = get_stock_info(ticker)
        stock_price = get_current_price(ticker)
        news_articles = fetch_stock_specific_news(ticker, limit=3)
        
        # Build analysis context
        analysis_context = {
            'ticker': ticker,
            'company_name': stock_info.get('company_name', ticker),
            'sector': stock_info.get('sector', 'N/A'),
            'current_price': stock_price.get('price', 0),
            'change_percent': stock_price.get('change_percent', 0),
            'pe_ratio': stock_info.get('pe_ratio', 'N/A'),
            'market_cap': stock_info.get('market_cap', 0),
            'news_count': len(news_articles)
        }
        
        # Try n8n AI analysis if enabled
        if use_ai and USE_N8N:
            ai_insights = _fetch_from_n8n(ticker, stock_info, stock_price, news_articles)
            if ai_insights:
                ai_insights['context'] = analysis_context
                return ai_insights
        
        # Fall back to local commentary
        return _generate_local_insights(ticker, analysis_context, stock_price, stock_info)
        
    except Exception as e:
        logger.error(f"Error generating market insights for {ticker}: {e}")
        return _generate_default_insights(ticker)


def _fetch_from_n8n(ticker: str, stock_info: Dict, stock_price: Dict, news_articles: list) -> Optional[Dict[str, Any]]:
    """
    Send analysis request to n8n webhook for AI commentary.
    
    Args:
        ticker: Stock ticker
        stock_info: Stock information dict
        stock_price: Current price dict
        news_articles: List of recent news articles
        
    Returns:
        AI-generated insights or None if webhook unavailable
    """
    try:
        # Build news context
        news_context = "\n".join([
            f"- {article.get('title', 'N/A')}"
            for article in news_articles[:3]
        ])
        
        # Prepare payload for n8n
        payload = {
            'ticker': ticker,
            'company_name': stock_info.get('company_name', ''),
            'sector': stock_info.get('sector', ''),
            'current_price': stock_price.get('price', 0),
            'change_percent': stock_price.get('change_percent', 0),
            'pe_ratio': stock_info.get('pe_ratio', ''),
            'market_cap': stock_info.get('market_cap', 0),
            'recent_news': news_context
        }
        
        # Call n8n webhook
        client = APIClient(base_url=N8N_WEBHOOK_URL)
        response = client.post('/webhook/finance-analysis', json=payload, timeout=10)
        
        if response and isinstance(response, dict):
            logger.info(f"Received AI insights from n8n for {ticker}")
            return response
        
        logger.warning(f"Invalid response from n8n webhook: {response}")
        return None
        
    except Exception as e:
        logger.error(f"Error calling n8n webhook: {e}")
        return None


def _generate_local_insights(ticker: str, context: Dict, stock_price: Dict, stock_info: Dict) -> Dict[str, Any]:
    """
    Generate local market insights based on technical/fundamental data.
    Provides fallback commentary when n8n is unavailable.
    
    Args:
        ticker: Stock ticker
        context: Analysis context dict
        stock_price: Current price dict
        stock_info: Stock info dict
        
    Returns:
        Dictionary with sentiment, key_factors, outlook, and risk_level
    """
    try:
        change = stock_price.get('change_percent', 0)
        pe_ratio = stock_info.get('pe_ratio', 0)
        market_cap = stock_info.get('market_cap', 0)
        
        # Determine sentiment based on price action
        if change >= 2:
            sentiment = "bullish"
            commentary = f"{ticker} is showing strong upward momentum with a {change}% gain."
        elif change >= 0:
            sentiment = "bullish"
            commentary = f"{ticker} is moderately positive, up {change}% today."
        elif change >= -2:
            sentiment = "neutral"
            commentary = f"{ticker} is relatively flat, down {abs(change)}% with neutral momentum."
        else:
            sentiment = "bearish"
            commentary = f"{ticker} is under pressure, declining {abs(change)}%."
        
        # Risk assessment based on metrics
        try:
            pe_float = float(pe_ratio) if isinstance(pe_ratio, (int, float)) else float(pe_ratio) if pe_ratio != 'N/A' else 0
            if pe_float > 30:
                risk_level = "high"
                risk_note = "High P/E ratio suggests elevated valuation risk."
            elif pe_float > 15:
                risk_level = "medium"
                risk_note = "Moderate P/E ratio indicates balanced valuation."
            else:
                risk_level = "low"
                risk_note = "Low P/E ratio suggests potential value opportunity."
        except:
            risk_level = "medium"
            risk_note = "Unable to calculate P/E-based risk."
        
        # Generate outlook
        if sentiment == "bullish":
            outlook = f"7-day outlook: Continued strength expected if support holds above current levels."
        elif sentiment == "neutral":
            outlook = f"7-day outlook: Consolidation likely; watch for breakout above resistance."
        else:
            outlook = f"7-day outlook: Monitor for stabilization; potential reversal if support holds."
        
        return {
            'sentiment': sentiment,
            'key_factors': [
                f"Price action: {change}% daily change",
                f"Valuation: P/E ratio at {pe_ratio}",
                risk_note,
                f"Sector: {context.get('sector', 'N/A')}"
            ],
            'outlook': outlook,
            'risk_level': risk_level,
            'commentary': commentary,
            'generated_at': datetime.now().isoformat(),
            'source': 'local_analysis'
        }
        
    except Exception as e:
        logger.error(f"Error generating local insights: {e}")
        return _generate_default_insights(ticker)


def _generate_default_insights(ticker: str) -> Dict[str, Any]:
    """Generate default placeholder insights."""
    return {
        'sentiment': 'neutral',
        'key_factors': [
            'Unable to fetch real-time data',
            'Check API configuration',
            'Verify ticker symbol'
        ],
        'outlook': 'Awaiting data...',
        'risk_level': 'unknown',
        'commentary': f'Market insights for {ticker} are temporarily unavailable.',
        'generated_at': datetime.now().isoformat(),
        'source': 'default'
    }
