"""Regenerate synthetic fixtures with separate seeded training/evaluation streams."""

from pathlib import Path

import numpy as np
import pandas as pd


def recording(count, seed):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "timestamp": np.arange(count),
            "temp_c": 24 + np.cumsum(rng.normal(0, 0.03, count)),
            "vibration": rng.normal(0.10, 0.005, count),
            "current_ma": rng.normal(80, 1, count),
        }
    )


def generate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    training = recording(200, 42)
    evaluation = recording(40, 2026)
    evaluation["is_anomaly"] = 0
    evaluation.loc[35:, ["temp_c", "vibration", "current_ma"]] = [90, 8, 900]
    evaluation.loc[35:, "is_anomaly"] = 1
    training.to_csv(output / "training.csv", index=False, float_format="%.8f")
    evaluation.to_csv(output / "evaluation.csv", index=False, float_format="%.8f")


if __name__ == "__main__":
    generate(Path(__file__).parent / "data")
