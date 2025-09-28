#!/usr/bin/env python3
"""
Data Fetcher & Time Series Analyzer - Multi-App Launcher
Panel-based multi-app suite for personal time series analytics workflows
Adapted from literature analysis project architecture
"""
import panel as pn
from apps.data_fetcher_app import DataFetcherApp
from apps.data_analyzer_app import DataAnalyzerApp
from apps.data_manager_app import DataManagerApp
from apps.trigger_controller_app import TriggerControllerApp

# Enable Panel extensions
pn.extension('plotly', 'tabulator', template='material')

def create_apps():
    """Create and configure all apps"""

    # Initialize apps
    fetcher_app = DataFetcherApp()
    analyzer_app = DataAnalyzerApp()
    manager_app = DataManagerApp()
    controller_app = TriggerControllerApp()

    return {
        'data_fetcher': fetcher_app.create_app(),
        'time_series_analyzer': analyzer_app.create_app(),
        'data_manager': manager_app.create_app(),
        'update_controller': controller_app.create_app()
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

    print("🚀 Starting Data Fetcher & Time Series Analyzer Suite...")
    print("=" * 60)

    # Create apps
    apps = create_apps()

    # Configure multi-app setup
    app_configs = {
        'data_fetcher': {
            'port': 5006,
            'title': 'Data Fetcher - Time Series Analytics',
            'description': 'Configure and trigger data collection from APIs'
        },
        'time_series_analyzer': {
            'port': 5007,
            'title': 'Time Series Analyzer - Analytics Dashboard',
            'description': 'Visualize and analyze collected time series data'
        },
        'data_manager': {
            'port': 5008,
            'title': 'Data Manager - Storage & Export',
            'description': 'Browse, backup, and export stored data'
        },
        'update_controller': {
            'port': 5009,
            'title': 'Update Controller - Manual Triggers',
            'description': 'Manage manual triggers and update schedules'
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

        print("\n🎯 Implementation Features:")
        print("- Multi-app architecture with responsive UX")
        print("- Manual trigger controls for all data operations")
        print("- Linear/Log Y-axis toggle in Time Series Analyzer")
        print("- Cross-app data sharing and automatic backups")
        print("- Non-blocking async operations")
        print("\n⚡ Performance Benefits:")
        print("- No UI freezing during data fetching")
        print("- Progressive loading for large time series")
        print("- Smart caching reduces redundant API calls")
        print("- Real-time progress indicators")

    except KeyboardInterrupt:
        print("\n👋 Shutting down Data Fetcher Suite...")
    except Exception as e:
        print(f"❌ Error starting apps: {e}")
        print("Make sure Panel is installed: pip install -r requirements.txt")