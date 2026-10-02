"""Train and persist the telemetry anomaly-detection model."""

import argparse

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from features import feature_matrix


def main():
    """Parse CLI arguments, train IsolationForest, and save the model."""
    parser = argparse.ArgumentParser(
        description="Train an IsolationForest model on embedded telemetry."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="CSV containing temp_c, vibration, and current_ma columns.",
    )
    parser.add_argument(
        "--output",
        default="model.joblib",
        help="Destination path for the trained model (default: model.joblib).",
    )
    args = parser.parse_args()

    # Load telemetry and apply exactly the same feature engineering used later
    # by inference. Sharing feature_matrix() prevents training/serving skew.
    dataframe = pd.read_csv(args.input)
    features = feature_matrix(dataframe)

    # IsolationForest is a lightweight unsupervised anomaly detector. It works
    # well for this demo because labeled failure data is not required.
    # contamination=0.03 tells the model to expect roughly 3% anomalies.
    model = IsolationForest(
        n_estimators=100,
        contamination=0.03,
        random_state=42,
    )
    model.fit(features)

    # joblib serializes the trained scikit-learn model for later inference.
    joblib.dump(model, args.output)

    print(f"Training samples: {len(features)}")
    print(f"Features: {list(features.columns)}")
    print(f"Model saved to {args.output}")


if __name__ == "__main__":
    main()
