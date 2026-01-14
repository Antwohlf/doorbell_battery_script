"""Configuration handling for Wyze Doorbell Battery Monitor."""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """Configuration manager with environment variable handling."""

    def __init__(self):
        self.battery_threshold = int(os.environ.get('BATTERY_THRESHOLD', 20))
        self.force_alert = os.environ.get('FORCE_ALERT', 'false').lower() == 'true'
        self.explore_mode = os.environ.get('EXPLORE_MODE', 'false').lower() == 'true'

    @staticmethod
    def validate():
        """Validate required environment variables are set."""
        required = ['WYZE_EMAIL', 'WYZE_PASSWORD', 'WYZE_KEY_ID', 'WYZE_API_KEY']
        missing = [var for var in required if not os.environ.get(var)]
        if missing:
            raise EnvironmentError(
                f"Missing required variables: {missing}\n"
                "Get API keys at: https://developer-api-console.wyze.com/#/apikey/view"
            )

    @staticmethod
    def validate_notification():
        """Validate notification environment variables are set."""
        required = ['RESEND_API_KEY', 'SENDER_EMAIL', 'RECIPIENT_EMAIL']
        missing = [var for var in required if not os.environ.get(var)]
        if missing:
            raise EnvironmentError(f"Missing notification variables: {missing}")
