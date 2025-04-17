import os
from urllib.parse import urlparse
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger('brute_forcer') # Or a more generic logger if needed

def validate_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate and normalize a URL.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, normalized_url or None, error_message or None)
    """
    if not url:
        return False, None, "URL cannot be empty"

    try:
        parsed_url = urlparse(url)

        if not parsed_url.scheme:
            return False, None, "URL must have a scheme (e.g., http, https)"

        if not parsed_url.netloc:
            return False, None, "URL must have a hostname"

        return True, parsed_url.geturl(), None

    except Exception as e:
        return False, None, f"Invalid URL format: {e}"


def validate_wordlist(path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a wordlist file exists and is readable.

    Args:
        path: Path to wordlist file

    Returns:
        Tuple of (is_valid, error_message or None)
    """
    if not path:
        return False, "Wordlist path cannot be empty"

    if not os.path.exists(path):
        return False, f"Wordlist file does not exist: {path}"

    if not os.path.isfile(path):
        return False, f"Wordlist path is not a file: {path}"

    if not os.access(path, os.R_OK):
        return False, f"Wordlist file is not readable: {path}"

    # Basic check for file extension (can be expanded)
    if not path.lower().endswith(('.txt', '.lst', '.dic')):
        logger.warning(f"Wordlist file '{path}' does not have a common wordlist extension.")
        # We still consider it valid for now, but the UI could inform the user.

    # Basic check to see if the file is likely a text file
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            first_few_chars = f.read(100)
            if '\0' in first_few_chars:
                return False, f"Wordlist file '{path}' appears to be binary."
    except Exception as e:
        logger.error(f"Error during basic wordlist content check: {e}")
        return False, f"Error reading wordlist for compatibility check."

    return True, None


def load_wordlist(path: str) -> List[str]:
    """
    Load words from a wordlist file.

    Args:
        path: Path to wordlist file

    Returns:
        List of words
    """
    wordlist = []
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                word = line.strip()
                if word:
                    wordlist.append(word)
    except Exception as e:
        logger.error(f"Error loading wordlist: {str(e)}")
    return wordlist


def parse_status_codes(status_str: str) -> List[int]:
    """
    Parse a comma-separated list of status codes.

    Args:
        status_str: String of comma-separated status codes

    Returns:
        List of integer status codes
    """
    result = []
    if not status_str:
        return result

    parts = status_str.split(',')
    for part in parts:
        part = part.strip()
        try:
            code = int(part)
            result.append(code)
        except ValueError:
            # Skip invalid codes
            continue

    return result


def build_url(base_url: str, path: str) -> str:
    """
    Build a URL by combining base URL and path.

    Args:
        base_url: Base URL
        path: Path to append

    Returns:
        Complete URL
    """
    # Ensure base URL ends with /
    if not base_url.endswith('/'):
        base_url += '/'

    # Ensure path doesn't start with /
    if path.startswith('/'):
        path = path[1:]

    return base_url + path


def apply_filters(response_data: Dict[str, Any],
                  hide_status: List[int],
                  show_only_status: List[int],
                  filter_by_content_length: Optional[str]) -> bool:
    """
    Apply filtering rules to determine if a result should be shown.

    Args:
        response_data: Response data dictionary
        hide_status: List of status codes to hide
        show_only_status: List of status codes to exclusively show
        filter_by_content_length: Content length filter expression

    Returns:
        True if result should be shown, False if filtered out
    """

    # Extract status code and content length
    status_code = response_data.get('status_code')
    content_length = response_data.get('content_length', 0)

    # Check for missing or invalid status_code
    if status_code is None:
        print("Warning: Missing 'status_code' in response_data:", response_data)
        return False  # You can change this to True if needed

    # Apply hide_status filter
    if hide_status and status_code in hide_status:
        return False

    # Apply show_only_status filter
    if show_only_status and status_code not in show_only_status:
        return False

    # Apply content length filter
    if filter_by_content_length:
        try:
            # Parse filter like '=100', '>100', '<100'
            filter_op = filter_by_content_length[0] if filter_by_content_length[0] in '=<>' else '='
            filter_value = int(filter_by_content_length.lstrip('=<>'))

            if filter_op == '=' and content_length != filter_value:
                return False
            elif filter_op == '>' and content_length <= filter_value:
                return False
            elif filter_op == '<' and content_length >= filter_value:
                return False
        except (ValueError, IndexError):
            # Invalid filter expression is ignored
            print("Warning: Invalid content length filter:", filter_by_content_length)

    # All filters passed
    return True