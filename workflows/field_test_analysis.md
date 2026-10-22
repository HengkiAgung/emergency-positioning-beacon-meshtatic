# Workflow: field_test_analysis

## Objective
Measure RSSI, SNR, delay and packet delivery for PSO vs baseline buoy placement, and calibrate the propagation model.

## Inputs
- Provisioned nodes (`node_provisioning.md`), boat, laptop on base node.
- `--scenario` labels: `pso_kN`, `baseline_kN`.

## Tools
- `tools/meshtastic_logger.py --port COMx --scenario pso_k3 --out data/field/pso_k3.csv`
- `tools/analyze_field_test.py data/field/*.csv --sent pso_k3=N --fit-path-loss --gateway-lat .. --gateway-lon ..`

## Steps
1. Place buoys per `results/buoys_kN.csv` (PSO) then per baseline layout; run the same boat route and send count in both.
2. Log on base during each run. Note planned packet count N per scenario (beacon interval × duration).
3. Analyse → table of PDR, mean/min RSSI & SNR, delay mean/p95 per scenario.
4. Fit path-loss exponent, update `configs/default.json`, re-run PSO, compare predicted vs measured coverage.
5. Fill sensor-test tables in the proposal (GPS: acquisition, coordinate linearity, accuracy; MPU6050: accel/gyro sensitivity, tilt linearity) from bench tests.

## Outputs
- `data/field/*.csv` (gitignored), summary tables for Bab IV.

## Edge Cases & Learnings
- Mesh flooding makes duplicates: analysis dedupes by `packet_id`.
- `delay_s` uses GPS packet time vs laptop clock → 1 s resolution, needs NTP sync. Use numbered messages for finer delay.
- RSSI vs distance fit needs ≥5 positioned packets and d > 50 m.
