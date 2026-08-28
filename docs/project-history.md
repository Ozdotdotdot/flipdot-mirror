# Project history

## The idea

The project began after seeing a flip-dot display in a coffee shop and wanting a similarly tactile, audible information surface for a bedroom. Commercial art pieces and completed displays were striking but frequently cost five figures; used transit panels were scarce, inconsistent, and difficult to source.

## Sourcing

European modular hardware established a useful quality and documentation benchmark, but a 50-inch build at the desired resolution remained expensive. Direct sourcing from Shenzhen made a custom-scale project plausible. The supplier conversation established that the F30 was not a bare electromagnetic matrix: every 5 × 7 module includes logic processing, an MCU, and H-bridge drivers.

The inquiry evolved from broad questions about matrix dimensions and controller compatibility into concrete engineering questions:

- individual-dot control;
- DMX512 channel mapping and addressing;
- multiple-universe behavior above 512 channels;
- single-wire voltage, timing, byte order, latching, and daisy chaining;
- power topology, peak consumption, cables, and connectors;
- white active face with black inactive face;
- DDP shipping and a protected sample transaction.

## Sample purchase and bring-up

A single F30 sample was purchased through Alibaba Trade Assurance for roughly USD 241 landed. The supplier factory-tested it, provided technical attachments, and shipped it through 3PE/Fly Rabbit with UPS last-mile delivery. It traveled from Shenzhen to metro Atlanta in only a few days.

One disc arrived detached and was reinstalled during the recorded unboxing. The module otherwise passed its automatic demonstration. The electrical bring-up required learning and applying:

- grounded AC pigtail construction;
- fork-terminal selection and ratcheting crimping;
- protective earth, line, and neutral identification by continuity;
- a terminal guard for an enclosed Mean Well supply;
- a fused 12V branch for the module cable;
- multimeter verification before connecting the load;
- the distinction between an RJ45 connector and Ethernet signaling.

## Open control achieved

Although the module accepts DMX512, the better fit for the final installation is its 5V, 800 kHz single-wire daisy-chain input. A Mega 2560 produced the required waveform using a raw NeoPixel-compatible byte stream. The first controlled frame reset all dots to black; subsequent commands addressed every dot independently and rapidly. This confirmed the supplier's documentation and removed the proprietary XiXun controller from the required architecture.

## Vision prototype

A browser prototype established the logical 35 × 21 canvas before the complete display existed. Simple luminance dithering lost the subject at this resolution. The successful pipeline uses lightweight on-device person segmentation, pose-based limb reinforcement, area-coverage downsampling, and per-dot hysteresis. It preserves arms and gestures much better than naive dithering or background subtraction.

## Where the project is now

The proven bench experiment is becoming a maintainable system:

- Raspberry Pi 4B: native camera/vision processing;
- ESP32: deterministic display timing and hardware abstraction;
- SN74AHCT125: 3.3V-to-5V signal conversion;
- 21 F30 modules: 35 × 21 physical framebuffer;
- seven or eight Mean Well LRS-350-12 supplies with protected distribution;
- a sectional, serviceable wall frame.
