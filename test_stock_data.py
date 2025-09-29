#!/usr/bin/env python3
"""
Test if stock data is being saved and retrieved correctly
"""
from utils.shared_store import shared_store

def test_stock_data():
    print("🔍 Testing Stock Data Storage and Retrieval")
    print("=" * 50)

    # Test fetching AAPL data
    print("1. Fetching AAPL data...")
    result = shared_store.fetch_stock_data("AAPL", full_history=False)
    print(f"   Fetch result: {result.get('success')}")
    if result.get('success'):
        print(f"   Data points fetched: {len(result.get('data', []))}")
    else:
        print(f"   Error: {result.get('error')}")

    # Test retrieving from database
    print("\n2. Retrieving AAPL from database...")
    price_data = shared_store.get_stock_prices("AAPL")
    print(f"   Records in database: {len(price_data)}")

    if not price_data.empty:
        print(f"   Date range: {price_data['date'].min()} to {price_data['date'].max()}")
        print(f"   Columns: {list(price_data.columns)}")
        print(f"   Sample data:")
        print(price_data.head(3))
    else:
        print("   ❌ No data in database!")

    # Check database stats
    print("\n3. Database Statistics:")
    status = shared_store.get_status()
    print(f"   Stock count: {status.get('stock_count')}")
    print(f"   Price records: {status.get('price_records')}")
    print(f"   Price data range: {status.get('price_data_range')}")

if __name__ == "__main__":
    test_stock_data()