import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from coordsys.modes.mode1_guess import GuessOrientationMode
from coordsys.modes.mode2_plane import PlaneTransformMode
from coordsys.modes.mode3_space import SpaceTransformMode


class CoordSysMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Системы координат и однородные координаты")
        self.resize(1150, 750)
        self.setMinimumSize(900, 600)

        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(
            "QMainWindow { background-color: #f8fafc; }"
            "QWidget { font-family: 'Segoe UI', -apple-system, sans-serif; color: #0f172a; }"
            "QTabWidget::pane { border: 1px solid #e2e8f0; background: #ffffff; border-radius: 6px; }"
            "QTabBar::tab { font-size: 13px; font-weight: bold; padding: 10px 22px; background: #e2e8f0; color: #475569; margin-right: 4px; border-top-left-radius: 6px; border-top-right-radius: 6px; }"
            "QTabBar::tab:selected { background: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; border-bottom: none; }"
            "QTabBar::tab:hover { background: #cbd5e1; }"
        )

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 12, 12, 12)

        self.tabs = QTabWidget()

        self.mode1 = GuessOrientationMode(self)
        self.mode2 = PlaneTransformMode(self)
        self.mode3 = SpaceTransformMode(self)

        self.tabs.addTab(self.mode1, "Режим 1: Определение ориентации 3D")
        self.tabs.addTab(self.mode2, "Режим 2: 2D-преобразования")
        self.tabs.addTab(self.mode3, "Режим 3: 3D-преобразования")

        layout.addWidget(self.tabs)


def main() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = CoordSysMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
