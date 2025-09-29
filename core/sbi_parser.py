"""
SBI Securities CSV Parser
Parses transaction data from SBI Securities CSV exports for US stock transactions
"""
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
import re
import json
from pathlib import Path

class SBICSVParser:
    """Parser for SBI Securities US stock transaction CSV files"""

    def __init__(self):
        self.supported_encodings = ['utf-8', 'shift-jis', 'cp932']
        self.date_formats = ['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y']

    def parse_csv_file(self, file_path: str) -> Dict:
        """
        Parse SBI Securities CSV file

        Args:
            file_path: Path to CSV file

        Returns:
            Dict with parsed transactions and metadata
        """
        try:
            # Try different encodings
            df = None
            encoding_used = None

            for encoding in self.supported_encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    encoding_used = encoding
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                return {'success': False, 'error': 'Could not decode CSV file with any supported encoding'}

            # Detect CSV format
            format_type = self._detect_csv_format(df)

            if format_type == 'sbi_us_transactions':
                transactions = self._parse_sbi_us_transactions(df)
            elif format_type == 'generic_transactions':
                transactions = self._parse_generic_format(df)
            else:
                return {'success': False, 'error': f'Unsupported CSV format: {format_type}'}

            return {
                'success': True,
                'transactions': transactions,
                'total_count': len(transactions),
                'encoding_used': encoding_used,
                'format_type': format_type,
                'file_path': file_path,
                'parsed_at': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Error parsing CSV file {file_path}: {e}")
            return {'success': False, 'error': str(e)}

    def _detect_csv_format(self, df: pd.DataFrame) -> str:
        """Detect the format of the CSV file"""
        columns = [col.lower() for col in df.columns]

        # SBI US stock transaction format detection
        if any('date' in col or '日付' in col for col in columns):
            if any('symbol' in col or 'ticker' in col or '銘柄' in col for col in columns):
                if any('buy' in col or 'sell' in col or '売買' in col for col in columns):
                    return 'sbi_us_transactions'

        # Generic transaction format
        required_fields = ['date', 'symbol', 'action', 'quantity', 'price']
        if all(any(field in col for col in columns) for field in required_fields):
            return 'generic_transactions'

        return 'unknown'

    def _parse_sbi_us_transactions(self, df: pd.DataFrame) -> List[Dict]:
        """Parse SBI-specific US stock transaction format"""
        transactions = []

        # Map column names (handle both English and Japanese)
        column_mapping = self._create_column_mapping(df.columns)

        for idx, row in df.iterrows():
            try:
                # Skip header rows or empty rows
                if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                    continue

                transaction = self._parse_transaction_row(row, column_mapping, idx)
                if transaction:
                    transactions.append(transaction)

            except Exception as e:
                logging.warning(f"Error parsing row {idx}: {e}")
                continue

        return transactions

    def _parse_generic_format(self, df: pd.DataFrame) -> List[Dict]:
        """Parse generic transaction format"""
        transactions = []

        for idx, row in df.iterrows():
            try:
                transaction = {
                    'date': self._parse_date(str(row.get('Date', row.get('date', ''))).strip()),
                    'symbol': str(row.get('Symbol', row.get('symbol', ''))).strip().upper(),
                    'action': self._normalize_action(str(row.get('Action', row.get('action', ''))).strip()),
                    'quantity': self._parse_float(row.get('Quantity', row.get('quantity', 0))),
                    'price_usd': self._parse_float(row.get('Price', row.get('price', 0))),
                    'commission_usd': self._parse_float(row.get('Commission', row.get('commission', 0))),
                    'total_usd': self._parse_float(row.get('Total', row.get('total', 0))),
                    'exchange_rate': self._parse_float(row.get('Exchange_Rate', row.get('exchange_rate', 150.0))),
                    'total_jpy': self._parse_float(row.get('Total_JPY', row.get('total_jpy', 0))),
                    'raw_data': row.to_dict()
                }

                # Validate required fields
                if self._validate_transaction(transaction):
                    transactions.append(transaction)

            except Exception as e:
                logging.warning(f"Error parsing generic row {idx}: {e}")
                continue

        return transactions

    def _create_column_mapping(self, columns: List[str]) -> Dict[str, str]:
        """Create mapping from actual column names to standard field names"""
        mapping = {}

        for col in columns:
            col_lower = col.lower()

            # Date fields
            if any(keyword in col_lower for keyword in ['date', '日付', '取引日']):
                mapping['date'] = col

            # Symbol fields
            elif any(keyword in col_lower for keyword in ['symbol', 'ticker', '銘柄', 'コード']):
                mapping['symbol'] = col

            # Action fields (Buy/Sell)
            elif any(keyword in col_lower for keyword in ['action', 'type', '売買', '取引種別']):
                mapping['action'] = col

            # Quantity fields
            elif any(keyword in col_lower for keyword in ['quantity', '数量', 'shares', '株数']):
                mapping['quantity'] = col

            # Price fields
            elif any(keyword in col_lower for keyword in ['price', '単価', '価格']) and 'usd' in col_lower:
                mapping['price_usd'] = col

            # Commission fields
            elif any(keyword in col_lower for keyword in ['commission', '手数料', 'fee']):
                mapping['commission_usd'] = col

            # Total USD fields
            elif any(keyword in col_lower for keyword in ['total', '合計']) and 'usd' in col_lower:
                mapping['total_usd'] = col

            # Exchange rate fields
            elif any(keyword in col_lower for keyword in ['exchange', 'rate', '為替', 'レート']):
                mapping['exchange_rate'] = col

            # Total JPY fields
            elif any(keyword in col_lower for keyword in ['total', '合計']) and ('jpy' in col_lower or '円' in col_lower):
                mapping['total_jpy'] = col

        return mapping

    def _parse_transaction_row(self, row: pd.Series, column_mapping: Dict[str, str], row_idx: int) -> Optional[Dict]:
        """Parse a single transaction row"""
        try:
            # Extract data using column mapping
            date_str = str(row.get(column_mapping.get('date', ''), '')).strip()
            symbol = str(row.get(column_mapping.get('symbol', ''), '')).strip().upper()
            action = str(row.get(column_mapping.get('action', ''), '')).strip()
            quantity = row.get(column_mapping.get('quantity', ''), 0)
            price_usd = row.get(column_mapping.get('price_usd', ''), 0)
            commission_usd = row.get(column_mapping.get('commission_usd', ''), 0)
            total_usd = row.get(column_mapping.get('total_usd', ''), 0)
            exchange_rate = row.get(column_mapping.get('exchange_rate', ''), 150.0)
            total_jpy = row.get(column_mapping.get('total_jpy', ''), 0)

            # Parse and validate data
            transaction = {
                'date': self._parse_date(date_str),
                'symbol': symbol,
                'action': self._normalize_action(action),
                'quantity': self._parse_float(quantity),
                'price_usd': self._parse_float(price_usd),
                'commission_usd': self._parse_float(commission_usd),
                'total_usd': self._parse_float(total_usd),
                'exchange_rate': self._parse_float(exchange_rate),
                'total_jpy': self._parse_float(total_jpy),
                'raw_data': row.to_dict()
            }

            # Calculate missing values
            if transaction['total_usd'] == 0 and transaction['quantity'] > 0 and transaction['price_usd'] > 0:
                transaction['total_usd'] = (transaction['quantity'] * transaction['price_usd']) + transaction['commission_usd']

            if transaction['total_jpy'] == 0 and transaction['total_usd'] > 0 and transaction['exchange_rate'] > 0:
                transaction['total_jpy'] = transaction['total_usd'] * transaction['exchange_rate']

            # Validate transaction
            if self._validate_transaction(transaction):
                return transaction

        except Exception as e:
            logging.warning(f"Error parsing transaction row {row_idx}: {e}")

        return None

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to YYYY-MM-DD format"""
        if not date_str or date_str.lower() in ['nan', 'none', '']:
            return None

        # Clean the date string
        date_str = re.sub(r'[^\d/\-]', '', date_str)

        for date_format in self.date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue

        logging.warning(f"Could not parse date: {date_str}")
        return None

    def _parse_float(self, value) -> float:
        """Parse value to float, handling various formats"""
        if pd.isna(value) or value == '' or value is None:
            return 0.0

        # Convert to string first
        value_str = str(value).strip()

        # Remove currency symbols and commas
        value_str = re.sub(r'[,$¥￥]', '', value_str)

        # Handle parentheses (negative values)
        if '(' in value_str and ')' in value_str:
            value_str = '-' + re.sub(r'[()]', '', value_str)

        try:
            return float(value_str)
        except ValueError:
            return 0.0

    def _normalize_action(self, action: str) -> str:
        """Normalize action to BUY or SELL"""
        if not action:
            return 'UNKNOWN'

        action_lower = action.lower()

        # Buy variations
        if any(keyword in action_lower for keyword in ['buy', '買', 'purchase', 'acquire']):
            return 'BUY'

        # Sell variations
        elif any(keyword in action_lower for keyword in ['sell', '売', 'sale', 'dispose']):
            return 'SELL'

        # Dividend variations
        elif any(keyword in action_lower for keyword in ['dividend', '配当', 'div']):
            return 'DIVIDEND'

        else:
            return action.upper()

    def _validate_transaction(self, transaction: Dict) -> bool:
        """Validate transaction data"""
        required_fields = ['date', 'symbol', 'action', 'quantity', 'price_usd']

        # Check required fields exist and are valid
        for field in required_fields:
            if field not in transaction or transaction[field] is None:
                return False

        # Check date format
        if not transaction['date']:
            return False

        # Check symbol is not empty
        if not transaction['symbol'] or len(transaction['symbol']) < 1:
            return False

        # Check action is valid
        if transaction['action'] not in ['BUY', 'SELL', 'DIVIDEND']:
            return False

        # Check numeric values are positive (except for sells which can be negative)
        if transaction['quantity'] <= 0:
            return False

        if transaction['price_usd'] <= 0:
            return False

        return True

    def create_sample_csv(self, output_path: str = None) -> str:
        """Create a sample SBI CSV file for testing"""
        if output_path is None:
            output_path = "sample_sbi_transactions.csv"

        sample_data = [
            {
                'Date': '2024-01-15',
                'Symbol': 'AAPL',
                'Company': 'Apple Inc.',
                'Action': 'BUY',
                'Quantity': 10,
                'Price(USD)': 185.50,
                'Commission(USD)': 1.50,
                'Total(USD)': 1856.50,
                'Exchange_Rate': 148.20,
                'Total(JPY)': 275073
            },
            {
                'Date': '2024-02-10',
                'Symbol': 'GOOGL',
                'Company': 'Alphabet Inc.',
                'Action': 'BUY',
                'Quantity': 5,
                'Price(USD)': 142.30,
                'Commission(USD)': 1.50,
                'Total(USD)': 713.00,
                'Exchange_Rate': 149.50,
                'Total(JPY)': 106594
            },
            {
                'Date': '2024-03-20',
                'Symbol': 'MSFT',
                'Company': 'Microsoft Corporation',
                'Action': 'BUY',
                'Quantity': 8,
                'Price(USD)': 412.80,
                'Commission(USD)': 1.50,
                'Total(USD)': 3303.90,
                'Exchange_Rate': 151.00,
                'Total(JPY)': 498889
            }
        ]

        df = pd.DataFrame(sample_data)
        df.to_csv(output_path, index=False)

        return output_path

def test_sbi_parser():
    """Test function for SBI parser"""
    print("Testing SBI CSV Parser...")

    parser = SBICSVParser()

    # Create sample CSV
    sample_file = parser.create_sample_csv("test_sbi_transactions.csv")
    print(f"Created sample CSV: {sample_file}")

    # Parse the sample file
    result = parser.parse_csv_file(sample_file)

    if result['success']:
        print(f"\n✅ Successfully parsed {result['total_count']} transactions")
        print(f"Format: {result['format_type']}")
        print(f"Encoding: {result['encoding_used']}")

        print("\nSample transactions:")
        for i, tx in enumerate(result['transactions'][:3]):
            print(f"{i+1}. {tx['date']} - {tx['action']} {tx['quantity']} {tx['symbol']} @ ${tx['price_usd']}")

    else:
        print(f"❌ Error: {result['error']}")

    # Clean up
    Path(sample_file).unlink(missing_ok=True)

if __name__ == "__main__":
    test_sbi_parser()