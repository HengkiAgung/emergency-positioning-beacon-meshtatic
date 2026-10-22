# Workflow: pso_buoy_placement

## Objective
Find K relay-buoy positions that maximise route coverage (multi-hop to gateway) with PSO, compare to a baseline, and find the minimum K for the target coverage.

## Inputs
- `data/route_waypoints.csv` — `name,lat,lon` fishing-route polyline (from QGIS / Google Earth Pro). **Currently PLACEHOLDER.**
- `data/candidate_sites.csv` — `name,lat,lon` feasible buoy sites (optional; used if `pso.snap_to_candidates=true`). **Currently PLACEHOLDER.**
- `configs/default.json` — gateway coords, radio params, hop limit, PSO params, target coverage.

## Tools
- `tools/pso_placement.py --k N` or `--sweep 1-6` — runs PSO + uniform baseline, writes `results/buoys_kN.csv`, `map_kN.png`, `map_kN_convergence.png`, `sweep.csv`.
- `tools/lora_model.py` — link budget, radio horizon, time on air.
- `tests/test_core.py` — `python -m pytest tests`.

## Steps
1. Replace placeholder CSVs and gateway coords with real data (QGIS: draw route over Teluk Balikpapan, export lat/lon; keep buoy candidates on water/at navigation markers).
2. Set `radio.*` from the actual hardware (Heltec V3 SX1262, TX915 antenna 3.5 dBi) and Meshtastic preset (sensitivity per preset). `max_hops` = Meshtastic hop limit (default 3).
3. `python tools/pso_placement.py --sweep 1-6` → read min K for `target_coverage`.
4. Report PSO vs baseline coverage at that K (Bab IV table). Re-run with several seeds (`pso.seed`) and report mean ± std.
5. After field data exists, fit `path_loss_exp` (see `field_test_analysis.md`), re-run, and compare predicted vs measured.

## Outputs
- `results/` (gitignored, regenerable). Copy final figures/tables into the report.

## Edge Cases & Learnings
- Model = log-distance + radio-horizon cap (2 m antennas ⇒ ~11.6 km). Defaults (`path_loss_exp=3.3`) are placeholders; Wiguna et al. (2025) measured ~1.2 km P2P at sea, so calibrate before trusting absolute coverage.
- No land/terrain obstruction in model (bay shoreline/hills can block LoS). Add a water-mask or per-link obstruction penalty if the lecturer asks for it.
- Coverage counts a boat→buoy→…→gateway chain only if total hops ≤ `max_hops`; disconnected buoys are penalised (`conn_penalty`).
- Prototype = 3 devices: Client (beacon on boat), Repeater (buoy), Base (gateway). So field test uses K=1: PSO picks the single repeater position; baseline = repeater at route midpoint / manual spot. K>1 sweeps are simulation-only (scalability argument in Bab IV).
- With K=1 and `max_hops=3`, boat→repeater→base is 2 hops; compare PSO vs baseline on a prototype-scale test area, not the full 25 km placeholder route.
