# Architecture

## Responsibilities

```text
┌──────────────────────────────┐
│ Raspberry Pi 4B             │
│ camera capture              │
│ person segmentation         │
│ pose/limb reinforcement     │
│ temporal filtering          │
│ logical 35×21 framebuffer   │
└──────────────┬───────────────┘
               │ framed binary messages
               │ USB serial first; TCP/WebSocket later
┌──────────────▼───────────────┐
│ ESP32                        │
│ validates complete frames   │
│ logical→physical mapping    │
│ optional transition policy  │
│ precise 800kHz output       │
└──────────────┬───────────────┘
               │ 3.3V
┌──────────────▼───────────────┐
│ SN74AHCT125                  │
│ 3.3V logic → 5V logic       │
└──────────────┬───────────────┘
               │ RJ45 pin 6 data + pin 3 ground
┌──────────────▼───────────────┐
│ 21-module F30 chain          │
│ 735 bytes per frame          │
└──────────────────────────────┘
```

## Why split Pi and ESP32?

Linux is excellent for cameras, OpenCV, MediaPipe/TFLite, networking, storage, and application logic. It is not ideal for sub-microsecond waveform generation under scheduler load. The ESP32 has hardware peripherals and a small deterministic runtime, so display timing remains stable even when vision processing stalls.

## Transport progression

1. **USB serial:** simplest, wired, recoverable, and easy to inspect. This is the initial production path.
2. **TCP on the local network:** the Pi or another computer can connect to the ESP32 without USB.
3. **WebSocket UI:** the ESP32 can serve a small control page and accept interactive frames from a browser.
4. **ESP32 access-point mode:** useful for commissioning when no trusted Wi-Fi network is available.

The ESP32 can absolutely run a web server. That server may host the entire static UI itself, while browser JavaScript sends commands or complete frames back over HTTP/WebSocket. For the permanent camera mirror, wired USB serial remains preferable because the Pi and ESP32 occupy the same enclosure and the display should not depend on Wi-Fi.

## Frame ownership

The Pi owns the **logical image**: 35 columns × 21 rows in ordinary reading order. The ESP32 owns the **physical topology**: module order, serpentine cabling, module-local reversal, and the exact single-wire waveform. This keeps camera code independent of how the chassis is wired.
