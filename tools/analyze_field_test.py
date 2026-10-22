"""Summarise field-test CSVs (from meshtastic_logger.py) per scenario: RSSI, SNR, delay, packet rate.

    python tools/analyze_field_test.py data/field/pso_k3.csv data/field/baseline_k3.csv
    python tools/analyze_field_test.py data/field/*.csv --fit-path-loss --gateway-lat -1.265 --gateway-lon 116.806

--fit-path-loss: least-squares fit of RSSI = a - 10*n*log10(d) using packets with lat/lon;
feed n back into configs/default.json (radio.path_loss_exp) and re-run PSO.
PDR needs known sent count: pass --sent scenario=N (repeatable).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _shared import ROOT  # noqa: E402
from geo import haversine_m  # noqa: E402
from lora_model import RadioParams  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--sent", action="append", default=[], help="scenario=N packets sent, for PDR")
    ap.add_argument("--fit-path-loss", action="store_true")
    ap.add_argument("--gateway-lat", type=float)
    ap.add_argument("--gateway-lon", type=float)
    a = ap.parse_args()

    df = pd.concat([pd.read_csv(p if Path(p).is_absolute() else ROOT / p) for p in a.csv], ignore_index=True)
    sent = {k: int(v) for k, v in (s.split("=") for s in a.sent)}
    for c in ("rssi", "snr", "delay_s"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    rows = []
    for sc, g in df.groupby("scenario"):
        # dedupe by packet id: mesh flooding can deliver duplicates
        g = g.drop_duplicates(subset="packet_id") if g["packet_id"].notna().any() else g
        rows.append({
            "scenario": sc, "rx_packets": len(g),
            "pdr_%": 100 * len(g) / sent[sc] if sc in sent else np.nan,
            "rssi_mean": g.rssi.mean(), "rssi_min": g.rssi.min(),
            "snr_mean": g.snr.mean(), "snr_min": g.snr.min(),
            "delay_mean_s": g.delay_s.mean(), "delay_p95_s": g.delay_s.quantile(0.95),
        })
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda v: f"{v:.2f}"))

    if a.fit_path_loss:
        if a.gateway_lat is None or a.gateway_lon is None:
            sys.exit("--fit-path-loss needs --gateway-lat/--gateway-lon")
        g = df.dropna(subset=["lat", "lon", "rssi"]).copy()
        g["d"] = haversine_m(g.lat, g.lon, a.gateway_lat, a.gateway_lon)
        g = g[g.d > 50]
        if len(g) < 5:
            sys.exit("not enough positioned packets for fit")
        slope, icpt = np.polyfit(10 * np.log10(g.d), g.rssi, 1)
        n = -slope
        print(f"\nfit: RSSI = {icpt:.1f} - 10*{n:.2f}*log10(d)   (n={n:.2f}, N={len(g)})")
        print(f"set radio.path_loss_exp ~ {n:.2f}; assumes same TX power/antennas as config "
              f"(tx={RadioParams().tx_power_dbm} dBm)")


if __name__ == "__main__":
    main()
