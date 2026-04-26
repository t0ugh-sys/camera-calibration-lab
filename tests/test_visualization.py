from __future__ import annotations

import json
import unittest
from pathlib import Path

import cv2
import numpy as np

from camera_calibration_lab.boards import ChessboardSpec
from camera_calibration_lab.visualization import batch_visualize_corners, load_calibration, visualize_undistort


class VisualizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace = Path(__file__).resolve().parents[1] / '.tmp_tests' / self._testMethodName
        self.workspace.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        for path in sorted(self.workspace.rglob('*'), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        if self.workspace.exists():
            self.workspace.rmdir()

    def test_load_calibration_reads_matrix_and_distortion(self) -> None:
        calibration_path = self.workspace / 'mono.json'
        calibration_path.write_text(
            json.dumps(
                {
                    'camera_matrix': [[1.0, 0.0, 2.0], [0.0, 3.0, 4.0], [0.0, 0.0, 1.0]],
                    'distortion_coefficients': [[0.1, 0.2, 0.0, 0.0, 0.0]],
                }
            ),
            encoding='utf-8',
        )

        camera_matrix, distortion = load_calibration(calibration_path)

        self.assertEqual(camera_matrix.shape, (3, 3))
        self.assertEqual(distortion.shape, (1, 5))

    def test_visualize_undistort_saves_side_by_side_image(self) -> None:
        image_path = self.workspace / 'image.jpg'
        image = np.full((20, 30, 3), 127, dtype=np.uint8)
        cv2.imwrite(str(image_path), image)

        calibration_path = self.workspace / 'mono.json'
        calibration_path.write_text(
            json.dumps(
                {
                    'camera_matrix': [[20.0, 0.0, 15.0], [0.0, 20.0, 10.0], [0.0, 0.0, 1.0]],
                    'distortion_coefficients': [[0.0, 0.0, 0.0, 0.0, 0.0]],
                }
            ),
            encoding='utf-8',
        )
        output_path = self.workspace / 'undistort.jpg'

        comparison = visualize_undistort(image_path, calibration_path, output_path)

        self.assertTrue(output_path.exists())
        self.assertEqual(comparison.shape, (20, 60, 3))

    def test_chessboard_spec_is_available_for_visualization_commands(self) -> None:
        board = ChessboardSpec(rows=8, cols=11, square_size=1.5)

        self.assertEqual(board.pattern_size, (11, 8))

    def test_batch_visualize_corners_writes_summary_for_images(self) -> None:
        image_dir = self.workspace / 'images'
        image_dir.mkdir()
        image_path = image_dir / 'sample.jpg'
        cv2.imwrite(str(image_path), np.zeros((20, 20, 3), dtype=np.uint8))

        board = ChessboardSpec(rows=8, cols=11, square_size=1.5)
        output_dir = self.workspace / 'outputs'
        summary_path = self.workspace / 'summary.json'

        summary = batch_visualize_corners(image_dir, board, output_dir, summary_path)

        self.assertEqual(summary['total_images'], 1)
        self.assertEqual(summary['success_count'], 0)
        self.assertTrue(summary_path.exists())

    def test_batch_visualize_corners_can_skip_image_export(self) -> None:
        image_dir = self.workspace / 'images_skip'
        image_dir.mkdir()
        image_path = image_dir / 'sample.jpg'
        cv2.imwrite(str(image_path), np.zeros((20, 20, 3), dtype=np.uint8))

        board = ChessboardSpec(rows=8, cols=11, square_size=1.5)
        output_dir = self.workspace / 'outputs_skip'

        summary = batch_visualize_corners(image_dir, board, output_dir, visualize=False)

        self.assertFalse(output_dir.exists())
        self.assertFalse(summary['visualize'])
        self.assertIsNone(summary['results'][0]['output'])


if __name__ == '__main__':
    unittest.main()
