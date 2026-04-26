from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from camera_calibration_lab.boards import ChessboardSpec
from camera_calibration_lab.mono import calibrate_mono


class MonoCalibrationTests(unittest.TestCase):
    @patch('camera_calibration_lab.mono._compute_reprojection_error', return_value=0.25)
    @patch(
        'camera_calibration_lab.mono.cv2.calibrateCamera',
        return_value=(1.0, np.eye(3), np.zeros((1, 5)), [], []),
    )
    @patch(
        'camera_calibration_lab.mono.list_image_files',
        return_value=[Path('001.jpg'), Path('002.jpg')],
    )
    @patch('camera_calibration_lab.mono._find_corners')
    def test_calibrate_mono_reports_used_and_rejected_images(
        self,
        find_corners_mock,
        _list_image_files_mock,
        _calibrate_camera_mock,
        _reprojection_error_mock,
    ) -> None:
        board = ChessboardSpec(rows=6, cols=9, square_size=25.0)
        find_corners_mock.side_effect = [
            ((640, 480), np.zeros((54, 1, 2), dtype=np.float32)),
            None,
        ]

        result = calibrate_mono(Path('images'), board)

        self.assertEqual(result.total_images, 2)
        self.assertEqual(result.valid_images, 1)
        self.assertEqual(result.used_images, ['001.jpg'])
        self.assertEqual(result.rejected_images, ['002.jpg'])
        self.assertEqual(result.as_dict()['board'], {'rows': 6, 'cols': 9, 'square_size': 25.0})

    @patch(
        'camera_calibration_lab.mono.list_image_files',
        return_value=[Path('001.jpg'), Path('002.jpg')],
    )
    @patch('camera_calibration_lab.mono._find_corners')
    def test_calibrate_mono_rejects_inconsistent_image_sizes(
        self,
        find_corners_mock,
        _list_image_files_mock,
    ) -> None:
        board = ChessboardSpec(rows=6, cols=9, square_size=25.0)
        find_corners_mock.side_effect = [
            ((640, 480), np.zeros((54, 1, 2), dtype=np.float32)),
            ((800, 600), np.zeros((54, 1, 2), dtype=np.float32)),
        ]

        with self.assertRaisesRegex(ValueError, 'inconsistent image size'):
            calibrate_mono(Path('images'), board)


if __name__ == '__main__':
    unittest.main()
