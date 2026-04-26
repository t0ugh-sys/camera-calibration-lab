from __future__ import annotations

import json
from pathlib import Path
from typing import Any


IMAGE_PATTERNS = ('*.jpg', '*.jpeg', '*.png', '*.bmp')


def list_image_files(directory: Path) -> list[Path]:
    if not directory.exists():
        raise FileNotFoundError(f'image directory not found: {directory}')
    if not directory.is_dir():
        raise NotADirectoryError(f'not a directory: {directory}')

    files: list[Path] = []
    for pattern in IMAGE_PATTERNS:
        files.extend(sorted(directory.glob(pattern)))
    return sorted(set(files))


def pair_stereo_images(left_dir: Path, right_dir: Path) -> list[tuple[Path, Path]]:
    left_files = list_image_files(left_dir)
    right_files = list_image_files(right_dir)

    right_map = {path.name: path for path in right_files}
    pairs = [(left_path, right_map[left_path.name]) for left_path in left_files if left_path.name in right_map]

    if not pairs:
        raise ValueError('no stereo image pairs found')

    return pairs


def ensure_consistent_image_size(
    expected: tuple[int, int] | None,
    current: tuple[int, int],
    source_name: str,
) -> tuple[int, int]:
    if expected is None:
        return current
    if expected != current:
        expected_width, expected_height = expected
        current_width, current_height = current
        raise ValueError(
            'inconsistent image size detected for '
            f'{source_name}: expected {expected_width}x{expected_height}, '
            f'got {current_width}x{current_height}'
        )
    return expected


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def to_serializable(value: Any) -> Any:
    if hasattr(value, 'tolist'):
        return value.tolist()
    if isinstance(value, dict):
        return {key: to_serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_serializable(item) for item in value]
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open('w', encoding='utf-8') as file:
        json.dump(to_serializable(payload), file, indent=2, ensure_ascii=False)
