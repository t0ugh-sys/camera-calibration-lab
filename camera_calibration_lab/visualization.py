from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

from .boards import ChessboardSpec


def load_calibration(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open('r', encoding='utf-8') as file:
        payload = json.load(file)

    camera_matrix = np.array(payload['camera_matrix'], dtype=np.float64)
    distortion_coefficients = np.array(payload['distortion_coefficients'], dtype=np.float64)
    return camera_matrix, distortion_coefficients


def visualize_corners(
    image_path: Path,
    board: ChessboardSpec,
    output_path: Path | None = None,
) -> bool:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f'failed to read image: {image_path}')

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, board.pattern_size)
    if found:
        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            30,
            0.001,
        )
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    annotated = image.copy()
    cv2.drawChessboardCorners(annotated, board.pattern_size, corners, found)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), annotated)

    return bool(found)


def visualize_undistort(
    image_path: Path,
    calibration_path: Path,
    output_path: Path | None = None,
) -> np.ndarray:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f'failed to read image: {image_path}')

    camera_matrix, distortion_coefficients = load_calibration(calibration_path)
    undistorted = cv2.undistort(image, camera_matrix, distortion_coefficients)
    comparison = np.hstack((image, undistorted))

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), comparison)

    return comparison
