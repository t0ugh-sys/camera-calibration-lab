from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .boards import ChessboardSpec
from .io_utils import ensure_consistent_image_size, pair_stereo_images
from .mono import MonoCalibrationResult, calibrate_mono


@dataclass
class StereoCalibrationResult:
    left_image_dir: str
    right_image_dir: str
    board: dict[str, float | int]
    image_size: tuple[int, int]
    left_camera_matrix: np.ndarray
    left_distortion_coefficients: np.ndarray
    right_camera_matrix: np.ndarray
    right_distortion_coefficients: np.ndarray
    rotation_matrix: np.ndarray
    translation_vector: np.ndarray
    essential_matrix: np.ndarray
    fundamental_matrix: np.ndarray
    stereo_error: float
    total_pairs: int
    valid_pairs: int
    used_pairs: list[dict[str, str]]
    rejected_pairs: list[dict[str, str]]

    def as_dict(self) -> dict[str, object]:
        return {
            'left_image_dir': self.left_image_dir,
            'right_image_dir': self.right_image_dir,
            'board': self.board,
            'image_size': list(self.image_size),
            'left_camera_matrix': self.left_camera_matrix,
            'left_distortion_coefficients': self.left_distortion_coefficients,
            'right_camera_matrix': self.right_camera_matrix,
            'right_distortion_coefficients': self.right_distortion_coefficients,
            'rotation_matrix': self.rotation_matrix,
            'translation_vector': self.translation_vector,
            'essential_matrix': self.essential_matrix,
            'fundamental_matrix': self.fundamental_matrix,
            'stereo_error': self.stereo_error,
            'total_pairs': self.total_pairs,
            'valid_pairs': self.valid_pairs,
            'used_pairs': self.used_pairs,
            'rejected_pairs': self.rejected_pairs,
        }


def _read_corners(
    image_path: Path,
    board: ChessboardSpec,
) -> tuple[tuple[int, int], np.ndarray] | None:
    image = cv2.imread(str(image_path))
    if image is None:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, board.pattern_size)
    if not found:
        return None

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.001,
    )
    refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    return (gray.shape[1], gray.shape[0]), refined


def calibrate_stereo(left_dir: Path, right_dir: Path, board: ChessboardSpec) -> StereoCalibrationResult:
    board.validate()
    left_mono = calibrate_mono(left_dir, board)
    right_mono = calibrate_mono(right_dir, board)
    reference_image_size = _ensure_matching_mono_sizes(left_mono, right_mono)
    pairs = pair_stereo_images(left_dir, right_dir)

    object_points: list[np.ndarray] = []
    left_points: list[np.ndarray] = []
    right_points: list[np.ndarray] = []
    image_size: tuple[int, int] | None = None
    template_points = board.object_points()
    used_pairs: list[dict[str, str]] = []
    rejected_pairs: list[dict[str, str]] = []

    for left_path, right_path in pairs:
        left_detected = _read_corners(left_path, board)
        right_detected = _read_corners(right_path, board)
        if left_detected is None or right_detected is None:
            rejected_pairs.append(
                {
                    'left': left_path.name,
                    'right': right_path.name,
                    'reason': 'chessboard_not_found',
                }
            )
            continue

        left_size, left_corners = left_detected
        right_size, right_corners = right_detected
        if left_size != right_size:
            raise ValueError(f'image size mismatch: {left_path.name} vs {right_path.name}')

        reference_image_size = ensure_consistent_image_size(
            reference_image_size,
            left_size,
            left_path.name,
        )
        image_size = ensure_consistent_image_size(image_size, left_size, left_path.name)
        object_points.append(template_points.copy())
        left_points.append(left_corners)
        right_points.append(right_corners)
        used_pairs.append({'left': left_path.name, 'right': right_path.name})

    if image_size is None or not left_points or not right_points:
        raise ValueError('no valid stereo chessboard detections found')

    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        100,
        1e-5,
    )
    flags = cv2.CALIB_FIX_INTRINSIC

    stereo_error, left_camera_matrix, left_distortion, right_camera_matrix, right_distortion, rotation, translation, essential, fundamental = cv2.stereoCalibrate(
        object_points,
        left_points,
        right_points,
        left_mono.camera_matrix,
        left_mono.distortion_coefficients,
        right_mono.camera_matrix,
        right_mono.distortion_coefficients,
        image_size,
        criteria=criteria,
        flags=flags,
    )

    return StereoCalibrationResult(
        left_image_dir=str(left_dir),
        right_image_dir=str(right_dir),
        board={
            'rows': board.rows,
            'cols': board.cols,
            'square_size': board.square_size,
        },
        image_size=image_size,
        left_camera_matrix=left_camera_matrix,
        left_distortion_coefficients=left_distortion,
        right_camera_matrix=right_camera_matrix,
        right_distortion_coefficients=right_distortion,
        rotation_matrix=rotation,
        translation_vector=translation,
        essential_matrix=essential,
        fundamental_matrix=fundamental,
        stereo_error=float(stereo_error),
        total_pairs=len(pairs),
        valid_pairs=len(left_points),
        used_pairs=used_pairs,
        rejected_pairs=rejected_pairs,
    )


def _ensure_matching_mono_sizes(
    left_result: MonoCalibrationResult,
    right_result: MonoCalibrationResult,
) -> tuple[int, int]:
    return ensure_consistent_image_size(
        left_result.image_size,
        right_result.image_size,
        'right mono calibration set',
    )
