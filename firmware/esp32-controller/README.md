# ESP32 controller

The ESP32 accepts complete validated logical frames over USB serial, maps them into physical module order, and generates the F30's 800 kHz single-wire output. The default `sample` environment targets one module; the `wall` environment targets the final 7 × 3 chain.

## Electrical connection

Do not connect GPIO18 directly to the F30. Use the 5V SN74AHCT125 circuit in [the hardware guide](../../docs/hardware.md).

## Serial packet

```text
offset  size  field
0       4     ASCII "FDM1"
4       2     payload length, little-endian
6       N     logical row-major pixels (0x00 or 0xFF), top-left first
6+N     2     CRC-16/CCITT over payload, little-endian
```

Default serial rate is 921600 baud. Successful frames produce `STATUS frame-ok`.

## Build

```sh
pio run
pio run -e sample -t upload
pio device monitor -b 921600
```

Build or upload the complete display firmware with `-e wall`.
