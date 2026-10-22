# Graph Report - .  (2026-10-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 131 nodes · 229 edges · 9 communities (7 shown, 2 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Capstone Proposal: Emergency Positioning Beacon
- analyze_field_test.py
- knowledge.py
- pso_placement.py
- lora_model.py
- Workflow: node_provisioning
- LocalProjection
- Base node (client base / gateway)
- Heltec LoRa32 V3 (SX1262)

## God Nodes (most connected - your core abstractions)
1. `Capstone Proposal: Emergency Positioning Beacon` - 17 edges
2. `Scenario` - 12 edges
3. `RadioParams` - 10 edges
4. `LocalProjection` - 8 edges
5. `max_range_m()` - 8 edges
6. `Workflow: node_provisioning` - 8 edges
7. `run_pso()` - 7 edges
8. `baseline_uniform()` - 7 edges
9. `run_one()` - 7 edges
10. `cmd_note()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Log-distance + radio-horizon propagation model` --implements--> `path_loss_db()`  [INFERRED]
  workflows/pso_buoy_placement.md → tools/lora_model.py
- `PSO relay-buoy placement` --implements--> `run_pso()`  [INFERRED]
  workflows/pso_buoy_placement.md → tools/pso_placement.py
- `Baseline uniform spacing placement` --implements--> `baseline_uniform()`  [INFERRED]
  workflows/pso_buoy_placement.md → tools/pso_placement.py
- `SOS button / MPU6050 tilt not stock Meshtastic` --semantically_similar_to--> `Open: SOS/tilt firmware approach (companion MCU vs custom module)`  [INFERRED] [semantically similar]
  workflows/node_provisioning.md → firmware/README.md
- `Prototype devices: Client -> Repeater -> Base` --semantically_similar_to--> `Resolved: 3-device prototype (Client, Repeater, Base)`  [INFERRED] [semantically similar]
  README.md → knowledge/notes/project-scope-and-open-decisions.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **3-device prototype chain** — workflows_node_provisioning_client_beacon, node_role_router, workflows_node_provisioning_base_gateway [EXTRACTED 0.95]
- **K=1 PSO vs baseline field comparison** — workflows_pso_buoy_placement_pso, pso_baseline_uniform_concept, workflows_pso_buoy_placement_k1_field_test [INFERRED 0.85]
- **Field test calibration loop** — workflows_field_test_analysis, tools_meshtastic_logger, tools_analyze_field_test, field_path_loss_calibration [INFERRED 0.85]
- **Beacon hardware stack** — docs_proposal_beacon_node, docs_proposal_heltec_v3, docs_proposal_gps_neo7m, docs_proposal_mpu6050, docs_proposal_sos_button [EXTRACTED 1.00]

## Communities (9 total, 2 thin omitted)

### Community 0 - "Capstone Proposal: Emergency Positioning Beacon"
Cohesion: 0.12
Nodes (27): Capstone Proposal: Emergency Positioning Beacon, Batasan Masalah (scope limits, 1 client + 1 base), Beacon node (boat client), Buoy 9 incident 10 May 2025, Buoy / Repeater relay node, COSPAS-SARSAT, EPIRB / GMDSS, GPS module NEO-7M (+19 more)

### Community 1 - "analyze_field_test.py"
Cohesion: 0.12
Nodes (15): Dedupe by packet_id (mesh flooding), Path-loss exponent calibration (path_loss_exp 3.3 placeholder), Note: PSO model design, Log-distance path loss + radio horizon model, Summarise field-test CSVs (from meshtastic_logger.py) per scenario: RSSI, SNR, d, Log received Meshtastic packets (RSSI, SNR, hops, position) from a USB-attached, load_env(), Path (+7 more)

### Community 2 - "knowledge.py"
Cohesion: 0.20
Nodes (17): Knowledge store (knowledge/ + graphify), WAT framework, Knowledge README, Namespace, cmd_add_url(), cmd_note(), cmd_query(), cmd_status() (+9 more)

### Community 3 - "pso_placement.py"
Cohesion: 0.25
Nodes (14): ndarray, PSO fitness: 1-coverage + conn_penalty, Coverage via BFS within max_hops, test_pso_beats_or_matches_baseline(), baseline_uniform(), main(), plot(), Path (+6 more)

### Community 4 - "lora_model.py"
Cohesion: 0.22
Nodes (14): test_rssi_decreases_with_distance_and_range_consistent(), test_time_on_air_semtech_reference(), link_ok(), max_range_m(), path_loss_db(), radio_horizon_m(), RadioParams, LoRa link model: path loss, RSSI, link feasibility, range, time on air.  Simpl (+6 more)

### Community 5 - "Workflow: node_provisioning"
Cohesion: 0.21
Nodes (16): Note: project scope and open decisions, Open: radio params (path_loss_exp 3.3, sens -132 dBm) are assumptions, Meshtastic ROUTER role for buoys, Open: 915 MHz vs Indonesia 920-923 MHz region, Open: PLACEHOLDER data CSVs and gateway coords pending QGIS, Resolved: 3-device prototype (Client, Repeater, Base), Baseline uniform spacing placement, Project README (+8 more)

### Community 6 - "LocalProjection"
Cohesion: 0.16
Nodes (9): test_projection_roundtrip_matches_haversine(), main(), haversine_m(), LocalProjection, Geo helpers: haversine, local metric projection, polyline resampling., Great-circle distance in meters. Accepts scalars or numpy arrays., Equirectangular projection around a reference point. Fine for < ~100 km., Points every ~spacing_m along a polyline (always keeps first and last). (+1 more)

## Knowledge Gaps
- **7 isolated node(s):** `Base node (client base / gateway)`, `Heltec LoRa32 V3 (SX1262)`, `UU No. 7/2016 nelayan kecil (10 GT)`, `RSSI / SNR / delay metrics`, `Workflow template` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Workflow: node_provisioning` connect `Workflow: node_provisioning` to `Capstone Proposal: Emergency Positioning Beacon`, `analyze_field_test.py`?**
  _High betweenness centrality (0.375) - this node is a cross-community bridge._
- **Why does `Workflow: field_test_analysis` connect `analyze_field_test.py` to `Workflow: node_provisioning`?**
  _High betweenness centrality (0.348) - this node is a cross-community bridge._
- **Why does `Open: SOS/tilt firmware approach (companion MCU vs custom module)` connect `Capstone Proposal: Emergency Positioning Beacon` to `Workflow: node_provisioning`?**
  _High betweenness centrality (0.308) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Scenario` (e.g. with `test_pso_beats_or_matches_baseline()` and `LocalProjection`) actually correct?**
  _`Scenario` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `RadioParams` (e.g. with `test_rssi_decreases_with_distance_and_range_consistent()` and `main()`) actually correct?**
  _`RadioParams` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `LocalProjection` (e.g. with `test_projection_roundtrip_matches_haversine()` and `Scenario`) actually correct?**
  _`LocalProjection` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `max_range_m()` (e.g. with `test_rssi_decreases_with_distance_and_range_consistent()` and `main()`) actually correct?**
  _`max_range_m()` has 3 INFERRED edges - model-reasoned connections that need verification._