"""Command-line interface for interacting with the ESP32 monitoring device."""

import argparse

from host.device import EmbeddedDevice
from host.telemetry import iter_samples, save_csv


def build_parser():
    """Create and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Communicate with the ESP32 monitoring platform over UART."
    )
    parser.add_argument(
        "--port",
        required=True,
        help="Serial port, for example COM5 or /dev/ttyUSB0.",
    )

    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=1.0)

    # Subcommands map directly to common embedded-device operations.
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("ping", help="Verify device communication.")
    subparsers.add_parser("status", help="Read device status.")
    subparsers.add_parser("telemetry", help="Read one telemetry sample.")

    led_parser = subparsers.add_parser("led", help="Control the status LED.")
    led_parser.add_argument("state", choices=["on", "off"])

    collect_parser = subparsers.add_parser(
        "collect", help="Collect telemetry for a period and save it to CSV."
    )
    collect_parser.add_argument(
        "--seconds", type=float, default=30, help="Collection duration."
    )
    collect_parser.add_argument(
        "--output", default="telemetry.csv", help="Output CSV path."
    )

    collect_parser.add_argument("--interval", type=float, default=1.0)
    return parser


def main():
    """Execute the requested device command."""
    args = build_parser().parse_args()

    # The context manager guarantees that the serial port is closed even if a
    # command raises an exception.
    with EmbeddedDevice(args.port, baudrate=args.baudrate, timeout=args.timeout) as device:
        if args.command == "ping":
            print("PONG" if device.ping() else "FAIL")
        elif args.command == "status":
            print(device.status())
        elif args.command == "telemetry":
            print(device.telemetry())
        elif args.command == "led":
            print(device.led(args.state == "on"))
        elif args.command == "collect":
            samples = iter_samples(device, args.seconds, args.interval)
            save_csv(samples, args.output)
            print(f"Collection complete: {args.output}")


if __name__ == "__main__":
    main()
