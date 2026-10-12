# Local milestone verification

Verified using Python 3.12 and the core dependency versions in
requirements-ml-reproducible.txt.

- Source installation: 27 tests passed, 3 hardware tests skipped.
- Built wheel installed and tested outside checkout: 27 passed, 3 skipped.
- Ruff lint and format checks passed.
- Wheel and source distribution built successfully.
- Demo: 200 training rows, 40 independent evaluation rows, 5/5 injected
  anomalies detected, 5 total anomalies (zero false positives in this fixture).

No hardware run or remote GitHub Actions run was performed. Metrics describe
synthetic fixtures and do not estimate production detector performance.
