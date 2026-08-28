# Pi vision service

This directory currently provides the hardware-independent foundation:

- a logical binary framebuffer;
- verified F30 local-byte mapping;
- optional serpentine module-chain mapping;
- a CRC-protected packet shared with the ESP32 controller.

Run tests without installing third-party packages:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Install the development package with serial support and send a one-module border test:

```sh
python3 -m pip install -e '.[serial]'
flipdot-send /dev/ttyUSB0 --pattern border
```

For the final 7 × 3 display, add `--modules-x 7 --modules-y 3`. The sender transmits an ordinary top-left-first logical canvas; the ESP32 owns the physical serpentine and module-local mapping.

The next increment will add camera capture and a native segmentation backend. The browser prototype in `apps/camera-web` remains the visual reference implementation.
