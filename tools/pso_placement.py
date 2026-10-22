"""PSO placement of K relay buoys on a fishing route (Teluk Balikpapan).

Fitness (minimise):  (1 - weighted_coverage) + conn_penalty * (disconnected_buoys / K)

A route point is covered if it has a link to the gateway, or to a buoy that
reaches the gateway within `max_hops` buoy-to-buoy/gateway hops. Buoys that
cannot reach the gateway are penalised so the swarm keeps the chain connected.

Usage:
    python tools/pso_placement.py --config configs/default.json --k 3
    python tools/pso_placement.py --config configs/default.json --sweep 1-6
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _shared import ROOT  # noqa: E402
from geo import LocalProjection, resample_polyline  # noqa: E402
from lora_model import RadioParams, link_ok, max_range_m  # noqa: E402


class Scenario:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.radio = RadioParams(**cfg.get("radio", {}))
        gw = cfg["gateway"]
        wp = pd.read_csv(ROOT / cfg["route_csv"])
        self.proj = LocalProjection(gw["lat"], gw["lon"])
        wx, wy = self.proj.to_xy(wp["lat"].values, wp["lon"].values)
        self.px, self.py = resample_polyline(wx, wy, cfg.get("route_spacing_m", 250))
        self.weights = np.ones(len(self.px)) / len(self.px)
        self.gw = np.array([0.0, 0.0])  # gateway = projection origin
        pad = cfg.get("bbox_pad_m", 2000)
        self.lo = np.array([self.px.min() - pad, self.py.min() - pad])
        self.hi = np.array([self.px.max() + pad, self.py.max() + pad])
        self.max_hops = int(cfg.get("max_hops", 3))
        self.conn_penalty = float(cfg.get("conn_penalty", 0.5))
        cands = cfg.get("candidates_csv")
        self.cand = None
        if cands and (ROOT / cands).exists():
            c = pd.read_csv(ROOT / cands)
            cx, cy = self.proj.to_xy(c["lat"].values, c["lon"].values)
            self.cand = np.stack([cx, cy], axis=1)

    # ---- evaluation -------------------------------------------------------
    def evaluate(self, buoys: np.ndarray) -> dict:
        """buoys: (K,2) metric xy. Returns coverage stats."""
        k = len(buoys)
        nodes = np.vstack([self.gw[None, :], buoys]) if k else self.gw[None, :]
        d_nn = np.hypot(*(nodes[:, None, :] - nodes[None, :, :]).transpose(2, 0, 1))
        adj = link_ok(d_nn, self.radio)
        np.fill_diagonal(adj, False)
        # BFS hop count from gateway (index 0)
        hops = np.full(len(nodes), np.inf)
        hops[0] = 0
        frontier = [0]
        for h in range(1, self.max_hops + 1):
            nxt = []
            for u in frontier:
                for v in np.nonzero(adj[u])[0]:
                    if hops[v] == np.inf:
                        hops[v] = h
                        nxt.append(v)
            frontier = nxt
        reach = hops < np.inf  # node can deliver to gateway
        d_pn = np.hypot(self.px[:, None] - nodes[None, :, 0], self.py[:, None] - nodes[None, :, 1])
        # a boat talking to node j needs hops[j] + 1 <= max_hops (boat -> ... -> gateway)
        usable = reach & (hops < self.max_hops)
        usable[0] = True
        covered = (link_ok(d_pn, self.radio) & usable[None, :]).any(axis=1)
        return {
            "coverage": float((covered * self.weights).sum()),
            "disconnected": int((~reach[1:]).sum()),
            "covered_mask": covered,
            "hops": hops,
        }

    def fitness(self, flat: np.ndarray) -> float:
        buoys = flat.reshape(-1, 2)
        r = self.evaluate(buoys)
        k = max(len(buoys), 1)
        return (1.0 - r["coverage"]) + self.conn_penalty * r["disconnected"] / k


# ---- PSO ------------------------------------------------------------------
def run_pso(sc: Scenario, k: int, seed: int | None = None) -> dict:
    p = sc.cfg.get("pso", {})
    n, iters = p.get("particles", 40), p.get("iterations", 150)
    w0, w1 = p.get("w_start", 0.9), p.get("w_end", 0.4)
    c1, c2 = p.get("c1", 1.8), p.get("c2", 1.8)
    rng = np.random.default_rng(p.get("seed", 0) if seed is None else seed)

    lo, hi = np.tile(sc.lo, k), np.tile(sc.hi, k)
    span = hi - lo
    x = rng.uniform(lo, hi, size=(n, 2 * k))
    v = rng.uniform(-span, span, size=(n, 2 * k)) * 0.1
    vmax = 0.2 * span

    f = np.array([sc.fitness(i) for i in x])
    pb, pbf = x.copy(), f.copy()
    g = pb[pbf.argmin()].copy()
    gf = float(pbf.min())
    history = [gf]

    for t in range(iters):
        w = w0 - (w0 - w1) * t / max(iters - 1, 1)  # linear inertia decay
        r1, r2 = rng.random(x.shape), rng.random(x.shape)
        v = w * v + c1 * r1 * (pb - x) + c2 * r2 * (g - x)  # eq 2.1
        v = np.clip(v, -vmax, vmax)
        x = np.clip(x + v, lo, hi)                           # eq 2.2
        f = np.array([sc.fitness(i) for i in x])
        better = f < pbf
        pb[better], pbf[better] = x[better], f[better]
        if pbf.min() < gf:
            gf, g = float(pbf.min()), pb[pbf.argmin()].copy()
        history.append(gf)

    buoys = g.reshape(-1, 2)
    if sc.cand is not None and p.get("snap_to_candidates", False):
        idx = np.hypot(*(buoys[:, None, :] - sc.cand[None, :, :]).transpose(2, 0, 1)).argmin(axis=1)
        buoys = sc.cand[idx]
    res = sc.evaluate(buoys)
    lat, lon = sc.proj.to_latlon(buoys[:, 0], buoys[:, 1])
    return {"k": k, "buoys_xy": buoys, "lat": lat, "lon": lon, "history": history, **res}


def baseline_uniform(sc: Scenario, k: int) -> dict:
    """Baseline: k buoys evenly spaced along the route (manual-placement proxy)."""
    idx = np.linspace(0, len(sc.px) - 1, k + 2)[1:-1].round().astype(int)
    buoys = np.stack([sc.px[idx], sc.py[idx]], axis=1)
    return {"k": k, "buoys_xy": buoys, **sc.evaluate(buoys)}


# ---- output ---------------------------------------------------------------
def plot(sc: Scenario, pso: dict, base: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    rng_m = max_range_m(sc.radio)
    for a, res, title in ((ax[0], base, "Baseline (uniform)"), (ax[1], pso, "PSO")):
        m = res["covered_mask"]
        a.scatter(sc.px[m], sc.py[m], s=8, c="tab:green", label="covered")
        a.scatter(sc.px[~m], sc.py[~m], s=8, c="tab:red", label="uncovered")
        for bx, by in res["buoys_xy"]:
            a.add_patch(plt.Circle((bx, by), rng_m, fill=False, ls="--", alpha=0.4))
        a.scatter(*res["buoys_xy"].T, marker="^", s=80, c="tab:blue", label="buoy")
        a.scatter(0, 0, marker="s", s=90, c="k", label="gateway")
        a.set_aspect("equal")
        a.set_title(f"{title}: coverage {res['coverage']*100:.1f}%")
        a.set_xlabel("x (m)")
        a.set_ylabel("y (m)")
    ax[0].legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

    fig, a = plt.subplots(figsize=(6, 4))
    a.plot(pso["history"])
    a.set_xlabel("iteration")
    a.set_ylabel("global-best fitness")
    a.set_title("PSO convergence")
    fig.tight_layout()
    fig.savefig(path.with_name(path.stem + "_convergence.png"), dpi=150)
    plt.close(fig)


def run_one(sc: Scenario, k: int, out_dir: Path) -> dict:
    pso, base = run_pso(sc, k), baseline_uniform(sc, k)
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"buoy": range(1, k + 1), "lat": pso["lat"], "lon": pso["lon"],
                  "hops_to_gateway": pso["hops"][1:]}).to_csv(out_dir / f"buoys_k{k}.csv", index=False)
    plot(sc, pso, base, out_dir / f"map_k{k}.png")
    return {"k": k, "coverage_pso": pso["coverage"], "coverage_baseline": base["coverage"],
            "disconnected_pso": pso["disconnected"]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/default.json")
    ap.add_argument("--k", type=int, help="number of buoys")
    ap.add_argument("--sweep", help="range of K, e.g. 1-6 (finds minimum K for target coverage)")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()

    cfg = json.loads((ROOT / a.config).read_text(encoding="utf-8"))
    sc = Scenario(cfg)
    print(f"route pts={len(sc.px)}  max link range={max_range_m(sc.radio)/1000:.2f} km  max_hops={sc.max_hops}")
    ks = range(*(lambda lo, hi: (int(lo), int(hi) + 1))(*a.sweep.split("-"))) if a.sweep else [a.k or cfg.get("k", 3)]
    rows = [run_one(sc, k, ROOT / a.out) for k in ks]
    df = pd.DataFrame(rows)
    print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    if a.sweep:
        df.to_csv(ROOT / a.out / "sweep.csv", index=False)
        tgt = cfg.get("target_coverage", 0.95)
        ok = df[df.coverage_pso >= tgt]
        print(f"min K for >= {tgt:.0%} coverage: {int(ok.k.min()) if len(ok) else 'not reached'}")


if __name__ == "__main__":
    main()
