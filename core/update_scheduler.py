#!/usr/bin/env python3
"""
Update Scheduler - Core Business Logic
Manual trigger management and reminder system for data updates
"""
import asyncio
import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
import time

class UpdateScheduler:
    """Manual trigger management with reminder notifications"""

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.schedules_file = self.data_dir / "update_schedules.json"
        self.manual_triggers_only = True  # Core philosophy
        self.active_reminders = {}
        self.reminder_callbacks = []
        self.is_running = False
        self.scheduler_thread = None

    def register_reminder_callback(self, callback):
        """Register callback for reminder notifications"""
        self.reminder_callbacks.append(callback)

    def set_reminder(self, interval_minutes, source_name=None, description=None):
        """Set a reminder for manual data updates"""
        try:
            reminder_id = f"{source_name or 'general'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            reminder = {
                'id': reminder_id,
                'source_name': source_name or 'all_sources',
                'description': description or f"Manual update reminder for {source_name or 'all sources'}",
                'interval_minutes': interval_minutes,
                'next_reminder': (datetime.now() + timedelta(minutes=interval_minutes)).isoformat(),
                'created': datetime.now().isoformat(),
                'active': True,
                'trigger_count': 0
            }

            self.active_reminders[reminder_id] = reminder
            self.save_schedules()

            logging.info(f"Set reminder: {reminder_id} for {interval_minutes} minutes")
            return reminder_id

        except Exception as e:
            logging.error(f"Error setting reminder: {e}")
            return None

    def cancel_reminder(self, reminder_id):
        """Cancel an active reminder"""
        try:
            if reminder_id in self.active_reminders:
                self.active_reminders[reminder_id]['active'] = False
                self.save_schedules()
                logging.info(f"Cancelled reminder: {reminder_id}")
                return True
            return False

        except Exception as e:
            logging.error(f"Error cancelling reminder: {e}")
            return False

    def get_active_reminders(self):
        """Get list of active reminders"""
        try:
            return {k: v for k, v in self.active_reminders.items() if v.get('active', False)}

        except Exception as e:
            logging.error(f"Error getting active reminders: {e}")
            return {}

    def trigger_manual_update(self, source_name=None, user_id=None):
        """Log a manual update trigger event"""
        try:
            trigger_event = {
                'event_type': 'manual_trigger',
                'source_name': source_name or 'all_sources',
                'user_id': user_id or 'unknown',
                'timestamp': datetime.now().isoformat(),
                'trigger_method': 'manual_button',
                'status': 'triggered'
            }

            # Log the trigger event
            self.log_trigger_event(trigger_event)

            # Reset relevant reminder timers
            self.reset_reminder_timers(source_name)

            logging.info(f"Manual update triggered for: {source_name or 'all sources'}")
            return trigger_event

        except Exception as e:
            logging.error(f"Error triggering manual update: {e}")
            return None

    def emergency_stop_all(self):
        """Emergency stop for all scheduled operations"""
        try:
            stop_event = {
                'event_type': 'emergency_stop',
                'timestamp': datetime.now().isoformat(),
                'action': 'stop_all_operations',
                'reason': 'user_initiated'
            }

            # Pause all reminders temporarily
            for reminder_id in self.active_reminders:
                if self.active_reminders[reminder_id].get('active'):
                    self.active_reminders[reminder_id]['paused'] = True

            self.log_trigger_event(stop_event)
            logging.warning("Emergency stop activated - all operations paused")
            return True

        except Exception as e:
            logging.error(f"Error in emergency stop: {e}")
            return False

    def resume_operations(self):
        """Resume operations after emergency stop"""
        try:
            # Unpause all reminders
            for reminder_id in self.active_reminders:
                if 'paused' in self.active_reminders[reminder_id]:
                    del self.active_reminders[reminder_id]['paused']

            resume_event = {
                'event_type': 'operations_resumed',
                'timestamp': datetime.now().isoformat(),
                'action': 'resume_all_operations'
            }

            self.log_trigger_event(resume_event)
            logging.info("Operations resumed after emergency stop")
            return True

        except Exception as e:
            logging.error(f"Error resuming operations: {e}")
            return False

    def start_reminder_system(self):
        """Start the reminder notification system"""
        if self.is_running:
            return

        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.scheduler_thread.start()
        logging.info("Reminder system started")

    def stop_reminder_system(self):
        """Stop the reminder notification system"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logging.info("Reminder system stopped")

    def _reminder_loop(self):
        """Main reminder loop (runs in background thread)"""
        while self.is_running:
            try:
                self._check_reminders()
                time.sleep(60)  # Check every minute

            except Exception as e:
                logging.error(f"Error in reminder loop: {e}")
                time.sleep(60)

    def _check_reminders(self):
        """Check and trigger due reminders"""
        current_time = datetime.now()

        for reminder_id, reminder in self.active_reminders.items():
            if not reminder.get('active') or reminder.get('paused'):
                continue

            try:
                next_reminder_time = datetime.fromisoformat(reminder['next_reminder'])

                if current_time >= next_reminder_time:
                    # Trigger reminder
                    self._trigger_reminder(reminder_id, reminder)

                    # Schedule next reminder
                    next_time = current_time + timedelta(minutes=reminder['interval_minutes'])
                    reminder['next_reminder'] = next_time.isoformat()
                    reminder['trigger_count'] += 1

                    self.save_schedules()

            except Exception as e:
                logging.error(f"Error checking reminder {reminder_id}: {e}")

    def _trigger_reminder(self, reminder_id, reminder):
        """Trigger a reminder notification"""
        try:
            notification = {
                'type': 'update_reminder',
                'reminder_id': reminder_id,
                'source_name': reminder['source_name'],
                'description': reminder['description'],
                'timestamp': datetime.now().isoformat(),
                'message': f"Time to manually update: {reminder['source_name']}"
            }

            # Call registered callbacks
            for callback in self.reminder_callbacks:
                try:
                    callback(notification)
                except Exception as e:
                    logging.error(f"Error in reminder callback: {e}")

            # Log the reminder
            self.log_trigger_event({
                'event_type': 'reminder_triggered',
                'reminder_id': reminder_id,
                'source_name': reminder['source_name'],
                'timestamp': datetime.now().isoformat()
            })

            logging.info(f"Reminder triggered: {reminder_id}")

        except Exception as e:
            logging.error(f"Error triggering reminder: {e}")

    def reset_reminder_timers(self, source_name=None):
        """Reset reminder timers after manual update"""
        try:
            current_time = datetime.now()

            for reminder_id, reminder in self.active_reminders.items():
                if not reminder.get('active'):
                    continue

                # Reset if it matches the source or if updating all sources
                if (source_name is None or
                    reminder['source_name'] == source_name or
                    reminder['source_name'] == 'all_sources'):

                    next_time = current_time + timedelta(minutes=reminder['interval_minutes'])
                    reminder['next_reminder'] = next_time.isoformat()

            self.save_schedules()
            logging.info(f"Reset reminder timers for: {source_name or 'all sources'}")

        except Exception as e:
            logging.error(f"Error resetting reminder timers: {e}")

    def get_next_reminders(self, limit=5):
        """Get upcoming reminders"""
        try:
            active_reminders = self.get_active_reminders()
            sorted_reminders = sorted(
                active_reminders.values(),
                key=lambda x: x['next_reminder']
            )

            return sorted_reminders[:limit]

        except Exception as e:
            logging.error(f"Error getting next reminders: {e}")
            return []

    def get_reminder_statistics(self):
        """Get reminder system statistics"""
        try:
            active_count = len(self.get_active_reminders())
            total_triggers = sum(r.get('trigger_count', 0) for r in self.active_reminders.values())

            next_reminders = self.get_next_reminders(3)
            next_reminder_time = None
            if next_reminders:
                next_reminder_time = next_reminders[0]['next_reminder']

            return {
                'active_reminders': active_count,
                'total_reminders_set': len(self.active_reminders),
                'total_triggers': total_triggers,
                'next_reminder': next_reminder_time,
                'system_running': self.is_running,
                'manual_triggers_only': self.manual_triggers_only
            }

        except Exception as e:
            logging.error(f"Error getting reminder statistics: {e}")
            return {}

    def save_schedules(self):
        """Save schedules to file"""
        try:
            with open(self.schedules_file, 'w') as f:
                json.dump(self.active_reminders, f, indent=2, default=str)

        except Exception as e:
            logging.error(f"Error saving schedules: {e}")

    def load_schedules(self):
        """Load schedules from file"""
        try:
            if self.schedules_file.exists():
                with open(self.schedules_file, 'r') as f:
                    self.active_reminders = json.load(f)
            else:
                self.active_reminders = {}

        except Exception as e:
            logging.error(f"Error loading schedules: {e}")
            self.active_reminders = {}

    def log_trigger_event(self, event):
        """Log trigger events for monitoring"""
        try:
            log_file = self.data_dir / "trigger_events.json"

            # Load existing events
            events = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    events = json.load(f)

            # Add new event
            events.append(event)

            # Keep only last 1000 events
            events = events[-1000:]

            # Save back
            with open(log_file, 'w') as f:
                json.dump(events, f, indent=2, default=str)

        except Exception as e:
            logging.error(f"Error logging trigger event: {e}")

    def get_trigger_history(self, limit=50):
        """Get recent trigger history"""
        try:
            log_file = self.data_dir / "trigger_events.json"

            if not log_file.exists():
                return []

            with open(log_file, 'r') as f:
                events = json.load(f)

            # Return most recent events
            return events[-limit:] if events else []

        except Exception as e:
            logging.error(f"Error getting trigger history: {e}")
            return []

    def cleanup_old_reminders(self, days_old=30):
        """Clean up old inactive reminders"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            removed_count = 0

            to_remove = []
            for reminder_id, reminder in self.active_reminders.items():
                if not reminder.get('active'):
                    created_date = datetime.fromisoformat(reminder['created'])
                    if created_date < cutoff_date:
                        to_remove.append(reminder_id)

            for reminder_id in to_remove:
                del self.active_reminders[reminder_id]
                removed_count += 1

            if removed_count > 0:
                self.save_schedules()

            logging.info(f"Cleaned up {removed_count} old reminders")
            return removed_count

        except Exception as e:
            logging.error(f"Error cleaning up old reminders: {e}")
            return 0