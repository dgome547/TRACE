import os
import sys
import asyncio
import json
import time
from typing import Dict, Any, List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

# Import the fuzzer module
from app.fuzzer.fuzzer import FuzzerConfig, Fuzzer, FuzzResult

# Target URL - Replace 'FUZZ' with where you want to inject payloads
TARGET_URL = "http://testphp.vulnweb.com"

# Path to your wordlist file (one word per line)
WORDLIST_PATH = "test_wordlist.txt"

# HTTP Method (GET, POST, or PUT)
HTTP_METHOD = "GET"

# Request timeout in seconds
REQUEST_TIMEOUT = 5.0

# Status codes to hide (e.g., [404, 403] to hide not found and forbidden)
HIDE_STATUS_CODES = [404]

# Only show these status codes (empty list means show all except hidden)
SHOW_STATUS_CODES = []

# Filter by content length (e.g., [100, 200] to only show responses between 100-200 bytes)
FILTER_CONTENT_LENGTH = []

# Cookies to send with each request
COOKIES = {
    # "session": "your-session-cookie",
    # "auth": "your-auth-cookie"
}

# Additional parameters for the request
ADDITIONAL_PARAMETERS = {
    # "param1": "value1",
    # "param2": "value2"
}

# Where to save results
JSON_OUTPUT = "fuzzer_results.json"
CSV_OUTPUT = "fuzzer_results.csv"


class FuzzerProgressDisplay:
    """Display fuzzer progress and results in real-time."""
    
    def __init__(self):
        self.start_time = time.time()
        self.results_count = 0
    
    def display_header(self):
        """Display the header for results."""
        print("\n{:<5} {:<8} {:<6} {:<5} {:<5} {:<10} {:<7} {:<5}".format(
            "ID", "Response", "Lines", "Words", "Chars", "Payload", "Length", "Error"
        ))
        print("-" * 70)
    
    def display_result(self, result: Dict[str, Any]):
        """Display a single result."""
        print("{:<5} {:<8} {:<6} {:<5} {:<5} {:<10} {:<7.3f} {:<5}".format(
            result['id'],
            result['status_code'],
            result['lines'],
            result['words'],
            result['chars'],
            result['payload'][:10] + '...' if len(result['payload']) > 10 else result['payload'],
            result['response_time'],
            result['error']
        ))
        self.results_count += 1
    
    def display_metrics(self, metrics: Dict[str, Any]):
        """Display metrics."""
        print("\n--- Fuzzing Metrics ---")
        print(f"Running Time: {metrics['running_time']}")
        print(f"Processed Requests: {metrics['processed_requests']}")
        print(f"Filtered Requests: {metrics['filtered_requests']}")
        print(f"Requests/sec: {metrics['requests_per_sec']}")
        
        if self.results_count == 0:
            print("\nNo results matched your filter criteria. Try adjusting your filters.")
    
    def display_progress(self, current: int, total: int):
        """Display progress bar."""
        progress = min(100, int(current / total * 100))
        bar_length = 40
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        elapsed = time.time() - self.start_time
        
        print(f"\rProgress: |{bar}| {progress}% Complete - {current}/{total} - {elapsed:.1f}s", end='')


async def monitor_fuzzing_progress(fuzzer: Fuzzer, total_payloads: int, display: FuzzerProgressDisplay):
    """Monitor and display fuzzing progress."""
    while fuzzer.state["running"]:
        display.display_progress(fuzzer.processed_payloads, total_payloads)
        await asyncio.sleep(0.5)
    
    # Final progress update
    display.display_progress(fuzzer.processed_payloads, total_payloads)
    print("\n")


async def process_result_callback(fuzzer, display, result):
    """Process and display each result as it comes in."""
    display.display_result(result.to_dict())


async def run_fuzzer_test():
    """Run the fuzzer with the configured parameters."""
    # Create fuzzer configuration
    config = FuzzerConfig(
        target_url=TARGET_URL,
        wordlist_path=WORDLIST_PATH,
        http_method=HTTP_METHOD,
        cookies=COOKIES,
        hide_status_codes=set(HIDE_STATUS_CODES),
        show_status_codes=set(SHOW_STATUS_CODES) if SHOW_STATUS_CODES else None,
        filter_content_length=FILTER_CONTENT_LENGTH,
        additional_parameters=ADDITIONAL_PARAMETERS,
        request_timeout=REQUEST_TIMEOUT
    )
    
    # Validate configuration
    validation_errors = config.validate()
    if validation_errors:
        print("Configuration errors:")
        for field, error in validation_errors.items():
            print(f"  {field}: {error}")
        return
    
    # Create fuzzer
    fuzzer = Fuzzer()
    
    # Create display
    display = FuzzerProgressDisplay()
    
    # Count payloads in wordlist
    try:
        with open(WORDLIST_PATH, 'r') as f:
            total_payloads = sum(1 for line in f if line.strip())
    except Exception as e:
        print(f"Error reading wordlist: {e}")
        return
    
    # Start monitor task
    print(f"Starting fuzzer with target URL: {TARGET_URL}")
    print(f"Using wordlist: {WORDLIST_PATH} ({total_payloads} payloads)")
    print(f"HTTP method: {HTTP_METHOD}, Timeout: {REQUEST_TIMEOUT}s")
    
    if HIDE_STATUS_CODES:
        print(f"Hiding status codes: {HIDE_STATUS_CODES}")
    if SHOW_STATUS_CODES:
        print(f"Only showing status codes: {SHOW_STATUS_CODES}")
    if FILTER_CONTENT_LENGTH:
        print(f"Filtering by content length: {FILTER_CONTENT_LENGTH}")
    
    # Display header for results
    display.display_header()
    
    # Create a modified fuzzer class with result callback
    original_should_display = fuzzer.should_display_result
    
    async def process_results():
        # Create a task to monitor progress
        monitor_task = asyncio.create_task(
            monitor_fuzzing_progress(fuzzer, total_payloads, display)
        )
        
        # Override the should_display_result method to add callback
        def new_should_display(result, config):
            should_display = original_should_display(result, config)
            if should_display:
                asyncio.create_task(process_result_callback(fuzzer, display, result))
            return should_display
            
        fuzzer.should_display_result = new_should_display
        
        # Start fuzzing
        results = await fuzzer.start_fuzzing(config)
        
        # Wait for monitor to finish
        await monitor_task
        
        return results
    
    # Run fuzzing and get results
    results = await process_results()
    
    # Display metrics
    display.display_metrics(fuzzer.metrics.get_metrics())
    
    # Export results
    if fuzzer.results:
        json_file = fuzzer.export_to_json(JSON_OUTPUT)
        csv_file = fuzzer.export_to_csv(CSV_OUTPUT)
        
        print(f"\nResults exported to:")
        print(f"  - JSON: {json_file}")
        print(f"  - CSV: {csv_file}")
    else:
        print("\nNo results to export.")
    



async def main():
    """Run the fuzzer."""
    try:
        await run_fuzzer_test()
    except KeyboardInterrupt:
        print("\nFuzzing interrupted by user")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())