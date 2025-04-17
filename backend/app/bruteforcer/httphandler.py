import asyncio
import aiohttp
import logging
import time
from typing import Optional

logger = logging.getLogger('httphandler')

class HttpResponse:
    """Simple class to hold HTTP response information."""
    def __init__(self, status_code: int, content: bytes, headers: dict, text: str):
        self.status_code = status_code
        self.content = content
        self.headers = headers
        self.text = text

class HttpHandler:
    """Handles HTTP requests with rate limiting."""
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self._last_request_time = 0
        self._session = None

    async def _get_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close_session(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def fetch(self, url: str, timeout: float = 5.0) -> Optional[HttpResponse]:
        """
        Fetches the content of a URL with rate limiting and error handling.

        Args:
            url: The URL to fetch.
            timeout: Request timeout in seconds.

        Returns:
            An HttpResponse object if successful, None otherwise.
        """
        now = time.time()
        wait_time = self.rate_limit - (now - self._last_request_time)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self._last_request_time = time.time()

        session = await self._get_session()
        try:
            async with session.get(url, timeout=timeout, allow_redirects=True) as response:
                await response.read()  # Ensure the response content is fully read
                return HttpResponse(
                    status_code=response.status,
                    content=await response.read(),
                    headers=dict(response.headers),
                    text=await response.text(errors='ignore') # Handle potential encoding issues
                )
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching {url}: {e}")
            return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()