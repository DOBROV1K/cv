import math

from coordsys.core.shapes import Point2D, Point3D

Matrix3x3 = list[list[float]]
Matrix4x4 = list[list[float]]

# Единичная матрица
def _identity(n: int) -> list[list[float]]:
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(1.0)
            else:
                row.append(0.0)
        matrix.append(row)
    return matrix


# Умножение двух матриц
def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    if not a or not b:
        raise ValueError("Матрицы пустые")
    if len(a[0]) != len(b):
        raise ValueError(
            f"Количество столбцов в первой матрице ({len(a[0])}) "
            f"должно совпадать с числом строк во второй матрице ({len(b)})"
        )

    n = len(a)
    m = len(b)
    p = len(b[0])

    result = []
    for i in range(n):
        row = []
        for j in range(p):
            cell_sum = 0.0
            for k in range(m):
                cell_sum += a[i][k] * b[k][j]
            row.append(cell_sum)
        result.append(row)
    return result


# Матрица на вектор
def _matvec(a: list[list[float]], v: list[float]) -> list[float]:
    if not a:
        raise ValueError("Матрица не может быть пустой")
    if len(a[0]) != len(v):
        raise ValueError(
            f"Количество столбцов в матрице ({len(a[0])}) "
            f"должно совпадать с длиной вектора ({len(v)})"
        )

    result = []
    for row in a:
        cell_sum = 0.0
        for k in range(len(v)):
            cell_sum += row[k] * v[k]
        result.append(cell_sum)
    return result

# Сдвиг
def translation_matrix(dx: float, dy: float) -> Matrix3x3:
    return [
        [1.0, 0.0, dx],
        [0.0, 1.0, dy],
        [0.0, 0.0, 1.0],
    ]


# Поворот относительно начала координат

def rotation_matrix(theta_rad: float) -> Matrix3x3:
    c, s = math.cos(theta_rad), math.sin(theta_rad)
    return [
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0],
    ]

# Масштабирование

def scale_matrix(sx: float, sy: float) -> Matrix3x3:
    return [
        [sx, 0.0, 0.0],
        [0.0, sy, 0.0],
        [0.0, 0.0, 1.0],
    ]


def combine(*matrices: Matrix3x3) -> Matrix3x3:
    result = _identity(3)
    for matrix in matrices:
        result = _matmul(matrix, result)
    return result


def apply(matrix: Matrix3x3, points: list[Point2D]) -> list[Point2D]:
    transformed = []
    for x, y in points:
        rx, ry, rw = _matvec(matrix, [x, y, 1.0])
        transformed.append((rx / rw, ry / rw))
    return transformed


# 3D

def translation_matrix_3d(dx: float, dy: float, dz: float) -> Matrix4x4:
    return [
        [1.0, 0.0, 0.0, dx],
        [0.0, 1.0, 0.0, dy],
        [0.0, 0.0, 1.0, dz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def rotation_matrix_3d(axis: str, theta_rad: float) -> Matrix4x4:
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
    return [
        [sx, 0.0, 0.0, 0.0],
        [0.0, sy, 0.0, 0.0],
        [0.0, 0.0, sz, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def combine_3d(*matrices: Matrix4x4) -> Matrix4x4:
    result = _identity(4)
    for matrix in matrices:
        result = _matmul(matrix, result)
    return result


def apply_3d(matrix: Matrix4x4, points: list[Point3D]) -> list[Point3D]:
    transformed = []
    for x, y, z in points:
        rx, ry, rz, rw = _matvec(matrix, [x, y, z, 1.0])
        transformed.append((rx / rw, ry / rw, rz / rw))
    return transformed
