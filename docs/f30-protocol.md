# F30 protocol notes

These facts were established from supplier engineering documents and verified on the physical sample.

## Module

- Matrix: 5 columns × 7 rows = 35 dots.
- Nominal module power: 12V DC, approximately 84W maximum.
- Dot values: `0x00` = black; `0xFF` = white.
- Avoid intermediate byte values; they may repeatedly drive the mechanism.
- Dots retain their state without power.

## Single-wire input

The supplier calls this input “SPI,” but it is not conventional clocked SPI. It is an approximately 800 kHz, one-data-wire, pulse-width-encoded stream resembling WS281x signaling.

- Logic level expected by module: 5V.
- One complete module frame: exactly 35 bytes.
- Each byte is sent most-significant bit first.
- Nominal bit period: approximately 1.25–1.3µs.
- Logical zero: approximately 0.4µs high, then low.
- Logical one: approximately 0.8–0.85µs high, then low.
- Hold data low for more than 24µs to latch the frame.
- A module consumes its first 35 bytes and forwards the remaining stream.
- Twenty-one modules consume exactly 735 bytes.
- Supplier recommends no more than 29 modules on one chain.

## RJ45 assignments (T568B conductor convention)

| Pin | T568B conductor | F30 function |
|---:|---|---|
| 1 | white/orange | DMX B |
| 2 | orange | DMX A |
| 3 | white/green | signal ground |
| 4 | blue | proprietary DMX address chain |
| 5 | white/blue | ground |
| 6 | green | single-wire data |
| 7 | white/brown | ground |
| 8 | brown | ground |

The connector is **not Ethernet**. Never connect it to a network adapter, router, or switch.

## Module-local byte order

Viewed from the front, upright, with dot 1 at bottom-right:

```text
35 34 33 32 31
30 29 28 27 26
25 24 23 22 21
20 19 18 17 16
15 14 13 12 11
10 09 08 07 06
05 04 03 02 01
```

In zero-based software, logical module coordinate `(x, y)` measured from the top-left maps to:

```text
byte_index = 34 - (y * 5) - x
```

## DMX fallback

- One channel per dot; 35 channels per module.
- `0` = black; `255` = white.
- Addresses are not assigned automatically.
- Twenty-one modules require 735 channels and therefore two DMX universes.
- The sample's programmed start address is 001.
