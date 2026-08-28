# ESP32 controller

The ESP32 accepts complete validated frames over USB serial and generates the F30's 800 kHz single-wire output. The default build targets one 35-byte module; change `DISPLAY_BYTES` to `735` for the final 21-module chain.

## Electrical connection

Do not connect GPIO18 directly to the F30. Use the 5V SN74AHCT125 circuit in [the hardware guide](../../docs/hardware.md).

## Serial packet

```text
offset  size  field
0       4     ASCII "FDM1"
4       2     payload length, little-endian
6       N     physical F30 bytes (0x00 or 0xFF)
6+N     2     CRC-16/CCITT over payload, little-endian
```

Default serial rate is 921600 baud. Successful frames produce `STATUS frame-ok`.

## Build

```sh
pio run
pio run -t upload
pio device monitor -b 921600
```
