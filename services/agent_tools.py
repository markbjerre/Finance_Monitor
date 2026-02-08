"""
Agent Tools Registry - Available tools for AI agent to call

Defines all tools (functions) that the AI agent can use to fetch data.
Each tool is mapped to an existing service function.
"""

from typing import Dict, Any, Callable, List
import logging

from services.stock_service import get_current_price, get_stock_info, get_historical_data
from services.technical_indicators import calculate_technical_summary
from services.company_metrics import get_company_metrics, format_number
from services.news_service import fetch_stock_specific_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Tool function wrappers
def tool_get_stock_price(ticker: str) -> Dict[str, Any]:
    """Get current stock price, change %, high, low, volume"""
    try:
        data = get_current_price(ticker)
        return {
            'ticker': ticker,
            'price': data.get('price'),
            'change_percent': data.get('change_percent'),
            'high': data.get('high'),
            'low': data.get('low'),
            'volume': data.get('volume'),
        }
    except Exception as e:
        logger.error(f"Error in tool_get_stock_price: {e}")
        return {'error': str(e), 'ticker': ticker}


def tool_get_technical_indicators(ticker: str) -> Dict[str, Any]:
    """Get RSI, MACD, Bollinger Bands, Moving Averages for a stock"""
    try:
        historical_data = get_historical_data(ticker, period='3mo')
        prices = [day['price'] for day in historical_data]
        
        summary = calculate_technical_summary(prices)
        
        if 'error' in summary:
            return summary
        
        indicators = summary.get('indicators', {})
        
        return {
            'ticker': ticker,
            'overall_signal': summary.get('overall_signal'),
            'rsi': {
                'value': indicators.get('rsi', {}).get('value'),
                'status': indicators.get('rsi', {}).get('status'),
            },
            'macd': {
                'value': indicators.get('macd', {}).get('value'),
                'signal': indicators.get('macd', {}).get('signal'),
                'status': indicators.get('macd', {}).get('status'),
            },
            'bollinger_bands': {
                'status': indicators.get('bollinger_bands', {}).get('status'),
                'upper': indicators.get('bollinger_bands', {}).get('upper'),
                'middle': indicators.get('bollinger_bands', {}).get('middle'),
                'lower': indicators.get('bollinger_bands', {}).get('lower'),
            },
            'moving_averages': {
                'status': indicators.get('moving_averages', {}).get('status'),
                'sma_20': indicators.get('moving_averages', {}).get('sma_20'),
                'sma_50': indicators.get('moving_averages', {}).get('sma_50'),
            }
        }
    except Exception as e:
        logger.error(f"Error in tool_get_technical_indicators: {e}")
        return {'error': str(e), 'ticker': ticker}


def tool_get_company_metrics(ticker: str) -> Dict[str, Any]:
    """Get company financial metrics, valuation, profitability, etc."""
    try:
        metrics = get_company_metrics(ticker)
        
        if 'error' in metrics:
            return metrics
        
        return {
            'ticker': ticker,
            'company_name': metrics.get('company_name'),
            'sector': metrics.get('sector'),
            'industry': metrics.get('industry'),
            'valuation': {
                'market_cap': format_number(metrics.get('valuation', {}).get('market_cap'), 'compact'),
                'pe_ratio': metrics.get('valuation', {}).get('trailing_pe'),
                'price_to_book': metrics.get('valuation', {}).get('price_to_book'),
            },
            'profitability': {
                'profit_margin': format_number(metrics.get('profitability', {}).get('profit_margin'), 'percentage'),
                'roe': format_number(metrics.get('profitability', {}).get('return_on_equity'), 'percentage'),
            },
            'financial_health': {
                'debt_to_equity': metrics.get('financial_health', {}).get('debt_to_equity'),
                'current_ratio': metrics.get('financial_health', {}).get('current_ratio'),
                'free_cashflow': format_number(metrics.get('financial_health', {}).get('free_cashflow'), 'currency'),
            },
            'trading': {
                'beta': metrics.get('trading', {}).get('beta'),
                'fifty_two_week_high': metrics.get('trading', {}).get('fifty_two_week_high'),
                'fifty_two_week_low': metrics.get('trading', {}).get('fifty_two_week_low'),
            }
        }
    except Exception as e:
        logger.error(f"Error in tool_get_company_metrics: {e}")
        return {'error': str(e), 'ticker': ticker}


def tool_search_stock_news(ticker: str, limit: int = 5) -> Dict[str, Any]:
    """Search recent news articles about a stock"""
    try:
        articles = fetch_stock_specific_news(ticker, limit=limit)
        
        return {
            'ticker': ticker,
            'news_count': len(articles),
            'articles': [
                {
                    'title': article.get('title'),
                    'source': article.get('source'),
                    'published_at': article.get('published_at'),
                    'summary': article.get('summary', '')[:150] + '...' if len(article.get('summary', '')) > 150 else article.get('summary', ''),
                }
                for article in articles[:limit]
            ]
        }
    except Exception as e:
        logger.error(f"Error in tool_search_stock_news: {e}")
        return {'error': str(e), 'ticker': ticker}


def tool_compare_stocks(ticker1: str, ticker2: str) -> Dict[str, Any]:
    """Compare two stocks side-by-side on key metrics"""
    try:
        stock1_price = get_current_price(ticker1)
        stock2_price = get_current_price(ticker2)
        
        stock1_info = get_stock_info(ticker1)
        stock2_info = get_stock_info(ticker2)
        
        return {
            'comparison': {
                ticker1: {
                    'price': stock1_price.get('price'),
                    'change_percent': stock1_price.get('change_percent'),
                    'pe_ratio': stock1_info.get('pe_ratio'),
                    'market_cap': stock1_info.get('market_cap'),
                    'sector': stock1_info.get('sector'),
                },
                ticker2: {
                    'price': stock2_price.get('price'),
                    'change_percent': stock2_price.get('change_percent'),
                    'pe_ratio': stock2_info.get('pe_ratio'),
                    'market_cap': stock2_info.get('market_cap'),
                    'sector': stock2_info.get('sector'),
                }
            }
        }
    except Exception as e:
        logger.error(f"Error in tool_compare_stocks: {e}")
        return {'error': str(e), 'tickers': [ticker1, ticker2]}


# Tool registry for OpenAI function calling
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "get_stock_price": {
        "function": tool_get_stock_price,
        "description": "Get the current stock price, daily change percentage, high, low, and volume for a ticker symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., META, AAPL, MSFT, GOOGL, TSLA)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_technical_indicators": {
        "function": tool_get_technical_indicators,
        "description": "Get technical analysis indicators including RSI (Relative Strength Index), MACD (Moving Average Convergence Divergence), Bollinger Bands, and Moving Averages for a stock. Use this to analyze momentum, trends, and overbought/oversold conditions.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_company_metrics": {
        "function": tool_get_company_metrics,
        "description": "Get comprehensive company financial metrics including valuation (P/E ratio, market cap), profitability (profit margin, ROE), financial health (debt-to-equity, free cashflow), and trading data (beta, 52-week high/low)",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                }
            },
            "required": ["ticker"]
        }
    },
    "search_stock_news": {
        "function": tool_search_stock_news,
        "description": "Search and retrieve recent news articles specifically about a stock ticker. Returns filtered news with titles, sources, and summaries.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of news articles to return (default: 5, max: 10)",
                    "default": 5
                }
            },
            "required": ["ticker"]
        }
    },
    "compare_stocks": {
        "function": tool_compare_stocks,
        "description": "Compare two stocks side-by-side on price, change percentage, P/E ratio, market cap, and sector. Useful for investment decisions.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker1": {
                    "type": "string",
                    "description": "First stock ticker symbol"
                },
                "ticker2": {
                    "type": "string",
                    "description": "Second stock ticker symbol"
                }
            },
            "required": ["ticker1", "ticker2"]
        }
    }
}


def get_tools_for_openai() -> List[Dict[str, Any]]:
    """
    Convert tool registry to OpenAI function calling format.
    
    Returns:
        List of tool definitions in OpenAI format
    """
    tools = []
    
    for tool_name, tool_def in TOOL_REGISTRY.items():
        tools.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_def["description"],
                "parameters": tool_def["parameters"]
            }
        })
    
    return tools


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Execute a tool by name with given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments to pass to the tool
        
    Returns:
        Result from the tool function
    """
    if tool_name not in TOOL_REGISTRY:
        logger.error(f"Unknown tool: {tool_name}")
        return {"error": f"Unknown tool: {tool_name}"}
    
    tool_function = TOOL_REGISTRY[tool_name]["function"]
    
    try:
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        result = tool_function(**arguments)
        return result
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {"error": str(e), "tool": tool_name}
