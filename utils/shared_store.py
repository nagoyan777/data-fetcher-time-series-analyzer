#!/usr/bin/env python3
"""
Shared Data Store for Data Fetcher Multi-App Communication
Allows apps to share time series data, API configurations, and processing state
Adapted from literature analysis project for time series data
"""
import json
import pickle
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
import logging

class SharedDataStore:
    """Shared storage for time series data between apps"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)

        # File paths for different data types
        self.time_series_file = self.data_dir / "time_series_data.pkl"
        self.api_config_file = self.data_dir / "api_config_data.pkl"
        self.fetch_history_file = self.data_dir / "fetch_history.json"
        self.metadata_file = self.data_dir / "metadata.json"

        # Ensure subdirectories exist
        for subdir in ['raw_data', 'processed_data', 'cache', 'backups']:
            (self.data_dir / subdir).mkdir(exist_ok=True)

    def save_time_series_data(self, data, source_name, metadata=None):
        """Save time series data from API fetching"""
        try:
            time_series_data = {
                'data': data,
                'source_name': source_name,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat(),
                'data_type': 'time_series'
            }

            with open(self.time_series_file, 'wb') as f:
                pickle.dump(time_series_data, f)

            # Update metadata
            self.update_metadata({
                'time_series_updated': datetime.now().isoformat(),
                'data_points': len(data) if data is not None else 0,
                'source_name': source_name,
                'last_fetch_success': True
            })
            return True
        except Exception as e:
            logging.error(f"Error saving time series data: {e}")
            return False

    def load_time_series_data(self):
        """Load time series data for analysis"""
        try:
            if self.time_series_file.exists():
                with open(self.time_series_file, 'rb') as f:
                    return pickle.load(f)
            return None
        except Exception as e:
            logging.error(f"Error loading time series data: {e}")
            return None

    def save_api_configuration(self, config_data):
        """Save API configuration settings"""
        try:
            api_config = {
                'config': config_data,
                'updated': datetime.now().isoformat()
            }

            with open(self.api_config_file, 'wb') as f:
                pickle.dump(api_config, f)

            self.update_metadata({
                'api_config_updated': datetime.now().isoformat(),
                'api_sources_count': len(config_data.get('sources', []))
            })
            return True
        except Exception as e:
            logging.error(f"Error saving API configuration: {e}")
            return False

    def load_api_configuration(self):
        """Load API configuration settings"""
        try:
            if self.api_config_file.exists():
                with open(self.api_config_file, 'rb') as f:
                    return pickle.load(f)
            return None
        except Exception as e:
            logging.error(f"Error loading API configuration: {e}")
            return None

    def save_fetch_event(self, event_data):
        """Log a data fetch event for history tracking"""
        try:
            # Load existing history
            history = self.load_fetch_history()

            # Add new event
            event_data['timestamp'] = datetime.now().isoformat()
            history.append(event_data)

            # Keep only last 100 events
            history = history[-100:]

            with open(self.fetch_history_file, 'w') as f:
                json.dump(history, f, indent=2)

            return True
        except Exception as e:
            logging.error(f"Error saving fetch event: {e}")
            return False

    def load_fetch_history(self):
        """Load fetch history for monitoring"""
        try:
            if self.fetch_history_file.exists():
                with open(self.fetch_history_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.error(f"Error loading fetch history: {e}")
            return []

    def update_metadata(self, new_data):
        """Update metadata file"""
        try:
            metadata = self.load_metadata()
            metadata.update(new_data)
            metadata['last_updated'] = datetime.now().isoformat()

            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logging.error(f"Error updating metadata: {e}")

    def load_metadata(self):
        """Load metadata"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading metadata: {e}")
            return {}

    def get_status(self):
        """Get current data status for all apps"""
        metadata = self.load_metadata()

        return {
            'time_series_available': self.time_series_file.exists(),
            'api_config_available': self.api_config_file.exists(),
            'fetch_history_count': len(self.load_fetch_history()),
            'last_updated': metadata.get('time_series_updated', 'Never'),
            'data_info': {
                'source': metadata.get('source_name', 'None'),
                'data_points': metadata.get('data_points', 0),
                'last_fetch_success': metadata.get('last_fetch_success', False)
            }
        }

    def save_app_config(self, app_name, config_data):
        """Save app-specific configuration settings"""
        try:
            config_file = self.data_dir / f"{app_name}_config.json"
            config = self.load_app_config(app_name)
            config.update(config_data)
            config['updated'] = datetime.now().isoformat()

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error saving app config for {app_name}: {e}")
            return False

    def load_app_config(self, app_name):
        """Load app-specific configuration settings"""
        try:
            config_file = self.data_dir / f"{app_name}_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading app config for {app_name}: {e}")
            return {}

    def get_sync_config(self, app_name):
        """Get configuration for a specific app with fallback defaults"""
        config = self.load_app_config(app_name)
        defaults = {
            'data_fetcher': {
                'default_api_timeout': 30,
                'retry_attempts': 3,
                'cache_duration': 3600
            },
            'time_series_analyzer': {
                'default_plot_height': 400,
                'y_axis_scale': 'Linear',
                'show_grid': True,
                'auto_refresh': False
            },
            'data_manager': {
                'backup_frequency': 'every_update',
                'export_format': 'json',
                'retention_days': 365
            },
            'update_controller': {
                'manual_triggers_only': True,
                'show_progress': True,
                'notification_enabled': True
            }
        }

        # Return app-specific config merged with defaults
        app_defaults = defaults.get(app_name, {})
        return {**app_defaults, **config}

    def clear_all_data(self):
        """Clear all stored data (for reset/testing)"""
        try:
            files_to_clear = [
                self.time_series_file,
                self.api_config_file,
                self.fetch_history_file,
                self.metadata_file
            ]

            for file_path in files_to_clear:
                if file_path.exists():
                    file_path.unlink()

            logging.info("All shared data cleared")
            return True
        except Exception as e:
            logging.error(f"Error clearing data: {e}")
            return False

# Global instance for all apps to use
shared_store = SharedDataStore()