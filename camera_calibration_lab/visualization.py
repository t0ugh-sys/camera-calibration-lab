from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

from .boards import ChessboardSpec
from .io_utils import list_image_files, write_json


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
    label = 'TRUE' if found else 'FALSE'
    color = (0, 180, 0) if found else (0, 0, 255)
    cv2.putText(
        annotated,
        label,
        (40, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        2.0,
        color,
        4,
        cv2.LINE_AA,
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), annotated)

    return bool(found)


def batch_visualize_corners(
    image_dir: Path,
    board: ChessboardSpec,
    output_dir: Path,
    summary_path: Path | None = None,
) -> dict[str, object]:
    image_paths = list_image_files(image_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, object]] = []
    success_count = 0

    for image_path in image_paths:
        output_path = output_dir / image_path.name
        found = visualize_corners(image_path, board, output_path)
        if found:
            success_count += 1
        results.append(
            {
                'image': image_path.name,
                'found': found,
                'output': str(output_path),
            }
        )

    summary = {
        'image_dir': str(image_dir),
        'output_dir': str(output_dir),
        'total_images': len(image_paths),
        'success_count': success_count,
        'failure_count': len(image_paths) - success_count,
        'results': results,
    }

    if summary_path is not None:
        write_json(summary_path, summary)

    return summary


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
