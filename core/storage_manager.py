#!/usr/bin/env python3
"""
Storage Manager - Core Business Logic
File operations, data versioning, and backup management for time series data
"""
import json
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
import logging
import gzip
import hashlib

class StorageManager:
    """Core storage operations with versioning and backup capabilities"""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Create directory structure
        self.raw_data_dir = self.data_dir / "raw_data"
        self.processed_data_dir = self.data_dir / "processed_data"
        self.cache_dir = self.data_dir / "cache"
        self.backups_dir = self.data_dir / "backups"

        for dir_path in [self.raw_data_dir, self.processed_data_dir, self.cache_dir, self.backups_dir]:
            dir_path.mkdir(exist_ok=True)

    def save_time_series_data(self, data, source_name, metadata=None, create_backup=True):
        """Save time series data with automatic versioning"""
        try:
            if create_backup:
                self.create_backup(source_name)

            # Prepare data structure
            time_series_data = {
                'data': data,
                'source_name': source_name,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat(),
                'version': self.get_next_version(source_name),
                'checksum': self.calculate_checksum(data)
            }

            # Save to raw data
            filename = f"{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = self.raw_data_dir / filename

            with open(file_path, 'w') as f:
                json.dump(time_series_data, f, indent=2, default=str)

            # Update latest symlink
            latest_link = self.raw_data_dir / f"{source_name}_latest.json"
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(filename)

            logging.info(f"Saved time series data: {filename}")
            return True

        except Exception as e:
            logging.error(f"Error saving time series data: {e}")
            return False

    def load_time_series_data(self, source_name=None, version=None):
        """Load time series data with version support"""
        try:
            if source_name and version:
                # Load specific version
                pattern = f"{source_name}_v{version}_*.json"
                files = list(self.raw_data_dir.glob(pattern))
                if not files:
                    return None
                file_path = files[0]
            elif source_name:
                # Load latest version
                latest_link = self.raw_data_dir / f"{source_name}_latest.json"
                if not latest_link.exists():
                    return None
                file_path = latest_link
            else:
                # Load most recent file
                files = list(self.raw_data_dir.glob("*.json"))
                if not files:
                    return None
                file_path = max(files, key=lambda x: x.stat().st_mtime)

            with open(file_path, 'r') as f:
                return json.load(f)

        except Exception as e:
            logging.error(f"Error loading time series data: {e}")
            return None

    def create_backup(self, source_name=None):
        """Create compressed backup of current data"""
        try:
            backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')

            if source_name:
                # Backup specific source
                source_files = list(self.raw_data_dir.glob(f"{source_name}*"))
                backup_name = f"backup_{source_name}_{backup_time}.tar.gz"
            else:
                # Backup all data
                source_files = list(self.raw_data_dir.glob("*.json"))
                backup_name = f"backup_all_{backup_time}.tar.gz"

            if not source_files:
                logging.warning("No files to backup")
                return False

            backup_path = self.backups_dir / backup_name

            # Create compressed backup
            import tarfile
            with tarfile.open(backup_path, 'w:gz') as tar:
                for file_path in source_files:
                    tar.add(file_path, arcname=file_path.name)

            logging.info(f"Created backup: {backup_name}")
            return True

        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return False

    def restore_backup(self, backup_name):
        """Restore data from backup"""
        try:
            backup_path = self.backups_dir / backup_name
            if not backup_path.exists():
                logging.error(f"Backup not found: {backup_name}")
                return False

            # Extract backup
            import tarfile
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(self.raw_data_dir)

            logging.info(f"Restored backup: {backup_name}")
            return True

        except Exception as e:
            logging.error(f"Error restoring backup: {e}")
            return False

    def export_data(self, format_type='json', source_name=None, output_path=None):
        """Export data in various formats"""
        try:
            data = self.load_time_series_data(source_name)
            if not data:
                logging.error("No data to export")
                return False

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if not output_path:
                filename = f"export_{source_name or 'all'}_{timestamp}"
                output_path = self.processed_data_dir / f"{filename}.{format_type.lower()}"

            if format_type.lower() == 'json':
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)

            elif format_type.lower() == 'csv':
                if 'data' in data and isinstance(data['data'], list):
                    df = pd.DataFrame(data['data'])
                    df.to_csv(output_path, index=False)
                else:
                    logging.error("Data format not suitable for CSV export")
                    return False

            elif format_type.lower() == 'excel':
                if 'data' in data and isinstance(data['data'], list):
                    df = pd.DataFrame(data['data'])
                    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Time Series Data', index=False)

                        # Add metadata sheet
                        metadata_df = pd.DataFrame([data.get('metadata', {})])
                        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                else:
                    logging.error("Data format not suitable for Excel export")
                    return False

            logging.info(f"Exported data to: {output_path}")
            return str(output_path)

        except Exception as e:
            logging.error(f"Error exporting data: {e}")
            return False

    def get_storage_stats(self):
        """Get storage statistics"""
        try:
            raw_files = list(self.raw_data_dir.glob("*.json"))
            processed_files = list(self.processed_data_dir.glob("*"))
            backup_files = list(self.backups_dir.glob("*.tar.gz"))
            cache_files = list(self.cache_dir.glob("*"))

            def get_dir_size(path):
                return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())

            return {
                'raw_data_files': len(raw_files),
                'processed_files': len(processed_files),
                'backup_files': len(backup_files),
                'cache_files': len(cache_files),
                'total_size_mb': get_dir_size(self.data_dir) / (1024 * 1024),
                'raw_data_size_mb': get_dir_size(self.raw_data_dir) / (1024 * 1024),
                'backup_size_mb': get_dir_size(self.backups_dir) / (1024 * 1024),
                'last_backup': self.get_latest_backup_info()
            }

        except Exception as e:
            logging.error(f"Error getting storage stats: {e}")
            return {}

    def cleanup_old_files(self, days_to_keep=30):
        """Clean up old files based on retention policy"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            removed_count = 0

            for file_path in self.raw_data_dir.glob("*.json"):
                if file_path.stat().st_mtime < cutoff_time:
                    if not file_path.name.endswith('_latest.json'):
                        file_path.unlink()
                        removed_count += 1

            # Clean old backups (keep last 10)
            backup_files = sorted(self.backups_dir.glob("*.tar.gz"),
                                key=lambda x: x.stat().st_mtime, reverse=True)
            for backup_file in backup_files[10:]:
                backup_file.unlink()
                removed_count += 1

            logging.info(f"Cleaned up {removed_count} old files")
            return removed_count

        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            return 0

    def get_next_version(self, source_name):
        """Get next version number for a source"""
        try:
            files = list(self.raw_data_dir.glob(f"{source_name}_*.json"))
            if not files:
                return 1

            versions = []
            for file_path in files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if 'version' in data:
                            versions.append(data['version'])
                except:
                    continue

            return max(versions, default=0) + 1

        except Exception as e:
            logging.error(f"Error getting next version: {e}")
            return 1

    def calculate_checksum(self, data):
        """Calculate checksum for data integrity"""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except:
            return None

    def get_latest_backup_info(self):
        """Get info about latest backup"""
        try:
            backup_files = list(self.backups_dir.glob("*.tar.gz"))
            if not backup_files:
                return "No backups"

            latest = max(backup_files, key=lambda x: x.stat().st_mtime)
            timestamp = datetime.fromtimestamp(latest.stat().st_mtime)
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')

        except:
            return "Unknown"