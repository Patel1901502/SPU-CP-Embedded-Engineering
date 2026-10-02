"""High-level host API for communicating with the embedded device."""

import serial

from .protocol import parse_response


class EmbeddedDevice:
    """Small Python client for the ESP32 newline-based UART protocol."""

    def __init__(self, port, baudrate=115200, timeout=1.0):
        """Open a serial connection to the device.

        Args:
            port: Serial port name, for example ``COM5`` or ``/dev/ttyUSB0``.
            baudrate: UART baud rate; must match the firmware configuration.
            timeout: Maximum seconds to wait for a response line.
        """
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    def close(self):
        """Close the underlying serial port."""
        self.serial.close()

    def __enter__(self):
        """Support ``with EmbeddedDevice(...) as device`` usage."""
        return self

    def __exit__(self, *_):
        """Always release the serial port when leaving a context manager."""
        self.close()

    def command(self, command):
        """Send one command and parse the device's single-line response."""
        # Firmware expects every command to be terminated by a newline.
        self.serial.write((command + "\n").encode())

        # readline() waits until newline or the configured serial timeout.
        response = self.serial.readline().decode(errors="replace")
        if not response:
            raise TimeoutError(f"No response to {command}")

        return parse_response(response)

    def ping(self):
        """Return True when the device responds correctly to PING."""
        return self.command("PING")["type"] == "pong"

    def status(self):
        """Request the device readiness/status message."""
        return self.command("STATUS")

    def telemetry(self):
        """Request one temperature/vibration/current sample."""
        return self.command("TELEMETRY")

    def led(self, state):
        """Turn the device LED on when *state* is truthy, otherwise off."""
        return self.command("LED ON" if state else "LED OFF")
