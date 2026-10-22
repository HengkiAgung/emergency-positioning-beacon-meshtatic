# Workflow: Firmware build & flash (beacon, capsize SOS)

## Objective
Put the beacon firmware (Meshtastic + MPU6050 capsize SOS) on a Heltec V3 and confirm the sensor works.

## Inputs
- Heltec V3 on USB, its serial port (e.g. `COM7`; Device Manager / `meshtastic --info --port COMx`)
- MPU6050 wired to GPIO41 (SDA) / GPIO42 (SCL), Z axis up when the boat is upright
- Repo cloned with submodules: `git clone --recurse-submodules git@github.com:HengkiAgung/emergency-positioning-beacon-meshtatic.git`
- `pip install platformio pyserial meshtastic`

## Tools
- `tools/firmware_flash.py` — init submodule if missing, build (`platformio run -e heltec-v3`), flash with esptool, read boot log for `MPU6050 init ok`.

## Steps
1. Existing Meshtastic node (keep config): `python tools/firmware_flash.py --port COM7`
2. Brand-new / bricked board: `python tools/firmware_flash.py --port COM7 --factory`, then provision per `workflows/node_provisioning.md` (config is wiped).
3. Several boards: build once, then `--skip-build` per board.
4. Field check: tilt board > 70° for 5 s → base receives `SOS CAPSIZE <lat>,<lon> tilt=N`; upright 5 s → `SOS CLEARED`.

## Outputs
- Flashed node. Build artifacts in `firmware/meshtastic-fw/.pio/build/heltec-v3/` (regenerable, ~1 GB).

## Firmware source
- Submodule `firmware/meshtastic-fw` → `HengkiAgung/firmware`, branch `beacon-capsize` (based on upstream tag `v2.7.26.54e0d8d`).
- Change code: edit in submodule, commit + push there, then in main repo `git add firmware/meshtastic-fw` and commit (records new submodule SHA).
- Upgrade Meshtastic: in submodule `git fetch upstream --tags`, `git rebase <new tag>`, rebuild, test, push `--force-with-lease`.
- Thresholds: `CAPSIZE_*` defines in `src/motion/MPU6050Sensor.h`.

## Edge Cases & Learnings
- Stock 2.7.26 MPU6050 driver always used `Wire` → `MPU6050 init failed` for sensor on `Wire1`. Fixed in fork.
- `pio run -t nobuild -t upload` fails in this tree (`Import of non-existent variable 'projenv'`); tool uses esptool directly.
- Update mode writes `boot_app0.bin` at 0xe000 too, so the board boots app0 even if it last ran from OTA slot.
- Boot log is plain text on USB serial only while no API client (phone app/CLI) is connected.
- First build ~12 min (toolchain download); later builds incremental.
