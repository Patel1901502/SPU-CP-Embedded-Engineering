# v2.0.0 — Automated Validation and Release

Adds Linux/Windows CI on Python 3.10, 3.12, and 3.13; Ruff lint/format checks;
wheel/source build validation; installed CLI and reproducible demo tests;
explicitly opt-in ESP32 integration tests; packaged synthetic training/evaluation
data; setup, architecture, and troubleshooting documentation; and a tag-triggered
GitHub release workflow with distributions, demo output, and SHA256 checksums.

Hardware tests require a flashed ESP32 and were not run in the build environment.
The included sensor backend and demo data are simulated. No real sensor accuracy
or on-device ML performance is claimed.
