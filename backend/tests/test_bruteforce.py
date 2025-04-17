import json
import pytest
import sys
import os
#in the trace root folder run this command to run the test pytest -s .\backend\tests\test_bruteforce.py
#pip install pytest-asyncio
# Update sys.path to ensure it includes the backend directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

# Now import the necessary modules
from app.bruteforcer.bruteforcer import BruteForcer
from app.bruteforcer.utils import load_wordlist


@pytest.mark.asyncio
async def test_run_live_bruteforce():
    """Tests the BruteForcer against a known test target with a small wordlist."""

    brute_forcer = BruteForcer()
    target_url = "http://testphp.vulnweb.com/"
    wordlist_file = "backend/tests/wordlist.txt"
    output_csv = "live_test_results.csv"

    # Create a small test wordlist if it doesn't exist
    if not os.path.exists(wordlist_file):
        with open(wordlist_file, "w") as f:
            f.write("admin\n")
            f.write("login\n")
            f.write("test\n")
            f.write("dashboard\n")
            f.write("robots.txt\n")

    wordlist = load_wordlist(wordlist_file)[:10]
    assert len(wordlist) > 0, "Wordlist failed to load or is empty."

    config = {
        "target_url": target_url,
        "wordlist_path": wordlist_file,
        "max_concurrent_requests": 5,
        "request_timeout": 5,
        "output_format": "csv",
        "hide_status": [],
        "show_only_status": []
    }

    scan_output = await brute_forcer.start_scan(config)
    print("Scan Results:")
    print(json.dumps(scan_output["results"], indent=2))



    # Basic checks to ensure scan was performed
    assert isinstance(scan_output, dict), "Scan output is not a dictionary."
    assert "results" in scan_output, "Missing 'results' in scan output."

    if scan_output["results"]:
        # Ensure tester folder exists
        output_folder = "backend/tests/tester"
        os.makedirs(output_folder, exist_ok=True)  # Create the 'tester' folder if it doesn't exist

        # Set the full path for the CSV file in the tester folder
        output_csv_path = os.path.join(output_folder, output_csv)

        # Export to CSV if we found anything
        
        brute_forcer._export_results_to_csv(output_csv_path)
        assert os.path.exists(output_csv_path), f"CSV export failed to {output_csv_path}."
        print(f"Results exported to {output_csv_path}")
    else:
        print("No results found during test scan.")
