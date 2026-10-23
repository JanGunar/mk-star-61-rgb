import argparse
import subprocess

from app import app
from udev_setup import setup_udev


def main():
    parser = argparse.ArgumentParser(description='MK Star 61 controller')
    parser.add_argument('--setup', action='store_true', help='install udev permissions')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8000, type=int)
    parser.add_argument('--mock', action='store_true', help='run without a physical HID device')
    args = parser.parse_args()

    if args.mock:
        import os
        os.environ['STAR61_MOCK_HID'] = '1'

    if args.setup:
        try:
            setup_udev()
        except (OSError, subprocess.CalledProcessError, PermissionError) as error:
            parser.error(f'Setup failed: {error}')
    else:
        app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
