def handle_command(command, sensors, led):
    command = command.strip().upper()
    if command == "PING":
        return "PONG"
    if command == "STATUS":
        return "OK STATUS=READY"
    if command == "TELEMETRY":
        s = sensors.read()
        return "TEL temp_c={temp_c},vibration={vibration},current_ma={current_ma}".format(**s)
    if command == "LED ON":
        led.value(1)
        return "OK LED=ON"
    if command == "LED OFF":
        led.value(0)
        return "OK LED=OFF"
    return "ERR BAD_COMMAND"
