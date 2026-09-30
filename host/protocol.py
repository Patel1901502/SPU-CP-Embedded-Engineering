def parse_response(response: str) -> dict:
    response = response.strip()
    if response == "PONG":
        return {"type": "pong"}
    if response.startswith("OK STATUS="):
        return {"type": "status", "status": response.split("=", 1)[1]}
    if response.startswith("OK LED="):
        return {"type": "led", "state": response.split("=", 1)[1]}
    if response.startswith("TEL "):
        values = {}
        for field in response[4:].split(","):
            key, value = field.split("=", 1)
            values[key] = float(value)
        return {"type": "telemetry", **values}
    if response.startswith("ERR "):
        return {"type": "error", "message": response[4:]}
    raise ValueError(f"Unknown response: {response}")
