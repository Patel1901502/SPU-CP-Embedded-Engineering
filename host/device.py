import serial
from .protocol import parse_response

class EmbeddedDevice:
    def __init__(self, port, baudrate=115200, timeout=1.0):
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    def close(self):
        self.serial.close()
    def __enter__(self):
        return self
    def __exit__(self, *_):
        self.close()
    def command(self, command):
        self.serial.write((command + "\n").encode())
        response = self.serial.readline().decode(errors="replace")
        if not response:
            raise TimeoutError(f"No response to {command}")
        return parse_response(response)
    def ping(self):
        return self.command("PING")["type"] == "pong"
    def status(self):
        return self.command("STATUS")
    def telemetry(self):
        return self.command("TELEMETRY")
    def led(self, state):
        return self.command("LED ON" if state else "LED OFF")
