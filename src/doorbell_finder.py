"""Device discovery and battery extraction for Wyze doorbell."""

import logging

logger = logging.getLogger(__name__)

DOORBELL_INDICATORS = [
    'doorbell',
    'wvdb',      # Wyze Video Doorbell prefix
    'gw_be1',    # Battery doorbell model (suspected)
]


def explore_devices(client):
    """
    Exploration mode: Print detailed info about all devices.

    Use this to discover the doorbell's exact model/type identifiers
    and find battery-related attributes.

    Args:
        client: Authenticated Wyze client
    """
    logger.info("Fetching all devices...")
    devices = client.devices_list()

    if not devices:
        logger.warning("No devices found in account")
        return

    logger.info(f"Found {len(devices)} device(s):\n")

    for device in devices:
        print("=" * 60)
        print(f"Nickname: {device.nickname}")
        print(f"MAC: {device.mac}")
        print(f"Online: {device.is_online}")

        if hasattr(device, 'product') and device.product:
            print(f"Product Type: {getattr(device.product, 'type', 'N/A')}")
            print(f"Product Model: {getattr(device.product, 'model', 'N/A')}")

        battery_attrs = ['battery', 'voltage', 'battery_level', 'power_level',
                         'electricity', 'battery_percentage']
        for attr in battery_attrs:
            if hasattr(device, attr):
                value = getattr(device, attr)
                if value is not None:
                    print(f"{attr}: {value}")

        if hasattr(device, 'to_dict'):
            try:
                data = device.to_dict()
                print(f"Full data: {data}")
            except Exception as e:
                print(f"Could not get dict: {e}")

        if hasattr(device, 'get_non_null_attributes'):
            try:
                attrs = device.get_non_null_attributes()
                print(f"Non-null attributes: {attrs}")
            except Exception:
                pass

        print()


def find_doorbell(client):
    """
    Find the doorbell device from all devices.

    Args:
        client: Authenticated Wyze client

    Returns:
        tuple: (doorbell_device or None, list of all device info dicts)
    """
    logger.info("Searching for doorbell device...")
    devices = client.devices_list()

    doorbell = None
    all_devices_info = []

    for device in devices:
        device_info = {
            'mac': device.mac,
            'nickname': device.nickname,
            'product_type': getattr(device.product, 'type', 'unknown') if device.product else 'unknown',
            'product_model': getattr(device.product, 'model', 'unknown') if device.product else 'unknown',
            'is_online': device.is_online,
        }
        all_devices_info.append(device_info)

        product_type = str(device_info['product_type']).lower()
        product_model = str(device_info['product_model']).lower()
        nickname = str(device.nickname).lower()

        for indicator in DOORBELL_INDICATORS:
            if (indicator in product_type or
                    indicator in product_model or
                    indicator in nickname):
                doorbell = device
                logger.info(f"Found doorbell: {device.nickname} (model: {device_info['product_model']})")
                break

        if doorbell:
            break

    if not doorbell:
        logger.warning("Doorbell not found by known identifiers")

    return doorbell, all_devices_info


def get_battery_level(device):
    """
    Extract battery level from device using multiple strategies.

    Args:
        device: Wyze device object

    Returns:
        int or None: Battery percentage (0-100) or None if not found
    """
    if hasattr(device, 'battery'):
        battery = device.battery
        if battery is not None:
            if isinstance(battery, int):
                return battery
            if isinstance(battery, float):
                return int(battery)
            if hasattr(battery, 'value'):
                return battery.value

    if hasattr(device, 'battery_level'):
        level = device.battery_level
        if level is not None:
            return int(level)

    # Note: Wyze doorbells report battery percentage in the 'voltage' field (0-100)
    # Actual voltage would be 2.5-4.2V, so values > 10 are already percentages
    if hasattr(device, 'voltage'):
        voltage = device.voltage
        if voltage is not None:
            if isinstance(voltage, str):
                voltage = int(voltage)
            if voltage > 10:
                return int(voltage)
            return voltage_to_percentage(voltage)

    if hasattr(device, 'to_dict'):
        try:
            data = device.to_dict()
            battery_keys = ['battery', 'battery_level', 'battery_percentage',
                           'power_level', 'electricity']
            for key in battery_keys:
                if key in data and data[key] is not None:
                    return int(data[key])
        except Exception:
            pass

    if hasattr(device, 'get_non_null_attributes'):
        try:
            attrs = device.get_non_null_attributes()
            for key, value in attrs.items():
                if 'battery' in key.lower() or 'power' in key.lower():
                    if isinstance(value, (int, float)):
                        return int(value)
        except Exception:
            pass

    return None


def voltage_to_percentage(voltage):
    """
    Convert Li-ion battery voltage to percentage.

    Typical range: 2.5V (0%) to 4.2V (100%)

    Args:
        voltage: Battery voltage

    Returns:
        int: Battery percentage (0-100)
    """
    MIN_VOLTAGE = 2.5
    MAX_VOLTAGE = 4.2

    if voltage <= MIN_VOLTAGE:
        return 0
    if voltage >= MAX_VOLTAGE:
        return 100

    return int(((voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)) * 100)
