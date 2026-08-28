import argparse
import time

from .framebuffer import FrameBuffer
from .protocol import encode_packet


def pattern_frame(width: int, height: int, pattern: str) -> FrameBuffer:
    frame = FrameBuffer(width, height)
    if pattern == "white":
        frame.bits[:] = bytes([1]) * len(frame.bits)
    elif pattern == "checker":
        for y in range(height):
            for x in range(width):
                frame.set(x, y, (x + y) % 2 == 0)
    elif pattern == "border":
        for y in range(height):
            for x in range(width):
                frame.set(x, y, x in (0, width - 1) or y in (0, height - 1))
    elif pattern == "single":
        frame.set(0, 0, True)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a test frame to the ESP32 controller")
    parser.add_argument("port", help="serial port, such as /dev/ttyUSB0 or /dev/cu.usbserial-0001")
    parser.add_argument("--baud", type=int, default=921600)
    parser.add_argument("--modules-x", type=int, default=1)
    parser.add_argument("--modules-y", type=int, default=1)
    parser.add_argument("--pattern", choices=("black", "white", "checker", "border", "single"), default="border")
    args = parser.parse_args()

    try:
        import serial
    except ImportError as error:
        raise SystemExit("Install serial support first: pip install -e '.[serial]'") from error

    width = args.modules_x * 5
    height = args.modules_y * 7
    frame = pattern_frame(width, height, args.pattern)
    payload = frame.to_f30_stream()

    with serial.Serial(args.port, args.baud, timeout=1) as device:
        time.sleep(0.25)
        device.reset_input_buffer()
        device.write(encode_packet(payload))
        device.flush()
        response = device.readline().decode("utf-8", errors="replace").strip()

    print(response or f"sent {len(payload)} bytes; no status response received")


if __name__ == "__main__":
    main()
