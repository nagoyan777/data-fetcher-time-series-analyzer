"""
Stock Data Fetcher - Alpha Vantage API Integration
Fetches US stock data with fallback to Yahoo Finance
"""
import requests
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import yfinance as yf  # Backup data source

class StockDataFetcher:
    """Alpha Vantage API integration for US stock data"""

    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_delay = 12  # Free tier: 5 calls per minute
        self.last_request_time = 0
        self.cache = {}  # Simple in-memory cache for Yahoo Finance
        self.cache_duration = 300  # Cache for 5 minutes

    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    def get_daily_prices(self, symbol: str, outputsize: str = "full") -> Dict:
        """
        Get daily stock prices from Alpha Vantage

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            outputsize: 'compact' (100 days) or 'full' (20+ years)

        Returns:
            Dict with price data or error info
        """
        self._rate_limit()

        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': outputsize,
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            data = response.json()

            if 'Error Message' in data:
                return {'success': False, 'error': data['Error Message']}

            if 'Note' in data:
                return {'success': False, 'error': 'API rate limit exceeded'}

            if 'Time Series (Daily)' not in data:
                # Try with Yahoo Finance fallback
                return self._get_yahoo_finance_data(symbol)

            time_series = data['Time Series (Daily)']

            # Convert to standardized format
            price_data = []
            for date_str, values in time_series.items():
                price_data.append({
                    'date': date_str,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'adjusted_close': float(values['5. adjusted close']),
                    'volume': int(values['6. volume'])
                })

            return {
                'success': True,
                'symbol': symbol,
                'data': price_data,
                'source': 'alpha_vantage',
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Alpha Vantage error for {symbol}: {e}")
            # Fallback to Yahoo Finance
            return self._get_yahoo_finance_data(symbol)

    def _get_yahoo_finance_data(self, symbol: str) -> Dict:
        """Fallback to Yahoo Finance for stock data"""
        try:
            # Check cache first
            cache_key = f"yf_{symbol}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if time.time() - cached_time < self.cache_duration:
                    logging.info(f"Using cached data for {symbol}")
                    return cached_data

            # Add rate limiting for Yahoo Finance (max 2000 requests/hour = ~1 request every 2 seconds)
            time.sleep(2)  # Simple rate limiting to avoid hitting Yahoo's limits

            # Get 5 years of data
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5y")

            if hist.empty:
                return {'success': False, 'error': f'No data found for {symbol}'}

            price_data = []
            for date, row in hist.iterrows():
                price_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'adjusted_close': float(row['Close']),  # Yahoo Finance already adjusts
                    'volume': int(row['Volume'])
                })

            result = {
                'success': True,
                'symbol': symbol,
                'data': price_data,
                'source': 'yahoo_finance',
                'last_updated': datetime.now().isoformat()
            }

            # Cache the result
            self.cache[cache_key] = (time.time(), result)

            return result

        except Exception as e:
            logging.error(f"Yahoo Finance error for {symbol}: {e}")
            return {'success': False, 'error': str(e)}

    def get_company_overview(self, symbol: str) -> Dict:
        """Get company fundamental data"""
        self._rate_limit()

        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            data = response.json()

            if 'Error Message' in data or not data:
                return {'success': False, 'error': 'No overview data available'}

            return {
                'success': True,
                'symbol': symbol,
                'name': data.get('Name', ''),
                'sector': data.get('Sector', ''),
                'industry': data.get('Industry', ''),
                'market_cap': self._parse_number(data.get('MarketCapitalization', '0')),
                'pe_ratio': self._parse_float(data.get('PERatio', 'None')),
                'dividend_yield': self._parse_float(data.get('DividendYield', '0')),
                'description': data.get('Description', ''),
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Company overview error for {symbol}: {e}")
            return {'success': False, 'error': str(e)}

    def get_current_quote(self, symbol: str) -> Dict:
        """Get real-time quote"""
        self._rate_limit()

        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            data = response.json()

            if 'Error Message' in data:
                return {'success': False, 'error': data['Error Message']}

            quote_data = data.get('Global Quote', {})
            if not quote_data:
                return {'success': False, 'error': 'No quote data available'}

            return {
                'success': True,
                'symbol': symbol,
                'price': float(quote_data.get('05. price', 0)),
                'change': float(quote_data.get('09. change', 0)),
                'change_percent': quote_data.get('10. change percent', '0%'),
                'volume': int(quote_data.get('06. volume', 0)),
                'latest_trading_day': quote_data.get('07. latest trading day', ''),
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Quote error for {symbol}: {e}")
            return {'success': False, 'error': str(e)}

    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get quotes for multiple symbols"""
        results = {}

        for symbol in symbols:
            results[symbol] = self.get_current_quote(symbol)
            # Small delay between requests to respect rate limits
            time.sleep(1)

        return results

    def get_market_indices(self) -> Dict:
        """Get major market index data"""
        indices = ['SPY', 'QQQ', 'VTI', 'DIA']  # ETFs that track major indices
        return self.get_multiple_quotes(indices)

    def _parse_number(self, value: str) -> int:
        """Parse string number with possible suffixes (M, B)"""
        if not value or value == 'None':
            return 0

        value = value.replace(',', '')

        try:
            if value.endswith('B'):
                return int(float(value[:-1]) * 1_000_000_000)
            elif value.endswith('M'):
                return int(float(value[:-1]) * 1_000_000)
            elif value.endswith('K'):
                return int(float(value[:-1]) * 1_000)
            else:
                return int(float(value))
        except:
            return 0

    def _parse_float(self, value: str) -> Optional[float]:
        """Parse string to float, return None if invalid"""
        if not value or value == 'None' or value == '-':
            return None
        try:
            return float(value.replace('%', ''))
        except:
            return None

    def download_historical_data(self, symbols: List[str], database_manager) -> Dict[str, bool]:
        """Download historical data for multiple symbols and save to database"""
        results = {}

        logging.info(f"Starting historical data download for {len(symbols)} symbols")

        for i, symbol in enumerate(symbols):
            try:
                logging.info(f"Downloading {symbol} ({i+1}/{len(symbols)})")

                # Get full historical data
                data = self.get_daily_prices(symbol, outputsize="full")

                if data['success']:
                    # Save to database
                    success = database_manager.save_stock_prices(symbol, data['data'])
                    results[symbol] = success

                    if success:
                        logging.info(f"✅ {symbol}: {len(data['data'])} records saved")
                    else:
                        logging.error(f"❌ {symbol}: Failed to save to database")
                else:
                    results[symbol] = False
                    logging.error(f"❌ {symbol}: {data.get('error', 'Unknown error')}")

                # Progress update every 5 stocks
                if (i + 1) % 5 == 0:
                    completed = sum(1 for r in results.values() if r)
                    logging.info(f"Progress: {i+1}/{len(symbols)} attempted, {completed} successful")

            except Exception as e:
                results[symbol] = False
                logging.error(f"❌ {symbol}: Exception occurred: {e}")

        # Final summary
        successful = sum(1 for r in results.values() if r)
        logging.info(f"Historical data download complete: {successful}/{len(symbols)} successful")

        return results

class CurrencyConverter:
    """USD/JPY exchange rate fetcher"""

    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest/USD"

    def get_current_rate(self) -> Optional[float]:
        """Get current USD/JPY exchange rate"""
        try:
            response = requests.get(self.base_url, timeout=10)
            data = response.json()
            return data['rates'].get('JPY')
        except Exception as e:
            logging.error(f"Error fetching exchange rate: {e}")
            return None

    def get_historical_rate(self, date: str) -> Optional[float]:
        """Get historical USD/JPY rate for specific date"""
        # For historical rates, we'd need a premium API
        # For now, return current rate as approximation
        return self.get_current_rate()

def test_stock_fetcher():
    """Test function for stock data fetcher"""
    print("Testing Stock Data Fetcher...")

    fetcher = StockDataFetcher()

    # Test current quote
    print("\n1. Testing current quote for AAPL:")
    quote = fetcher.get_current_quote("AAPL")
    print(json.dumps(quote, indent=2))

    # Test daily prices (compact)
    print("\n2. Testing daily prices for AAPL (compact):")
    prices = fetcher.get_daily_prices("AAPL", "compact")
    if prices['success']:
        print(f"Got {len(prices['data'])} days of data")
        print(f"Latest: {prices['data'][0]}")
    else:
        print(f"Error: {prices['error']}")

    # Test currency converter
    print("\n3. Testing currency converter:")
    converter = CurrencyConverter()
    rate = converter.get_current_rate()
    print(f"Current USD/JPY rate: {rate}")

if __name__ == "__main__":
    test_stock_fetcher()