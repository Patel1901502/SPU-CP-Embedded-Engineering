import pandas as pd
from sklearn.ensemble import IsolationForest
from ml.features import feature_matrix

def test_model_detects_outlier():
    df=pd.DataFrame({
        "temp_c":[24,24.1,24.2,24.1,24,90],
        "vibration":[.10,.11,.10,.09,.10,8.0],
        "current_ma":[80,81,80,82,81,900]})
    m=IsolationForest(n_estimators=200,contamination=1/6,random_state=42)
    m.fit(feature_matrix(df))
    assert m.predict(feature_matrix(df))[-1]==-1
