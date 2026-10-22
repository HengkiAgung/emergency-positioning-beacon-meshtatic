# Workflow: node_provisioning

## Objective
Flash and configure the 3 prototype Heltec LoRa32 V3 devices with Meshtastic: Client (beacon on boat), Repeater (buoy, ROUTER), Base (CLIENT_BASE / gateway).

## Inputs
- Heltec LoRa32 V3 (915 MHz, SX1262) × N, USB cable, `pip install meshtastic`
- GPS NEO-7M (UART) on the beacon, MPU6050 (I2C), SOS button — see `firmware/README.md`

## Tools
- Meshtastic Web Flasher (flasher.meshtastic.org) or `esptool` — flash firmware.
- `meshtastic` CLI — configure over USB.

## Steps
1. Flash latest stable Meshtastic firmware for `heltec-v3`.
2. Common config (all nodes — region/preset MUST match):
   ```
   meshtastic --port COMx --set lora.region <REGION> --set lora.modem_preset LONG_FAST --set lora.hop_limit 3 --set lora.tx_power 22
   ```
   `<REGION>`: run `meshtastic --set lora.region` with no value to list enums. Indonesia ISM = 920–923 MHz (Permenkominfo 1/2019 jo. 2/2023). Confirm the enum covering 920–923 MHz and legal TX power **before** field tests (see Edge Cases).
3. Beacon (boat): `--set device.role CLIENT --set position.gps_mode ENABLED --set position.position_broadcast_secs 30 --set position.gps_update_interval 30`; set GPS RX/TX pins (`--set position.rx_gpio N --set position.tx_gpio N`).
4. Buoy: `--set device.role ROUTER` (or `ROUTER_LATE`), fixed position (`--setlat --setlon --setalt`), GPS off.
5. Base: `--set device.role CLIENT` (or `CLIENT_BASE`), keep USB to laptop; run `tools/meshtastic_logger.py`.
6. Same channel name + PSK on all nodes. Verify with `meshtastic --nodes`.

## Outputs
- Provisioned nodes; per-node config exports: `meshtastic --export-config > data/field/node_<name>.yaml`.

## Edge Cases & Learnings
- **Region/frequency**: Heltec "915 MHz" hardware band covers 902–928 MHz; Indonesia permits 920–923 MHz. Meshtastic region enums are fixed lists — verify the right one (and duty-cycle/power limits) rather than assuming. Proposal doc is inconsistent on 915 vs 920–923; resolve in Bab II/III.
- MPU6050 tilt auto-trigger and SOS button are **not** stock Meshtastic features: need custom firmware module or an external MCU sending a trigger (see `firmware/README.md`).
- Meshtastic ROUTER role rebroadcasts everything; for fixed buoys it is the intended role.
