from contextlib import contextmanager
import os

import hid


DEVICE_VID = 0x258A
DEVICE_PID = 0x013B
DEVICE_INTERFACE = 1
MOCK_STATE = {'mode': 1, 'speed': 1, 'brightness': 4}


def is_mock_enabled():
    return os.getenv('STAR61_MOCK_HID') == '1'


def find_device():
    if is_mock_enabled():
        return {
            'path': b'mock://star61',
            'vendor_id': DEVICE_VID,
            'product_id': DEVICE_PID,
            'product_string': 'MK Star 61 (mock)',
            'interface_number': DEVICE_INTERFACE,
        }
    devices = hid.enumerate(DEVICE_VID, DEVICE_PID)
    if not devices:
        raise RuntimeError(
            f'HID device {DEVICE_VID:04x}:{DEVICE_PID:04x} not found'
        )
    interface_devices = [
        device for device in devices
        if device.get('interface_number') == DEVICE_INTERFACE
    ]
    return (interface_devices or devices)[0]


@contextmanager
def open_hid_device(path):
    if hasattr(hid, 'Device'):
        with hid.Device(path=path) as device:
            yield device
        return

    device = hid.device()
    try:
        device.open_path(path)
        yield device
    finally:
        device.close()


def read_state():
    if is_mock_enabled():
        return MOCK_STATE.copy()
    with open_hid_device(find_device()['path']) as device:
        current = device.get_feature_report(10, 42)
    return {
        'mode': current[1],
        'speed': current[3],
        'brightness': current[4],
    }


def update_state(data):
    if is_mock_enabled():
        MOCK_STATE.update(data)
        return read_state()
    with open_hid_device(find_device()['path']) as device:
        current = bytearray(device.get_feature_report(10, 42))
        if 'mode' in data:
            current[1] = data['mode']
        if 'speed' in data:
            current[3] = data['speed']
        if 'brightness' in data:
            current[4] = data['brightness']
        device.send_feature_report(bytes(current))
    return read_state()
