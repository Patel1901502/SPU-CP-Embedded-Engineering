# Troubleshooting

- CLI missing: activate your virtual environment and install `.[dev]`. Use
  `python -m tools.demo` for diagnosis from the project root.
- Import errors: use Python 3.10 or later, run `python -m pip check`, and confirm
  the interpreter belongs to your environment. Do not name scripts `serial.py`.
- Serial permission errors: verify the port and Linux dialout permissions.
  Close mpremote and serial terminals before opening the device CLI.
- Timeouts or unknown responses: confirm 115200 baud, deploy all five device
  files, and reset the board. UART0 shares the MicroPython console on many
  ESP32s: boot text or REPL output can interfere. Use a dedicated UART with a
  USB-UART adapter if your board cannot reliably serve this application over
  UART0. Wiring, GPIO selection, and transport changes depend on the board.
- Hardware suite skipped: use `--hardware --port COM5`; missing port is an error.
  The suite does not flash firmware or control LEDs.
- Demo data missing after installation: reinstall the built wheel; package data
  must contain `tools/data/training.csv` and `evaluation.csv`.
- Model files: load only models you trust; joblib deserialization executes code.
  Retrain after changing feature order or scikit-learn version.
- Release failure: ensure tag equals package version, Actions has permission to
  write contents, and the tag points to the validated commit. The workflow
  publishes on GitHub, not PyPI. Check Actions logs before retrying.
