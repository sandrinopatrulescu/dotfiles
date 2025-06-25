#!/usr/bin/env python3

import argparse
import re
import subprocess
import sys

VALID_ROTATIONS = ["normal", "left", "right", "inverted"]


def get_connected_monitors():
    try:
        output = subprocess.check_output(['xrandr'], text=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to run xrandr")
        sys.exit(1)

    monitors = []
    for line in output.splitlines():
        match = re.match(r'^([A-Za-z0-9-]+) connected', line)
        if match:
            monitors.append(match.group(1))
    return monitors


def rotate_monitor(monitor, rotation):
    try:
        subprocess.run(['xrandr', '--output', monitor, '--rotate', rotation], check=True)
        print(f"✅ Rotated {monitor} to {rotation}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to rotate {monitor} to {rotation}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Rotate a monitor using xrandr.")
    parser.add_argument("monitor", help="Monitor name (e.g., HDMI-1, eDP-1)", choices=get_connected_monitors())
    parser.add_argument("rotation", help=f"Rotation mode: {VALID_ROTATIONS}", choices=VALID_ROTATIONS)

    args = parser.parse_args()

    rotate_monitor(args.monitor, args.rotation)


if __name__ == "__main__":
    main()
