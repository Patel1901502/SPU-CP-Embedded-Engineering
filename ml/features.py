"""Feature engineering shared by ML training and inference."""

# Keep the exact feature order centralized. The model must receive columns in
# the same order during inference as it did during training.
FEATURE_COLUMNS = ["temp_c", "vibration", "current_ma", "temp_delta"]


def add_features(df):
    """Return a copy of *df* with derived model features added."""
    result = df.copy()

    # Temperature delta captures change between consecutive samples. A sudden
    # thermal jump can be informative even when absolute temperature is modest.
    # The first row has no previous sample, so use a neutral delta of zero.
    result["temp_delta"] = result["temp_c"].diff().fillna(0.0)
    return result


def feature_matrix(df):
    """Build the numeric feature matrix expected by the anomaly detector."""
    return add_features(df)[FEATURE_COLUMNS]
