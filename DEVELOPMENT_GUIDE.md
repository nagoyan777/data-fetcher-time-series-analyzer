# 🚀 Data Fetcher & Time Series Analyzer - Development Guide

## 🎯 Quick Start for Developers

**Focus**: Manual-triggered data fetching with responsive Panel GUI for personal time series analysis

### **Getting the Project Running (5 minutes)**
```bash
# 1. Navigate to project directory
cd /Users/akihironagoya/MyProjects/Experiments/20250928_data_fetcher_mock

# 2. Check current files
ls -la
# Expected: main.py, apps/, core/, data/, requirements.txt

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the data fetcher suite
python main.py

# 5. Access applications:
#    Data Fetcher: http://localhost:5006
#    Time Series Analyzer: http://localhost:5007
#    Data Manager: http://localhost:5008
#    Update Controller: http://localhost:5009
```

### **Key Files to Understand First**
1. **main.py** - Multi-app launcher, start here
2. **apps/data_fetcher_app.py** - Main data fetching interface
3. **core/data_fetcher.py** - Core fetching logic
4. **PROJECT_SPECIFICATIONS.md** - Technical details (reference document)

## 🔧 Development Patterns (Manual Control & Performance Focused)

### **Manual Trigger Pattern**
```python
# Core pattern: User-initiated actions only
@param.depends('fetch_button', watch=True)
def manual_fetch_trigger(self):
    """Execute data fetch only when user clicks button"""
    if self.fetch_button:
        # Reset button state
        self.fetch_button = False

        # Execute async fetch with progress indicator
        self.fetch_status = "Fetching..."
        asyncio.create_task(self._fetch_data_async())

async def _fetch_data_async(self):
    """Non-blocking data fetch with error handling"""
    try:
        # Show progress to user
        self.progress_bar.value = 0

        # Fetch data with timeout
        data = await self.api_client.fetch_with_timeout(
            url=self.api_url,
            timeout=30
        )

        # Update progress
        self.progress_bar.value = 50

        # Store data locally
        await self.storage_manager.save_data_async(data)

        # Complete
        self.progress_bar.value = 100
        self.fetch_status = f"✅ Fetched {len(data)} records"

    except Exception as e:
        self.fetch_status = f"❌ Error: {str(e)}"
```

### **Shared State Management**
```python
# Cross-app data sharing pattern
class SharedDataStore(param.Parameterized):
    """Centralized data store for all apps"""

    current_data = param.Parameter(default=None)
    last_update = param.Parameter(default=None)
    data_sources = param.List(default=[])

    def update_data(self, new_data, source_name):
        """Update shared data and notify all apps"""
        self.current_data = new_data
        self.last_update = datetime.now()
        if source_name not in self.data_sources:
            self.data_sources.append(source_name)

# Usage in apps
class DataAnalyzerApp(param.Parameterized):
    def __init__(self, shared_store):
        super().__init__()
        self.shared_store = shared_store

        # Watch for data updates
        self.shared_store.param.watch(
            self._on_data_update, 'current_data'
        )
```

### **Time Series Processing Pattern**
```python
# Efficient time series handling
class TimeSeriesProcessor:
    """Optimized time series operations"""

    @staticmethod
    def process_raw_data(raw_data, data_path="value"):
        """Convert raw API response to time series DataFrame"""
        # Extract time series from nested JSON
        if isinstance(raw_data, dict):
            if 'data' in raw_data:
                time_series = raw_data['data']
            else:
                time_series = [raw_data]  # Single point
        else:
            time_series = raw_data

        # Create DataFrame with proper datetime index
        df = pd.DataFrame(time_series)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # Sort by time and remove duplicates
        df.sort_index(inplace=True)
        df = df[~df.index.duplicated(keep='last')]

        return df

    @staticmethod
    def create_plotly_chart(df, title="Time Series"):
        """Create responsive time series chart"""
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['value'],
            mode='lines+markers',
            name='Value',
            line=dict(width=2),
            marker=dict(size=4)
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Value",
            hovermode='x unified',
            showlegend=True,
            height=400
        )

        return fig
```

### **API Client Pattern with Retry Logic**
```python
# Robust API client with error handling
class APIClient:
    """HTTP client with retry and timeout handling"""

    def __init__(self, base_url, timeout=30, max_retries=3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = aiohttp.ClientSession()

    async def fetch_with_retry(self, endpoint, params=None):
        """Fetch data with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    raise e

                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
```

### **Storage Manager Pattern**
```python
# Local file storage with versioning
class StorageManager:
    """Local data storage with backup and versioning"""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw_data"
        self.processed_dir = self.data_dir / "processed_data"
        self.backup_dir = self.data_dir / "backups"

        # Create directories
        for dir_path in [self.raw_dir, self.processed_dir, self.backup_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    async def save_data_async(self, data, source_name, create_backup=True):
        """Save data with automatic backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{source_name}_{timestamp}.json"

        # Save raw data
        raw_file = self.raw_dir / filename
        with open(raw_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        # Create backup if requested
        if create_backup:
            backup_file = self.backup_dir / filename
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        return raw_file

    def list_data_files(self, data_type="raw"):
        """List available data files"""
        target_dir = self.raw_dir if data_type == "raw" else self.processed_dir
        return list(target_dir.glob("*.json"))
```

## 🎨 Panel GUI Development Patterns

### **Responsive Layout Pattern**
```python
def create_responsive_layout(self):
    """Create responsive multi-column layout"""

    # Control panel (left side)
    control_panel = pn.Column(
        "## Data Fetching Controls",
        self.api_url_input,
        self.fetch_button,
        self.progress_bar,
        self.status_indicator,
        width=300,
        margin=(10, 10)
    )

    # Main content (right side)
    main_content = pn.Column(
        "## Live Data Preview",
        self.data_table,
        self.time_series_plot,
        sizing_mode="stretch_width"
    )

    # Responsive row layout
    return pn.Row(
        control_panel,
        main_content,
        sizing_mode="stretch_width"
    )
```

### **Real-time Update Pattern**
```python
# Live status updates without page refresh
class FetchStatusIndicator(param.Parameterized):
    status = param.String(default="Ready")
    color = param.String(default="blue")

    def view(self):
        return pn.pane.HTML(
            f'<div style="padding:10px; background-color:{self.color}; color:white; border-radius:5px;">'
            f'{self.status}</div>',
            sizing_mode="stretch_width"
        )

    def update_status(self, status, status_type="info"):
        """Update status with appropriate color"""
        colors = {
            "info": "#007bff",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545"
        }
        self.status = status
        self.color = colors.get(status_type, "#007bff")
```

## 📊 Data Quality & Validation

### **API Response Validation**
```python
def validate_api_response(data):
    """Validate API response structure and content"""
    validation_results = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "quality_score": 100
    }

    # Check basic structure
    if not isinstance(data, (dict, list)):
        validation_results["is_valid"] = False
        validation_results["errors"].append("Data is not JSON object or array")
        return validation_results

    # Check for time series data
    if isinstance(data, dict) and 'data' in data:
        time_series = data['data']
    elif isinstance(data, list):
        time_series = data
    else:
        validation_results["warnings"].append("Could not identify time series data")
        validation_results["quality_score"] -= 20
        return validation_results

    # Validate time series structure
    required_fields = ['timestamp', 'value']
    for i, record in enumerate(time_series[:10]):  # Check first 10 records
        if not isinstance(record, dict):
            validation_results["errors"].append(f"Record {i} is not an object")
            validation_results["is_valid"] = False
            continue

        for field in required_fields:
            if field not in record:
                validation_results["warnings"].append(f"Missing {field} in record {i}")
                validation_results["quality_score"] -= 5

    return validation_results
```

## 🔧 Performance Optimization

### **Async Operations**
- Use `asyncio` for all I/O operations
- Implement progress indicators for long-running tasks
- Non-blocking GUI updates

### **Memory Management**
- Stream large datasets instead of loading entirely into memory
- Implement data pagination for visualization
- Clear unused data from memory after processing

### **Caching Strategy**
- Cache API responses to reduce redundant calls
- Store processed data for quick reload
- Implement cache expiration based on data source update frequency

## 🚨 Error Handling Best Practices

### **User-Friendly Error Messages**
```python
def handle_fetch_error(self, error):
    """Convert technical errors to user-friendly messages"""
    error_messages = {
        aiohttp.ClientConnectorError: "❌ Cannot connect to data source. Check your internet connection.",
        aiohttp.ClientResponseError: "❌ Data source returned an error. Please check your API settings.",
        asyncio.TimeoutError: "⏱️ Request timed out. The data source might be slow or unavailable.",
        json.JSONDecodeError: "❌ Received invalid data format from source.",
    }

    user_message = error_messages.get(type(error), f"❌ Unexpected error: {str(error)}")
    self.status_indicator.update_status(user_message, "error")
```

### **Graceful Degradation**
- Continue operation even if some features fail
- Provide alternative data sources
- Offline mode for previously cached data

## 🧪 Testing Strategy

### **Manual Testing Checklist**
1. **Data Fetching**:
   - [ ] Manual trigger buttons work
   - [ ] Progress indicators show during fetch
   - [ ] Error handling displays user-friendly messages
   - [ ] Data validation catches malformed responses

2. **Data Storage**:
   - [ ] Files saved with correct timestamps
   - [ ] Backups created automatically
   - [ ] Data can be loaded from storage

3. **Time Series Analysis**:
   - [ ] Charts render correctly
   - [ ] Interactive features work (zoom, pan)
   - [ ] Multiple time series can be compared

4. **Cross-App Communication**:
   - [ ] Data updates propagate between apps
   - [ ] Navigation between apps works
   - [ ] Shared state remains consistent

### **Performance Testing**
- Test with datasets of varying sizes (100, 1K, 10K, 100K points)
- Measure response times for each operation
- Monitor memory usage during long sessions
- Test concurrent operations (multiple fetches)

## 📝 Development Workflow

1. **Start Development Server**: `python main.py`
2. **Make Changes**: Edit files in `apps/`, `core/`, or `utils/`
3. **Test Changes**: Manual testing in browser
4. **Check Performance**: Monitor memory and response times
5. **Commit Changes**: Git commit with descriptive message

## 🎯 Next Development Steps

1. **Phase 1**: Basic data fetching and storage
2. **Phase 2**: Time series analysis and visualization
3. **Phase 3**: Advanced analytics and forecasting
4. **Phase 4**: Multiple data source integration
5. **Phase 5**: Automated monitoring and alerting