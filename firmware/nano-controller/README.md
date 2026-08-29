# Nano controller firmware

Same minimal bench firmware as `mega-bench`, retargeted to an Arduino Nano (ATmega328P, 16MHz — same AVR family and clock as the Mega, so the NeoPixel-timed single-wire protocol ports unchanged). Drives the F30 directly at native 5V logic; no level shifter needed.

```text
Nano D6  → RJ45 pin 6 / green
Nano GND → RJ45 pin 3 / white-green
```

Set the F30 to `1 OFF / 2 OFF / 3 ON`. Install dependencies and upload with:

```sh
pio run -t upload
pio device monitor -b 115200
```

Serial commands: `b` black | `w` white | `n` next dot | `p` previous dot | `t` test all dots | `h` help
