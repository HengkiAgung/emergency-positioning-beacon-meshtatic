---
title: Three-node mesh provisioned 2026-10-22
created: 2026-10-22
---

# Three-node mesh provisioned 2026-10-22

Nodes: Base UNIBA TE KT30 !09d3ef1c (CLIENT_BASE, fw 2.7.15); Repeater UNIBA_TE_02 KT31 !09d3bf28 (ROUTER, fw 2.7.26); Client UNIBA-TE23 KT29 !09d44508 (CLIENT, fw 2.7.26, GPS rx7 tx6, pos 30s, MQTT off). All MY_919 LONG_FAST slot16 hop4, primary channel UnibaCHA (same PSK). Base ch1 = old unnamed PSK. COM ports change on replug: identify by Owner via --info. Client was on UNIBABASE default PSK (isolated) before fix. Traceroute Client<->Base 6.75/5.75 dB direct. PKI DM Repeater->Base unreliable (NodeInfo exchange stuck, maybe RX saturation at -16 dBm bench range); decided NodeInfo not required: SOS + position as channel broadcast. Configs exported data/field/node_*.yaml (gitignored, PSKs). TX power 27 and Base/Repeater public MQTT uplink still open items.
