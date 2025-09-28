# CLAUDE.md - Data Fetcher & Time Series Analyzer

## Project Overview
A comprehensive Panel-based data fetching and time series analysis platform with manual trigger controls, responsive UX, and local storage management. The application emphasizes user-controlled data collection with powerful time series visualization for personal analytics workflows.

## Project Structure
```
data_fetcher_mock/
├── main.py                      # Multi-app launcher
├── apps/                        # Individual Panel applications
│   ├── data_fetcher_app.py      # Data fetching interface
│   ├── data_analyzer_app.py     # Time series analysis
│   ├── data_manager_app.py      # Storage management
│   └── trigger_controller_app.py # Update controls
├── core/                        # Business logic
│   ├── data_fetcher.py          # Fetching engine
│   ├── storage_manager.py       # File operations
│   ├── time_series_analyzer.py  # Analysis algorithms
│   └── update_scheduler.py      # Trigger management
├── utils/                       # Shared utilities
│   ├── shared_store.py          # Cross-app data sharing
│   ├── api_client.py            # HTTP client with retry
│   └── performance_utils.py     # Optimization tools
└── data/                        # Local storage
    ├── raw_data/                # Fetched data
    ├── processed_data/          # Cleaned data
    ├── cache/                   # API cache
    └── backups/                 # Data backups
```

## Technology Stack
- **Framework**: Panel (web framework for GUI)
- **Data Processing**: pandas, numpy
- **Visualization**: plotly
- **HTTP Client**: requests, aiohttp
- **Storage**: JSON files, local filesystem
- **Async Processing**: asyncio

## Key Features
1. **Manual Trigger Controls**: User-initiated data fetching with one-click buttons
2. **Multiple API Sources**: Support for REST APIs and JSON endpoints
3. **Real-time Progress**: Live progress indicators and status updates
4. **Interactive Visualization**: Plotly-based charts with zoom, pan, and hover
5. **Local Storage**: JSON-based file storage with automatic timestamping
6. **Data Versioning**: Automatic backups with rollback capability
7. **Cross-App Navigation**: Seamless navigation between applications

## Applications
- **Data Fetcher** (port 5006): Configure and trigger data collection
- **Time Series Analyzer** (port 5007): Visualize and analyze collected data
- **Data Manager** (port 5008): Browse, backup, and export stored data
- **Update Controller** (port 5009): Manage manual triggers and schedules

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
- API sources: `config/api_config.json`
- Storage settings: `config/storage_config.json`
- Application settings: `config/app_config.json`

## Data Format
Time series data stored in JSON format with metadata, schema, and data arrays. Each record includes timestamp, value, unit, and quality indicators.

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

## Roadmap
- **Phase 1** (Current): Basic Panel multi-app structure, manual data fetching, local storage
- **Phase 2** (Next): Advanced time series analysis, multiple data source management
- **Phase 3** (Future): Custom dashboard creation, data source plugins, machine learning integration

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