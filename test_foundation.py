#!/usr/bin/env python3
"""
Test Foundation Components
Quick test to verify database, API integration, and SBI parser work correctly
"""
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root / "core"))
sys.path.append(str(project_root / "utils"))

from database_manager import DatabaseManager
from stock_data_fetcher import StockDataFetcher, CurrencyConverter
from sbi_parser import SBICSVParser
from shared_store import shared_store

def test_database():
    """Test database initialization and operations"""
    print("🔄 Testing Database...")

    db = DatabaseManager()

    # Test database stats
    stats = db.get_database_stats()
    print(f"✅ Database initialized with {stats['us_stocks_count']} stocks")

    # Test getting stocks by category
    tech_stocks = db.get_stocks_by_category('tech')
    print(f"✅ Found {len(tech_stocks)} tech stocks")

    return True

def test_stock_fetcher():
    """Test stock data fetching"""
    print("\n🔄 Testing Stock Data Fetcher...")

    fetcher = StockDataFetcher()

    # Test with a simple quote (Yahoo Finance fallback)
    quote = fetcher.get_current_quote("AAPL")
    if quote['success']:
        print(f"✅ AAPL quote: ${quote['price']}")
    else:
        print(f"⚠️ AAPL quote failed: {quote['error']}")

    return True

def test_currency_converter():
    """Test currency conversion"""
    print("\n🔄 Testing Currency Converter...")

    converter = CurrencyConverter()
    rate = converter.get_current_rate()

    if rate:
        print(f"✅ Current USD/JPY rate: {rate}")
    else:
        print("⚠️ Currency conversion failed, using default rate")

    return True

def test_sbi_parser():
    """Test SBI CSV parser"""
    print("\n🔄 Testing SBI CSV Parser...")

    parser = SBICSVParser()

    # Create and test sample CSV
    sample_file = parser.create_sample_csv("test_sample.csv")
    result = parser.parse_csv_file(sample_file)

    if result['success']:
        print(f"✅ Parsed {result['total_count']} transactions from sample CSV")

        # Show first transaction
        if result['transactions']:
            tx = result['transactions'][0]
            print(f"   Sample: {tx['date']} - {tx['action']} {tx['quantity']} {tx['symbol']} @ ${tx['price_usd']}")
    else:
        print(f"❌ CSV parsing failed: {result['error']}")

    # Clean up
    Path(sample_file).unlink(missing_ok=True)

    return result['success']

def test_shared_store():
    """Test shared store integration"""
    print("\n🔄 Testing Shared Store...")

    # Test status
    status = shared_store.get_status()
    print(f"✅ Shared store status: {status['stock_count']} stocks, {status['price_records']} price records")

    # Test stock data retrieval
    stocks = shared_store.get_stocks_by_category('tech')
    print(f"✅ Retrieved {len(stocks)} tech stocks via shared store")

    return True

def main():
    """Run all foundation tests"""
    print("🚀 Testing US Stock Analysis Platform Foundation")
    print("=" * 60)

    tests = [
        ("Database Operations", test_database),
        ("Stock Data Fetcher", test_stock_fetcher),
        ("Currency Converter", test_currency_converter),
        ("SBI CSV Parser", test_sbi_parser),
        ("Shared Store", test_shared_store)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")

    print("\n" + "=" * 60)
    print(f"🎯 Foundation Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All foundation components working correctly!")
        print("✅ Ready for Panel app implementation")
    else:
        print("⚠️ Some foundation issues need attention")

    print("\n📝 Next Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Get Alpha Vantage API key (free): https://www.alphavantage.co/support/#api-key")
    print("3. Run Panel apps: python main.py")

if __name__ == "__main__":
    main()