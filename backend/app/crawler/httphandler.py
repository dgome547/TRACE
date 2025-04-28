import asyncio
import requests
import logging
from typing import Optional


class HttpHandler:
    def __init__(self, rate_limit: float = 1.0, user_agent: str = 'TRACE-Crawler/1.0', proxy: str = None):
        """
        HTTP Handler for web requests with rate limiting, custom user agent, and proxy support.

        Args:
            rate_limit (float): Minimum time between requests in seconds
            user_agent (str): User-Agent string to use for requests
            proxy (str): Proxy URL to use for requests (e.g., 'http://proxy:port')
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.user_agent = user_agent
        self.proxy = proxy

    async def fetch(self, url: str, timeout: float) -> Optional[requests.Response]:
        """
        Fetch a URL with rate limiting

        Args:
            url (str): The URL to fetch
            timeout (float): Request timeout in seconds

        Returns:
            Optional[requests.Response]: Response object or None if failed
        """
        try:
            # Implement rate limiting
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.rate_limit:
                await asyncio.sleep(self.rate_limit - time_since_last)

            self.last_request_time = asyncio.get_event_loop().time()

            # Prepare headers
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            # Prepare proxies if configured
            proxies = None
            if self.proxy:
                proxies = {
                    'http': self.proxy,
                    'https': self.proxy
                }

            response = requests.get(url, timeout=timeout, headers=headers, proxies=proxies)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error while fetching {url}: {str(e)}")
            return None