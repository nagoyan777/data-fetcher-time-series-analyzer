#!/usr/bin/env python3
"""
Test all export functionality in Database Manager
"""
from utils.shared_store import shared_store
import os

def test_all_exports():
    print("🔍 Testing All Export Functions")
    print("=" * 50)

    # 1. Test Stock Prices CSV Export
    print("\n1. Testing Stock Prices CSV Export...")
    result = shared_store.export_stock_prices(format='csv')
    if result['success']:
        file_size = os.path.getsize(result['file_path']) / 1024
        print(f"   ✅ CSV export successful ({file_size:.2f} KB)")
        print(f"   📄 {result['file_path']}")
    else:
        print(f"   ❌ Export failed: {result.get('error')}")

    # 2. Test Stock Prices JSON Export
    print("\n2. Testing Stock Prices JSON Export...")
    result = shared_store.export_stock_prices(format='json')
    if result['success']:
        file_size = os.path.getsize(result['file_path']) / 1024
        print(f"   ✅ JSON export successful ({file_size:.2f} KB)")
        print(f"   📄 {result['file_path']}")
    else:
        print(f"   ❌ Export failed: {result.get('error')}")

    # 3. Test Complete Excel Export
    print("\n3. Testing Complete Excel Export...")
    result = shared_store.export_all_data(format='excel')
    if result['success']:
        file_size = os.path.getsize(result['file_path']) / 1024
        print(f"   ✅ Excel export successful ({file_size:.2f} KB)")
        print(f"   📄 {result['file_path']}")

        # Verify sheets
        import pandas as pd
        with pd.ExcelFile(result['file_path']) as xls:
            sheets = xls.sheet_names
            print(f"   📊 Sheets: {', '.join(sheets)}")
    else:
        print(f"   ❌ Export failed: {result.get('error')}")

    # 4. Test Database Backup
    print("\n4. Testing Database Backup...")
    result = shared_store.backup_database()
    if result['success']:
        file_size = os.path.getsize(result['backup_file']) / (1024 * 1024)  # MB
        print(f"   ✅ Backup successful ({file_size:.2f} MB)")
        print(f"   💾 {result['backup_file']}")
    else:
        print(f"   ❌ Backup failed: {result.get('error')}")

    # 5. Test Portfolio Report Export (even if empty)
    print("\n5. Testing Portfolio Report Export...")
    result = shared_store.export_portfolio_report(format='excel')
    if result['success']:
        file_size = os.path.getsize(result['file_path']) / 1024
        print(f"   ✅ Portfolio report successful ({file_size:.2f} KB)")
        print(f"   📄 {result['file_path']}")
    else:
        print(f"   ❌ Export failed: {result.get('error')}")

    # 6. Test Database Vacuum
    print("\n6. Testing Database Vacuum...")
    result = shared_store.vacuum_database()
    if result['success']:
        print(f"   ✅ Vacuum successful")
        print(f"   💾 Space saved: {result['space_saved']}")
    else:
        print(f"   ❌ Vacuum failed: {result.get('error')}")

    # Summary
    print("\n" + "=" * 50)
    print("✅ All export tests completed!")
    print("\nExported files are in: data/exports/")
    print("Backup files are in: data/backups/")

if __name__ == "__main__":
    test_all_exports()