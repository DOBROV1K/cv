import math
from types import ModuleType

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (
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
from coordsys.core.shapes import Point2D, demo_polygon_2d
from coordsys.rendering import draw2d
from coordsys.transforms import library as transforms_library
from coordsys.transforms import manual as transforms_manual

_BACKENDS: dict[str, ModuleType] = {
    "Ручной": transforms_manual,
    "Библиотека (NumPy)": transforms_library,
}


class PlaneTransformMode(QWidget):
    #2D-преобразования в однородных координатах.

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.points: list[Point2D] = demo_polygon_2d()
        self.handedness = Handedness.RIGHT
        self.backend_name = "Ручной"

        self._build_ui()
        self._redraw()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # 1. 2D Холст Matplotlib
        self.figure = Figure(figsize=(6, 6), facecolor="#ffffff")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas, stretch=3)

        # 2. Панель управления
        panel = QFrame(self)
        panel.setStyleSheet(
            "QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }"
            "QGroupBox { font-weight: bold; border: 1px solid #cbd5e1; border-radius: 6px; margin-top: 10px; padding-top: 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #1e293b; }"
        )
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(15, 15, 15, 15)
        panel_layout.setSpacing(12)

        # Ориентация системы координат
        grp_orient = QGroupBox("Ориентация системы координат")
        l_orient = QVBoxLayout(grp_orient)
        self.rb_right = QRadioButton("Правая (против часовой стрелки, CCW)")
        self.rb_left = QRadioButton("Левая (по часовой стрелке, CW)")
        self.rb_right.setChecked(True)
        self.rb_right.toggled.connect(self._on_handedness_changed)
        l_orient.addWidget(self.rb_right)
        l_orient.addWidget(self.rb_left)
        panel_layout.addWidget(grp_orient)

        # Способ расчёта однородных координат
        grp_calc = QGroupBox("Способ расчёта")
        l_calc = QVBoxLayout(grp_calc)
        self.rb_manual = QRadioButton("Ручной (матрицы списков)")
        self.rb_numpy = QRadioButton("Библиотека (NumPy)")
        self.rb_manual.setChecked(True)
        self.rb_manual.toggled.connect(self._on_backend_changed)
        l_calc.addWidget(self.rb_manual)
        l_calc.addWidget(self.rb_numpy)
        panel_layout.addWidget(grp_calc)

        # Преобразования
        grp_trans = QGroupBox("Преобразования")
        l_trans = QGridLayout(grp_trans)
        l_trans.setSpacing(8)

        # Сдвиг
        l_trans.addWidget(QLabel("dx:"), 0, 0)
        self.spin_dx = QDoubleSpinBox(self)
        self.spin_dx.setRange(-10.0, 10.0)
        self.spin_dx.setValue(1.0)
        self.spin_dx.setSingleStep(0.5)
        l_trans.addWidget(self.spin_dx, 0, 1)

        l_trans.addWidget(QLabel("dy:"), 0, 2)
        self.spin_dy = QDoubleSpinBox(self)
        self.spin_dy.setRange(-10.0, 10.0)
        self.spin_dy.setValue(1.0)
        self.spin_dy.setSingleStep(0.5)
        l_trans.addWidget(self.spin_dy, 0, 3)

        self.btn_translate = QPushButton("Сдвиг")
        self.btn_translate.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-weight: bold; border-radius: 4px; padding: 4px 10px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        self.btn_translate.clicked.connect(self._apply_translate)
        l_trans.addWidget(self.btn_translate, 0, 4)

        # Поворот
        l_trans.addWidget(QLabel("Угол (°):"), 1, 0)
        self.spin_angle = QDoubleSpinBox(self)
        self.spin_angle.setRange(-360.0, 360.0)
        self.spin_angle.setValue(30.0)
        self.spin_angle.setSingleStep(5.0)
        l_trans.addWidget(self.spin_angle, 1, 1, 1, 3)

        self.btn_rotate = QPushButton("Поворот")
        self.btn_rotate.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-weight: bold; border-radius: 4px; padding: 4px 10px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        self.btn_rotate.clicked.connect(self._apply_rotate)
        l_trans.addWidget(self.btn_rotate, 1, 4)

        # Масштаб
        l_trans.addWidget(QLabel("Масштаб:"), 2, 0)
        self.spin_scale = QDoubleSpinBox(self)
        self.spin_scale.setRange(0.1, 5.0)
        self.spin_scale.setValue(1.2)
        self.spin_scale.setSingleStep(0.1)
        l_trans.addWidget(self.spin_scale, 2, 1, 1, 3)

        self.btn_scale = QPushButton("Масштаб")
        self.btn_scale.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-weight: bold; border-radius: 4px; padding: 4px 10px; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
        )
        self.btn_scale.clicked.connect(self._apply_scale)
        l_trans.addWidget(self.btn_scale, 2, 4)

        # Кнопка сброса
        self.btn_reset = QPushButton("Сброс")
        self.btn_reset.setStyleSheet(
            "QPushButton { background-color: #f1f5f9; color: #475569; font-weight: bold; border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px; }"
            "QPushButton:hover { background-color: #e2e8f0; }"
        )
        self.btn_reset.clicked.connect(self._reset)
        l_trans.addWidget(self.btn_reset, 3, 0, 1, 5)

        panel_layout.addWidget(grp_trans)

        # Координаты вершин
        grp_vertices = QGroupBox("Координаты вершин")
        l_vertices = QVBoxLayout(grp_vertices)
        self.txt_vertices = QTextEdit(self)
        self.txt_vertices.setReadOnly(True)
        self.txt_vertices.setStyleSheet("font-family: Consolas, monospace; font-size: 11px; background-color: #f8f9fa; border: 1px solid #e2e8f0;")
        l_vertices.addWidget(self.txt_vertices)
        panel_layout.addWidget(grp_vertices)

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

    def _apply_translate(self) -> None:
        dx = self.spin_dx.value()
        dy = self.spin_dy.value()
        matrix = self._backend.translation_matrix(dx, dy)
        self.points = self._backend.apply(matrix, self.points)
        self._redraw()

    def _apply_rotate(self) -> None:
        angle_rad = math.radians(self.spin_angle.value())
        matrix = self._backend.rotation_matrix(angle_rad)
        self.points = self._backend.apply(matrix, self.points)
        self._redraw()

    def _apply_scale(self) -> None:
        s = self.spin_scale.value()
        matrix = self._backend.scale_matrix(s, s)
        self.points = self._backend.apply(matrix, self.points)
        self._redraw()

    def _reset(self) -> None:
        self.points = demo_polygon_2d()
        self._redraw()

    def _update_info(self) -> None:
        lines = [
            f"Расчёт: {self.backend_name}",
            f"Ориентация: {self.handedness.value.upper()}",
            "-" * 28,
            "Координаты вершин (x, y):",
        ]
        for i, (x, y) in enumerate(self.points):
            lines.append(f"  P{i}: ({x:+6.2f}, {y:+6.2f})")
        self.txt_vertices.setText("\n".join(lines))

    def _redraw(self) -> None:
        draw2d.setup_axes(self.ax, self.handedness)
        draw2d.draw_polygon(self.ax, self.points)
        self.canvas.draw()
        self._update_info()
