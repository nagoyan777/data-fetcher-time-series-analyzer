#!/usr/bin/env python3
"""
Performance Utils - Shared Utility
Memory monitoring, optimization tools, and performance metrics for data operations
"""
import psutil
import time
import threading
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json
from typing import Dict, Any, List, Optional
import functools
import gc

class PerformanceMonitor:
    """System and application performance monitoring"""

    def __init__(self, log_dir="data/performance"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.monitoring_active = False
        self.monitor_thread = None
        self.performance_data = []
        self.max_history = 1000  # Keep last 1000 measurements

    def start_monitoring(self, interval_seconds=60):
        """Start continuous performance monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        logging.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logging.info("Performance monitoring stopped")

    def _monitor_loop(self, interval_seconds):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self.get_system_metrics()
                self.performance_data.append(metrics)

                # Keep only recent data
                if len(self.performance_data) > self.max_history:
                    self.performance_data = self.performance_data[-self.max_history:]

                # Save to file periodically
                if len(self.performance_data) % 10 == 0:
                    self.save_performance_log()

                time.sleep(interval_seconds)

            except Exception as e:
                logging.error(f"Error in performance monitoring: {e}")
                time.sleep(interval_seconds)

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk = psutil.disk_usage('/')

            # Process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()

            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'cpu_count': cpu_count,
                    'memory_total_gb': memory.total / (1024**3),
                    'memory_used_gb': memory.used / (1024**3),
                    'memory_percent': memory.percent,
                    'swap_used_gb': swap.used / (1024**3),
                    'disk_used_gb': disk.used / (1024**3),
                    'disk_free_gb': disk.free / (1024**3),
                    'disk_percent': (disk.used / disk.total) * 100
                },
                'process': {
                    'cpu_percent': process_cpu,
                    'memory_rss_mb': process_memory.rss / (1024**2),
                    'memory_vms_mb': process_memory.vms / (1024**2),
                    'num_threads': process.num_threads(),
                    'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
                }
            }

        except Exception as e:
            logging.error(f"Error getting system metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def get_memory_usage(self) -> Dict[str, float]:
        """Get detailed memory usage information"""
        try:
            # System memory
            memory = psutil.virtual_memory()

            # Process memory
            process = psutil.Process()
            process_memory = process.memory_info()

            # Python memory (if available)
            python_objects = len(gc.get_objects())

            return {
                'system_total_gb': memory.total / (1024**3),
                'system_available_gb': memory.available / (1024**3),
                'system_used_percent': memory.percent,
                'process_rss_mb': process_memory.rss / (1024**2),
                'process_vms_mb': process_memory.vms / (1024**2),
                'python_objects_count': python_objects
            }

        except Exception as e:
            logging.error(f"Error getting memory usage: {e}")
            return {}

    def check_memory_pressure(self, threshold_percent=85) -> Dict[str, Any]:
        """Check if system is under memory pressure"""
        try:
            memory = psutil.virtual_memory()

            under_pressure = memory.percent > threshold_percent

            if under_pressure:
                logging.warning(f"Memory pressure detected: {memory.percent:.1f}% used")

            return {
                'under_pressure': under_pressure,
                'memory_percent': memory.percent,
                'threshold': threshold_percent,
                'available_gb': memory.available / (1024**3),
                'recommendation': 'Consider reducing data processing or clearing caches' if under_pressure else 'Memory usage normal'
            }

        except Exception as e:
            logging.error(f"Error checking memory pressure: {e}")
            return {'error': str(e)}

    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization"""
        try:
            # Get memory before optimization
            before_memory = self.get_memory_usage()

            # Force garbage collection
            collected = gc.collect()

            # Get memory after optimization
            after_memory = self.get_memory_usage()

            memory_freed = (before_memory.get('process_rss_mb', 0) -
                          after_memory.get('process_rss_mb', 0))

            result = {
                'objects_collected': collected,
                'memory_freed_mb': memory_freed,
                'before_memory_mb': before_memory.get('process_rss_mb', 0),
                'after_memory_mb': after_memory.get('process_rss_mb', 0),
                'optimization_effective': memory_freed > 1.0
            }

            logging.info(f"Memory optimization completed: {memory_freed:.1f}MB freed, {collected} objects collected")
            return result

        except Exception as e:
            logging.error(f"Error optimizing memory: {e}")
            return {'error': str(e)}

    def save_performance_log(self):
        """Save performance data to log file"""
        try:
            log_file = self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.json"

            with open(log_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2, default=str)

        except Exception as e:
            logging.error(f"Error saving performance log: {e}")

    def get_performance_summary(self, hours=1) -> Dict[str, Any]:
        """Get performance summary for recent time period"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            recent_data = [
                data for data in self.performance_data
                if datetime.fromisoformat(data['timestamp']) > cutoff_time
            ]

            if not recent_data:
                return {'message': 'No recent performance data available'}

            # Calculate averages
            cpu_values = [d['system']['cpu_percent'] for d in recent_data if 'system' in d]
            memory_values = [d['system']['memory_percent'] for d in recent_data if 'system' in d]
            process_memory = [d['process']['memory_rss_mb'] for d in recent_data if 'process' in d]

            return {
                'time_period_hours': hours,
                'data_points': len(recent_data),
                'cpu': {
                    'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    'max': max(cpu_values) if cpu_values else 0,
                    'min': min(cpu_values) if cpu_values else 0
                },
                'memory': {
                    'average_percent': sum(memory_values) / len(memory_values) if memory_values else 0,
                    'max_percent': max(memory_values) if memory_values else 0,
                    'process_avg_mb': sum(process_memory) / len(process_memory) if process_memory else 0,
                    'process_max_mb': max(process_memory) if process_memory else 0
                }
            }

        except Exception as e:
            logging.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}


class PerformanceProfiler:
    """Function-level performance profiling"""

    def __init__(self):
        self.profile_data = {}

    def profile(self, func_name=None):
        """Decorator for profiling function performance"""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self._get_memory_usage()

                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = self._get_memory_usage()

                    self._record_profile(name, start_time, end_time,
                                       start_memory, end_memory, success, error)

                return result

            return wrapper
        return decorator

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024**2)
        except:
            return 0.0

    def _record_profile(self, func_name, start_time, end_time,
                       start_memory, end_memory, success, error):
        """Record profiling data"""
        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory

        if func_name not in self.profile_data:
            self.profile_data[func_name] = {
                'call_count': 0,
                'total_time': 0,
                'total_memory_delta': 0,
                'max_time': 0,
                'min_time': float('inf'),
                'errors': 0,
                'last_called': None
            }

        profile = self.profile_data[func_name]
        profile['call_count'] += 1
        profile['total_time'] += execution_time
        profile['total_memory_delta'] += memory_delta
        profile['max_time'] = max(profile['max_time'], execution_time)
        profile['min_time'] = min(profile['min_time'], execution_time)
        profile['last_called'] = datetime.now().isoformat()

        if not success:
            profile['errors'] += 1

    def get_profile_report(self, sort_by='total_time') -> List[Dict[str, Any]]:
        """Get profiling report sorted by specified metric"""
        try:
            report = []

            for func_name, data in self.profile_data.items():
                avg_time = data['total_time'] / data['call_count'] if data['call_count'] > 0 else 0
                avg_memory = data['total_memory_delta'] / data['call_count'] if data['call_count'] > 0 else 0

                report.append({
                    'function': func_name,
                    'call_count': data['call_count'],
                    'total_time_seconds': data['total_time'],
                    'average_time_seconds': avg_time,
                    'max_time_seconds': data['max_time'],
                    'min_time_seconds': data['min_time'] if data['min_time'] != float('inf') else 0,
                    'total_memory_delta_mb': data['total_memory_delta'],
                    'average_memory_delta_mb': avg_memory,
                    'error_count': data['errors'],
                    'error_rate_percent': (data['errors'] / data['call_count']) * 100 if data['call_count'] > 0 else 0,
                    'last_called': data['last_called']
                })

            # Sort by specified metric
            if sort_by in ['total_time', 'average_time_seconds', 'call_count', 'error_count']:
                report.sort(key=lambda x: x.get(sort_by, 0), reverse=True)

            return report

        except Exception as e:
            logging.error(f"Error generating profile report: {e}")
            return []

    def clear_profile_data(self):
        """Clear all profiling data"""
        self.profile_data = {}
        logging.info("Profile data cleared")


class DataOptimizer:
    """Data processing optimization utilities"""

    @staticmethod
    def optimize_dataframe(df, memory_usage_threshold_mb=100):
        """Optimize pandas DataFrame memory usage"""
        try:
            if df is None or df.empty:
                return df

            # Get initial memory usage
            initial_memory = df.memory_usage(deep=True).sum() / (1024**2)

            if initial_memory < memory_usage_threshold_mb:
                return df

            # Optimize numeric columns
            for col in df.select_dtypes(include=['int', 'float']).columns:
                df[col] = pd.to_numeric(df[col], downcast='integer' if df[col].dtype.kind == 'i' else 'float')

            # Optimize object columns
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                    df[col] = df[col].astype('category')

            # Get final memory usage
            final_memory = df.memory_usage(deep=True).sum() / (1024**2)
            memory_saved = initial_memory - final_memory

            logging.info(f"DataFrame optimized: {memory_saved:.1f}MB saved ({initial_memory:.1f}MB -> {final_memory:.1f}MB)")

            return df

        except Exception as e:
            logging.error(f"Error optimizing DataFrame: {e}")
            return df

    @staticmethod
    def batch_process_data(data_list, batch_size=1000, process_func=None):
        """Process large datasets in batches to manage memory"""
        try:
            if not data_list or not process_func:
                return []

            results = []
            total_batches = (len(data_list) + batch_size - 1) // batch_size

            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                batch_num = (i // batch_size) + 1

                logging.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")

                try:
                    batch_result = process_func(batch)
                    results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
                except Exception as e:
                    logging.error(f"Error processing batch {batch_num}: {e}")
                    continue

                # Optional garbage collection between batches
                if batch_num % 10 == 0:
                    gc.collect()

            return results

        except Exception as e:
            logging.error(f"Error in batch processing: {e}")
            return []


# Global instances
performance_monitor = PerformanceMonitor()
performance_profiler = PerformanceProfiler()

# Convenience functions
def start_monitoring(interval_seconds=60):
    """Start performance monitoring"""
    performance_monitor.start_monitoring(interval_seconds)

def stop_monitoring():
    """Stop performance monitoring"""
    performance_monitor.stop_monitoring()

def get_memory_status():
    """Get current memory status"""
    return performance_monitor.get_memory_usage()

def optimize_memory():
    """Optimize memory usage"""
    return performance_monitor.optimize_memory()

def profile_function(func_name=None):
    """Decorator for profiling functions"""
    return performance_profiler.profile(func_name)