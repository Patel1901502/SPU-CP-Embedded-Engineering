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
- `data/`: sample telemetry
- `.github/workflows/`: CI

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
python ml/train.py --input data/sample_telemetry.csv --output model.joblib
python ml/infer.py --model model.joblib --input data/sample_telemetry.csv
```

The model uses an IsolationForest on temperature, vibration, current, and temperature delta. It is deliberately lightweight and demonstrates an embedded-monitoring ML pipeline rather than requiring neural-network deployment on the MCU.

## CLI
```bash
python tools/cli.py --port COM5 ping
python tools/cli.py --port COM5 status
python tools/cli.py --port COM5 telemetry
python tools/cli.py --port COM5 collect --seconds 60 --output telemetry.csv
```

## UART commands
`PING`, `STATUS`, `TELEMETRY`, `LED ON`, `LED OFF`

## Engineering flow
Sensor -> embedded acquisition -> UART telemetry -> Python collection -> feature extraction -> ML anomaly detection -> automated tests -> CI.

## Resume bullet
> Built a Python-first ESP32 embedded monitoring platform using MicroPython, UART telemetry, automated pytest validation, and a lightweight scikit-learn anomaly-detection pipeline to identify abnormal temperature, vibration, and current behavior; integrated testing and ML training into GitHub Actions CI.
