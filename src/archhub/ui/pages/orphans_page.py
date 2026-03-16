"""Orphans page: list of orphan packages."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from archhub.app.viewmodel import AppViewModel


class OrphansPage(QWidget):
    """Find Orphans tab: list of unrequired packages."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._view_model = view_model
        self._build_ui()
        self._connect_signals()
        self._view_model.refreshOrphans()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self._list_widget = QListWidget()
        layout.addWidget(self._list_widget)
        self._sync_list()

    def _connect_signals(self) -> None:
        model = self._view_model.getOrphanModel()
        model.modelReset.connect(self._sync_list)

    def _sync_list(self) -> None:
        self._list_widget.clear()
        model = self._view_model.getOrphanModel()
        for row in range(model.rowCount()):
            display = model.data(model.index(row, 0), Qt.ItemDataRole.DisplayRole)
            self._list_widget.addItem(QListWidgetItem(display or ""))
