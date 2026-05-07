"""Wyze API client authentication."""

import os
import logging

from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError, WyzeClientConfigurationError

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Wyze authentication failed."""
    pass


def create_authenticated_client():
    """
    Create and authenticate a Wyze client.

    As of July 2023, Wyze requires API keys for authentication.
    Get your API key at: https://developer-api-console.wyze.com/#/apikey/view

    Returns:
        Client: Authenticated Wyze client

    Raises:
        AuthenticationError: If authentication fails
    """
    email = os.environ.get('WYZE_EMAIL')
    password = os.environ.get('WYZE_PASSWORD')
    key_id = os.environ.get('WYZE_KEY_ID')
    api_key = os.environ.get('WYZE_API_KEY')

    if not email or not password:
        raise AuthenticationError("WYZE_EMAIL and WYZE_PASSWORD must be set")

    if not key_id or not api_key:
        raise AuthenticationError(
            "WYZE_KEY_ID and WYZE_API_KEY are required.\n"
            "Get your API keys at: https://developer-api-console.wyze.com/#/apikey/view"
        )

    try:
        client = Client()
        client.login(email=email, password=password, key_id=key_id, api_key=api_key)
        logger.info("Successfully authenticated with Wyze")
        return client
    except (WyzeApiError, WyzeClientConfigurationError) as e:
        raise AuthenticationError(f"Failed to authenticate with Wyze: {e}")
