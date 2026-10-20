"""Read-only integration checks against the flashed UART application."""

import math

import pytest

pytestmark = pytest.mark.hardware


def test_ping(hardware_device):
    assert hardware_device.ping()


def test_status(hardware_device):
    assert hardware_device.status() == {"type": "status", "status": "READY"}


def test_telemetry(hardware_device):
    sample = hardware_device.telemetry()
    assert sample["type"] == "telemetry"
    for key in ("temp_c", "raw_temp_c"):
        assert math.isfinite(sample[key])


def test_hardware_source(hardware_device):
    info = hardware_device.command("SENSOR_INFO")["info"]
    assert info["source"] == "hardware"
    assert info["sensor"] == "TMP102"
