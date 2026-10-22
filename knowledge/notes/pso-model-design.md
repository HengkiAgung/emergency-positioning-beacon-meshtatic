---
title: PSO model design
created: 2026-10-22
tags: [pso, model]
---

# PSO model design

tools/pso_placement.py: continuous PSO over K buoy xy, fitness = (1-weighted route coverage) + conn_penalty*disconnected/K. Coverage = route point links to gateway or buoy reaching gateway within max_hops (BFS). Link = log-distance RSSI >= sensitivity+fade margin AND d <= radio horizon (2 m antennas ~11.6 km). Default link range ~4.1 km. Placeholder 25 km route plateaus ~54% coverage with 3 hops. Baseline = uniform spacing along route.
