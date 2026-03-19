from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ChessboardSpec:
    rows: int
    cols: int
    square_size: float

    def validate(self) -> None:
        if self.rows <= 0:
            raise ValueError('rows must be greater than 0')
        if self.cols <= 0:
            raise ValueError('cols must be greater than 0')
        if self.square_size <= 0:
            raise ValueError('square_size must be greater than 0')

    @property
    def pattern_size(self) -> tuple[int, int]:
        return (self.cols, self.rows)

    def object_points(self) -> np.ndarray:
        self.validate()
        grid = np.zeros((self.rows * self.cols, 3), np.float32)
        coordinates = np.mgrid[0 : self.cols, 0 : self.rows].T.reshape(-1, 2)
        grid[:, :2] = coordinates * self.square_size
        return grid

