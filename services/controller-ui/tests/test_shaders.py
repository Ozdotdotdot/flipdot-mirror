import unittest

from controller_ui import shaders


class ShaderTests(unittest.TestCase):
    def test_every_shader_renders_binary_grids_at_both_target_sizes(self):
        for key in shaders.SHADERS:
            for width, height in ((5, 7), (35, 21)):
                with self.subTest(shader=key, size=(width, height)):
                    grid = shaders.render(key, 1.234, width, height)
                    self.assertEqual(len(grid), height)
                    self.assertTrue(all(len(row) == width for row in grid))
                    self.assertTrue(all(type(dot) is bool for row in grid for dot in row))

    def test_domino_run_advances_one_dot_at_a_time(self):
        counts = [
            sum(map(sum, shaders.render("domino_run", step * 0.11, 5, 7)))
            for step in range(4)
        ]
        self.assertEqual(counts, [1, 2, 3, 4])

    def test_sos_starts_with_three_short_pulses(self):
        states = [shaders.sos_beacon(0, 0, unit * 0.22, 5, 7) for unit in range(8)]
        self.assertEqual(states, [True, False, True, False, True, False, False, False])

    def test_countdown_has_a_rest_after_the_burst(self):
        self.assertGreater(sum(map(sum, shaders.render("countdown_pop", 0, 5, 7))), 0)
        self.assertEqual(sum(map(sum, shaders.render("countdown_pop", 4.0, 5, 7))), 0)


if __name__ == "__main__":
    unittest.main()
