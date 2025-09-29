#!/usr/bin/env python3
"""
US Stock Analysis & Investment Tracker - Multi-App Launcher
Panel-based platform for stock research, SBI portfolio tracking, and long-term analysis
"""
import panel as pn
from apps.data_fetcher_app import MarketExplorerApp
from apps.data_analyzer_app import StockAnalyzerApp
from apps.data_manager_app import DatabaseManagerApp
from apps.trigger_controller_app import PortfolioTrackerApp

# Enable Panel extensions
pn.extension('plotly', 'tabulator', template='material')

def create_apps():
    """Create and configure all stock analysis apps"""

    # Initialize apps
    market_explorer = MarketExplorerApp()
    stock_analyzer = StockAnalyzerApp()
    data_manager = DatabaseManagerApp()
    portfolio_tracker = PortfolioTrackerApp()

    return {
        'market_explorer': market_explorer.create_app(),
        'stock_analyzer': stock_analyzer.create_app(),
        'data_manager': data_manager.create_app(),
        'portfolio_tracker': portfolio_tracker.create_app()
    }

def create_navigation_bar():
    """Create navigation bar for all apps"""
    nav_buttons = pn.Row(
        pn.pane.HTML("""
        <div style="padding: 10px; background: #28a745; color: white; margin-bottom: 20px;">
            <h3 style="margin: 0;">📊 Data Fetcher & Time Series Analyzer</h3>
            <p style="margin: 5px 0;">Multi-App Panel Interface for Personal Analytics</p>
            <a href="http://localhost:5006" style="color: #fff; margin-right: 15px;">📥 Data Fetcher</a>
            <a href="http://localhost:5007" style="color: #fff; margin-right: 15px;">📈 Time Series Analyzer</a>
            <a href="http://localhost:5008" style="color: #fff; margin-right: 15px;">💾 Data Manager</a>
            <a href="http://localhost:5009" style="color: #fff;">⚡ Update Controller</a>
        </div>
        """),
        sizing_mode='stretch_width'
    )
    return nav_buttons

if __name__ == "__main__":

    print("🚀 Starting US Stock Analysis & Investment Tracker Suite...")
    print("=" * 60)

    # Create apps
    apps = create_apps()

    # Configure multi-app setup
    app_configs = {
        'market_explorer': {
            'port': 5006,
            'title': 'Market Explorer - US Stock Research',
            'description': 'Research stocks, analyze market trends, and screen investments'
        },
        'stock_analyzer': {
            'port': 5007,
            'title': 'Stock Analyzer - Advanced Charts & Analysis',
            'description': 'Candlestick charts, technical indicators, and performance analysis'
        },
        'data_manager': {
            'port': 5008,
            'title': 'Database Manager - SQLite Operations & Export',
            'description': 'Manage stock database, export portfolio reports, and maintain data integrity'
        },
        'portfolio_tracker': {
            'port': 5009,
            'title': 'Portfolio Tracker - SBI Investment Tracking',
            'description': 'Import SBI transactions, track P&L, and analyze portfolio performance'
        }
    }

    print("Available Applications:")
    for app_name, config in app_configs.items():
        print(f"  {config['title']}")
        print(f"    → http://localhost:{config['port']}")
        print(f"    → {config['description']}")
        print()

    # Launch all apps simultaneously
    try:
        import threading
        import time

        def serve_app(name, app, port, title):
            """Serve an individual app"""
            try:
                print(f"🚀 Starting {title} on port {port}...")
                pn.serve(
                    app,
                    port=port,
                    title=title,
                    show=False,
                    autoreload=False,  # Disable autoreload for multi-app
                    allow_websocket_origin=[f'localhost:{port}']
                )
            except Exception as e:
                print(f"❌ Error starting {title}: {e}")

        # Start all apps in separate threads
        threads = []

        for app_name, config in app_configs.items():
            app = apps[app_name]
            thread = threading.Thread(
                target=serve_app,
                args=(app_name, app, config['port'], config['title']),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            time.sleep(1)  # Stagger startup

        print("\n" + "=" * 60)
        print("🎉 ALL APPS SUCCESSFULLY STARTED!")
        print("=" * 60)
        for app_name, config in app_configs.items():
            print(f"✅ {config['title']}")
            print(f"   🌐 http://localhost:{config['port']}")
            print(f"   📝 {config['description']}")
            print()

        print("💡 TIP: Open multiple browser tabs to test the multi-app experience!")
        print("⏹️  Press Ctrl+C to stop all servers")

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down all apps...")
            pass

        print("\n🎯 Platform Features:")
        print("- Multi-app stock analysis and portfolio tracking")
        print("- SQLite database with 10+ year data retention")
        print("- SBI Securities CSV import and P&L tracking")
        print("- Real-time stock quotes and market data")
        print("- Tech/Growth/Value investment focus")
        print("- USD/JPY currency conversion")
        print("\n📊 Analysis Capabilities:")
        print("- Candlestick charts and technical indicators")
        print("- Portfolio performance vs market benchmarks")
        print("- Long-term trend analysis and sector comparison")
        print("- Excel export for tax reporting")

    except KeyboardInterrupt:
        print("\n👋 Shutting down US Stock Analysis Suite...")
    except Exception as e:
        print(f"❌ Error starting apps: {e}")
        print("Make sure dependencies are installed: pip install -r requirements.txt")