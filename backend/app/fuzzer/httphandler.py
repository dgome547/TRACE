import asyncio
import requests
import logging
from typing import Optional

class HttpHandler:
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.user_agent = 'TRACE-Fuzzer/1.0'
        self.proxy = None

    async def fetch(self, url: str, timeout: float) -> Optional[requests.Response]:
        try:
            # Rate limiting
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.rate_limit:
                await asyncio.sleep(self.rate_limit - time_since_last)

            self.last_request_time = asyncio.get_event_loop().time()

            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            proxies = {
                'http': self.proxy,
                'https': self.proxy
            } if self.proxy else None

            response = requests.get(url, timeout=timeout, headers=headers, proxies=proxies)
            response.raise_for_status()
            return response

        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error while fetching {url}: {str(e)}")
            return None
