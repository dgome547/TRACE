import asyncio
import os
import time
from bruteforcer import BruteForcer
from utils import load_wordlist

async def run_live_test(target_url="http://testphp.vulnweb.com/", wordlist_file="wordlist.txt", output_csv="live_test_results.csv", max_words=10):
    """Runs a live brute-force test against a target URL and exports specific SRS info to CSV."""
    brute_forcer = BruteForcer()

    # Ensure wordlist.txt exists (create a sample if not)
    if not os.path.exists(wordlist_file):
        with open(wordlist_file, "w") as f:
            f.write("admin\n")
            f.write("login\n")
            f.write("test\n")
            f.write("dashboard\n")
            f.write("robots.txt\n")
        print(f"Created a sample {wordlist_file} for testing.")

    wordlist = load_wordlist(wordlist_file)[:max_words]

    if not wordlist:
        print(f"Error: Wordlist {wordlist_file} is empty or could not be loaded.")
        return

    config = {
        "target_url": target_url,
        "wordlist_path": wordlist_file,
        "max_concurrent_requests": 5,  # Keep this low
        "request_timeout": 5,
        "output_format": "csv",  # Set output format to CSV
        "hide_status": [],       # Do not hide any status codes
        "show_only_status": []  # Do not show only specific status codes
    }

    print(f"Starting live test against {target_url} with {len(wordlist)} words.")
    start_time = time.time()
    scan_output = await brute_forcer.start_scan(config)
    end_time = time.time()
    print(f"Live test finished in {end_time - start_time:.2f} seconds.")

    if "results" in scan_output and scan_output["results"]:
        # The results are now stored in brute_forcer.results
        brute_forcer._export_results_to_csv(output_csv) # Call the export method
    else:
        print("No results to export.")
        if "message" in scan_output:
            print(f"Error during scan: {scan_output['message']}")

async def main():
    await run_live_test()

if __name__ == "__main__":
    asyncio.run(main())