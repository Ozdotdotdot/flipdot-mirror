import unittest

from flipdot_mirror.send import pattern_frame


class TestPatterns(unittest.TestCase):
    def test_white_module(self):
        payload = pattern_frame(5, 7, "white").to_f30_stream()
        self.assertEqual(payload, bytes([0xFF]) * 35)

    def test_border_module(self):
        payload = pattern_frame(5, 7, "border").to_f30_stream()
        self.assertEqual(len(payload), 35)
        self.assertEqual(payload.count(0xFF), 20)

    def test_final_display_size(self):
        payload = pattern_frame(35, 21, "black").to_f30_stream()
        self.assertEqual(len(payload), 735)


if __name__ == "__main__":
    unittest.main()
