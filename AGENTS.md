# Project handoff

This is the compact context needed to continue the project from another machine or coding session.

## Goal and topology

Build a camera-driven 35 × 21 wall display from 21 white/black F30 flip-dot modules arranged 7 × 3.

```text
camera -> Raspberry Pi 4 vision process -> USB serial -> ESP32
       -> SN74AHCT125 3.3V-to-5V buffer -> F30 single-wire chain
```

Use the logical 35 × 21 framebuffer as the boundary between vision and hardware. Keep physical module order and serpentine wiring out of image-processing code.

## Verified F30 facts

- Each F30 is 5 columns × 7 rows = 35 dots.
- Front-view physical order starts at dot 1 in the bottom-right, proceeds right-to-left along each row, then bottom-to-top.
- The supplier calls the control mode SPI; it is a proprietary 5V, 800 kHz, self-clocking single-wire stream, not conventional clocked SPI.
- One byte controls one dot: `0x00` black, `0xFF` white. Avoid intermediate values.
- Send bytes MSB first and hold data low for more than 24 microseconds to latch a frame.
- Each module consumes 35 bytes and forwards the remaining stream. Twenty-one modules consume exactly 735 bytes.
- Supplier recommends at most 29 modules per single-wire chain.
- RJ45 T568B pin 6 (green) is data; pin 3 (white/green) is signal ground.
- The Arduino Mega bench test has independently controlled all 35 sample dots.

## Default physical layout

The planned cable route is serpentine by module row. Production mapping lives in `firmware/esp32-controller/src/main.cpp`; change that one boundary if the installed cable order differs. Python's `to_f30_stream()` remains a reference implementation and direct-driver utility.

## Commands

```sh
cd services/pi-vision
PYTHONPATH=src python3 -m unittest discover -s tests -v

cd ../../firmware/mega-bench
pio run

cd ../esp32-controller
pio run
pio run -t upload
pio device monitor -b 921600
```

## Working rules

- Treat mains wiring and 12V high-current distribution as safety-critical.
- Never commit invoices, contracts, addresses, phone numbers, private supplier messages, tracking data, or proprietary supplier PDFs.
- Record newly verified hardware behavior in `docs/` and distinguish measurement from assumption.
- Run relevant tests and commit completed changes. The public repository should remain reproducible from a fresh clone.
