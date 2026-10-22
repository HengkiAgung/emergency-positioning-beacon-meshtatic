"""LoRa link model: path loss, RSSI, link feasibility, range, time on air.

Simple log-distance model. ALL parameters are assumptions until calibrated with
field RSSI measurements (see workflows/field_test_analysis.md). Re-fit
`path_loss_exp` and `ref_loss_db` from field data, then re-run PSO.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class RadioParams:
    freq_mhz: float = 915.0
    tx_power_dbm: float = 22.0        # SX1262 max; check regional limit
    tx_gain_dbi: float = 3.5          # TX915-XPL-100
    rx_gain_dbi: float = 3.5
    sensitivity_dbm: float = -132.0   # SF10/BW125 ballpark; Meshtastic LongFast ~ -129..-134
    fade_margin_db: float = 10.0
    path_loss_exp: float = 3.3        # placeholder (sea-level antennas, ducting/multipath); fit from field data
    ref_dist_m: float = 1.0
    ref_loss_db: float | None = None  # None -> free-space loss at ref_dist_m
    antenna_height_m: float = 2.0     # both ends; sets radio-horizon cap on link range

    def pl_ref(self) -> float:
        if self.ref_loss_db is not None:
            return self.ref_loss_db
        # FSPL(d0) = 20log10(d_km) + 20log10(f_MHz) + 32.44
        return 20 * math.log10(self.ref_dist_m / 1000.0) + 20 * math.log10(self.freq_mhz) + 32.44


def path_loss_db(d_m, p: RadioParams):
    d = np.maximum(np.asarray(d_m, float), p.ref_dist_m)
    return p.pl_ref() + 10 * p.path_loss_exp * np.log10(d / p.ref_dist_m)


def rssi_dbm(d_m, p: RadioParams):
    return p.tx_power_dbm + p.tx_gain_dbi + p.rx_gain_dbi - path_loss_db(d_m, p)


def link_ok(d_m, p: RadioParams):
    """True where predicted RSSI clears sensitivity + fade margin."""
    d = np.asarray(d_m, float)
    ok = rssi_dbm(d, p) >= p.sensitivity_dbm + p.fade_margin_db
    return ok & (d <= radio_horizon_m(p.antenna_height_m, p.antenna_height_m))


def max_range_m(p: RadioParams) -> float:
    """Usable link range: min(link-budget range, radio horizon)."""
    budget = p.tx_power_dbm + p.tx_gain_dbi + p.rx_gain_dbi - (p.sensitivity_dbm + p.fade_margin_db)
    d = p.ref_dist_m * 10 ** ((budget - p.pl_ref()) / (10 * p.path_loss_exp))
    return min(d, radio_horizon_m(p.antenna_height_m, p.antenna_height_m))


def radio_horizon_m(h1_m: float, h2_m: float) -> float:
    """Approx radio horizon (4/3 earth): 4.12*(sqrt(h1)+sqrt(h2)) km."""
    return 4120.0 * (math.sqrt(h1_m) + math.sqrt(h2_m))


def time_on_air_s(payload_bytes: int, sf: int = 11, bw_hz: int = 250000, cr: int = 5,
                  preamble: int = 16, explicit_header: bool = True, crc: bool = True) -> float:
    """LoRa time on air (Semtech AN1200.13). cr: 5..8 meaning 4/5..4/8. Meshtastic preamble=16."""
    t_sym = (2 ** sf) / bw_hz
    de = 1 if t_sym > 0.016 else 0
    h = 0 if explicit_header else 1
    num = 8 * payload_bytes - 4 * sf + 28 + (16 if crc else 0) - 20 * h
    n_payload = 8 + max(math.ceil(num / (4 * (sf - 2 * de))) * cr, 0)
    return (preamble + 4.25) * t_sym + n_payload * t_sym
