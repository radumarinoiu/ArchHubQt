"""Updates page: list of upgradable packages."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from archhub.app.viewmodel import AppViewModel, UpdateListModel


def _format_size(bytes_val: int) -> str:
    if bytes_val < 1024:
        return f"{bytes_val} B"
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KiB"
    return f"{bytes_val / (1024 * 1024):.1f} MiB"


class UpdatesPage(QWidget):
    """Updates tab: include AUR toggle, download size, list of updates."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._view_model = view_model
        self._build_ui()
        self._connect_signals()
        self._view_model.refreshUpdatesList()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        row = QHBoxLayout()
        row.addWidget(QLabel("Include AUR updates"))
        self._aur_check = QCheckBox()
        self._aur_check.setChecked(self._view_model.updatesIncludeAur)
        row.addWidget(self._aur_check)
        row.addStretch()
        layout.addLayout(row)

        self._size_label = QLabel()
        layout.addWidget(self._size_label)

        self._list_widget = QListWidget()
        layout.addWidget(self._list_widget)

        btn_row = QHBoxLayout()
        update_sel = QPushButton("Update Selected")
        update_sel.setEnabled(False)
        update_sel.setToolTip("Not implemented yet")
        update_all = QPushButton("Update All")
        update_all.setEnabled(False)
        update_all.setToolTip("Not implemented yet")
        btn_row.addWidget(update_sel)
        btn_row.addWidget(update_all)
        layout.addLayout(btn_row)

        layout.addWidget(QLabel("Arch News preview"))
        layout.addWidget(QLabel("(Arch News preview not implemented)"))
        layout.addStretch()
        self._sync_list()
        self._update_size_label()

    def _connect_signals(self) -> None:
        self._aur_check.toggled.connect(self._view_model.setUpdatesIncludeAur)
        self._view_model.getUpdateModel().modelReset.connect(self._sync_list)
        self._view_model.getUpdateModel().modelReset.connect(self._update_size_label)

    def _sync_list(self) -> None:
        self._list_widget.clear()
        model = self._view_model.getUpdateModel()
        for row in range(model.rowCount()):
            display = model.data(model.index(row, 0), Qt.ItemDataRole.DisplayRole)
            self._list_widget.addItem(QListWidgetItem(display or ""))

    def _update_size_label(self) -> None:
        size = self._view_model.getTotalDownloadSize()
        self._size_label.setText(f"Total download size: {_format_size(size)}")
