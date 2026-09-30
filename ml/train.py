import argparse
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from features import feature_matrix

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input", required=True); p.add_argument("--output", default="model.joblib")
    a=p.parse_args()
    df=pd.read_csv(a.input); x=feature_matrix(df)
    model=IsolationForest(n_estimators=100, contamination=0.03, random_state=42)
    model.fit(x); joblib.dump(model,a.output)
    print(f"Training samples: {len(x)}")
    print(f"Features: {list(x.columns)}")
    print(f"Model saved to {a.output}")

if __name__=="__main__": main()
