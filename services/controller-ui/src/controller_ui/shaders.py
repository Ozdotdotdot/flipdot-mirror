"""Procedural generators for the flip-dot grid.

Each shader is `f(x, y, t, width, height) -> bool`, evaluated per-dot per-frame.
Designed by Fable for a binary, mechanically-flipped medium: rhythm and clacking
cadence matter more than smoothness, so playback fps is intentionally low (see
playback.py). Coordinates generalize from the current 5x7 single module to the
eventual 35x21 wall.
"""

import hashlib
import math
import random

BAYER_4X4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
]


def ripple(x, y, t, width, height):
    cx, cy = (width - 1) / 2, (height - 1) / 2
    dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    wave_speed, wavelength = 3.0, 2.2
    phase = (dist - wave_speed * t) / wavelength
    return (phase % 1.0) < 0.5


def ember_static(x, y, t, width, height):
    frame = int(t * 6)
    h = int(hashlib.md5(f"{x}-{y}-{frame}".encode()).hexdigest(), 16)
    rand_val = (h % 1000) / 1000.0
    density = 0.35 + 0.25 * (0.5 + 0.5 * math.sin(t * 1.3))
    return rand_val < density


def bayer_fade(x, y, t, width, height):
    level = 0.5 + 0.5 * math.sin(t * 0.4)
    threshold = BAYER_4X4[y % 4][x % 4] / 16.0
    return level > threshold


def gear_sweep(x, y, t, width, height):
    cx, cy = (width - 1) / 2, (height - 1) / 2
    angle = math.atan2(y - cy, x - cx)
    sweep_angle = (t * 1.2) % (2 * math.pi)
    diff = (angle - sweep_angle + math.pi) % (2 * math.pi) - math.pi
    return abs(diff) < 0.5


_life_cache = {}


def _seed_state(width, height):
    rng = random.Random(42)
    return {(x, y) for x in range(width) for y in range(height) if rng.random() < 0.35}


def _life_step(state, width, height):
    def neighbors(x, y):
        return sum(
            (x + dx, y + dy) in state
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not (dx == 0 and dy == 0)
        )

    new_state = set()
    for x in range(width):
        for y in range(height):
            n = neighbors(x, y)
            alive = (x, y) in state
            if alive and n in (2, 3):
                new_state.add((x, y))
            elif not alive and n == 3:
                new_state.add((x, y))
    return new_state or _seed_state(width, height)


def conway_clack(x, y, t, width, height):
    gen_duration = 0.8
    generation = int(t / gen_duration)
    key = (width, height)
    cache = _life_cache.setdefault(key, {0: _seed_state(width, height)})
    max_gen = max(cache.keys())
    while max_gen < generation:
        cache[max_gen + 1] = _life_step(cache[max_gen], width, height)
        max_gen += 1
    return (x, y) in cache[generation]


def pulse_heart(x, y, t, width, height):
    cx, cy = (width - 1) / 2, (height - 1) / 2
    dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
    max_dist = (cx**2 + cy**2) ** 0.5 or 1.0

    beat_period = 1.6
    phase = (t % beat_period) / beat_period
    if phase < 0.12:
        thump = 1.0
    elif 0.18 <= phase < 0.28:
        thump = 0.7
    else:
        thump = 0.0

    radius_frac = 0.25 + 0.55 * thump
    return dist <= radius_frac * max_dist


def curtain_wipe(x, y, t, width, height):
    diag = width + height
    speed = 4.0
    cycle = 2 * diag / speed
    progress = (t % cycle) / cycle * 2 * diag
    if progress > diag:
        progress = 2 * diag - progress
    return (x + y) < progress


def snow_drift(x, y, t, width, height):
    fall_speed = 1.5
    n_flakes = max(3, width)
    for i in range(n_flakes):
        h = int(hashlib.md5(f"flake-{i}".encode()).hexdigest(), 16)
        flake_x = h % width
        phase_offset = (h // width) % 100 / 100.0 * height
        flake_y = (fall_speed * t + phase_offset) % height
        if x == flake_x and abs(y - flake_y) < 0.6:
            return True
    return False


def checker_breath(x, y, t, width, height):
    flip_period = 1.2
    flip_index = int(t / flip_period)
    base = (x + y) % 2 == 0
    return base if flip_index % 2 == 0 else not base


def swirl(x, y, t, width, height):
    cx, cy = (width - 1) / 2, (height - 1) / 2
    dx, dy = x - cx, y - cy
    dist = (dx * dx + dy * dy) ** 0.5
    angle = math.atan2(dy, dx)
    arms = 2
    twist = 2.5       # how tightly the arms wind per unit distance
    spin_speed = 6.0  # radians/sec
    phase = angle * arms + dist * twist - t * spin_speed
    return math.sin(phase) > 0


def standing_wave(x, y, t, width, height):
    src1, src2 = (0, 0), (width - 1, height - 1)
    speed, wavelength = 2.5, 2.0
    d1 = ((x - src1[0]) ** 2 + (y - src1[1]) ** 2) ** 0.5
    d2 = ((x - src2[0]) ** 2 + (y - src2[1]) ** 2) ** 0.5
    w1 = math.sin(2 * math.pi * (d1 / wavelength - speed * t))
    w2 = math.sin(2 * math.pi * (d2 / wavelength - speed * t))
    return (w1 + w2) > 0.3


def domino_run(x, y, t, width, height):
    """Walk a single change through a serpentine path, then walk it back.

    Most frames make exactly one new mechanical click.  The short pauses at the
    two ends make the direction change legible by ear as well as by eye.
    """
    cells = max(1, width * height)
    step_time = 0.11
    pause_steps = 5
    phase = int(t / step_time) % (2 * cells + 2 * pause_steps)
    if phase < cells:
        filled = phase + 1
    elif phase < cells + pause_steps:
        filled = cells
    elif phase < 2 * cells + pause_steps:
        filled = 2 * cells + pause_steps - phase - 1
    else:
        filled = 0

    path_x = x if y % 2 == 0 else width - 1 - x
    return y * width + path_x < filled


def shutter_clack(x, y, t, width, height):
    """Close horizontal slats in a roll, hold, then reopen them in reverse."""
    beat = 0.18
    pause = 4
    phase = int(t / beat) % (2 * height + 2 * pause)
    if phase < height:
        closed_rows = phase + 1
    elif phase < height + pause:
        closed_rows = height
    elif phase < 2 * height + pause:
        closed_rows = 2 * height + pause - phase - 1
    else:
        closed_rows = 0
    return y < closed_rows


# A whole-panel light is an unusually forceful sound on flip-dot hardware.  SOS
# gives that sound a familiar phrase instead of using it as undifferentiated noise.
_SOS_UNITS = (
    True, False, True, False, True, False, False, False,       # S
    True, True, True, False, True, True, True, False,
    True, True, True, False, False, False,                      # O
    True, False, True, False, True, False, False, False, False, False,
)


def sos_beacon(x, y, t, width, height):
    """Flash an endlessly repeating SOS with one time unit per 0.22 seconds."""
    return _SOS_UNITS[int(t / 0.22) % len(_SOS_UNITS)]


_COUNTDOWN_GLYPHS = {
    "3": ("111", "001", "111", "001", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "1": ("010", "110", "010", "010", "111"),
}


def countdown_pop(x, y, t, width, height):
    """Count 3-2-1, then fire a brief radial burst and take a breath."""
    phase = t % 4.8
    if phase < 3.0:
        glyph = _COUNTDOWN_GLYPHS[str(3 - int(phase))]
        scale = max(1, min(width // 3, height // 5))
        glyph_w, glyph_h = 3 * scale, 5 * scale
        left, top = (width - glyph_w) // 2, (height - glyph_h) // 2
        gx, gy = (x - left) // scale, (y - top) // scale
        return (
            left <= x < left + glyph_w
            and top <= y < top + glyph_h
            and glyph[gy][gx] == "1"
        )
    if phase < 3.65:
        cx, cy = (width - 1) / 2, (height - 1) / 2
        distance = math.hypot(x - cx, y - cy)
        radius = (phase - 3.0) / 0.65 * math.hypot(cx, cy)
        return abs(distance - radius) < 0.75
    return False


def pinball(x, y, t, width, height):
    """A two-click travelling ball punctuated by loud bumper impacts."""
    frame = int(t * 6)
    span_x, span_y = max(1, 2 * (width - 1)), max(1, 2 * (height - 1))

    def bounce(step, span, size):
        p = step % span
        return p if p < size else span - p

    ball_x = bounce(frame, span_x, width)
    ball_y = bounce(frame * 2 + 1, span_y, height)
    impact = frame % 17 == 0
    border = x in (0, width - 1) or y in (0, height - 1)
    return (x == ball_x and y == ball_y) or (impact and border)


SHADERS = {
    "ripple": ("Ripple", ripple),
    "ember_static": ("Ember Static", ember_static),
    "bayer_fade": ("Bayer Fade", bayer_fade),
    "gear_sweep": ("Gear Sweep", gear_sweep),
    "conway_clack": ("Conway Clack", conway_clack),
    "pulse_heart": ("Pulse Heart", pulse_heart),
    "curtain_wipe": ("Curtain Wipe", curtain_wipe),
    "snow_drift": ("Static Snow Drift", snow_drift),
    "checker_breath": ("Checker Breath", checker_breath),
    "standing_wave": ("Standing Wave Interference", standing_wave),
    "swirl": ("Swirl", swirl),
    "domino_run": ("Domino Run", domino_run),
    "shutter_clack": ("Shutter Clack", shutter_clack),
    "sos_beacon": ("SOS Beacon", sos_beacon),
    "countdown_pop": ("Countdown Pop", countdown_pop),
    "pinball": ("Pinball", pinball),
}


def render(shader_key: str, t: float, width: int, height: int) -> list[list[bool]]:
    fn = SHADERS[shader_key][1]
    return [[fn(x, y, t, width, height) for x in range(width)] for y in range(height)]
