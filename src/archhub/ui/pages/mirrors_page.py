"""Mirrors page: placeholder."""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from archhub.app.viewmodel import AppViewModel


class MirrorsPage(QWidget):
    """Mirrors tab: placeholder."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Mirrors configuration (placeholder)"))
