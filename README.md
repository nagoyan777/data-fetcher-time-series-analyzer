# 🚀 Data Fetcher & Time Series Analyzer

A comprehensive Panel-based multi-app suite for personal time series analytics with enhanced individual axis controls and seamless cross-app navigation.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Panel](https://img.shields.io/badge/panel-1.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Key Features

### 🎛️ **Individual Axis Controls**
- **Synchronized Controls**: Text inputs + sliders for precise data alignment
- **Multi-Series Support**: Independent scaling for different data units
- **Real-time Updates**: Immediate chart updates as you adjust controls
- **Data Alignment**: Compare USD, °C, visitor counts on the same scale

### 🧭 **Cross-App Navigation**
- **Seamless Switching**: Navigate between all 4 apps with one click
- **Visual Continuity**: Consistent design across applications
- **Context Preservation**: Maintain workflow state during navigation
- **Professional Interface**: Gradient backgrounds with hover effects

### ⚡ **Manual Trigger Philosophy**
- **User-Controlled Operations**: No automatic background updates
- **One-Click Actions**: Immediate feedback for all operations
- **Real-time Progress**: Live progress indicators and status updates
- **Data Integrity**: Manual triggers ensure data quality control

## 📱 Applications

The suite consists of 4 integrated Panel applications:

| App | Port | Description | Key Features |
|-----|------|-------------|--------------|
| **📥 Data Fetcher** | 5006 | API configuration and data collection | Manual triggers, progress monitoring, API testing |
| **📈 Time Series Analyzer** | 5007 | Data visualization and analysis | Individual axis controls, multi-series plots, Linear/Log scales |
| **💾 Data Manager** | 5008 | Storage and export management | Backup creation, data export, storage statistics |
| **⚡ Update Controller** | 5009 | Manual trigger management | Update scheduling, system monitoring, trigger history |

## 🚀 Quick Start

```bash
# 1. Install dependencies (Panel-based)
pip install panel pandas plotly numpy requests aiohttp schedule python-dateutil

# 2. Run the data fetcher suite
python main.py

# 3. Access applications:
#    Data Fetcher: http://localhost:5006
#    Time Series Analyzer: http://localhost:5007
#    Data Manager: http://localhost:5008
#    Update Controller: http://localhost:5009
```

## ✨ Features

### 📥 **Data Fetching**
- **Manual Trigger Controls**: User-initiated data fetching with one-click buttons
- **Multiple API Sources**: Support for REST APIs, JSON endpoints, and custom data sources
- **Real-time Progress**: Live progress indicators and status updates
- **Error Handling**: Robust retry logic with user-friendly error messages

### 📈 **Time Series Analysis**
- **Interactive Visualization**: Plotly-based charts with zoom, pan, and hover features
- **Trend Analysis**: Time series decomposition and statistical summaries
- **Multi-Series Comparison**: Compare multiple data sources side-by-side
- **Anomaly Detection**: Automatic outlier identification and highlighting

### 💾 **Data Management**
- **Local Storage**: JSON-based file storage with automatic timestamping
- **Data Versioning**: Automatic backups for every update with rollback capability
- **Export Options**: Export to CSV, JSON, Excel formats
- **Storage Analytics**: Monitor disk usage and data quality metrics

### ⚡ **Manual Update Controls**
- **Immediate Triggers**: Instant data refresh buttons across all apps
- **Update Scheduling**: Configure manual update reminders and notifications
- **Update History**: Track all manual updates with timestamps and results
- **Batch Operations**: Update multiple data sources with single trigger

## 🏗️ Architecture (Panel Multi-App)

### **Multi-App Structure**
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

### **Cross-App Navigation**
Navigate seamlessly between applications:
- **Data Fetcher**: Configure and trigger data collection
- **Time Series Analyzer**: Visualize and analyze collected data
- **Data Manager**: Browse, backup, and export stored data
- **Update Controller**: Manage manual triggers and schedules

## 🎯 Use Cases

### **Personal Weather Monitoring**
```python
# Example: Monitor local weather data
API_CONFIG = {
    "url": "https://api.openweathermap.org/data/2.5/weather",
    "params": {"q": "Tokyo", "units": "metric"},
    "data_path": "main.temp",
    "update_frequency": "manual"  # User-triggered only
}
```

### **Stock Price Tracking**
```python
# Example: Track specific stock prices
API_CONFIG = {
    "url": "https://api.example.com/stocks/{symbol}",
    "params": {"symbol": "AAPL"},
    "data_path": "price",
    "update_frequency": "manual"
}
```

### **IoT Sensor Data**
```python
# Example: Collect IoT sensor readings
API_CONFIG = {
    "url": "http://local-sensor.local/api/data",
    "data_path": "sensor_value",
    "update_frequency": "manual"
}
```

## 🔧 Configuration

### **API Source Configuration (config/api_config.json)**
```json
{
  "sources": [
    {
      "name": "weather_tokyo",
      "url": "https://api.openweathermap.org/data/2.5/weather",
      "method": "GET",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      },
      "params": {
        "q": "Tokyo",
        "units": "metric"
      },
      "data_path": "main.temp",
      "description": "Tokyo temperature readings"
    }
  ]
}
```

### **Storage Configuration (config/storage_config.json)**
```json
{
  "format": "json",
  "backup_frequency": "every_update",
  "max_file_size_mb": 100,
  "compression": false,
  "retention_days": 365
}
```

## 📊 Data Format

### **Stored Time Series Format**
```json
{
  "metadata": {
    "source": "weather_tokyo",
    "last_updated": "2025-09-28T16:10:00Z",
    "total_records": 1440,
    "quality_score": 98.5
  },
  "data": [
    {
      "timestamp": "2025-09-28T10:00:00Z",
      "value": 23.5,
      "unit": "celsius",
      "quality": "good"
    }
  ]
}
```

## 🚀 Getting Started

### **1. Set Up Your First Data Source**
1. Open **Data Fetcher** app (http://localhost:5006)
2. Configure API endpoint and parameters
3. Test connection with "Fetch Now" button
4. Review fetched data in preview panel

### **2. Analyze Your Data**
1. Switch to **Time Series Analyzer** app (http://localhost:5007)
2. Select your data source from dropdown
3. Explore interactive charts and statistics
4. Use zoom and pan for detailed analysis

### **3. Manage Your Data**
1. Open **Data Manager** app (http://localhost:5008)
2. Browse stored data files by date
3. Create manual backups before major changes
4. Export data in preferred format

### **4. Control Updates**
1. Access **Update Controller** app (http://localhost:5009)
2. Set up manual trigger buttons for quick updates
3. Monitor update history and status
4. Configure update reminders

## 🎨 Manual Trigger Philosophy

This application emphasizes **user control** over automatic operations:
- **No Background Updates**: Data is only fetched when you explicitly trigger it
- **One-Click Operations**: Easy manual triggers across all interfaces
- **Immediate Feedback**: Real-time status updates for all operations
- **User Confirmation**: Important operations require explicit user action

## 📈 Performance Features

### **Async Operations**
- Non-blocking data fetching with progress indicators
- Responsive GUI during long-running operations
- Concurrent processing of multiple data sources

### **Memory Optimization**
- Streaming for large datasets
- Automatic memory cleanup
- Efficient data structures for time series

### **Local Caching**
- API response caching to reduce redundant calls
- Quick data reload from local storage
- Smart cache invalidation

## 🛡️ Error Handling

### **Robust API Client**
- Automatic retry with exponential backoff
- Timeout handling for slow responses
- Connection error recovery

### **Data Validation**
- Automatic data quality checks
- Format validation for API responses
- User-friendly error messages

### **Graceful Degradation**
- Continue operation when some features fail
- Offline mode for cached data
- Alternative data source fallbacks

## 🔍 Troubleshooting

### **Common Issues**

**Data Fetching Fails**
- Check internet connection
- Verify API endpoint URL and parameters
- Review API key/authentication settings

**Charts Not Displaying**
- Ensure data contains valid timestamps
- Check for sufficient data points
- Verify data format matches expected structure

**Cross-App Data Not Updating**
- Trigger manual refresh in source app
- Check shared data store status
- Restart application if needed

### **Performance Issues**
- Reduce data fetch frequency
- Clear old cached data
- Monitor memory usage in browser

## 📝 Development

See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for detailed development instructions and patterns.

### **Quick Development Setup**
```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python main.py

# Access development tools at respective ports
```

## 📚 Documentation

- [PROJECT_SPECIFICATIONS.md](PROJECT_SPECIFICATIONS.md) - Technical architecture and component details
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Development patterns and best practices
- [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - Supported data sources and API formats
- [USAGE_GUIDE.md](docs/USAGE_GUIDE.md) - Detailed user manual

## 🎯 Roadmap

### **Phase 1** (Current)
- [x] Basic Panel multi-app structure
- [x] Manual data fetching with GUI controls
- [x] Local JSON storage with versioning
- [x] Basic time series visualization

### **Phase 2** (Next)
- [ ] Advanced time series analysis (decomposition, forecasting)
- [ ] Multiple data source management
- [ ] Data export in multiple formats
- [ ] Enhanced error handling and validation

### **Phase 3** (Future)
- [ ] Custom dashboard creation
- [ ] Data source plugins architecture
- [ ] Advanced analytics and machine learning
- [ ] Real-time data streaming support

## 🤝 Contributing

This is a personal project template. Feel free to adapt and modify for your specific data fetching and analysis needs.

## 📄 License

MIT License - Feel free to use and modify for personal or commercial projects.