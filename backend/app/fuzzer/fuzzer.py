import asyncio
import time
import logging
import json
import csv
from fastapi import WebSocket
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime
from app.fuzzer.httphandler import HttpHandler
from app.crawler.utils import valid_url


@dataclass
class FuzzerConfig:
    """
    Configuration class for the fuzzer that holds all user-defined parameters
    from the Parameter Fuzzing Setup page.
    [SRS 22] Configuration parameters for parameter fuzzing
    """
    target_url: str  # [SRS 22] Target URL input
    wordlist_path: str  # [SRS 22] Word List input
    http_method: str = "GET"  # [SRS 22] GET, PUT, POST radio buttons
    cookies: Dict[str, str] = None  # [SRS 22] Cookies input
    hide_status_codes: Set[int] = None  # [SRS 22] Hide Status input
    show_status_codes: Set[int] = None  # [SRS 22] Show Status input
    filter_content_length: List[int] = None  # [SRS 22] Filter by Content Length input
    additional_parameters: Dict[str, Any] = None  # [SRS 22] Additional Parameters input
    request_timeout: float = 5.0
    
    def __post_init__(self):
        """Initialize default values for None fields"""
        if self.cookies is None:
            self.cookies = {}
        if self.hide_status_codes is None:
            self.hide_status_codes = set()
        if self.show_status_codes is None:
            self.show_status_codes = set()
        if self.filter_content_length is None:
            self.filter_content_length = []
        if self.additional_parameters is None:
            self.additional_parameters = {}
    
    def validate(self) -> Dict[str, str]:
        """
        Validate the configuration parameters
        [SRS 22.1] Validate fields for correctness and completeness
        [SRS 22.4] Highlight errors in user input
        
        Returns:
            Dictionary with field names as keys and error messages as values
        """
        errors = {}
        
        # Validate target URL
        if not self.target_url:
            errors["target_url"] = "Target URL is required"
        elif not valid_url(self.target_url):
            errors["target_url"] = "Invalid URL format"   
        # Validate wordlist
        if not self.wordlist_path:
            errors["wordlist_path"] = "Word list is required"
            
        # Validate HTTP method
        if self.http_method not in ["GET", "POST", "PUT"]:
            errors["http_method"] = "Invalid HTTP method"
            
        # Validate content length filter format
        if self.filter_content_length:
            try:
                # Verify if content length filters are valid
                # Could be a range [min, max] or single value
                if len(self.filter_content_length) > 2:
                    errors["filter_content_length"] = "Content length filter must be a single value or range"
                elif len(self.filter_content_length) == 2 and self.filter_content_length[0] > self.filter_content_length[1]:
                    errors["filter_content_length"] = "Invalid range: min value must be less than max value"
            except (ValueError, TypeError):
                errors["filter_content_length"] = "Invalid content length filter format"
                
        return errors


@dataclass
class FuzzResult:
    """
    Represents the result of a single fuzzing request
    [SRS 23] Display real-time information and results
    [SRS 24] Present finalized results
    """
    id: int  # [SRS 23, 24] ID column
    url: str
    payload: str  # [SRS 23, 24] Payload column
    status_code: int  # [SRS 23, 24] Response column
    content_length: int  # [SRS 23, 24] Length column
    lines: int  # [SRS 23, 24] Lines column
    words: int  # [SRS 23, 24] Word column
    chars: int  # [SRS 23, 24] Chars column
    response_time: float
    error: str = "false"  # [SRS 23, 24] Error column
    timestamp: str = None
    
    def __post_init__(self):
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization"""
        return {
            'id': self.id,
            'url': self.url,
            'payload': self.payload,
            'status_code': self.status_code,
            'content_length': self.content_length,
            'lines': self.lines,
            'words': self.words,
            'chars': self.chars,
            'response_time': self.response_time,
            'error': self.error,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_response(cls, id: int, url: str, payload: str, response, response_time: float) -> 'FuzzResult':
        """
        Create a FuzzResult from an HTTP response
        
        Args:
            id: Request ID
            url: The URL that was fuzzed
            payload: The payload that was used
            response: The HTTP response object
            response_time: Time taken for the request
            
        Returns:
            FuzzResult object with parsed response data
        """
        if response is None:
            return cls.error_result(id, url, payload, "No response received")
            
        status_code = getattr(response, 'status_code', 0)
        
        # For 404 responses, we want to show them as errors with 0 content length
        if status_code == 404:
            return cls(
                id=id,
                url=url,
                payload=payload,
                status_code=status_code,
                content_length=0,
                lines=0,
                words=0,
                chars=0,
                response_time=response_time,
                error="true"
            )
            
        content = getattr(response, 'text', '')
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Count lines
        lines = len(content.splitlines())
        
        # Count words (including special characters)
        words = len(re.findall(r'[\w\-\']+|[\S]+', content))
        
        # Count characters (visible characters only)
        # Remove whitespace and count remaining characters
        chars = len(''.join(content.split()))
        
        return cls(
            id=id,
            url=url,
            payload=payload,
            status_code=status_code,
            content_length=len(getattr(response, 'content', b'')),
            lines=lines,
            words=words,
            chars=chars,
            response_time=response_time,
            error="false"
        )
    
    @classmethod
    def error_result(cls, id: int, url: str, payload: str, error_msg: str) -> 'FuzzResult':
        """Create an error result when the request fails"""
        return cls(
            id=id,
            url=url,
            payload=payload,
            status_code=0,
            content_length=0,
            lines=0,
            words=0,
            chars=0,
            response_time=0,
            error="true"
        )


class FuzzerMetrics:
    """
    Tracks and calculates metrics for the fuzzing process
    [SRS 23] Display real-time metrics
    [SRS 24] Display summary metrics
    """
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.total_requests: int = 0
        self.filtered_requests: int = 0
        self.error_requests: int = 0
        self.request_times: List[float] = []
        
    def start(self):
        """Start tracking metrics"""
        self.start_time = datetime.now()
        
    def stop(self):
        """Stop tracking metrics"""
        self.end_time = datetime.now()
        
    def add_request(self, response_time: float, is_filtered: bool = False, is_error: bool = False):
        """Record a request and its metrics"""
        self.total_requests += 1
        self.request_times.append(response_time)
        
        if is_filtered:
            self.filtered_requests += 1
        elif is_error:
            self.error_requests += 1
            
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics
        [SRS 23] Four key metrics display
        [SRS 24] Four key metrics display
        
        Returns:
            Dictionary with current metrics
        """
        now = datetime.now()
        running_time = (now - self.start_time).total_seconds() if self.start_time else 0
        
        if self.end_time:
            running_time = (self.end_time - self.start_time).total_seconds()
            
        # Calculate requests per second
        requests_per_sec = self.total_requests / running_time if running_time > 0 else 0
        
        return {
            "running_time": f"{int(running_time // 60)}m {int(running_time % 60)}s",  # [SRS 23, 24] Running Time
            "processed_requests": self.total_requests,  # [SRS 23, 24] Processed Requests
            "filtered_requests": self.filtered_requests,  # [SRS 23, 24] Filtered Requests
            "requests_per_sec": round(requests_per_sec, 2)  # [SRS 23, 24] Requests/sec
        }


class Fuzzer:
    """
    Main fuzzer class that orchestrates the fuzzing process based on user configuration
    """
    def __init__(self):
        self.results: List[FuzzResult] = []
        self.state = {"running": False, "paused": False, "stopped": False}
        self.metrics = FuzzerMetrics()
        self.http_handler = HttpHandler()
        self.total_payloads = 0
        self.processed_payloads = 0

    async def start_fuzzing(self, config: FuzzerConfig, websocket: Optional[WebSocket] = None) -> Dict[str, Any]:
        """
        Start the fuzzing process with the provided configuration
        [SRS 23] Running the parameter fuzzing process
        
        Args:
            config: FuzzerConfig with all parameters
            websocket: Optional WebSocket for real-time updates
            
        Returns:
            Dictionary with fuzzing results and metrics
        """
        # Validate configuration before starting
        # [SRS 22.1] Validate fields for correctness
        validation_errors = config.validate()
        if validation_errors:
            return {"status": "error", "errors": validation_errors}
            
        self.state["running"] = True
        self.metrics.start()
        self.results = []
        self.processed_payloads = 0
        
        # Load payloads from wordlist
        payloads = self.load_payloads(config.wordlist_path)
        if not payloads:
            return {"status": "error", "message": "Failed to load payloads or wordlist is empty"}
            
        task_id = 1
        
        # Begin fuzzing process
        for payload in payloads:
            if self.state["stopped"]:
                break
                
            while self.state["paused"]:
                await asyncio.sleep(1)
                
            # If URL doesn't contain FUZZ, append it to the path
            if "FUZZ" not in config.target_url:
                # Ensure URL ends with a slash if it doesn't have one
                base_url = config.target_url.rstrip('/') + '/'
                fuzzed_url = base_url + "FUZZ"
            else:
                fuzzed_url = config.target_url
            
            # Replace FUZZ placeholder with payload
            fuzzed_url = fuzzed_url.replace("FUZZ", payload)
            
            # Make the request
            start = time.time()
            try:
                response = await self.http_handler.fetch(
                    url=fuzzed_url,
                    method=config.http_method,  # [SRS 22] Support for GET, PUT, POST
                    timeout=config.request_timeout,
                    cookies=config.cookies,  # [SRS 22] Cookies input
                    additional_params=config.additional_parameters  # [SRS 22] Additional Parameters
                )
                end = time.time()
                
                # Always create a result from the response
                result = FuzzResult.from_response(
                    id=task_id,
                    url=fuzzed_url,
                    payload=payload,
                    response=response,
                    response_time=end - start
                )
                    
                # Check if result should be displayed based on filters
                is_filtered = not self.should_display_result(result, config)
                
                # Update metrics based on result
                self.metrics.add_request(
                    response_time=result.response_time,
                    is_filtered=is_filtered,
                    is_error=bool(result.error)
                )
                
                # Add to results and send update if result passes filters
                if not is_filtered:
                    self.results.append(result)
                    
                    # Send real-time update via WebSocket if available
                    # [SRS 23.1] Update progress bar dynamically
                    if websocket:
                        progress = self.get_progress()
                        await websocket.send_json({
                            "type": "fuzz_result",
                            "data": result.to_dict(),
                            "progress": progress,
                            "metrics": self.metrics.get_metrics()
                        })
                        
            except Exception as e:
                logging.error(f"Error processing payload {payload}: {str(e)}")
                
            task_id += 1
            self.processed_payloads += 1
            
        # Fuzzing complete
        self.metrics.stop()
        self.state["running"] = False
        
        # Return final results
        return {
            "status": "complete",
            "results": [r.to_dict() for r in self.results],
            "metrics": self.metrics.get_metrics()
        }

    async def stop_fuzzing(self) -> Dict[str, str]:
        """
        Stop the fuzzing process
        [SRS 23.3] Display confirmation prompt before stopping
        
        Returns:
            Status dictionary
        """
        self.state["stopped"] = True
        self.metrics.stop()
        return {"status": "stopped"}

    async def pause_fuzzing(self) -> Dict[str, str]:
        """
        Pause the fuzzing process
        
        Returns:
            Status dictionary
        """
        self.state["paused"] = True
        return {"status": "paused"}

    async def resume_fuzzing(self) -> Dict[str, Union[str, Dict]]:
        """
        Resume the fuzzing process
        
        Returns:
            Status dictionary
        """
        if self.state["paused"]:
            self.state["paused"] = False
            return {"status": "resumed"}
        return {"status": "error", "message": "Fuzzer is not paused."}

    def export_to_json(self, filename="fuzz_results.json") -> str:
        """
        Export results to JSON file
        [SRS 24] Present finalized results
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the exported file
        """
        with open(filename, 'w') as f:
            json.dump({
                "results": [{
                    'id': r.id,
                    'status_code': r.status_code,
                    'lines': r.lines,
                    'words': r.words,
                    'chars': r.chars,
                    'payload': r.payload,
                    'response_time': r.response_time,
                    'error': r.error
                } for r in self.results],
                "metrics": self.metrics.get_metrics(),
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        return filename

    def export_to_csv(self, filename="fuzz_results.csv") -> str:
        """
        Export results to CSV file
        [SRS 24] Present finalized results
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the exported file
        """
        if not self.results:
            return None
            
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'status_code', 'lines', 'words', 'chars', 'payload', 'content_length', 'error'
            ])
            writer.writeheader()
            for result in self.results:
                # Create a dictionary with only the required fields
                result_dict = {
                    'id': result.id,
                    'status_code': result.status_code,
                    'lines': result.lines,
                    'words': result.words,
                    'chars': result.chars,
                    'payload': result.payload,
                    'content_length': result.content_length,
                    'error': result.error
                }
                writer.writerow(result_dict)
        return filename



    def load_payloads(self, path: str) -> List[str]:
        """
        Load payloads from a wordlist file
        [SRS 22] Word List input
        
        Args:
            path: Path to the wordlist file
            
        Returns:
            List of payloads
        """
        try:
            with open(path, 'r') as f:
                payloads = [line.strip() for line in f if line.strip()]
                self.total_payloads = len(payloads)
                return payloads
        except Exception as e:
            logging.error(f"Failed to load payloads: {e}")
            return []
            
    def should_display_result(self, result: FuzzResult, config: FuzzerConfig) -> bool:
        """
        Determine if a result should be displayed based on filtering criteria
        [SRS 22] Hide Status, Show Status, Filter by Content Length
        
        Args:
            result: The FuzzResult to check
            config: FuzzerConfig with filtering criteria
            
        Returns:
            True if the result should be displayed, False otherwise
        """
        # If no filters are set, show all results
        if not config.hide_status_codes and not config.show_status_codes and not config.filter_content_length:
            return True
            
        # Check if status code should be hidden
        if config.hide_status_codes and result.status_code in config.hide_status_codes:
            return False
            
        # Check if only specific status codes should be shown
        if config.show_status_codes and result.status_code not in config.show_status_codes:
            return False
            
        # Check content length filters
        if config.filter_content_length:
            if len(config.filter_content_length) == 1:
                # Single value means "equal to"
                if result.content_length != config.filter_content_length[0]:
                    return False
            elif len(config.filter_content_length) == 2:
                # Range values mean "between min and max"
                min_len, max_len = config.filter_content_length
                if not (min_len <= result.content_length <= max_len):
                    return False
                    
        return True
        
    def get_progress(self) -> float:
        """
        Calculate the current progress percentage
        [SRS 23.1] Update progress bar dynamically
        
        Returns:
            Progress percentage (0-100)
        """
        if self.total_payloads == 0:
            return 0
        return (self.processed_payloads / self.total_payloads) * 100

    def load_payloads(self, path: str) -> List[str]:
        """
        Load payloads from a wordlist file
        [SRS 22] Word List input
        
        Args:
            path: Path to the wordlist file
            
        Returns:
            List of payloads
        """
        try:
            with open(path, 'r') as f:
                payloads = [line.strip() for line in f if line.strip()]
                self.total_payloads = len(payloads)
                return payloads
        except Exception as e:
            logging.error(f"Failed to load payloads: {e}")
            return []
            
    def should_display_result(self, result: FuzzResult, config: FuzzerConfig) -> bool:
        """
        Determine if a result should be displayed based on filtering criteria
        [SRS 22] Hide Status, Show Status, Filter by Content Length
        
        Args:
            result: The FuzzResult to check
            config: FuzzerConfig with filtering criteria
            
        Returns:
            True if the result should be displayed, False otherwise
        """
        # If no filters are set, show all results
        if not config.hide_status_codes and not config.show_status_codes and not config.filter_content_length:
            return True
            
        # Check if status code should be hidden
        if config.hide_status_codes and result.status_code in config.hide_status_codes:
            return False
            
        # Check if only specific status codes should be shown
        if config.show_status_codes and result.status_code not in config.show_status_codes:
            return False
            
        # Check content length filters
        if config.filter_content_length:
            if len(config.filter_content_length) == 1:
                # Single value means "equal to"
                if result.content_length != config.filter_content_length[0]:
                    return False
            elif len(config.filter_content_length) == 2:
                # Range values mean "between min and max"
                min_len, max_len = config.filter_content_length
                if not (min_len <= result.content_length <= max_len):
                    return False
                    
        return True
        
    def get_progress(self) -> float:
        """
        Calculate the current progress percentage
        [SRS 23.1] Update progress bar dynamically
        
        Returns:
            Progress percentage (0-100)
        """
        if self.total_payloads == 0:
            return 0
        return (self.processed_payloads / self.total_payloads) * 100