# Real Sensor Integration validation

Local validation: Python 3.12, 20 October 2026.

- 42 automated tests passed; four hardware checks skipped (no serial hardware).
- Ruff lint and formatting checks passed.
- Built and installed the project wheel; CLI help, existing ML demo and pipeline
  checks pass. The new `embedded-record-real` CLI is included.
- Injected I2C tests cover positive/negative conversion, driver configuration,
  calibration, invalid configuration, short/malformed reads, range checks,
  rate limits, fault reporting and reconnect.
- Capture tests cover rejecting simulation, metadata/hash output, preserving
  existing captures and retaining partial rows with an explicit failure state.
- Restored missing synthetic demo fixtures using `tools/generate_data.py`.
  These fixtures are not real measurements.

Not validated: electrical wiring, behavior on actual MicroPython/ESP32 hardware,
reference-temperature accuracy, or physical disconnect/reconnect. No genuine
sensor dataset was collected. Follow REAL_SENSOR.md to complete these steps.
