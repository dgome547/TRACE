import asyncio
import json
import sys
import os
from datetime import datetime

# Make sure the modules are in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crawler.utils import setup_logging, validate_config
from app.crawler.crawler import run_crawler, Crawler
from app.crawler.httphandler import HttpHandler

def get_test_output_path(filename):
    """Helper to get output path in the tests directory."""
    import os
    return os.path.join(os.path.dirname(__file__), filename)


class MockWebSocket:
    """Mock websocket for testing"""

    def __init__(self):
        self.messages = []

    async def send_json(self, data):
        self.messages.append(data)
        progress = data.get('progress', 0)
        if 'current_result' in data:
            url = data['current_result'].get('url', '')
            print(f"Progress: {progress}% - Processing: {url}")

    def get_messages(self):
        return self.messages


async def test_crawler_config():
    """Test crawler configuration validation"""
    print("\n=== Testing Configuration Validation ===")

    # Valid configuration
    valid_config = {
        "targetUrl": "https://example.com",
        "crawlDepth": 5,
        "limitPages": 10,
        "requestDelay": 1.0,
        "userAgent": "TestAgent/1.0",
        "proxy": "http://127.0.0.1:8080",
        "outputFile": get_test_output_path(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    }

    is_valid, errors = validate_config(valid_config)
    print(f"Valid config test passed: {is_valid}")
    assert is_valid, f"Expected valid config to pass, but got errors: {errors}"

    # Invalid configuration (missing target URL)
    invalid_config = {
        "crawlDepth": 2,
        "limitPages": 10,
    }

    is_valid, errors = validate_config(invalid_config)
    print(f"Invalid config test (missing URL): {not is_valid}")
    print(f"Error messages: {errors}")

    # Invalid configuration (negative value)
    invalid_config2 = {
        "targetUrl": "https://example.com",
        "crawlDepth": -1,
    }

    is_valid, errors = validate_config(invalid_config2)
    print(f"Invalid config test (negative value): {not is_valid}")
    print(f"Error messages: {errors}")


async def test_crawler_run():
    """Test running the crawler with example website"""
    print("\n=== Testing Crawler Run ===")

    # Configuration for a small test with userAgent and proxy
    config = {
        "targetUrl": "https://example.com",
        "crawlDepth": 2,
        "limitPages": 10,
        "requestDelay": 1.0,
        "userAgent": "TestAgent/1.0",
        "proxy": "http://127.0.0.1:8080",
        "outputFile": get_test_output_path(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    }

    # Create a mock websocket
    mock_socket = MockWebSocket()

    # Run the crawler
    print(f"Starting crawler test with config: {json.dumps(config, indent=2)}")
    result = await run_crawler(config, mock_socket)

    # Check results
    print(f"Crawler completed with status: {result['status']}")
    if result['status'] == 'success':
        print(f"Pages processed: {result['stats']['processed_requests']}")
        print(f"Results exported to: {config['outputFile']}")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")

    # Count number of updates sent via websocket
    print(f"WebSocket received {len(mock_socket.messages)} updates")


async def test_crawler_pause_resume():
    """Testing pausing and resuming the crawler"""
    print("\n=== Testing Crawler Pause/Resume ===")

    crawler = Crawler()
    crawler.state["running"] = True

    # Test pause
    result = await crawler.pause_crawler()
    print(f"Pause result: {result['status']}")

    # Test resume
    result = await crawler.resume_crawler()
    print(f"Resume result: {result['status']}")

    # Test stop without confirmation
    result = await crawler.stop_crawler(confirm=False)
    print(f"Stop without confirmation: {result['status']}")

    # Test stop with confirmation
    result = await crawler.stop_crawler(confirm=True)
    print(f"Stop with confirmation: {result['status']}")


async def main():
    """Run all tests"""
    setup_logging(log_file=get_test_output_path("test_crawler.log"))

    print("=== Starting Crawler Tests ===")

    # Run configuration tests
    await test_crawler_config()

    # Run crawler tests
    await test_crawler_run()

    # Run crawler control tests
    await test_crawler_pause_resume()

    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    asyncio.run(main())