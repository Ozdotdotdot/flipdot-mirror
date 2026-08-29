# controller-ui

Web UI and shader engine for driving the flip-dot display over the FDM1 serial protocol
(shared with `services/pi-vision`). Grid dimensions (`WIDTH`/`HEIGHT` in `device.py`) must
match whatever `DISPLAY_WIDTH`/`DISPLAY_HEIGHT` the connected controller firmware was built
with (currently 5x7, the single-module bench setup).

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pip install -e ../pi-vision
```

## Run

```sh
.venv/bin/python -m controller_ui.app
```

Serves on `0.0.0.0:8091`. Open `/` for the grid view, shader picker, and media upload.

## Shaders

Sixteen procedural generators live in `shaders.py`. Alongside spatial patterns such as
ripple, swirl, snow drift, and standing-wave interference are five deliberately percussive
sequences: Domino Run makes a single-dot roll, Shutter Clack moves whole rows, SOS Beacon
uses the panel as a mechanical sounder, Countdown Pop ends in a radial burst, and Pinball
alternates quiet two-dot motion with loud border hits. Each is a pure function of
`(x, y, t, width, height)` returning on/off, so it generalizes to the eventual 35x21 wall.

Playback fps is capped at 12 (see `playback.py`) — these are real mechanical relays
flipping, not screen pixels, so the frame rate is deliberately conservative.
Shaders and uploaded media play once by default. Enable **loop playback** in the control
panel to repeat the current item; the same setting is applied when starting another shader
or uploading media.

## Media upload

Accepts images, animated GIFs, and video files. Images/GIF frames are resize-cropped to
the grid and converted with PIL's Floyd-Steinberg dithering (`Image.convert('1')`) to fake
grayscale on a binary display. Video is demuxed via `ffmpeg` at 6fps first, then run
through the same per-frame conversion.
