"""Command handler for the ESP32 text-based UART protocol.

Protocol examples::

    Host -> Device: PING
    Device -> Host: PONG

    Host -> Device: TELEMETRY
    Device -> Host: TEL temp_c=24.1,vibration=0.1,current_ma=80.0

A human-readable text protocol keeps this portfolio project easy to debug with
any serial terminal. A production system could replace it with a framed binary
protocol including message IDs, lengths, checksums/CRC, and versioning.
"""


def handle_command(command, sensors, led):
    """Execute one host command and return the response string.

    Args:
        command: Raw command text received over UART.
        sensors: SensorSuite-compatible object exposing ``read()``.
        led: MicroPython Pin-compatible output object exposing ``value()``.

    Returns:
        A protocol response string without CR/LF terminators.
    """
    # Ignore leading/trailing whitespace and make commands case-insensitive.
    command = command.strip().upper()

    if command == "PING":
        # Basic communication/health check used by the host API.
        return "PONG"

    if command == "STATUS":
        # A simple readiness response. More fields (firmware version, faults,
        # uptime, etc.) can be added here as the embedded application grows.
        return "OK STATUS=READY"

    if command == "SENSOR_INFO":
        import json

        return "INFO " + json.dumps(sensors.info())

    if command == "TELEMETRY":
        # Take a fresh sensor snapshot only when telemetry is requested.
        try:
            sample = sensors.read()
        except Exception as exc:
            return "ERR SENSOR=" + str(exc).replace("\n", " ").replace("\r", " ")
        return "TEL " + ",".join("{}={}".format(key, value) for key, value in sample.items())

    if command == "LED ON":
        led.value(1)
        return "OK LED=ON"

    if command == "LED OFF":
        led.value(0)
        return "OK LED=OFF"

    # Unknown commands get an explicit protocol error rather than being ignored.
    return "ERR BAD_COMMAND"
