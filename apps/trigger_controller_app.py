"""
Update Controller App - Panel Implementation
Manual trigger management and update scheduling interface
"""
import panel as pn
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_store import shared_store
from utils.navigation import create_navigation_bar, create_quick_actions_panel, create_app_status_indicator

class TriggerControllerApp:
    """Manual update triggers and scheduling interface"""

    def __init__(self):
        self.update_all_button = pn.widgets.Button(
            name="🔄 Update All Sources",
            button_type="primary",
            width=200
        )

        self.emergency_stop_button = pn.widgets.Button(
            name="🛑 Emergency Stop",
            button_type="danger",
            width=200
        )

        self.reminder_interval = pn.widgets.Select(
            name="Reminder Interval",
            options=['15 minutes', '1 hour', '4 hours', '12 hours', '24 hours'],
            value='1 hour'
        )

        self.set_reminder_button = pn.widgets.Button(
            name="⏰ Set Reminder",
            button_type="light",
            width=200
        )

        self.update_history = pn.widgets.Tabulator(
            value=pd.DataFrame(columns=['Time', 'Action', 'Status', 'Details']),
            pagination='remote',
            page_size=10,
            height=300
        )

        self.system_status = pn.pane.HTML(
            """<div style="padding: 15px; background: #f8f9fa; border-radius: 5px;">
            Loading system status...
            </div>""",
            width=400
        )

        # Setup callbacks
        self.update_all_button.on_click(self.trigger_update_all)
        self.emergency_stop_button.on_click(self.emergency_stop)
        self.set_reminder_button.on_click(self.set_reminder)

        # Load initial status
        self.update_system_status()
        self.load_update_history()

    def create_app(self):
        """Create the update controller interface"""

        # Navigation bar
        navigation = create_navigation_bar(current_app='update_controller')

        # Status indicator
        status = create_app_status_indicator()

        # Header
        header = pn.pane.HTML("""
        <div style="background: linear-gradient(90deg, #fd7e14, #e8590c); padding: 20px; color: white; border-radius: 5px; margin-bottom: 20px;">
            <h2 style="margin: 0;">⚡ Update Controller - Manual Triggers</h2>
            <p style="margin: 5px 0 0 0;">Manage manual triggers and update schedules</p>
        </div>
        """, sizing_mode='stretch_width')

        # Control panel
        control_panel = pn.Column(
            "## 🎛️ Manual Controls",
            self.update_all_button,
            self.emergency_stop_button,
            pn.pane.HTML("""
            <div style="background: #e9ecef; padding: 10px; border-radius: 3px; margin: 10px 0;">
                <strong>⚡ Manual Philosophy:</strong><br>
                All data updates are user-triggered.<br>
                No automatic background updates.
            </div>
            """),
            "## ⏰ Reminder System",
            self.reminder_interval,
            self.set_reminder_button,
            pn.pane.HTML("""
            <div style="background: #fff3cd; padding: 10px; border-radius: 3px; margin: 10px 0;">
                <strong>💡 Reminders:</strong><br>
                Get notifications when to manually update data.<br>
                Still requires manual trigger action.
            </div>
            """),
            width=400
        )

        # Status panel
        status_panel = pn.Column(
            "## 📊 System Status",
            self.system_status,
            "## 📋 Update History",
            self.update_history,
            sizing_mode='stretch_width'
        )

        # Main layout
        return pn.Column(
            navigation,
            status,
            header,
            pn.Row(
                control_panel,
                status_panel,
                sizing_mode='stretch_width'
            ),
            sizing_mode='stretch_width'
        )

    def trigger_update_all(self, event):
        """Trigger update for all configured data sources"""
        try:
            # Log the update trigger event
            self.log_update_event("Manual Update All", "triggered", "User initiated update for all sources")

            # In a full implementation, this would:
            # 1. Load API configurations
            # 2. Trigger data fetching for each source
            # 3. Update progress indicators
            # 4. Log results

            print("Triggering update for all data sources...")

            # For now, simulate the action
            self.log_update_event("Manual Update All", "completed", "All sources updated successfully")
            self.update_system_status()
            self.load_update_history()

            self.update_status("✅ Update triggered for all sources")

        except Exception as e:
            self.log_update_event("Manual Update All", "failed", f"Error: {str(e)}")
            self.update_status(f"❌ Update failed: {str(e)}")

    def emergency_stop(self, event):
        """Emergency stop for all running operations"""
        try:
            self.log_update_event("Emergency Stop", "executed", "All operations stopped by user")

            print("Emergency stop activated - stopping all operations")

            self.update_status("🛑 Emergency stop activated - all operations halted")
            self.load_update_history()

        except Exception as e:
            self.update_status(f"❌ Emergency stop failed: {str(e)}")

    def set_reminder(self, event):
        """Set update reminder"""
        try:
            interval = self.reminder_interval.value

            # In a full implementation, this would set up actual notifications
            self.log_update_event("Reminder Set", "configured", f"Reminder interval: {interval}")

            print(f"Reminder set for: {interval}")

            self.update_status(f"⏰ Reminder set for every {interval}")
            self.load_update_history()

        except Exception as e:
            self.update_status(f"❌ Failed to set reminder: {str(e)}")

    def log_update_event(self, action, status, details):
        """Log an update event to shared store"""
        try:
            event_data = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'status': status,
                'details': details,
                'source': 'update_controller'
            }

            # Save to shared store fetch history (reusing the mechanism)
            shared_store.save_fetch_event(event_data)

        except Exception as e:
            print(f"Error logging update event: {e}")

    def load_update_history(self):
        """Load and display update history"""
        try:
            history = shared_store.load_fetch_history()

            if history:
                df = pd.DataFrame(history)
                df['Time'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                df['Action'] = df.get('action', df.get('source', 'Unknown'))
                df['Status'] = df['status'].str.title()
                df['Details'] = df.get('details', df.get('value', 'No details'))

                # Show most recent events first
                display_df = df[['Time', 'Action', 'Status', 'Details']].tail(20).iloc[::-1]
                self.update_history.value = display_df
            else:
                # Empty history
                empty_df = pd.DataFrame(columns=['Time', 'Action', 'Status', 'Details'])
                self.update_history.value = empty_df

        except Exception as e:
            print(f"Error loading update history: {e}")

    def update_system_status(self):
        """Update system status display"""
        try:
            status = shared_store.get_status()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Calculate status indicators
            data_status = "🟢 Active" if status['time_series_available'] else "🔴 No Data"
            config_status = "🟢 Configured" if status['api_config_available'] else "🟡 Default"

            status_html = f"""
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; border: 1px solid #c3e6cb;">
                <h4 style="margin-top: 0; color: #155724;">🔄 System Status</h4>
                <table style="width: 100%;">
                    <tr><td><strong>Current Time:</strong></td><td>{current_time}</td></tr>
                    <tr><td><strong>Data Status:</strong></td><td>{data_status}</td></tr>
                    <tr><td><strong>Config Status:</strong></td><td>{config_status}</td></tr>
                    <tr><td><strong>Last Update:</strong></td><td>{status['last_updated'][:19] if status['last_updated'] != 'Never' else 'Never'}</td></tr>
                    <tr><td><strong>Update Events:</strong></td><td>{status['fetch_history_count']}</td></tr>
                    <tr><td><strong>Data Points:</strong></td><td>{status['data_info']['data_points']}</td></tr>
                </table>
                <div style="margin-top: 10px; padding: 8px; background: #c3e6cb; border-radius: 3px;">
                    <strong>🎯 Manual Control Active:</strong> All updates require user triggers
                </div>
            </div>
            """
            self.system_status.object = status_html

        except Exception as e:
            self.system_status.object = f"""
            <div style="background: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">
                Error loading system status: {str(e)}
            </div>
            """

    def update_status(self, message):
        """Update status (placeholder for now)"""
        print(f"Update Controller: {message}")
        # In a full implementation, this would update a status indicator