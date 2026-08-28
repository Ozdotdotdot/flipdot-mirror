# Flipdot Mirror

An open hardware and software project for a camera-driven, wall-mounted **35 × 21 mechanical flip-dot mirror**.

The planned display uses 21 F30 modules in a 7 × 3 arrangement. Each module contains 5 × 7 bistable magnetic dots, its own MCU, and H-bridge drivers. A Raspberry Pi turns camera frames into a 735-bit logical image; an ESP32 receives that image, maps it to the physical module chain, and generates the display's 800 kHz single-wire waveform.

```text
camera → Raspberry Pi vision → 35×21 framebuffer → ESP32 → 5V buffer → F30 chain
```

## Current status

- One white/black F30 sample received and inspected.
- Safe 12V bench supply and fused module branch built.
- Automatic factory demonstration passed.
- All 35 dots independently controlled from an Arduino Mega.
- Physical byte order and 800 kHz waveform behavior verified.
- Browser-based 35 × 21 AI silhouette mirror working.
- ESP32 controller and native Raspberry Pi service are the next integration target.

## Repository map

```text
apps/camera-web/             Browser camera and 35×21 preview
firmware/mega-bench/         Proven single-module Arduino test
firmware/esp32-controller/   ESP32 display controller
services/pi-vision/          Native Pi framebuffer and transport foundation
docs/                        Hardware, protocol, architecture, history, roadmap
```

## Read first

- [Project history](docs/project-history.md)
- [System architecture](docs/architecture.md)
- [F30 protocol](docs/f30-protocol.md)
- [Hardware and electrical design](docs/hardware.md)
- [Roadmap and purchase gate](docs/roadmap.md)

## Important safety note

The display uses exposed-terminal AC/DC power supplies and high-current 12V branches. The repository documents the prototype that was built; it is not a substitute for applicable electrical codes, qualified review, strain relief, branch protection, enclosures, grounding, or safe installation practices.

## Privacy and supplier documents

Commercial quotations, contracts, addresses, private chat logs, and supplier-owned PDFs are intentionally excluded. Protocol facts needed to reproduce the controller are summarized here in original language.

## License

MIT. See [LICENSE](LICENSE).
