import os
import subprocess
from pathlib import Path

from hid_controller import DEVICE_PID, DEVICE_VID


UDEV_RULE_PATH = Path('/etc/udev/rules.d/99-mk-star-61.rules')


def setup_udev():
    if os.geteuid() != 0:
        raise PermissionError('Setup must be run with sudo')

    rule = (
        'SUBSYSTEM=="hidraw", '
        f'ATTRS{{idVendor}}=="{DEVICE_VID:04x}", '
        f'ATTRS{{idProduct}}=="{DEVICE_PID:04x}", '
        'MODE="0660", GROUP="input"\n'
    )
    UDEV_RULE_PATH.write_text(rule, encoding='utf-8')
    subprocess.run(['udevadm', 'control', '--reload-rules'], check=True)
    subprocess.run(['udevadm', 'trigger'], check=True)
    print(f'Installed udev rule at {UDEV_RULE_PATH}')
    print('Reconnect the HID device before starting the server.')
