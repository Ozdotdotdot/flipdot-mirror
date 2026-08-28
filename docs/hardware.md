# Hardware

## Sample bench system

- XQD F30 5 × 7 module, white/black.
- Mean Well LRS-350-12, 12V/29A.
- Grounded three-conductor AC pigtail connected to `L`, `N`, and `FG`.
- 10A ATC/ATO fuse in the module's red `+12V` branch.
- Supplier VH3.96-2P power cable, 2 × 0.75mm².
- Arduino Mega for the proven 5V waveform test.
- Cut T568B cable: pin 6 data, pin 3 signal ground.

## ESP32 level shifter

The ESP32 is 3.3V logic. Use one channel of an SN74AHCT125 powered at 5V:

| SN74AHCT125 pin | Connection |
|---:|---|
| 1 (`1OE`) | GND; enables channel 1 |
| 2 (`1A`) | ESP32 GPIO18 |
| 3 (`1Y`) | F30 RJ45 pin 6 |
| 7 | GND |
| 14 | 5V |

Also connect ESP32 ground to RJ45 pin 3. Place a 0.1µF ceramic capacitor directly between pins 14 and 7. Tie unused output-enable pins 4, 10, and 13 high to 5V so unused channels remain disabled.

The capacitor is local energy storage and high-frequency noise suppression for the logic IC. It is not part of the voltage conversion itself.

## Planned full display

- 21 modules arranged 7 × 3.
- Logical resolution: 35 × 21 = 735 dots.
- Approximate active dimensions: 1118.6 × 668.4mm.
- Approximate module mass: 22.05kg / 48.6lb total.
- Seven installed LRS-350 supplies add about 5.32kg / 11.7lb.
- Expected complete installation with frame and distribution: roughly 75–100lb.

The supplier estimated approximately 1800W only in the pathological case where all mechanisms flip simultaneously; normal animations were estimated near half that. AC distribution, branch breakers, fusing, grounding, enclosure, thermal behavior, and household-circuit loading require a complete design before the full wall installation.

## Mechanical direction

A promising structure is a wall-mounted master frame accepting three serviceable 7 × 1 module rows. Each row would weigh roughly 22–30lb including its share of power hardware. Datum surfaces, locating pins, and fine adjustment must keep the two horizontal seams visually gapless.
