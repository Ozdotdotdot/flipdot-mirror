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
}


def render(shader_key: str, t: float, width: int, height: int) -> list[list[bool]]:
    fn = SHADERS[shader_key][1]
    return [[fn(x, y, t, width, height) for x in range(width)] for y in range(height)]
