import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class Crawler:
    def __init__(self, output_file="crawl_results.csv"):
        self.visited = set()
        self.output_file = output_file  # Store output filename
        self.results = []  # Store crawled URLs for CSV export

    def validUrl(self, url: str) -> bool:
        return url.startswith("http://") or url.startswith("https://")

    def crawlStarted(self, url: str) -> bool:
        return url in self.visited

    def pathsFollowed(self, config: dict):
        return len(self.visited) <= config["depth_limit"]

    def reachDepthLimit(self, depth_limit: int) -> bool:
        return len(self.visited) >= depth_limit

    def start_crawling(self, start_url: str, config: dict, http_handler) -> None:
        assert isinstance(config, dict), "Config must be a dictionary"
        assert isinstance(config["depth_limit"], int) and config[
            "depth_limit"] > 0, "Depth limit must be a positive integer"
        assert isinstance(config["timeout"], int) and config["timeout"] > 0, "Timeout must be a positive integer"
        assert self.validUrl(start_url) and isinstance(start_url, str), "Invalid start URL"

        self.visited.clear()
        self.results = []  # Reset results before each crawl
        self._crawl(start_url, config, 0, http_handler)
        self.export_to_csv()  # Export data after crawling

    def _crawl(self, url: str, config: dict, depth: int, http_handler):
        if depth >= config["depth_limit"] or url in self.visited:
            return

        self.visited.add(url)
        print(f"Crawling: {url}")
        self.results.append((url, depth))  # Store URL with depth

        response = http_handler.fetch(url, config["timeout"])
        if response is None:
            print(f"Failed to fetch {url}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            next_url = urljoin(url, link["href"])
            if self.validUrl(next_url):
                self._crawl(next_url, config, depth + 1, http_handler)

    def export_to_csv(self):
        with open(self.output_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "Depth"])
            writer.writerows(self.results)
        print(f"Results exported to {self.output_file}")

