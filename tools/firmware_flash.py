"""Build and flash the beacon Meshtastic firmware (fork submodule) to a Heltec V3, then verify the MPU6050.

Source: firmware/meshtastic-fw = submodule HengkiAgung/firmware, branch beacon-capsize.
Needs: pip install platformio pyserial (first build downloads the ESP32 toolchain, ~15 min).

    python tools/firmware_flash.py --port COM7                # build + update app, keeps node config
    python tools/firmware_flash.py --port COM7 --skip-build   # flash last build
    python tools/firmware_flash.py --port COM7 --factory      # brand-new board: erase all + full image

Update mode writes only otadata (0xe000) + app (0x10000), so channel/LoRa/position config survives.
--factory erases the whole flash (config lost) and writes the merged factory image at 0x0.
Verify reads the boot log and expects 'MPU6050 init ok'.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _shared import ROOT  # noqa: E402

FW = ROOT / "firmware" / "meshtastic-fw"
PIO_HOME = Path.home() / ".platformio"
BOOT_APP0 = PIO_HOME / "packages" / "framework-arduinoespressif32" / "tools" / "partitions" / "boot_app0.bin"
ESPTOOL = PIO_HOME / "packages" / "tool-esptoolpy" / "esptool.py"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("$", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], cwd=cwd, check=True)


def ensure_source() -> None:
    if not (FW / "platformio.ini").exists():
        run(["git", "submodule", "update", "--init", "--recursive", "--depth", "1"], cwd=ROOT)


def build(env: str) -> None:
    run([sys.executable, "-m", "platformio", "run", "-e", env], cwd=FW)


def find_image(env: str, pattern: str) -> Path:
    hits = sorted((FW / ".pio" / "build" / env).glob(pattern), key=lambda p: p.stat().st_mtime)
    if not hits:
        sys.exit(f"No {pattern} in .pio/build/{env}. Build first (drop --skip-build).")
    return hits[-1]


def esptool(args: list) -> None:
    base = [sys.executable, ESPTOOL] if ESPTOOL.exists() else [sys.executable, "-m", "esptool"]
    run(base + args)


def check_port(port: str) -> None:
    from serial.tools import list_ports

    ports = {p.device: p.description for p in list_ports.comports()}
    if port not in ports:
        listing = "\n".join(f"  {d}  {desc}" for d, desc in ports.items()) or "  (none)"
        sys.exit(f"Port {port} not found. Plug the board in. Available:\n{listing}")


def flash(port: str, env: str, factory: bool, baud: int) -> None:
    common = ["--chip", "esp32s3", "--port", port, "--baud", baud]
    if factory:
        esptool(common + ["erase_flash"])
        img = find_image(env, "firmware-*.factory.bin")
        esptool(common + ["write_flash", "-z", "0x0", img])
    else:
        app = [p for p in (FW / ".pio" / "build" / env).glob("firmware-*.bin") if ".factory" not in p.name]
        if not app:
            sys.exit(f"No app image in .pio/build/{env}. Build first (drop --skip-build).")
        esptool(common + ["write_flash", "-z", "0xe000", BOOT_APP0, "0x10000", max(app, key=lambda p: p.stat().st_mtime)])


def verify(port: str, secs: float) -> bool:
    import serial

    ansi = re.compile(rb"\x1b\[[0-9;]*m")
    buf, deadline = b"", time.time() + secs
    verdict = re.compile(rb"MPU6050 init (ok|failed)")
    while time.time() < deadline and not verdict.search(buf):
        try:
            with serial.Serial(port, 115200, timeout=0.5) as s:
                while time.time() < deadline and not verdict.search(buf):
                    buf += s.read(4096)
        except serial.SerialException:
            time.sleep(0.3)  # port vanishes while USB re-enumerates after reset
    for line in ansi.sub(b"", buf).decode(errors="replace").splitlines():
        if re.search(r"MPU6050|AccelerometerThread|Capsize", line):
            print("  ", line.strip())
    if b"MPU6050 init ok" in buf:
        print("OK: MPU6050 init ok")
        return True
    if b"MPU6050 init failed" in buf:
        print("FAIL: MPU6050 init failed (check wiring on GPIO41/42)")
    else:
        print("FAIL: no MPU6050 line in boot log (sensor not found on I2C, or log missed)")
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", required=True, help="serial port, e.g. COM7")
    ap.add_argument("--env", default="heltec-v3", help="PlatformIO env (default heltec-v3)")
    ap.add_argument("--skip-build", action="store_true", help="flash the existing build")
    ap.add_argument("--factory", action="store_true", help="erase flash + full image (new board, config lost)")
    ap.add_argument("--no-verify", action="store_true", help="skip boot-log MPU6050 check")
    ap.add_argument("--baud", type=int, default=921600)
    a = ap.parse_args()

    ensure_source()
    if not a.skip_build:
        build(a.env)
    check_port(a.port)
    flash(a.port, a.env, a.factory, a.baud)
    if not a.no_verify and not verify(a.port, 30):
        sys.exit(1)


if __name__ == "__main__":
    main()
