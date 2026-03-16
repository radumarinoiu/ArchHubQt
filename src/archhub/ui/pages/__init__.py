from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ...app.viewmodel import AppViewModel
from .cache_page import CachePage
from .mirrors_page import MirrorsPage
from .orphans_page import OrphansPage
from .packages_page import PackagesPage
from .settings_page import SettingsPage
from .updates_page import UpdatesPage


class PageStackWidget(QWidget):
    """Content area: stacked pages and route handling (e.g. packages-search -> packages + search bar)."""

    def __init__(
        self,
        view_model: AppViewModel,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._view_model = view_model
        self._pages: dict[str, QWidget] = {}
        self._stack: Optional[QStackedWidget] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setMinimumWidth(600)
        self._stack.setMinimumHeight(500)

        self._pages["packages"] = PackagesPage(self._view_model, self)
        self._pages["updates"] = UpdatesPage(self._view_model, self)
        self._pages["mirrors"] = MirrorsPage(self._view_model, self)
        self._pages["orphans"] = OrphansPage(self._view_model, self)
        self._pages["cache"] = CachePage(self._view_model, self)
        self._pages["settings"] = SettingsPage(self._view_model, self)

        for widget in self._pages.values():
            self._stack.addWidget(widget)

        self._stack.setCurrentWidget(self._pages["packages"])
        layout.addWidget(self._stack, 1)

    def setCurrentPage(self, route: str) -> None:
        if route in self._pages:
            return self._stack.setCurrentWidget(self._pages[route])
        if route.startswith("packages:"):
            return self._stack.setCurrentWidget(self._pages["packages"])

__all__ = [
    "PageStackWidget",
    "CachePage",
    "MirrorsPage",
    "OrphansPage",
    "PackagesPage",
    "SettingsPage",
    "UpdatesPage",
]