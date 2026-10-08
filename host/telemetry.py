"""Reusable streaming acquisition and CSV export."""

import csv
import time
from pathlib import Path


def iter_samples(
    device, seconds, interval=1.0, *, clock=time.monotonic, timestamp=time.time, sleep=time.sleep
):
    """Yield telemetry without accumulating it in memory.

    device needs only telemetry(); timing functions can be injected for tests.
    Collection stops between requests; a blocking transport may exceed duration.
    Device error packets are skipped, matching the original collector.
    """
    if seconds < 0 or interval <= 0:
        raise ValueError("seconds must be nonnegative and interval positive")
    deadline = clock() + seconds
    while clock() < deadline:
        packet = device.telemetry()
        if packet["type"] == "telemetry":
            sample = {key: value for key, value in packet.items() if key != "type"}
            sample["timestamp"] = timestamp()
            yield sample
        remaining = deadline - clock()
        if remaining > 0:
            sleep(min(interval, remaining))


def collect(device, seconds, interval=1.0, **timing):
    """Backward-compatible list collector built on the streaming API."""
    return list(iter_samples(device, seconds, interval, **timing))


def save_csv(samples, output):
    """Write a list or single-pass iterator; leave output untouched if empty."""
    samples = iter(samples)
    first = next(samples, None)
    if first is None:
        return
    with Path(output).open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(first))
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(samples)
