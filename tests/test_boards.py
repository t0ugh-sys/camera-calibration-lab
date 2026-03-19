from __future__ import annotations

import unittest

from camera_calibration_lab.boards import ChessboardSpec


class ChessboardSpecTests(unittest.TestCase):
    def test_object_points_shape_matches_rows_and_cols(self) -> None:
        spec = ChessboardSpec(rows=6, cols=9, square_size=25.0)

        points = spec.object_points()

        self.assertEqual(points.shape, (54, 3))
        self.assertEqual(points[0].tolist(), [0.0, 0.0, 0.0])
        self.assertEqual(points[1].tolist(), [25.0, 0.0, 0.0])

    def test_validate_rejects_invalid_square_size(self) -> None:
        spec = ChessboardSpec(rows=6, cols=9, square_size=0.0)

        with self.assertRaises(ValueError):
            spec.validate()


if __name__ == '__main__':
    unittest.main()
