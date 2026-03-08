"""
Finance Dashboard - Main Application
A personal finance tracking dashboard with stock prices, news, and AI insights.
"""

import logging
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from datetime import datetime

from load_1password_env import load_1password_env
load_1password_env(Path(__file__).resolve().parent)

from dotenv import load_dotenv
load_dotenv()

from services.stock_service import get_current_price, get_historical_data, get_stock_info
from services.news_service import get_news_with_cache
from services.ai_insights_service import get_market_insights
from services.technical_indicators import calculate_technical_summary
from services.company_metrics import get_metrics_summary
from services.ai_insights_service_v2 import get_llm_market_insights
from services.agent_chat_service import chat_with_agent, clear_conversation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    # Fetch ticker-specific news with 1-hour cache
    news_articles = get_news_with_cache(category='business', limit=10, max_age_minutes=60, ticker=ticker)
    
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


@app.route('/api/ai-insights')
def get_ai_insights():
    """
    API endpoint to fetch AI-powered market insights for a stock.
    
    Query params:
        ticker (str): Stock ticker symbol (default: META)
        use_ai (bool): Force use of n8n AI analysis (default: false)
    
    Returns:
        JSON with sentiment, key_factors, outlook, risk_level, and commentary
    """
    ticker = request.args.get('ticker', 'META')
    use_ai = request.args.get('use_ai', 'false').lower() == 'true'
    
    insights = get_market_insights(ticker=ticker, use_ai=use_ai)
    return jsonify(insights)


@app.route('/api/ai-insights-llm')
def get_ai_insights_llm():
    """
    NEW: LLM-powered market insights endpoint.
    
    Uses OpenAI GPT-4o Mini or Anthropic Claude to generate professional
    market analysis including buy/sell signals, trend analysis, and risk assessment.
    
    Query params:
        ticker (str): Stock ticker symbol (default: META)
        use_cache (bool): Use cached insights if available (default: true)
    
    Returns:
        JSON with AI-generated market insights:
        - sentiment: bullish|bearish|neutral
        - recommendation: strong_buy|buy|hold|sell|strong_sell
        - buy_sell_signal: Brief action signal
        - trend_analysis: Market trend description
        - key_drivers: List of key factors
        - risk_level: low|medium|high
        - macro_insights: Sector/macro context
        - risk_factors: List of risks
        - price_target: Price target or range
        - timeframe: Time horizon
        - source: LLM provider and model
        - confidence: high|medium|low
    """
    ticker = request.args.get('ticker', 'META')
    use_cache = request.args.get('use_cache', 'true').lower() == 'true'
    
    try:
        insights = get_llm_market_insights(ticker=ticker, use_cache=use_cache)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e), 'ticker': ticker}), 400


@app.route('/api/chat-agent', methods=['POST'])
def chat_agent():
    """
    Interactive chat endpoint with AI agent that has tool calling capabilities.
    
    The agent can call various tools to fetch real-time stock data, technical indicators,
    company metrics, and news to answer user questions intelligently.
    
    Request Body (JSON):
        {
            "message": "User's question",
            "ticker": "META" (optional - provides context),
            "conversation_id": "unique-id" (optional),
            "history": [...] (optional - previous messages)
        }
    
    Returns:
        {
            "reply": "AI assistant response",
            "tool_calls": [{"tool": "get_stock_price", "args": {...}, "result": {...}}],
            "conversation_id": "unique-id",
            "timestamp": "ISO timestamp"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        ticker = data.get('ticker')
        conversation_id = data.get('conversation_id', f'chat-{datetime.now().timestamp()}')
        history = data.get('history', [])
        
        # Call agent with tool access
        response = chat_with_agent(
            user_message=user_message,
            conversation_id=conversation_id,
            ticker=ticker,
            history=history
        )
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in chat_agent endpoint: {e}")
        return jsonify({
            'error': str(e),
            'reply': 'Sorry, I encountered an error. Please try again.'
        }), 500


@app.route('/api/chat-clear/<conversation_id>', methods=['POST'])
def clear_chat(conversation_id: str):
    """
    Clear conversation history for a specific conversation ID.
    
    Args:
        conversation_id: Conversation ID to clear
    
    Returns:
        JSON with success status
    """
    success = clear_conversation(conversation_id)
    return jsonify({'success': success, 'conversation_id': conversation_id})


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
    ticker = request.args.get('ticker', 'META')
    news_limit = int(request.args.get('news_limit', 5))
    
    # Fetch stock data
    stock_info = get_stock_info(ticker)
    stock_price = get_current_price(ticker)
    
    # Fetch recent news - ALWAYS force fresh for API analysis
    # max_age_minutes=0 forces API fetch regardless of cache
    news_articles = get_news_with_cache(category='business', limit=news_limit, max_age_minutes=0)
    
    # Build news context - handle empty news gracefully
    news_context = ""
    if news_articles and len(news_articles) > 0:
        news_context = "\n\n".join([
            f"{i+1}. {article.get('ai_context', article.get('title', 'No title'))}"
            for i, article in enumerate(news_articles)
        ])
    else:
        news_context = "No recent news available. Analyzing based on company fundamentals and market trends."
    
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
        'prompt_template': f"""Analyze {ticker} stock with following context:

Company: {stock_info.get('company_name', ticker)}
Sector: {stock_info.get('sector', 'N/A')}
Current Price: ${stock_price.get('price', 0)}
Change: {stock_price.get('change_percent', 0)}%
Market Cap: ${stock_info.get('market_cap', 0):,}
P/E Ratio: {stock_info.get('pe_ratio', 'N/A')}

Recent News & Market Context:
{news_context}

Provide analysis as JSON with keys:
1. sentiment (bullish/bearish/neutral)
2. key_factors (list of factors)
3. outlook (1-7 day prediction)
4. risk_level (low/medium/high)"""
    }
    
    return jsonify(response)


@app.route('/api/technical-indicators')
def get_technical_indicators():
    """
    API endpoint to fetch technical indicators for a stock
    
    Query params:
        ticker (str): Stock ticker symbol (default: META)
    
    Returns:
        JSON with RSI, MACD, Bollinger Bands, and summary
    """
    ticker = request.args.get('ticker', 'META')
    
    try:
        # Get historical data
        historical_data = get_historical_data(ticker, period='3mo')
        prices = [day['price'] for day in historical_data]
        
        # Calculate technical indicators
        technical_summary = calculate_technical_summary(prices)
        technical_summary['ticker'] = ticker
        
        return jsonify(technical_summary)
    except Exception as e:
        return jsonify({'error': str(e), 'ticker': ticker}), 400


@app.route('/api/company-metrics')
def get_company_metrics_api():
    """
    API endpoint to fetch company financial metrics
    
    Query params:
        ticker (str): Stock ticker symbol (default: META)
    
    Returns:
        JSON with company metrics, financial health, profitability, etc.
    """
    ticker = request.args.get('ticker', 'META')
    
    try:
        metrics = get_metrics_summary(ticker)
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e), 'ticker': ticker}), 400


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
