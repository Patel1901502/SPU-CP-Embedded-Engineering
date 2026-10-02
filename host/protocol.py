"""Parser for responses produced by the ESP32 UART firmware."""


def parse_response(response: str) -> dict:
    """Convert one device response line into a structured dictionary.

    Keeping protocol parsing in a separate module isolates wire-format details
    from the rest of the host application and makes the parser easy to unit test.

    Raises:
        ValueError: If the response does not match a known protocol message.
    """
    response = response.strip()

    if response == "PONG":
        return {"type": "pong"}

    if response.startswith("OK STATUS="):
        status = response.split("=", 1)[1]
        return {"type": "status", "status": status}

    if response.startswith("OK LED="):
        state = response.split("=", 1)[1]
        return {"type": "led", "state": state}

    if response.startswith("TEL "):
        values = {}

        # Telemetry is encoded as comma-separated key=value fields.
        # Example: temp_c=24.5,vibration=0.12,current_ma=82.0
        for field in response[4:].split(","):
            key, value = field.split("=", 1)
            values[key] = float(value)

        return {"type": "telemetry", **values}

    if response.startswith("ERR "):
        # Device-reported errors are returned as data so callers can decide
        # whether to retry, display the error, or escalate it.
        return {"type": "error", "message": response[4:]}

    # A completely unknown response usually means a protocol/version mismatch
    # or corrupted serial data, so fail loudly instead of silently accepting it.
    raise ValueError(f"Unknown response: {response}")
