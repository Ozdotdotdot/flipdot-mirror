# Roadmap and purchase gate

## Immediate

- [ ] Drive the sample from ESP32 GPIO18 through the SN74AHCT125.
- [ ] Verify all-black, single-dot, all-dot, and rapid animation frames.
- [ ] Run a supervised one-hour repeating-pattern soak test.
- [ ] Confirm the previously detached disc remains secure.
- [ ] Measure rough current behavior for representative transitions.
- [ ] Connect the Python framebuffer sender to the ESP32 over USB serial.
- [ ] Port the browser segmentation decisions into a headless Pi service.

## Before ordering 21 modules plus spares

- [ ] Receive a satisfactory supplier response about the detached disc and cosmetic wear.
- [ ] Require new-production white/black modules and documented pre-shipment testing.
- [ ] Confirm final quantities: 21 production modules plus 2 spares.
- [ ] Confirm seven operating LRS-350-12 supplies plus one spare, or obtain the supplier's final grouping diagram.
- [ ] Confirm every module includes its 0.3m RJ45 and 0.5m fused-branch-compatible DC lead.
- [ ] Obtain final DDP total and Trade Assurance terms in writing.
- [ ] Complete a preliminary sectional-frame and service-access design.
- [ ] Complete household AC load and distribution review.
- [ ] Decide whether a second sample is worthwhile for real two-module daisy-chain testing.

## Recommendation

Do **not** place the full order merely because the Mega test succeeded. The sample has passed the core technical risk—open individual control—but the next inexpensive gate is ESP32 + level-shifter control and a short reliability soak. Once those pass and the supplier addresses sample condition, the project will have enough evidence to make the full purchase rational.

## Later

- Multi-module serpentine mapping.
- WebSocket commissioning UI hosted by ESP32.
- Raspberry Pi 4B native segmentation and pose pipeline.
- Differential-only updates and transition choreography.
- Sectional frame prototype.
- Protected AC/DC distribution enclosure.
- Camera selection and final optical placement.
- Installation, calibration, and long-duration reliability testing.
