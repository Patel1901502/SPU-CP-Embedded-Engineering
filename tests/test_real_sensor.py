"""Driver and capture checks using an injected bus; no physical measurements."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from host.protocol import parse_response
from host.telemetry import collect
from tools.record_real import record

ROOT = Path(__file__).resolve().parents[1]


def load_device(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "device" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def sensor_module(monkeypatch):
    module = load_device("sensors")
    monkeypatch.setattr(module.time, "sleep_ms", lambda _: None, raising=False)
    monkeypatch.setattr(module.time, "ticks_ms", lambda: 1000, raising=False)
    monkeypatch.setattr(module.time, "ticks_diff", lambda a, b: a - b, raising=False)
    return module


class Bus:
    data = bytes([0x19, 0x00])
    fail = False

    def writeto_mem(self, addr, register, data):
        self.config = (addr, register, data)

    def readfrom_mem(self, *args):
        if self.fail:
            raise OSError("NACK")
        return self.data


def settings(**changes):
    values = dict(
        SAMPLE_PERIOD_MS=1000,
        TEMP_SCALE=1.0,
        TEMP_OFFSET_C=0.0,
        TMP102_ADDRESS=0x48,
        I2C_SDA_PIN=21,
        I2C_SCL_PIN=22,
        I2C_FREQ_HZ=100000,
    )
    return SimpleNamespace(**(values | changes))


@pytest.mark.parametrize(
    "raw,expected", [(b"\x19\x00", 25), (b"\xff\xf0", -0.0625), (b"\xe7\x00", -25)]
)
def test_signed_conversion(sensor_module, raw, expected):
    bus = Bus()
    bus.data = raw
    driver = sensor_module.TMP102(bus)
    assert bus.config == (0x48, 1, b"\x60\xa0")
    assert driver.read_c() == expected


@pytest.mark.parametrize("raw", [b"\x19", b"\x19\x01", b"\x7f\xf0"])
def test_invalid_sensor_data(sensor_module, raw):
    bus = Bus()
    bus.data = raw
    with pytest.raises(OSError):
        sensor_module.TMP102(bus).read_c()


def test_calibration_rate_limit_and_reconnect(sensor_module, monkeypatch):
    bus = Bus()
    suite = sensor_module.SensorSuite(bus, settings(TEMP_SCALE=2, TEMP_OFFSET_C=-1))
    assert suite.read() == {"temp_c": 49.0, "raw_temp_c": 25.0}
    with pytest.raises(sensor_module.SensorReadError, match="RATE_LIMIT"):
        suite.read()
    monkeypatch.setattr(sensor_module.time, "ticks_ms", lambda: 2000)
    bus.fail = True
    with pytest.raises(sensor_module.SensorReadError, match="TMP102_READ_FAILED"):
        suite.read()
    assert suite.driver is None
    monkeypatch.setattr(sensor_module.time, "ticks_ms", lambda: 3000)
    bus.fail = False
    assert suite.read()["temp_c"] == 49


@pytest.mark.parametrize(
    "changes", [dict(SAMPLE_PERIOD_MS=249), dict(TEMP_SCALE=0), dict(TEMP_OFFSET_C=float("nan"))]
)
def test_bad_configuration(sensor_module, changes):
    with pytest.raises(ValueError):
        sensor_module.SensorSuite(Bus(), settings(**changes))


def test_wire_fault_and_info(sensor_module):
    protocol = load_device("protocol")

    class Broken:
        def read(self):
            raise OSError("NACK")

    packet = parse_response(protocol.handle_command("TELEMETRY", Broken(), None))
    assert packet == {"type": "error", "message": "SENSOR=NACK"}
    suite = sensor_module.SensorSuite(Bus(), settings())
    packet = parse_response(protocol.handle_command("SENSOR_INFO", suite, None))
    assert packet["info"]["source"] == "hardware"
    assert packet["info"]["temp_scale"] == 1


def test_collection_does_not_swallow_error():
    device = SimpleNamespace(telemetry=lambda: {"type": "error", "message": "SENSOR=NACK"})
    with pytest.raises(RuntimeError, match="SENSOR=NACK"):
        collect(device, 1)


def test_capture_metadata_and_fault_state(tmp_path, monkeypatch):
    import tools.record_real as capture

    device = SimpleNamespace(
        command=lambda _: {
            "info": {"source": "hardware", "sensor": "TMP102", "sample_period_ms": 1000}
        }
    )
    monkeypatch.setattr(
        capture,
        "iter_samples",
        lambda *a: iter([{"timestamp": 123, "temp_c": 25, "raw_temp_c": 25}]),
    )
    output = tmp_path / "real.csv"
    result = record(device, output)
    assert result["complete"] and result["rows"] == 1
    assert len(result["sha256"]) == 64
    with pytest.raises(FileExistsError):
        record(device, output)

    def broken(*args):
        yield {"timestamp": 123, "temp_c": 25, "raw_temp_c": 25}
        raise RuntimeError("SENSOR=NACK")

    monkeypatch.setattr(capture, "iter_samples", broken)
    output = tmp_path / "partial.csv"
    with pytest.raises(RuntimeError):
        record(device, output)
    result = json.loads(output.with_suffix(".csv.json").read_text())
    assert not result["complete"] and result["rows"] == 1
    assert "NACK" in result["error"]


def test_capture_rejects_simulation(tmp_path):
    device = SimpleNamespace(command=lambda _: {"info": {"source": "synthetic"}})
    with pytest.raises(ValueError, match="hardware"):
        record(device, tmp_path / "fake.csv")
    assert not list(tmp_path.iterdir())
