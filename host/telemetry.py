import csv
import time
from pathlib import Path

def collect(device, seconds, interval=1.0):
    samples=[]
    deadline=time.monotonic()+seconds
    while time.monotonic() < deadline:
        sample=device.telemetry()
        if sample["type"] == "telemetry":
            sample.pop("type", None)
            sample["timestamp"]=time.time()
            samples.append(sample)
        time.sleep(interval)
    return samples

def save_csv(samples, output):
    if not samples: return
    with Path(output).open("w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f, fieldnames=samples[0].keys())
        writer.writeheader(); writer.writerows(samples)
