"""Reproducible, hardware-free demonstration using packaged synthetic telemetry."""

import argparse
import json
from importlib.resources import files
from pathlib import Path

import joblib
import pandas as pd

from ml.model import score_samples, train_model


def run_demo(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    training = pd.read_csv(files("tools").joinpath("data/training.csv"))
    evaluation = pd.read_csv(files("tools").joinpath("data/evaluation.csv"))
    model = train_model(training)
    scored = score_samples(model, evaluation)
    joblib.dump(model, output / "model.joblib")
    scored.to_csv(output / "predictions.csv", index=False)
    # The last five samples deliberately contain large injected faults.
    faults = int((scored.tail(5)["anomaly"] == "ANOMALY").sum())
    if faults != 5:
        raise RuntimeError(f"Demo detected {faults}/5 injected faults")
    summary = {
        "training_samples": len(training),
        "evaluation_samples": len(evaluation),
        "injected_faults_detected": faults,
        "total_anomalies": int((scored["anomaly"] == "ANOMALY").sum()),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="demo-output")
    args = parser.parse_args()
    print(json.dumps(run_demo(args.output), indent=2))


if __name__ == "__main__":
    main()
