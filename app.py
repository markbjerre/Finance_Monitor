"""
Finance Dashboard - Main Application
A personal finance tracking dashboard with stock prices, news, and AI insights.
"""

from flask import Flask, render_template, jsonify
from datetime import datetime
from services.stock_service import get_current_price, get_historical_data, get_stock_info
from services.news_service import get_news_with_cache

app = Flask(__name__)


@app.route('/')
def dashboard():
    """Render the main dashboard page with real stock data and news."""
    # Fetch META stock data
    ticker = 'META'
    stock_data = get_current_price(ticker)
    stock_info = get_stock_info(ticker)
    
    # Get historical data for chart
    historical_data = get_historical_data(ticker, period='1mo')
    
    # Fetch financial news with 1-hour cache
    news_articles = get_news_with_cache(category='business', limit=10, max_age_minutes=60)
    
    context = {
        'current_time': datetime.now().strftime('%B %d, %Y %H:%M'),
        'page_title': 'Finance Dashboard',
        'stock': stock_data,
        'stock_info': stock_info,
        'historical_data': historical_data,
        'ticker': ticker,
        'news': news_articles  # Add news to context
    }
    return render_template('dashboard.html', **context)


@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "ok"})


@app.route('/api/analysis-data')
def get_analysis_data():
    """
    API endpoint for n8n to fetch stock and news data for AI analysis.
    Returns combined data ready for AI processing.
    
    Query params:
        ticker (str): Stock ticker symbol (default: META)
        news_limit (int): Number of news articles (default: 5)
    
    Returns:
        JSON with stock info, current price, and recent news articles
    """
    from flask import request
    
    ticker = request.args.get('ticker', 'META')
    news_limit = int(request.args.get('news_limit', 5))
    
    # Fetch stock data
    stock_info = get_stock_info(ticker)
    stock_price = get_current_price(ticker)
    
    # Fetch recent news
    news_articles = get_news_with_cache(category='business', limit=news_limit, max_age_minutes=60)
    
    # Combine into AI-ready format
    response = {
        'ticker': ticker,
        'timestamp': datetime.now().isoformat(),
        'stock': {
            'company_name': stock_info.get('company_name', ''),
            'sector': stock_info.get('sector', ''),
            'industry': stock_info.get('industry', ''),
            'current_price': stock_price.get('price', 0),
            'change_percent': stock_price.get('change_percent', 0),
            'market_cap': stock_info.get('market_cap', 0),
            'pe_ratio': stock_info.get('pe_ratio', 0),
            'description': stock_info.get('description', '')
        },
        'news': news_articles,
        'prompt_template': f"""Analyze the following financial news in context of {ticker} stock:

Company: {stock_info.get('company_name', ticker)}
Sector: {stock_info.get('sector', 'N/A')}
Current Price: ${stock_price.get('price', 0)}
Change: {stock_price.get('change_percent', 0)}%
Market Cap: ${stock_info.get('market_cap', 0):,}

Recent News:
{{news_context}}

Provide:
1. Overall Sentiment (bullish/bearish/neutral)
2. Key Factors affecting the stock
3. Short-term outlook (1-7 days)
4. Risk Assessment (low/medium/high)

Format as JSON with keys: sentiment, key_factors, outlook, risk_level"""
    }
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
