"""Те же однородные преобразования, что и в ``manual.py``, но через numpy.

API намеренно идентичен модулю ``manual``: одинаковые имена функций и
одинаковые типы входа/выхода (обычные точки, не массивы numpy снаружи). Это
позволяет коду режимов 2 и 3 переключаться между "ручным" и "библиотечным"
расчётом простой подменой импортируемого модуля (см. ``modes/mode2_plane.py``
и ``modes/mode3_space.py``), не меняя остальную логику.

Разница с ``manual.py`` — только в реализации: матрицы это ``np.ndarray``,
умножение матриц и матрицы на вектор — оператор ``@`` (встроенное умножение
numpy вместо ручных циклов).
"""

from __future__ import annotations

import numpy as np

from coordsys.core.shapes import Point2D, Point3D

Matrix3x3 = np.ndarray
Matrix4x4 = np.ndarray


# ---------------------------------------------------------------------------
# 2D: матрицы 3x3, точки (x, y, 1)
# ---------------------------------------------------------------------------


def translation_matrix(dx: float, dy: float) -> Matrix3x3:
    """Матрица сдвига на (dx, dy) — см. docstring в ``manual.translation_matrix``."""

    return np.array(
        [
            [1.0, 0.0, dx],
            [0.0, 1.0, dy],
            [0.0, 0.0, 1.0],
        ]
    )


def rotation_matrix(theta_rad: float) -> Matrix3x3:
    """Матрица поворота на угол theta против часовой стрелки."""

    c, s = np.cos(theta_rad), np.sin(theta_rad)
    return np.array(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def scale_matrix(sx: float, sy: float) -> Matrix3x3:
    """Матрица масштабирования по осям X и Y независимо."""

    return np.array(
        [
            [sx, 0.0, 0.0],
            [0.0, sy, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def combine(*matrices: Matrix3x3) -> Matrix3x3:
    """Последовательное применение нескольких 2D-преобразований (см. manual.combine)."""

    result = np.eye(3)
    for matrix in matrices:
        result = matrix @ result
    return result


def apply(matrix: Matrix3x3, points: list[Point2D]) -> list[Point2D]:
    """Применяет матрицу 3x3 ко списку 2D-точек через однородные координаты."""

    homogeneous = np.array([[x, y, 1.0] for x, y in points]).T  # 3 x N
    transformed = matrix @ homogeneous  # 3 x N
    transformed /= transformed[2, :]  # нормализация по w (здесь всегда w=1)
    return [(float(x), float(y)) for x, y in transformed[:2, :].T]


# ---------------------------------------------------------------------------
# 3D: матрицы 4x4, точки (x, y, z, 1)
# ---------------------------------------------------------------------------


def translation_matrix_3d(dx: float, dy: float, dz: float) -> Matrix4x4:
    """Матрица сдвига в пространстве."""

    return np.array(
        [
            [1.0, 0.0, 0.0, dx],
            [0.0, 1.0, 0.0, dy],
            [0.0, 0.0, 1.0, dz],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


def rotation_matrix_3d(axis: str, theta_rad: float) -> Matrix4x4:
    """Матрица поворота вокруг одной из осей (x, y или z) на угол theta."""

    c, s = np.cos(theta_rad), np.sin(theta_rad)
    if axis == "x":
        return np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, c, -s, 0.0],
                [0.0, s, c, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
    if axis == "y":
        return np.array(
            [
                [c, 0.0, s, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [-s, 0.0, c, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
    if axis == "z":
        return np.array(
            [
                [c, -s, 0.0, 0.0],
                [s, c, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
    raise ValueError(f"Неизвестная ось вращения: {axis!r}, ожидалось 'x', 'y' или 'z'")


def scale_matrix_3d(sx: float, sy: float, sz: float) -> Matrix4x4:
    """Матрица масштабирования по трём осям независимо."""

    return np.array(
        [
            [sx, 0.0, 0.0, 0.0],
            [0.0, sy, 0.0, 0.0],
            [0.0, 0.0, sz, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


def combine_3d(*matrices: Matrix4x4) -> Matrix4x4:
    """3D-аналог ``combine``: последовательное применение преобразований."""

    result = np.eye(4)
    for matrix in matrices:
        result = matrix @ result
    return result


def apply_3d(matrix: Matrix4x4, points: list[Point3D]) -> list[Point3D]:
    """Применяет матрицу 4x4 ко списку 3D-точек через однородные координаты."""

    homogeneous = np.array([[x, y, z, 1.0] for x, y, z in points]).T  # 4 x N
    transformed = matrix @ homogeneous  # 4 x N
    transformed /= transformed[3, :]  # нормализация по w
    return [(float(x), float(y), float(z)) for x, y, z in transformed[:3, :].T]
