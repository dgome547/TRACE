# backend/app/webcrawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def crawl(start_url, depth_limit=1, timeout=5000):
    """
    Web crawler function that crawls starting from a URL up to a certain depth
    
    Args:
        start_url (str): The URL to start crawling from
        depth_limit (int): How many links deep to crawl
        timeout (int): Request timeout in milliseconds
        
    Returns:
        dict: Results of the crawl including pages visited and links found
    """
    visited = set()
    results = {
        "pages_visited": 0,
        "links_found": 0,
        "data": []
    }
    
    def visit_url(url, current_depth):
        if current_depth > depth_limit or url in visited or not url.startswith(('http://', 'https://')):
            return
        
        visited.add(url)
        
        try:
            response = requests.get(url, timeout=timeout/1000)
            results["pages_visited"] += 1
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_title = soup.title.string if soup.title else "No title"
                
                page_data = {
                    "url": url,
                    "title": page_title,
                    "status": response.status_code,
                    "links": []
                }
                
                # Find all links on the page
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    absolute_url = urljoin(url, href)
                    
                    # Skip fragment links or other non-http URLs
                    if not absolute_url.startswith(('http://', 'https://')):
                        continue
                        
                    # Only include links from the same domain
                    if urlparse(absolute_url).netloc == urlparse(url).netloc:
                        page_data["links"].append(absolute_url)
                        results["links_found"] += 1
                        
                        # Visit the linked page if we haven't reached depth limit
                        if current_depth < depth_limit:
                            visit_url(absolute_url, current_depth + 1)
                
                results["data"].append(page_data)
                
        except Exception as e:
            results["data"].append({
                "url": url,
                "error": str(e),
                "status": "error"
            })
    
    # Start crawling from the initial URL
    visit_url(start_url, 1)
    return results