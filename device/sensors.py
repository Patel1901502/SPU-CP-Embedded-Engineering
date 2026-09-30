import math
import time

class SensorSuite:
    # Deterministic simulation; replace read() with real I2C/ADC sensors.
    def __init__(self):
        self.start_ms = time.ticks_ms()

    def read(self):
        elapsed_s = time.ticks_diff(time.ticks_ms(), self.start_ms) / 1000
        return {
            "temp_c": round(24.0 + 0.5 * math.sin(elapsed_s / 10), 3),
            "vibration": round(0.10 + 0.02 * math.sin(elapsed_s * 2), 4),
            "current_ma": round(80.0 + 5.0 * math.sin(elapsed_s / 5), 3),
        }
