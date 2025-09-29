"""
Portfolio Tracker App - SBI Securities Integration & P&L Analysis
Import SBI transactions, track portfolio performance, and analyze investments
"""
import panel as pn
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
import io
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_store import shared_store
from utils.navigation import create_navigation_bar, create_quick_actions_panel, create_app_status_indicator

class PortfolioTrackerApp:
    """SBI Securities portfolio tracking and P&L analysis"""

    def __init__(self):
        # File upload for SBI CSV
        self.file_input = pn.widgets.FileInput(
            accept='.csv',
            multiple=False,
            name="Upload SBI CSV File",
            width=300
        )

        # Currency display toggle
        self.currency_display = pn.widgets.RadioButtonGroup(
            name="Display Currency",
            options=["USD", "JPY", "Both"],
            value="USD",
            button_type="primary"
        )

        # Action buttons
        self.import_button = pn.widgets.Button(
            name="📥 Import Transactions",
            button_type="primary",
            width=200
        )

        self.refresh_button = pn.widgets.Button(
            name="🔄 Refresh Portfolio",
            button_type="success",
            width=200
        )

        self.export_button = pn.widgets.Button(
            name="📊 Export Report",
            button_type="light",
            width=200
        )

        # Progress and status
        self.progress_bar = pn.indicators.Progress(
            name="Operation Progress",
            value=0,
            width=400,
            bar_color="success"
        )

        self.status_indicator = pn.pane.HTML(
            """<div style="padding: 10px; background: #e9ecef; border-radius: 5px;">
            <strong>Status:</strong> Ready to import SBI transactions
            </div>""",
            width=400
        )

        # Portfolio overview
        self.portfolio_overview = pn.pane.HTML(
            self._create_empty_overview(),
            width=400,
            height=300
        )

        # Holdings table
        self.holdings_table = pn.widgets.Tabulator(
            value=pd.DataFrame(),
            pagination='remote',
            page_size=10,
            height=300,
            sizing_mode='stretch_width'
        )

        # Transactions table
        self.transactions_table = pn.widgets.Tabulator(
            value=pd.DataFrame(),
            pagination='remote',
            page_size=15,
            height=300,
            sizing_mode='stretch_width'
        )

        # Portfolio allocation chart
        self.allocation_chart = pn.pane.Plotly(
            object=self._create_empty_chart("Portfolio Allocation"),
            height=400,
            width=500
        )

        # Performance chart
        self.performance_chart = pn.pane.Plotly(
            object=self._create_empty_chart("Portfolio Performance"),
            height=400,
            sizing_mode='stretch_width'
        )

        # Exchange rate info
        self.exchange_rate_info = pn.pane.HTML(
            self._create_exchange_rate_info(),
            width=400,
            height=100
        )

        # Setup callbacks
        self.import_button.on_click(self._import_sbi_transactions)
        self.refresh_button.on_click(self._refresh_portfolio)
        self.export_button.on_click(self._export_portfolio_report)
        self.currency_display.param.watch(self._on_currency_change, 'value')

        # Load initial data
        self._load_portfolio_data()

    def create_app(self):
        """Create the portfolio tracker interface"""

        # Navigation bar
        navigation = create_navigation_bar(current_app='portfolio_tracker')

        # Status indicator
        status = create_app_status_indicator()

        # Header
        header = pn.pane.HTML("""
        <div style="background: linear-gradient(90deg, #6A5ACD, #9370DB); padding: 20px; color: white; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">💼 Portfolio Tracker - SBI Investment Analysis</h2>
            <p style="margin: 5px 0 0 0;">Import SBI transactions, track P&L, and analyze portfolio performance</p>
        </div>
        """, sizing_mode='stretch_width')

        # Import panel
        import_panel = pn.Column(
            "## 📥 Import SBI Data",
            self.file_input,
            self.import_button,
            "## ⚙️ Settings",
            self.currency_display,
            "## ⚡ Actions",
            pn.Row(self.refresh_button, self.export_button),
            "## 💱 Exchange Rate",
            self.exchange_rate_info,
            width=400
        )

        # Overview panel
        overview_panel = pn.Column(
            "## 📊 Portfolio Overview",
            self.progress_bar,
            self.status_indicator,
            self.portfolio_overview,
            self.allocation_chart,
            width=500
        )

        # Holdings panel
        holdings_panel = pn.Column(
            "## 📋 Current Holdings",
            self.holdings_table,
            "## 📈 Performance Analysis",
            self.performance_chart,
            sizing_mode='stretch_width'
        )

        # Transactions panel
        transactions_panel = pn.Column(
            "## 📝 Transaction History",
            self.transactions_table,
            sizing_mode='stretch_width'
        )

        # Main layout with tabs
        tabs = pn.Tabs(
            ("Portfolio Overview", pn.Row(import_panel, overview_panel, holdings_panel, sizing_mode='stretch_width')),
            ("Transaction History", transactions_panel),
            dynamic=True,
            sizing_mode='stretch_width'
        )

        return pn.Column(
            navigation,
            status,
            header,
            tabs,
            sizing_mode='stretch_width'
        )

    async def _import_sbi_transactions(self, event):
        """Import SBI CSV transactions"""
        if not self.file_input.value:
            self.update_status("❌ Please select a CSV file first", "error")
            return

        self.progress_bar.value = 0
        self.update_status("📥 Importing SBI transactions...", "info")

        try:
            # Get file data
            file_data = self.file_input.value
            self.progress_bar.value = 25

            # Save file temporarily
            temp_file = f"/tmp/sbi_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(temp_file, 'wb') as f:
                f.write(file_data)

            self.progress_bar.value = 50

            # Import using shared store
            result = shared_store.import_sbi_csv(temp_file)
            self.progress_bar.value = 75

            if result['success']:
                self.progress_bar.value = 100
                self.update_status(
                    f"✅ Imported {result['saved_transactions']}/{result['total_transactions']} transactions",
                    "success"
                )

                # Refresh portfolio data
                await self._refresh_portfolio(None)
            else:
                self.update_status(f"❌ Import error: {result.get('error', 'Unknown error')}", "error")

            # Clean up temp file
            os.unlink(temp_file)

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Import error: {str(e)}", "error")

    async def _refresh_portfolio(self, event):
        """Refresh portfolio data and calculations"""
        self.progress_bar.value = 0
        self.update_status("🔄 Refreshing portfolio data...", "info")

        try:
            self.progress_bar.value = 25

            # Update exchange rates
            shared_store.update_exchange_rates()
            self.progress_bar.value = 50

            # Load portfolio data
            self._load_portfolio_data()
            self.progress_bar.value = 75

            # Update charts
            self._update_charts()
            self.progress_bar.value = 100

            self.update_status("✅ Portfolio data refreshed successfully", "success")

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Refresh error: {str(e)}", "error")

    async def _export_portfolio_report(self, event):
        """Export portfolio report"""
        self.update_status("📊 Generating portfolio report...", "info")

        try:
            report_path = shared_store.export_portfolio_report()

            if report_path:
                self.update_status(f"✅ Report exported: {report_path}", "success")
            else:
                self.update_status("❌ Export failed", "error")

        except Exception as e:
            self.update_status(f"❌ Export error: {str(e)}", "error")

    def _on_currency_change(self, event):
        """Handle currency display change"""
        self._load_portfolio_data()
        self._update_charts()

    def _load_portfolio_data(self):
        """Load and display portfolio data"""
        try:
            # Load holdings
            holdings = shared_store.get_portfolio_summary()

            if not holdings.empty:
                # Format holdings for display
                display_holdings = holdings.copy()

                if self.currency_display.value == "USD":
                    display_holdings = display_holdings[['symbol', 'name', 'total_shares', 'avg_cost_usd', 'total_invested_usd']]
                    display_holdings.columns = ['Symbol', 'Company', 'Shares', 'Avg Cost', 'Total Invested']
                elif self.currency_display.value == "JPY":
                    # Convert to JPY (would need current prices)
                    pass  # Implement JPY display
                else:  # Both
                    pass  # Implement both currencies

                self.holdings_table.value = display_holdings

                # Update overview
                self._update_portfolio_overview(holdings)
            else:
                self.holdings_table.value = pd.DataFrame(columns=['Symbol', 'Company', 'Shares', 'Avg Cost', 'Total Invested'])

            # Load transactions
            transactions = shared_store.get_portfolio_transactions()

            if not transactions.empty:
                # Format transactions for display
                display_transactions = transactions[['date', 'symbol', 'action', 'quantity', 'price_usd', 'total_usd']].copy()
                display_transactions.columns = ['Date', 'Symbol', 'Action', 'Quantity', 'Price USD', 'Total USD']
                display_transactions = display_transactions.sort_values('Date', ascending=False)
                self.transactions_table.value = display_transactions
            else:
                self.transactions_table.value = pd.DataFrame(columns=['Date', 'Symbol', 'Action', 'Quantity', 'Price USD', 'Total USD'])

        except Exception as e:
            print(f"Error loading portfolio data: {e}")

    def _update_portfolio_overview(self, holdings):
        """Update portfolio overview panel"""
        try:
            # Calculate portfolio performance
            performance = shared_store.calculate_portfolio_performance()

            if performance['success']:
                total_invested = performance['total_invested_usd']
                current_value = performance['current_value_usd']
                total_return = performance['total_return_pct']
                unrealized_pnl = performance['unrealized_pnl_usd']

                overview_html = f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: 'Arial', sans-serif;">
                    <h4 style="margin-top: 0; color: #495057;">Portfolio Summary</h4>
                    <table style="width: 100%; font-size: 14px;">
                        <tr><td><strong>Total Invested:</strong></td><td>${total_invested:,.2f}</td></tr>
                        <tr><td><strong>Current Value:</strong></td><td>${current_value:,.2f}</td></tr>
                        <tr><td><strong>Unrealized P&L:</strong></td><td style="color: {'green' if unrealized_pnl >= 0 else 'red'}">${unrealized_pnl:,.2f}</td></tr>
                        <tr><td><strong>Total Return:</strong></td><td style="color: {'green' if total_return >= 0 else 'red'}">{total_return:.2f}%</td></tr>
                        <tr><td><strong>Holdings:</strong></td><td>{len(holdings)} stocks</td></tr>
                        <tr><td><strong>Last Updated:</strong></td><td>{performance['last_updated'][:19]}</td></tr>
                    </table>
                </div>
                """
            else:
                overview_html = f"""
                <div style="background: #f8d7da; padding: 15px; border-radius: 5px; color: #721c24;">
                    <h4 style="margin-top: 0;">Portfolio Summary</h4>
                    <p>Error calculating performance: {performance.get('error', 'Unknown error')}</p>
                </div>
                """

            self.portfolio_overview.object = overview_html

        except Exception as e:
            self.portfolio_overview.object = self._create_empty_overview()

    def _update_charts(self):
        """Update portfolio charts"""
        try:
            holdings = shared_store.get_portfolio_summary()

            if not holdings.empty:
                # Create allocation pie chart
                allocation_fig = px.pie(
                    holdings,
                    values='total_invested_usd',
                    names='symbol',
                    title="Portfolio Allocation by Investment"
                )
                allocation_fig.update_layout(height=400)
                self.allocation_chart.object = allocation_fig

                # Create performance chart (placeholder - would need historical data)
                performance_fig = go.Figure()
                performance_fig.add_annotation(
                    text="Performance chart requires historical portfolio data<br>Will be implemented with transaction history",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=14, color="gray")
                )
                performance_fig.update_layout(
                    title="Portfolio Performance vs Market",
                    height=400,
                    template='plotly_white'
                )
                self.performance_chart.object = performance_fig

            else:
                self.allocation_chart.object = self._create_empty_chart("Portfolio Allocation")
                self.performance_chart.object = self._create_empty_chart("Portfolio Performance")

        except Exception as e:
            print(f"Error updating charts: {e}")

    def _create_empty_chart(self, title):
        """Create empty chart placeholder"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available<br>Import SBI transactions to view {title.lower()}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            height=400,
            template='plotly_white'
        )
        return fig

    def _create_empty_overview(self):
        """Create empty portfolio overview"""
        return """
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
            <h4 style="margin-top: 0;">Portfolio Summary</h4>
            <p style="color: #666; margin: 0;">Import SBI transactions to view portfolio overview</p>
        </div>
        """

    def _create_exchange_rate_info(self):
        """Create exchange rate information panel"""
        try:
            rate = shared_store.get_latest_exchange_rate()
            return f"""
            <div style="background: #e7f3ff; padding: 10px; border-radius: 5px; border: 1px solid #b3d7ff;">
                <h6 style="margin-top: 0; color: #004085;">💱 USD/JPY Exchange Rate</h6>
                <div style="font-size: 14px; font-weight: bold;">
                    1 USD = {rate:.2f} JPY
                </div>
                <div style="font-size: 11px; color: #666;">
                    Used for portfolio valuation
                </div>
            </div>
            """
        except:
            return """
            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
                <h6 style="margin-top: 0;">💱 Exchange Rate</h6>
                <p style="margin: 0; font-size: 12px;">Loading rate...</p>
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
TriggerControllerApp = PortfolioTrackerApp