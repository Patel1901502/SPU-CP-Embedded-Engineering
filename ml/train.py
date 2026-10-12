"""Train a versioned anomaly detector and save its reproducibility metadata."""

import argparse
import json
from pathlib import Path

import pandas as pd

from ml.model import save_model, train_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="model.joblib")
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--contamination", type=float, default=0.03)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()
    model = train_model(
        pd.read_csv(args.input),
        n_estimators=args.n_estimators,
        contamination=args.contamination,
        random_state=args.random_state,
    )
    save_model(model, args.output)
    Path(str(args.output) + ".metadata.json").write_text(
        json.dumps(model.metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Training samples: {model.metadata['training_samples']}")
    print(f"Model saved to {args.output}")


if __name__ == "__main__":
    main()
