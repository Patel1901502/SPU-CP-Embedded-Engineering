"""Sensor abstraction used by the ESP32 firmware.

The project intentionally uses deterministic simulated signals so it can be
run without external hardware. In a real product, ``SensorSuite.read`` would
be the boundary where I2C/SPI/ADC drivers are called.
"""

import math
import time


class SensorSuite:
    """Provide a single interface for all monitored sensor measurements."""

    def __init__(self):
        # ticks_ms() is preferred over wall-clock time on MicroPython because
        # it is monotonic and designed to work correctly across tick wraparound.
        self.start_ms = time.ticks_ms()

    def read(self):
        """Return one snapshot of temperature, vibration, and current.

        The sine waves make the values change slowly and predictably, which is
        useful for demos and automated host testing. Replace these expressions
        with real sensor-driver calls when hardware is available.
        """
        elapsed_ms = time.ticks_diff(time.ticks_ms(), self.start_ms)
        elapsed_s = elapsed_ms / 1000.0

        # Simulated temperature: approximately 24 C with a slow +/-0.5 C drift.
        temperature_c = 24.0 + 0.5 * math.sin(elapsed_s / 10.0)

        # Simulated vibration: small periodic movement around a 0.10 baseline.
        vibration = 0.10 + 0.02 * math.sin(elapsed_s * 2.0)

        # Simulated load current: approximately 80 mA with +/-5 mA variation.
        current_ma = 80.0 + 5.0 * math.sin(elapsed_s / 5.0)

        # Round values before transmission to keep UART messages compact and
        # stable while still retaining useful precision.
        return {
            "temp_c": round(temperature_c, 3),
            "vibration": round(vibration, 4),
            "current_ma": round(current_ma, 3),
        }
