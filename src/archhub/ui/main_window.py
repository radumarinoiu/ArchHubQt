"""Main application window: sidebar navigation and stacked pages."""

from __future__ import annotations

import os
from typing import Optional

from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QWidget,
)


from ..app.viewmodel import AppViewModel
from .pages import PageStackWidget
from .widgets import (
    SidebarWidget,
    VSeparatorWidget,
)


class MainWindow(QMainWindow):
    """Main window: sidebar + stacked content area."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._view_model = view_model
        self._sidebar: Optional[SidebarWidget] = None
        self._page_stack: Optional[PageStackWidget] = None
        self.setWindowTitle("ArchHub")
        self.resize(1000, 700)
        self._build_ui()
        self._setup_shortcuts()
        self._view_model.refreshAll()
        self._view_model.setPackageFilter("all")
        with open(os.path.join(os.path.dirname(__file__), "style.qss"), "r") as f:
            self.setStyleSheet(f.read())
        self._on_page_requested("packages")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self._sidebar = SidebarWidget(
            self._view_model,
            self,
            on_page_requested=self._on_page_requested,
        )
        central_layout.addWidget(self._sidebar)

        VSeparatorWidget(parent_layout=central_layout)

        self._page_stack = PageStackWidget(self._view_model, self)
        central_layout.addWidget(self._page_stack, 1)

    def _on_page_requested(self, route: str) -> None:
        self._sidebar.setCurrentPage(route)
        self._page_stack.setCurrentPage(route)
        # if route.startswith("packages"):
        #     target = "packages-search" if route == "packages:search" else "packages"
        #     self._page_stack.setCurrentPage(target)
        #     self._sidebar.setCurrentPage("packages")
        # else:
        #     self._page_stack.setCurrentPage(route)
        #     self._sidebar.setCurrentPage(route)

    def _setup_shortcuts(self) -> None:
        refresh = QAction(self)
        refresh.setShortcut(QKeySequence("F5"))
        refresh.triggered.connect(self._view_model.refreshInstalledCache)
        self.addAction(refresh)

    def closeEvent(self, event: QCloseEvent) -> None:
        thread = getattr(self._view_model, "_loader_thread", None)
        if thread is not None and thread.isRunning():
            thread.quit()
            thread.wait(2000)
        super().closeEvent(event)
