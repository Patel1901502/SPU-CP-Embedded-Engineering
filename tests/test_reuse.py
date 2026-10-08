import pandas as pd
import pytest

from host.device import EmbeddedDevice
from host.telemetry import collect, save_csv
from ml.model import score_samples, train_model


class Transport:
    closed = False

    def write(self, data):
        self.sent = data

    def readline(self):
        return b"PONG\r\n"

    def close(self):
        self.closed = True


def test_injected_transport_ownership_and_commands():
    transport = Transport()
    with EmbeddedDevice(transport=transport) as device:
        assert device.ping()
        assert transport.sent == b"PING\n"
        with pytest.raises(ValueError):
            device.command("PING\nSTATUS")
    assert not transport.closed
    with EmbeddedDevice(transport=transport, close_transport=True):
        pass
    assert transport.closed


def test_stream_collection_preserves_packets_and_exports_generator(tmp_path):
    packet = {"type": "telemetry", "temp_c": 24.0}

    class Device:
        def telemetry(self):
            return packet

    now = [0.0]

    def sleep(duration):
        now[0] += duration

    rows = collect(
        Device(), 2.5, interval=1, clock=lambda: now[0], timestamp=lambda: 123, sleep=sleep
    )
    assert len(rows) == 3
    assert now[0] == 2.5
    assert packet == {"type": "telemetry", "temp_c": 24.0}
    output = tmp_path / "samples.csv"
    save_csv(iter(rows), output)
    assert len(pd.read_csv(output)) == 3
    with pytest.raises(ValueError):
        collect(Device(), 1, interval=0)


def test_ml_api_preserves_non_default_index():
    frame = pd.DataFrame(
        {
            "temp_c": [24, 25, 24, 90],
            "vibration": [0.1, 0.2, 0.1, 8],
            "current_ma": [80, 81, 82, 900],
        },
        index=[5, 7, 9, 11],
    )
    model = train_model(frame, contamination=0.25, n_estimators=20)
    scored = score_samples(model, frame)
    assert scored.index.equals(frame.index)
    assert scored.anomaly.notna().all()
    assert scored.iloc[-1].anomaly == "ANOMALY"
    assert "anomaly" not in frame
