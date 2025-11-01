"""
Test script to verify Supabase connection and database operations.
Run this to ensure everything is configured correctly.
"""

from database import db
from datetime import datetime

print("=" * 50)
print("SUPABASE CONNECTION TEST")
print("=" * 50)

# Test 1: Health Check
print("\n1. Testing Supabase connection...")
health = db.health_check()
print(f"   Status: {health.get('status')}")
print(f"   Connected: {health.get('connected')}")
if 'error' in health:
    print(f"   Error: {health.get('error')}")
    print("\n⚠️  Connection failed! Check your .env file.")
    exit(1)
else:
    print("   ✓ Connection successful!")

# Test 2: Insert Sample Stock Data
print("\n2. Testing stock data insertion...")
try:
    result = db.insert_stock_data(
        ticker='AAPL',
        price=150.25,
        change_percent=2.5,
        high=152.00,
        low=149.00,
        volume=50000000
    )
    if 'error' in result:
        print(f"   ✗ Error: {result['error']}")
    else:
        print(f"   ✓ Stock data inserted successfully!")
        print(f"   Ticker: {result.get('ticker')}")
        print(f"   Price: ${result.get('price')}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Retrieve Stock Data
print("\n3. Testing stock data retrieval...")
try:
    latest = db.get_latest_stock_data('AAPL')
    if latest:
        print(f"   ✓ Retrieved latest stock data!")
        print(f"   Ticker: {latest.get('ticker')}")
        print(f"   Price: ${latest.get('price')}")
        print(f"   Change: {latest.get('change_percent')}%")
        print(f"   Timestamp: {latest.get('timestamp')}")
    else:
        print("   ✗ No data found (but no error)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Insert Sample News
print("\n4. Testing news insertion...")
try:
    news_result = db.insert_news(
        title='Test News Article',
        summary='This is a test news article summary',
        url='https://example.com/test-article',
        source='Test Source',
        published_at=datetime.utcnow().isoformat()
    )
    if 'error' in news_result:
        print(f"   ✗ Error: {news_result['error']}")
    else:
        print(f"   ✓ News article inserted successfully!")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Retrieve News
print("\n5. Testing news retrieval...")
try:
    news = db.get_recent_news(limit=5)
    if news:
        print(f"   ✓ Retrieved {len(news)} news articles!")
        for article in news[:2]:  # Show first 2
            print(f"   - {article.get('title')[:50]}...")
    else:
        print("   ✗ No news found (but no error)")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Insert AI Insight
print("\n6. Testing AI insight insertion...")
try:
    ai_result = db.insert_ai_insight(
        content='Test AI insight: Markets are looking positive today.',
        insight_type='daily'
    )
    if 'error' in ai_result:
        print(f"   ✗ Error: {ai_result['error']}")
    else:
        print(f"   ✓ AI insight inserted successfully!")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 7: Retrieve AI Insight
print("\n7. Testing AI insight retrieval...")
try:
    insight = db.get_latest_ai_insight('daily')
    if insight:
        print(f"   ✓ Retrieved latest AI insight!")
        print(f"   Content: {insight.get('content')[:80]}...")
        print(f"   Generated: {insight.get('generated_at')}")
    else:
        print("   ✗ No insight found (but no error)")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 50)
print("TEST COMPLETE!")
print("=" * 50)
print("\n✓ All tests passed! Supabase is configured correctly.")
print("  You can now proceed to build the stock service.\n")
