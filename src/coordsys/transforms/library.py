import numpy as np

from coordsys.core.shapes import Point2D, Point3D

Matrix3x3 = np.ndarray
Matrix4x4 = np.ndarray


def translation_matrix(dx: float, dy: float) -> Matrix3x3:
    return np.array(
        [
            [1.0, 0.0, dx],
            [0.0, 1.0, dy],
            [0.0, 0.0, 1.0],
        ]
    )


def rotation_matrix(theta_rad: float) -> Matrix3x3:
    c, s = np.cos(theta_rad), np.sin(theta_rad)
    return np.array(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def scale_matrix(sx: float, sy: float) -> Matrix3x3:
    return np.array(
        [
            [sx, 0.0, 0.0],
            [0.0, sy, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def combine(*matrices: Matrix3x3) -> Matrix3x3:
    result = np.eye(3)
    for matrix in matrices:
        result = matrix @ result
    return result


def apply(matrix: Matrix3x3, points: list[Point2D]) -> list[Point2D]:
    homogeneous = np.array([[x, y, 1.0] for x, y in points]).T
    transformed = matrix @ homogeneous
    transformed /= transformed[2, :]
    return [(float(x), float(y)) for x, y in transformed[:2, :].T]




def translation_matrix_3d(dx: float, dy: float, dz: float) -> Matrix4x4:
    return np.array(
        [
            [1.0, 0.0, 0.0, dx],
            [0.0, 1.0, 0.0, dy],
            [0.0, 0.0, 1.0, dz],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


def rotation_matrix_3d(axis: str, theta_rad: float) -> Matrix4x4:
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
    return np.array(
        [
            [sx, 0.0, 0.0, 0.0],
            [0.0, sy, 0.0, 0.0],
            [0.0, 0.0, sz, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


def combine_3d(*matrices: Matrix4x4) -> Matrix4x4:
    result = np.eye(4)
    for matrix in matrices:
        result = matrix @ result
    return result


def apply_3d(matrix: Matrix4x4, points: list[Point3D]) -> list[Point3D]:
    homogeneous = np.array([[x, y, z, 1.0] for x, y, z in points]).T
    transformed = matrix @ homogeneous
    transformed /= transformed[3, :]
    return [(float(x), float(y), float(z)) for x, y, z in transformed[:3, :].T]
