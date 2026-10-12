"""Score telemetry and optionally export all original columns, delta and scores."""

import argparse

import pandas as pd

from ml.model import InferenceSession, load_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", help="Scored CSV destination")
    parser.add_argument("--batch-size", type=int, help="Rows per ordered inference batch")
    parser.add_argument("--previous-temp", type=float, help="Last temperature of same stream")
    args = parser.parse_args()
    if args.batch_size is not None and args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    dataframe = pd.read_csv(args.input)
    session = InferenceSession(load_model(args.model), previous_temp=args.previous_temp)
    size = args.batch_size or max(len(dataframe), 1)
    if dataframe.empty:
        parser.error("input must contain telemetry rows")
    output = pd.concat(
        [
            session.score(dataframe.iloc[start : start + size])
            for start in range(0, len(dataframe), size)
        ]
    )
    if args.output:
        output.to_csv(args.output, index=False)
    print(output.to_string(index=False))
    print(f"Anomalies detected: {(output['anomaly'] == 'ANOMALY').sum()} / {len(output)}")


if __name__ == "__main__":
    main()
