"""Convert uploaded images/GIFs/video into dot-grid frame sequences.

Uses PIL's built-in Floyd-Steinberg dithering (Image.convert('1')) to fake
grayscale on the binary display, and ffmpeg to pull frames out of video files.
"""

import io
import pathlib
import subprocess
import tempfile

from PIL import Image, ImageOps, ImageSequence

from .device import HEIGHT, WIDTH

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"}
MAX_FRAMES = 300
EXTRACT_FPS = 6


def _frame_to_grid(img: Image.Image) -> list[list[bool]]:
    fitted = ImageOps.fit(img.convert("RGB"), (WIDTH, HEIGHT), method=Image.LANCZOS)
    dithered = fitted.convert("L").convert("1")
    pixels = dithered.load()
    return [[bool(pixels[x, y]) for x in range(WIDTH)] for y in range(HEIGHT)]


def _convert_video(data: bytes) -> list[list[list[bool]]]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        input_path = tmp_path / "input"
        input_path.write_bytes(data)
        out_pattern = tmp_path / "frame_%04d.png"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(input_path),
                "-vf", f"fps={EXTRACT_FPS}",
                "-frames:v", str(MAX_FRAMES),
                str(out_pattern),
            ],
            check=True,
            capture_output=True,
        )
        return [_frame_to_grid(Image.open(p)) for p in sorted(tmp_path.glob("frame_*.png"))]


def convert_upload(data: bytes, filename: str) -> tuple[list[list[list[bool]]], float]:
    """Returns (frames, suggested_fps)."""
    ext = pathlib.Path(filename).suffix.lower()
    if ext in VIDEO_EXTENSIONS:
        return _convert_video(data), float(EXTRACT_FPS)

    img = Image.open(io.BytesIO(data))
    if getattr(img, "is_animated", False):
        frames = []
        for frame in ImageSequence.Iterator(img):
            frames.append(_frame_to_grid(frame))
            if len(frames) >= MAX_FRAMES:
                break
        return frames, float(EXTRACT_FPS)

    return [_frame_to_grid(img)], float(EXTRACT_FPS)
