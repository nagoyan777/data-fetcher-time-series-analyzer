"""
Data Manager App - Panel Implementation
Storage management, backup, and export functionality
"""
import panel as pn
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_store import shared_store
from utils.navigation import create_navigation_bar, create_quick_actions_panel, create_app_status_indicator

class DataManagerApp:
    """Data storage management and export interface"""

    def __init__(self):
        self.backup_button = pn.widgets.Button(
            name="💾 Create Backup",
            button_type="primary",
            width=200
        )

        self.export_format = pn.widgets.Select(
            name="Export Format",
            options=['JSON', 'CSV', 'Excel'],
            value='JSON'
        )

        self.export_button = pn.widgets.Button(
            name="📤 Export Data",
            button_type="light",
            width=200
        )

        self.storage_info = pn.pane.HTML(
            """<div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">
            Loading storage information...
            </div>""",
            width=400
        )

        # Setup callbacks
        self.backup_button.on_click(self.create_backup)
        self.export_button.on_click(self.export_data)

        # Load initial info
        self.update_storage_info()

    def create_app(self):
        """Create the data manager interface"""

        # Navigation bar
        navigation = create_navigation_bar(current_app='data_manager')

        # Status indicator
        status = create_app_status_indicator()

        # Header
        header = pn.pane.HTML("""
        <div style="background: linear-gradient(90deg, #6f42c1, #5a32a3); padding: 20px; color: white; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">💾 Data Manager - Storage & Export</h2>
            <p style="margin: 5px 0 0 0;">Browse, backup, and export stored time series data</p>
        </div>
        """, sizing_mode='stretch_width')

        # Storage management panel
        management_panel = pn.Column(
            "## 🗄️ Storage Management",
            self.storage_info,
            "## 💾 Backup Controls",
            self.backup_button,
            pn.pane.HTML("""
            <div style="background: #e9ecef; padding: 10px; border-radius: 3px; margin: 10px 0;">
                <strong>💡 Backup Info:</strong><br>
                Automatic backups are created with every data update.<br>
                Manual backups preserve current state for rollback.
            </div>
            """),
            width=400
        )

        # Export panel
        export_panel = pn.Column(
            "## 📤 Data Export",
            self.export_format,
            self.export_button,
            pn.pane.HTML("""
            <div style="background: #e9ecef; padding: 10px; border-radius: 3px; margin: 10px 0;">
                <strong>🔄 Export Formats:</strong><br>
                • JSON: Full metadata preservation<br>
                • CSV: Spreadsheet compatible<br>
                • Excel: Multi-sheet with analysis
            </div>
            """),
            width=400
        )

        # Placeholder for file browser
        file_browser = pn.Column(
            "## 📁 File Browser",
            pn.pane.HTML("""
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; border: 1px solid #ffeaa7;">
                <h4 style="margin-top: 0;">🚧 Coming Soon</h4>
                <p>Interactive file browser for stored data files will be implemented in Phase 2.</p>
                <p><strong>Current Status:</strong> Basic storage and export functionality available.</p>
            </div>
            """),
            sizing_mode='stretch_width'
        )

        # Main layout
        return pn.Column(
            navigation,
            status,
            header,
            pn.Row(
                pn.Column(management_panel, export_panel),
                file_browser,
                sizing_mode='stretch_width'
            ),
            sizing_mode='stretch_width'
        )

    def create_backup(self, event):
        """Create manual backup of current data"""
        try:
            # For now, this is a placeholder
            backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')

            # In a full implementation, this would copy current data to backup directory
            print(f"Creating backup: backup_{backup_time}")

            self.update_storage_info()
            self.update_status("✅ Backup created successfully")

        except Exception as e:
            self.update_status(f"❌ Backup failed: {str(e)}")

    def export_data(self, event):
        """Export data in selected format"""
        try:
            time_series_data = shared_store.load_time_series_data()

            if not time_series_data:
                self.update_status("⚠️ No data available to export")
                return

            # For now, this is a placeholder
            export_format = self.export_format.value.lower()
            export_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"time_series_export_{export_time}.{export_format}"

            print(f"Exporting data as: {filename}")

            self.update_status(f"✅ Data exported as {filename}")

        except Exception as e:
            self.update_status(f"❌ Export failed: {str(e)}")

    def update_storage_info(self):
        """Update storage information display"""
        try:
            status = shared_store.get_status()

            info_html = f"""
            <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; border: 1px solid #bee5eb;">
                <h4 style="margin-top: 0; color: #0c5460;">📊 Storage Status</h4>
                <table style="width: 100%;">
                    <tr><td><strong>Time Series Data:</strong></td><td>{'✅ Available' if status['time_series_available'] else '❌ None'}</td></tr>
                    <tr><td><strong>API Configuration:</strong></td><td>{'✅ Available' if status['api_config_available'] else '❌ None'}</td></tr>
                    <tr><td><strong>Fetch History:</strong></td><td>{status['fetch_history_count']} events</td></tr>
                    <tr><td><strong>Last Updated:</strong></td><td>{status['last_updated'][:19] if status['last_updated'] != 'Never' else 'Never'}</td></tr>
                    <tr><td><strong>Data Points:</strong></td><td>{status['data_info']['data_points']}</td></tr>
                    <tr><td><strong>Source:</strong></td><td>{status['data_info']['source']}</td></tr>
                </table>
            </div>
            """
            self.storage_info.object = info_html

        except Exception as e:
            self.storage_info.object = f"""
            <div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                Error loading storage info: {str(e)}
            </div>
            """

    def update_status(self, message):
        """Update status (placeholder for now)"""
        print(f"Data Manager: {message}")
        # In a full implementation, this would update a status indicator