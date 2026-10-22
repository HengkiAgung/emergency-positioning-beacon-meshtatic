---
title: MPU6050 capsize SOS custom firmware
created: 2026-10-22
---

# MPU6050 capsize SOS custom firmware

Stock Meshtastic 2.7.26 MPU6050Sensor::init calls sensor.begin(addr) with default Wire, so an MPU6050 on Heltec V3 Wire1 (GPIO41/42) is detected by the I2C scan but logs 'MPU6050 init failed'. Fixed in firmware/meshtastic-fw/src/motion/MPU6050Sensor.cpp (pick Wire1 by scanned port) and added capsize detection: tilt>70deg for 5s -> broadcast 'SOS CAPSIZE lat,lon tilt=N' + position, repeat 60s, clear at <45deg for 5s. pio '-t nobuild -t upload' fails in Meshtastic (projenv import error); flash with esptool: boot_app0.bin at 0xe000 + firmware.bin at 0x10000, which keeps config. GPS on COM7 node (RX48/TX47) not detected at any baud; using fixed position -1.2599561,116.8826342 for now.
