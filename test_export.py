#!/usr/bin/env python3
"""
Test database export functionality
"""
from utils.shared_store import shared_store

def test_export():
    print("🔍 Testing Database Export Functions")
    print("=" * 50)

    # Test export stock prices
    print("1. Testing Stock Prices Export...")
    result = shared_store.export_stock_prices(format='csv')
    if result['success']:
        print(f"   ✅ Stock prices exported to: {result['file_path']}")
    else:
        print(f"   ❌ Export failed: {result.get('error')}")

    # Test export all data
    print("\n2. Testing All Data Export (Excel)...")
    result = shared_store.export_all_data(format='excel')
    if result['success']:
        print(f"   ✅ All data exported to: {result['file_path']}")
    else:
        print(f"   ❌ Export failed: {result.get('error')}")

    # Test backup
    print("\n3. Testing Database Backup...")
    result = shared_store.backup_database()
    if result['success']:
        print(f"   ✅ Database backed up to: {result['backup_file']}")
    else:
        print(f"   ❌ Backup failed: {result.get('error')}")

    print("\n✅ Export tests complete!")

if __name__ == "__main__":
    test_export()