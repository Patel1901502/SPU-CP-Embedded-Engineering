# ESP32 Python + ML Embedded Monitoring — v2.0.0

Python host tools, MicroPython ESP32 firmware, and lightweight PC-side anomaly
 detection. A hardware-free demonstration is included.

## Fresh setup

Use Python 3.10+ (CI checks 3.10, 3.12, 3.13 on Linux and Windows).
From the extracted project directory:

```sh
python -m venv .venv
```

Activate with `source .venv/bin/activate` on Linux/macOS, or
`.venv\Scripts\Activate.ps1` in Windows PowerShell.

```sh
python -m pip install --upgrade pip
python -m pip install ".[dev]"
python -m pip check
ruff check .
ruff format --check .
python -m pytest -q
embedded-demo --output demo-output
```

Expected demo summary: 200 training samples, 40 evaluation samples, and
`injected_faults_detected: 5`. The command checks all five injected faults and
writes `model.joblib`, `predictions.csv`, and `summary.json`. Total anomalies may
vary with dependency versions. Input data in `tools/data/` is synthetic; no board,
network service, or previously collected telemetry is needed.

## Validate distributable installation

```sh
python -m build
python -m twine check dist/*
```

Create a second clean virtual environment, install the generated wheel from
`dist/` using its full path, then run `embedded-demo` from another directory.
CI performs this outside-checkout wheel verification and tests all installed
entry points. A source installation cannot substitute for this check.

## CLI and training

```sh
embedded-device --port COM5 ping
embedded-device --port COM5 status
embedded-device --port COM5 collect --seconds 60 --output telemetry.csv
embedded-train --input tools/data/training.csv --output model.joblib
embedded-infer --model model.joblib --input tools/data/evaluation.csv
```

Replace COM5 with your port. Every command supports `--help`.
`embedded-demo` demonstrates ML without hardware. See
[architecture](docs/ARCHITECTURE.md) and [troubleshooting](docs/TROUBLESHOOTING.md).

## ESP32 setup and opt-in integration checks

Install MicroPython appropriate for your ESP32 board, then install `mpremote`
on the PC (`python -m pip install mpremote`). Copy each firmware file explicitly
so the command also works in PowerShell:

```sh
mpremote connect COM5 cp device/boot.py device/config.py device/main.py device/protocol.py device/sensors.py :
```

Reset the board and close mpremote before testing. Confirm the LED pin in
`device/config.py`. The default sensor backend is simulated. UART0/USB console
sharing depends on the board; see troubleshooting if it returns boot/REPL text.

```sh
python -m pytest tests/hardware -q --hardware --port COM5
```

Tests check PING, READY status, and finite telemetry. They are skipped by default;
`--hardware` without `--port` fails explicitly. No real ESP32 was available for
local verification. Firmware deployment and board validation are manual.

## Publish the release

Commit this project, including `.github/workflows`, to your GitHub repository.
Wait for automated validation to pass, then run:

```sh
git tag -a v2.0.0 -m "v2.0.0 Automated Validation and Release"
git push origin v2.0.0
```

The tagged workflow validates the built wheel before creating the GitHub release
with wheel, source distribution, synthetic datasets, demo output, docs, and
checksums. GitHub Actions requires contents-write permission. The ZIP prepares
this release; it does not itself push a tag or publish on GitHub.

## Reusable APIs

`EmbeddedDevice(transport=adapter)` accepts write/readline/close transports.
Injected transports remain caller-owned unless `close_transport=True`.
`iter_samples` streams telemetry, and `save_csv` accepts generators.
`train_model` and `score_samples` share feature engineering and preserve inputs.
