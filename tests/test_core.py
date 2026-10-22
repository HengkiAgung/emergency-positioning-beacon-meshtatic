import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from geo import LocalProjection, haversine_m  # noqa: E402
from lora_model import RadioParams, max_range_m, rssi_dbm, time_on_air_s  # noqa: E402
from pso_placement import Scenario, baseline_uniform, run_pso  # noqa: E402


def test_projection_roundtrip_matches_haversine():
    pr = LocalProjection(-1.2, 116.8)
    x, y = pr.to_xy(-1.1, 116.9)
    assert abs(np.hypot(x, y) - haversine_m(-1.2, 116.8, -1.1, 116.9)) < 50
    lat, lon = pr.to_latlon(x, y)
    assert abs(lat + 1.1) < 1e-9 and abs(lon - 116.9) < 1e-9


def test_rssi_decreases_with_distance_and_range_consistent():
    p = RadioParams()
    assert rssi_dbm(1000, p) > rssi_dbm(5000, p)
    d = max_range_m(p)
    assert 1000 < d <= 11700  # capped by radio horizon


def test_time_on_air_semtech_reference():
    # AN1200.13-style check: SF7/BW125/CR4-5, 10 B payload, 8-symbol preamble, explicit hdr, CRC -> ~41.2 ms
    t = time_on_air_s(10, sf=7, bw_hz=125000, cr=5, preamble=8)
    assert abs(t - 0.0412) < 0.001


def test_pso_beats_or_matches_baseline():
    cfg = json.loads((ROOT / "configs/default.json").read_text(encoding="utf-8"))
    cfg["pso"].update(particles=20, iterations=40)
    sc = Scenario(cfg)
    pso, base = run_pso(sc, 3), baseline_uniform(sc, 3)
    assert pso["coverage"] >= base["coverage"] - 0.02
    assert pso["history"][-1] <= pso["history"][0]
