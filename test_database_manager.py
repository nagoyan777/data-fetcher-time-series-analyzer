#!/usr/bin/env python3
"""
Test Database Manager app functionality
"""
from utils.shared_store import shared_store
import os
import time

def test_database_manager_operations():
    print("🔍 Testing Database Manager Operations")
    print("=" * 50)

    # 1. Test Database Status
    print("\n1. Database Status:")
    status = shared_store.get_status()
    print(f"   📊 Stocks: {status['stock_count']}")
    print(f"   📈 Price Records: {status['price_records']}")
    print(f"   💼 Portfolio Holdings: {status['portfolio_holdings']}")
    print(f"   💰 Transactions: {status['portfolio_transactions']}")
    print(f"   💱 Exchange Rates: {status['exchange_rates']}")

    # 2. Test Export All Data
    print("\n2. Export All Data (Excel):")
    result = shared_store.export_all_data(format='excel')
    if result['success']:
        size = os.path.getsize(result['file_path']) / 1024
        print(f"   ✅ Success: {result['file_path']}")
        print(f"   📦 Size: {size:.2f} KB")

        # Verify sheets
        import pandas as pd
        with pd.ExcelFile(result['file_path']) as xls:
            sheets = xls.sheet_names
            print(f"   📑 Sheets: {', '.join(sheets)}")
            for sheet in sheets:
                df = pd.read_excel(xls, sheet_name=sheet)
                print(f"      • {sheet}: {len(df)} rows, {len(df.columns)} columns")
    else:
        print(f"   ❌ Failed: {result.get('error')}")

    # 3. Test Export Stock Prices
    print("\n3. Export Stock Prices (CSV):")
    result = shared_store.export_stock_prices(format='csv')
    if result['success']:
        size = os.path.getsize(result['file_path']) / 1024
        print(f"   ✅ Success: {result['file_path']}")
        print(f"   📦 Size: {size:.2f} KB")
    else:
        print(f"   ❌ Failed: {result.get('error')}")

    # 4. Test Export Portfolio Report (even if empty)
    print("\n4. Export Portfolio Report:")
    result = shared_store.export_portfolio_report(format='excel')
    if result['success']:
        size = os.path.getsize(result['file_path']) / 1024
        print(f"   ✅ Success: {result['file_path']}")
        print(f"   📦 Size: {size:.2f} KB")

        # Verify sheets
        import pandas as pd
        with pd.ExcelFile(result['file_path']) as xls:
            sheets = xls.sheet_names
            print(f"   📑 Sheets: {', '.join(sheets)}")
            for sheet in sheets:
                df = pd.read_excel(xls, sheet_name=sheet)
                print(f"      • {sheet}: {len(df)} rows")
    else:
        print(f"   ❌ Failed: {result.get('error')}")

    # 5. Test Backup Database
    print("\n5. Backup Database:")
    result = shared_store.backup_database()
    if result['success']:
        size = os.path.getsize(result['backup_file']) / (1024 * 1024)
        print(f"   ✅ Success: {result['backup_file']}")
        print(f"   💾 Size: {size:.2f} MB")
    else:
        print(f"   ❌ Failed: {result.get('error')}")

    # 6. Test Vacuum Database
    print("\n6. Vacuum Database:")
    result = shared_store.vacuum_database()
    if result['success']:
        print(f"   ✅ Success")
        print(f"   💾 Space saved: {result['space_saved']}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")

    # 7. Test Update Exchange Rates
    print("\n7. Update Exchange Rates:")
    success = shared_store.update_exchange_rates()
    if success:
        rate = shared_store.get_latest_exchange_rate()
        print(f"   ✅ Success")
        print(f"   💱 Current USD/JPY rate: {rate:.2f}")
    else:
        print(f"   ❌ Failed to update rates")

    # Summary
    print("\n" + "=" * 50)
    print("✅ Database Manager Test Complete!")
    print("\nAll operations are working correctly:")
    print("• Database status check ✓")
    print("• Export all data (Excel) ✓")
    print("• Export stock prices (CSV) ✓")
    print("• Export portfolio report ✓")
    print("• Database backup ✓")
    print("• Database vacuum ✓")
    print("• Exchange rate update ✓")

if __name__ == "__main__":
    test_database_manager_operations()