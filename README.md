# US Stock Analysis & Investment Tracker

A comprehensive Panel-based platform for US stock analysis and investment tracking, designed for long-term investors using SBI Securities in Japan.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application suite
python main.py

# Access the apps in your browser:
# - Market Explorer: http://localhost:5006
# - Portfolio Tracker: http://localhost:5007
# - Stock Analyzer: http://localhost:5008
# - Database Manager: http://localhost:5009
```

## Features

### 📊 Market Explorer (Port 5006)
- Browse 19 pre-configured US stocks (Tech, Growth, Value categories)
- Fetch real-time quotes from Yahoo Finance
- Download historical data (1 month to 10+ years)
- View detailed stock information and metrics

### 💼 Portfolio Tracker (Port 5007)
- Import SBI Securities transactions (CSV support planned)
- Track portfolio holdings and performance
- Calculate P&L in USD and JPY
- Monitor unrealized gains/losses

### 📈 Stock Analyzer (Port 5008)
- Interactive candlestick charts with Plotly
- Technical indicators: SMA (20/50), RSI, Bollinger Bands
- Multiple timeframes: 1M, 3M, 6M, 1Y, 5Y, 10Y, All
- Volume analysis and price patterns

### 🗄️ Database Manager (Port 5009)
- Export data in JSON (default), CSV, or Excel formats
- Backup SQLite database
- Optimize database performance
- Monitor data statistics

## Stock Coverage

### Technology Stocks
- AAPL (Apple), GOOGL (Alphabet), MSFT (Microsoft)
- NVDA (NVIDIA), META (Meta), AMZN (Amazon)

### Growth Stocks
- TSLA (Tesla), NFLX (Netflix)
- AMD (Advanced Micro Devices), CRM (Salesforce)

### Value Stocks
- BRK.B (Berkshire Hathaway), JPM (JPMorgan Chase)
- WMT (Walmart), PG (Procter & Gamble)
- JNJ (Johnson & Johnson), KO (Coca-Cola)

### Market ETFs
- SPY (S&P 500), QQQ (NASDAQ-100), VTI (Total Market)

## Data Storage

All data is stored locally in SQLite database:
- `data/stock_analysis.db` - Main database
- `data/exports/` - Exported files
- `data/backups/` - Database backups
- `data/sbi_imports/` - SBI CSV files (future)

## Export Formats

- **JSON** (Default): Structured data with metadata
- **CSV**: Simple tabular format
- **Excel**: Multi-sheet workbooks

## Rate Limiting

The app includes built-in rate limiting for Yahoo Finance:
- 2-second delay between API calls
- 5-minute cache for fetched data
- Graceful handling of rate limit errors

## Requirements

- Python 3.8+
- Panel 1.0+
- See `requirements.txt` for full list

## Known Limitations

- Yahoo Finance rate limiting (use fetch buttons sparingly)
- SBI CSV parser not yet implemented
- Limited to pre-configured stock list

## Support

For issues or questions, check the documentation:
- `CLAUDE.md` - Development guide
- `PROJECT_SPECIFICATIONS.md` - Technical details

## License

This is a personal project for investment tracking and analysis.