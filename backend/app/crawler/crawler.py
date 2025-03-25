import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import csv
import re
import requests
from typing import Optional, Dict, Any

class HttpHandler:
    def fetch(self, url: str, timeout: float) -> Optional[requests.Response]:
        try:
            return requests.get(url, timeout=timeout)
        except requests.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

class Crawler:
    def __init__(self, output_file="crawl_results.csv"):
        self.visited = set()
        self.output_file = output_file
        self.results = []
        self.state = {
            "running": False,
            "paused": False,
            "stopped": False
        }

    def reset_state(self):
        self.state = {
            "running": False,
            "paused": False,
            "stopped": False
        }

    def valid_url(self, url: str) -> bool:
    
        #Validates if a URL is properly formatted and meets security criteria.
        
        #Args:
        #    url (str): The URL to validate
            
        #Returns:
        #    bool: True if URL is valid, False otherwise

        try:
            # Basic type check
            if not isinstance(url, str) or not url:
                return False
                
            # Check for allowed schemes
            allowed_schemes = {'http', 'https'}
            if not any(url.startswith(scheme + '://') for scheme in allowed_schemes):
                return False
                
            # Check for common URL patterns
            url_pattern = re.compile(
                r'^'
                r'(?:http|https)://'  # scheme
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip address
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                
            if not url_pattern.match(url):
                return False
                
            # Additional security checks
            # Prevent URLs with user:pass@ format
            if '@' in url:
                return False
                
            # Check for common file extensions that might be dangerous
            dangerous_extensions = {'.exe', '.dll', '.bat', '.cmd', '.sh', '.jar', '.app'}
            if any(url.lower().endswith(ext) for ext in dangerous_extensions):
                return False
                
            # Check URL length
            if len(url) > 2048:  # Common URL length limit
                return False
                
            return True
            
        except Exception:
            return False

    async def start_crawling(self, start_url: str, config: dict, http_handler, websocket=None):
        self.visited.clear()
        self.results = []
        await self._crawl(start_url, config, 0, http_handler, websocket)
        self.export_to_csv()

    async def _crawl(self, url: str, config: dict, depth: int, http_handler, websocket=None):
        if self.state["stopped"] or depth >= config["depth_limit"] or url in self.visited:
            return

        while self.state["paused"]:
            await asyncio.sleep(1)

        self.visited.add(url)
        self.results.append((url, depth))
        print(f"Crawling: {url}")

        # Send actual crawled URL to frontend
        if websocket:
            await websocket.send_json({"url": url})

        response = http_handler.fetch(url, config["timeout"])
        if response is None:
            print(f"Failed to fetch {url}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            next_url = urljoin(url, link["href"])
            if self.valid_url(next_url):
                await self._crawl(next_url, config, depth + 1, http_handler, websocket)

    def export_to_csv(self):
        try:
            with open(self.output_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["URL", "Depth"])
                writer.writerows(self.results)
            print(f"Results exported to {self.output_file}")
        except IOError as e:
            print(f"Error exporting results to CSV: {str(e)}")

async def run_crawler(config: Dict[str, Any], websocket=None):
    print("Crawler started with config:")
    for key, value in config.items():
        print(f"{key}: {value}")

    crawler = Crawler()
    crawler.reset_state()
    
    await crawler.start_crawling(
        start_url=config["targetUrl"],
        config={
            "depth_limit": config["crawlDepth"],
            "timeout": config["requestDelay"]
        },
        http_handler=HttpHandler(),
        websocket=websocket
    )