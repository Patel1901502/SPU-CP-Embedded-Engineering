# Reusable firmware components

`main.py` composes and starts the service. Importing it does not start an infinite
loop or import `machine`. `board.create_service(settings, uart=None, sensors=None,
led=None)` creates only missing dependencies. Fully injected operation needs no
`machine` module. The caller owns injected objects; the service does not close them.

```python
from service import UARTService

service = UARTService(my_uart, my_sensors, my_led)
service.poll()  # schedule periodically; retains partial frames
# Or: service.run_forever(poll_interval_ms=10)
```

UART objects expose `any()`, `read()` returning bytes or None, and `write(bytes)`
returning a byte count. Sensor objects expose `read()` returning numeric telemetry
fields and `info()` returning JSON-compatible metadata. LED objects expose
`value(0 or 1)`. Command handling remains in the unchanged `protocol.py`.
UART writes that make no progress raise an I/O error to the caller. Oversized
commands are discarded through newline, then return `ERR COMMAND_TOO_LONG`.
Sensor/command errors remain one-line responses and subsequent commands continue.

## Board configuration

Edit `config.py` for UART ID/options (including optional tx/rx pins), LED pin,
CPU frequency, poll delay, maximum command length, sensor selection, I2C pins,
address, sampling period, and calibration. Copy **all device/*.py files** to the
MicroPython filesystem root. UART0 may share the REPL on some boards; select a
suitable UART and pins for your board. No change to command handling is required.
The original SensorSuite injected-I2C API and lazy initialization remain supported.

## Second hardware backend: analog temperature

Select `SENSOR_BACKEND = "analog"`. This backend accepts an ADC with `read_u16()`
and provides the same TELEMETRY and SENSOR_INFO commands as TMP102. Configure
ANALOG_TEMP_PIN and ANALOG_ADC_ATTEN for your board, then calibrate
ANALOG_FULL_SCALE_V, ANALOG_ZERO_C_V and ANALOG_VOLTS_PER_C against the ADC and
sensor. Defaults describe a linear 0.5 V zero-degree offset and 10 mV/degree
sensor model; they are not a claim of board ADC accuracy. Board ports without
`atten()` can inject an already configured ADC via AnalogSensorSuite instead.

Temperature is `(raw / 65535 * full_scale_v - zero_c_v) / volts_per_c`, followed
by the shared TEMP_SCALE and TEMP_OFFSET_C calibration. Only temperature is
reported; no vibration/current values are fabricated. Failed acquisition returns
an explicit sensor error; rate limiting uses wrap-safe ticks. Simulation remains
available through `SENSOR_BACKEND = "simulated"`.

## Validation

`python -m pytest -q` exercises injected UART framing, partial writes, malformed
and oversized command recovery, all three backends through unchanged command
handling, analog conversion, acquisition failure/recovery, and rate limiting.
Tests use fake hardware; flashing and electrical/ADC calibration require a board.
