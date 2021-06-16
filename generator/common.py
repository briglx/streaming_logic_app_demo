"""Init file for python_generator script."""
import ipaddress
import random
import uuid
from datetime import datetime, timedelta, timezone

TOTAL_DEVICE_COUNT = 60
FAULTY_DEVICE_COUNT = 3
FAULT_DURATION = 5
FAULT_CHANCE = 0.1
DEFAULT_WAIT_TIME_SEC = 30

IP_NET = ipaddress.ip_network("10.0.0.0/12")


def generate_guid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


def generate_id():
    """Generate Hexadecimal 32 length id."""
    return f"{random.randrange(16 ** 32):32x}"


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


def create_sample_data(device):
    """Generate Sample Data."""
    # Create message specific data
    event_id = generate_guid()
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
            "event_desc": f"Event desc for {event_id}",
            "event_name": f"Event Name for {event_id}",
            "set_or_clear": True,
            "create_datetime": get_date_isoformat(period_start_time),
            "stop_point_id": f"{random.randrange(2 ** 32):08x}",
            "event_reason_code_id": f"{random.randrange(2 ** 16):04x}",
            "period_start_time": get_date_isoformat(period_start_time),
            "period_end_time": get_date_isoformat(period_end_time),
            "values": values,
        },
        "system_guid": generate_guid(),
    }

    return sample_data


def create_drop_list(device_list, count):
    """Return a list of random devices."""
    return random.sample(device_list, count)


def drop_device_message(data, drop_list, device_drop_count):
    """Check if the message should be dropped."""
    device_id = data["device"]["device_id"]
    if data["device"] in drop_list:

        # Add tracking
        if device_id not in device_drop_count:
            device_drop_count[device_id] = 0

        # Check in in fault state
        if device_drop_count[device_id] > 0:
            device_drop_count[device_id] -= 1
            return True

        # Mark device to fail
        if random.random() < FAULT_CHANCE:
            device_drop_count[device_id] = FAULT_DURATION

    return False
