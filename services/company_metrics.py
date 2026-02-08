"""
Company Metrics Service - Fetch and cache financial metrics and company information

Integrates with yfinance to get earnings, revenue, balance sheet data, and key metrics
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for company metrics (ticker -> data + timestamp)
METRICS_CACHE = {}
CACHE_EXPIRY_MINUTES = 1440  # 24 hours


def get_company_metrics(ticker: str, max_age_minutes: int = CACHE_EXPIRY_MINUTES) -> Dict[str, Any]:
    """
    Get comprehensive company metrics and financial data
    
    Args:
        ticker: Stock ticker symbol
        max_age_minutes: Maximum age of cached data before refreshing
        
    Returns:
        Dictionary with company metrics, earnings, and key financial data
    """
    try:
        # Check cache
        if ticker in METRICS_CACHE:
            cached_data, cached_time = METRICS_CACHE[ticker]
            age_minutes = (datetime.now() - cached_time).total_seconds() / 60
            
            if age_minutes < max_age_minutes:
                logger.info(f"Using cached metrics for {ticker} (age: {age_minutes:.0f}m)")
                return cached_data
        
        logger.info(f"Fetching fresh metrics for {ticker}")
        
        # Fetch ticker data
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        
        # Extract key metrics
        metrics = {
            'ticker': ticker,
            'company_name': info.get('longName', ticker),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'website': info.get('website', ''),
            
            # Valuation Metrics
            'valuation': {
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'trailing_pe': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 'N/A'),
                'peg_ratio': info.get('pegRatio', 'N/A'),
            },
            
            # Profitability Metrics
            'profitability': {
                'profit_margin': info.get('profitMargins', 'N/A'),
                'operating_margin': info.get('operatingMargins', 'N/A'),
                'gross_margin': info.get('grossMargins', 'N/A'),
                'return_on_assets': info.get('returnOnAssets', 'N/A'),
                'return_on_equity': info.get('returnOnEquity', 'N/A'),
            },
            
            # Growth Metrics
            'growth': {
                'earnings_growth': info.get('earningsGrowth', 'N/A'),
                'revenue_growth': info.get('revenueGrowth', 'N/A'),
                'earnings_per_share': info.get('trailingEps', 'N/A'),
            },
            
            # Financial Health
            'financial_health': {
                'current_ratio': info.get('currentRatio', 'N/A'),
                'quick_ratio': info.get('quickRatio', 'N/A'),
                'debt_to_equity': info.get('debtToEquity', 'N/A'),
                'total_debt': info.get('totalDebt', 0),
                'total_cash': info.get('totalCash', 0),
                'free_cashflow': info.get('freeCashflow', 0),
            },
            
            # Dividend Info
            'dividend': {
                'dividend_rate': info.get('dividendRate', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'payout_ratio': info.get('payoutRatio', 'N/A'),
                'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield', 'N/A'),
            },
            
            # Trading Info
            'trading': {
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'fifty_day_average': info.get('fiftyDayAverage', 0),
                'two_hundred_day_average': info.get('twoHundredDayAverage', 0),
                'beta': info.get('beta', 'N/A'),
                'average_volume': info.get('averageVolume', 0),
            },
            
            # Analyst Info
            'analyst': {
                'target_price': info.get('targetPrice', 'N/A'),
                'number_of_analysts': info.get('numberOfAnalysts', 0),
                'recommendation_rating': info.get('recommendationKey', 'N/A'),
            }
        }
        
        # Get quarterly financials
        try:
            quarterly_financials = ticker_obj.quarterly_financials
            if quarterly_financials is not None and not quarterly_financials.empty:
                latest_quarter = quarterly_financials.iloc[:, 0]
                metrics['latest_financials'] = {
                    'period': str(quarterly_financials.columns[0].date()),
                    'total_revenue': latest_quarter.get('Total Revenue', 0),
                    'operating_income': latest_quarter.get('Operating Income', 0),
                    'net_income': latest_quarter.get('Net Income', 0),
                }
        except Exception as e:
            logger.warning(f"Could not fetch quarterly financials for {ticker}: {e}")
        
        # Cache the results
        METRICS_CACHE[ticker] = (metrics, datetime.now())
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error fetching metrics for {ticker}: {e}")
        return {'error': str(e), 'ticker': ticker}


def format_number(value: Any, format_type: str = 'compact') -> str:
    """
    Format numbers for display
    
    Args:
        value: Numeric value
        format_type: 'compact', 'percentage', 'decimal', or 'currency'
        
    Returns:
        Formatted string
    """
    if value is None or value == 'N/A' or isinstance(value, str):
        return 'N/A'
    
    try:
        value = float(value)
        
        if format_type == 'percentage':
            return f"{value * 100:.2f}%"
        elif format_type == 'currency':
            if value >= 1e9:
                return f"${value / 1e9:.2f}B"
            elif value >= 1e6:
                return f"${value / 1e6:.2f}M"
            elif value >= 1e3:
                return f"${value / 1e3:.2f}K"
            else:
                return f"${value:.2f}"
        elif format_type == 'compact':
            if value >= 1e9:
                return f"{value / 1e9:.2f}B"
            elif value >= 1e6:
                return f"{value / 1e6:.2f}M"
            elif value >= 1e3:
                return f"{value / 1e3:.2f}K"
            else:
                return f"{value:.2f}"
        else:  # decimal
            return f"{value:.2f}"
    except (ValueError, TypeError):
        return 'N/A'


def get_metrics_summary(ticker: str) -> Dict[str, Any]:
    """
    Get a concise summary of most important metrics
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with key summary metrics
    """
    metrics = get_company_metrics(ticker)
    
    if 'error' in metrics:
        return metrics
    
    return {
        'ticker': ticker,
        'company_name': metrics.get('company_name', 'N/A'),
        'sector': metrics.get('sector', 'N/A'),
        'industry': metrics.get('industry', 'N/A'),
        'valuation': {
            'market_cap': format_number(metrics['valuation'].get('market_cap'), 'compact'),
            'pe_ratio': metrics['valuation'].get('trailing_pe'),
            'price_to_book': metrics['valuation'].get('price_to_book'),
        },
        'profitability': {
            'profit_margin': format_number(metrics['profitability'].get('profit_margin'), 'percentage'),
            'return_on_equity': format_number(metrics['profitability'].get('return_on_equity'), 'percentage'),
        },
        'financial_health': {
            'debt_to_equity': metrics['financial_health'].get('debt_to_equity'),
            'current_ratio': metrics['financial_health'].get('current_ratio'),
            'free_cashflow': format_number(metrics['financial_health'].get('free_cashflow'), 'currency'),
        },
        'dividend_yield': format_number(metrics['dividend'].get('dividend_yield'), 'percentage'),
        'beta': metrics['trading'].get('beta'),
        'fifty_two_week_high': metrics['trading'].get('fifty_two_week_high'),
        'fifty_two_week_low': metrics['trading'].get('fifty_two_week_low'),
    }
