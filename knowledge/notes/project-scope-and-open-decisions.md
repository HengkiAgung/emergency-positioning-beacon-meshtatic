---
title: Project scope and open decisions
created: 2026-10-22
tags: [project, decision]
---

# Project scope and open decisions

Capstone: Meshtastic emergency beacon (boat) -> buoy relays -> base, PSO buoy placement, Teluk Balikpapan. Proposal in docs/. Open: (1) prototype is 1 client + 1 base per Batasan 1 but PSO needs relays; (2) proposal says 915 MHz but Indonesia ISM is 920-923 MHz, verify Meshtastic region enum + TX power; (3) SOS button and MPU6050 tilt trigger are not stock Meshtastic, need companion MCU or custom module; (4) data/*.csv and gateway coords are PLACEHOLDER until QGIS data; (5) radio params (path_loss_exp 3.3, sens -132 dBm) are assumptions, calibrate from field data.


## Update 2026-10-22

RESOLVED (user, 2026-10-22): prototype has 3 devices: Base, Repeater, Client. Field test K=1 repeater; PSO picks its position vs baseline manual spot. K>1 only simulated. Open (1) 1+1 prototype question is closed.
