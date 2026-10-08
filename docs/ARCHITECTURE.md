# Architecture

`device/` is MicroPython firmware; it does not run in desktop CPython. It serves
newline-delimited UART commands via `device/protocol.py` and a simulated sensor
backend. `host/protocol.py` parses responses, `host/device.py` manages serial
ownership, and `host/telemetry.py` streams samples to CSV. `ml/features.py`
centralizes feature order; `ml/model.py` fits and scores IsolationForest.
Installed CLI scripts wrap these APIs. `embedded-demo` loads packaged synthetic
CSV files with importlib.resources, fits a deterministic model (seed 42), and
writes a model, scored CSV, and JSON summary.

The final five evaluation rows have injected high temperature, vibration, and
current. The demo must detect all five; total anomaly count can vary across
supported dependency versions. These synthetic results are a demonstration,
not a measure of real sensor accuracy. The model runs on the PC, not the MCU.

CI builds a wheel and source archive, replaces the source installation with the
wheel, and runs copied tests outside the checkout. This catches missing package
data and broken entry points. Firmware tests require a real board and are never
implicitly enabled in shared CI. Tagged release validation repeats the wheel
checks before publishing distributions, the demo asset, and SHA256 checksums.
