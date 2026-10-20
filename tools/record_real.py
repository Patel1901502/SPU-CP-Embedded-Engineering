"""Capture a hardware-only dataset with provenance and explicit failure state."""

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from host.device import EmbeddedDevice
from host.telemetry import iter_samples


def record(device, output, seconds=60, interval=1):
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("seconds must be finite and positive")
    if not math.isfinite(interval) or interval <= 0:
        raise ValueError("interval must be finite and positive")
    packet = device.command("SENSOR_INFO")
    info = packet.get("info", {})
    if info.get("source") != "hardware" or info.get("sensor") != "TMP102":
        raise ValueError("Real capture requires the TMP102 hardware backend")
    if interval * 1000 < info["sample_period_ms"]:
        raise ValueError("interval is shorter than device sample_period_ms")
    output = Path(output)
    manifest = output.with_suffix(output.suffix + ".json")
    if output.exists() or manifest.exists():
        raise FileExistsError("Choose a new output path; existing captures are preserved")
    metadata = {
        "sensor_info": info,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "requested_seconds": seconds,
        "interval_seconds": interval,
        "rows": 0,
        "complete": False,
    }
    try:
        with output.open("x", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["timestamp", "temp_c", "raw_temp_c"])
            writer.writeheader()
            for row in iter_samples(device, seconds, interval):
                if set(row) != {"timestamp", "temp_c", "raw_temp_c"}:
                    raise ValueError("Unexpected real sensor schema")
                if not all(math.isfinite(value) for value in row.values()):
                    raise ValueError("Nonfinite real sensor measurement")
                writer.writerow(row)
                metadata["rows"] += 1
        if metadata["rows"] == 0:
            raise RuntimeError("No measurements collected")
        metadata["complete"] = True
    except BaseException as exc:
        metadata["error"] = str(exc) or type(exc).__name__
        raise
    finally:
        metadata["ended_utc"] = datetime.now(timezone.utc).isoformat()
        if output.exists():
            metadata["sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--interval", type=float, default=1)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with EmbeddedDevice(args.port, timeout=2) as device:
        result = record(device, args.output, args.seconds, args.interval)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
