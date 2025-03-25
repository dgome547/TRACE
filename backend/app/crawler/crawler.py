import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import csv

crawler_state = {
    "running": False,
    "paused": False,
    "stopped": False
}

class Crawler:
    def __init__(self, output_file="crawl_results.csv"):
        self.visited = set()
        self.output_file = output_file
        self.results = []

    def valid_url(self, url: str) -> bool:
        return url.startswith("http://") or url.startswith("https://")

    async def start_crawling(self, start_url: str, config: dict, http_handler, websocket=None):
        self.visited.clear()
        self.results = []
        await self._crawl(start_url, config, 0, http_handler, websocket)
        self.export_to_csv()

    async def _crawl(self, url: str, config: dict, depth: int, http_handler, websocket=None):
        if crawler_state["stopped"] or depth >= config["depth_limit"] or url in self.visited:
            return

        while crawler_state["paused"]:
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
        with open(self.output_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "Depth"])
            writer.writerows(self.results)
        print(f"Results exported to {self.output_file}")

    # Add this at the bottom of crawler.py
async def run_crawler(config: dict, websocket=None):
    print("Crawler started with config:")
    for key, value in config.items():
        print(f"{key}: {value}")

    crawler = Crawler()

    class DummyHttp:
        def fetch(self, url, timeout):
            import requests
            try:
                return requests.get(url, timeout=timeout)
            except:
                return None

    await crawler.start_crawling(
        start_url=config["targetUrl"],
        config={
            "depth_limit": config["crawlDepth"],
            "timeout": config["requestDelay"]
        },
        http_handler=DummyHttp(),
        websocket=websocket
    )