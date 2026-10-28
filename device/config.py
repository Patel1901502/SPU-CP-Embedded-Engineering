"""Central configuration for the ESP32 firmware.

Keeping board/application constants in one module makes hardware changes easy
without scattering magic numbers throughout the firmware.
"""

# UART speed used by both the ESP32 firmware and the host-side Python client.
UART_BAUDRATE = 115200

# GPIO connected to the board's status LED on many ESP32 development boards.
# Change this value if your board uses a different pin.
LED_PIN = 2

# Minimum interval between real sensor requests in milliseconds.
# Sampling is command-driven; requests faster than this return RATE_LIMIT.
SAMPLE_PERIOD_MS = 1000


# Real hardware is the default; simulation must be selected explicitly.
SENSOR_BACKEND = "tmp102"  # "tmp102" or "simulated"
I2C_ID = 0
I2C_SDA_PIN = 21
I2C_SCL_PIN = 22
I2C_FREQ_HZ = 100000
TMP102_ADDRESS = 0x48
# calibrated_c = raw_c * TEMP_SCALE + TEMP_OFFSET_C
TEMP_SCALE = 1.0
TEMP_OFFSET_C = 0.0

# Board composition settings. UART_OPTIONS may also specify tx/rx pins.
UART_ID = 0
UART_OPTIONS = {"baudrate": UART_BAUDRATE}
UART_POLL_INTERVAL_MS = 10
UART_MAX_COMMAND_BYTES = 256
CPU_FREQ_HZ = 160_000_000

# Optional linear analog temperature sensor (select SENSOR_BACKEND = "analog").
# ESP32 ADC attenuation constant 3; adapt for your board's ADC implementation.
ANALOG_TEMP_PIN = 34
ANALOG_ADC_ATTEN = 3
# Calibrate these against the board ADC and sensor before using measurements.
ANALOG_FULL_SCALE_V = 3.3
ANALOG_VOLTS_PER_C = 0.01
ANALOG_ZERO_C_V = 0.5
