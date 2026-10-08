"""Hardware tests are skipped unless explicitly requested with a port."""

import pytest


def pytest_addoption(parser):
    parser.addoption("--hardware", action="store_true", help="Enable ESP32 tests")
    parser.addoption("--port", default=None, help="ESP32 serial port")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--hardware") and not config.getoption("--port"):
        raise pytest.UsageError("--hardware requires --port")
    if not config.getoption("--hardware"):
        for item in items:
            if "hardware" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="requires --hardware --port PORT"))


@pytest.fixture
def hardware_device(request):
    from host.device import EmbeddedDevice

    with EmbeddedDevice(request.config.getoption("--port"), timeout=2.0) as device:
        yield device
