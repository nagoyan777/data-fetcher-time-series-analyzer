"""
Database Manager App - SQLite Database Operations & Export
Stock data management, portfolio exports, and database maintenance
"""
import panel as pn
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_store import shared_store
from utils.navigation import create_navigation_bar, create_quick_actions_panel, create_app_status_indicator

class DatabaseManagerApp:
    """Database operations and stock data management interface"""

    def __init__(self):
        # Database operations
        self.backup_button = pn.widgets.Button(
            name="💾 Backup Database",
            button_type="primary",
            width=200
        )

        self.vacuum_button = pn.widgets.Button(
            name="🧹 Optimize Database",
            button_type="success",
            width=200
        )

        self.clear_button = pn.widgets.Button(
            name="🗑️ Clear Old Data",
            button_type="light",
            width=200
        )

        # Export options
        self.export_type = pn.widgets.Select(
            name="Export Type",
            options=["Portfolio Report", "Stock Prices", "All Data"],
            value="Portfolio Report",
            width=200
        )

        self.export_format = pn.widgets.Select(
            name="Export Format",
            options=["JSON", "CSV", "Excel"],
            value="JSON",
            width=200
        )

        self.export_button = pn.widgets.Button(
            name="📊 Export Data",
            button_type="primary",
            width=200
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
            <strong>Status:</strong> Ready for database operations
            </div>""",
            width=400
        )

        # Database info
        self.database_info = pn.pane.HTML(
            self._create_empty_db_info(),
            width=400,
            height=300
        )

        # Data tables
        self.stock_table = pn.widgets.Tabulator(
            value=pd.DataFrame(),
            pagination='remote',
            page_size=10,
            height=200,
            sizing_mode='stretch_width'
        )

        self.portfolio_table = pn.widgets.Tabulator(
            value=pd.DataFrame(),
            pagination='remote',
            page_size=10,
            height=200,
            sizing_mode='stretch_width'
        )

        # Setup callbacks
        self.backup_button.on_click(self._backup_database)
        self.vacuum_button.on_click(self._vacuum_database)
        self.clear_button.on_click(self._clear_old_data)
        self.export_button.on_click(self._export_data)

        # Load initial info
        self._load_database_info()

    def create_app(self):
        """Create the data manager interface"""

        # Navigation bar
        navigation = create_navigation_bar(current_app='database_manager')

        # Status indicator
        status = create_app_status_indicator()

        # Header
        header = pn.pane.HTML("""
        <div style="background: linear-gradient(90deg, #6f42c1, #5a32a3); padding: 20px; color: white; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">🗄️ Database Manager - SQLite Operations & Export</h2>
            <p style="margin: 5px 0 0 0;">Manage stock database, export portfolio reports, and maintain data integrity</p>
        </div>
        """, sizing_mode='stretch_width')

        # Database management panel
        management_panel = pn.Column(
            "## 🗄️ Database Status",
            self.progress_bar,
            self.status_indicator,
            self.database_info,
            "## 💾 Database Operations",
            pn.Row(self.backup_button, self.vacuum_button),
            self.clear_button,
            pn.pane.HTML("""
            <div style="background: #e9ecef; padding: 10px; border-radius: 3px; margin: 10px 0;">
                <strong>💡 Operations:</strong><br>
                • Backup: Creates timestamped database copy<br>
                • Optimize: Rebuilds database for better performance<br>
                • Clear: Removes price data older than 2 years
            </div>
            """),
            width=400
        )

        # Export panel
        export_panel = pn.Column(
            "## 📊 Data Export",
            self.export_type,
            self.export_format,
            self.export_button,
            pn.pane.HTML("""
            <div style="background: #e9ecef; padding: 10px; border-radius: 3px; margin: 10px 0;">
                <strong>📋 Export Types:</strong><br>
                • Portfolio Report: P&L analysis for tax reporting<br>
                • Stock Prices: Historical price data<br>
                • All Data: Complete database dump
            </div>
            """),
            width=400
        )

        # Data browser
        data_browser = pn.Column(
            "## 📋 Database Contents",
            pn.Tabs(
                ("Stock Master", self.stock_table),
                ("Portfolio Holdings", self.portfolio_table),
                dynamic=True
            ),
            sizing_mode='stretch_width'
        )

        # Main layout
        return pn.Column(
            navigation,
            status,
            header,
            pn.Row(
                management_panel,
                export_panel,
                sizing_mode='stretch_width'
            ),
            data_browser,
            sizing_mode='stretch_width'
        )

    async def _backup_database(self, event):
        """Create database backup"""
        self.progress_bar.value = 0
        self.update_status("💾 Creating database backup...", "info")

        try:
            self.progress_bar.value = 25
            result = shared_store.backup_database()
            self.progress_bar.value = 75

            if result['success']:
                self.progress_bar.value = 100
                self.update_status(f"✅ Backup created: {result['backup_file']}", "success")
                self._load_database_info()
            else:
                self.update_status(f"❌ Backup failed: {result.get('error', 'Unknown error')}", "error")

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Backup error: {str(e)}", "error")

    async def _vacuum_database(self, event):
        """Optimize database performance"""
        self.progress_bar.value = 0
        self.update_status("🧹 Optimizing database...", "info")

        try:
            self.progress_bar.value = 50
            result = shared_store.vacuum_database()
            self.progress_bar.value = 100

            if result['success']:
                self.update_status(f"✅ Database optimized. Space saved: {result.get('space_saved', 'Unknown')}", "success")
                self._load_database_info()
            else:
                self.update_status(f"❌ Optimization failed: {result.get('error', 'Unknown error')}", "error")

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Optimization error: {str(e)}", "error")

    async def _clear_old_data(self, event):
        """Clear old price data to save space"""
        self.progress_bar.value = 0
        self.update_status("🗑️ Clearing old data...", "info")

        try:
            self.progress_bar.value = 30
            result = shared_store.clear_old_price_data(days=730)  # Keep 2 years
            self.progress_bar.value = 100

            if result['success']:
                self.update_status(f"✅ Removed {result['removed_count']} old records", "success")
                self._load_database_info()
            else:
                self.update_status(f"❌ Clear failed: {result.get('error', 'Unknown error')}", "error")

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Clear error: {str(e)}", "error")

    async def _export_data(self, event):
        """Export data in selected format"""
        self.progress_bar.value = 0
        self.update_status("📊 Exporting data...", "info")

        try:
            export_type = self.export_type.value
            export_format = self.export_format.value.lower()
            self.progress_bar.value = 25

            if export_type == "Portfolio Report":
                result = shared_store.export_portfolio_report(format=export_format)
            elif export_type == "Stock Prices":
                result = shared_store.export_stock_prices(format=export_format)
            else:  # All Data
                result = shared_store.export_all_data(format=export_format)

            self.progress_bar.value = 75

            if result and result.get('success'):
                self.progress_bar.value = 100
                self.update_status(f"✅ Exported: {result['file_path']}", "success")
            else:
                self.update_status(f"❌ Export failed: {result.get('error', 'Unknown error') if result else 'No result'}", "error")

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Export error: {str(e)}", "error")

    def _load_database_info(self):
        """Load and display database information"""
        try:
            status = shared_store.get_status()

            info_html = f"""
            <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; border: 1px solid #bee5eb;">
                <h4 style="margin-top: 0; color: #0c5460;">🗄️ Database Status</h4>
                <table style="width: 100%; font-size: 14px;">
                    <tr><td><strong>Database:</strong></td><td>{'✅ Connected' if status.get('database_connected', False) else '❌ Error'}</td></tr>
                    <tr><td><strong>Stocks:</strong></td><td>{status.get('stock_count', 0)} symbols</td></tr>
                    <tr><td><strong>Price Records:</strong></td><td>{status.get('price_records', 0):,}</td></tr>
                    <tr><td><strong>Portfolio Holdings:</strong></td><td>{status.get('portfolio_holdings', 0)}</td></tr>
                    <tr><td><strong>SBI Transactions:</strong></td><td>{status.get('sbi_transactions', 0)}</td></tr>
                    <tr><td><strong>Exchange Rates:</strong></td><td>{status.get('exchange_rates', 0)} records</td></tr>
                    <tr><td><strong>Data Range:</strong></td><td>{status.get('price_data_range', 'No data')}</td></tr>
                    <tr><td><strong>Last Updated:</strong></td><td>{status.get('last_updated', 'Never')[:19] if status.get('last_updated') != 'Never' else 'Never'}</td></tr>
                </table>
            </div>
            """
            self.database_info.object = info_html

            # Load stock table
            stocks = shared_store.get_stocks_by_category()
            if not stocks.empty:
                display_stocks = stocks[['symbol', 'name', 'sector', 'category']].copy()
                display_stocks.columns = ['Symbol', 'Company', 'Sector', 'Category']
                self.stock_table.value = display_stocks

            # Load portfolio table
            portfolio = shared_store.get_portfolio_summary()
            if not portfolio.empty:
                display_portfolio = portfolio[['symbol', 'name', 'total_shares', 'avg_cost_usd', 'total_invested_usd']].copy()
                display_portfolio.columns = ['Symbol', 'Company', 'Shares', 'Avg Cost', 'Total Invested']
                self.portfolio_table.value = display_portfolio

        except Exception as e:
            self.database_info.object = self._create_empty_db_info(error=str(e))

    def _create_empty_db_info(self, error=None):
        """Create empty database info panel"""
        if error:
            return f"""
            <div style="background: #f8d7da; padding: 15px; border-radius: 5px; color: #721c24;">
                <h4 style="margin-top: 0;">❌ Database Error</h4>
                <p>Error loading database info: {error}</p>
            </div>
            """
        else:
            return """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h4 style="margin-top: 0;">🗄️ Database Status</h4>
                <p style="color: #666; margin: 0;">Loading database information...</p>
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
DataManagerApp = DatabaseManagerApp