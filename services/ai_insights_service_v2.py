"""
AI Insights Service V2 - LLM-powered Market Analysis

Integrates with OpenAI GPT-4o Mini or Anthropic Claude for professional market insights.
Provides AI-generated buy/sell recommendations, trend analysis, and risk assessment.
"""

from typing import Dict, Any, Optional
import logging
import json
import os
from datetime import datetime, timedelta
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for LLM insights
LLM_INSIGHTS_CACHE = {}
CACHE_EXPIRY_MINUTES = int(os.getenv('LLM_CACHE_MINUTES', 5))
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai').lower()
LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT_SECONDS', 10))

# Try to import LLM clients
try:
    from openai import OpenAI, APIError as OpenAIError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI client not installed. Install with: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic client not installed. Install with: pip install anthropic")


# System prompt for financial analysis
SYSTEM_PROMPT = """You are a professional financial analyst providing concise, actionable market insights for retail investors.

Analyze the provided stock data, technical indicators, financial metrics, and recent news.

Respond ONLY with valid JSON (no markdown, no code blocks) in exactly this format:
{
  "sentiment": "bullish|bearish|neutral",
  "recommendation": "strong_buy|buy|hold|sell|strong_sell",
  "buy_sell_signal": "Brief 1-line signal (max 60 chars)",
  "trend_analysis": "1-2 sentences on trend (max 150 chars)",
  "key_drivers": ["Driver 1 (max 50 chars)", "Driver 2", "Driver 3"],
  "risk_level": "low|medium|high",
  "macro_insights": "1-2 sentences on sector context (max 150 chars)",
  "risk_factors": ["Risk 1 (max 50 chars)", "Risk 2"],
  "price_target": "Target price or range or null",
  "timeframe": "Time horizon assessment (max 50 chars)"
}

Keep responses concise, professional, and suitable for a financial dashboard.
Focus on actionable insights, not generic commentary.
Consider both technical and fundamental factors."""


def get_llm_market_insights(ticker: str = 'META', use_cache: bool = True) -> Dict[str, Any]:
    """
    Generate AI-powered market insights using LLM API.
    
    Collects stock data, technical indicators, metrics, and news,
    then sends to LLM for professional market analysis.
    
    Args:
        ticker: Stock ticker symbol (default: META)
        use_cache: Use cached insights if available (default: True)
        
    Returns:
        Dictionary with AI-generated market insights
    """
    try:
        # Check cache first
        if use_cache and ticker in LLM_INSIGHTS_CACHE:
            cached_data, cached_time = LLM_INSIGHTS_CACHE[ticker]
            age_minutes = (datetime.now() - cached_time).total_seconds() / 60
            
            if age_minutes < CACHE_EXPIRY_MINUTES:
                logger.info(f"Using cached LLM insights for {ticker} (age: {age_minutes:.0f}m)")
                return cached_data
        
        logger.info(f"Generating fresh LLM insights for {ticker}")
        
        # Collect context data
        context = _build_analysis_context(ticker)
        
        if 'error' in context:
            logger.error(f"Failed to build context: {context['error']}")
            return context
        
        # Call LLM API
        llm_response = _call_llm_api(context)
        
        if 'error' in llm_response:
            logger.error(f"LLM API error: {llm_response['error']}")
            return llm_response
        
        # Parse and format response
        insights = _parse_llm_response(llm_response, ticker)
        
        # Cache the result
        LLM_INSIGHTS_CACHE[ticker] = (insights, datetime.now())
        
        return insights
        
    except Exception as e:
        logger.error(f"Unexpected error generating LLM insights for {ticker}: {e}")
        return {
            'error': str(e),
            'ticker': ticker,
            'fallback': True
        }


def _build_analysis_context(ticker: str) -> Dict[str, Any]:
    """
    Build comprehensive analysis context from multiple data sources.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with all stock data, metrics, indicators, and news
    """
    try:
        from services.stock_service import get_current_price, get_stock_info, get_historical_data
        from services.technical_indicators import calculate_technical_summary
        from services.company_metrics import get_company_metrics
        from services.news_service import fetch_stock_specific_news
        
        # Fetch data
        stock_price = get_current_price(ticker)
        stock_info = get_stock_info(ticker)
        company_metrics = get_company_metrics(ticker)
        news_articles = fetch_stock_specific_news(ticker, limit=3)
        
        # Technical indicators
        historical_data = get_historical_data(ticker, period='3mo')
        prices = [day['price'] for day in historical_data]
        technical_summary = calculate_technical_summary(prices)
        
        # Extract key indicators
        indicators = technical_summary.get('indicators', {})
        
        # Build compact context for LLM
        context = {
            'ticker': ticker,
            'company': {
                'name': stock_info.get('company_name', ticker),
                'sector': stock_info.get('sector', 'N/A'),
                'industry': stock_info.get('industry', 'N/A'),
            },
            'current_price': {
                'price': stock_price.get('price', 0),
                'change_percent': stock_price.get('change_percent', 0),
                'high': stock_price.get('high', 0),
                'low': stock_price.get('low', 0),
                'volume': stock_price.get('volume', 0),
                'market_cap': company_metrics.get('valuation', {}).get('market_cap', 0),
            },
            'technical_indicators': {
                'rsi': indicators.get('rsi', {}).get('value'),
                'rsi_status': indicators.get('rsi', {}).get('status'),
                'macd': {
                    'value': indicators.get('macd', {}).get('value'),
                    'signal': indicators.get('macd', {}).get('signal'),
                    'status': indicators.get('macd', {}).get('status'),
                },
                'bollinger_bands': {
                    'position': indicators.get('bollinger_bands', {}).get('status'),
                },
                'moving_averages': indicators.get('moving_averages', {}).get('status'),
            },
            'financial_metrics': {
                'pe_ratio': company_metrics.get('valuation', {}).get('trailing_pe', 'N/A'),
                'profit_margin': company_metrics.get('profitability', {}).get('profit_margin', 'N/A'),
                'roe': company_metrics.get('profitability', {}).get('return_on_equity', 'N/A'),
                'debt_to_equity': company_metrics.get('financial_health', {}).get('debt_to_equity', 'N/A'),
                'free_cashflow': company_metrics.get('financial_health', {}).get('free_cashflow', 0),
            },
            'recent_news': [
                {
                    'title': article.get('title', ''),
                    'source': article.get('source', ''),
                }
                for article in news_articles[:3]
            ]
        }
        
        return context
        
    except Exception as e:
        logger.error(f"Error building analysis context for {ticker}: {e}")
        return {'error': str(e), 'ticker': ticker}


def _call_llm_api(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call LLM API (OpenAI or Claude) with analysis context.
    
    Args:
        context: Analysis context dictionary
        
    Returns:
        Dictionary with LLM response or error
    """
    try:
        # Determine provider and call appropriate API
        if LLM_PROVIDER == 'anthropic':
            if not ANTHROPIC_AVAILABLE:
                return {'error': 'Anthropic client not available. Install: pip install anthropic'}
            return _call_anthropic_api(context)
        else:  # Default to OpenAI
            if not OPENAI_AVAILABLE:
                return {'error': 'OpenAI client not available. Install: pip install openai'}
            return _call_openai_api(context)
    
    except Exception as e:
        logger.error(f"LLM API call failed: {e}")
        return {'error': str(e)}


def _call_openai_api(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call OpenAI GPT-4o Mini API.
    
    Args:
        context: Analysis context dictionary
        
    Returns:
        Dictionary with response or error
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {'error': 'OPENAI_API_KEY not set in environment'}
        
        client = OpenAI(api_key=api_key)
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        user_prompt = f"""Analyze this stock and provide concise market insights:

{json.dumps(context, indent=2)}

Respond with ONLY valid JSON, no markdown or extra text."""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.7,
            max_tokens=500,
            timeout=LLM_TIMEOUT
        )
        
        content = response.choices[0].message.content
        logger.info(f"OpenAI response received (model: {model})")
        
        return {
            'raw_response': content,
            'provider': 'openai',
            'model': model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
            }
        }
    
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return {'error': str(e), 'provider': 'openai'}


def _call_anthropic_api(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call Anthropic Claude API.
    
    Args:
        context: Analysis context dictionary
        
    Returns:
        Dictionary with response or error
    """
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return {'error': 'ANTHROPIC_API_KEY not set in environment'}
        
        client = anthropic.Anthropic(api_key=api_key)
        model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        
        user_prompt = f"""Analyze this stock and provide concise market insights:

{json.dumps(context, indent=2)}

Respond with ONLY valid JSON, no markdown or extra text."""
        
        response = client.messages.create(
            model=model,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        
        content = response.content[0].text
        logger.info(f"Claude response received (model: {model})")
        
        return {
            'raw_response': content,
            'provider': 'anthropic',
            'model': model,
            'usage': {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
            }
        }
    
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        return {'error': str(e), 'provider': 'anthropic'}


def _parse_llm_response(llm_response: Dict[str, Any], ticker: str) -> Dict[str, Any]:
    """
    Parse LLM API response and extract structured insights.
    
    Args:
        llm_response: Raw response from LLM API
        ticker: Stock ticker symbol
        
    Returns:
        Structured insights dictionary
    """
    try:
        if 'error' in llm_response:
            return llm_response
        
        raw_response = llm_response.get('raw_response', '')
        provider = llm_response.get('provider', 'unknown')
        model = llm_response.get('model', 'unknown')
        
        # Clean response (remove markdown if present)
        raw_response = raw_response.strip()
        if raw_response.startswith('```'):
            raw_response = re.sub(r'^```(?:json)?\s*', '', raw_response)
            raw_response = re.sub(r'\s*```$', '', raw_response)
        
        # Parse JSON
        insights_json = json.loads(raw_response)
        
        # Add metadata
        insights_json['ticker'] = ticker
        insights_json['generated_at'] = datetime.now().isoformat()
        insights_json['source'] = f"{provider.capitalize()} {model}"
        insights_json['provider'] = provider
        insights_json['confidence'] = 'high' if provider in ['openai', 'anthropic'] else 'medium'
        
        logger.info(f"Successfully parsed LLM response for {ticker}")
        return insights_json
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        return {
            'error': f'Failed to parse LLM response: {e}',
            'ticker': ticker,
            'raw_response': llm_response.get('raw_response', '')
        }
    except Exception as e:
        logger.error(f"Error parsing LLM response: {e}")
        return {'error': str(e), 'ticker': ticker}


def clear_cache(ticker: Optional[str] = None) -> None:
    """
    Clear LLM insights cache.
    
    Args:
        ticker: Clear specific ticker or all if None
    """
    if ticker:
        if ticker in LLM_INSIGHTS_CACHE:
            del LLM_INSIGHTS_CACHE[ticker]
            logger.info(f"Cleared cache for {ticker}")
    else:
        LLM_INSIGHTS_CACHE.clear()
        logger.info("Cleared all LLM insights cache")
