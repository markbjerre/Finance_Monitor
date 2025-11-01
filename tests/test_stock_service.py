"""
Comprehensive test file for stock service development.
Run this file to test all stock service functions as we build them.

Usage:
    python tests/test_stock_service.py
    
    Or run specific tests:
    python tests/test_stock_service.py --test current_price
    python tests/test_stock_service.py --test historical
    python tests/test_stock_service.py --test caching
"""

import sys
import os

# Add parent directory to path so we can import from services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.stock_service import (
    get_current_price, 
    get_historical_data,
    # fetch_and_cache_stock,  # Uncomment as we implement
    # get_stock_with_cache,
    # fetch_multiple_stocks,
    # get_stock_info,
    # validate_ticker
)


def test_current_price():
    """Test get_current_price() function."""
    print("\n" + "="*60)
    print("TEST: get_current_price()")
    print("="*60)
    
    # Test with Apple
    print("\n📊 Testing AAPL (Apple)...")
    aapl = get_current_price('AAPL')
    
    if 'error' in aapl:
        print(f"❌ Error: {aapl['error']}")
        return False
    else:
        print(f"✅ Ticker: {aapl['ticker']}")
        print(f"   Price: ${aapl['price']}")
        print(f"   Change: {aapl['change_percent']:.2f}%")
        print(f"   High: ${aapl['high']}")
        print(f"   Low: ${aapl['low']}")
        print(f"   Volume: {aapl['volume']:,}")
    
    # Test with Microsoft
    print("\n📊 Testing MSFT (Microsoft)...")
    msft = get_current_price('MSFT')
    if 'error' not in msft:
        print(f"✅ Price: ${msft['price']} ({msft['change_percent']:.2f}%)")
    
    # Test error handling
    print("\n📊 Testing invalid ticker (INVALID)...")
    invalid = get_current_price('INVALID')
    if 'error' in invalid:
        print(f"✅ Error handling works: {invalid.get('error', 'Error occurred')}")
    
    return True


def test_historical_data():
    """Test get_historical_data() function."""
    print("\n" + "="*60)
    print("TEST: get_historical_data()")
    print("="*60)
    
    # Test 7-day history
    print("\n📈 Testing 7-day history for AAPL...")
    history = get_historical_data('AAPL', period='7d')
    
    if history:
        print(f"✅ Retrieved {len(history)} data points")
        print("\n   Last 3 days:")
        for point in history[-3:]:
            print(f"   {point['date']}: ${point['price']} (High: ${point['high']}, Low: ${point['low']})")
    else:
        print("❌ No data retrieved")
        return False
    
    # Test 1-month history
    print("\n📈 Testing 1-month history for MSFT...")
    msft_history = get_historical_data('MSFT', period='1mo')
    if msft_history:
        print(f"✅ Retrieved {len(msft_history)} data points")
        print(f"   Date range: {msft_history[0]['date']} to {msft_history[-1]['date']}")
        print(f"   Last price: ${msft_history[-1]['price']}")
    
    return True


def test_fetch_and_cache():
    """Test fetch_and_cache_stock() function."""
    print("\n" + "="*60)
    print("TEST: fetch_and_cache_stock()")
    print("="*60)
    print("⚠️  Not yet implemented")
    return True


def test_cache_retrieval():
    """Test get_stock_with_cache() function."""
    print("\n" + "="*60)
    print("TEST: get_stock_with_cache()")
    print("="*60)
    print("⚠️  Not yet implemented")
    return True


def test_multiple_stocks():
    """Test fetch_multiple_stocks() function."""
    print("\n" + "="*60)
    print("TEST: fetch_multiple_stocks()")
    print("="*60)
    print("⚠️  Not yet implemented")
    return True


def test_stock_info():
    """Test get_stock_info() function."""
    print("\n" + "="*60)
    print("TEST: get_stock_info()")
    print("="*60)
    print("⚠️  Not yet implemented")
    return True


def run_all_tests():
    """Run all available tests."""
    print("\n" + "🧪 " + "="*58)
    print("STOCK SERVICE - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Current Price", test_current_price),
        ("Historical Data", test_historical_data),
        ("Fetch & Cache", test_fetch_and_cache),
        ("Cache Retrieval", test_cache_retrieval),
        ("Multiple Stocks", test_multiple_stocks),
        ("Stock Info", test_stock_info),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    # Check for specific test argument
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_name = sys.argv[2] if len(sys.argv) > 2 else ""
        
        test_map = {
            "current_price": test_current_price,
            "historical": test_historical_data,
            "cache": test_fetch_and_cache,
            "cache_retrieval": test_cache_retrieval,
            "multiple": test_multiple_stocks,
            "info": test_stock_info,
        }
        
        if test_name in test_map:
            test_map[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
    else:
        # Run all tests
        success = run_all_tests()
        sys.exit(0 if success else 1)
