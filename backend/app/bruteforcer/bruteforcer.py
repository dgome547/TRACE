import requests

def run_bruteforce(base_url, wordlist_path):
    found = []
    with open(wordlist_path, 'r') as f:
        paths = [line.strip() for line in f.readlines()]
    
    for path in paths:
        url = f"{base_url.rstrip('/')}/{path}"
        try:
            res = requests.get(url)
            if res.status_code in [200, 403]:
                print(f"[+] Found: {url} (Status: {res.status_code})")
                found.append((url, res.status_code))
        except requests.RequestException:
            print(f"[-] Error requesting {url}")
    
    return found
