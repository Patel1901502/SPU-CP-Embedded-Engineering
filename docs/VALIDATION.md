# Local verification — 2026-10-08

A fresh isolated virtual environment installed the built v2.0.0 wheel and its
runtime dependencies. Tests were copied outside the source checkout and executed
with importlib mode. No PYTHONPATH override or editable installation was used.

- CPython 3.12.14: 16 tests passed; 3 hardware tests skipped.
- All four installed CLI help commands passed; training/inference CLI round trip passed.
- Installed demo: 200 training rows, 40 evaluation rows, all 5 injected faults
  detected, 8 total anomalies. Demo writes model, predictions, and JSON summary.
- Explicit hardware opt-in without a port returned pytest usage error (exit 4).
- Ruff lint and formatting passed.
- Wheel and source distribution built successfully; Twine checks passed without warnings.
- Fresh environment `pip check` reported no broken requirements.
- Workflow YAML parsed successfully; remote GitHub Actions runs have not occurred.

Verified dependency versions: numpy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1,
pyserial 3.5, joblib 1.6.0, pytest 9.1.1. The workflow also targets Windows and
Python 3.10/3.13; those environments were not locally executed.

## Milestone status

Implementation and the documented fresh-install demo are verified locally.
Real ESP32 integration remains unverified. The GitHub release is prepared but
not published: commit the changes, pass CI, and push tag v2.0.0 as documented.
The milestone's publication item is complete only after that workflow succeeds.
