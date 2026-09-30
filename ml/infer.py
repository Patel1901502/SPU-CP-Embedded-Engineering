import argparse
import joblib
import pandas as pd
from features import feature_matrix

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model", required=True); p.add_argument("--input", required=True)
    a=p.parse_args()
    model=joblib.load(a.model); df=pd.read_csv(a.input); x=feature_matrix(df)
    pred=model.predict(x); score=model.decision_function(x)
    out=df.copy()
    out["anomaly"]=pd.Series(pred).map({1:"NORMAL",-1:"ANOMALY"})
    out["score"]=score
    print(out[["temp_c","vibration","current_ma","anomaly","score"]].to_string(index=False))
    print(f"Anomalies detected: {(pred==-1).sum()} / {len(pred)}")

if __name__=="__main__": main()
