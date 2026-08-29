"""Serial link to the flip-dot controller (Nano/ESP32), speaking the FDM1 protocol."""

import threading

import serial
from serial.tools import list_ports

from flipdot_mirror.framebuffer import FrameBuffer
from flipdot_mirror.protocol import encode_packet

# Must match the flashed firmware's DISPLAY_WIDTH/DISPLAY_HEIGHT build flags.
WIDTH = 5
HEIGHT = 7


class Device:
    def __init__(self):
        self._lock = threading.Lock()
        self._serial: serial.Serial | None = None
        self.port: str | None = None
        self.baud: int = 115200
        self.last_status: str = ""
        self.grid: list[list[bool]] = [[False] * WIDTH for _ in range(HEIGHT)]

    def list_ports(self):
        # Exclude bare /dev/ttySN legacy console ports (dozens on this box, none real USB).
        return [
            {"device": p.device, "description": p.description}
            for p in list_ports.comports()
            if p.vid is not None
        ]

    def connect(self, port: str, baud: int = 115200):
        with self._lock:
            if self._serial is not None:
                self._serial.close()
            self._serial = serial.Serial(port, baud, timeout=2)
            self.port, self.baud = port, baud
            # AVR/ESP32 boards reset on port-open (DTR toggle); wait for boot line.
            self._serial.readline()
            self._serial.reset_input_buffer()
            self.last_status = "connected"

    def disconnect(self):
        with self._lock:
            if self._serial is not None:
                self._serial.close()
                self._serial = None
            self.port = None

    @property
    def connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def send_grid(self, grid: list[list[bool]]):
        frame = FrameBuffer(WIDTH, HEIGHT)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                frame.set(x, y, bool(grid[y][x]))
        payload = frame.to_logical_bytes()
        packet = encode_packet(payload)

        with self._lock:
            self.grid = grid
            if self._serial is None:
                return
            self._serial.write(packet)
            self._serial.flush()
            try:
                line = self._serial.readline().decode("utf-8", errors="replace").strip()
                if line:
                    self.last_status = line
            except Exception:
                pass


device = Device()
