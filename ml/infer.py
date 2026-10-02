"""Run anomaly detection on telemetry using a previously trained model."""

import argparse

import joblib
import pandas as pd

from features import feature_matrix


def main():
    """Load model/data, classify each sample, and print anomaly results."""
    parser = argparse.ArgumentParser(
        description="Detect anomalous embedded telemetry samples."
    )
    parser.add_argument("--model", required=True, help="Path to model.joblib.")
    parser.add_argument("--input", required=True, help="Telemetry CSV to score.")
    args = parser.parse_args()

    # Load the fitted model and transform input telemetry using the same feature
    # pipeline used during training.
    model = joblib.load(args.model)
    dataframe = pd.read_csv(args.input)
    features = feature_matrix(dataframe)

    # IsolationForest predicts +1 for inliers and -1 for anomalies.
    predictions = model.predict(features)

    # decision_function provides a continuous score. Lower/more-negative values
    # indicate samples that the model considers more unusual.
    scores = model.decision_function(features)

    output = dataframe.copy()
    output["anomaly"] = pd.Series(predictions).map({1: "NORMAL", -1: "ANOMALY"})
    output["score"] = scores

    display_columns = [
        "temp_c",
        "vibration",
        "current_ma",
        "anomaly",
        "score",
    ]
    print(output[display_columns].to_string(index=False))
    print(f"Anomalies detected: {(predictions == -1).sum()} / {len(predictions)}")


if __name__ == "__main__":
    main()
