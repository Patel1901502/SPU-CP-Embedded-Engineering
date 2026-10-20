# Real Sensor Integration — TMP102

## Implementation and remaining hardware acceptance

Implemented: I2C temperature driver, default hardware backend, calibration,
explicit read faults, rate limiting, capture CLI and provenance manifests.
**Not completed here:** physical board verification and recording an actual real
telemetry dataset. No sensor/serial hardware is available in this environment.
No real-data CSV is claimed or fabricated. Complete acceptance using the steps below.

## Wiring (classic ESP32 DevKit, TMP102 breakout)

Power off before wiring. Use a 3.3 V compatible TMP102 breakout.

| ESP32 | TMP102 breakout | Purpose |
|---|---|---|
| 3V3 | V+ / VCC | 3.3 V supply |
| GND | GND | Common ground |
| GPIO21 | SDA | I2C data |
| GPIO22 | SCL | I2C clock |
| GND | ADD0 | Select 7-bit address 0x48 |
| unconnected | ALERT | Unused |

SDA/SCL need pull-ups to **3.3 V**, typically 4.7 kOhm; many breakouts
already include them. Do not pull ESP32 IO up to 5 V. A bare IC also requires
local supply decoupling per TI's reference circuit. Check your board pinout:
ESP32-C3/S3 and other variants may need different GPIO and I2C configuration.

## Driver, units, limits and calibration

Source: [TI TMP102 datasheet](https://www.ti.com/lit/ds/symlink/tmp102.pdf).
Normal mode uses signed 12-bit readings with 0.0625 degree C per count;
resolution is not accuracy. Consult the datasheet for accuracy over temperature.
The driver sets continuous conversion at 4 Hz, normal mode, and waits 300 ms
before the first read. Valid physical readings are -40 to 125 degrees C.
100 kHz I2C is the default. Requests are command-driven, not background samples.

Edit `device/config.py` before copying firmware:

- `SENSOR_BACKEND = "tmp102"` (default). `"simulated"` explicitly enables demos.
- `I2C_ID`, `I2C_SDA_PIN`, `I2C_SCL_PIN`, `I2C_FREQ_HZ`, `TMP102_ADDRESS`.
- `SAMPLE_PERIOD_MS = 1000` (minimum 250 ms; faster reads cannot provide new conversions).
- `TEMP_SCALE = 1.0`, `TEMP_OFFSET_C = 0.0`.

`temp_c = raw_temp_c * TEMP_SCALE + TEMP_OFFSET_C`. Both columns use degrees C.
Use a stable reference thermometer at thermal equilibrium. For one-point
calibration keep scale 1 and set offset to reference minus raw reading.
For two points, scale = (reference2-reference1)/(raw2-raw1), then offset =
reference1-scale*raw1. Record reference equipment and conditions separately.
Scale must be positive and both parameters finite. Restart after configuration
changes. SENSOR_INFO reports the active calibration, wiring and period.

## Faults and protocol

`TELEMETRY` returns `TEL temp_c=...,raw_temp_c=...` only after a successful read.
There are no invented current or vibration fields. Bus NACK/disconnect, short
reads, mode mismatch or out-of-range values return `ERR SENSOR=...`.
Too-frequent requests return `ERR SENSOR=RATE_LIMIT`; no stale value is reused.
A failed driver is reinitialized on the next allowed request, allowing reconnect.
PING/STATUS indicate UART service availability, not sensor health; use TELEMETRY
for a live health check. SENSOR_INFO returns `INFO {JSON}` identifying hardware
or simulation. Initialization is lazy so a missing sensor does not stop UART.
Host collection aborts visibly on ERR rather than silently discarding faults.

## Record the real dataset

Install project and flash all five device files using README instructions.
Close serial monitors/mpremote so only this host owns the port. The firmware
uses UART0, which may conflict with the MicroPython REPL; follow troubleshooting.

```sh
embedded-record-real --port COM5 --seconds 120 --interval 1 --output real-telemetry.csv
python -m pytest tests/hardware -q --hardware --port COM5
```

Use a fresh output path. The recorder refuses simulation, verifies columns and
finite values, and writes `real-telemetry.csv.json` with source, calibration,
UTC start/end times, sample count and CSV SHA256. CSV timestamps are host Unix
seconds at reception, not sensor acquisition time. USB latency, conversion and
request overhead affect timing; interval is a delay between requests, not a
precision clock. Failures/interrupts leave partial rows plus `complete: false`
and an error in the manifest; the command exits unsuccessfully.

Acceptance: capture a stable baseline, gently warm the sensor, observe a change,
and compare to a reference. Disconnect SDA and confirm an explicit fault and an
incomplete manifest; reconnect and capture to a new path. Preserve CSV, manifest,
board/firmware version, reference and environmental notes. A successful manifest
records the configured backend; it is not independent physical attestation.

The existing ML pipeline requires temperature, vibration and current. These
real temperature-only data are intentionally incompatible; retrain a separate
model with appropriate temperature-only features or add actual sensors for the
other channels. Synthetic demo datasets remain explicitly synthetic.
