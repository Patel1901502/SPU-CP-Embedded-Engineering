"""Exercise real command handling through injected UART and sensor backends."""

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def firmware(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "device"))
    modules = {
        name: importlib.import_module(name)
        for name in ("config", "protocol", "service", "sensors", "board", "main")
    }
    monkeypatch.setattr(modules["sensors"].time, "ticks_ms", lambda: 1000, raising=False)
    monkeypatch.setattr(modules["sensors"].time, "ticks_diff", lambda a, b: a - b, raising=False)
    monkeypatch.setattr(modules["sensors"].time, "sleep_ms", lambda _: None, raising=False)
    yield SimpleNamespace(**modules)
    for name in modules:
        sys.modules.pop(name, None)


class UART:
    def __init__(self):
        self.pending = b""
        self.output = bytearray()

    def any(self):
        return len(self.pending)

    def read(self):
        data, self.pending = self.pending, b""
        return data

    def write(self, data):
        # Force partial writes to verify response preservation.
        self.output.extend(data[:3])
        return min(3, len(data))


class LED:
    state = 0

    def value(self, value):
        self.state = value


def test_framing_injection_and_recovery(firmware):
    uart, led = UART(), LED()
    sensors = SimpleNamespace(read=lambda: {"temp_c": 25}, info=lambda: {"sensor": "custom"})
    service = firmware.board.create_service(firmware.config, uart, sensors, led)
    assert service.uart is uart and service.sensors is sensors and service.led is led
    uart.pending = b"PI"
    service.poll()
    assert not uart.output
    uart.pending = b"NG\r\nLED ON\nTELEMETRY\n\xff\nPING\n"
    service.poll()
    lines = uart.output.decode().splitlines()
    assert lines[:3] == ["PONG", "OK LED=ON", "TEL temp_c=25"]
    assert lines[3].startswith("ERR INTERNAL=") and lines[4] == "PONG"
    assert led.state == 1
    service.max_command_bytes = 4
    uart.output.clear()
    uart.pending = b"12345"
    service.poll()
    assert not service.buffer
    uart.pending = b"PING\nPING\n"
    service.poll()
    assert uart.output == b"ERR COMMAND_TOO_LONG\r\nPONG\r\n"


@pytest.mark.parametrize("backend", ["tmp102", "analog", "simulated"])
def test_backends_share_unchanged_commands(firmware, backend):
    s = firmware.sensors
    if backend == "tmp102":
        bus = SimpleNamespace(writeto_mem=lambda *a: None, readfrom_mem=lambda *a: b"\x19\x00")
        sensor = s.SensorSuite(bus, firmware.config)
    elif backend == "analog":
        sensor = s.AnalogSensorSuite(SimpleNamespace(read_u16=lambda: 14894), firmware.config)
    else:
        sensor = s.SimulatedSensorSuite()
    uart = UART()
    service = firmware.service.UARTService(uart, sensor, LED())
    uart.pending = b"SENSOR_INFO\nTELEMETRY\n"
    service.poll()
    lines = uart.output.decode().splitlines()
    assert lines[0].startswith("INFO ")
    assert lines[1].startswith("TEL temp_c=")
    if backend != "simulated":
        uart.pending = b"TELEMETRY\n"
        service.poll()
        assert uart.output.endswith(b"ERR SENSOR=RATE_LIMIT\r\n")


def test_analog_conversion_fault_and_recovery(firmware, monkeypatch):
    settings = SimpleNamespace(**{k: v for k, v in vars(firmware.config).items() if k.isupper()})
    settings.ANALOG_FULL_SCALE_V = 1.5
    adc = SimpleNamespace(read_u16=lambda: 32767.5)
    sensor = firmware.sensors.AnalogSensorSuite(adc, settings)
    assert sensor.read()["temp_c"] == 25
    monkeypatch.setattr(firmware.sensors.time, "ticks_ms", lambda: 2000)
    adc.read_u16 = lambda: 70000
    with pytest.raises(firmware.sensors.SensorReadError, match="ADC_OUT_OF_RANGE"):
        sensor.read()
    monkeypatch.setattr(firmware.sensors.time, "ticks_ms", lambda: 3000)
    adc.read_u16 = lambda: 32767.5
    assert sensor.read()["temp_c"] == 25
    settings.ANALOG_VOLTS_PER_C = 0
    with pytest.raises(ValueError):
        firmware.sensors.AnalogSensorSuite(adc, settings)


def test_board_uses_configuration(firmware, monkeypatch):
    calls = {}

    class Pin(LED):
        OUT = 1

        def __init__(self, *args):
            calls.setdefault("pins", []).append(args)

    def uart_factory(identifier, **options):
        calls["uart"] = (identifier, options)
        return UART()

    class ADC:
        def __init__(self, pin):
            self.pin = pin

        def atten(self, value):
            calls["atten"] = value

        def read_u16(self):
            return 14894

    monkeypatch.setitem(
        sys.modules, "machine", SimpleNamespace(Pin=Pin, UART=uart_factory, ADC=ADC)
    )
    monkeypatch.setattr(firmware.config, "SENSOR_BACKEND", "analog")
    monkeypatch.setattr(firmware.config, "UART_ID", 2)
    monkeypatch.setattr(firmware.config, "UART_OPTIONS", {"baudrate": 9600, "tx": 17, "rx": 16})
    service = firmware.board.create_service(firmware.config)
    assert calls["uart"] == (2, {"baudrate": 9600, "tx": 17, "rx": 16})
    assert calls["atten"] == firmware.config.ANALOG_ADC_ATTEN
    assert calls["pins"] == [(firmware.config.ANALOG_TEMP_PIN,), (firmware.config.LED_PIN, 1)]
    assert isinstance(service.sensors, firmware.sensors.AnalogSensorSuite)
