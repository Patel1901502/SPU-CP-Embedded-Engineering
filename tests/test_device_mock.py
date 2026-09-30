from host.device import EmbeddedDevice

class FakeSerial:
    def __init__(self,*args,**kwargs): self.response=b""
    def write(self,data):
        self.response={
            "PING":b"PONG\r\n",
            "STATUS":b"OK STATUS=READY\r\n",
            "TELEMETRY":b"TEL temp_c=24.5,vibration=0.1,current_ma=80.0\r\n"
        }[data.decode().strip()]
    def readline(self): return self.response
    def close(self): pass

def test_mock_device(monkeypatch):
    import host.device as module
    monkeypatch.setattr(module.serial,"Serial",FakeSerial)
    with EmbeddedDevice("FAKE") as d:
        assert d.ping(); assert d.status()["status"]=="READY"; assert d.telemetry()["temp_c"]==24.5
