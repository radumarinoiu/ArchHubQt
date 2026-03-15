"""Cache page: cache stats placeholder."""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from archhub.app.viewmodel import AppViewModel


def _format_size(bytes_val: int) -> str:
    if bytes_val < 1024:
        return f"{bytes_val} B"
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KiB"
    return f"{bytes_val / (1024 * 1024):.1f} MiB"


class CachePage(QWidget):
    """Clear Cache tab: show cache stats."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._view_model = view_model
        self._build_ui()
        self._view_model.cacheStatsChanged.connect(self._update_labels)
        self._view_model.refreshCacheStats()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self._size_label = QLabel()
        self._count_label = QLabel()
        layout.addWidget(self._size_label)
        layout.addWidget(self._count_label)
        layout.addWidget(QLabel("Clear cache (not implemented yet)"))
        layout.addStretch()
        self._update_labels()

    def _update_labels(self) -> None:
        size = self._view_model.getCacheStatsSize()
        count = self._view_model.getCacheStatsCount()
        self._size_label.setText(f"Cache size: {_format_size(size)}")
        self._count_label.setText(f"Package count: {count}")
