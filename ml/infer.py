"""Run anomaly detection on telemetry using a previously trained model."""

import argparse

import joblib
import pandas as pd

from ml.model import score_samples


def main():
    """Load model/data, classify each sample, and print anomaly results."""
    parser = argparse.ArgumentParser(description="Detect anomalous embedded telemetry samples.")
    parser.add_argument("--model", required=True, help="Path to model.joblib.")
    parser.add_argument("--input", required=True, help="Telemetry CSV to score.")
    args = parser.parse_args()

    # Load the fitted model and transform input telemetry using the same feature
    # pipeline used during training.
    model = joblib.load(args.model)
    dataframe = pd.read_csv(args.input)
    output = score_samples(model, dataframe)

    display_columns = [
        "temp_c",
        "vibration",
        "current_ma",
        "anomaly",
        "score",
    ]
    print(output[display_columns].to_string(index=False))
    print(f"Anomalies detected: {(output['anomaly'] == 'ANOMALY').sum()} / {len(output)}")


if __name__ == "__main__":
    main()
