"""
Market Explorer App - US Stock Research & Screening
Stock market analysis, screening, and data collection for long-term investing
"""
import panel as pn
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import asyncio
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_store import shared_store
from utils.navigation import create_navigation_bar, create_quick_actions_panel, create_app_status_indicator

class MarketExplorerApp:
    """Market research and stock screening interface"""

    def __init__(self):
        # Stock selection
        stock_options = self._get_stock_options()
        self.stock_selector = pn.widgets.Select(
            name="Select Stock",
            options=stock_options,
            value=stock_options[0][1] if stock_options else "AAPL",  # Use the value part of first tuple
            width=200
        )

        # Category filter
        self.category_filter = pn.widgets.Select(
            name="Investment Category",
            options=["All", "tech", "growth", "value", "market"],
            value="All",
            width=200
        )

        # Time period selector
        self.time_period = pn.widgets.Select(
            name="Time Period",
            options=["1M", "3M", "6M", "1Y", "2Y", "5Y", "MAX"],
            value="1Y",
            width=150
        )

        # Action buttons
        self.fetch_button = pn.widgets.Button(
            name="📊 Get Stock Data",
            button_type="primary",
            width=180
        )

        self.quote_button = pn.widgets.Button(
            name="💰 Current Quote",
            button_type="success",
            width=180
        )

        self.download_button = pn.widgets.Button(
            name="📥 Download Historical",
            button_type="light",
            width=180
        )

        # Progress and status
        self.progress_bar = pn.indicators.Progress(
            name="Operation Progress",
            value=0,
            width=400,
            bar_color="primary"
        )

        self.status_indicator = pn.pane.HTML(
            """<div style="padding: 10px; background: #e9ecef; border-radius: 5px;">
            <strong>Status:</strong> Ready to explore stocks
            </div>""",
            width=400
        )

        # Stock information display
        self.stock_info_panel = pn.pane.HTML(
            self._create_empty_stock_info(),
            width=400,
            height=300
        )

        # Price chart
        self.price_chart = pn.pane.Plotly(
            object=self._create_empty_chart(),
            height=400,
            sizing_mode='stretch_width'
        )

        # Stock screener table
        self.stock_table = pn.widgets.Tabulator(
            value=pd.DataFrame(),
            pagination='remote',
            page_size=15,
            height=300,
            sizing_mode='stretch_width'
        )

        # Market overview
        self.market_overview = pn.pane.HTML(
            self._create_market_overview(),
            width=400,
            height=200
        )

        # Setup callbacks
        self.stock_selector.param.watch(self._on_stock_change, 'value')
        self.category_filter.param.watch(self._on_category_change, 'value')
        self.fetch_button.on_click(self._fetch_stock_data)
        self.quote_button.on_click(self._get_current_quote)
        self.download_button.on_click(self._download_historical_data)

        # Load initial data
        self._load_stock_screener()

    def create_app(self):
        """Create the market explorer interface"""

        # Navigation bar
        navigation = create_navigation_bar(current_app='market_explorer')

        # Status indicator
        status = create_app_status_indicator()

        # Header
        header = pn.pane.HTML("""
        <div style="background: linear-gradient(90deg, #2E8B57, #3CB371); padding: 20px; color: white; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">📊 Market Explorer - US Stock Research</h2>
            <p style="margin: 5px 0 0 0;">Research stocks, analyze trends, and screen investment opportunities</p>
        </div>
        """, sizing_mode='stretch_width')

        # Control panel
        control_panel = pn.Column(
            "## 🎯 Stock Selection",
            self.category_filter,
            self.stock_selector,
            self.time_period,
            "## ⚡ Actions",
            pn.Row(self.quote_button, self.fetch_button),
            self.download_button,
            "## 📈 Market Overview",
            self.market_overview,
            width=400
        )

        # Analysis panel
        analysis_panel = pn.Column(
            "## 📊 Stock Analysis",
            self.progress_bar,
            self.status_indicator,
            self.price_chart,
            sizing_mode='stretch_width'
        )

        # Info panel
        info_panel = pn.Column(
            "## 📋 Stock Information",
            self.stock_info_panel,
            "## 🔍 Stock Screener",
            self.stock_table,
            width=400
        )

        # Main layout
        return pn.Column(
            navigation,
            status,
            header,
            pn.Row(
                control_panel,
                analysis_panel,
                info_panel,
                sizing_mode='stretch_width'
            ),
            sizing_mode='stretch_width'
        )

    def _get_stock_options(self):
        """Get available stock options from database"""
        try:
            stocks = shared_store.get_stocks_by_category()
            options = [(f"{row['symbol']} - {row['name']}", row['symbol']) for _, row in stocks.iterrows()]
            return options
        except Exception as e:
            return [("AAPL - Apple Inc.", "AAPL")]

    def _get_selected_symbol(self):
        """Get the actual symbol from stock selector (handles tuple values)"""
        value = self.stock_selector.value
        # If value is a tuple (label, symbol), return just the symbol
        if isinstance(value, tuple):
            return value[1]
        return value

    def _on_stock_change(self, event):
        """Handle stock selection change"""
        self._update_stock_info()

    def _on_category_change(self, event):
        """Handle category filter change"""
        self._load_stock_screener()
        # Update stock selector options
        if event.new == "All":
            stocks = shared_store.get_stocks_by_category()
        else:
            stocks = shared_store.get_stocks_by_category(event.new)

        options = [(f"{row['symbol']} - {row['name']}", row['symbol']) for _, row in stocks.iterrows()]
        self.stock_selector.options = options
        if options:
            self.stock_selector.value = options[0][1]

    async def _fetch_stock_data(self, event):
        """Fetch stock price data"""
        self.progress_bar.value = 0
        self.update_status("📊 Fetching stock data...", "info")

        try:
            symbol = self._get_selected_symbol()
            self.progress_bar.value = 25

            # Fetch stock data
            result = shared_store.fetch_stock_data(symbol, full_history=False)
            self.progress_bar.value = 75

            if result['success']:
                # Get price data from database
                price_data = shared_store.get_stock_prices(symbol)

                if not price_data.empty:
                    # Create chart
                    chart = self._create_stock_chart(symbol, price_data)
                    self.price_chart.object = chart

                    self.progress_bar.value = 100
                    self.update_status(f"✅ Loaded {len(price_data)} price records for {symbol}", "success")
                else:
                    self.update_status("⚠️ No price data available", "warning")
            else:
                self.update_status(f"❌ Error: {result.get('error', 'Unknown error')}", "error")

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Error: {str(e)}", "error")

    async def _get_current_quote(self, event):
        """Get current stock quote"""
        self.update_status("💰 Getting current quote...", "info")

        try:
            symbol = self._get_selected_symbol()
            quote = shared_store.get_current_quote(symbol)

            if quote['success']:
                price = quote['price']
                change = quote.get('change', 0)
                change_pct = quote.get('change_percent', '0%')

                self.update_status(f"✅ {symbol}: ${price:.2f} ({change_pct})", "success")
                self._update_stock_info(quote)
            else:
                self.update_status(f"❌ Quote error: {quote.get('error', 'Unknown error')}", "error")

        except Exception as e:
            self.update_status(f"❌ Quote error: {str(e)}", "error")

    async def _download_historical_data(self, event):
        """Download historical data for selected stock"""
        self.progress_bar.value = 0
        self.update_status("📥 Downloading historical data...", "info")

        try:
            symbol = self._get_selected_symbol()
            self.progress_bar.value = 20

            # Download full historical data
            result = shared_store.fetch_stock_data(symbol, full_history=True)
            self.progress_bar.value = 80

            if result['success']:
                data_count = len(result['data'])
                self.progress_bar.value = 100
                self.update_status(f"✅ Downloaded {data_count} historical records for {symbol}", "success")

                # Refresh chart with new data
                await self._fetch_stock_data(None)
            else:
                self.update_status(f"❌ Download error: {result.get('error', 'Unknown error')}", "error")

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Download error: {str(e)}", "error")

    def _create_stock_chart(self, symbol, price_data):
        """Create stock price chart"""
        try:
            # Filter by time period
            end_date = datetime.now()
            if self.time_period.value == "1M":
                start_date = end_date - timedelta(days=30)
            elif self.time_period.value == "3M":
                start_date = end_date - timedelta(days=90)
            elif self.time_period.value == "6M":
                start_date = end_date - timedelta(days=180)
            elif self.time_period.value == "1Y":
                start_date = end_date - timedelta(days=365)
            elif self.time_period.value == "2Y":
                start_date = end_date - timedelta(days=730)
            elif self.time_period.value == "5Y":
                start_date = end_date - timedelta(days=1825)
            else:  # MAX
                start_date = None

            if start_date:
                filtered_data = price_data[price_data['date'] >= start_date.strftime('%Y-%m-%d')]
            else:
                filtered_data = price_data

            if filtered_data.empty:
                return self._create_empty_chart()

            # Create candlestick chart
            fig = go.Figure(data=go.Candlestick(
                x=pd.to_datetime(filtered_data['date']),
                open=filtered_data['open_price'],
                high=filtered_data['high_price'],
                low=filtered_data['low_price'],
                close=filtered_data['close_price'],
                name=symbol
            ))

            fig.update_layout(
                title=f"{symbol} Stock Price - {self.time_period.value}",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                height=400,
                template='plotly_white',
                showlegend=False
            )

            return fig

        except Exception as e:
            return self._create_empty_chart()

    def _create_empty_chart(self):
        """Create empty chart placeholder"""
        fig = go.Figure()
        fig.add_annotation(
            text="Select a stock and click 'Get Stock Data' to view chart",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Stock Price Chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=400,
            template='plotly_white'
        )
        return fig

    def _update_stock_info(self, quote_data=None):
        """Update stock information panel"""
        try:
            symbol = self._get_selected_symbol()
            stocks = shared_store.get_stocks_by_category()
            stock_info = stocks[stocks['symbol'] == symbol].iloc[0]

            info_html = f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: 'Arial', sans-serif;">
                <h4 style="margin-top: 0; color: #495057;">{symbol} - {stock_info['name']}</h4>
                <table style="width: 100%; font-size: 14px;">
                    <tr><td><strong>Sector:</strong></td><td>{stock_info.get('sector', 'N/A')}</td></tr>
                    <tr><td><strong>Category:</strong></td><td>{stock_info.get('category', 'N/A').title()}</td></tr>
                    <tr><td><strong>Market Cap:</strong></td><td>${stock_info.get('market_cap', 0):,.0f}</td></tr>
                    <tr><td><strong>P/E Ratio:</strong></td><td>{stock_info.get('pe_ratio', 'N/A')}</td></tr>
                    <tr><td><strong>Dividend Yield:</strong></td><td>{stock_info.get('dividend_yield', 0):.2f}%</td></tr>
            """

            if quote_data and quote_data.get('success'):
                info_html += f"""
                    <tr style="border-top: 1px solid #dee2e6;"><td><strong>Current Price:</strong></td><td>${quote_data['price']:.2f}</td></tr>
                    <tr><td><strong>Change:</strong></td><td>{quote_data.get('change_percent', 'N/A')}</td></tr>
                    <tr><td><strong>Volume:</strong></td><td>{quote_data.get('volume', 0):,}</td></tr>
                """

            info_html += """
                </table>
            </div>
            """

            self.stock_info_panel.object = info_html

        except Exception as e:
            self.stock_info_panel.object = self._create_empty_stock_info()

    def _create_empty_stock_info(self):
        """Create empty stock info panel"""
        return """
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h4 style="margin-top: 0;">Stock Information</h4>
            <p style="color: #666; margin: 0;">Select a stock to view detailed information</p>
        </div>
        """

    def _load_stock_screener(self):
        """Load stock screener data"""
        try:
            category = self.category_filter.value
            if category == "All":
                stocks = shared_store.get_stocks_by_category()
            else:
                stocks = shared_store.get_stocks_by_category(category)

            # Format for display
            display_data = stocks[['symbol', 'name', 'sector', 'category', 'market_cap', 'pe_ratio', 'dividend_yield']].copy()
            display_data.columns = ['Symbol', 'Company', 'Sector', 'Category', 'Market Cap', 'P/E Ratio', 'Div Yield %']
            display_data['Market Cap'] = display_data['Market Cap'].apply(lambda x: f"${x/1e9:.1f}B" if pd.notna(x) and x > 0 else "N/A")
            display_data['Category'] = display_data['Category'].str.title()

            self.stock_table.value = display_data

        except Exception as e:
            self.stock_table.value = pd.DataFrame(columns=['Symbol', 'Company', 'Sector', 'Category', 'Market Cap', 'P/E Ratio', 'Div Yield %'])

    def _create_market_overview(self):
        """Create market overview panel"""
        try:
            status = shared_store.get_status()
            return f"""
            <div style="background: #e8f5e8; padding: 10px; border-radius: 5px; border: 1px solid #c3e6c3;">
                <h5 style="margin-top: 0; color: #155724;">📈 Market Overview</h5>
                <div style="font-size: 12px;">
                    <strong>Stocks Available:</strong> {status['stock_count']}<br>
                    <strong>Price Records:</strong> {status['price_records']:,}<br>
                    <strong>Data Range:</strong> {status['price_data_range']}<br>
                    <strong>Last Updated:</strong> {status['last_updated'][:19] if status['last_updated'] else 'Unknown'}
                </div>
            </div>
            """
        except:
            return """
            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
                <h5 style="margin-top: 0;">📈 Market Overview</h5>
                <p style="margin: 0; font-size: 12px;">Loading market data...</p>
            </div>
            """

    def update_status(self, message, status_type="info"):
        """Update status indicator with color coding"""
        colors = {
            "info": "#007bff",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545"
        }

        self.status_indicator.object = f"""
        <div style="padding: 10px; background: {colors.get(status_type, '#e9ecef')}; color: white; border-radius: 5px;">
            <strong>Status:</strong> {message}
        </div>
        """

# Backward compatibility alias
DataFetcherApp = MarketExplorerApp