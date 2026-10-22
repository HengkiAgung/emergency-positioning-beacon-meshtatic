---
title: Base node audit 2026-10-22
created: 2026-10-22
---

# Base node audit 2026-10-22

Base = UNIBA TE (KT30, !09d3ef1c), fw 2.7.15, role CLIENT_BASE, COM6 (CP210x). LoRa MY_919 LONG_FAST slot 16 hop 4 txPower 27 (SX1262 max ~22). Channels: 0 primary (unnamed, custom PSK), 1 'UnibaCHA'; both uplink+downlink MQTT on, positionPrecision 32. Repeater = UNIBA_TE_02 (KT31, !09d3bf28) heard direct, SNR 5.75, on ch1, role field absent = CLIENT (not ROUTER yet). NodeDB has 86 nodes from public mesh/MQTT: field-test logs must filter by our node IDs. Config export at data/field/node_base.yaml (gitignored, has PSKs).
