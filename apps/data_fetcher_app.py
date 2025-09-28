"""
Data Fetcher App - Panel Implementation
Manual trigger controls for API data fetching with progress monitoring
"""
import panel as pn
import pandas as pd
import asyncio
import requests
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_store import shared_store
from utils.navigation import create_navigation_bar, create_quick_actions_panel, create_app_status_indicator

class DataFetcherApp:
    """Data fetching interface with manual trigger controls"""

    def __init__(self):
        self.api_url = pn.widgets.TextInput(
            name="API URL",
            value="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            placeholder="Enter API endpoint URL"
        )

        self.data_path = pn.widgets.TextInput(
            name="Data Path",
            value="bitcoin.usd",
            placeholder="e.g. main.temp or bitcoin.usd"
        )

        self.fetch_button = pn.widgets.Button(
            name="🔍 Fetch Data Now",
            button_type="primary",
            width=200
        )

        self.test_button = pn.widgets.Button(
            name="🧪 Test Connection",
            button_type="light",
            width=200
        )

        self.progress_bar = pn.indicators.Progress(
            name="Fetch Progress",
            value=0,
            width=400,
            bar_color="success"
        )

        self.status_indicator = pn.pane.HTML(
            """<div style="padding: 10px; background: #e9ecef; border-radius: 5px;">
            <strong>Status:</strong> Ready to fetch data
            </div>""",
            width=400
        )

        self.data_preview = pn.pane.JSON(
            object={},
            name="API Response Preview",
            height=300
        )

        self.fetch_history = pn.widgets.Tabulator(
            value=pd.DataFrame(columns=['Timestamp', 'Source', 'Status', 'Data Points']),
            pagination='remote',
            page_size=10,
            height=200
        )

        # Setup callbacks
        self.fetch_button.on_click(self.manual_fetch_trigger)
        self.test_button.on_click(self.test_connection)

    def create_app(self):
        """Create the data fetcher interface"""

        # Navigation bar
        navigation = create_navigation_bar(current_app='data_fetcher')

        # Status indicator
        status = create_app_status_indicator()

        # Header
        header = pn.pane.HTML("""
        <div style="background: linear-gradient(90deg, #28a745, #20c997); padding: 20px; color: white; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">📥 Data Fetcher - Manual Trigger Controls</h2>
            <p style="margin: 5px 0 0 0;">Configure API endpoints and trigger data collection</p>
        </div>
        """, sizing_mode='stretch_width')

        # Configuration panel
        config_panel = pn.Column(
            "## 🔧 API Configuration",
            self.api_url,
            self.data_path,
            pn.pane.HTML("""
            <div style="background: #f8f9fa; padding: 10px; border-radius: 3px; margin: 10px 0;">
                <strong>💡 Example APIs:</strong><br>
                • Weather: https://api.openweathermap.org/data/2.5/weather?q=Tokyo&units=metric<br>
                • Crypto: https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd<br>
                • Stock: https://api.example.com/quote?symbol=AAPL
            </div>
            """),
            width=500
        )

        # Control panel
        control_panel = pn.Column(
            "## ⚡ Manual Controls",
            pn.Row(self.test_button, self.fetch_button),
            self.progress_bar,
            self.status_indicator,
            width=500
        )

        # Data preview panel
        preview_panel = pn.Column(
            "## 📊 Live Data Preview",
            self.data_preview,
            "## 📋 Fetch History",
            self.fetch_history,
            sizing_mode='stretch_width'
        )

        # Main layout
        return pn.Column(
            navigation,
            status,
            header,
            pn.Row(
                pn.Column(config_panel, control_panel),
                preview_panel,
                sizing_mode='stretch_width'
            ),
            sizing_mode='stretch_width'
        )

    async def manual_fetch_trigger(self, event):
        """Execute manual data fetch with progress monitoring"""
        self.progress_bar.value = 0
        self.update_status("🔄 Fetching data...", "info")

        try:
            # Validate inputs
            if not self.api_url.value:
                self.update_status("❌ Please enter an API URL", "error")
                return

            # Start fetch
            self.progress_bar.value = 25

            # Fetch data with timeout
            response = await asyncio.to_thread(
                requests.get,
                self.api_url.value,
                timeout=30
            )

            self.progress_bar.value = 50

            if response.status_code == 200:
                data = response.json()
                self.progress_bar.value = 75

                # Extract value using data path
                extracted_value = self.extract_data_value(data, self.data_path.value)

                # Create time series data point
                time_series_data = [{
                    'timestamp': datetime.now().isoformat(),
                    'value': extracted_value,
                    'source': self.api_url.value,
                    'data_path': self.data_path.value
                }]

                # Save to shared store
                success = shared_store.save_time_series_data(
                    time_series_data,
                    source_name=f"manual_fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    metadata={'api_url': self.api_url.value, 'data_path': self.data_path.value}
                )

                if success:
                    self.progress_bar.value = 100
                    self.update_status(f"✅ Fetched successfully: {extracted_value}", "success")
                    self.data_preview.object = data

                    # Log fetch event
                    shared_store.save_fetch_event({
                        'source': self.api_url.value,
                        'status': 'success',
                        'data_points': 1,
                        'value': extracted_value
                    })

                    # Update fetch history
                    self.update_fetch_history()
                else:
                    self.update_status("❌ Failed to save data", "error")
            else:
                self.update_status(f"❌ API Error: {response.status_code}", "error")

        except Exception as e:
            self.progress_bar.value = 0
            self.update_status(f"❌ Error: {str(e)}", "error")

    async def test_connection(self, event):
        """Test API connection without saving data"""
        self.update_status("🧪 Testing connection...", "info")

        try:
            response = await asyncio.to_thread(
                requests.get,
                self.api_url.value,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                extracted_value = self.extract_data_value(data, self.data_path.value)
                self.update_status(f"✅ Connection successful. Value: {extracted_value}", "success")
                self.data_preview.object = data
            else:
                self.update_status(f"⚠️ API returned status: {response.status_code}", "warning")

        except Exception as e:
            self.update_status(f"❌ Connection failed: {str(e)}", "error")

    def extract_data_value(self, data, data_path):
        """Extract value from nested JSON using dot notation"""
        try:
            value = data
            for key in data_path.split('.'):
                if key.isdigit():
                    value = value[int(key)]
                else:
                    value = value[key]
            return value
        except (KeyError, IndexError, TypeError):
            return None

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

    def update_fetch_history(self):
        """Update fetch history table"""
        history = shared_store.load_fetch_history()

        if history:
            df = pd.DataFrame(history)
            df['Timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            df['Source'] = df['source'].str.slice(0, 50) + '...'
            df['Status'] = df['status'].str.title()
            df['Data Points'] = df.get('data_points', 0)

            self.fetch_history.value = df[['Timestamp', 'Source', 'Status', 'Data Points']].tail(10)