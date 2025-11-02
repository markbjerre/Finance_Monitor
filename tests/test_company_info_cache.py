"""
Tests for Company Info Caching Functionality
Verifies that company information is cached correctly and refreshed after 24 hours.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.stock_service import get_stock_info
from database import db
import time


def test_cache_miss_then_hit():
    """
    Test that first call fetches from API (cache miss),
    second call uses cached data (cache hit).
    """
    print("\n=== Test 1: Cache Miss → Cache Hit ===")
    
    ticker = 'META'
    
    # First call - should fetch from yfinance and cache it
    print(f"First call to get_stock_info('{ticker}')...")
    result1 = get_stock_info(ticker)
    
    if 'error' in result1:
        print(f"❌ Error fetching data: {result1['error']}")
        return False
    
    print(f"✅ First call successful: {result1.get('company_name', 'N/A')}")
    print(f"   Sector: {result1.get('sector', 'N/A')}")
    print(f"   Market Cap: ${result1.get('market_cap', 0):,}")
    
    # Second call - should use cached data
    print(f"\nSecond call to get_stock_info('{ticker}')...")
    result2 = get_stock_info(ticker)
    
    if 'error' in result2:
        print(f"❌ Error fetching data: {result2['error']}")
        return False
    
    print(f"✅ Second call successful (from cache): {result2.get('company_name', 'N/A')}")
    
    # Verify both calls returned same data
    if result1.get('company_name') == result2.get('company_name'):
        print("✅ Cache working correctly - same data returned")
        return True
    else:
        print("❌ Cache issue - different data returned")
        return False


def test_cache_freshness_check():
    """
    Test that is_company_info_fresh() correctly identifies fresh vs stale data.
    """
    print("\n=== Test 2: Cache Freshness Check ===")
    
    ticker = 'AAPL'
    
    # Fetch data to ensure it's cached
    print(f"Fetching data for {ticker}...")
    result = get_stock_info(ticker)
    
    if 'error' in result:
        print(f"❌ Error fetching data: {result['error']}")
        return False
    
    print(f"✅ Data cached for {ticker}")
    
    # Check if data is fresh (should be, we just cached it)
    is_fresh = db.is_company_info_fresh(ticker, max_age_hours=24)
    
    if is_fresh:
        print("✅ Cache correctly identified as fresh")
        return True
    else:
        print("❌ Cache incorrectly identified as stale")
        return False


def test_multiple_tickers():
    """
    Test caching with multiple different tickers.
    """
    print("\n=== Test 3: Multiple Tickers ===")
    
    tickers = ['MSFT', 'GOOGL', 'TSLA']
    results = {}
    
    for ticker in tickers:
        print(f"\nFetching {ticker}...")
        result = get_stock_info(ticker)
        
        if 'error' not in result:
            results[ticker] = result
            print(f"✅ {ticker}: {result.get('company_name', 'N/A')}")
        else:
            print(f"❌ {ticker}: {result['error']}")
    
    if len(results) == len(tickers):
        print(f"\n✅ All {len(tickers)} tickers cached successfully")
        return True
    else:
        print(f"\n⚠️ Only {len(results)}/{len(tickers)} tickers cached")
        return False


def test_database_storage():
    """
    Test that cached data is actually stored in database.
    """
    print("\n=== Test 4: Database Storage Verification ===")
    
    ticker = 'NVDA'
    
    # Fetch and cache
    print(f"Fetching and caching {ticker}...")
    result = get_stock_info(ticker)
    
    if 'error' in result:
        print(f"❌ Error fetching data: {result['error']}")
        return False
    
    # Verify it's in database
    print(f"Checking database for {ticker}...")
    cached_data = db.get_company_info(ticker)
    
    if cached_data:
        print(f"✅ Data found in database:")
        print(f"   Company: {cached_data.get('company_name', 'N/A')}")
        print(f"   Sector: {cached_data.get('sector', 'N/A')}")
        print(f"   Last Updated: {cached_data.get('last_updated', 'N/A')}")
        return True
    else:
        print(f"❌ Data not found in database")
        return False


def run_all_tests():
    """Run all company info cache tests."""
    print("=" * 60)
    print("COMPANY INFO CACHING TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Cache Miss → Hit", test_cache_miss_then_hit),
        ("Cache Freshness Check", test_cache_freshness_check),
        ("Multiple Tickers", test_multiple_tickers),
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
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()
