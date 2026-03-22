from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from .boards import ChessboardSpec
from .io_utils import list_image_files


@dataclass
class MonoCalibrationResult:
    image_size: tuple[int, int]
    camera_matrix: np.ndarray
    distortion_coefficients: np.ndarray
    reprojection_error: float
    valid_images: int

    def as_dict(self) -> dict[str, object]:
        return {
            'image_size': list(self.image_size),
            'camera_matrix': self.camera_matrix,
            'distortion_coefficients': self.distortion_coefficients,
            'reprojection_error': self.reprojection_error,
            'valid_images': self.valid_images,
        }


def _find_corners(image_path: Path, board: ChessboardSpec) -> tuple[tuple[int, int], np.ndarray] | None:
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
    image_size = (gray.shape[1], gray.shape[0])
    return image_size, refined


def calibrate_mono(image_dir: Path, board: ChessboardSpec) -> MonoCalibrationResult:
    board.validate()
    image_paths = list_image_files(image_dir)
    if not image_paths:
        raise ValueError(f'no images found in {image_dir}')

    object_points: list[np.ndarray] = []
    image_points: list[np.ndarray] = []
    image_size: tuple[int, int] | None = None
    template_points = board.object_points()

    for image_path in image_paths:
        detected = _find_corners(image_path, board)
        if detected is None:
            continue
        current_image_size, corners = detected
        image_size = current_image_size
        object_points.append(template_points.copy())
        image_points.append(corners)

    if image_size is None or not image_points:
        raise ValueError('no valid chessboard detections found for mono calibration')

    success, camera_matrix, distortion_coefficients, _, _ = cv2.calibrateCamera(
        object_points,
        image_points,
        image_size,
        None,
        None,
    )
    if not success:
        raise RuntimeError('mono calibration failed')

    reprojection_error = _compute_reprojection_error(
        object_points,
        image_points,
        camera_matrix,
        distortion_coefficients,
    )
    return MonoCalibrationResult(
        image_size=image_size,
        camera_matrix=camera_matrix,
        distortion_coefficients=distortion_coefficients,
        reprojection_error=reprojection_error,
        valid_images=len(image_points),
    )


def _compute_reprojection_error(
    object_points: list[np.ndarray],
    image_points: list[np.ndarray],
    camera_matrix: np.ndarray,
    distortion_coefficients: np.ndarray,
) -> float:
    total_error = 0.0
    total_points = 0

    for obj_points, img_points in zip(object_points, image_points):
        success, rvec, tvec = cv2.solvePnP(obj_points, img_points, camera_matrix, distortion_coefficients)
        if not success:
            continue
        reprojected, _ = cv2.projectPoints(obj_points, rvec, tvec, camera_matrix, distortion_coefficients)
        error = cv2.norm(img_points, reprojected, cv2.NORM_L2)
        total_error += error * error
        total_points += len(obj_points)

    if total_points == 0:
        return float('inf')

    return float((total_error / total_points) ** 0.5)

