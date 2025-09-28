"""
Data Fetching Engine - Core Implementation
HTTP client with retry logic and time series data processing
Adapted from literature analysis project patterns
"""
import asyncio
import aiohttp
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import time

class DataFetchingEngine:
    """Core engine for fetching time series data from APIs"""

    def __init__(self, timeout: int = 30, max_retries: int = 3, rate_limit_delay: float = 1.0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.session = None
        self.last_request_time = 0

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_data_async(self, url: str, headers: Optional[Dict] = None,
                              params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fetch data from API endpoint with retry logic and rate limiting

        Args:
            url: API endpoint URL
            headers: Optional HTTP headers
            params: Optional query parameters

        Returns:
            Dict containing response data and metadata
        """
        # Ensure rate limiting
        await self._enforce_rate_limit()

        headers = headers or {}
        params = params or {}

        for attempt in range(self.max_retries):
            try:
                if not self.session:
                    raise RuntimeError("Session not initialized. Use 'async with' context manager.")

                async with self.session.get(url, headers=headers, params=params) as response:
                    self.last_request_time = time.time()

                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'data': data,
                            'status_code': response.status,
                            'timestamp': datetime.now().isoformat(),
                            'url': str(response.url),
                            'attempt': attempt + 1
                        }
                    elif response.status == 429:  # Rate limited
                        logging.warning(f"Rate limited (429) on attempt {attempt + 1}")
                        await asyncio.sleep(self.rate_limit_delay * (2 ** attempt))
                        continue
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.warning(f"Request failed on attempt {attempt + 1}: {str(e)}")

                if attempt == self.max_retries - 1:
                    return {
                        'success': False,
                        'error': str(e),
                        'status_code': getattr(e, 'status', None),
                        'timestamp': datetime.now().isoformat(),
                        'url': url,
                        'attempts': self.max_retries
                    }

                # Exponential backoff
                await asyncio.sleep(self.rate_limit_delay * (2 ** attempt))

        return {
            'success': False,
            'error': 'Max retries exceeded',
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'attempts': self.max_retries
        }

    def fetch_data_sync(self, url: str, headers: Optional[Dict] = None,
                       params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Synchronous version of data fetching (for backward compatibility)

        Args:
            url: API endpoint URL
            headers: Optional HTTP headers
            params: Optional query parameters

        Returns:
            Dict containing response data and metadata
        """
        headers = headers or {}
        params = params or {}

        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                current_time = time.time()
                if current_time - self.last_request_time < self.rate_limit_delay:
                    time.sleep(self.rate_limit_delay - (current_time - self.last_request_time))

                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )

                self.last_request_time = time.time()

                if response.status_code == 200:
                    return {
                        'success': True,
                        'data': response.json(),
                        'status_code': response.status_code,
                        'timestamp': datetime.now().isoformat(),
                        'url': response.url,
                        'attempt': attempt + 1
                    }
                elif response.status_code == 429:  # Rate limited
                    logging.warning(f"Rate limited (429) on attempt {attempt + 1}")
                    time.sleep(self.rate_limit_delay * (2 ** attempt))
                    continue
                else:
                    response.raise_for_status()

            except (requests.RequestException, requests.Timeout) as e:
                logging.warning(f"Request failed on attempt {attempt + 1}: {str(e)}")

                if attempt == self.max_retries - 1:
                    return {
                        'success': False,
                        'error': str(e),
                        'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                        'timestamp': datetime.now().isoformat(),
                        'url': url,
                        'attempts': self.max_retries
                    }

                # Exponential backoff
                time.sleep(self.rate_limit_delay * (2 ** attempt))

        return {
            'success': False,
            'error': 'Max retries exceeded',
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'attempts': self.max_retries
        }

    async def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        if current_time - self.last_request_time < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - (current_time - self.last_request_time))

    def extract_time_series_value(self, data: Dict, data_path: str) -> Any:
        """
        Extract value from nested JSON using dot notation

        Args:
            data: JSON response data
            data_path: Dot notation path (e.g., 'main.temp', 'bitcoin.usd')

        Returns:
            Extracted value or None if path not found
        """
        try:
            value = data
            for key in data_path.split('.'):
                if key.isdigit():
                    value = value[int(key)]
                else:
                    value = value[key]
            return value
        except (KeyError, IndexError, TypeError) as e:
            logging.error(f"Failed to extract value at path '{data_path}': {str(e)}")
            return None

    def create_time_series_point(self, value: Any, source_url: str,
                                data_path: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Create a standardized time series data point

        Args:
            value: The extracted value
            source_url: Source API URL
            data_path: Data extraction path
            metadata: Optional additional metadata

        Returns:
            Standardized time series data point
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'value': value,
            'source_url': source_url,
            'data_path': data_path,
            'metadata': metadata or {},
            'quality': self._assess_data_quality(value)
        }

    def _assess_data_quality(self, value: Any) -> str:
        """
        Assess data quality of extracted value

        Args:
            value: The extracted value

        Returns:
            Quality assessment: 'good', 'warning', 'error'
        """
        if value is None:
            return 'error'

        # Check for numeric values
        try:
            float(value)
            return 'good'
        except (ValueError, TypeError):
            # Non-numeric values are still valid but marked as warning
            return 'warning'

    def validate_api_response(self, response_data: Dict) -> Dict[str, Any]:
        """
        Validate API response structure and content

        Args:
            response_data: Response from fetch_data methods

        Returns:
            Validation results with errors and warnings
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'quality_score': 100
        }

        if not response_data.get('success', False):
            validation['is_valid'] = False
            validation['errors'].append(f"Request failed: {response_data.get('error', 'Unknown error')}")
            validation['quality_score'] = 0
            return validation

        data = response_data.get('data')
        if not data:
            validation['is_valid'] = False
            validation['errors'].append("No data in response")
            validation['quality_score'] = 0
            return validation

        # Check response structure
        if not isinstance(data, (dict, list)):
            validation['warnings'].append("Response is not JSON object or array")
            validation['quality_score'] -= 20

        # Check for common error indicators
        if isinstance(data, dict):
            if 'error' in data:
                validation['warnings'].append(f"API returned error: {data['error']}")
                validation['quality_score'] -= 30

            if 'status' in data and data['status'] != 'success':
                validation['warnings'].append(f"API status: {data['status']}")
                validation['quality_score'] -= 20

        return validation


class TimeSeriesDataProcessor:
    """Process and validate time series data"""

    @staticmethod
    def process_raw_response(response_data: Dict, data_path: str) -> Dict[str, Any]:
        """
        Process raw API response into time series format

        Args:
            response_data: Raw response from DataFetchingEngine
            data_path: Path to extract value from response

        Returns:
            Processed time series data
        """
        if not response_data.get('success', False):
            return {
                'success': False,
                'error': response_data.get('error', 'Unknown error'),
                'timestamp': datetime.now().isoformat()
            }

        # Extract value
        engine = DataFetchingEngine()
        value = engine.extract_time_series_value(response_data['data'], data_path)

        if value is None:
            return {
                'success': False,
                'error': f"Failed to extract value at path: {data_path}",
                'timestamp': datetime.now().isoformat()
            }

        # Create time series point
        time_series_point = engine.create_time_series_point(
            value=value,
            source_url=response_data.get('url', 'unknown'),
            data_path=data_path,
            metadata={
                'status_code': response_data.get('status_code'),
                'attempt': response_data.get('attempt'),
                'response_timestamp': response_data.get('timestamp')
            }
        )

        return {
            'success': True,
            'time_series_point': time_series_point,
            'raw_response': response_data['data'],
            'timestamp': datetime.now().isoformat()
        }