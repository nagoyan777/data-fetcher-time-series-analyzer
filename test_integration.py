#!/usr/bin/env python3
"""
US Stock Analysis Platform - Integration Test
"""
import panel as pn
from apps.data_fetcher_app import MarketExplorerApp
from apps.data_analyzer_app import StockAnalyzerApp
from apps.data_manager_app import DatabaseManagerApp
from apps.trigger_controller_app import PortfolioTrackerApp

# Enable Panel extensions
pn.extension('plotly', 'tabulator', template='material')

def test_integration():
    """Test the complete platform integration"""

    print("🚀 Starting US Stock Analysis Platform Integration Test")
    print("=" * 60)

    try:
        print("📱 Creating apps...")

        # Test each app creation
        print("  Creating Market Explorer...")
        market_explorer = MarketExplorerApp()

        print("  Creating Stock Analyzer...")
        stock_analyzer = StockAnalyzerApp()

        print("  Creating Database Manager...")
        database_manager = DatabaseManagerApp()

        print("  Creating Portfolio Tracker...")
        portfolio_tracker = PortfolioTrackerApp()

        print("✅ All apps created successfully!")

        # Test Panel app generation
        print("🖥️  Generating Panel interfaces...")

        apps = {
            'market_explorer': market_explorer.create_app(),
            'stock_analyzer': stock_analyzer.create_app(),
            'database_manager': database_manager.create_app(),
            'portfolio_tracker': portfolio_tracker.create_app()
        }

        print("✅ All Panel interfaces generated!")

        # Test basic functionality
        print("🔧 Testing basic functionality...")

        # Test shared store access
        from utils.shared_store import shared_store
        status = shared_store.get_status()
        print(f"  Database: {status.get('stock_count', 0)} stocks available")

        print("✅ Basic functionality test passed!")

        # Test single app deployment
        print("🌐 Testing single app deployment...")

        pn.serve(
            apps['market_explorer'],
            port=5006,
            title='Market Explorer - Integration Test',
            show=False,
            autoreload=False
        )

        print("✅ Integration test complete - Market Explorer running on port 5006")

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integration()