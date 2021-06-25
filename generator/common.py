"""Init file for python_generator script."""
import ipaddress
import random
import uuid
from datetime import datetime, timedelta, timezone

TOTAL_DEVICE_COUNT = 30
DROP_CHANCE = 0.1
FAULTY_DEVICE_COUNT = 3
FAULT_DURATION = 5
FAULT_CHANCE = 0.5
DEFAULT_WAIT_TIME_SEC = 30

IP_NET = ipaddress.ip_network("10.0.0.0/12")

EVENT_CODES = [
    "3f25",
    "19a5",
    "f6d2",
    "976b",
    "f8f4",
    "ffff",
    "3d4b",
    "d9dd",
    "6050",
    "2b9b",
]

DEFAULT_DEVICE_CODE = 100
DEVICE_CODES = {
    100: "Normal State",
    101: "Voltage Dropout",
    105: "System Time Sync Adjustment",
    108: "Maintenance Door Open/Closed ",
    109: "Loss of Comms with Local Devices",
    117: "Warning Extreme Temperature",
    118: "Extreme Temperature Reached",
    131: "Missing Tables ",
    134: "Device Restart ",
    140: "In Service",
    141: "Software Activation Failed",
    143: "Software Error",
    144: "Battery Disconnected",
    152: "Software Digest Missing",
    153: "Software Digest Invalid",
    158: "Battery Charge Fail",
    165: "Vehicle Ignition off",
    172: "Orphan Mode Timeout",
    182: "Software Installation Failed",
    183: "Fatal Failure",
    186: "P2PE Device Tampered",
    201: "CSC Target Fault",
    209: "Tri-Reader Comms Error",
    220: "Missing Keys",
    602: "Disk Almost Full",
    603: "Disk Full",
    1201: "Barrier Failure",
    1228: "68K Board Out of Service",
    2205: "DAP Taps Table Almost Full",
    2206: "DAP Taps Table Full",
    2207: "DAP Database Failure",
    2224: "DAP Taps Error In Record",
    2228: "DAP Invalid Encryption Key",
    2243: "DAP Risk List Far Behind",
    2246: "BIN List MAC Error",
    2247: "RTVS MAC Error",
    50101: "No Heartbeat",
    50140: "Out of Service (50140)",
}


def generate_guid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


def generate_id():
    """Generate Hexadecimal 32 length id."""
    return f"{random.randrange(16 ** 32):32x}"


def generate_faulty_event_id():
    """Generate random event id from list."""
    # Unpack dict_keys to array
    return random.choice([*DEVICE_CODES.keys()])


def generate_event_reason_code_id():
    """Return random event code."""
    return random.choice(EVENT_CODES)
    # return f"{random.randrange(2 ** 16):04x}"


def get_date_now_isoformat():
    """Generate Iso Formatted Date based on Now."""
    cur_time = datetime.utcnow()
    return get_date_isoformat(cur_time)


def get_date_isoformat(date):
    """Format Iso Formatted Date."""
    cur_time = date.replace(tzinfo=timezone.utc, microsecond=0)
    return cur_time.isoformat().replace("+00:00", "Z")


def create_device(device_index):
    """Create device for given index."""
    device_id = generate_id()

    device = {
        "device_id": device_id,
        "device_serial_number": f"sn-{random.randrange(16 ** 12):12x}",
        "componant_id": f"comp-{device_id}",
        "componant_position": f"{random.randrange(2 ** 8):2x}",
        "ip_address": IP_NET[device_index],
        "operator_id": f"op-{device_id}",
    }

    return device


def create_device_list(count=TOTAL_DEVICE_COUNT):
    """Create list of devices for testing."""
    device_list = []
    for device_index in range(count):
        device = create_device(device_index)
        device_list.append(device)
    return device_list


def get_random_device_id(device_list):
    """Return a random device from the device list."""
    return random.choice(device_list)


def create_sample_data(device, faulty_devices_ids):
    """Generate Sample Data."""
    # Send faulty code
    if send_error_message(device["device_id"], faulty_devices_ids):
        event_id = generate_faulty_event_id()
    else:
        event_id = DEFAULT_DEVICE_CODE

    period_start_time = datetime.utcnow()
    period_count = random.randint(0, 30)
    period_end_time = period_start_time + timedelta(0, period_count)
    max_value = 50
    start_value = random.uniform(20, max_value)
    delta_value = random.uniform(-1, 1) * max_value

    values = []
    cur_value = start_value
    for i in range(period_count):
        start_interval = period_start_time + timedelta(0, i)
        end_interval = period_start_time + timedelta(0, i + 1)
        values.append(
            {
                "start_interval": get_date_isoformat(start_interval),
                "end_interval": get_date_isoformat(end_interval),
                "value": f"{cur_value:.2f}",
            }
        )
        cur_value = cur_value + delta_value

    sample_data = {
        "device": device,
        "event": {
            "event_id": event_id,
            "event_name": f"Event Name for {event_id}",
            "set_or_clear": True,
            "create_datetime": get_date_isoformat(period_start_time),
            "stop_point_id": f"{random.randrange(2 ** 32):08x}",
            "event_reason_code_id": generate_event_reason_code_id(),
            "period_start_time": get_date_isoformat(period_start_time),
            "period_end_time": get_date_isoformat(period_end_time),
            "values": values,
        },
        "system_guid": generate_guid(),
    }

    return sample_data


def create_fault_list(device_list, count):
    """Return a list of random faulty devices."""
    faulty_devices = random.sample(device_list, count)
    faulty_device_ids = [d["device_id"] for d in faulty_devices]
    return (faulty_device_ids, faulty_devices)


def drop_device_message(device_id, device_drop_count):
    """Check if the message should be dropped."""
    # check if device already in drop state
    if device_id in device_drop_count and device_drop_count[device_id] > 0:
        device_drop_count[device_id] -= 1
        return True

    if random.random() <= DROP_CHANCE:

        # Mark device to fail N times
        device_drop_count[device_id] = FAULT_DURATION

    return False


def send_error_message(device_id, faulty_list):
    """Check if the message should be an error."""
    if device_id in faulty_list:

        # Mark device to fail
        if random.random() < FAULT_CHANCE:
            return True

    return False
