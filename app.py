"""
Finance Dashboard - Main Application
A personal finance tracking dashboard with stock prices, news, and AI insights.
"""

from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def dashboard():
    """Render the main dashboard page with placeholder data."""
    # Placeholder data - will be replaced with real data later
    context = {
        'current_time': datetime.now().strftime('%B %d, %Y %H:%M'),
        'page_title': 'Finance Dashboard'
    }
    return render_template('dashboard.html', **context)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
