import unittest

from controller_ui.playback import Playback


class PlaybackTests(unittest.TestCase):
    def test_shader_finishes_after_one_performance_by_default(self):
        playback = Playback()
        playback.mode = "shader"
        playback.shader_key = "countdown_pop"
        playback._started_at = 10.0

        self.assertIsNotNone(playback._frame_at(10.0))
        self.assertIsNone(playback._frame_at(14.8))
        self.assertEqual(playback.mode, "idle")

    def test_looping_shader_wraps_instead_of_stopping(self):
        playback = Playback()
        playback.mode = "shader"
        playback.shader_key = "countdown_pop"
        playback.loop = True
        playback._started_at = 10.0

        first = playback._frame_at(10.0)
        wrapped = playback._frame_at(14.8)
        self.assertEqual(first, wrapped)
        self.assertEqual(playback.mode, "shader")

    def test_media_plays_each_frame_once_by_default(self):
        playback = Playback()
        frames = [[[False]], [[True]]]
        playback.mode = "media"
        playback.media_frames = frames

        self.assertIs(playback._frame_at(0), frames[0])
        self.assertIs(playback._frame_at(1), frames[1])
        self.assertIsNone(playback._frame_at(2))
        self.assertEqual(playback.mode, "idle")


if __name__ == "__main__":
    unittest.main()
