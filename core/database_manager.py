"""
Database Manager - SQLite operations for US Stock Analysis Platform
Handles all database operations for stock data, portfolio tracking, and SBI integration
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import json

class DatabaseManager:
    """SQLite database manager for stock analysis platform"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = Path(__file__).parent.parent / "data" / "stock_analysis.db"
        else:
            self.db_path = Path(db_path)

        # Ensure data directory exists
        self.db_path.parent.mkdir(exist_ok=True)

        # Initialize database
        self.init_database()

    def get_connection(self):
        """Get database connection with optimizations"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            # US stocks information table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS us_stocks (
                    symbol TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    sector TEXT,
                    category TEXT,  -- tech, growth, value
                    market_cap INTEGER,
                    pe_ratio REAL,
                    dividend_yield REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Daily stock price data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    symbol TEXT,
                    date DATE,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    adjusted_close REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, date),
                    FOREIGN KEY (symbol) REFERENCES us_stocks (symbol)
                )
            """)

            # SBI transaction records
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sbi_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    symbol TEXT,
                    action TEXT,  -- BUY, SELL
                    quantity REAL,
                    price_usd REAL,
                    commission_usd REAL,
                    total_usd REAL,
                    exchange_rate REAL,
                    total_jpy REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data TEXT,  -- Original CSV row for reference
                    FOREIGN KEY (symbol) REFERENCES us_stocks (symbol)
                )
            """)

            # Current portfolio holdings
            conn.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_holdings (
                    symbol TEXT PRIMARY KEY,
                    total_shares REAL,
                    avg_cost_usd REAL,
                    total_invested_usd REAL,
                    current_value_usd REAL,
                    unrealized_pnl_usd REAL,
                    unrealized_pnl_jpy REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol) REFERENCES us_stocks (symbol)
                )
            """)

            # USD/JPY exchange rates
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usd_jpy_rates (
                    date DATE PRIMARY KEY,
                    rate REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Market indices data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_indices (
                    symbol TEXT,
                    date DATE,
                    value REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, date)
                )
            """)

            # Create indices for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sbi_transactions_date ON sbi_transactions(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sbi_transactions_symbol ON sbi_transactions(symbol)")

            conn.commit()

        self._populate_initial_stocks()

    def _populate_initial_stocks(self):
        """Populate database with popular tech/growth/value stocks"""
        stocks_data = [
            # Technology Leaders
            ("AAPL", "Apple Inc.", "Technology", "tech", 3000000000000, 28.5, 0.5),
            ("GOOGL", "Alphabet Inc.", "Technology", "tech", 2100000000000, 25.2, 0.0),
            ("MSFT", "Microsoft Corporation", "Technology", "tech", 2800000000000, 32.1, 0.7),
            ("NVDA", "NVIDIA Corporation", "Technology", "tech", 1800000000000, 65.8, 0.03),
            ("META", "Meta Platforms Inc.", "Technology", "tech", 800000000000, 24.7, 0.0),
            ("AMZN", "Amazon.com Inc.", "Technology", "growth", 1500000000000, 50.3, 0.0),

            # Growth Stocks
            ("TSLA", "Tesla Inc.", "Consumer Discretionary", "growth", 800000000000, 58.2, 0.0),
            ("NFLX", "Netflix Inc.", "Communication Services", "growth", 200000000000, 35.4, 0.0),
            ("AMD", "Advanced Micro Devices", "Technology", "growth", 250000000000, 28.9, 0.0),
            ("CRM", "Salesforce Inc.", "Technology", "growth", 250000000000, 45.6, 0.0),

            # Value Stocks
            ("BRK.B", "Berkshire Hathaway Inc.", "Financial Services", "value", 900000000000, 8.5, 0.0),
            ("JPM", "JPMorgan Chase & Co.", "Financial Services", "value", 500000000000, 12.8, 2.2),
            ("WMT", "Walmart Inc.", "Consumer Staples", "value", 500000000000, 27.1, 1.8),
            ("PG", "Procter & Gamble Co.", "Consumer Staples", "value", 350000000000, 24.5, 2.4),
            ("JNJ", "Johnson & Johnson", "Healthcare", "value", 450000000000, 21.3, 2.9),
            ("KO", "The Coca-Cola Company", "Consumer Staples", "value", 280000000000, 25.8, 3.1),

            # Market ETFs
            ("SPY", "SPDR S&P 500 ETF Trust", "ETF", "market", 450000000000, None, 1.3),
            ("QQQ", "Invesco QQQ Trust", "ETF", "market", 200000000000, None, 0.5),
            ("VTI", "Vanguard Total Stock Market ETF", "ETF", "market", 300000000000, None, 1.3),
        ]

        with self.get_connection() as conn:
            # Check if stocks already exist
            cursor = conn.execute("SELECT COUNT(*) FROM us_stocks")
            count = cursor.fetchone()[0]

            if count == 0:  # Only insert if empty
                conn.executemany("""
                    INSERT OR IGNORE INTO us_stocks
                    (symbol, name, sector, category, market_cap, pe_ratio, dividend_yield)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, stocks_data)
                conn.commit()
                logging.info(f"Populated database with {len(stocks_data)} stocks")

    def save_stock_prices(self, symbol: str, price_data: List[Dict]) -> bool:
        """Save stock price data to database"""
        try:
            with self.get_connection() as conn:
                for price in price_data:
                    conn.execute("""
                        INSERT OR REPLACE INTO stock_prices
                        (symbol, date, open_price, high_price, low_price, close_price, volume, adjusted_close)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        price['date'],
                        price.get('open'),
                        price.get('high'),
                        price.get('low'),
                        price.get('close'),
                        price.get('volume'),
                        price.get('adjusted_close', price.get('close'))
                    ))
                conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving stock prices for {symbol}: {e}")
            return False

    def get_stock_prices(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get stock price data as DataFrame"""
        query = "SELECT * FROM stock_prices WHERE symbol = ?"
        params = [symbol]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_all_stock_prices(self) -> pd.DataFrame:
        """Get all stock price data from database"""
        query = "SELECT * FROM stock_prices ORDER BY symbol, date"
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def save_sbi_transaction(self, transaction_data: Dict) -> bool:
        """Save SBI transaction to database"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO sbi_transactions
                    (date, symbol, action, quantity, price_usd, commission_usd,
                     total_usd, exchange_rate, total_jpy, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction_data['date'],
                    transaction_data['symbol'],
                    transaction_data['action'],
                    transaction_data['quantity'],
                    transaction_data['price_usd'],
                    transaction_data['commission_usd'],
                    transaction_data['total_usd'],
                    transaction_data['exchange_rate'],
                    transaction_data['total_jpy'],
                    json.dumps(transaction_data.get('raw_data', {}))
                ))
                conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving SBI transaction: {e}")
            return False

    def get_portfolio_transactions(self) -> pd.DataFrame:
        """Get all portfolio transactions"""
        query = """
            SELECT * FROM sbi_transactions
            ORDER BY date DESC
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def calculate_portfolio_holdings(self) -> bool:
        """Calculate and update current portfolio holdings"""
        try:
            with self.get_connection() as conn:
                # Get all transactions grouped by symbol
                transactions = pd.read_sql_query("""
                    SELECT symbol, action, quantity, price_usd, total_usd
                    FROM sbi_transactions
                    ORDER BY date
                """, conn)

                if transactions.empty:
                    return True

                # Calculate holdings for each symbol
                holdings = {}
                for _, tx in transactions.iterrows():
                    symbol = tx['symbol']
                    if symbol not in holdings:
                        holdings[symbol] = {'shares': 0, 'invested': 0}

                    if tx['action'] == 'BUY':
                        holdings[symbol]['shares'] += tx['quantity']
                        holdings[symbol]['invested'] += tx['total_usd']
                    elif tx['action'] == 'SELL':
                        holdings[symbol]['shares'] -= tx['quantity']
                        # For avg cost, we need to reduce invested proportionally
                        if holdings[symbol]['shares'] > 0:
                            reduction_ratio = tx['quantity'] / (holdings[symbol]['shares'] + tx['quantity'])
                            holdings[symbol]['invested'] *= (1 - reduction_ratio)

                # Clear existing holdings
                conn.execute("DELETE FROM portfolio_holdings")

                # Insert updated holdings
                for symbol, data in holdings.items():
                    if data['shares'] > 0:  # Only active holdings
                        avg_cost = data['invested'] / data['shares'] if data['shares'] > 0 else 0
                        conn.execute("""
                            INSERT INTO portfolio_holdings
                            (symbol, total_shares, avg_cost_usd, total_invested_usd)
                            VALUES (?, ?, ?, ?)
                        """, (symbol, data['shares'], avg_cost, data['invested']))

                conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error calculating portfolio holdings: {e}")
            return False

    def get_portfolio_summary(self) -> pd.DataFrame:
        """Get current portfolio summary with current values"""
        query = """
            SELECT
                h.symbol,
                s.name,
                s.sector,
                s.category,
                h.total_shares,
                h.avg_cost_usd,
                h.total_invested_usd,
                h.current_value_usd,
                h.unrealized_pnl_usd,
                h.last_updated
            FROM portfolio_holdings h
            JOIN us_stocks s ON h.symbol = s.symbol
            WHERE h.total_shares > 0
            ORDER BY h.total_invested_usd DESC
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def save_exchange_rate(self, date: str, rate: float) -> bool:
        """Save USD/JPY exchange rate"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO usd_jpy_rates (date, rate)
                    VALUES (?, ?)
                """, (date, rate))
                conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving exchange rate: {e}")
            return False

    def get_latest_exchange_rate(self) -> float:
        """Get latest USD/JPY exchange rate"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT rate FROM usd_jpy_rates
                ORDER BY date DESC LIMIT 1
            """)
            result = cursor.fetchone()
            return result[0] if result else 150.0  # Default rate

    def get_stocks_by_category(self, category: str = None) -> pd.DataFrame:
        """Get stocks filtered by category"""
        query = "SELECT * FROM us_stocks"
        params = []

        if category:
            query += " WHERE category = ?"
            params.append(category)

        query += " ORDER BY market_cap DESC"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def backup_database(self, backup_path: str = None) -> bool:
        """Create database backup"""
        try:
            if backup_path is None:
                backup_dir = self.db_path.parent / "backups"
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"stock_analysis_backup_{timestamp}.db"

            # Simple file copy for SQLite
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logging.info(f"Database backed up to {backup_path}")
            return str(backup_path)
        except Exception as e:
            logging.error(f"Error backing up database: {e}")
            return None

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            stats = {}

            # Count records in each table
            tables = ['us_stocks', 'stock_prices', 'sbi_transactions', 'portfolio_holdings', 'usd_jpy_rates']
            for table in tables:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]

            # Get date ranges
            cursor = conn.execute("SELECT MIN(date), MAX(date) FROM stock_prices")
            result = cursor.fetchone()
            stats['price_data_range'] = f"{result[0]} to {result[1]}" if result[0] else "No data"

            cursor = conn.execute("SELECT MIN(date), MAX(date) FROM sbi_transactions")
            result = cursor.fetchone()
            stats['transaction_range'] = f"{result[0]} to {result[1]}" if result[0] else "No transactions"

            return stats

    def vacuum_database(self) -> Dict:
        """Optimize database by vacuuming"""
        try:
            with self.get_connection() as conn:
                # Get size before vacuum
                cursor = conn.cursor()
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                size_before = cursor.fetchone()[0]

                # Vacuum
                conn.execute("VACUUM")

                # Get size after vacuum
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                size_after = cursor.fetchone()[0]

                space_saved = (size_before - size_after) / (1024 * 1024)  # Convert to MB

                return {
                    'success': True,
                    'space_saved': space_saved
                }
        except Exception as e:
            logging.error(f"Error vacuuming database: {e}")
            return {'success': False, 'error': str(e)}

    def clear_old_price_data(self, days: int = 730) -> int:
        """Clear price data older than specified days"""
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM stock_prices WHERE date < ?", (cutoff_date,))
                removed_count = cursor.rowcount
                conn.commit()

                logging.info(f"Removed {removed_count} old price records")
                return removed_count
        except Exception as e:
            logging.error(f"Error clearing old price data: {e}")
            return 0