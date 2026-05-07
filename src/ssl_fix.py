"""Requests SSL workaround for Wyze's API certificate chain in GitHub Actions."""

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

_ORIGINAL_SEND = requests.Session.send
_PATCHED = False


def disable_wyze_ssl_verification():
    """Disable certificate verification only for Wyze API requests."""
    global _PATCHED

    if _PATCHED:
        return

    urllib3.disable_warnings(InsecureRequestWarning)

    def send_with_wyze_ssl_workaround(session, request, **kwargs):
        if request.url.startswith("https://api.wyzecam.com/"):
            kwargs["verify"] = False
        return _ORIGINAL_SEND(session, request, **kwargs)

    requests.Session.send = send_with_wyze_ssl_workaround
    _PATCHED = True
