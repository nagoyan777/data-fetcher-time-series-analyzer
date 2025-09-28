#!/usr/bin/env python3
"""
API Client - Shared Utility
HTTP client with retry logic, rate limiting, and caching for data fetching
"""
import asyncio
import aiohttp
import requests
import time
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Optional, Dict, Any, List

class APIClient:
    """Enhanced HTTP client with retry, rate limiting, and caching"""

    def __init__(self, cache_dir="data/cache", default_timeout=30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_timeout = default_timeout

        # Rate limiting
        self.rate_limits = {}  # domain -> (requests, window_start)
        self.max_requests_per_minute = 60

        # Retry configuration
        self.max_retries = 3
        self.retry_backoff = [1, 2, 4]  # Exponential backoff in seconds

        # Session for connection pooling
        self.session = None

    async def get_async(self, url: str, headers: Optional[Dict] = None,
                       timeout: Optional[int] = None, use_cache: bool = True,
                       cache_duration: int = 3600) -> Dict[str, Any]:
        """Async GET request with retry and caching"""
        try:
            # Check cache first
            if use_cache:
                cached_data = self.get_cached_response(url, cache_duration)
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'from_cache': True,
                        'timestamp': datetime.now().isoformat()
                    }

            # Rate limiting check
            if not self.check_rate_limit(url):
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'retry_after': 60
                }

            # Make request with retry logic
            for attempt in range(self.max_retries):
                try:
                    async with aiohttp.ClientSession() as session:
                        timeout_obj = aiohttp.ClientTimeout(total=timeout or self.default_timeout)

                        async with session.get(url, headers=headers, timeout=timeout_obj) as response:
                            if response.status == 200:
                                data = await response.json()

                                # Cache successful response
                                if use_cache:
                                    self.cache_response(url, data)

                                return {
                                    'success': True,
                                    'data': data,
                                    'status_code': response.status,
                                    'from_cache': False,
                                    'timestamp': datetime.now().isoformat(),
                                    'attempt': attempt + 1
                                }

                            elif response.status == 429:  # Rate limited
                                retry_after = int(response.headers.get('Retry-After', 60))
                                await asyncio.sleep(retry_after)
                                continue

                            else:
                                error_text = await response.text()
                                if attempt == self.max_retries - 1:
                                    return {
                                        'success': False,
                                        'error': f'HTTP {response.status}: {error_text}',
                                        'status_code': response.status
                                    }

                except asyncio.TimeoutError:
                    if attempt == self.max_retries - 1:
                        return {
                            'success': False,
                            'error': 'Request timeout',
                            'timeout': timeout or self.default_timeout
                        }

                except Exception as e:
                    if attempt == self.max_retries - 1:
                        return {
                            'success': False,
                            'error': f'Request failed: {str(e)}'
                        }

                # Wait before retry (exponential backoff)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_backoff[attempt])

            return {
                'success': False,
                'error': 'Max retries exceeded'
            }

        except Exception as e:
            logging.error(f"Error in async GET request: {e}")
            return {
                'success': False,
                'error': f'Client error: {str(e)}'
            }

    def get_sync(self, url: str, headers: Optional[Dict] = None,
                timeout: Optional[int] = None, use_cache: bool = True,
                cache_duration: int = 3600) -> Dict[str, Any]:
        """Synchronous GET request with retry and caching"""
        try:
            # Check cache first
            if use_cache:
                cached_data = self.get_cached_response(url, cache_duration)
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'from_cache': True,
                        'timestamp': datetime.now().isoformat()
                    }

            # Rate limiting check
            if not self.check_rate_limit(url):
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'retry_after': 60
                }

            # Make request with retry logic
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        url,
                        headers=headers,
                        timeout=timeout or self.default_timeout
                    )

                    if response.status_code == 200:
                        data = response.json()

                        # Cache successful response
                        if use_cache:
                            self.cache_response(url, data)

                        return {
                            'success': True,
                            'data': data,
                            'status_code': response.status_code,
                            'from_cache': False,
                            'timestamp': datetime.now().isoformat(),
                            'attempt': attempt + 1
                        }

                    elif response.status_code == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        time.sleep(retry_after)
                        continue

                    else:
                        if attempt == self.max_retries - 1:
                            return {
                                'success': False,
                                'error': f'HTTP {response.status_code}: {response.text}',
                                'status_code': response.status_code
                            }

                except requests.exceptions.Timeout:
                    if attempt == self.max_retries - 1:
                        return {
                            'success': False,
                            'error': 'Request timeout',
                            'timeout': timeout or self.default_timeout
                        }

                except Exception as e:
                    if attempt == self.max_retries - 1:
                        return {
                            'success': False,
                            'error': f'Request failed: {str(e)}'
                        }

                # Wait before retry (exponential backoff)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_backoff[attempt])

            return {
                'success': False,
                'error': 'Max retries exceeded'
            }

        except Exception as e:
            logging.error(f"Error in sync GET request: {e}")
            return {
                'success': False,
                'error': f'Client error: {str(e)}'
            }

    def check_rate_limit(self, url: str) -> bool:
        """Check if request is within rate limits"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc

            current_time = time.time()

            if domain not in self.rate_limits:
                self.rate_limits[domain] = {'requests': [], 'window_start': current_time}
                return True

            # Clean old requests (older than 1 minute)
            domain_data = self.rate_limits[domain]
            domain_data['requests'] = [
                req_time for req_time in domain_data['requests']
                if current_time - req_time < 60
            ]

            # Check if under rate limit
            if len(domain_data['requests']) < self.max_requests_per_minute:
                domain_data['requests'].append(current_time)
                return True

            return False

        except Exception as e:
            logging.error(f"Error checking rate limit: {e}")
            return True  # Allow request if rate limit check fails

    def cache_response(self, url: str, data: Any) -> bool:
        """Cache API response"""
        try:
            # Create cache key from URL
            cache_key = hashlib.md5(url.encode()).hexdigest()
            cache_file = self.cache_dir / f"{cache_key}.json"

            cache_data = {
                'url': url,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'cache_key': cache_key
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)

            return True

        except Exception as e:
            logging.error(f"Error caching response: {e}")
            return False

    def get_cached_response(self, url: str, cache_duration: int = 3600) -> Optional[Any]:
        """Get cached response if valid"""
        try:
            cache_key = hashlib.md5(url.encode()).hexdigest()
            cache_file = self.cache_dir / f"{cache_key}.json"

            if not cache_file.exists():
                return None

            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time > timedelta(seconds=cache_duration):
                return None

            return cache_data['data']

        except Exception as e:
            logging.error(f"Error getting cached response: {e}")
            return None

    def clear_cache(self, older_than_hours: int = 24) -> int:
        """Clear old cache files"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            removed_count = 0

            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)

                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    if cache_time < cutoff_time:
                        cache_file.unlink()
                        removed_count += 1

                except Exception:
                    # Remove corrupted cache files
                    cache_file.unlink()
                    removed_count += 1

            logging.info(f"Cleared {removed_count} old cache files")
            return removed_count

        except Exception as e:
            logging.error(f"Error clearing cache: {e}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)

            # Get cache hit rate (simplified)
            hit_count = 0
            total_count = 0

            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    total_count += 1
                    # Simplified: consider as hit if accessed recently
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cache_time < timedelta(hours=1):
                        hit_count += 1
                except:
                    continue

            return {
                'total_files': len(cache_files),
                'total_size_mb': total_size / (1024 * 1024),
                'estimated_hit_rate': (hit_count / max(total_count, 1)) * 100,
                'cache_directory': str(self.cache_dir)
            }

        except Exception as e:
            logging.error(f"Error getting cache stats: {e}")
            return {}

    def test_connection(self, url: str) -> Dict[str, Any]:
        """Test connection to an API endpoint"""
        try:
            start_time = time.time()

            response = requests.head(url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # ms

            return {
                'success': True,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'headers': dict(response.headers),
                'url': url,
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Connection timeout',
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }

    def batch_get(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Make multiple GET requests (synchronous)"""
        results = []

        for url in urls:
            result = self.get_sync(url, **kwargs)
            result['url'] = url
            results.append(result)

            # Small delay between requests to be respectful
            time.sleep(0.1)

        return results

    async def batch_get_async(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Make multiple async GET requests"""
        tasks = []

        for url in urls:
            task = self.get_async(url, **kwargs)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Add URL to results and handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = {
                    'success': False,
                    'error': str(result),
                    'url': urls[i]
                }
            else:
                result['url'] = urls[i]

        return results

    def set_rate_limit(self, requests_per_minute: int):
        """Set custom rate limit"""
        self.max_requests_per_minute = requests_per_minute

    def set_retry_config(self, max_retries: int, backoff_pattern: List[int]):
        """Set custom retry configuration"""
        self.max_retries = max_retries
        self.retry_backoff = backoff_pattern

    def __del__(self):
        """Cleanup"""
        if self.session:
            try:
                asyncio.run(self.session.close())
            except:
                pass

# Global instance for use across apps
api_client = APIClient()