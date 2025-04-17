import os
import time
import asyncio
import logging
import re
import json
import csv
from typing import Dict, List, Optional, Any
from datetime import datetime
from httphandler import HttpHandler
from utils import (
    validate_url,
    validate_wordlist,
    load_wordlist,
    build_url,
    apply_filters
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('brute_forcer')


class BruteForceConfig:
    """Configuration for a brute force scan."""

    def __init__(self,
                 target_url: str,
                 wordlist_path: str,
                 top_level_directory: str = "",
                 hide_status: List[int] = None,
                 show_only_status: List[int] = None,
                 filter_by_content_length: Optional[str] = None,
                 request_timeout: float = 5.0,
                 max_concurrent_requests: int = 10,
                 rate_limit: float = 0.5,
                 additional_parameters: Dict[str, Any] = None,
                 output_format: str = "csv"):

        self.target_url = target_url
        self.wordlist_path = wordlist_path
        self.top_level_directory = top_level_directory
        self.hide_status = hide_status or []
        self.show_only_status = show_only_status or []
        self.filter_by_content_length = filter_by_content_length
        self.request_timeout = request_timeout
        self.max_concurrent_requests = max_concurrent_requests
        self.rate_limit = rate_limit
        self.additional_parameters = additional_parameters or {}
        self.output_format = output_format


class BruteForceResult:
    """Result from a single brute force request."""

    def __init__(self, id: int, url: str, payload: str):
        self.id = id
        self.url = url
        self.payload = payload
        # [SRS 27.5] and [SRS 28.3] require these specific fields in the data table
        self.status_code = 0
        self.response_time = 0.0
        self.content_length = 0
        self.word_count = 0
        self.line_count = 0
        self.char_count = 0
        self.error = None
        self.response_headers = {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization and UI display."""
        return {
            "id": self.id,
            "url": self.url,
            "payload": self.payload,
            "status_code": self.status_code,
            "response_time": round(self.response_time, 3),
            "content_length": self.content_length,
            "word_count": self.word_count,
            "line_count": self.line_count,
            "char_count": self.char_count,
            "error": self.error,
            "timestamp": self.timestamp
        }


class BruteForceStats:
    """Statistics for a brute force scan."""

    def __init__(self):
        # [SRS 27.4] and [SRS 28.4] require these metrics
        self.start_time = time.time()
        self.end_time = None
        self.processed_requests = 0
        self.filtered_requests = 0
        self.requests_per_second = 0.0

    @property
    def running_time(self) -> float:
        """Calculate the running time of the scan."""
        current_time = self.end_time if self.end_time else time.time()
        return current_time - self.start_time

    def update_requests_per_second(self) -> None:
        """Update the requests per second calculation."""
        runtime = self.running_time
        if runtime > 0:
            self.requests_per_second = self.processed_requests / runtime

    def formatted_running_time(self) -> str:
        """Return a formatted string of running time (HH:MM:SS)."""
        runtime = self.running_time
        hours, remainder = divmod(runtime, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary for JSON serialization and UI display."""
        return {
            "running_time": self.formatted_running_time(),
            "raw_running_time": self.running_time,
            "processed_requests": self.processed_requests,
            "filtered_requests": self.filtered_requests,
            "requests_per_second": round(self.requests_per_second, 2),
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None
        }

    def __str__(self) -> str:
        """Return a string representation of the stats."""
        return (f"Running Time: {self.formatted_running_time()}, "
                f"Processed Requests: {self.processed_requests}, "
                f"Filtered Requests: {self.filtered_requests}, "
                f"Requests/sec: {self.requests_per_second:.2f}")


class BruteForcer:
    """BruteForcer class for discovering hidden directories and files."""

    def __init__(self):
        """Initialize a BruteForcer instance."""
        self.config = None
        self.http_handler = None
        self.semaphore = None
        self.stats = BruteForceStats()
        self.results = []
        # State management for [SRS 27.3] stop confirmation
        self.state = {
            "running": False,
            "paused": False,
            "stopped": False,
            "completed": False,
            "stopping_confirmation_pending": False
        }
        self.wordlist = []
        self.progress = 0.0
        self._cancel_event = asyncio.Event()
        # For [SRS 27.2] and [SRS 28.2] table sorting
        self.sort_field = "id"
        self.sort_ascending = True

    def _create_config_from_dict(self, config: Dict[str, Any]) -> BruteForceConfig:
        """Create a BruteForceConfig object from a dictionary."""
        return BruteForceConfig(**config)

    def _export_results_to_csv(self, filename="brute_force_results.csv"):
        """Export the scan results to a CSV file with specific fields."""
        if not self.results:
            logger.info("No results to export to CSV.")
            return

        fieldnames = [
            "id",
            "url",
            "response code",
            "lines",
            "word",
            "chars",
            "payload",
            "time length"
        ]
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for result in self.results:
                    writer.writerow({
                        "id": result.id,
                        "url": result.url,
                        "response code": result.status_code,
                        "lines": result.line_count,
                        "word": result.word_count,
                        "chars": result.char_count,
                        "payload": result.payload,
                        "time length": round(result.response_time, 3),
                    })
            logger.info(f"Scan results exported to CSV: {filename}")
        except Exception as e:
            logger.error(f"Error exporting results to CSV: {e}")

    def _export_results_to_json(self, filename="brute_force_results.json"):
        """Export the scan results to a JSON file."""
        if not self.results:
            logger.info("No results to export to JSON.")
            return

        data = [result.to_dict() for result in self.results]
        try:
            with open(filename, 'w') as jsonfile:
                json.dump(data, jsonfile, indent=4)
            logger.info(f"Scan results exported to JSON: {filename}")
        except Exception as e:
            logger.error(f"Error exporting results to JSON: {e}")

    async def start_scan(self, config: Dict[str, Any], websocket=None) -> Dict[str, Any]:
        """
        Start a brute force scan with the given configuration.

        Args:
            config: Dictionary with scan configuration
            websocket: Optional websocket for real-time updates per [SRS 27.1]

        Returns:
            Dictionary with scan status and potential errors
        """
        # Create config object from dictionary
        self.config = self._create_config_from_dict(config)

        # Validate configuration
        valid_url, normalized_url, url_error = validate_url(self.config.target_url)
        if not valid_url:
            error_msg = f"Invalid target URL: {url_error}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "field": "target_url"
            }
        else:
            self.config.target_url = normalized_url  # Use normalized URL

        valid_wordlist, wordlist_error = validate_wordlist(self.config.wordlist_path)
        if not valid_wordlist:
            error_msg = f"Invalid wordlist: {wordlist_error}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "field": "wordlist_path"
            }

        # Setup
        async with HttpHandler(rate_limit=self.config.rate_limit) as self.http_handler:
            self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
            self.stats = BruteForceStats()
            self.results = []
            self._cancel_event.clear()

            # Reset state
            self.state = {
                "running": False,
                "paused": False,
                "stopped": False,
                "completed": False,
                "stopping_confirmation_pending": False
            }

            # Load wordlist
            self.wordlist = load_wordlist(self.config.wordlist_path)
            if not self.wordlist:
                error_msg = "Wordlist is empty"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "field": "wordlist_path" # Or perhaps a general error field
                }

            logger.info(f"Starting brute force scan against {self.config.target_url}")
            logger.info(f"Loaded {len(self.wordlist)} entries from wordlist")

            try:
                self.state["running"] = True

                # Create tasks for each word in the wordlist
                tasks = []
                for i, word in enumerate(self.wordlist):
                    task = self._process_word(i + 1, word, websocket)  # Assign id starting from 1
                    tasks.append(task)

                # Run tasks concurrently
                await asyncio.gather(*tasks)

                # Sort results by id
                self.results.sort(key=lambda result: result.id)

                # Mark as completed
                self.state["completed"] = True
                self.state["running"] = False

                return {
                    "status": "completed",
                    "results": [result.to_dict() for result in self.results],
                    "stats": self.stats.to_dict()
                }

            except asyncio.CancelledError:
                logger.info("Brute force scan was cancelled")
                self.state["running"] = False
                return {
                    "status": "cancelled",
                    "results": [result.to_dict() for result in self.results],
                    "stats": self.stats.to_dict()
                }
            except Exception as e:
                error_msg = f"Error during brute force scan: {str(e)}"
                logger.error(error_msg)
                self.state["running"] = False
                return {
                    "status": "error",
                    "message": error_msg
                }

    async def _process_word(self, id: int, word: str, websocket):
        """Process a single word from the wordlist."""
        if self.state["stopped"]:
            return

        url = build_url(self.config.target_url, os.path.join(self.config.top_level_directory, word))
        start_time = asyncio.get_event_loop().time()
        response = await self.http_handler.fetch(url, self.config.request_timeout)
        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time

        self.stats.processed_requests += 1
        self.stats.update_requests_per_second()
        self.progress = (self.stats.processed_requests / len(self.wordlist)) * 100 if self.wordlist else 0

        result = BruteForceResult(id=id, url=url, payload=word)

        if response:
            result.status_code = response.status_code
            result.response_time = response_time
            result.content_length = len(response.content)
            result.response_headers = dict(response.headers)
            result.word_count = len(re.findall(r'\b\w+\b', response.text, re.IGNORECASE))
            result.line_count = response.text.count('\n')
            result.char_count = len(response.text)

            if result.status_code >= 400 and result.status_code < 500:
                # Reset content-related fields for client error responses
                result.content_length = 0
                result.word_count = 0
                result.line_count = 0
                result.char_count = 0

            if apply_filters(result.to_dict(), self.config.hide_status, self.config.show_only_status, self.config.filter_by_content_length):
                self.results.append(result)
                logger.info(f"[{result.status_code}] {url} - Length: {result.content_length}")
                if websocket:
                    await websocket.send_json({"type": "result", "data": result.to_dict()})
            else:
                self.stats.filtered_requests += 1
        else:
            result.error = "Request failed or timed out"
            result.response_time = end_time - start_time
            self.results.append(result)  # Append even on error
            logger.warning(f"[Error] {url} - {result.error}")
            if websocket:
                await websocket.send_json({"type": "result", "data": result.to_dict()})

        if websocket:
            await websocket.send_json({"type": "stats", "data": self.stats.to_dict(), "progress": self.progress})

        # Introduce a delay based on the rate limit
        await asyncio.sleep(0) # Allow other tasks to run

    async def stop_scan(self, confirm: bool = False) -> Dict[str, str]:
        """Stop the brute force scan."""
        if self.state["running"]:
            if not confirm:
                self.state["stopping_confirmation_pending"] = True
                return {"status": "pending_confirmation", "message": "Confirmation required to stop scan."}
            else:
                self.state["running"] = False
                self.state["stopped"] = True
                self._cancel_event.set()
                self.stats.end_time = time.time()
                logger.info("Brute force scan stopped by user.")
                return {"status": "stopped", "message": "Scan stopped."}
        elif self.state["paused"]:
            self.state["running"] = False
            self.state["stopped"] = True
            self._cancel_event.set()
            self.stats.end_time = time.time()
            logger.info("Brute force scan stopped while paused.")
            return {"status": "stopped", "message": "Scan stopped."}
        else:
            return {"status": "idle", "message": "Scan is not running."}

    async def pause_scan(self) -> Dict[str, str]:
        """Pause the brute force scan."""
        if self.state["running"]:
            self.state["running"] = False
            self.state["paused"] = True
            logger.info("Brute force scan paused.")
            return {"status": "paused", "message": "Scan paused."}
        else:
            return {"status": "idle", "message": "Scan is not running."}

    async def resume_scan(self) -> Dict[str, str]:
        """Resume the brute force scan."""
        if self.state["paused"]:
            self.state["running"] = True
            self.state["paused"] = False
            logger.info("Brute force scan resumed.")

            return {"status": "running", "message": "Scan resumed."}
        else:
            return {"status": "idle", "message": "Scan is not paused."}

    def sort_results(self, field: str, ascending: bool) -> List[Dict[str, Any]]:
        """Sort the results based on the specified field."""
        if not self.results or not hasattr(self.results[0], field):
            return [result.to_dict() for result in self.results]  # Return as is if no results or invalid field

        self.sort_field = field
        self.sort_ascending = ascending
        self.results.sort(key=lambda x: getattr(x, field), reverse=not ascending)
        return [result.to_dict() for result in self.results]

    def filter_results(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply additional filters to the results."""
        filtered_results_list = []
        if filters:
            def matches_filter(result: BruteForceResult) -> bool:
                for key, value in filters.items():
                    if hasattr(result, key):
                        result_value = getattr(result, key)
                        if isinstance(value, list):
                            if result_value not in value:
                                return False
                        elif isinstance(value, str) and value.startswith(('>', '<', '=')):
                            op = value[0]
                            try:
                                filter_val = int(value[1:])
                                if op == '>' and not result_value > filter_val:
                                    return False
                                elif op == '<' and not result_value < filter_val:
                                    return False
                                elif op == '=' and not result_value == filter_val:
                                    return False
                            except ValueError:
                                # Ignore invalid filter values
                                pass
                return True

            filtered_results_list = [result.to_dict() for result in self.results if matches_filter(result)]
        else:
            filtered_results_list = [result.to_dict() for result in self.results]

        return filtered_results_list