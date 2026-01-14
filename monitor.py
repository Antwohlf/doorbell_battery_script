#!/usr/bin/env python3
"""
Wyze Doorbell Battery Monitor

Checks the battery level of a Wyze doorbell and sends email alerts when the battery drops below a configurable threshold.

Usage:
    # Normal run
    python monitor.py

    # Explore devices (first run)
    EXPLORE_MODE=true python monitor.py

    # Force a test alert
    FORCE_ALERT=true python monitor.py
"""

import sys
import logging
from datetime import datetime

from src.config import Config
from src.wyze_client import create_authenticated_client, AuthenticationError
from src.doorbell_finder import find_doorbell, explore_devices, get_battery_level
from src.notifier import EmailNotifier, NotificationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    config = Config()

    logger.info(f"Doorbell Battery Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        Config.validate()
    except EnvironmentError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info("Authenticating with Wyze...")
    try:
        client = create_authenticated_client()
    except AuthenticationError as e:
        logger.error(str(e))
        sys.exit(1)

    if config.explore_mode:
        logger.info("Running in exploration mode...")
        explore_devices(client)
        logger.info("Exploration complete. Use the device info above to identify your doorbell.")
        return

    doorbell, all_devices = find_doorbell(client)

    if doorbell is None:
        logger.error("Doorbell not found!")
        logger.info("Available devices:")
        for device in all_devices:
            logger.info(f"  - {device['nickname']} (type: {device['product_type']}, model: {device['product_model']})")
        sys.exit(2)

    logger.info(f"Found doorbell: {doorbell.nickname}")

    battery_level = get_battery_level(doorbell)

    if battery_level is None:
        logger.error("Could not determine battery level")
        sys.exit(3)

    logger.info(f"Battery level: {battery_level}%")

    should_alert = (
        battery_level < config.battery_threshold or
        config.force_alert
    )

    if should_alert:
        if config.force_alert:
            logger.info("Force alert enabled, sending test notification...")
        else:
            logger.info(f"Battery below threshold ({config.battery_threshold}%), sending alert...")

        try:
            Config.validate_notification()
        except EnvironmentError as e:
            logger.error(str(e))
            sys.exit(4)

        try:
            notifier = EmailNotifier()
            notifier.send_battery_alert(battery_level, doorbell.nickname)
            logger.info("Alert sent successfully")
        except NotificationError as e:
            logger.error(str(e))
            sys.exit(4)
    else:
        logger.info(f"Battery level OK (threshold: {config.battery_threshold}%)")

    logger.info("Monitor completed successfully")


if __name__ == '__main__':
    main()
