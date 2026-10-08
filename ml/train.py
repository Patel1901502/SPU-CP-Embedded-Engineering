"""Train and persist the telemetry anomaly-detection model."""

import argparse

import joblib
import pandas as pd

from ml.features import FEATURE_COLUMNS
from ml.model import train_model


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
    model = train_model(dataframe)

    # joblib serializes the trained scikit-learn model for later inference.
    joblib.dump(model, args.output)

    print(f"Training samples: {len(dataframe)}")
    print(f"Features: {FEATURE_COLUMNS}")
    print(f"Model saved to {args.output}")


if __name__ == "__main__":
    main()
