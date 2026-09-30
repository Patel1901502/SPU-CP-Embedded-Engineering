FEATURE_COLUMNS=["temp_c","vibration","current_ma","temp_delta"]

def add_features(df):
    result=df.copy()
    result["temp_delta"]=result["temp_c"].diff().fillna(0.0)
    return result

def feature_matrix(df):
    return add_features(df)[FEATURE_COLUMNS]
