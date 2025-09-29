#!/usr/bin/env python3
"""
Test if chart creation works
"""
import plotly.graph_objects as go
import pandas as pd
from utils.shared_store import shared_store

def test_chart_creation():
    print("Testing chart creation...")

    # Get AAPL data
    data = shared_store.get_stock_prices("AAPL")
    print(f"Data loaded: {len(data)} records")

    if not data.empty:
        # Take last 30 days
        data = data.tail(30)

        # Create candlestick chart
        fig = go.Figure(data=go.Candlestick(
            x=pd.to_datetime(data['date']),
            open=data['open_price'],
            high=data['high_price'],
            low=data['low_price'],
            close=data['close_price'],
            name='AAPL'
        ))

        fig.update_layout(
            title="AAPL Stock Price",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            template='plotly_white'
        )

        # Save to HTML to verify it works
        fig.write_html("/tmp/test_chart.html")
        print("✅ Chart created and saved to /tmp/test_chart.html")
        print("   You can open it with: open /tmp/test_chart.html")
    else:
        print("❌ No data available")

if __name__ == "__main__":
    test_chart_creation()