import os
import sys
import asyncio
import json
import pytest
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

# Import required modules
from app.bruteforcer.bruteforcer import BruteForcer
from app.bruteforcer.utils import load_wordlist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_websocket')

class WebsocketMessage:
    """Class to represent WebSocket messages in a uniform format."""
    
    @staticmethod
    def create_result_message(result: Dict[str, Any]) -> Dict[str, Any]:
        """Format a result message for terminal display."""
        status = result.get("status_code", 0)
        url = result.get("url", "unknown")
        content_length = result.get("content_length", 0)
        response_time = result.get("response_time", 0)
        payload = result.get("payload", "")
        error = result.get("error", None)
        
        # Determine message type and color based on status
        if status == 0 or error:
            msg_type = "error"
            color = "red"
            prefix = "ERROR"
        elif 200 <= status < 300:
            msg_type = "success"
            color = "green"
            prefix = str(status)
        elif 300 <= status < 400:
            msg_type = "redirect"
            color = "blue"
            prefix = str(status)
        elif 400 <= status < 500:
            msg_type = "client_error"
            color = "yellow"
            prefix = str(status)
        else:
            msg_type = "server_error"
            color = "red"
            prefix = str(status)
            
        # Create the formatted message
        formatted_message = {
            "type": "terminal_output",
            "message_type": msg_type,
            "content": {
                "prefix": prefix,
                "url": url,
                "payload": payload,
                "content_length": content_length,
                "response_time": round(response_time, 3),
                "error": error
            },
            "display": {
                "color": color,
                "text": f"[{prefix}] {url} - Length: {content_length}, Time: {response_time:.3f}s" + 
                       (f" - Error: {error}" if error else "")
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return formatted_message
    
    @staticmethod
    def create_stats_message(stats: Dict[str, Any], progress: float) -> Dict[str, Any]:
        """Format a stats message for terminal display."""
        # Create the formatted message
        formatted_message = {
            "type": "terminal_output",
            "message_type": "stats",
            "content": {
                "progress": progress,
                "processed_requests": stats.get("processed_requests", 0),
                "filtered_requests": stats.get("filtered_requests", 0),
                "requests_per_second": stats.get("requests_per_second", 0),
                "running_time": stats.get("running_time", "00:00:00"),
                "raw_running_time": stats.get("raw_running_time", 0)
            },
            "display": {
                "color": "gray",
                "text": (
                    f"Progress: {progress:.1f}% | "
                    f"Processed: {stats.get('processed_requests', 0)} | "
                    f"Time: {stats.get('running_time', '00:00:00')} | "
                    f"Req/sec: {stats.get('requests_per_second', 0):.2f}"
                ),
                "progress_bar": {
                    "value": progress,
                    "max": 100
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return formatted_message


class FrontendWebsocket:
    """
    WebSocket class for frontend integration.
    
    This class can be used two ways:
    1. Standalone testing: It will print to console for testing
    2. Frontend integration: Pass in a callback function that will receive messages
    """
    
    def __init__(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize the websocket.
        
        Args:
            callback: Optional function to call with each message.
                      If None, messages are printed to console.
        """
        self.sent_messages = []
        self.connected = True
        self.callback = callback
        
    async def send_json(self, data: Dict[str, Any]):
        """Process a JSON message."""
        self.sent_messages.append(data)
        
        # Format the message based on its type
        formatted_message = None
        
        if data.get("type") == "result":
            formatted_message = WebsocketMessage.create_result_message(data.get("data", {}))
        elif data.get("type") == "stats":
            formatted_message = WebsocketMessage.create_stats_message(
                data.get("data", {}), 
                data.get("progress", 0)
            )
        else:
            # Just pass through other message types
            formatted_message = {
                "type": "terminal_output",
                "message_type": "other",
                "content": data,
                "display": {
                    "color": "white",
                    "text": str(data)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Handle the formatted message
        if self.callback:
            # Send to the callback function (e.g., a frontend handler)
            self.callback(formatted_message)
        else:
            # Default behavior: print to console
            self._print_to_console(formatted_message)
    
    def _print_to_console(self, message: Dict[str, Any]):
        """Print the message to console for testing purposes."""
        # Map colors to ANSI codes for terminal display
        color_map = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "gray": "\033[90m",
            "reset": "\033[0m"
        }
        
        # Get color and text from the message
        color = message.get("display", {}).get("color", "white")
        text = message.get("display", {}).get("text", "")
        color_code = color_map.get(color, color_map["white"])
        reset = color_map["reset"]
        
        # Handle progress bar special case
        if message.get("message_type") == "stats":
            progress = message.get("content", {}).get("progress", 0)
            
            # Create a simple progress bar
            bar_length = 30
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            # Print with progress bar and carriage return to update in place
            print(f"\r{color_code}[STATS] [{bar}] {text}{reset}", end='', flush=True)
            
            # Add a newline if progress is complete
            if progress >= 100:
                print()
        else:
            # Print regular message with a newline
            print(f"{color_code}{text}{reset}")


@pytest.mark.asyncio
async def test_bruteforcer_with_frontend():
    """Test the BruteForcer with websocket for frontend terminal integration."""
    
    # Create a BruteForcer instance
    brute_forcer = BruteForcer()
    
    # Define test parameters
    target_url = "http://testphp.vulnweb.com/"
    wordlist_file = "test_wordlist.txt"
    
    # Create a test wordlist if it doesn't exist
    if not os.path.exists(wordlist_file):
        with open(wordlist_file, "w") as f:
            f.write("admin\n")
            f.write("login\n")
            f.write("test\n")
            f.write("images\n")
            f.write("css\n")
            f.write("js\n")
            f.write("index.php\n")
            f.write("robots.txt\n")
            f.write("sitemap.xml\n")
            f.write("search\n")
    
    # Confirm wordlist loaded successfully
    wordlist = load_wordlist(wordlist_file)
    assert len(wordlist) > 0, "Wordlist failed to load or is empty."
    
    # This would be replaced with a real frontend callback in actual use
    def frontend_message_handler(message):
        # In a real application, this would send to a frontend
        # For testing, we just print the JSON
        if message.get("message_type") != "stats":  # Don't print every stats update
            print(f"Frontend would receive: {json.dumps(message, indent=2)}")
    
    # Create a frontend websocket (passing None means it will print to console instead)
    # For integration with a real frontend, you'd pass frontend_message_handler
    frontend_websocket = FrontendWebsocket(None)  # Use None for console output
    
    # Define configuration for the bruteforcer
    config = {
        "target_url": target_url,
        "wordlist_path": wordlist_file,
        "max_concurrent_requests": 3,
        "request_timeout": 5.0,
        "rate_limit": 0.5,
        "hide_status": [],
        "show_only_status": [],
        "output_format": "csv"
    }
    
    # Print test header
    print("\n" + "="*80)
    print(f"Starting Bruteforcer Frontend WebSocket Test against {target_url}")
    print(f"Using wordlist: {wordlist_file} with {len(wordlist)} entries")
    print("="*80 + "\n")
    
    # Start the scan with the frontend websocket
    start_time = datetime.now()
    print(f"[INFO] Test started at {start_time.strftime('%H:%M:%S')}")
    
    # Run the bruteforcer with our frontend websocket
    scan_output = await brute_forcer.start_scan(config, frontend_websocket)
    
    # Display summary
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print("\n" + "="*80)
    print(f"Test completed at {end_time.strftime('%H:%M:%S')}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Total messages sent via WebSocket: {len(frontend_websocket.sent_messages)}")
    print(f"Results count: {len(scan_output.get('results', []))}")
    print("="*80)
    
    # Export results to CSV for verification
    output_folder = "results"
    os.makedirs(output_folder, exist_ok=True)
    output_csv = os.path.join(output_folder, "frontend_test_results.csv")
    
    if scan_output.get("results"):
        brute_forcer._export_results_to_csv(output_csv)
        print(f"\n[INFO] Results exported to {output_csv}")
    else:
        print("\n[INFO] No results to export")
    
    # Basic assertions to ensure the test worked
    assert "status" in scan_output, "Missing 'status' in scan output"
    assert "results" in scan_output, "Missing 'results' in scan output"
    assert "stats" in scan_output, "Missing 'stats' in scan output"
    assert len(frontend_websocket.sent_messages) > 0, "No messages were sent via WebSocket"
    
    print("\n[INFO] Test completed successfully!")
    

# Example of how to integrate with a frontend
def example_frontend_integration():
    """
    This function demonstrates how to integrate the test with a real frontend.
    Not meant to be run directly - just an example.
    """
    # For a real frontend integration, you'd create a message handler
    def send_to_frontend(message):
        # This would send the formatted message to your frontend
        # For example, using a WebSocket connection to the frontend
        print(f"Sending to frontend: {json.dumps(message)}")
        
        # In a real app, you might do something like:
        # web_socket_connection.send(json.dumps(message))
    
    # Then create the FrontendWebsocket with your handler
    frontend_websocket = FrontendWebsocket(send_to_frontend)
    
    # This websocket would then be passed to the bruteforcer.start_scan method


if __name__ == "__main__":
    # Run the test directly if executed as a script
    asyncio.run(test_bruteforcer_with_frontend())