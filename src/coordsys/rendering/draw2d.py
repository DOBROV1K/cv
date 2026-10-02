"""Отрисовка 2D-сцены: оси, направление вращения, демонстрационный объект.

Ориентация системы координат в 2D влияет только на то, *как* мы рисуем
стандартный базис — на саму математику поворота/сдвига/масштаба (она всегда
выполняется по "обычным" формулам из ``transforms``) это не влияет.
Правая система на экране — обычные оси X вправо, Y вверх, поворот от X к Y
идёт против часовой стрелки (CCW). Левая система получается отражением оси Y
(ось Y направлена вниз), из-за чего тот же "от X к Y" поворот визуально
становится движением по часовой стрелке (CW).
"""

from __future__ import annotations

from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch, Polygon

from coordsys.core.orientation import Handedness
from coordsys.core.shapes import Point2D

AXIS_LENGTH = 5.0


def setup_axes(ax: Axes, handedness: Handedness, *, show_orientation: bool = True) -> None:
    """Готовит координатную плоскость: пределы, подписи осей, направление поворота.

    Args:
        ax: оси matplotlib, на которых рисуем.
        handedness: правая или левая система координат.
        show_orientation: если False, подпись направления поворота (CW/CCW)
            не выводится — используется в режиме 1, где ориентацию нужно угадать.
    """

    ax.clear()
    ax.set_xlim(-AXIS_LENGTH, AXIS_LENGTH)
    ax.set_ylim(-AXIS_LENGTH, AXIS_LENGTH)
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.5)

    # Левая система отображается отражением оси Y (ось направлена вниз).
    # Поворот сам по себе ориентацию не меняет, поэтому это единственное
    # отличие в отрисовке правой/левой 2D-системы.
    if handedness is Handedness.LEFT:
        ax.invert_yaxis()

    ax.annotate(
        "X", xy=(AXIS_LENGTH, 0), xytext=(AXIS_LENGTH * 0.95, AXIS_LENGTH * 0.08),
        fontsize=12, fontweight="bold",
    )
    ax.annotate(
        "Y", xy=(0, AXIS_LENGTH), xytext=(AXIS_LENGTH * 0.08, AXIS_LENGTH * 0.95),
        fontsize=12, fontweight="bold",
    )
    ax.axhline(0, color="black", linewidth=1.0)
    ax.axvline(0, color="black", linewidth=1.0)

    if show_orientation:
        _draw_rotation_hint(ax, handedness)


def _draw_rotation_hint(ax: Axes, handedness: Handedness) -> None:
    """Рисует дугу-подсказку: положительное направление поворота от X к Y."""

    arrow = FancyArrowPatch(
        (AXIS_LENGTH * 0.5, 0),
        (0, AXIS_LENGTH * 0.5),
        connectionstyle="arc3,rad=0.3",
        arrowstyle="-|>",
        mutation_scale=15,
        color="tab:blue",
    )
    ax.add_patch(arrow)

    label = "против часовой стрелки (CCW)" if handedness is Handedness.RIGHT else "по часовой стрелке (CW)"
    ax.set_title(f"Положительный поворот (от X к Y): {label}")


def draw_polygon(ax: Axes, points: list[Point2D], *, color: str = "tab:red") -> None:
    """Рисует демонстрационный многоугольник по списку вершин."""

    polygon = Polygon(points, closed=True, facecolor=color, edgecolor="black", alpha=0.6)
    ax.add_patch(polygon)


def format_points(points: list[Point2D]) -> str:
    """Форматирует список точек для информационной панели."""

    lines = [f"  P{i}: ({x:+.2f}, {y:+.2f})" for i, (x, y) in enumerate(points)]
    return "\n".join(lines)
