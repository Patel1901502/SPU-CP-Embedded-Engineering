from host.protocol import parse_response

def test_ping(): assert parse_response("PONG")=={"type":"pong"}
def test_status(): assert parse_response("OK STATUS=READY")["status"]=="READY"
def test_telemetry():
    r=parse_response("TEL temp_c=24.5,vibration=0.12,current_ma=82.0")
    assert r["type"]=="telemetry"; assert r["temp_c"]==24.5; assert r["current_ma"]==82.0
