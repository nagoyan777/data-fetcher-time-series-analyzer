#!/usr/bin/env python3
"""
Time Series Analyzer - Core Business Logic
Statistical analysis, trend detection, and data transformation algorithms
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from scipy import stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesAnalyzer:
    """Core time series analysis algorithms and statistical computations"""

    def __init__(self):
        self.analysis_cache = {}

    def analyze_series(self, data, source_name=None):
        """Comprehensive time series analysis"""
        try:
            if not data or not isinstance(data, list):
                return self.create_empty_analysis()

            df = self.prepare_dataframe(data)
            if df.empty:
                return self.create_empty_analysis()

            # Core statistical analysis
            analysis = {
                'source_name': source_name or 'Unknown',
                'timestamp': datetime.now().isoformat(),
                'data_points': len(df),
                'time_range': self.get_time_range(df),
                'basic_stats': self.calculate_basic_statistics(df),
                'trend_analysis': self.analyze_trend(df),
                'seasonality': self.detect_seasonality(df),
                'anomalies': self.detect_anomalies(df),
                'correlations': self.calculate_autocorrelation(df),
                'volatility': self.calculate_volatility(df),
                'distribution': self.analyze_distribution(df),
                'quality_metrics': self.assess_data_quality(df)
            }

            # Cache results
            cache_key = f"{source_name}_{len(data)}_{hash(str(data))}"
            self.analysis_cache[cache_key] = analysis

            return analysis

        except Exception as e:
            logging.error(f"Error in time series analysis: {e}")
            return self.create_error_analysis(str(e))

    def prepare_dataframe(self, data):
        """Convert data to pandas DataFrame with proper datetime indexing"""
        try:
            df = pd.DataFrame(data)

            # Handle timestamp column
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            else:
                # Create synthetic timestamps
                df.index = pd.date_range(
                    start=datetime.now() - timedelta(hours=len(df)),
                    periods=len(df),
                    freq='H'
                )

            # Ensure numeric values
            if 'value' in df.columns:
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
            else:
                logging.warning("No 'value' column found in data")
                return pd.DataFrame()

            # Remove NaN values
            df = df.dropna()

            return df

        except Exception as e:
            logging.error(f"Error preparing dataframe: {e}")
            return pd.DataFrame()

    def calculate_basic_statistics(self, df):
        """Calculate comprehensive basic statistics"""
        try:
            values = df['value']

            return {
                'count': len(values),
                'mean': float(values.mean()),
                'median': float(values.median()),
                'std': float(values.std()),
                'variance': float(values.var()),
                'min': float(values.min()),
                'max': float(values.max()),
                'range': float(values.max() - values.min()),
                'q25': float(values.quantile(0.25)),
                'q75': float(values.quantile(0.75)),
                'iqr': float(values.quantile(0.75) - values.quantile(0.25)),
                'skewness': float(values.skew()),
                'kurtosis': float(values.kurtosis()),
                'coefficient_of_variation': float(values.std() / values.mean()) if values.mean() != 0 else 0
            }

        except Exception as e:
            logging.error(f"Error calculating basic statistics: {e}")
            return {}

    def analyze_trend(self, df):
        """Analyze trend patterns using multiple methods"""
        try:
            values = df['value'].values
            time_index = np.arange(len(values))

            # Linear trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_index, values)

            # Moving averages
            ma_short = df['value'].rolling(window=min(7, len(df)//4)).mean()
            ma_long = df['value'].rolling(window=min(30, len(df)//2)).mean()

            # Trend direction
            if abs(slope) < std_err:
                trend_direction = 'stable'
            elif slope > 0:
                trend_direction = 'increasing'
            else:
                trend_direction = 'decreasing'

            return {
                'trend_direction': trend_direction,
                'slope': float(slope),
                'r_squared': float(r_value ** 2),
                'p_value': float(p_value),
                'trend_strength': abs(float(r_value)),
                'ma_short_last': float(ma_short.iloc[-1]) if not ma_short.empty else None,
                'ma_long_last': float(ma_long.iloc[-1]) if not ma_long.empty else None,
                'trend_acceleration': self.calculate_trend_acceleration(values)
            }

        except Exception as e:
            logging.error(f"Error in trend analysis: {e}")
            return {}

    def detect_seasonality(self, df):
        """Detect seasonal patterns in the data"""
        try:
            if len(df) < 24:  # Need minimum data for seasonality
                return {'seasonal_pattern': 'insufficient_data'}

            values = df['value']

            # Hour-based seasonality (if timestamps available)
            hourly_pattern = {}
            if hasattr(df.index, 'hour'):
                hourly_means = values.groupby(df.index.hour).mean()
                hourly_pattern = {
                    'hourly_variation': float(hourly_means.std()),
                    'peak_hour': int(hourly_means.idxmax()),
                    'low_hour': int(hourly_means.idxmin())
                }

            # Day-based seasonality
            daily_pattern = {}
            if hasattr(df.index, 'dayofweek'):
                daily_means = values.groupby(df.index.dayofweek).mean()
                daily_pattern = {
                    'daily_variation': float(daily_means.std()),
                    'peak_day': int(daily_means.idxmax()),
                    'low_day': int(daily_means.idxmin())
                }

            return {
                'seasonal_pattern': 'detected' if hourly_pattern or daily_pattern else 'none',
                'hourly_patterns': hourly_pattern,
                'daily_patterns': daily_pattern,
                'seasonality_strength': self.calculate_seasonality_strength(values)
            }

        except Exception as e:
            logging.error(f"Error in seasonality detection: {e}")
            return {}

    def detect_anomalies(self, df):
        """Detect anomalies using statistical methods"""
        try:
            values = df['value']

            # Z-score method
            z_scores = np.abs(stats.zscore(values))
            z_anomalies = values[z_scores > 3]

            # IQR method
            q25, q75 = values.quantile([0.25, 0.75])
            iqr = q75 - q25
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr
            iqr_anomalies = values[(values < lower_bound) | (values > upper_bound)]

            # Peak detection
            peaks, _ = find_peaks(values, height=values.mean() + 2*values.std())
            valleys, _ = find_peaks(-values, height=-(values.mean() - 2*values.std()))

            return {
                'anomaly_count': len(z_anomalies) + len(iqr_anomalies),
                'z_score_anomalies': len(z_anomalies),
                'iqr_anomalies': len(iqr_anomalies),
                'peaks_count': len(peaks),
                'valleys_count': len(valleys),
                'anomaly_percentage': float((len(z_anomalies) + len(iqr_anomalies)) / len(values) * 100),
                'max_z_score': float(z_scores.max()),
                'anomaly_severity': 'high' if z_scores.max() > 5 else 'medium' if z_scores.max() > 3 else 'low'
            }

        except Exception as e:
            logging.error(f"Error in anomaly detection: {e}")
            return {}

    def calculate_autocorrelation(self, df):
        """Calculate autocorrelation patterns"""
        try:
            values = df['value']

            if len(values) < 10:
                return {'autocorrelation': 'insufficient_data'}

            # Calculate autocorrelation for different lags
            max_lag = min(20, len(values) // 2)
            autocorr_values = [values.autocorr(lag=i) for i in range(1, max_lag + 1)]
            autocorr_values = [v for v in autocorr_values if not pd.isna(v)]

            if not autocorr_values:
                return {'autocorrelation': 'no_correlation'}

            return {
                'max_autocorr': float(max(autocorr_values)),
                'avg_autocorr': float(np.mean(autocorr_values)),
                'lag_of_max_autocorr': autocorr_values.index(max(autocorr_values)) + 1,
                'significant_lags': len([v for v in autocorr_values if abs(v) > 0.3])
            }

        except Exception as e:
            logging.error(f"Error calculating autocorrelation: {e}")
            return {}

    def calculate_volatility(self, df):
        """Calculate volatility metrics"""
        try:
            values = df['value']

            if len(values) < 2:
                return {'volatility': 'insufficient_data'}

            # Calculate returns
            returns = values.pct_change().dropna()

            if len(returns) == 0:
                return {'volatility': 'no_variation'}

            return {
                'volatility': float(returns.std()),
                'annualized_volatility': float(returns.std() * np.sqrt(252)),  # Assuming daily data
                'max_drawdown': float(self.calculate_max_drawdown(values)),
                'value_at_risk_95': float(returns.quantile(0.05)),
                'sharpe_ratio': float(returns.mean() / returns.std()) if returns.std() != 0 else 0
            }

        except Exception as e:
            logging.error(f"Error calculating volatility: {e}")
            return {}

    def analyze_distribution(self, df):
        """Analyze data distribution"""
        try:
            values = df['value']

            # Normality test
            _, normality_p = stats.normaltest(values)

            # Histogram bins
            hist, bin_edges = np.histogram(values, bins=20)

            return {
                'is_normal': bool(normality_p > 0.05),
                'normality_p_value': float(normality_p),
                'distribution_shape': 'normal' if normality_p > 0.05 else 'non_normal',
                'outlier_count': len(values[np.abs(stats.zscore(values)) > 2]),
                'histogram_bins': len(hist),
                'mode_estimate': float(values.mode().iloc[0]) if not values.mode().empty else None
            }

        except Exception as e:
            logging.error(f"Error analyzing distribution: {e}")
            return {}

    def assess_data_quality(self, df):
        """Assess overall data quality"""
        try:
            values = df['value']

            # Missing data
            missing_count = values.isna().sum()

            # Duplicate timestamps
            duplicate_timestamps = df.index.duplicated().sum()

            # Data consistency
            zero_values = (values == 0).sum()
            negative_values = (values < 0).sum()

            quality_score = 100
            if missing_count > 0:
                quality_score -= (missing_count / len(df)) * 30
            if duplicate_timestamps > 0:
                quality_score -= (duplicate_timestamps / len(df)) * 20
            if zero_values > len(df) * 0.1:  # More than 10% zeros
                quality_score -= 15

            return {
                'quality_score': max(0, float(quality_score)),
                'missing_values': int(missing_count),
                'duplicate_timestamps': int(duplicate_timestamps),
                'zero_values': int(zero_values),
                'negative_values': int(negative_values),
                'data_completeness': float((len(df) - missing_count) / len(df) * 100),
                'quality_rating': 'excellent' if quality_score > 90 else 'good' if quality_score > 70 else 'fair' if quality_score > 50 else 'poor'
            }

        except Exception as e:
            logging.error(f"Error assessing data quality: {e}")
            return {}

    def get_time_range(self, df):
        """Get time range information"""
        try:
            if df.empty:
                return {}

            start_time = df.index.min()
            end_time = df.index.max()
            duration = end_time - start_time

            return {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_hours': float(duration.total_seconds() / 3600),
                'duration_days': float(duration.days),
                'frequency_estimate': self.estimate_frequency(df)
            }

        except Exception as e:
            logging.error(f"Error getting time range: {e}")
            return {}

    def calculate_trend_acceleration(self, values):
        """Calculate trend acceleration (second derivative)"""
        try:
            if len(values) < 3:
                return 0.0

            # First derivative (velocity)
            first_diff = np.diff(values)
            # Second derivative (acceleration)
            second_diff = np.diff(first_diff)

            return float(np.mean(second_diff))

        except:
            return 0.0

    def calculate_seasonality_strength(self, values):
        """Calculate seasonality strength measure"""
        try:
            if len(values) < 24:
                return 0.0

            # Simple measure based on hour-of-day variation
            seasonal_var = 0.0
            total_var = values.var()

            if total_var > 0:
                seasonal_var = min(1.0, seasonal_var / total_var)

            return float(seasonal_var)

        except:
            return 0.0

    def calculate_max_drawdown(self, values):
        """Calculate maximum drawdown"""
        try:
            cumulative = values.cummax()
            drawdown = (values - cumulative) / cumulative
            return drawdown.min()

        except:
            return 0.0

    def estimate_frequency(self, df):
        """Estimate data frequency"""
        try:
            if len(df) < 2:
                return "insufficient_data"

            time_diffs = df.index.to_series().diff().dropna()
            median_diff = time_diffs.median()

            if median_diff <= timedelta(minutes=1):
                return "minute"
            elif median_diff <= timedelta(hours=1):
                return "hourly"
            elif median_diff <= timedelta(days=1):
                return "daily"
            elif median_diff <= timedelta(weeks=1):
                return "weekly"
            else:
                return "irregular"

        except:
            return "unknown"

    def create_empty_analysis(self):
        """Create empty analysis structure"""
        return {
            'source_name': 'Unknown',
            'timestamp': datetime.now().isoformat(),
            'data_points': 0,
            'status': 'no_data',
            'message': 'No data available for analysis'
        }

    def create_error_analysis(self, error_message):
        """Create error analysis structure"""
        return {
            'source_name': 'Unknown',
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error_message': error_message,
            'message': f'Analysis failed: {error_message}'
        }

    def compare_series(self, series1, series2):
        """Compare two time series"""
        try:
            analysis1 = self.analyze_series(series1, "Series 1")
            analysis2 = self.analyze_series(series2, "Series 2")

            if analysis1.get('status') == 'error' or analysis2.get('status') == 'error':
                return {'status': 'error', 'message': 'One or both series could not be analyzed'}

            # Correlation analysis
            df1 = self.prepare_dataframe(series1)
            df2 = self.prepare_dataframe(series2)

            correlation = 0.0
            if not df1.empty and not df2.empty:
                min_len = min(len(df1), len(df2))
                correlation = df1['value'][:min_len].corr(df2['value'][:min_len])

            return {
                'series1_analysis': analysis1,
                'series2_analysis': analysis2,
                'correlation': float(correlation) if not pd.isna(correlation) else 0.0,
                'comparison_summary': {
                    'mean_difference': analysis1.get('basic_stats', {}).get('mean', 0) - analysis2.get('basic_stats', {}).get('mean', 0),
                    'volatility_ratio': analysis1.get('volatility', {}).get('volatility', 0) / max(analysis2.get('volatility', {}).get('volatility', 1), 0.001),
                    'trend_similarity': abs(analysis1.get('trend_analysis', {}).get('slope', 0) - analysis2.get('trend_analysis', {}).get('slope', 0))
                }
            }

        except Exception as e:
            logging.error(f"Error comparing series: {e}")
            return {'status': 'error', 'message': str(e)}