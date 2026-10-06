# ESP32 Python + Tiny ML Embedded Monitoring Platform

GitHub-ready portfolio project combining Python-first ESP32 MicroPython firmware, UART telemetry, pytest, and lightweight scikit-learn anomaly detection.

## Architecture
PC Python -> USB/UART -> ESP32 MicroPython -> sensors/GPIO
PC Python also performs feature extraction and IsolationForest anomaly detection.

## Layout
- `device/`: MicroPython firmware
- `host/`: Python serial/device API
- `ml/`: feature engineering, training, inference
- `tests/`: pytest unit/mock/ML tests
- `tools/`: device CLI

## Hardware
ESP32 development board + USB cable. External sensors are optional; the included firmware uses a deterministic simulated sensor backend. Replace `device/sensors.py` with I2C/ADC sensor reads for real hardware.

## ESP32
Install MicroPython, then copy:
```bash
mpremote connect COM5 cp device/*.py :
```
Linux/macOS:
```bash
mpremote connect /dev/ttyUSB0 cp device/*.py :
```

## Python
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Train ML model
```bash
python -m ml.train --input telemetry.csv --output model.joblib
python -m ml.infer --model model.joblib --input telemetry.csv
```

The model uses an IsolationForest on temperature, vibration, current, and temperature delta. It is deliberately lightweight and demonstrates an embedded-monitoring ML pipeline rather than requiring neural-network deployment on the MCU.

## CLI
```bash
python -m tools.cli --port COM5 ping
python -m tools.cli --port COM5 status
python -m tools.cli --port COM5 telemetry
python -m tools.cli --port COM5 collect --seconds 60 --output telemetry.csv
```

## UART commands
`PING`, `STATUS`, `TELEMETRY`, `LED ON`, `LED OFF`

## Engineering flow
Sensor -> embedded acquisition -> UART telemetry -> Python collection -> feature extraction -> ML anomaly detection -> automated tests -> CI.

## Resume bullet
> Built a Python-first ESP32 embedded monitoring platform using MicroPython, UART telemetry, automated pytest validation, and a lightweight scikit-learn anomaly-detection pipeline to identify abnormal temperature, vibration, and current behavior; integrated testing and ML training into GitHub Actions CI.

## Reusing the components

```python
from host.device import EmbeddedDevice
from host.telemetry import iter_samples, save_csv
from ml.model import train_model, score_samples
import pandas as pd

with EmbeddedDevice("COM5") as device:
    save_csv(iter_samples(device, seconds=60, interval=0.5), "telemetry.csv")

frame = pd.read_csv("telemetry.csv")
model = train_model(frame, contamination=0.05, n_estimators=200)
scored = score_samples(model, frame)
```

An alternative transport can be supplied with `EmbeddedDevice(transport=adapter)`.
The adapter implements `write(bytes)`, `readline()` returning bytes, and `close()`.
Injected adapters remain caller-owned; set `close_transport=True` to transfer
ownership to the client. Existing `EmbeddedDevice(port)` calls still work.

`iter_samples` accepts `clock`, `timestamp`, and `sleep` functions for deterministic
tests. It never mutates the device's response dictionary. `collect` remains available
when a list is needed. `save_csv` accepts generators and avoids buffering all rows.

Installed entry points: `embedded-device`, `embedded-train`, `embedded-infer`.
Use module invocation (`python -m ...`) from the project root without installation.
Firmware deployment remains unchanged; this refactor targets host acquisition and ML.
Hardware validation on an ESP32 is still required. No sample dataset or CI workflow
is bundled in this archive; collect telemetry before running the training example.
