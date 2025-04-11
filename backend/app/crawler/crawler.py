import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import csv
import re
import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)

class HttpHandler:
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0

    async def fetch(self, url: str, timeout: float) -> Optional[requests.Response]:
        try:
            # Implement rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.rate_limit:
                await asyncio.sleep(self.rate_limit - time_since_last)
            
            self.last_request_time = time.time()
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'TRACE-Crawler/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            })
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error while fetching {url}: {str(e)}")
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
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_urls": 0,
            "successful_fetches": 0,
            "failed_fetches": 0
        }

    def reset_state(self):
        self.state = {
            "running": False,
            "paused": False,
            "stopped": False
        }
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_urls": 0,
            "successful_fetches": 0,
            "failed_fetches": 0
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
        self.stats["start_time"] = datetime.now()
        self.visited.clear()
        self.results = []
        try:
            await self._crawl(start_url, config, 0, http_handler, websocket)
            self.export_to_csv()
            self.stats["end_time"] = datetime.now()
            self.log_stats()
        except Exception as e:
            logging.error(f"Error during crawling: {str(e)}")
            raise

    def log_stats(self):
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        logging.info(f"Crawling Statistics:")
        logging.info(f"Total URLs crawled: {self.stats['total_urls']}")
        logging.info(f"Successful fetches: {self.stats['successful_fetches']}")
        logging.info(f"Failed fetches: {self.stats['failed_fetches']}")
        logging.info(f"Total duration: {duration:.2f} seconds")
        logging.info(f"Average time per URL: {duration/self.stats['total_urls']:.2f} seconds")

    async def _crawl(self, url: str, config: dict, depth: int, http_handler, websocket=None):
        if self.state["stopped"] or depth >= config["depth_limit"] or url in self.visited:
            return

        while self.state["paused"]:
            await asyncio.sleep(1)

        self.visited.add(url)
        self.results.append((url, depth))
        self.stats["total_urls"] += 1
        logging.info(f"Crawling: {url} (Depth: {depth})")

        if websocket:
            try:
                await websocket.send_json({"url": url})
            except Exception as e:
                logging.error(f"Error sending to websocket: {str(e)}")

        response = await http_handler.fetch(url, config["timeout"])
        if response is None:
            self.stats["failed_fetches"] += 1
            logging.warning(f"Failed to fetch {url}")
            return

        self.stats["successful_fetches"] += 1
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                next_url = urljoin(url, link["href"])
                if self.valid_url(next_url):
                    await self._crawl(next_url, config, depth + 1, http_handler, websocket)
        except Exception as e:
            logging.error(f"Error parsing {url}: {str(e)}")

    def export_to_csv(self):
        try:
            with open(self.output_file, mode="w", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["URL", "Depth", "Timestamp"])
                writer.writerows([(url, depth, datetime.now().isoformat()) for url, depth in self.results])
            logging.info(f"Results exported to {self.output_file}")
        except IOError as e:
            logging.error(f"Error exporting results to CSV: {str(e)}")
            raise

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