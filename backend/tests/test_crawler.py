from crawler import Crawler  # Import the updated crawler


# Mock HTTP Handler for Testing
class MockHttpHandler:
    def __init__(self):
        self.pages = {
            "http://example.com": "<html><body><a href='http://example.com/page1'>Page 1</a><a href='http://example.com/page2'>Page 2</a></body></html>",
            "http://example.com/page1": "<html><body><a href='http://example.com/page3'>Page 3</a></body></html>",
            "http://example.com/page2": "<html><body><p>No more links here.</p></body></html>",
            "http://example.com/page3": "<html><body><p>End of crawl.</p></body></html>",
        }

    def fetch(self, url, timeout):
        if url in self.pages:
            class MockResponse:
                def __init__(self, text):
                    self.text = text

            return MockResponse(self.pages[url])
        return None


# Running the mock tester
if __name__ == "__main__":
    crawler = Crawler(output_file="mock_crawl_results.csv")  # Now this works!
    config = {"depth_limit": 2, "timeout": 1}  # Limit to 2 levels deep
    mock_handler = MockHttpHandler()

    print("Starting Mock Crawler Test:")
    crawler.start_crawling("http://example.com", config, mock_handler)
