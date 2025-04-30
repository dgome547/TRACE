import asyncio
import requests
import logging
from typing import Optional, Dict, Any

class HttpHandler:
    """
    Enhanced HTTP handler to support SRS requirements including multiple HTTP methods,
    cookies handling, and filtering capabilities.
    """
    def __init__(self):
        # Removed rate limit, request time tracking and user agent as per requirements
        self.proxy = None
        
    async def fetch(self, 
                   url: str, 
                   method: str = "GET",  # [SRS 22] Support for GET, PUT, POST methods
                   timeout: float = 5.0,
                   cookies: Dict[str, str] = None,  # [SRS 22] Support for cookies
                   additional_params: Dict[str, Any] = None,  # [SRS 22] Support for additional parameters
                   headers: Dict[str, str] = None) -> Optional[requests.Response]:
        """
        Send HTTP request based on configured parameters
        
        Args:
            url: Target URL for fuzzing
            method: HTTP method (GET, PUT, POST) [SRS 22]
            timeout: Request timeout in seconds
            cookies: Cookie values to send with request [SRS 22]
            additional_params: Additional parameters for the request [SRS 22]
            headers: Custom headers for the request
            
        Returns:
            Response object or None if request failed
        """
        try:
            # Default headers if none provided
            if not headers:
                headers = {
                    'User-Agent': 'TRACE-Fuzzer/1.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
                
            # Set up proxy if configured
            proxies = {
                'http': self.proxy,
                'https': self.proxy
            } if self.proxy else None
            
            # Create request kwargs based on method and params
            kwargs = {
                'timeout': timeout, 
                'headers': headers, 
                'cookies': cookies,
                'proxies': proxies
            }
            
            # Handle request data based on method
            if method == "GET":
                # For GET requests, params go in the URL query string
                kwargs['params'] = additional_params
                response = requests.get(url, **kwargs)
            elif method == "POST":
                # [SRS 22] Support for POST method
                # For POST requests, params go in the request body
                kwargs['data'] = additional_params
                response = requests.post(url, **kwargs)
            elif method == "PUT":
                # [SRS 22] Support for PUT method
                # For PUT requests, params go in the request body
                kwargs['data'] = additional_params
                response = requests.put(url, **kwargs)
            else:
                logging.error(f"Unsupported HTTP method: {method}")
                return None
                
            # Return the response regardless of status code
            return response

        except requests.RequestException as e:
            logging.error(f"Error making {method} request to {url}: {str(e)}")
            # Create a response object with error status
            response = requests.Response()
            response.status_code = 0
            response.reason = str(e)
            return response
        except Exception as e:
            logging.error(f"Unexpected error while making request to {url}: {str(e)}")
            # Create a response object with error status
            response = requests.Response()
            response.status_code = 0
            response.reason = str(e)
            return response