"""Main ESP32 MicroPython application.

The firmware implements a small request/response UART service. The host sends
newline-terminated ASCII commands and the ESP32 returns newline-terminated
responses containing status, telemetry, or command results.
"""

import time
from machine import Pin, UART

import config
from protocol import handle_command
from sensors import SensorSuite


def main():
    """Initialize hardware and service UART commands forever."""
    # UART0 is used for this demonstration because it is readily accessible
    # over USB on many ESP32 development boards.
    uart = UART(0, baudrate=config.UART_BAUDRATE)

    # Configure the status LED as a digital output controlled by host commands.
    led = Pin(config.LED_PIN, Pin.OUT)

    # SensorSuite currently generates simulated values; its public API is kept
    # hardware-independent so real drivers can be substituted later.
    sensors = SensorSuite()

    # UART reads may return partial commands or multiple commands at once.
    # Accumulate bytes until a complete newline-delimited frame is available.
    receive_buffer = b""

    while True:
        if uart.any():
            incoming = uart.read()
            if incoming:
                receive_buffer += incoming

            # Process every complete command currently buffered. Any trailing
            # partial command remains in receive_buffer for the next iteration.
            while b"\n" in receive_buffer:
                raw_command, receive_buffer = receive_buffer.split(b"\n", 1)

                try:
                    command = raw_command.decode().strip()
                    response = handle_command(command, sensors, led)
                    uart.write(response + "\r\n")
                except Exception as exc:
                    # Keep the firmware alive if one malformed command or sensor
                    # operation fails. Production firmware should also log/count
                    # faults and avoid exposing sensitive exception information.
                    uart.write("ERR INTERNAL={}\r\n".format(exc))

        # A short sleep prevents this polling loop from consuming 100% CPU.
        time.sleep_ms(10)


# MicroPython executes main.py directly after boot.py.
main()
