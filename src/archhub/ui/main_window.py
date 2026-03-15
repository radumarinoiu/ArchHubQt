"""Main application window: sidebar navigation and stacked pages."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from archhub.app.viewmodel import AppViewModel
from archhub.ui.styles import SEPARATOR_LINE_STYLE
from archhub.ui.widgets import QPageButton, QSquareLabel, QSubPageButton


class MainWindow(QMainWindow):
    """Main window: sidebar + stacked content area."""
    def __init__(
        self,
        view_model: AppViewModel,
        parent: Optional[QWidget] = None,
        *,
        on_page_requested: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent)
        self._view_model = view_model
        self._on_page_requested = on_page_requested or (lambda _: None)
        self._current_page = "packages"
        self._stack = None
        self._sidebar = None
        self._page_buttons = []
        self.setWindowTitle("ArchHub")
        self.resize(1000, 700)
        self._build_ui()

    def _build_counters_layout(self) -> QLayout:
        counters_layout = QHBoxLayout()
        counters_layout.setContentsMargins(0, 0, 0, 0)
        counters_layout.setSpacing(0)

        installed_square_label = QSquareLabel("Installed", "0")
        aur_square_label = QSquareLabel("AUR", "0")
        updates_square_label = QSquareLabel("Updates", "0")

        counters_layout.addWidget(installed_square_label)
        counters_layout.addWidget(aur_square_label)
        counters_layout.addWidget(updates_square_label)

        return counters_layout
    
    def _build_page_buttons(self) -> list[QPageButton]:
        def on_click(page: str):
            self._current_page = page
            self._on_page_requested(page)
            for button in self._page_buttons:
                button.setChecked(button.page == page)

        page_buttons = [
            QPageButton("All Packages", "packages", on_click),
            QSubPageButton("Pacman", "packages:pacman", on_click),
            QSubPageButton("AUR", "packages:aur", on_click),
            QSubPageButton("Search Packages", "packages:search", on_click),
            QPageButton("Updates", "updates", on_click),
            QPageButton("Mirrors", "mirrors", on_click),
            QPageButton("Find Orphans", "orphans", on_click),
            QPageButton("Clear Cache", "cache", on_click),
            QPageButton("Settings", "settings", on_click),
        ]
        self._page_buttons = page_buttons
        return page_buttons

    def _build_left_sidebar_layout(self) -> QLayout:
        left_sidebar_layout = QVBoxLayout()
        left_sidebar_layout.setContentsMargins(8, 8, 8, 8)
        left_sidebar_layout.setSpacing(0)

        # title_label = QLabel("ArchHub")
        # title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 4px;")
        # title_label.setFixedWidth(220)

        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(SEPARATOR_LINE_STYLE)
        
        # left_sidebar_layout.addWidget(title_label)
        left_sidebar_layout.addLayout(self._build_counters_layout())
        left_sidebar_layout.addWidget(separator)

        for page_button in self._build_page_buttons():
            left_sidebar_layout.addWidget(page_button)
        
        left_sidebar_layout.addStretch()

        return left_sidebar_layout

    def _build_right_content_layout(self) -> QLayout:
        right_content_layout = QVBoxLayout()
        right_content_layout.setContentsMargins(0, 0, 0, 0)
        right_content_layout.setSpacing(0)

        # separator = QWidget()
        # separator.setFixedWidth(1)
        # separator.setStyleSheet(SEPARATOR_LINE_STYLE)

        self._stack = QStackedWidget()
        self._stack.setMinimumWidth(600)
        self._stack.setMinimumHeight(500)

        # right_content_layout.addWidget(separator)
        right_content_layout.addWidget(self._stack, 1)

        return right_content_layout

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet(SEPARATOR_LINE_STYLE)

        central_layout.addLayout(self._build_left_sidebar_layout())
        central_layout.addWidget(separator)
        central_layout.addLayout(self._build_right_content_layout())

    def closeEvent(self, event: QCloseEvent) -> None:
        thread = getattr(self._view_model, "_loader_thread", None)
        if thread is not None and thread.isRunning():
            thread.quit()
            thread.wait(2000)
        super().closeEvent(event)
