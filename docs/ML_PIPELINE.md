# v1.4 — Reproducible ML Pipeline

All five milestone requirements are implemented. This increment retains the
existing package version 2.0.0 and release workflow; v1.4 names the requested
milestone, not a downgrade of the package version.

## Reproduce training, evaluation, and export

After `python -m pip install ".[dev]"`, run from the project directory:

```sh
embedded-train --input tools/data/training.csv --output model.joblib --n-estimators 100 --contamination 0.03 --random-state 42
embedded-evaluate --model model.joblib --input tools/data/evaluation.csv --output evaluation-scored.csv --metrics metrics.json
embedded-infer --model model.joblib --input tools/data/evaluation.csv --batch-size 7 --output predictions.csv
embedded-demo --output demo-output
```

Training has 200 normal synthetic rows; evaluation is a separately seeded
40-row recording with five injected faults (`is_anomaly=1`). Evaluation never
fits or tunes the estimator. Metrics include TP/TN/FP/FN, precision, recall, F1,
and ROC AUC (lower decision scores mean more anomalous). Both label classes are
required; 0 means normal, 1 means anomaly. Custom labels use `--label-column`.
These easy synthetic faults demonstrate plumbing, not production accuracy.
Use independently collected labeled telemetry to assess real deployment.

`python -m tools.generate_data` regenerates the checked-in fixtures (training
seed 42, evaluation seed 2026). The included `requirements-ml-reproducible.txt` pins the locally verified core
versions. Install with `python -m pip install -r requirements-ml-reproducible.txt`
when using Python 3.12 to match that environment. Preserve exact dataset bytes and dependency
versions for repeated experiments. The model is deterministic for a fixed
integer seed, input row order, parameters, and software environment; numerical
identity across library versions or platforms is not promised.

## Input contract

Required columns: `temp_c`, `vibration`, `current_ma`. Nonempty input, unique
column names and finite numeric readings are mandatory. Numeric strings are
accepted. Missing columns, nulls, NaN, infinity and nonnumeric values raise
clear ValueErrors; values are never silently filled or dropped. Extra columns
(such as timestamps and ground-truth labels) are preserved in scored output
but never enter training. Existing `temp_delta`, `anomaly`, and `score` columns
are overwritten with freshly computed results. Rows remain in supplied order;
callers must separate devices and recordings and order samples chronologically.

## Saved artifact

The joblib file contains a `ModelArtifact` with the fitted estimator and:

- Schema version and ordered features: temp_c, vibration, current_ma, temp_delta.
- All estimator parameters, including seed, contamination and n_estimators.
- Training row count and SHA-256 of the canonical feature CSV.
- Temperature-delta policy, Python version and core dependency versions.

Training also writes `<model path>.metadata.json` for inspection. Inference uses
the artifact's feature order and checks it against estimator feature names.
Legacy bare estimators are rejected with instructions to retrain. Only load
trusted joblib files, because loading them can execute code. The data hash
fingerprints transformed training data; it is not a security signature.

## Temperature delta across batches

For an independent recording, the first row gets delta=0. Subsequent rows get
current temperature minus previous row temperature. `score_samples(model, df)`
starts a fresh recording each call. Pass `previous_temp=` only to continue the
same ordered stream, or use `InferenceSession(model).score(batch)` to carry
state automatically. `session.reset()` starts a new recording. Invalid batches
do not change session state; empty batches are rejected. Each device/recording
needs its own session. Do not bridge a data gap or different device implicitly.

The CLI's `--batch-size` carries state within one input file: batch size does
not change features, labels or scores. `--previous-temp` explicitly continues
from a previous file. Separate CLI invocations otherwise start at delta=0.
The CLI currently loads input and output in memory; batch size controls
inference boundaries, not total CSV memory consumption. Scored CSV exports all
input columns plus temp_delta, anomaly and score, without a pandas index.

## Verification

`python -m pytest -q` covers malformed input, serialization, repeatability,
column ordering, held-out evaluation, stream reset and failure behavior, and
installed CLI CSV exports. `ruff check .` and `ruff format --check .` verify
style. Existing CI installs a built wheel outside the checkout and runs the
same suite. The hardware-free demo exports model metadata and evaluation
metrics as well as model, predictions and summary.

## Completion evidence

The source now includes both seeded CSV fixtures; `.gitignore` explicitly retains
`tools/data/*.csv` so future repository exports preserve them. The demo reloads
the saved model and asserts exact DataFrame equality for full-recording and
seven-row batch inference. Metadata validation also rejects missing reproducibility
fields and estimator parameters that disagree with the saved configuration.

`milestone-evidence/` contains the saved model, metadata, scored CSV, metrics,
and consistency summary from the verified demo. Regenerate it with
`embedded-demo --output milestone-evidence`.
