"""Режим 1 — задание с практики: определение ориентации трехмерной системы координат.

Случайным образом генерируется правая или левая 3D-система координат и случайный поворот.
Отрисовываются координатные оси. Пользователь выбирает «Правая» или «Левая»,
приложение сообщает «Верно» или «Неверно».
"""

from __future__ import annotations

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from coordsys.core.orientation import Handedness, RandomTrial, random_trial
from coordsys.rendering import draw3d
from coordsys.transforms import manual as transforms


def _rotated_basis(trial: RandomTrial) -> dict[str, np.ndarray]:
    """Строит три повернутых базисных вектора для текущего испытания."""
    z_sign = 1.0 if trial.handedness is Handedness.RIGHT else -1.0
    base_points = [
        (draw3d.AXIS_LENGTH, 0.0, 0.0),
        (0.0, draw3d.AXIS_LENGTH, 0.0),
        (0.0, 0.0, draw3d.AXIS_LENGTH * z_sign),
    ]

    ax_rad, ay_rad, az_rad = (np.radians(a) for a in trial.angles_deg)
    rotation = transforms.combine_3d(
        transforms.rotation_matrix_3d("z", az_rad),
        transforms.rotation_matrix_3d("y", ay_rad),
        transforms.rotation_matrix_3d("x", ax_rad),
    )
    rotated = transforms.apply_3d(rotation, base_points)
    names = ("x", "y", "z")
    return {name: np.array(point) for name, point in zip(names, rotated)}


class GuessOrientationMode(QWidget):
    """Виджет Режима 1: Определение ориентации 3D системы координат."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.trial: RandomTrial = random_trial()
        self.score_correct = 0
        self.score_total = 0
        self.answered = False

        self._build_ui()
        self._new_trial()

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
        )
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 25, 20, 25)
        panel_layout.setSpacing(15)

        title = QLabel("Ориентация системы координат")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e293b; border: none;")
        panel_layout.addWidget(title)

        panel_layout.addSpacing(10)

        # Кнопки ответа
        self.btn_right = QPushButton("Правая")
        self.btn_right.setFixedHeight(42)
        self.btn_right.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_right.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
            "QPushButton:disabled { background-color: #cbd5e1; color: #64748b; }"
        )
        self.btn_right.clicked.connect(lambda: self._check_answer(Handedness.RIGHT))
        panel_layout.addWidget(self.btn_right)

        self.btn_left = QPushButton("Левая")
        self.btn_left.setFixedHeight(42)
        self.btn_left.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_left.setStyleSheet(
            "QPushButton { background-color: #2563eb; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; }"
            "QPushButton:hover { background-color: #1d4ed8; }"
            "QPushButton:disabled { background-color: #cbd5e1; color: #64748b; }"
        )
        self.btn_left.clicked.connect(lambda: self._check_answer(Handedness.LEFT))
        panel_layout.addWidget(self.btn_left)

        # Результат
        self.lbl_verdict = QLabel("")
        self.lbl_verdict.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b; border: none; margin-top: 10px;")
        panel_layout.addWidget(self.lbl_verdict)

        panel_layout.addStretch()

        self.btn_next = QPushButton("Новое задание")
        self.btn_next.setFixedHeight(40)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet(
            "QPushButton { background-color: #f1f5f9; color: #0f172a; font-weight: bold; font-size: 13px; border-radius: 6px; border: 1px solid #cbd5e1; }"
            "QPushButton:hover { background-color: #e2e8f0; }"
        )
        self.btn_next.clicked.connect(self._new_trial)
        panel_layout.addWidget(self.btn_next)

        self.lbl_stats = QLabel("Счет: 0 / 0")
        self.lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_stats.setStyleSheet("font-weight: bold; color: #475569; font-size: 13px; border: none;")
        panel_layout.addWidget(self.lbl_stats)

        layout.addWidget(panel, stretch=2)

    def _draw_trial(self) -> None:
        vectors = _rotated_basis(self.trial)
        self.ax.clear()
        limit = draw3d.AXIS_LENGTH * 1.3
        self.ax.set_xlim(-limit, limit)
        self.ax.set_ylim(-limit, limit)
        self.ax.set_zlim(-limit, limit)
        self.ax.set_box_aspect([1, 1, 1])

        colors = {"x": "red", "y": "green", "z": "blue"}
        for name, vec in vectors.items():
            col = colors[name]
            self.ax.quiver(0, 0, 0, *vec, color=col, arrow_length_ratio=0.15, linewidth=2.5)
            self.ax.text(*(vec * 1.15), name.upper(), color=col, fontsize=12, fontweight="bold")

        self.ax.set_title("3D система координат (X: красный, Y: зеленый, Z: синий)")
        self.canvas.draw()

    def _check_answer(self, guess: Handedness) -> None:
        if self.answered:
            return
        self.answered = True
        self.score_total += 1

        correct = (guess is self.trial.handedness)
        if correct:
            self.score_correct += 1
            self.lbl_verdict.setText("Верно")
            self.lbl_verdict.setStyleSheet("font-size: 16px; font-weight: bold; color: #16a34a; border: none;")
        else:
            self.lbl_verdict.setText("Неверно")
            self.lbl_verdict.setStyleSheet("font-size: 16px; font-weight: bold; color: #dc2626; border: none;")

        self.lbl_stats.setText(f"Счет: {self.score_correct} / {self.score_total}")

        self.btn_right.setEnabled(False)
        self.btn_left.setEnabled(False)

    def _new_trial(self) -> None:
        self.trial = random_trial()
        self.answered = False
        self.btn_right.setEnabled(True)
        self.btn_left.setEnabled(True)
        self.lbl_verdict.setText("")
        self._draw_trial()
