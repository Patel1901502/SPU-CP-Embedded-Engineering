"""MicroPython entry point; reusable components live outside this module."""

import config
from board import create_service


def main(uart=None, sensors=None, led=None, settings=config):
    service = create_service(settings, uart=uart, sensors=sensors, led=led)
    service.run_forever(settings.UART_POLL_INTERVAL_MS)


if __name__ == "__main__":
    main()
