import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.bruteforcer.httphandler import HttpHandler
from app.crawler.utils import valid_url, validate_config


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
            "failed_fetches": 0,
            "processed_requests": 0,
            "filtered_requests": 0,
            "requests_per_second": 0,
            "running_time": 0
        }
        # Store detailed info for each URL as required by SRS-31
        self.detailed_results = []

    def reset_state(self):
        """Reset crawler state and statistics"""
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
            "failed_fetches": 0,
            "processed_requests": 0,
            "filtered_requests": 0,
            "requests_per_second": 0,
            "running_time": 0
        }
        self.detailed_results = []
        self.visited.clear()
        self.results = []

    async def start_crawling(self, start_url: str, config: dict, http_handler, websocket=None):
        """
        Start the crawling process

        Args:
            start_url (str): The starting URL
            config (dict): Crawl configuration parameters
            http_handler (HttpHandler): Instance of HTTP handler
            websocket: Optional websocket for real-time updates
        """
        self.stats["start_time"] = datetime.now()
        self.state["running"] = True

        try:
            await self._crawl(start_url, config, 0, http_handler, websocket)
            self.export_to_csv()
            self.stats["end_time"] = datetime.now()
            self.log_stats()
            self.state["running"] = False
        except Exception as e:
            logging.error(f"Error during crawling: {str(e)}")
            self.state["running"] = False
            raise

    def log_stats(self):
        """Log detailed crawling statistics"""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds() if self.stats["end_time"] else 0
        self.stats["running_time"] = duration
        logging.info(f"Crawling Statistics:")
        logging.info(f"Total URLs crawled: {self.stats['total_urls']}")
        logging.info(f"Successful fetches: {self.stats['successful_fetches']}")
        logging.info(f"Failed fetches: {self.stats['failed_fetches']}")
        logging.info(f"Filtered requests: {self.stats['filtered_requests']}")
        logging.info(f"Processed requests: {self.stats['processed_requests']}")
        logging.info(f"Total duration: {duration:.2f} seconds")
        if self.stats['processed_requests'] > 0:
            logging.info(f"Average time per URL: {duration / self.stats['processed_requests']:.2f} seconds")
            logging.info(f"Requests per second: {self.stats['requests_per_second']:.2f}")

    async def _crawl(self, url: str, config: dict, depth: int, http_handler, websocket=None):
        """
        Main crawl method to process a single URL

        Args:
            url (str): The URL to crawl
            config (dict): Crawl configuration
            depth (int): Current depth level
            http_handler (HttpHandler): Instance of HTTP handler
            websocket: Optional websocket for real-time updates
        """
        # Check stopping conditions
        if self.state["stopped"] or depth >= config["depth_limit"] or url in self.visited:
            if url in self.visited:
                self.stats["filtered_requests"] += 1
            return

        # Check if we've reached the max pages limit
        if "max_pages" in config and self.stats["processed_requests"] >= config["max_pages"]:
            self.state["stopped"] = True
            logging.info(f"Reached maximum page limit of {config['max_pages']}")
            return

        # Handle pause state
        while self.state["paused"]:
            await asyncio.sleep(1)

        # Update running time
        if self.stats["start_time"]:
            current_time = datetime.now()
            self.stats["running_time"] = (current_time - self.stats["start_time"]).total_seconds()

        self.visited.add(url)
        self.stats["total_urls"] += 1
        self.stats["processed_requests"] += 1

        # Calculate requests per second
        if self.stats["running_time"] > 0:
            self.stats["requests_per_second"] = self.stats["processed_requests"] / self.stats["running_time"]

        logging.info(f"Crawling: {url} (Depth: {depth})")

        # Prepare a detailed result entry
        result_entry = {
            "id": self.stats["processed_requests"],
            "url": url,
            "title": "",
            "word_count": 0,
            "character_count": 0,
            "links_found": 0,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }

        # Send progress update
        await self._send_update(websocket, url, result_entry, config, in_progress=True)

        response = await http_handler.fetch(url, config["timeout"])
        if response is None:
            self.stats["failed_fetches"] += 1
            logging.warning(f"Failed to fetch {url}")
            result_entry["error"] = "Failed to fetch URL"
            self.detailed_results.append(result_entry)
            return

        self.stats["successful_fetches"] += 1
        try:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title_tag = soup.find("title")
            result_entry["title"] = title_tag.get_text() if title_tag else "No title"

            # Get text content
            text_content = soup.get_text()
            result_entry["word_count"] = len(re.findall(r'\b\w+\b', text_content))
            result_entry["character_count"] = len(text_content)

            # Find links
            links = soup.find_all("a", href=True)
            result_entry["links_found"] = len(links)

            self.detailed_results.append(result_entry)

            # Send completed result update
            await self._send_update(websocket, url, result_entry, config, in_progress=False)

            # Continue crawling
            for link in links:
                next_url = urljoin(url, link["href"])
                if valid_url(next_url) and next_url not in self.visited:
                    await self._crawl(next_url, config, depth + 1, http_handler, websocket)
        except Exception as e:
            logging.error(f"Error parsing {url}: {str(e)}")
            result_entry["error"] = f"Error parsing content: {str(e)}"
            self.detailed_results.append(result_entry)

    async def _send_update(self, websocket, url, result_entry, config, in_progress=True):
        """Send update to websocket if available"""
        if websocket:
            try:
                progress = min(100, int(self.stats["processed_requests"] * 100 / config.get("max_pages", 100)))
                await websocket.send_json({
                    "url": url,
                    "stats": self.stats,
                    "current_result": result_entry,
                    "completed": not in_progress,
                    "progress": progress
                })
            except Exception as e:
                logging.error(f"Error sending to websocket: {str(e)}")

    def export_to_csv(self):
        """Export crawl results to CSV file"""
        try:
            with open(self.output_file, mode="w", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "URL"])
                writer.writerows([
                    [result["id"], result["url"]]
                    for result in self.detailed_results
                ])
            logging.info(f"Results exported to {self.output_file}")
        except IOError as e:
            logging.error(f"Error exporting results to CSV: {str(e)}")
            raise

    def export_to_json(self, filename="crawl_results.json"):
        """Export crawl results to JSON file"""
        try:
            with open(filename, mode="w", encoding='utf-8') as file:
                json.dump({
                    "stats": self.stats,
                    "results": self.detailed_results
                }, file, indent=2)
            logging.info(f"Results exported to {filename}")
        except IOError as e:
            logging.error(f"Error exporting results to JSON: {str(e)}")
            raise

    async def pause_crawler(self):
        """Pauses the crawler operation"""
        if self.state["running"] and not self.state["paused"]:
            self.state["paused"] = True
            logging.info("Crawler paused")
            return {"status": "paused", "message": "Crawler paused successfully"}
        return {"status": "error", "message": "Crawler is not running or already paused"}

    async def resume_crawler(self):
        """Resumes the crawler operation"""
        if self.state["running"] and self.state["paused"]:
            self.state["paused"] = False
            logging.info("Crawler resumed")
            return {"status": "resumed", "message": "Crawler resumed successfully"}
        return {"status": "error", "message": "Crawler is not paused"}

    async def stop_crawler(self, confirm=False):
        """
        Stops the crawler operation

        Args:
            confirm (bool): Confirmation flag required by SRS-30.4
        """
        if not confirm:
            return {"status": "confirmation_required", "message": "Confirmation required to stop crawler"}

        if self.state["running"]:
            self.state["stopped"] = True
            self.state["running"] = False
            self.state["paused"] = False
            self.stats["end_time"] = datetime.now()
            logging.info("Crawler stopped")
            return {"status": "stopped", "message": "Crawler stopped successfully"}
        return {"status": "error", "message": "Crawler is not running"}


async def run_crawler(config: Dict[str, Any], websocket=None) -> Dict[str, Any]:
    """
    Main function to run the crawler with given configuration

    Args:
        config (Dict[str, Any]): Crawler configuration parameters
        websocket: Optional websocket for real-time updates

    Returns:
        Dict[str, Any]: Results and statistics
    """
    logging.info("Validating crawler configuration...")
    is_valid, errors = validate_config(config)

    if not is_valid:
        error_response = {
            "status": "error",
            "errors": errors
        }
        if websocket:
            await websocket.send_json(error_response)
        return error_response

    logging.info("Crawler started with config:")
    for key, value in config.items():
        logging.info(f"{key}: {value}")

    crawler = Crawler(output_file=config.get("outputFile", "crawl_results.csv"))
    crawler.reset_state()

    # Set up HttpHandler with rate limiting from config
    http_handler = HttpHandler(rate_limit=float(config.get("requestDelay", 1.0)))

    # Set user agent if provided
    if config.get("userAgent"):
        http_handler.user_agent = config["userAgent"]

    # Handle proxy if provided
    if config.get("proxy"):
        http_handler.proxy = config["proxy"]

    try:
        await crawler.start_crawling(
            start_url=config["targetUrl"],
            config={
                "depth_limit": int(config.get("crawlDepth", 3)),
                "timeout": float(config.get("requestDelay", 5.0)),
                "max_pages": int(config.get("limitPages", 100)),
                "additional_params": config.get("additionalParams", {})
            },
            http_handler=http_handler,
            websocket=websocket
        )

        return {
            "status": "success",
            "stats": crawler.stats,
            "results": crawler.detailed_results
        }

    except Exception as e:
        error_msg = f"Error during crawling: {str(e)}"
        logging.error(error_msg)
        error_response = {
            "status": "error",
            "message": error_msg
        }
        if websocket:
            await websocket.send_json(error_response)
        return error_response