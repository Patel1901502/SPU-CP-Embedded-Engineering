"""Validated, ordered telemetry features. Row order is acquisition order."""

import numpy as np
import pandas as pd

INPUT_COLUMNS = ["temp_c", "vibration", "current_ma"]
FEATURE_COLUMNS = [*INPUT_COLUMNS, "temp_delta"]


def validate_telemetry(df):
    """Reject empty, duplicate-column, missing, nonnumeric or nonfinite inputs."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("telemetry must be a nonempty DataFrame")
    if not df.columns.is_unique:
        raise ValueError("telemetry columns must be unique")
    missing = [name for name in INPUT_COLUMNS if name not in df]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    result = df.copy()
    for name in INPUT_COLUMNS:
        try:
            result[name] = pd.to_numeric(df[name], errors="raise").astype(float)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{name} must contain numeric values") from exc
        if not np.isfinite(result[name].to_numpy()).all():
            raise ValueError(f"{name} contains missing or nonfinite values")
    return result


def add_features(df, *, previous_temp=None):
    """First delta is zero, or first temperature minus explicit previous_temp.

    Never sort rows or bridge independent recordings automatically. All later
    deltas use the preceding row. Caller input is left unchanged.
    """
    result = validate_telemetry(df)
    delta = result["temp_c"].diff()
    if previous_temp is not None and not np.isfinite(previous_temp):
        raise ValueError("previous_temp must be finite")
    delta.iloc[0] = 0.0 if previous_temp is None else result["temp_c"].iloc[0] - previous_temp
    result["temp_delta"] = delta
    return result


def feature_matrix(df, *, previous_temp=None, feature_order=None):
    order = FEATURE_COLUMNS if feature_order is None else list(feature_order)
    if len(order) != len(FEATURE_COLUMNS) or set(order) != set(FEATURE_COLUMNS):
        raise ValueError("Unsupported model feature order; retrain the model")
    return add_features(df, previous_temp=previous_temp)[order]
