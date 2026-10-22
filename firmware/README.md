# Firmware notes (Beacon node)

Meshtastic stock firmware covers LoRa mesh, GPS position broadcast and routing. Beacon-specific behaviour is NOT stock:

| Feature | Approach |
|---|---|
| Manual SOS button | Wire to a free GPIO. Option A: stock `Canned Message`/`External Notification` modules (button → preset text "SOS"). Option B: custom module. |
| Auto-trigger on capsize (MPU6050) | Custom firmware module (PlatformIO, fork `meshtastic/firmware`) or companion MCU reading MPU6050 over I2C and sending SOS via Meshtastic serial/`--sendtext`. Trigger: tilt angle > ~60–90° sustained > N s; debounce wave motion. |
| Faster position rate in SOS | On trigger set `position_broadcast_secs` low (e.g. 10 s) and send text `SOS lat,lon`. |

Wiring (to finalise; schematic is TODO per proposal §3.4.2): NEO-7M → UART (GPIO per `position.rx_gpio/tx_gpio`), MPU6050 → I2C (Heltec V3 SDA/SCL pins), button → GPIO + pull-up. Check Heltec V3 pinout for pins shared with OLED/LoRa.

Decision (2026-10-22): **custom firmware**, MPU6050 wired directly to Heltec V3 `Wire1` (GPIO41 SDA / GPIO42 SCL), no companion MCU.

## Custom firmware: capsize SOS (MPU6050)

Source: `patches/0001-mpu6050-wire1-fix-and-capsize-sos.patch` on top of `meshtastic/firmware` tag `v2.7.26.54e0d8d` (same as stock on devices). The clone `meshtastic-fw/` is gitignored; recreate it with:

```
cd firmware
git clone --depth 1 --branch v2.7.26.54e0d8d --recurse-submodules --shallow-submodules https://github.com/meshtastic/firmware.git meshtastic-fw
cd meshtastic-fw && git apply ../patches/0001-mpu6050-wire1-fix-and-capsize-sos.patch
```

Changed files only:

- `src/motion/MPU6050Sensor.h/.cpp`
  - **Bug fix (upstream):** stock `sensor.begin(addr)` always used `Wire`, so MPU6050 on `Wire1` logged `MPU6050 init failed`. Now picks `Wire1` when scanned on port 2.
  - **Capsize detection:** tilt = angle between sensor Z axis and gravity, low-passed. Tilt > 70° for 5 s → broadcast text `SOS CAPSIZE <lat>,<lon> tilt=<deg>` (channel 0, priority ALERT) + position packet. Repeats every 60 s while capsized. Tilt < 45° for 5 s → `SOS CLEARED ...`.
  - Thresholds are `#define CAPSIZE_*` in the header (override via `-D` build flags).
  - Mount MPU6050 with Z axis pointing up when the boat is upright.

Build / flash (PlatformIO, `pip install platformio`):

```
cd firmware/meshtastic-fw
python -m platformio run -e heltec-v3
python -m esptool --chip esp32s3 --port COM7 --baud 921600 write_flash -z \
  0xe000 ~/.platformio/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin \
  0x10000 .pio/build/heltec-v3/firmware-heltec-v3-2.7.26.54e0d8d.bin
```

(`esptool` lives in `~/.platformio/packages/tool-esptoolpy/esptool.py` if not on PATH.) Only otadata + app are written, so node config in LittleFS is kept. `pio run -t nobuild -t upload` fails in this tree (`Import of non-existent variable 'projenv'`). Verify on boot log: `MPU6050 init ok`.
