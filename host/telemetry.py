"""Utilities for collecting device telemetry and saving it as CSV."""

import csv
import time
from pathlib import Path


def collect(device, seconds, interval=1.0):
    """Collect telemetry samples for a requested duration.

    ``time.monotonic`` is used for duration measurement because it cannot jump
    backward/forward when the system wall clock is adjusted.
    """
    samples = []
    deadline = time.monotonic() + seconds

    while time.monotonic() < deadline:
        sample = device.telemetry()

        # Only valid telemetry packets are stored. Protocol errors remain the
        # responsibility of the caller/device layer.
        if sample["type"] == "telemetry":
            sample.pop("type", None)

            # Unix wall-clock time is useful when correlating exported samples
            # with logs or other system events.
            sample["timestamp"] = time.time()
            samples.append(sample)

        time.sleep(interval)

    return samples


def save_csv(samples, output):
    """Write collected telemetry samples to *output* as a CSV file."""
    if not samples:
        # Avoid creating an empty CSV with no meaningful column definition.
        return

    output_path = Path(output)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        # All samples are expected to have the same keys as the first sample.
        writer = csv.DictWriter(csv_file, fieldnames=samples[0].keys())
        writer.writeheader()
        writer.writerows(samples)
