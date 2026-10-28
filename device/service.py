"""Board-independent newline-delimited UART service; no hardware setup."""

from protocol import handle_command


class UARTService:
    """Injected UART: any/read/write; sensors: read/info; LED: value.

    Call poll() from a scheduler or run_forever() for a blocking service.
    Oversized frames are discarded through the next newline to resynchronize.
    """

    def __init__(self, uart, sensors, led, max_command_bytes=256):
        if max_command_bytes < 1:
            raise ValueError("max_command_bytes must be positive")
        self.uart = uart
        self.sensors = sensors
        self.led = led
        self.max_command_bytes = max_command_bytes
        self.buffer = bytearray()
        self.discarding = False

    def poll(self):
        """Process available input once, preserving partial frames between calls."""
        if not self.uart.any():
            return
        incoming = self.uart.read()
        if not incoming:
            return
        for byte in incoming:
            if byte == 10:
                if self.discarding:
                    response = "ERR COMMAND_TOO_LONG"
                else:
                    try:
                        response = handle_command(
                            self.buffer.decode().strip(), self.sensors, self.led
                        )
                    except Exception as exc:
                        response = "ERR INTERNAL=" + str(exc).replace("\r", " ").replace("\n", " ")
                self.buffer = bytearray()
                self.discarding = False
                self._write(response + "\r\n")
            elif not self.discarding:
                if len(self.buffer) >= self.max_command_bytes:
                    self.buffer = bytearray()
                    self.discarding = True
                else:
                    self.buffer.append(byte)

    def _write(self, response):
        data = response.encode()
        while data:
            written = self.uart.write(data)
            if written is None or written <= 0 or written > len(data):
                raise OSError("UART_WRITE_FAILED")
            data = data[written:]

    def run_forever(self, poll_interval_ms=10, sleep_ms=None):
        if poll_interval_ms < 0:
            raise ValueError("poll_interval_ms must be nonnegative")
        if sleep_ms is None:
            from time import sleep_ms
        while True:
            self.poll()
            sleep_ms(poll_interval_ms)
