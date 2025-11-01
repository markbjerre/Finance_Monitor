"""
Finance Dashboard - Main Application
A personal finance tracking dashboard with stock prices, news, and AI insights.
"""

from flask import Flask, render_template, jsonify
from datetime import datetime
from services.stock_service import get_current_price, get_historical_data, get_stock_info

app = Flask(__name__)


@app.route('/')
def dashboard():
    """Render the main dashboard page with real stock data."""
    # Fetch META stock data
    ticker = 'META'
    stock_data = get_current_price(ticker)
    stock_info = get_stock_info(ticker)
    
    # Get historical data for chart
    historical_data = get_historical_data(ticker, period='1mo')
    
    context = {
        'current_time': datetime.now().strftime('%B %d, %Y %H:%M'),
        'page_title': 'Finance Dashboard',
        'stock': stock_data,
        'stock_info': stock_info,
        'historical_data': historical_data,
        'ticker': ticker
    }
    return render_template('dashboard.html', **context)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
