from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from camera_calibration_lab.boards import ChessboardSpec
from camera_calibration_lab.mono import MonoCalibrationResult
from camera_calibration_lab.stereo import calibrate_stereo


class StereoCalibrationTests(unittest.TestCase):
    @patch(
        'camera_calibration_lab.stereo.cv2.stereoCalibrate',
        return_value=(
            0.5,
            np.eye(3),
            np.zeros((1, 5)),
            np.eye(3),
            np.zeros((1, 5)),
            np.eye(3),
            np.array([[1.0], [0.0], [0.0]]),
            np.eye(3),
            np.eye(3),
        ),
    )
    @patch(
        'camera_calibration_lab.stereo.pair_stereo_images',
        return_value=[(Path('001.jpg'), Path('001.jpg')), (Path('002.jpg'), Path('002.jpg'))],
    )
    @patch('camera_calibration_lab.stereo._read_corners')
    @patch('camera_calibration_lab.stereo.calibrate_mono')
    def test_calibrate_stereo_reports_used_and_rejected_pairs(
        self,
        calibrate_mono_mock,
        read_corners_mock,
        _pair_stereo_images_mock,
        _stereo_calibrate_mock,
    ) -> None:
        board = ChessboardSpec(rows=6, cols=9, square_size=25.0)
        mono_result = MonoCalibrationResult(
            image_dir='images',
            board={'rows': 6, 'cols': 9, 'square_size': 25.0},
            image_size=(640, 480),
            camera_matrix=np.eye(3),
            distortion_coefficients=np.zeros((1, 5)),
            reprojection_error=0.1,
            total_images=2,
            valid_images=2,
            used_images=['001.jpg', '002.jpg'],
            rejected_images=[],
        )
        calibrate_mono_mock.side_effect = [mono_result, mono_result]
        read_corners_mock.side_effect = [
            ((640, 480), np.zeros((54, 1, 2), dtype=np.float32)),
            ((640, 480), np.zeros((54, 1, 2), dtype=np.float32)),
            None,
            ((640, 480), np.zeros((54, 1, 2), dtype=np.float32)),
        ]

        result = calibrate_stereo(Path('left'), Path('right'), board)

        self.assertEqual(result.total_pairs, 2)
        self.assertEqual(result.valid_pairs, 1)
        self.assertEqual(result.used_pairs, [{'left': '001.jpg', 'right': '001.jpg'}])
        self.assertEqual(
            result.rejected_pairs,
            [{'left': '002.jpg', 'right': '002.jpg', 'reason': 'chessboard_not_found'}],
        )

    @patch('camera_calibration_lab.stereo.calibrate_mono')
    def test_calibrate_stereo_rejects_mismatched_mono_image_sizes(
        self,
        calibrate_mono_mock,
    ) -> None:
        board = ChessboardSpec(rows=6, cols=9, square_size=25.0)
        left_result = MonoCalibrationResult(
            image_dir='left',
            board={'rows': 6, 'cols': 9, 'square_size': 25.0},
            image_size=(640, 480),
            camera_matrix=np.eye(3),
            distortion_coefficients=np.zeros((1, 5)),
            reprojection_error=0.1,
            total_images=1,
            valid_images=1,
            used_images=['001.jpg'],
            rejected_images=[],
        )
        right_result = MonoCalibrationResult(
            image_dir='right',
            board={'rows': 6, 'cols': 9, 'square_size': 25.0},
            image_size=(800, 600),
            camera_matrix=np.eye(3),
            distortion_coefficients=np.zeros((1, 5)),
            reprojection_error=0.1,
            total_images=1,
            valid_images=1,
            used_images=['001.jpg'],
            rejected_images=[],
        )
        calibrate_mono_mock.side_effect = [left_result, right_result]

        with self.assertRaisesRegex(ValueError, 'inconsistent image size'):
            calibrate_stereo(Path('left'), Path('right'), board)


if __name__ == '__main__':
    unittest.main()
