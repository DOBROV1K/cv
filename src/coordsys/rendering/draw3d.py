import numpy as np
from matplotlib.axes import Axes

from coordsys.core.orientation import Handedness
from coordsys.core.shapes import Point3D

AXIS_LENGTH = 3.0

_ROTATION_PLANES = {
    "x": (1, 2),
    "y": (2, 0),
    "z": (0, 1),
}
_AXIS_NAMES = ("X", "Y", "Z")


def setup_axes(ax: Axes, handedness: Handedness, *, show_orientation: bool = True) -> None:
    ax.clear()
    limit = AXIS_LENGTH * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)

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

    for a, b in edges:
        xs = [vertices[a][0], vertices[b][0]]
        ys = [vertices[a][1], vertices[b][1]]
        zs = [vertices[a][2], vertices[b][2]]
        ax.plot(xs, ys, zs, color=color, linewidth=2)


def format_points(points: list[Point3D]) -> str:
    lines = [f"  P{i}: ({x:+.2f}, {y:+.2f}, {z:+.2f})" for i, (x, y, z) in enumerate(points)]
    return "\n".join(lines)
