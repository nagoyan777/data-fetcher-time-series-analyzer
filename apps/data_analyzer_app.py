"""
Stock Analyzer App - Advanced Charts & Technical Analysis
Interactive stock visualization with technical indicators and comparative analysis
"""
import panel as pn
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_store import shared_store
from utils.navigation import create_navigation_bar, create_quick_actions_panel, create_app_status_indicator

class StockAnalyzerApp:
    """Advanced stock chart analysis with technical indicators"""

    def __init__(self):
        # Stock selection
        stock_options = self._get_stock_options()
        self.stock_selector = pn.widgets.Select(
            name="Primary Stock",
            options=stock_options,
            value=stock_options[0][1] if stock_options else "AAPL",  # Use the value part
            width=200
        )

        self.comparison_stock = pn.widgets.Select(
            name="Compare With",
            options=[("None", "")] + stock_options,
            value="",
            width=200
        )

        # Chart type selection
        self.chart_type = pn.widgets.RadioButtonGroup(
            name="Chart Type",
            options=["Candlestick", "Line", "OHLC"],
            value="Candlestick",
            button_type="primary"
        )

        # Time period
        self.time_period = pn.widgets.Select(
            name="Time Period",
            options=["1M", "3M", "6M", "1Y", "2Y", "5Y", "MAX"],
            value="1Y",
            width=150
        )

        # Technical indicators
        self.show_volume = pn.widgets.Checkbox(
            name="Show Volume",
            value=True
        )

        self.show_sma = pn.widgets.Checkbox(
            name="Simple Moving Averages",
            value=False
        )

        self.sma_periods = pn.widgets.MultiSelect(
            name="SMA Periods",
            options=[20, 50, 100, 200],
            value=[20, 50],
            size=4,
            width=150
        )

        self.show_bollinger = pn.widgets.Checkbox(
            name="Bollinger Bands",
            value=False
        )

        self.show_rsi = pn.widgets.Checkbox(
            name="RSI (14)",
            value=False
        )

        # Y-axis controls
        self.y_scale_toggle = pn.widgets.RadioButtonGroup(
            name='Y-Axis Scale',
            options=['Linear', 'Log'],
            value='Linear',
            button_type='light'
        )

        # Analysis controls
        self.normalize_prices = pn.widgets.Checkbox(
            name="Normalize to 100",
            value=False
        )

        self.show_returns = pn.widgets.Checkbox(
            name="Show % Returns",
            value=False
        )

        # Action buttons
        self.analyze_button = pn.widgets.Button(
            name="📊 Analyze Stock",
            button_type="primary",
            width=180
        )

        self.compare_button = pn.widgets.Button(
            name="📈 Compare Stocks",
            button_type="success",
            width=180
        )

        self.refresh_button = pn.widgets.Button(
            name="🔄 Refresh Data",
            button_type="light",
            width=180
        )

        # Status and progress
        self.status_indicator = pn.pane.HTML(
            """<div style="padding: 10px; background: #e9ecef; border-radius: 5px;">
            <strong>Status:</strong> Ready to analyze stocks
            </div>""",
            width=400
        )

        # Main stock chart
        self.main_chart = pn.pane.Plotly(
            object=self._create_empty_chart(),
            height=500,
            sizing_mode='stretch_width'
        )

        # Volume chart
        self.volume_chart = pn.pane.Plotly(
            object=self._create_empty_volume_chart(),
            height=200,
            sizing_mode='stretch_width'
        )

        # Technical indicators chart
        self.indicators_chart = pn.pane.Plotly(
            object=self._create_empty_indicators_chart(),
            height=200,
            sizing_mode='stretch_width'
        )

        # Statistics panel
        self.stats_panel = pn.pane.HTML(
            self._create_empty_stats(),
            width=400,
            height=400
        )

        # Performance comparison table
        self.comparison_table = pn.widgets.Tabulator(
            value=pd.DataFrame(),
            pagination='remote',
            page_size=10,
            height=250,
            sizing_mode='stretch_width'
        )

        # Setup callbacks
        self.stock_selector.param.watch(self._on_stock_change, 'value')
        self.chart_type.param.watch(self._update_charts, 'value')
        self.time_period.param.watch(self._update_charts, 'value')
        self.y_scale_toggle.param.watch(self._update_charts, 'value')

        # Technical indicator callbacks
        for widget in [self.show_volume, self.show_sma, self.show_bollinger,
                      self.show_rsi, self.normalize_prices, self.show_returns]:
            widget.param.watch(self._update_charts, 'value')

        self.sma_periods.param.watch(self._update_charts, 'value')

        self.analyze_button.on_click(self._analyze_stock)
        self.compare_button.on_click(self._compare_stocks)
        self.refresh_button.on_click(self._refresh_data)

        # Don't load initial data - wait for user to click analyze
        # self._load_initial_data()

    def create_app(self):
        """Create the stock analyzer interface"""

        # Navigation bar
        navigation = create_navigation_bar(current_app='stock_analyzer')

        # Status indicator
        status = create_app_status_indicator()

        # Header
        header = pn.pane.HTML("""
        <div style="background: linear-gradient(90deg, #FF6B35, #F7931E); padding: 20px; color: white; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">📈 Stock Analyzer - Advanced Charts & Technical Analysis</h2>
            <p style="margin: 5px 0 0 0;">Interactive candlestick charts, technical indicators, and comparative analysis</p>
        </div>
        """, sizing_mode='stretch_width')

        # Control panel
        control_panel = pn.Column(
            "## 🎯 Stock Selection",
            self.stock_selector,
            self.comparison_stock,
            self.time_period,
            "## 📊 Chart Settings",
            self.chart_type,
            self.y_scale_toggle,
            self.normalize_prices,
            self.show_returns,
            "## 🔧 Technical Indicators",
            self.show_volume,
            self.show_sma,
            self.sma_periods,
            self.show_bollinger,
            self.show_rsi,
            "## ⚡ Actions",
            self.analyze_button,
            self.compare_button,
            self.refresh_button,
            width=300
        )

        # Chart panel
        chart_panel = pn.Column(
            "## 📊 Price Chart",
            self.main_chart,
            "## 📊 Volume",
            self.volume_chart,
            "## 📊 Technical Indicators",
            self.indicators_chart,
            sizing_mode='stretch_width'
        )

        # Analysis panel
        analysis_panel = pn.Column(
            "## 📈 Stock Statistics",
            self.status_indicator,
            self.stats_panel,
            "## 📊 Performance Comparison",
            self.comparison_table,
            width=400
        )

        # Main layout
        return pn.Column(
            navigation,
            status,
            header,
            pn.Row(
                control_panel,
                chart_panel,
                analysis_panel,
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

    def _get_comparison_symbol(self):
        """Get the actual symbol from comparison selector (handles tuple values)"""
        value = self.comparison_stock.value
        # If value is a tuple (label, symbol), return just the symbol
        if isinstance(value, tuple):
            return value[1]
        return value

    def _on_stock_change(self, event):
        """Handle stock selection change"""
        self._load_stock_data()

    async def _analyze_stock(self, event):
        """Analyze selected stock"""
        self.update_status("📊 Analyzing stock data...", "info")

        try:
            symbol = self._get_selected_symbol()

            # Ensure we have data
            result = shared_store.fetch_stock_data(symbol, full_history=False)

            if result['success']:
                self._load_stock_data()
                self.update_status(f"✅ Analysis complete for {symbol}", "success")
            else:
                self.update_status(f"❌ Error: {result.get('error', 'Unknown error')}", "error")

        except Exception as e:
            self.update_status(f"❌ Analysis error: {str(e)}", "error")

    async def _compare_stocks(self, event):
        """Compare two stocks"""
        if not self._get_comparison_symbol():
            self.update_status("❌ Please select a comparison stock", "warning")
            return

        self.update_status("📈 Comparing stocks...", "info")

        try:
            primary = self._get_selected_symbol()
            comparison = self._get_comparison_symbol()

            # Fetch data for both stocks
            for symbol in [primary, comparison]:
                result = shared_store.fetch_stock_data(symbol, full_history=False)
                if not result['success']:
                    self.update_status(f"❌ Error fetching {symbol}: {result.get('error')}", "error")
                    return

            # Update charts with comparison
            self._update_charts()
            self._update_comparison_table()

            self.update_status(f"✅ Comparison complete: {primary} vs {comparison}", "success")

        except Exception as e:
            self.update_status(f"❌ Comparison error: {str(e)}", "error")

    async def _refresh_data(self, event):
        """Refresh stock data"""
        self.update_status("🔄 Refreshing data...", "info")

        try:
            symbol = self._get_selected_symbol()
            result = shared_store.fetch_stock_data(symbol, full_history=True)

            if result['success']:
                self._load_stock_data()
                self.update_status(f"✅ Data refreshed for {symbol}", "success")
            else:
                self.update_status(f"❌ Refresh error: {result.get('error')}", "error")

        except Exception as e:
            self.update_status(f"❌ Refresh error: {str(e)}", "error")

    def _load_initial_data(self):
        """Load initial stock data"""
        self._load_stock_data()

    def _load_stock_data(self):
        """Load and process stock data"""
        try:
            symbol = self._get_selected_symbol()
            print(f"📊 Loading data for symbol: {symbol}")
            price_data = shared_store.get_stock_prices(symbol)

            if not price_data.empty:
                print(f"✅ Loaded {len(price_data)} records for {symbol}")
                self.current_data = price_data
                self._update_charts()
                self._update_statistics()
            else:
                print(f"⚠️ No data found for {symbol}")
                self.current_data = pd.DataFrame()
                self._show_no_data_charts()

        except Exception as e:
            print(f"❌ Error loading stock data: {e}")
            self.current_data = pd.DataFrame()
            self._show_no_data_charts()

    def _update_charts(self, event=None):
        """Update all charts"""
        if hasattr(self, 'current_data') and not self.current_data.empty:
            self._update_main_chart()
            self._update_volume_chart()
            self._update_indicators_chart()
        else:
            self._show_no_data_charts()

    def _update_main_chart(self):
        """Update main price chart"""
        try:
            data = self._filter_data_by_period(self.current_data)

            if data.empty:
                self.main_chart.object = self._create_empty_chart()
                return

            # Create base chart
            if self.chart_type.value == "Candlestick":
                fig = go.Figure(data=go.Candlestick(
                    x=pd.to_datetime(data['date']),
                    open=data['open_price'],
                    high=data['high_price'],
                    low=data['low_price'],
                    close=data['close_price'],
                    name=self._get_selected_symbol()
                ))
            elif self.chart_type.value == "Line":
                fig = go.Figure(data=go.Scatter(
                    x=pd.to_datetime(data['date']),
                    y=data['close_price'],
                    mode='lines',
                    name=self._get_selected_symbol(),
                    line=dict(width=2)
                ))
            else:  # OHLC
                fig = go.Figure(data=go.Ohlc(
                    x=pd.to_datetime(data['date']),
                    open=data['open_price'],
                    high=data['high_price'],
                    low=data['low_price'],
                    close=data['close_price'],
                    name=self._get_selected_symbol()
                ))

            # Add comparison stock if selected
            if self._get_comparison_symbol():
                comp_data = shared_store.get_stock_prices(self._get_comparison_symbol())
                if not comp_data.empty:
                    comp_data = self._filter_data_by_period(comp_data)

                    if self.normalize_prices.value:
                        # Normalize both to 100
                        data_norm = (data['close_price'] / data['close_price'].iloc[0]) * 100
                        comp_norm = (comp_data['close_price'] / comp_data['close_price'].iloc[0]) * 100

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=pd.to_datetime(data['date']),
                            y=data_norm,
                            mode='lines',
                            name=self._get_selected_symbol(),
                            line=dict(width=2)
                        ))
                        fig.add_trace(go.Scatter(
                            x=pd.to_datetime(comp_data['date']),
                            y=comp_norm,
                            mode='lines',
                            name=self._get_comparison_symbol(),
                            line=dict(width=2, dash='dash')
                        ))
                    else:
                        fig.add_trace(go.Scatter(
                            x=pd.to_datetime(comp_data['date']),
                            y=comp_data['close_price'],
                            mode='lines',
                            name=self._get_comparison_symbol(),
                            line=dict(width=2, dash='dash'),
                            yaxis='y2'
                        ))

            # Add moving averages
            if self.show_sma.value and self.sma_periods.value:
                for period in self.sma_periods.value:
                    sma = data['close_price'].rolling(window=period).mean()
                    fig.add_trace(go.Scatter(
                        x=pd.to_datetime(data['date']),
                        y=sma,
                        mode='lines',
                        name=f'SMA {period}',
                        line=dict(width=1),
                        opacity=0.7
                    ))

            # Add Bollinger Bands
            if self.show_bollinger.value:
                sma_20 = data['close_price'].rolling(window=20).mean()
                std_20 = data['close_price'].rolling(window=20).std()
                upper_band = sma_20 + (std_20 * 2)
                lower_band = sma_20 - (std_20 * 2)

                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(data['date']),
                    y=upper_band,
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='rgba(255,0,0,0.3)', width=1)
                ))
                fig.add_trace(go.Scatter(
                    x=pd.to_datetime(data['date']),
                    y=lower_band,
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='rgba(255,0,0,0.3)', width=1),
                    fill='tonexty'
                ))

            # Configure layout
            layout_updates = {
                'title': f"{self._get_selected_symbol()} - {self.chart_type.value} Chart ({self.time_period.value})",
                'xaxis_title': "Date",
                'yaxis_title': "Price (USD)",
                'height': 500,
                'template': 'plotly_white',
                'xaxis_rangeslider_visible': False
            }

            if self.y_scale_toggle.value == 'Log':
                layout_updates['yaxis_type'] = 'log'

            if self._get_comparison_symbol() and not self.normalize_prices.value:
                layout_updates['yaxis2'] = dict(
                    title=f"{self._get_comparison_symbol()} Price",
                    overlaying='y',
                    side='right'
                )

            fig.update_layout(**layout_updates)
            self.main_chart.object = fig

        except Exception as e:
            print(f"❌ Error creating main chart: {e}")
            import traceback
            traceback.print_exc()
            self.main_chart.object = self._create_empty_chart()

    def _update_volume_chart(self):
        """Update volume chart"""
        if not self.show_volume.value:
            self.volume_chart.object = self._create_empty_volume_chart()
            return

        try:
            data = self._filter_data_by_period(self.current_data)

            if data.empty:
                self.volume_chart.object = self._create_empty_volume_chart()
                return

            fig = go.Figure(data=go.Bar(
                x=pd.to_datetime(data['date']),
                y=data['volume'],
                name='Volume',
                marker_color='rgba(0,100,200,0.6)'
            ))

            fig.update_layout(
                title=f"{self.stock_selector.value} - Volume",
                xaxis_title="Date",
                yaxis_title="Volume",
                height=200,
                template='plotly_white',
                showlegend=False
            )

            self.volume_chart.object = fig

        except Exception as e:
            self.volume_chart.object = self._create_empty_volume_chart()

    def _update_indicators_chart(self):
        """Update technical indicators chart"""
        if not self.show_rsi.value:
            self.indicators_chart.object = self._create_empty_indicators_chart()
            return

        try:
            data = self._filter_data_by_period(self.current_data)

            if data.empty or len(data) < 14:
                self.indicators_chart.object = self._create_empty_indicators_chart()
                return

            # Calculate RSI
            rsi = self._calculate_rsi(data['close_price'], 14)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pd.to_datetime(data['date']),
                y=rsi,
                mode='lines',
                name='RSI (14)',
                line=dict(color='purple', width=2)
            ))

            # Add RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5)
            fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.3)

            fig.update_layout(
                title=f"{self.stock_selector.value} - RSI (14)",
                xaxis_title="Date",
                yaxis_title="RSI",
                yaxis_range=[0, 100],
                height=200,
                template='plotly_white'
            )

            self.indicators_chart.object = fig

        except Exception as e:
            self.indicators_chart.object = self._create_empty_indicators_chart()

    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _filter_data_by_period(self, data):
        """Filter data by selected time period"""
        if data.empty:
            return data

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
            return data

        return data[data['date'] >= start_date.strftime('%Y-%m-%d')]

    def _update_statistics(self):
        """Update statistics panel"""
        try:
            data = self._filter_data_by_period(self.current_data)

            if data.empty:
                self.stats_panel.object = self._create_empty_stats()
                return

            # Calculate statistics
            latest_price = data['close_price'].iloc[-1]
            period_return = ((latest_price - data['close_price'].iloc[0]) / data['close_price'].iloc[0]) * 100
            volatility = data['close_price'].pct_change().std() * np.sqrt(252) * 100  # Annualized

            high_52w = data['high_price'].max()
            low_52w = data['low_price'].min()
            avg_volume = data['volume'].mean()

            stats_html = f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: 'Arial', sans-serif;">
                <h4 style="margin-top: 0; color: #495057;">{self.stock_selector.value} Statistics</h4>
                <table style="width: 100%; font-size: 14px;">
                    <tr><td><strong>Latest Price:</strong></td><td>${latest_price:.2f}</td></tr>
                    <tr><td><strong>Period Return:</strong></td><td style="color: {'green' if period_return >= 0 else 'red'}">{period_return:.2f}%</td></tr>
                    <tr><td><strong>Volatility (Ann.):</strong></td><td>{volatility:.2f}%</td></tr>
                    <tr><td><strong>52W High:</strong></td><td>${high_52w:.2f}</td></tr>
                    <tr><td><strong>52W Low:</strong></td><td>${low_52w:.2f}</td></tr>
                    <tr><td><strong>Avg Volume:</strong></td><td>{avg_volume:,.0f}</td></tr>
                    <tr><td><strong>Data Points:</strong></td><td>{len(data)}</td></tr>
                    <tr><td><strong>Period:</strong></td><td>{self.time_period.value}</td></tr>
                </table>
            </div>
            """

            self.stats_panel.object = stats_html

        except Exception as e:
            self.stats_panel.object = self._create_empty_stats()

    def _update_comparison_table(self):
        """Update performance comparison table"""
        try:
            if not self._get_comparison_symbol():
                self.comparison_table.value = pd.DataFrame()
                return

            primary_data = self._filter_data_by_period(self.current_data)
            comp_data = shared_store.get_stock_prices(self._get_comparison_symbol())
            comp_data = self._filter_data_by_period(comp_data)

            if primary_data.empty or comp_data.empty:
                return

            # Calculate comparison metrics
            primary_return = ((primary_data['close_price'].iloc[-1] - primary_data['close_price'].iloc[0]) / primary_data['close_price'].iloc[0]) * 100
            comp_return = ((comp_data['close_price'].iloc[-1] - comp_data['close_price'].iloc[0]) / comp_data['close_price'].iloc[0]) * 100

            primary_vol = primary_data['close_price'].pct_change().std() * np.sqrt(252) * 100
            comp_vol = comp_data['close_price'].pct_change().std() * np.sqrt(252) * 100

            comparison_df = pd.DataFrame({
                'Metric': ['Return (%)', 'Volatility (%)', 'Max Price', 'Min Price', 'Avg Volume'],
                self.stock_selector.value: [
                    f"{primary_return:.2f}%",
                    f"{primary_vol:.2f}%",
                    f"${primary_data['high_price'].max():.2f}",
                    f"${primary_data['low_price'].min():.2f}",
                    f"{primary_data['volume'].mean():,.0f}"
                ],
                self._get_comparison_symbol(): [
                    f"{comp_return:.2f}%",
                    f"{comp_vol:.2f}%",
                    f"${comp_data['high_price'].max():.2f}",
                    f"${comp_data['low_price'].min():.2f}",
                    f"{comp_data['volume'].mean():,.0f}"
                ]
            })

            self.comparison_table.value = comparison_df

        except Exception as e:
            self.comparison_table.value = pd.DataFrame()

    def _show_no_data_charts(self):
        """Show empty charts when no data available"""
        self.main_chart.object = self._create_empty_chart()
        self.volume_chart.object = self._create_empty_volume_chart()
        self.indicators_chart.object = self._create_empty_indicators_chart()
        self.stats_panel.object = self._create_empty_stats()

    def _create_empty_chart(self):
        """Create empty main chart"""
        fig = go.Figure()
        fig.add_annotation(
            text="Select a stock and click 'Analyze Stock' to view chart",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Stock Price Chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            template='plotly_white'
        )
        return fig

    def _create_empty_volume_chart(self):
        """Create empty volume chart"""
        fig = go.Figure()
        fig.add_annotation(
            text="Volume chart will appear here",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Volume",
            xaxis_title="Date",
            yaxis_title="Volume",
            height=200,
            template='plotly_white'
        )
        return fig

    def _create_empty_indicators_chart(self):
        """Create empty indicators chart"""
        fig = go.Figure()
        fig.add_annotation(
            text="Technical indicators will appear here",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            title="Technical Indicators",
            xaxis_title="Date",
            yaxis_title="Value",
            height=200,
            template='plotly_white'
        )
        return fig

    def _create_empty_stats(self):
        """Create empty statistics panel"""
        return """
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h4 style="margin-top: 0;">Stock Statistics</h4>
            <p style="color: #666; margin: 0;">Select a stock and analyze to view statistics</p>
        </div>
        """

    def update_status(self, message, status_type="info"):
        """Update status indicator"""
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
DataAnalyzerApp = StockAnalyzerApp