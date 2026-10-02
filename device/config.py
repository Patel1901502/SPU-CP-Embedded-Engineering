"""Central configuration for the ESP32 firmware.

Keeping board/application constants in one module makes hardware changes easy
without scattering magic numbers throughout the firmware.
"""

# UART speed used by both the ESP32 firmware and the host-side Python client.
UART_BAUDRATE = 115200

# GPIO connected to the board's status LED on many ESP32 development boards.
# Change this value if your board uses a different pin.
LED_PIN = 2

# Nominal sensor sampling period in milliseconds. The current command-driven
# demo reads sensors on demand, but this constant is useful when extending the
# firmware to periodic/background telemetry.
SAMPLE_PERIOD_MS = 1000
