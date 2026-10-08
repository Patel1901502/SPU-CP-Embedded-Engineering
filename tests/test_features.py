import pandas as pd

from ml.features import add_features, feature_matrix


def test_feature_generation():
    df = pd.DataFrame(
        {"temp_c": [20, 20.5, 20.7], "vibration": [0.1, 0.2, 0.1], "current_ma": [80, 81, 82]}
    )
    r = add_features(df)
    assert "temp_delta" in r and r.iloc[0]["temp_delta"] == 0


def test_feature_matrix_shape():
    df = pd.DataFrame({"temp_c": [20, 20.5], "vibration": [0.1, 0.2], "current_ma": [80, 81]})
    assert feature_matrix(df).shape == (2, 4)
