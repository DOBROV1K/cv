"""Режим 3 — интерактивное 3D-преобразование объекта в однородных координатах (PyQt6).

Аналогично режиму 2, но в трёхмерном пространстве:
  - объект: каркасный 3D-домик (core.shapes.demo_wireframe_3d);
  - для каждой из трёх осей показано направление положительного поворота вокруг неё;
  - пользователь может выбирать ось вращения (X, Y или Z);
  - сдвиг (dx, dy, dz), поворот и масштабирование рассчитываются в однородных координатах 4×4.
"""

from __future__ import annotations

import math
from types import ModuleType

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from coordsys.core.orientation import Handedness
from coordsys.core.shapes import Point3D, demo_wireframe_3d
from coordsys.rendering import draw3d
from coordsys.transforms import library as transforms_library
from coordsys.transforms import manual as transforms_manual

_BACKENDS: dict[str, ModuleType] = {
    "Ручной": transforms_manual,
    "Библиотека (NumPy)": transforms_library,
}


class SpaceTransformMode(QWidget):
    """Виджет Режима 3: 3D-преобразования в однородных координатах."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.vertices: list[Point3D] = []
        self.edges: list[tuple[int, int]] = []
        self.handedness = Handedness.RIGHT
        self.backend_name = "Ручной"
        self.rotation_axis = "z"

        self.vertices, self.edges = demo_wireframe_3d()
        self._build_ui()
        self._redraw()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # 1. 3D Холст Matplotlib
        self.figure = Figure(figsize=(6, 6), facecolor="#ffffff")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111, projection="3d")
        layout.addWidget(self.canvas, stretch=3)

        # 2. Панель управления
        panel = QFrame()
        panel.setStyleSheet(
            "QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }"
            "QGroupBox { font-weight: bold; border: 1px solid #cbd5e1; border-radius: 6px; margin-top: 10px; padding-top: 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #1e293b; }"
        )
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(15, 15, 15, 15)
        panel_layout.setSpacing(10)

        # Группа 1: Ориентация
        grp_orient = QGroupBox("Ориентация системы координат")
        l_orient = QVBoxLayout(grp_orient)
        self.rb_right = QRadioButton("Правая (X × Y = Z)")
        self.rb_left = QRadioButton("Левая (X × Y = -Z)")
        self.rb_right.setChecked(True)
        self.rb_right.toggled.connect(self._on_handedness_changed)
        l_orient.addWidget(self.rb_right)
        l_orient.addWidget(self.rb_left)
        panel_layout.addWidget(grp_orient)

        # Группа 2: Способ расчёта
        grp_calc = QGroupBox("Способ расчёта")
        l_calc = QVBoxLayout(grp_calc)
        self.rb_manual = QRadioButton("Ручной (матрицы 4×4)")
        self.rb_numpy = QRadioButton("Библиотека (NumPy)")
        self.rb_manual.setChecked(True)
        self.rb_manual.toggled.connect(self._on_backend_changed)
        l_calc.addWidget(self.rb_manual)
        l_calc.addWidget(self.rb_numpy)
        panel_layout.addWidget(grp_calc)

        # Группа 3: Ось вращения
        grp_axis = QGroupBox("Ось вращения")
        l_axis = QHBoxLayout(grp_axis)
        self.rb_axis_x = QRadioButton("X")
        self.rb_axis_y = QRadioButton("Y")
        self.rb_axis_z = QRadioButton("Z")
        self.rb_axis_z.setChecked(True)

        self.axis_group = QButtonGroup(self)
        self.axis_group.addButton(self.rb_axis_x, 0)
        self.axis_group.addButton(self.rb_axis_y, 1)
        self.axis_group.addButton(self.rb_axis_z, 2)
        self.axis_group.idToggled.connect(self._on_axis_changed)

        l_axis.addWidget(self.rb_axis_x)
        l_axis.addWidget(self.rb_axis_y)
        l_axis.addWidget(self.rb_axis_z)
        panel_layout.addWidget(grp_axis)

        # Группа 4: Аффинные преобразования 3D
        grp_trans = QGroupBox("Преобразования 3D")
        l_trans = QGridLayout(grp_trans)
        l_trans.setSpacing(6)

        # Сдвиг
        l_trans.addWidget(QLabel("dx:"), 0, 0)
        self.spin_dx = QDoubleSpinBox()
        self.spin_dx.setRange(-10.0, 10.0)
        self.spin_dx.setValue(1.0)
        self.spin_dx.setSingleStep(0.5)
        l_trans.addWidget(self.spin_dx, 0, 1)

        l_trans.addWidget(QLabel("dy:"), 0, 2)
        self.spin_dy = QDoubleSpinBox()
        self.spin_dy.setRange(-10.0, 10.0)
        self.spin_dy.setValue(1.0)
        self.spin_dy.setSingleStep(0.5)
        l_trans.addWidget(self.spin_dy, 0, 3)

        l_trans.addWidget(QLabel("dz:"), 0, 4)
        self.spin_dz = QDoubleSpinBox()
        self.spin_dz.setRange(-10.0, 10.0)
        self.spin_dz.setValue(1.0)
        self.spin_dz.setSingleStep(0.5)
        l_trans.addWidget(self.spin_dz, 0, 5)

        self.btn_translate = QPushButton("Сдвиг")
        self.btn_translate.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-weight: bold; border-radius: 4px; padding: 4px 8px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        self.btn_translate.clicked.connect(self._apply_translate)
        l_trans.addWidget(self.btn_translate, 0, 6)

        # Поворот
        l_trans.addWidget(QLabel("Угол (°):"), 1, 0)
        self.spin_angle = QDoubleSpinBox()
        self.spin_angle.setRange(-360.0, 360.0)
        self.spin_angle.setValue(30.0)
        self.spin_angle.setSingleStep(5.0)
        l_trans.addWidget(self.spin_angle, 1, 1, 1, 5)

        self.btn_rotate = QPushButton("Поворот")
        self.btn_rotate.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-weight: bold; border-radius: 4px; padding: 4px 8px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        self.btn_rotate.clicked.connect(self._apply_rotate)
        l_trans.addWidget(self.btn_rotate, 1, 6)

        # Масштаб
        l_trans.addWidget(QLabel("Масштаб:"), 2, 0)
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setRange(0.1, 5.0)
        self.spin_scale.setValue(1.2)
        self.spin_scale.setSingleStep(0.1)
        l_trans.addWidget(self.spin_scale, 2, 1, 1, 5)

        self.btn_scale = QPushButton("Масштаб")
        self.btn_scale.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-weight: bold; border-radius: 4px; padding: 4px 8px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        self.btn_scale.clicked.connect(self._apply_scale)
        l_trans.addWidget(self.btn_scale, 2, 6)

        # Сброс
        self.btn_reset = QPushButton("Сброс")
        self.btn_reset.setStyleSheet(
            "QPushButton { background-color: #f1f5f9; color: #475569; font-weight: bold; border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; }"
            "QPushButton:hover { background-color: #e2e8f0; }"
        )
        self.btn_reset.clicked.connect(self._reset)
        l_trans.addWidget(self.btn_reset, 3, 0, 1, 7)

        panel_layout.addWidget(grp_trans)

        # Группа 5: Координаты вершин
        grp_coords = QGroupBox("Координаты вершин (3D)")
        l_coords = QVBoxLayout(grp_coords)
        self.txt_coords = QTextEdit()
        self.txt_coords.setReadOnly(True)
        self.txt_coords.setStyleSheet("font-family: Consolas, monospace; font-size: 10px; background-color: #f8fafc; border: 1px solid #e2e8f0;")
        l_coords.addWidget(self.txt_coords)
        panel_layout.addWidget(grp_coords)

        layout.addWidget(panel, stretch=2)

    @property
    def _backend(self) -> ModuleType:
        return _BACKENDS[self.backend_name]

    def _on_handedness_changed(self) -> None:
        self.handedness = Handedness.RIGHT if self.rb_right.isChecked() else Handedness.LEFT
        self._redraw()

    def _on_backend_changed(self) -> None:
        self.backend_name = "Ручной" if self.rb_manual.isChecked() else "Библиотека (NumPy)"
        self._update_info()

    def _on_axis_changed(self, btn_id: int, checked: bool) -> None:
        if checked:
            mapping = {0: "x", 1: "y", 2: "z"}
            self.rotation_axis = mapping.get(btn_id, "z")
            self._update_info()

    def _apply_translate(self) -> None:
        dx = self.spin_dx.value()
        dy = self.spin_dy.value()
        dz = self.spin_dz.value()
        matrix = self._backend.translation_matrix_3d(dx, dy, dz)
        self.vertices = self._backend.apply_3d(matrix, self.vertices)
        self._redraw()

    def _apply_rotate(self) -> None:
        angle_rad = math.radians(self.spin_angle.value())
        matrix = self._backend.rotation_matrix_3d(self.rotation_axis, angle_rad)
        self.vertices = self._backend.apply_3d(matrix, self.vertices)
        self._redraw()

    def _apply_scale(self) -> None:
        s = self.spin_scale.value()
        matrix = self._backend.scale_matrix_3d(s, s, s)
        self.vertices = self._backend.apply_3d(matrix, self.vertices)
        self._redraw()

    def _reset(self) -> None:
        self.vertices, self.edges = demo_wireframe_3d()
        self._redraw()

    def _update_info(self) -> None:
        lines = [
            f"Расчёт: {self.backend_name}",
            f"Ориентация: {self.handedness.value.upper()}",
            f"Ось поворота: {self.rotation_axis.upper()}",
            "-" * 32,
            "Координаты вершин (x, y, z):",
        ]
        for i, (x, y, z) in enumerate(self.vertices):
            lines.append(f"  P{i}: ({x:+6.2f}, {y:+6.2f}, {z:+6.2f})")
        self.txt_coords.setText("\n".join(lines))

    def _redraw(self) -> None:
        draw3d.setup_axes(self.ax, self.handedness)
        draw3d.draw_wireframe(self.ax, self.vertices, self.edges)
        self.ax.set_box_aspect([1, 1, 1])
        self.canvas.draw()
        self._update_info()
