from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

from ...app.viewmodel import AppViewModel
from .widgets import (
    CountersCardWidget,
    HSeparatorWidget,
    PageButtonWidget,
    SubPageButtonWidget,
)


class SidebarWidget(QWidget):
    """Left sidebar: counters and navigation buttons."""

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
        self._package_filter = "all"
        self._page_buttons: list[PageButtonWidget] = list()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        CountersCardWidget(self._view_model.totalPackages, self._view_model.aurPackages, self._view_model.updatesCount, parent_layout=layout)

        HSeparatorWidget(parent_layout=layout)

        def on_page(page: str) -> None:
            self._current_page = page
            self._on_page_requested(page)
            self._update_checked()
        
        self._page_buttons = [
            PageButtonWidget("All Packages", "packages", on_page, parent_layout=layout),
            SubPageButtonWidget("Pacman", "packages:pacman", on_page, parent_layout=layout),
            SubPageButtonWidget("AUR", "packages:aur", on_page, parent_layout=layout),
            SubPageButtonWidget("Search Packages", "packages:search", on_page, parent_layout=layout),
            PageButtonWidget("Updates", "updates", on_page, parent_layout=layout),
            PageButtonWidget("Mirrors", "mirrors", on_page, parent_layout=layout),
            PageButtonWidget("Find Orphans", "orphans", on_page, parent_layout=layout),
            PageButtonWidget("Clear Cache", "cache", on_page, parent_layout=layout),
        ]

        layout.addStretch()

        self._page_buttons.append(PageButtonWidget("Settings", "settings", on_page, parent_layout=layout))

        # self._connect_signals()

    # def _connect_signals(self) -> None:
    #     self._view_model.totalPackagesChanged.connect(
    #         lambda: self._installed_label.setValue(str(self._view_model.totalPackages))
    #     )
    #     self._view_model.aurPackagesChanged.connect(
    #         lambda: self._aur_label.setValue(str(self._view_model.aurPackages))
    #     )
    #     self._view_model.aurPackagesChanged.connect(
    #         lambda: self._aur_btn.setVisible(self._view_model.aurPackages > 0)
    #     )
    #     self._view_model.updatesCountChanged.connect(
    #         lambda: self._updates_label.setValue(str(self._view_model.updatesCount))
    #     )
    #     self._aur_btn.setVisible(self._view_model.aurPackages > 0)

    def _update_checked(self) -> None:
        for btn in self._page_buttons:
            btn.setChecked(self._current_page == btn.page)

    def setCurrentPage(self, page: str) -> None:
        self._current_page = page
        self._update_checked()