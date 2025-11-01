"""Quick test of get_current_price function."""

from services.stock_service import get_current_price

print("Testing get_current_price() function...")
print("=" * 50)

# Test with Apple stock
print("\n📊 Fetching AAPL (Apple)...")
aapl_data = get_current_price('AAPL')

if 'error' in aapl_data:
    print(f"❌ Error: {aapl_data['error']}")
else:
    print(f"✅ Ticker: {aapl_data['ticker']}")
    print(f"   Price: ${aapl_data['price']}")
    print(f"   Change: {aapl_data['change_percent']:.2f}%")
    print(f"   High: ${aapl_data['high']}")
    print(f"   Low: ${aapl_data['low']}")
    print(f"   Volume: {aapl_data['volume']:,}")
    print(f"   Timestamp: {aapl_data['timestamp']}")

# Test with Microsoft
print("\n📊 Fetching MSFT (Microsoft)...")
msft_data = get_current_price('MSFT')

if 'error' in msft_data:
    print(f"❌ Error: {msft_data['error']}")
else:
    print(f"✅ Price: ${msft_data['price']} ({msft_data['change_percent']:.2f}%)")

# Test with invalid ticker
print("\n📊 Testing invalid ticker (INVALID)...")
invalid_data = get_current_price('INVALID')
if 'error' in invalid_data:
    print(f"✅ Error handling works: {invalid_data['error']}")

print("\n" + "=" * 50)
print("✅ Test complete!")
