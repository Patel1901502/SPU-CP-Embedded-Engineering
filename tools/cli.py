import argparse
from host.device import EmbeddedDevice
from host.telemetry import collect, save_csv

def main():
    p=argparse.ArgumentParser(); p.add_argument("--port",required=True)
    s=p.add_subparsers(dest="command",required=True)
    s.add_parser("ping"); s.add_parser("status"); s.add_parser("telemetry")
    led=s.add_parser("led"); led.add_argument("state",choices=["on","off"])
    c=s.add_parser("collect"); c.add_argument("--seconds",type=float,default=30); c.add_argument("--output",default="telemetry.csv")
    a=p.parse_args()
    with EmbeddedDevice(a.port) as d:
        if a.command=="ping": print("PONG" if d.ping() else "FAIL")
        elif a.command=="status": print(d.status())
        elif a.command=="telemetry": print(d.telemetry())
        elif a.command=="led": print(d.led(a.state=="on"))
        elif a.command=="collect":
            samples=collect(d,a.seconds); save_csv(samples,a.output); print(f"Saved {len(samples)} samples to {a.output}")

if __name__=="__main__": main()
