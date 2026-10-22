---
title: Mesh network config in use (from phone screenshots)
created: 2026-10-22
---

# Mesh network config in use (from phone screenshots)

Base+repeater run: region MY_919 (Malaysia 919MHz, covers ID 920-923), preset LONG_FAST, hop_limit 4, frequency_slot 16, TX enabled, duty cycle override off. MQTT on public idmeshnode (mqtt.meshnode.id, root msh/ID), proxy via phone, map reporting off. Client MUST match region, preset, slot and channel PSK. Client has no phone at sea so MQTT off on client. Public MQTT uplink leaks beacon GPS positions; keep client MQTT off, consider base MQTT off or private channel.
