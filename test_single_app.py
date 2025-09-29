#!/usr/bin/env python3
"""
Test single app deployment
"""
import panel as pn
from apps.data_fetcher_app import MarketExplorerApp

# Enable Panel extensions
pn.extension('plotly', 'tabulator', template='material')

if __name__ == "__main__":
    print("🚀 Testing single app deployment...")

    # Create app
    app = MarketExplorerApp()
    panel_app = app.create_app()

    print("✅ App created successfully")
    print("🌐 Starting server on port 5006...")

    # Serve the app
    pn.serve(
        panel_app,
        port=5006,
        title='Market Explorer - Test',
        show=False,
        autoreload=False
    )