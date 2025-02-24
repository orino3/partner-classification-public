import validators
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Validate URL format and ensure it has a scheme."""
    if not url:
        return False
        
    # Add http:// if no scheme is present
    if not urlparse(url).scheme:
        url = "http://" + url
        
    return validators.url(url) 