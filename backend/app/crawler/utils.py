import re
import logging
from typing import Dict, Any, Tuple


def valid_url(url: str) -> bool:
    """
    Validates if a URL is properly formatted and meets security criteria.

    Args:
        url (str): The URL to validate

    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        # Basic type check
        if not isinstance(url, str) or not url:
            return False

        # Check for allowed schemes
        allowed_schemes = {'http', 'https'}
        if not any(url.startswith(scheme + '://') for scheme in allowed_schemes):
            return False

        # Check for common URL patterns
        url_pattern = re.compile(
            r'^'
            r'(?:http|https)://'  # scheme
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip address
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            return False

        # Additional security checks
        # Prevent URLs with user:pass@ format
        if '@' in url:
            return False

        # Check for common file extensions that might be dangerous
        dangerous_extensions = {'.exe', '.dll', '.bat', '.cmd', '.sh', '.jar', '.app'}
        if any(url.lower().endswith(ext) for ext in dangerous_extensions):
            return False

        # Check URL length
        if len(url) > 2048:  # Common URL length limit
            return False

        return True

    except Exception:
        return False


def validate_config(config: Dict[str, Any]) -> Tuple[bool, list]:
    """
    Validates crawler configuration according to SRS requirements

    Args:
        config (dict): Configuration parameters

    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []

    # SRS-29.1: Validate required fields
    if not config.get("targetUrl"):
        errors.append("Target URL is required")

    # Validate Target URL format
    if config.get("targetUrl") and not valid_url(config["targetUrl"]):
        errors.append("Target URL is invalid or not properly formatted")

    # SRS-29.5: Require positive values
    numeric_fields = [
        ("depth_limit", "Depth Limit"),
        ("limitPages", "Limit on Number of Pages"),
        ("requestDelay", "Request Delay")
    ]

    for field_name, field_label in numeric_fields:
        if field_name in config:
            try:
                value = float(config[field_name])
                if value <= 0:
                    errors.append(f"{field_label} must be a positive value")
            except (ValueError, TypeError):
                if config[field_name]:  # Only add error if field has a non-empty value
                    errors.append(f"{field_label} must be a valid number")

    # Validate optional userAgent and proxy fields
    if "userAgent" in config and not isinstance(config["userAgent"], str):
        errors.append("User Agent must be a string")
    if "proxy" in config and config["proxy"] and not isinstance(config["proxy"], str):
        errors.append("Proxy must be a string or None")

    return (len(errors) == 0, errors)


def setup_logging(log_file='crawler.log'):
    """Configure logging for crawler operations"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )