"""SSL certificate verification fix for Wyze SDK."""

import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress the SSL warning
urllib3.disable_warnings(InsecureRequestWarning)


def disable_ssl_verification():
    """Disable SSL verification for requests in GitHub Actions."""
    import requests
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
