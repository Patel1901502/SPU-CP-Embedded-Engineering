# Reproducible ML milestone verification

Verified on Python 3.12 with the core versions recorded in the saved model metadata.

- Full test suite: 44 passed, 4 skipped (opt-in hardware tests).
- Ruff lint and formatting checks passed.
- Wheel built successfully and includes both training and evaluation CSV fixtures.
- Saved-model reload and seven-row batch scores match full-recording scores exactly.
- Repeated seeded training and CSV export are covered by automated tests.

## Separate evaluation recording

Training: 200 synthetic normal rows (seed 42). Evaluation: 40 separately seeded
rows (seed 2026), including five injected faults; no evaluation data is fitted.

| Metric | Result |
| --- | --- |
| True negatives | 35 |
| False positives | 0 |
| False negatives | 0 |
| True positives | 5 |
| Precision | 1.0 |
| Recall | 1.0 |
| F1 | 1.0 |
| ROC AUC | 1.0 |

Evidence is in `milestone-evidence/`. These synthetic faults verify pipeline
behavior and do not estimate production detector accuracy. No hardware or remote
GitHub Actions run was performed.
