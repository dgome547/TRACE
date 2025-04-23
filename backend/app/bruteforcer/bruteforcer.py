import requests
import concurrent.futures
import os

# === CONFIGURATION ===
THREADS = 20
EXTENSIONS = ['', '.php', '.html', '.bak']  # Add extensions here
HEADERS = {'User-Agent': 'Mozilla/5.0 (DirFuzzer)'}
TIMEOUT = 5
ALLOWED_CODES = [200, 301, 302, 403]  # What to consider valid
MAX_RECURSION_DEPTH = 2  # Limit how deep to recurse

found_urls = []

def is_valid_response(url, status_code, base_response_length):
    try:
        if status_code in ALLOWED_CODES:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            return len(res.text) != base_response_length
    except:
        pass
    return False

def fuzz_path(base_url, path, base_response_length, depth=0):
    global found_urls

    for ext in EXTENSIONS:
        full_path = f"{path}{ext}".lstrip('/')
        url = f"{base_url.rstrip('/')}/{full_path}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            if res.status_code in ALLOWED_CODES:
                if len(res.text) != base_response_length:
                    print(f"[+] Found: {url} (Status: {res.status_code})")
                    found_urls.append((url, res.status_code))

                    # Recursively fuzz if it's a directory and depth allows
                    if url.endswith('/') or res.text.lower().find('index of') != -1:
                        if depth < MAX_RECURSION_DEPTH:
                            run_fuzzer(base_url, wordlist_path, base_response_length, prefix=full_path + '/', depth=depth + 1)
        except requests.RequestException:
            pass

def run_fuzzer(base_url, wordlist_path, base_response_length=0, prefix='', depth=0):
    with open(wordlist_path, 'r') as f:
        paths = [line.strip() for line in f.readlines() if line.strip()]

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(fuzz_path, base_url, os.path.join(prefix, path), base_response_length, depth) for path in paths]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    base_url = input("Base URL (e.g., http://example.com): ").strip()
    wordlist_path = input("Path to wordlist file: ").strip()

    # Send a dummy request to get the base response length (used to detect wildcard 200s)
    try:
        dummy = requests.get(f"{base_url.rstrip('/')}/this_path_does_not_exist", headers=HEADERS, timeout=TIMEOUT)
        base_response_length = len(dummy.text)
    except:
        base_response_length = 0

    print("\n[*] Starting directory fuzzing...\n")
    run_fuzzer(base_url, wordlist_path, base_response_length)

    print("\n[*] Fuzzing complete. Results:")
    for url, status in found_urls:
        print(f"{url} - {status}")
