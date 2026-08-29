"""Background playback loop: drives shaders or uploaded-media sequences to the device."""

import threading
import time

from . import shaders
from .device import HEIGHT, WIDTH, device

# Real mechanical relays are flipping here, not pixels on a screen. Cap fps low
# so playback stays within a flip-dot's actual actuation speed.
MIN_FPS = 1
MAX_FPS = 12
DEFAULT_FPS = 6


class Playback:
    def __init__(self):
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self.mode: str = "idle"  # idle | shader | media
        self.shader_key: str | None = None
        self.loop: bool = False
        self.fps: float = DEFAULT_FPS
        self.media_frames: list[list[list[bool]]] = []
        self.media_index: int = 0
        self.media_name: str | None = None
        self._started_at: float = 0.0

    def _run(self):
        while not self._stop.is_set():
            frame_start = time.monotonic()
            grid = self._frame_at(frame_start)
            if grid is None:
                time.sleep(0.1)
                continue
            device.send_grid(grid)

            elapsed = time.monotonic() - frame_start
            time.sleep(max(0.0, 1.0 / self.fps - elapsed))

    def _frame_at(self, now: float):
        """Return the next frame, or finish a non-looping performance."""
        if self.mode == "shader" and self.shader_key:
            t = now - self._started_at
            duration = shaders.SHADER_DURATIONS[self.shader_key]
            if not self.loop and t >= duration:
                self.mode = "idle"
                return None
            if self.loop:
                t %= duration
            return shaders.render(self.shader_key, t, WIDTH, HEIGHT)

        if self.mode == "media" and self.media_frames:
            if not self.loop and self.media_index >= len(self.media_frames):
                self.mode = "idle"
                return None
            grid = self.media_frames[self.media_index % len(self.media_frames)]
            self.media_index += 1
            return grid

        return None

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def play_shader(self, key: str, fps: float | None = None, loop: bool = False):
        if key not in shaders.SHADERS:
            raise ValueError(f"unknown shader: {key}")
        self.mode = "shader"
        self.shader_key = key
        self.loop = loop
        self._started_at = time.monotonic()
        if fps is not None:
            self.fps = max(MIN_FPS, min(MAX_FPS, fps))
        self.start()

    def play_media(
        self,
        frames: list[list[list[bool]]],
        name: str,
        fps: float | None = None,
        loop: bool = False,
    ):
        self.mode = "media"
        self.media_frames = frames
        self.media_index = 0
        self.media_name = name
        self.loop = loop
        self._started_at = time.monotonic()
        if fps is not None:
            self.fps = max(MIN_FPS, min(MAX_FPS, fps))
        self.start()

    def stop(self):
        self.mode = "idle"

    def status(self):
        return {
            "mode": self.mode,
            "shader": self.shader_key if self.mode == "shader" else None,
            "media": self.media_name if self.mode == "media" else None,
            "fps": self.fps,
            "loop": self.loop,
        }


playback = Playback()
