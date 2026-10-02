"""Отрисовка 3D-сцены: оси, направление поворота вокруг каждой оси, объект.

Как и в 2D (см. ``draw2d.py``), ориентация влияет только на отрисовку, а не
на саму математику поворота. Правая система — оси X, Y, Z расположены по
правилу правой руки. Левая система получается отражением оси Z (на экране её
направление инвертируется) — при этом положительные повороты вокруг X и Y
меняют видимое направление на противоположное, а вокруг Z — остаётся прежним
(это стандартное следствие однократного отражения одной оси).
"""

from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes

from coordsys.core.orientation import Handedness
from coordsys.core.shapes import Point3D

AXIS_LENGTH = 3.0

# Для каждой оси вращения указываем две "соседние" оси, в плоскости которых
# рисуется дуга положительного поворота (по правилу правой руки: поворот
# вокруг X идёт от Y к Z, вокруг Y — от Z к X, вокруг Z — от X к Y).
_ROTATION_PLANES = {
    "x": (1, 2),
    "y": (2, 0),
    "z": (0, 1),
}
_AXIS_NAMES = ("X", "Y", "Z")


def setup_axes(ax: Axes, handedness: Handedness, *, show_orientation: bool = True) -> None:
    """Готовит 3D-оси: пределы, подписи, при необходимости — дуги поворота.

    Args:
        ax: 3D-оси matplotlib (``projection="3d"``).
        handedness: правая или левая система координат.
        show_orientation: если False, дуги положительного поворота не рисуются
            (режим 1, где ориентацию нужно угадать по виду осей).
    """

    ax.clear()
    limit = AXIS_LENGTH * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)

    # Левая система координат получается отражением оси Z.
    z_sign = 1.0 if handedness is Handedness.RIGHT else -1.0

    axis_vectors = {
        "x": np.array([AXIS_LENGTH, 0.0, 0.0]),
        "y": np.array([0.0, AXIS_LENGTH, 0.0]),
        "z": np.array([0.0, 0.0, AXIS_LENGTH * z_sign]),
    }
    for name, vec in axis_vectors.items():
        ax.quiver(0, 0, 0, *vec, color="black", arrow_length_ratio=0.1)
        ax.text(*(vec * 1.1), name.upper(), fontsize=12, fontweight="bold")

    if show_orientation:
        for axis_name in ("x", "y", "z"):
            _draw_rotation_hint(ax, axis_name, axis_vectors)


def _draw_rotation_hint(ax: Axes, axis_name: str, axis_vectors: dict[str, np.ndarray]) -> None:
    """Рисует дугу положительного поворота вокруг заданной оси.

    Направление дуги определяется фактическим (возможно отражённым)
    положением двух "соседних" осей — поэтому для левой системы дуга
    сама по себе развернётся в нужную сторону без отдельных условий.
    """

    i, j = _ROTATION_PLANES[axis_name]
    u = axis_vectors[_AXIS_NAMES[i].lower()] / AXIS_LENGTH
    v = axis_vectors[_AXIS_NAMES[j].lower()] / AXIS_LENGTH
    radius = AXIS_LENGTH * 0.6

    angles = np.linspace(0, 0.75 * np.pi, 20)
    arc = np.array([radius * (np.cos(t) * u + np.sin(t) * v) for t in angles])
    ax.plot(arc[:, 0], arc[:, 1], arc[:, 2], color="tab:blue", linewidth=1.5)

    tip = arc[-1]
    direction = arc[-1] - arc[-3]
    ax.quiver(*tip, *direction, color="tab:blue", arrow_length_ratio=0.8, linewidth=1.5)


def draw_basis_vectors(ax: Axes, vectors: dict[str, np.ndarray]) -> None:
    """Рисует три произвольных базисных вектора (для режима 1 — угадайки).

    В отличие от ``setup_axes``, векторы здесь могут быть повёрнуты на
    произвольный угол и, возможно, отражены — ориентацию нужно определить
    по рисунку, поэтому никаких подсказок (дуг поворота, подписи CW/CCW)
    не рисуется.
    """

    ax.clear()
    limit = AXIS_LENGTH * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)

    for name, vec in vectors.items():
        ax.quiver(0, 0, 0, *vec, color="black", arrow_length_ratio=0.15, linewidth=2)
        ax.text(*(vec * 1.15), name.upper(), fontsize=12, fontweight="bold")


def draw_wireframe(
    ax: Axes,
    vertices: list[Point3D],
    edges: list[tuple[int, int]],
    *,
    color: str = "tab:red",
) -> None:
    """Рисует каркасный объект по вершинам и рёбрам (списку пар индексов)."""

    for a, b in edges:
        xs = [vertices[a][0], vertices[b][0]]
        ys = [vertices[a][1], vertices[b][1]]
        zs = [vertices[a][2], vertices[b][2]]
        ax.plot(xs, ys, zs, color=color, linewidth=2)


def format_points(points: list[Point3D]) -> str:
    """Форматирует список 3D-точек для информационной панели."""

    lines = [f"  P{i}: ({x:+.2f}, {y:+.2f}, {z:+.2f})" for i, (x, y, z) in enumerate(points)]
    return "\n".join(lines)
