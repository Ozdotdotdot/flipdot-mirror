# Mega bench firmware

This is the minimal firmware used to prove open control of the physical sample. It transmits 36 raw NeoPixel-timed bytes; the F30 consumes the first 35 and ignores/forwards the final padding byte.

```text
Mega pin 6 → RJ45 pin 6 / green
Mega GND   → RJ45 pin 3 / white-green
```

Set the F30 to `1 OFF / 2 OFF / 3 ON`. Install dependencies and upload with:

```sh
pio run -t upload
pio device monitor -b 115200
```
