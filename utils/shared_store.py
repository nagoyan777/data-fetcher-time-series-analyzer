#!/usr/bin/env python3
"""
Shared Data Store for US Stock Analysis Platform
SQLite-based data sharing between apps with stock data, portfolio tracking, and SBI integration
"""
import json
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
import logging
from typing import Dict, List, Optional
import sys

# Add core module to path
sys.path.append(str(Path(__file__).parent.parent / "core"))
from database_manager import DatabaseManager
from stock_data_fetcher import StockDataFetcher, CurrencyConverter
from sbi_parser import SBICSVParser

class SharedDataStore:
    """Shared storage for stock analysis platform using SQLite database"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)

        # Initialize database manager
        self.db = DatabaseManager()

        # Initialize other components
        self.stock_fetcher = StockDataFetcher()
        self.currency_converter = CurrencyConverter()
        self.sbi_parser = SBICSVParser()

        # Ensure subdirectories exist
        for subdir in ['sbi_imports', 'exports', 'backups']:
            (self.data_dir / subdir).mkdir(exist_ok=True)

    # ===== STOCK DATA METHODS =====

    def fetch_stock_data(self, symbol: str, full_history: bool = False) -> Dict:
        """Fetch and save stock data"""
        try:
            outputsize = "full" if full_history else "compact"
            result = self.stock_fetcher.get_daily_prices(symbol, outputsize)

            if result['success']:
                # Save to database
                self.db.save_stock_prices(symbol, result['data'])
                logging.info(f"Saved {len(result['data'])} price records for {symbol}")

            return result
        except Exception as e:
            logging.error(f"Error fetching stock data for {symbol}: {e}")
            return {'success': False, 'error': str(e)}

    def get_stock_prices(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get stock price data"""
        return self.db.get_stock_prices(symbol, start_date, end_date)

    def get_current_quote(self, symbol: str) -> Dict:
        """Get current stock quote"""
        return self.stock_fetcher.get_current_quote(symbol)

    def download_historical_data(self, symbols: List[str] = None) -> Dict[str, bool]:
        """Download historical data for multiple stocks"""
        if symbols is None:
            # Get all stocks from database
            stocks_df = self.db.get_stocks_by_category()
            symbols = stocks_df['symbol'].tolist()

        return self.stock_fetcher.download_historical_data(symbols, self.db)

    def get_stocks_by_category(self, category: str = None) -> pd.DataFrame:
        """Get stocks filtered by category (tech, growth, value)"""
        return self.db.get_stocks_by_category(category)

    # ===== PORTFOLIO METHODS =====

    def import_sbi_csv(self, file_path: str) -> Dict:
        """Import SBI Securities CSV transactions"""
        try:
            result = self.sbi_parser.parse_csv_file(file_path)

            if result['success']:
                # Save transactions to database
                saved_count = 0
                for transaction in result['transactions']:
                    if self.db.save_sbi_transaction(transaction):
                        saved_count += 1

                # Recalculate portfolio holdings
                self.db.calculate_portfolio_holdings()

                return {
                    'success': True,
                    'total_transactions': result['total_count'],
                    'saved_transactions': saved_count,
                    'file_path': file_path
                }
            else:
                return result

        except Exception as e:
            logging.error(f"Error importing SBI CSV: {e}")
            return {'success': False, 'error': str(e)}

    def get_portfolio_summary(self) -> pd.DataFrame:
        """Get current portfolio summary"""
        return self.db.get_portfolio_summary()

    def get_portfolio_transactions(self) -> pd.DataFrame:
        """Get all portfolio transactions"""
        return self.db.get_portfolio_transactions()

    def calculate_portfolio_performance(self) -> Dict:
        """Calculate portfolio performance metrics"""
        try:
            portfolio = self.get_portfolio_summary()
            if portfolio.empty:
                return {'success': False, 'error': 'No portfolio data available'}

            # Get current exchange rate
            current_rate = self.currency_converter.get_current_rate() or 150.0

            # Calculate metrics
            total_invested_usd = portfolio['total_invested_usd'].sum()
            total_current_value_usd = 0

            # Get current prices and calculate current values
            for _, holding in portfolio.iterrows():
                quote = self.get_current_quote(holding['symbol'])
                if quote['success']:
                    current_price = quote['price']
                    current_value = holding['total_shares'] * current_price
                    total_current_value_usd += current_value

            total_pnl_usd = total_current_value_usd - total_invested_usd
            total_return_pct = (total_pnl_usd / total_invested_usd * 100) if total_invested_usd > 0 else 0

            return {
                'success': True,
                'total_invested_usd': total_invested_usd,
                'current_value_usd': total_current_value_usd,
                'unrealized_pnl_usd': total_pnl_usd,
                'total_return_pct': total_return_pct,
                'current_exchange_rate': current_rate,
                'current_value_jpy': total_current_value_usd * current_rate,
                'unrealized_pnl_jpy': total_pnl_usd * current_rate,
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Error calculating portfolio performance: {e}")
            return {'success': False, 'error': str(e)}

    # ===== CURRENCY METHODS =====

    def update_exchange_rates(self) -> bool:
        """Update USD/JPY exchange rates"""
        try:
            current_rate = self.currency_converter.get_current_rate()
            if current_rate:
                today = datetime.now().strftime('%Y-%m-%d')
                return self.db.save_exchange_rate(today, current_rate)
            return False
        except Exception as e:
            logging.error(f"Error updating exchange rates: {e}")
            return False

    def get_latest_exchange_rate(self) -> float:
        """Get latest USD/JPY exchange rate"""
        return self.db.get_latest_exchange_rate()

    # ===== SYSTEM METHODS =====

    def get_status(self) -> Dict:
        """Get current system status"""
        stats = self.db.get_database_stats()

        return {
            'database_available': True,
            'stock_count': stats.get('us_stocks_count', 0),
            'price_records': stats.get('stock_prices_count', 0),
            'portfolio_transactions': stats.get('sbi_transactions_count', 0),
            'portfolio_holdings': stats.get('portfolio_holdings_count', 0),
            'exchange_rates': stats.get('usd_jpy_rates_count', 0),
            'price_data_range': stats.get('price_data_range', 'No data'),
            'transaction_range': stats.get('transaction_range', 'No transactions'),
            'last_updated': datetime.now().isoformat()
        }

    def backup_database(self) -> Dict:
        """Create database backup"""
        try:
            backup_path = self.db.backup_database()
            if backup_path:
                return {'success': True, 'backup_file': backup_path}
            else:
                return {'success': False, 'error': 'Backup creation failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def vacuum_database(self) -> Dict:
        """Optimize database by vacuuming"""
        try:
            result = self.db.vacuum_database()
            return {
                'success': True,
                'space_saved': f"{result.get('space_saved', 0)} MB"
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def clear_old_price_data(self, days: int = 730) -> Dict:
        """Clear price data older than specified days"""
        try:
            removed_count = self.db.clear_old_price_data(days)
            return {
                'success': True,
                'removed_count': removed_count
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def export_stock_prices(self, format: str = 'csv') -> Dict:
        """Export all stock price data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = self.data_dir / "exports" / f"stock_prices_{timestamp}.{format.lower()}"

            # Get all stock prices
            all_prices = self.db.get_all_stock_prices()

            if format.lower() == 'excel':
                all_prices.to_excel(str(file_path), index=False)
            elif format.lower() == 'json':
                all_prices.to_json(str(file_path), orient='records')
            else:  # CSV
                all_prices.to_csv(str(file_path), index=False)

            return {'success': True, 'file_path': str(file_path)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def export_all_data(self, format: str = 'json') -> Dict:
        """Export complete database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if format.lower() == 'excel':
                file_path = self.data_dir / "exports" / f"complete_export_{timestamp}.xlsx"

                with pd.ExcelWriter(str(file_path), engine='openpyxl') as writer:
                    sheets_written = False

                    # Export all tables - always write stocks sheet even if empty
                    stocks = self.get_stocks_by_category()
                    if stocks.empty:
                        # Create empty DataFrame with expected columns
                        stocks = pd.DataFrame(columns=['symbol', 'name', 'sector', 'category', 'market_cap', 'pe_ratio', 'dividend_yield'])
                    stocks.to_excel(writer, sheet_name='Stocks', index=False)
                    sheets_written = True

                    # Export price data
                    prices = self.db.get_all_stock_prices()
                    if not prices.empty:
                        prices.to_excel(writer, sheet_name='Stock Prices', index=False)
                    else:
                        # Write empty sheet with columns if no data
                        pd.DataFrame(columns=['symbol', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'adjusted_close']).to_excel(
                            writer, sheet_name='Stock Prices', index=False)

                    # Export portfolio data
                    portfolio = self.get_portfolio_summary()
                    if not portfolio.empty:
                        portfolio.to_excel(writer, sheet_name='Portfolio', index=False)
                    else:
                        # Write empty sheet with expected columns
                        pd.DataFrame(columns=['symbol', 'name', 'total_shares', 'avg_cost_usd', 'total_invested_usd']).to_excel(
                            writer, sheet_name='Portfolio', index=False)

                    # Export transactions
                    transactions = self.get_portfolio_transactions()
                    if not transactions.empty:
                        transactions.to_excel(writer, sheet_name='Transactions', index=False)
                    else:
                        # Write empty sheet with expected columns
                        pd.DataFrame(columns=['date', 'symbol', 'action', 'quantity', 'price_usd', 'total_usd']).to_excel(
                            writer, sheet_name='Transactions', index=False)

                    # Ensure at least one sheet was written
                    if not sheets_written:
                        pd.DataFrame({'Info': ['No data available']}).to_excel(writer, sheet_name='Info', index=False)

                return {'success': True, 'file_path': str(file_path)}

            elif format.lower() == 'json':
                file_path = self.data_dir / "exports" / f"complete_export_{timestamp}.json"

                # Collect all data into a dictionary
                export_data = {}

                # Export stocks
                stocks = self.get_stocks_by_category()
                export_data['stocks'] = stocks.to_dict('records') if not stocks.empty else []

                # Export price data
                prices = self.db.get_all_stock_prices()
                if not prices.empty:
                    # Convert datetime columns to string for JSON serialization
                    prices['date'] = prices['date'].astype(str)
                    prices['last_updated'] = prices['last_updated'].astype(str) if 'last_updated' in prices.columns else None
                export_data['stock_prices'] = prices.to_dict('records') if not prices.empty else []

                # Export portfolio data
                portfolio = self.get_portfolio_summary()
                export_data['portfolio'] = portfolio.to_dict('records') if not portfolio.empty else []

                # Export transactions
                transactions = self.get_portfolio_transactions()
                if not transactions.empty:
                    # Convert datetime columns to string
                    transactions['date'] = transactions['date'].astype(str)
                    if 'created_at' in transactions.columns:
                        transactions['created_at'] = transactions['created_at'].astype(str)
                export_data['transactions'] = transactions.to_dict('records') if not transactions.empty else []

                # Add metadata
                export_data['metadata'] = {
                    'exported_at': timestamp,
                    'total_stocks': len(export_data['stocks']),
                    'total_price_records': len(export_data['stock_prices']),
                    'total_holdings': len(export_data['portfolio']),
                    'total_transactions': len(export_data['transactions'])
                }

                # Write JSON file
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)

                return {'success': True, 'file_path': str(file_path)}

            elif format.lower() == 'csv':
                # CSV format exports multiple files since we have multiple tables
                base_path = self.data_dir / "exports" / f"complete_export_{timestamp}"
                base_path.mkdir(exist_ok=True)

                files_created = []

                # Export stocks
                stocks = self.get_stocks_by_category()
                if not stocks.empty:
                    stocks_file = base_path / "stocks.csv"
                    stocks.to_csv(stocks_file, index=False)
                    files_created.append(str(stocks_file))

                # Export price data
                prices = self.db.get_all_stock_prices()
                if not prices.empty:
                    prices_file = base_path / "stock_prices.csv"
                    prices.to_csv(prices_file, index=False)
                    files_created.append(str(prices_file))

                # Export portfolio
                portfolio = self.get_portfolio_summary()
                if not portfolio.empty:
                    portfolio_file = base_path / "portfolio.csv"
                    portfolio.to_csv(portfolio_file, index=False)
                    files_created.append(str(portfolio_file))

                # Export transactions
                transactions = self.get_portfolio_transactions()
                if not transactions.empty:
                    transactions_file = base_path / "transactions.csv"
                    transactions.to_csv(transactions_file, index=False)
                    files_created.append(str(transactions_file))

                return {
                    'success': True,
                    'file_path': str(base_path),
                    'files_created': files_created,
                    'message': f"Created {len(files_created)} CSV files in {base_path}"
                }

            else:
                return {'success': False, 'error': f'Unsupported format: {format}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def export_portfolio_report(self, format: str = 'excel', file_path: str = None) -> Dict:
        """Export portfolio report"""
        try:
            if file_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                extension = 'xlsx' if format.lower() == 'excel' else format.lower()
                file_path = self.data_dir / "exports" / f"portfolio_report_{timestamp}.{extension}"

            # Get portfolio data
            portfolio = self.get_portfolio_summary()
            transactions = self.get_portfolio_transactions()

            if format.lower() == 'excel':
                # Create detailed Excel report
                with pd.ExcelWriter(str(file_path), engine='openpyxl') as writer:
                    # Always write Current Holdings sheet (even if empty)
                    if not portfolio.empty:
                        portfolio.to_excel(writer, sheet_name='Current Holdings', index=False)
                    else:
                        # Write empty sheet with expected columns
                        empty_holdings = pd.DataFrame(columns=['symbol', 'name', 'sector', 'category',
                                                              'total_shares', 'avg_cost_usd', 'total_invested_usd',
                                                              'current_value_usd', 'unrealized_pnl_usd'])
                        empty_holdings.to_excel(writer, sheet_name='Current Holdings', index=False)

                    # Always write Transactions sheet (even if empty)
                    if not transactions.empty:
                        transactions.to_excel(writer, sheet_name='All Transactions', index=False)
                    else:
                        # Write empty sheet with expected columns
                        empty_transactions = pd.DataFrame(columns=['date', 'symbol', 'action', 'quantity',
                                                                  'price_usd', 'commission_usd', 'total_usd',
                                                                  'exchange_rate', 'total_jpy'])
                        empty_transactions.to_excel(writer, sheet_name='All Transactions', index=False)

                    # Add performance summary
                    performance = self.calculate_portfolio_performance()
                    if performance['success']:
                        summary_data = pd.DataFrame([{
                            'Metric': 'Total Invested',
                            'Value USD': f"${performance['total_invested_usd']:,.2f}",
                            'Value JPY': f"¥{performance.get('total_invested_jpy', performance['total_invested_usd'] * 150):,.0f}"
                        }, {
                            'Metric': 'Current Value',
                            'Value USD': f"${performance['current_value_usd']:,.2f}",
                            'Value JPY': f"¥{performance['current_value_jpy']:,.0f}"
                        }, {
                            'Metric': 'Unrealized P&L',
                            'Value USD': f"${performance['unrealized_pnl_usd']:,.2f}",
                            'Value JPY': f"¥{performance['unrealized_pnl_jpy']:,.0f}"
                        }, {
                            'Metric': 'Total Return',
                            'Value USD': f"{performance['total_return_pct']:.2f}%",
                            'Value JPY': f"{performance['total_return_pct']:.2f}%"
                        }])
                        summary_data.to_excel(writer, sheet_name='Performance Summary', index=False)
                    else:
                        # Write empty performance summary with placeholder data
                        summary_data = pd.DataFrame([{
                            'Metric': 'Total Invested',
                            'Value USD': '$0.00',
                            'Value JPY': '¥0'
                        }, {
                            'Metric': 'Current Value',
                            'Value USD': '$0.00',
                            'Value JPY': '¥0'
                        }, {
                            'Metric': 'Unrealized P&L',
                            'Value USD': '$0.00',
                            'Value JPY': '¥0'
                        }, {
                            'Metric': 'Total Return',
                            'Value USD': '0.00%',
                            'Value JPY': '0.00%'
                        }])
                        summary_data.to_excel(writer, sheet_name='Performance Summary', index=False)
            elif format.lower() == 'csv':
                if not portfolio.empty:
                    portfolio.to_csv(str(file_path), index=False)
            else:  # JSON
                if not portfolio.empty:
                    portfolio.to_json(str(file_path), orient='records')

            return {'success': True, 'file_path': str(file_path)}

        except Exception as e:
            logging.error(f"Error exporting portfolio report: {e}")
            return {'success': False, 'error': str(e)}

    # ===== LEGACY METHODS (for backward compatibility) =====

    def save_time_series_data(self, data, source_name, metadata=None):
        """Legacy method - now saves stock data"""
        if isinstance(data, list) and len(data) > 0:
            if 'symbol' in data[0]:
                symbol = data[0]['symbol']
                return self.fetch_stock_data(symbol)
        return False

    def load_time_series_data(self):
        """Legacy method - returns stock data"""
        stocks = self.get_stocks_by_category()
        if not stocks.empty:
            # Return data for first stock
            symbol = stocks.iloc[0]['symbol']
            price_data = self.get_stock_prices(symbol)
            if not price_data.empty:
                return {
                    'data': price_data.to_dict('records'),
                    'source_name': symbol,
                    'timestamp': datetime.now().isoformat()
                }
        return None

    def save_fetch_event(self, event_data):
        """Legacy method for fetch event logging"""
        # Could log to database if needed
        return True

    def load_fetch_history(self):
        """Legacy method for fetch history"""
        # Return recent stock fetches from database
        return []

    def save_app_config(self, app_name, config_data):
        """Save app-specific configuration settings"""
        try:
            config_file = self.data_dir / f"{app_name}_config.json"
            config = self.load_app_config(app_name)
            config.update(config_data)
            config['updated'] = datetime.now().isoformat()

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving app config for {app_name}: {e}")
            return False

    def load_app_config(self, app_name):
        """Load app-specific configuration settings"""
        try:
            config_file = self.data_dir / f"{app_name}_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading app config for {app_name}: {e}")
            return {}

    def get_sync_config(self, app_name):
        """Get configuration for a specific app with fallback defaults"""
        config = self.load_app_config(app_name)
        defaults = {
            'market_explorer': {
                'default_symbols': ['AAPL', 'GOOGL', 'MSFT', 'SPY', 'QQQ'],
                'default_period': '1Y',
                'show_volume': True
            },
            'portfolio_tracker': {
                'currency_display': 'USD',
                'show_unrealized_pnl': True,
                'auto_refresh_quotes': False
            },
            'data_manager': {
                'backup_frequency': 'weekly',
                'export_format': 'xlsx',
                'retention_years': 10
            },
            'analysis_dashboard': {
                'default_charts': ['portfolio_allocation', 'performance_vs_market'],
                'refresh_interval': 300,
                'show_benchmarks': True
            }
        }

        # Return app-specific config merged with defaults
        app_defaults = defaults.get(app_name, {})
        return {**app_defaults, **config}

# Global instance for all apps to use
shared_store = SharedDataStore()