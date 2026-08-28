import unittest

from flipdot_mirror import FrameBuffer, encode_packet
from flipdot_mirror.protocol import crc16


class FrameBufferTests(unittest.TestCase):
    def test_single_module_corner_mapping(self):
        frame = FrameBuffer(5, 7)
        frame.set(0, 0)
        frame.set(4, 6)
        stream = frame.to_f30_stream()
        self.assertEqual(len(stream), 35)
        self.assertEqual(stream[34], 0xFF)  # physical dot 35, top-left
        self.assertEqual(stream[0], 0xFF)   # physical dot 1, bottom-right

    def test_full_display_length(self):
        self.assertEqual(len(FrameBuffer().to_f30_stream()), 735)

    def test_logical_transport_order(self):
        frame = FrameBuffer(5, 7)
        frame.set(0, 0)
        frame.set(4, 6)
        payload = frame.to_logical_bytes()
        self.assertEqual(payload[0], 0xFF)
        self.assertEqual(payload[-1], 0xFF)
        self.assertEqual(payload.count(0xFF), 2)

    def test_serpentine_second_row(self):
        frame = FrameBuffer(10, 14)
        frame.set(5, 7)  # top-left of bottom-right logical module
        stream = frame.to_f30_stream(serpentine=True)
        self.assertEqual(stream[70 + 34], 0xFF)

    def test_packet(self):
        payload = bytes([0x00, 0xFF] * 10)
        packet = encode_packet(payload)
        self.assertEqual(packet[:4], b"FDM1")
        self.assertEqual(packet[4:6], len(payload).to_bytes(2, "little"))
        self.assertEqual(packet[-2:], crc16(payload).to_bytes(2, "little"))


if __name__ == "__main__":
    unittest.main()
