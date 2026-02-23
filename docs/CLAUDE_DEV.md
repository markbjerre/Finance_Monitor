# Finance Dashboard - Development Guide for Claude Code

## Project Overview

**Type**: AI-Powered Financial Analytics Backend  
**Status**: Production-ready with AI features  
**Live URL**: https://ai-vaerksted.cloud/finance  
**Repository**: Local monorepo under `/Finance dashboard`

### Architecture
```
Finance dashboard/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── database/                   # Database schemas & Supabase
├── services/                   # Business logic
│   ├── stock_service.py        # Stock price & data
│   ├── news_service.py         # News aggregation
│   ├── ai_insights_service.py  # AI analysis
│   ├── company_metrics.py       # Financial metrics
│   ├── technical_indicators.py # TA calculations
│   ├── agent_chat_service.py   # Chat agent with tools
│   └── api_utils.py            # Utility functions
├── templates/                  # Jinja2 templates
├── static/                     # CSS, images
└── tests/                      # Unit & integration tests
```

---

## Development Stack

| Layer | Technology | Details |
|-------|-----------|---------|
| **Backend** | Python 3.11, Flask | Port 5002, REST API |
| **AI/LLM** | OpenAI/Claude | Market insights generation |
| **Data** | yfinance, NewsAPI | Stock & news data |
| **Database** | Supabase (PostgreSQL) | User data, cache |
| **Cache** | Redis (optional) | Session & response cache |
| **Testing** | pytest, unittest | Unit & integration tests |

---

## Getting Started

### Quick Start (Docker)
```bash
# From project root
docker-compose -f docker-compose.dev.yml up finance-backend

# Backend: http://localhost:5002
# Dashboard: http://localhost:5002/
# API: http://localhost:5002/api/*
```

### Local Development (No Docker)
```bash
# Setup
cd "Finance dashboard"
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Run
flask run
# http://localhost:5002
```

### Environment Variables

Create `.env` file:
```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=1

# APIs
OPENAI_API_KEY=sk_... (OpenAI API key)
NEWSAPI_KEY=...       (NewsAPI key)

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=...

# Optional: Feature flags
USE_CACHE=true
CACHE_TTL=3600
```

---

## Agent Utilization Strategy

### For Feature Development
Use **fullstack-developer** agent:
- Add new financial metrics endpoints
- Create API service layers
- Implement data caching strategies

### For AI Features
Use **ai-engineer** agent:
- Integrate new LLM models
- Develop market insights generation
- Implement agent tools and capabilities
- Build chat agent enhancements

**Example**:
```
Task: "Add macro-economic indicators API"
└─ ai-engineer handles:
   - LLM prompt engineering for analysis
   - Market context integration
   - Risk assessment generation
```

### For Testing
Use **fullstack-developer**:
- Write unit tests for services
- Create API endpoint tests
- Test LLM integration

### For Code Quality
Use **code-reviewer**:
- Review AI prompt engineering
- Validate API design
- Security review (API key handling, input validation)

---

## API Endpoints Reference

### Pages
```
GET /                           # Main dashboard page
```

### Health & Status
```
GET /health                     # Health check
Response: {"status": "ok"}
```

### Stock Data APIs
```
GET /api/analysis-data?ticker=META&news_limit=5
Response: Stock info + news + prompt template

GET /api/technical-indicators?ticker=META
Response: RSI, MACD, Bollinger Bands

GET /api/company-metrics?ticker=META
Response: Financial health metrics
```

### AI Analysis APIs
```
GET /api/ai-insights?ticker=META&use_ai=false
Response: {
  "sentiment": "bullish|bearish|neutral",
  "key_factors": [...],
  "outlook": "...",
  "risk_level": "low|medium|high",
  "commentary": "..."
}

GET /api/ai-insights-llm?ticker=META&use_cache=true
Response: LLM-generated market insights with recommendations

POST /api/chat-agent
Body: {"message": "Is META overvalued?", "ticker": "META"}
Response: {
  "reply": "...",
  "tool_calls": [{...}],
  "conversation_id": "..."
}

POST /api/chat-clear/<conversation_id>
Response: {"success": true}
```

---

## Development Workflow

### Adding a New Service

1. **Create service file**
   ```python
   # services/new_metric_service.py
   def get_new_metric(ticker: str) -> dict:
       """Get new financial metric for ticker."""
       # Implementation
       return {...}
   ```

2. **Add to app.py**
   ```python
   from services.new_metric_service import get_new_metric
   
   @app.route('/api/new-metric')
   def new_metric():
       ticker = request.args.get('ticker', 'META')
       return jsonify(get_new_metric(ticker))
   ```

3. **Write tests**
   ```python
   # tests/test_new_metric.py
   def test_get_new_metric():
       result = get_new_metric('META')
       assert 'value' in result
   ```

4. **Test locally**
   ```bash
   # Start dev server
   flask run
   
   # Test endpoint
   curl http://localhost:5002/api/new-metric?ticker=META
   ```

### Adding an AI Feature

1. **Design the feature**
   - Define LLM task/prompt
   - Identify required tools/data
   - Plan integration with existing services

2. **Create LLM integration**
   ```python
   # services/new_ai_feature.py
   from openai import OpenAI
   
   def analyze_with_new_feature(ticker: str) -> str:
       # Fetch data, build prompt, call LLM
       pass
   ```

3. **Add API endpoint**
   ```python
   @app.route('/api/new-ai-feature')
   def new_ai_feature():
       ticker = request.args.get('ticker', 'META')
       analysis = analyze_with_new_feature(ticker)
       return jsonify({"analysis": analysis})
   ```

4. **Test with agent tool**
   - Use `agent-chat` endpoint to test
   - Validate LLM output quality
   - Iterate on prompts

---

## Services Reference

### stock_service.py
```python
get_current_price(ticker)    # Current stock price & change
get_historical_data(ticker, period='1mo')  # Price history
get_stock_info(ticker)       # Company info & fundamentals
```

### news_service.py
```python
get_news_with_cache(category, limit, max_age_minutes, ticker=None)
# Fetches news articles with intelligent caching
```

### ai_insights_service.py
```python
get_market_insights(ticker, use_ai=False)
# Traditional insights OR AI-generated (via n8n)
```

### ai_insights_service_v2.py
```python
get_llm_market_insights(ticker, use_cache=True)
# Direct LLM-generated insights with professional analysis
```

### agent_chat_service.py
```python
chat_with_agent(user_message, conversation_id, ticker, history)
# Interactive chat with tool calling capabilities
```

### technical_indicators.py
```python
calculate_technical_summary(prices)
# RSI, MACD, Bollinger Bands calculations
```

### company_metrics.py
```python
get_metrics_summary(ticker)
# Financial health, profitability, valuation metrics
```

---

## Testing

### Run Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_stock_service.py

# With coverage
pytest --cov=.

# Verbose output
pytest -v

# Watch mode (requires pytest-watch)
ptw
```

### Test Structure
```
tests/
├── test_stock_service.py       # Stock API tests
├── test_news_service.py        # News aggregation tests
├── test_ai_insights_service.py # AI feature tests
├── test_supabase.py            # Database tests
└── __init__.py
```

### Writing Tests
```python
# tests/test_new_feature.py
import pytest
from services.new_feature import get_feature_data

def test_get_feature_data():
    """Test feature data retrieval."""
    result = get_feature_data('META')
    assert isinstance(result, dict)
    assert 'data' in result
    
def test_get_feature_data_invalid_ticker():
    """Test handling of invalid ticker."""
    with pytest.raises(ValueError):
        get_feature_data('INVALID')
```

---

## Debugging

### View Logs
```bash
# Flask dev server output
# Automatic with FLASK_DEBUG=1

# Docker logs
docker logs finance-backend-dev -f

# Check API endpoint
curl http://localhost:5002/api/ai-insights?ticker=META
```

### Debug LLM Integration
```python
# In your service code
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"LLM Prompt: {prompt}")
logger.debug(f"LLM Response: {response}")
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:5002/health

# Stock data
curl http://localhost:5002/api/analysis-data?ticker=META

# Chat agent
curl -X POST http://localhost:5002/api/chat-agent \
  -H "Content-Type: application/json" \
  -d '{"message":"Is META a good buy?","ticker":"META"}'
```

---

## MCP Servers Available

- **Docker MCP** - Container operations
- **Brave Search MCP** - Web research for market insights
- **GitHub MCP** - Version control
- **Playwright MCP** - Web testing (future UI)

---

## Code Conventions

### Python
- 4-space indentation (PEP 8)
- `snake_case` for functions/variables
- `UPPER_SNAKE_CASE` for constants
- Type hints on all functions
- Google-style docstrings

### API Design
- RESTful endpoints (GET, POST, etc.)
- JSON request/response
- HTTP status codes (200, 400, 404, 500)
- Consistent error format

### Error Handling
```python
@app.errorhandler(ValueError)
def handle_value_error(e):
    return jsonify({'error': str(e)}), 400

@app.errorhandler(Exception)
def handle_generic_error(e):
    logger.error(f"Unhandled error: {e}")
    return jsonify({'error': 'Internal server error'}), 500
```

---

## Common Tasks

### Add a new stock ticker to dashboard
```python
# In app.py
ticker = 'AAPL'  # Change from META to AAPL
stock_data = get_current_price(ticker)
```

### Change LLM provider
```python
# In services/ai_insights_service_v2.py
# Swap OpenAI for Claude, etc.
```

### Cache API responses
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_data(ticker):
    return expensive_operation(ticker)
```

### Monitor API performance
```bash
# Use curl with timing
curl -w "Time: %{time_total}s\n" http://localhost:5002/api/data
```

---

## Troubleshooting

### OpenAI API errors
```
Error: Invalid API key

Solution:
1. Check .env OPENAI_API_KEY is set
2. Verify API key is valid at openai.com
3. Restart Flask: Ctrl+C, flask run
```

### Supabase connection errors
```
Error: connection refused

Solution:
1. Verify SUPABASE_URL and KEY in .env
2. Check network connectivity
3. Test connection: python -c "from database.supabase_service import supabase; print(supabase.auth.get_session())"
```

### NewsAPI rate limits
```
Error: 429 Too Many Requests

Solution:
1. Caching is handled automatically (1-hour TTL)
2. Check max_age_minutes parameter
3. Upgrade API plan if needed
```

### LLM timeout issues
```
Error: timeout while calling OpenAI API

Solution:
1. Check internet connection
2. Try simpler prompts
3. Add timeout parameter to OpenAI client
4. Retry with exponential backoff
```

---

## Performance Tips

### API Response Time
- Use caching for frequently accessed data
- Parallelize API calls where possible
- Minimize LLM API calls (cache results)

### Database Queries
- Add indexes to frequently queried columns
- Use connection pooling
- Monitor slow queries with logs

### LLM Integration
- Use shorter prompts for faster responses
- Cache LLM outputs (1-hour TTL typical)
- Consider async processing for heavy operations

---

## Useful Commands

```bash
# Development
flask run                              # Start dev server
flask shell                            # Python shell with app context
python -m pip freeze > requirements.txt # Update dependencies

# Testing
pytest                                 # Run all tests
pytest tests/test_stock_service.py    # Run specific test
pytest --cov                          # With coverage report

# Docker
docker-compose -f docker-compose.dev.yml up finance-backend
docker logs finance-backend-dev -f

# Database
supabase status                        # Check Supabase status
supabase migration list                # View migrations

# API Testing
curl http://localhost:5002/health
curl http://localhost:5002/api/ai-insights?ticker=META
```

---

## Next Steps

1. **Enhance AI Features**
   - Add more LLM models
   - Improve prompts
   - Add sentiment analysis

2. **Add Real-Time Data**
   - WebSocket for live prices
   - Real-time alerts
   - Push notifications

3. **Improve UI**
   - Create React frontend
   - Interactive charts
   - Custom dashboards

4. **Scale Infrastructure**
   - Add caching layer (Redis)
   - Database optimization
   - API rate limiting
   - Load balancing

---

## Getting Help

Ask Claude Code for:
- Feature implementation guidance
- Debugging specific errors
- LLM prompt engineering advice
- API design recommendations
- Performance optimization

Check the code comments and docstrings first!
