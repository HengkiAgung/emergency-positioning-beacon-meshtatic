"""Geo helpers: haversine, local metric projection, polyline resampling."""
from __future__ import annotations

import numpy as np

EARTH_R = 6371000.0


def haversine_m(lat1, lon1, lat2, lon2):
    """Great-circle distance in meters. Accepts scalars or numpy arrays."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dlmb = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * EARTH_R * np.arcsin(np.sqrt(a))


class LocalProjection:
    """Equirectangular projection around a reference point. Fine for < ~100 km."""

    def __init__(self, ref_lat: float, ref_lon: float):
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon
        self._kx = np.radians(1.0) * EARTH_R * np.cos(np.radians(ref_lat))
        self._ky = np.radians(1.0) * EARTH_R

    def to_xy(self, lat, lon):
        lat, lon = np.asarray(lat, float), np.asarray(lon, float)
        return (lon - self.ref_lon) * self._kx, (lat - self.ref_lat) * self._ky

    def to_latlon(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        return self.ref_lat + y / self._ky, self.ref_lon + x / self._kx


def resample_polyline(x, y, spacing_m: float):
    """Points every ~spacing_m along a polyline (always keeps first and last)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    seg = np.hypot(np.diff(x), np.diff(y))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    n = max(int(np.ceil(s[-1] / spacing_m)), 1)
    t = np.linspace(0.0, s[-1], n + 1)
    return np.interp(t, s, x), np.interp(t, s, y)
