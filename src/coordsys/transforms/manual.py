"""Ручная (без сторонних библиотек) реализация однородных преобразований.

Идея однородных координат: обычную точку ``(x, y)`` дополняют третьей
координатой ``w = 1``, получая ``(x, y, 1)``. Тогда и поворот/масштабирование
(линейные преобразования), и сдвиг (который линейным не является — сдвиг не
переводит начало координат в себя) можно записать одной и той же операцией —
умножением точки на матрицу 3x3. Без однородной координаты сдвиг пришлось бы
обрабатывать отдельно от поворота и масштаба (нельзя выразить как матрицу 2x2).

В пространстве тот же приём работает с координатой ``(x, y, z, 1)`` и матрицами
4x4.

Матрицы здесь — обычные вложенные списки Python (без numpy), а умножение
матриц и векторов реализовано вручную тройным циклом — это ровно то же самое
вычисление, которое "под капотом" делает библиотека в ``library.py``, но без
использования сторонних пакетов.
"""

from __future__ import annotations

import math

from coordsys.core.shapes import Point2D, Point3D

Matrix3x3 = list[list[float]]
Matrix4x4 = list[list[float]]


def _identity(n: int) -> list[list[float]]:
    """Единичная матрица n x n: нейтральный элемент умножения матриц."""

    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Произведение двух матриц C = A @ B, вычисленное вручную.

    c[i][j] = сумма по k от a[i][k] * b[k][j] — стандартное определение
    матричного умножения, без использования numpy.
    """

    n, m, p = len(a), len(b), len(b[0])
    result = [[0.0] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            result[i][j] = sum(a[i][k] * b[k][j] for k in range(m))
    return result


def _matvec(a: list[list[float]], v: list[float]) -> list[float]:
    """Произведение матрицы на вектор-столбец (однородные координаты точки)."""

    return [sum(row[k] * v[k] for k in range(len(v))) for row in a]


# ---------------------------------------------------------------------------
# 2D: матрицы 3x3, точки (x, y, 1)
# ---------------------------------------------------------------------------


def translation_matrix(dx: float, dy: float) -> Matrix3x3:
    """Матрица сдвига на (dx, dy).

    Третий столбец матрицы — это и есть вектор сдвига; при умножении на
    точку (x, y, 1) координата w=1 "достаёт" dx и dy и прибавляет их к x, y.
    """

    return [
        [1.0, 0.0, dx],
        [0.0, 1.0, dy],
        [0.0, 0.0, 1.0],
    ]


def rotation_matrix(theta_rad: float) -> Matrix3x3:
    """Матрица поворота на угол theta (в радианах) против часовой стрелки.

    Стандартный вывод: базовый вектор (1, 0) переходит в (cos, sin),
    а (0, 1) — в (-sin, cos); это и есть столбцы матрицы поворота.
    """

    c, s = math.cos(theta_rad), math.sin(theta_rad)
    return [
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0],
    ]


def scale_matrix(sx: float, sy: float) -> Matrix3x3:
    """Матрица масштабирования по осям X и Y независимо."""

    return [
        [sx, 0.0, 0.0],
        [0.0, sy, 0.0],
        [0.0, 0.0, 1.0],
    ]


def combine(*matrices: Matrix3x3) -> Matrix3x3:
    """Последовательное применение нескольких 2D-преобразований.

    Преобразования применяются в порядке аргументов: ``combine(T, R, S)``
    означает "сначала S, затем R, затем T" (матрицы умножаются справа
    налево при действии на вектор-столбец точки).
    """

    result = _identity(3)
    for matrix in matrices:
        result = _matmul(matrix, result)
    return result


def apply(matrix: Matrix3x3, points: list[Point2D]) -> list[Point2D]:
    """Применяет матрицу 3x3 ко списку 2D-точек через однородные координаты."""

    transformed = []
    for x, y in points:
        rx, ry, rw = _matvec(matrix, [x, y, 1.0])
        transformed.append((rx / rw, ry / rw))
    return transformed


# ---------------------------------------------------------------------------
# 3D: матрицы 4x4, точки (x, y, z, 1)
# ---------------------------------------------------------------------------


def translation_matrix_3d(dx: float, dy: float, dz: float) -> Matrix4x4:
    """Матрица сдвига в пространстве — тот же приём, что и в 2D, но с w=1."""

    return [
        [1.0, 0.0, 0.0, dx],
        [0.0, 1.0, 0.0, dy],
        [0.0, 0.0, 1.0, dz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_matrix_3d(axis: str, theta_rad: float) -> Matrix4x4:
    """Матрица поворота вокруг одной из осей (x, y или z) на угол theta.

    Поворот вокруг оси оставляет координату вдоль этой оси неизменной и
    вращает две оставшиеся координаты так же, как 2D-поворот.
    Направление — по правилу правой руки (смотрим с положительного конца
    оси поворота на начало координат).
    """

    c, s = math.cos(theta_rad), math.sin(theta_rad)
    if axis == "x":
        return [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, c, -s, 0.0],
            [0.0, s, c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    if axis == "y":
        return [
            [c, 0.0, s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-s, 0.0, c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    if axis == "z":
        return [
            [c, -s, 0.0, 0.0],
            [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    raise ValueError(f"Неизвестная ось вращения: {axis!r}, ожидалось 'x', 'y' или 'z'")


def scale_matrix_3d(sx: float, sy: float, sz: float) -> Matrix4x4:
    """Матрица масштабирования по трём осям независимо."""

    return [
        [sx, 0.0, 0.0, 0.0],
        [0.0, sy, 0.0, 0.0],
        [0.0, 0.0, sz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def combine_3d(*matrices: Matrix4x4) -> Matrix4x4:
    """3D-аналог ``combine``: последовательное применение преобразований."""

    result = _identity(4)
    for matrix in matrices:
        result = _matmul(matrix, result)
    return result


def apply_3d(matrix: Matrix4x4, points: list[Point3D]) -> list[Point3D]:
    """Применяет матрицу 4x4 ко списку 3D-точек через однородные координаты."""

    transformed = []
    for x, y, z in points:
        rx, ry, rz, rw = _matvec(matrix, [x, y, z, 1.0])
        transformed.append((rx / rw, ry / rw, rz / rw))
    return transformed
