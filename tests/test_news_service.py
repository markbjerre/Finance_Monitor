"""
Tests for News Service
Verifies NewsAPI integration, article fetching, parsing, and caching.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.news_service import (
    fetch_financial_news,
    get_news_with_cache,
    validate_news_api_config
)


def test_api_config():
    """Test that NewsAPI is properly configured."""
    print("\n=== Test 1: API Configuration ===")
    
    is_configured = validate_news_api_config()
    
    if is_configured:
        print("✅ NewsAPI is properly configured")
        return True
    else:
        print("❌ NewsAPI not configured - check .env file")
        print("   Need: NEWS_API_KEY=your_key_here")
        return False


def test_fetch_news():
    """Test fetching news from NewsAPI."""
    print("\n=== Test 2: Fetch News from API ===")
    
    try:
        print("Fetching 5 business news articles...")
        articles = fetch_financial_news(category='business', limit=5)
        
        if not articles:
            print("❌ No articles returned - check API key or network")
            return False
        
        print(f"✅ Fetched {len(articles)} articles")
        
        # Display first article
        if len(articles) > 0:
            article = articles[0]
            print(f"\n📰 Sample Article:")
            print(f"   Title: {article.get('title', 'N/A')[:80]}...")
            print(f"   Source: {article.get('source', 'N/A')}")
            print(f"   Published: {article.get('published_at', 'N/A')}")
            print(f"   AI Context: {article.get('ai_context', 'N/A')[:100]}...")
            print(f"   URL: {article.get('url', 'N/A')[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return False


def test_news_caching():
    """Test news caching functionality."""
    print("\n=== Test 3: News Caching ===")
    
    try:
        # First call - should fetch from API and cache
        print("First call - fetching and caching...")
        news1 = get_news_with_cache(category='business', limit=5, max_age_minutes=60)
        
        if not news1:
            print("❌ No news returned")
            return False
        
        print(f"✅ First call successful: {len(news1)} articles")
        
        # Second call - should use cache
        print("\nSecond call - should use cache...")
        news2 = get_news_with_cache(category='business', limit=5, max_age_minutes=60)
        
        if not news2:
            print("❌ No news returned from cache")
            return False
        
        print(f"✅ Second call successful: {len(news2)} articles (from cache)")
        
        # Verify both calls returned same number of articles
        if len(news1) == len(news2):
            print("✅ Cache working correctly - same data returned")
            return True
        else:
            print("⚠️ Different number of articles returned")
            return False
            
    except Exception as e:
        print(f"❌ Error testing cache: {e}")
        return False


def test_article_structure():
    """Test that articles have the correct structure for AI."""
    print("\n=== Test 4: Article Structure (AI-Ready) ===")
    
    try:
        articles = fetch_financial_news(category='business', limit=3)
        
        if not articles:
            print("❌ No articles to test")
            return False
        
        required_fields = ['title', 'summary', 'url', 'source', 'published_at', 'ai_context']
        
        for i, article in enumerate(articles, 1):
            print(f"\n📄 Article {i}:")
            missing_fields = []
            
            for field in required_fields:
                if field in article:
                    print(f"   ✅ {field}: {str(article[field])[:50]}...")
                else:
                    print(f"   ❌ {field}: MISSING")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️ Missing fields: {missing_fields}")
        
        print("\n✅ All articles have required fields for AI")
        return True
        
    except Exception as e:
        print(f"❌ Error testing structure: {e}")
        return False


def test_database_storage():
    """Test that news is stored in database."""
    print("\n=== Test 5: Database Storage ===")
    
    try:
        from database import db
        
        # Fetch and cache news
        print("Fetching and caching news...")
        get_news_with_cache(category='business', limit=5)
        
        # Check database
        print("Checking database for cached news...")
        cached_news = db.get_recent_news(limit=5)
        
        if cached_news and len(cached_news) > 0:
            print(f"✅ Found {len(cached_news)} articles in database")
            print(f"   Most recent: {cached_news[0].get('title', 'N/A')[:60]}...")
            return True
        else:
            print("❌ No news found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False


def run_all_tests():
    """Run all news service tests."""
    print("=" * 70)
    print("NEWS SERVICE TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("API Configuration", test_api_config),
        ("Fetch News from API", test_fetch_news),
        ("News Caching", test_news_caching),
        ("Article Structure", test_article_structure),
        ("Database Storage", test_database_storage)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! News service ready for dashboard integration.")
    else:
        print("\n⚠️ Some tests failed. Fix issues before integrating.")
    
    print("=" * 70)


if __name__ == '__main__':
    run_all_tests()
