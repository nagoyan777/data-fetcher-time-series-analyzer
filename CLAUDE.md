# CLAUDE.md - US Stock Analysis & Investment Tracker

## Project Overview
A comprehensive Panel-based US stock analysis and personal investment tracking platform with SBI Securities integration. The application focuses on long-term investment analysis, portfolio P&L tracking, and market research for tech/growth/value investing strategies. Designed for personal analytics workflows with 10+ year data retention capabilities.

## Project Structure
```
stock_analysis_platform/
├── main.py                      # Multi-app launcher
├── apps/                        # Individual Panel applications
│   ├── data_fetcher_app.py      # Market Explorer - stock research & data fetching
│   ├── time_sync_app.py         # Portfolio Tracker - SBI investment tracking
│   ├── data_analyzer_app.py     # Stock Analyzer - technical analysis & charts
│   └── data_manager_app.py      # Database Manager - exports & maintenance
├── core/                        # Business logic
│   ├── stock_data_fetcher.py    # Yahoo Finance API with caching & rate limiting
│   ├── database_manager.py      # SQLite operations & schema management
│   └── sbi_parser.py            # SBI Securities CSV parser (planned)
├── utils/                       # Shared utilities
│   ├── shared_store.py          # Cross-app data sharing
│   ├── stock_screener.py        # Tech/Growth/Value filtering
│   └── analysis_tools.py        # Long-term analysis functions
└── data/                        # Local storage
    ├── stock_analysis.db         # SQLite database
    ├── sbi_imports/             # SBI CSV files
    ├── exports/                 # Reports & tax documents
    └── backups/                 # Database backups
```

## Technology Stack
- **Framework**: Panel (web framework for GUI)
- **Database**: SQLite (local database for 10+ year data retention)
- **Data Processing**: pandas, numpy, sqlite3
- **Visualization**: plotly (candlestick charts, portfolio dashboards)
- **Stock API**: Yahoo Finance (primary with rate limiting & caching)
- **HTTP Client**: requests, aiohttp
- **Currency Data**: Federal Reserve API (USD/JPY rates)

## Key Features
1. **US Stock Analysis**: Tech/Growth/Value stock research with 10+ year data
2. **SBI Securities Integration**: CSV import parser for portfolio tracking
3. **Portfolio P&L Tracking**: Cost basis, unrealized/realized gains, currency conversion
4. **Long-term Analysis**: Market cycle analysis, sector rotation, performance attribution
5. **Currency Handling**: USD/JPY conversion for Japanese tax reporting
6. **Data Persistence**: SQLite database with automatic backup and export
7. **Investment Categories**: Focused on Technology, Growth, and Value investing

## Applications
- **Market Explorer** (port 5006): US stock research, real-time quotes, historical data fetching
- **Portfolio Tracker** (port 5007): SBI portfolio import, P&L tracking, performance metrics
- **Stock Analyzer** (port 5008): Technical analysis, candlestick charts, indicators (SMA, RSI, Bollinger)
- **Database Manager** (port 5009): Data export (JSON/CSV/Excel), backup, maintenance

## Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Access applications at respective ports
```

## Development Guidelines

### Code Style
- Use async/await for all I/O operations
- Implement manual trigger patterns (no automatic background updates)
- Follow Panel parameterized class patterns
- Use shared state management for cross-app communication

### Testing
- Manual testing checklist provided in DEVELOPMENT_GUIDE.md
- Test with varying dataset sizes
- Monitor memory usage and response times
- Verify cross-app data propagation

### Error Handling
- User-friendly error messages
- Graceful degradation for failed operations
- Retry logic with exponential backoff
- Data validation for API responses

## Commands

### Development
```bash
python main.py                  # Start all applications
```

### Testing
```bash
# Manual testing through web interface
# Performance monitoring through browser dev tools
```

### Lint/Type Check
```bash
# Add specific linting commands here when implemented
```

## Configuration
- Database: `data/stock_analysis.db` (SQLite)
- Exports: `data/exports/` (JSON default, CSV, Excel)
- Backups: `data/backups/` (automated SQLite backups)
- SBI Imports: `data/sbi_imports/` (CSV files)

## Data Format
- **Database Schema**: SQLite with tables for stocks, prices, portfolio, transactions, exchange rates
- **Export Formats**:
  - JSON (default): Single file with structured data and metadata
  - CSV: Multiple files for complex exports
  - Excel: Multi-sheet workbooks
- **Stock Data**: OHLCV with adjusted close, stored with daily granularity

## Performance Targets
- Data fetch operations: < 5 seconds
- GUI responsiveness: < 100ms for user interactions
- Data loading from storage: < 1 second
- Chart rendering: < 2 seconds for 10K+ points

## Manual Trigger Philosophy
The application emphasizes user control over automatic operations:
- No background updates without explicit user action
- One-click operations with immediate feedback
- Real-time status updates for all operations
- User confirmation for important operations

## Current Implementation Status (✅ Completed)
- **Market Explorer**: Fetch real-time quotes, download historical data for 19 pre-configured stocks
- **Portfolio Tracker**: Ready for SBI CSV import, P&L calculations, currency conversion
- **Stock Analyzer**: Candlestick charts with SMA, RSI, Bollinger Bands indicators
- **Database Manager**: Export to JSON (default), CSV, Excel; backup & optimization tools
- **Rate Limiting**: 2-second delay between API calls with 5-minute caching
- **Error Handling**: Graceful handling of API limits, empty data, invalid symbols

## Known Limitations
- Yahoo Finance API rate limiting (mitigated with caching)
- SBI CSV parser not yet implemented (manual portfolio entry required)
- Limited to pre-configured stock list (can be expanded in database)

## Roadmap
- **Phase 1** ✅ (Completed): Panel multi-app structure, Yahoo Finance integration, SQLite database
- **Phase 2** (Next): SBI CSV parser implementation, portfolio performance analytics
- **Phase 3** (Future): Additional technical indicators, backtesting, ML predictions

## Documentation
- [README.md](README.md) - User guide and quick start
- [PROJECT_SPECIFICATIONS.md](PROJECT_SPECIFICATIONS.md) - Technical architecture
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Development patterns and best practices

---

# Claude Code Implementation Methodology

## Deep Analysis Approach (Adapted from Literature Analysis Project)

**Philosophy**: Prioritize thorough analysis and strategic planning over quick fixes to prevent recurring issues and architectural debt.

### 1. Investigation Phase (Required First Step)
```
BEFORE any implementation, Claude must:
✅ Root cause analysis: Why did this issue occur?
✅ Pattern recognition: Is this part of a larger architectural problem?
✅ Dependencies mapping: What other components might be affected?
✅ Historical context: What previous decisions led to this state?
✅ Data flow analysis: How does data move through the system?
```

### 2. Planning Phase (Present Options)
```
Claude must provide:
✅ Multiple solution paths (3-4 different approaches)
✅ Trade-offs analysis for each approach
✅ Impact assessment on broader system
✅ Future-proofing considerations
✅ Resource requirements (time, complexity, maintenance)
✅ Risk assessment for each option
```

### 3. Decision Phase (Wait for User Approval)
```
Claude must:
✅ Present recommendation with clear rationale
✅ Wait for explicit user approval before implementation
✅ Never assume which approach to take
✅ Ask clarifying questions if requirements unclear
```

### 4. Implementation Phase (Only After Approval)
```
Claude must:
✅ Break large changes into testable increments
✅ Validate functionality at each step
✅ Document decisions and rationale
✅ Provide rollback plan for complex changes
✅ Test thoroughly before marking complete
```

## Process Control Keywords

**User can use these to control Claude's behavior:**
- **"Plan only"** - Provide analysis and options, do not implement
- **"Debug first"** - Analyze the issue thoroughly before proposing solutions
- **"Implement after approval"** - Wait for explicit go-ahead
- **"Check status first"** - Verify current system state before proceeding

## Implementation History & Architectural Decisions

### ❌ Rejected Approaches (For Data Fetcher Context)
- **Real-time automatic fetching** - Rejected, prefer manual trigger control
- **Single monolithic app** - Rejected, multi-app architecture provides better UX
- **Database storage** - Rejected for simplicity, file-based storage sufficient
- **Complex scheduling system** - Rejected, manual triggers with reminders preferred

### ✅ Approved Architecture (For Data Fetcher)
- **Panel multi-app architecture** - Primary approach for responsive UX
- **Manual trigger philosophy** - User-controlled data collection
- **File-based storage with versioning** - Simple and reliable for personal use
- **Async processing with progress indicators** - Non-blocking UI operations
- **JSON configuration system** - Easy to modify and version control

### ⚠️ Known Issues & Solutions (Data Fetcher Specific)
- **API rate limiting** - Implement exponential backoff and respect limits
- **Large time series rendering** - Use data sampling and progressive loading
- **Cross-app data sync** - Verify shared store updates before UI refresh
- **Memory usage with large datasets** - Implement streaming and cleanup
- **Configuration file corruption** - Add JSON validation and backup/restore

## Common Debugging Checklist

**Before implementing any fix:**
1. Check running processes: `lsof -ti:5006,5007,5008,5009`
2. Verify data integrity: Check JSON structure and API responses
3. Review logs for patterns: Look for recurring error messages
4. Test with minimal data: Isolate the core issue with small datasets
5. Reference this document: Check for previous similar issues
6. Verify API endpoints: Test external data sources independently

## Communication Patterns

### ❌ Avoid These Patterns
```
User: "API fetching doesn't work"
Claude: [Immediately starts implementing multiple solutions]
```

### ✅ Preferred Patterns
```
User: "API fetching doesn't work"
Claude: "Let me analyze the issue systematically..."
Claude: [Investigation: Check API endpoint, authentication, rate limits, data format]
Claude: "Root cause: API key authentication failure. I can fix this with approaches A, B, or C. Here are the trade-offs..."
Claude: "I recommend approach B (environment variable configuration) because... Should I proceed?"
User: "Yes, go with B"
Claude: [Implements only approved approach B]
```

## Quality Standards

**Claude must ensure:**
- **Sustainable solutions** over quick fixes
- **Architectural consistency** with approved Panel multi-app patterns
- **Thorough testing** with various data sources and sizes
- **Clear documentation** of changes and rationale
- **Future maintainability** considerations for personal analytics workflows
- **Manual trigger philosophy** - maintain user control over all operations

## Data Fetcher Specific Guidelines

### Performance Considerations
- Always test with realistic data volumes (1K-10K data points)
- Monitor memory usage during time series processing
- Verify UI responsiveness during async operations
- Test cross-app data sharing under load

### API Integration Best Practices
- Always implement retry logic with exponential backoff
- Validate API responses before processing
- Handle rate limiting gracefully with user feedback
- Cache responses appropriately to reduce API calls

### User Experience Priorities
- Manual triggers must provide immediate feedback
- Progress indicators for all long-running operations
- Clear error messages with suggested solutions
- Maintain responsive UI during background processing