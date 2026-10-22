"""Log received Meshtastic packets (RSSI, SNR, hops, position) from a USB-attached node to CSV.

Run on the laptop attached to the RX node (client-base / gateway) during field tests.
Needs: pip install meshtastic pypubsub.   UNTESTED without hardware.

    python tools/meshtastic_logger.py --port COM5 --scenario pso_k3 --out data/field/pso_k3.csv

Delay: Meshtastic position packets carry the sender GPS `time`; delay_s = rx_wallclock - packet time.
Needs laptop clock NTP-synced; resolution is 1 s, so use it only for coarse delay. For precise delay
send numbered text messages and log tx time on the sender.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _shared import ROOT  # noqa: E402

FIELDS = ["rx_time", "scenario", "from", "portnum", "rssi", "snr", "hop_limit", "hop_start",
          "lat", "lon", "pkt_time", "delay_s", "packet_id"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True, help="serial port, e.g. COM5")
    ap.add_argument("--scenario", required=True, help="label, e.g. pso_k3 or baseline_k3")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    import meshtastic.serial_interface
    from pubsub import pub

    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    new = not out.exists()
    fh = out.open("a", newline="", encoding="utf-8")
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    if new:
        w.writeheader()

    def on_receive(packet, interface):  # noqa: ARG001
        dec = packet.get("decoded", {})
        pos = dec.get("position", {})
        now = time.time()
        pkt_time = pos.get("time")
        hs, hl = packet.get("hopStart"), packet.get("hopLimit")
        w.writerow({
            "rx_time": f"{now:.3f}", "scenario": a.scenario, "from": packet.get("fromId"),
            "portnum": dec.get("portnum"), "rssi": packet.get("rxRssi"), "snr": packet.get("rxSnr"),
            "hop_limit": hl, "hop_start": hs,
            "lat": pos.get("latitude"), "lon": pos.get("longitude"), "pkt_time": pkt_time,
            "delay_s": f"{now - pkt_time:.1f}" if pkt_time else "", "packet_id": packet.get("id"),
        })
        fh.flush()
        print(f"{packet.get('fromId')} rssi={packet.get('rxRssi')} snr={packet.get('rxSnr')} {dec.get('portnum')}")

    pub.subscribe(on_receive, "meshtastic.receive")
    iface = meshtastic.serial_interface.SerialInterface(a.port)
    print("Logging... Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        iface.close()
        fh.close()


if __name__ == "__main__":
    main()
