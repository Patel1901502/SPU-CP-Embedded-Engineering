import time
from machine import Pin, UART
import config
from protocol import handle_command
from sensors import SensorSuite

def main():
    uart = UART(0, baudrate=config.UART_BAUDRATE)
    led = Pin(config.LED_PIN, Pin.OUT)
    sensors = SensorSuite()
    buffer = b""
    while True:
        if uart.any():
            buffer += uart.read()
            while b"\n" in buffer:
                raw, buffer = buffer.split(b"\n", 1)
                try:
                    response = handle_command(raw.decode().strip(), sensors, led)
                    uart.write(response + "\r\n")
                except Exception as exc:
                    uart.write("ERR INTERNAL={}\r\n".format(exc))
        time.sleep_ms(10)

main()
