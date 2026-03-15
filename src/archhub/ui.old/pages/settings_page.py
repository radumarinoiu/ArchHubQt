"""Settings page: AUR helpers, config paths."""

from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from archhub.app.viewmodel import AppViewModel


class SettingsPage(QWidget):
    """Settings tab: helper toggles, config file links."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._view_model = view_model
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        layout.addWidget(QLabel("AUR Helpers"))
        for helper_id in self._view_model.getAvailableHelperIds():
            cb = QCheckBox(helper_id)
            cb.setChecked(self._view_model.getHelperEnabled(helper_id))
            cb.toggled.connect(
                lambda checked, h=helper_id: self._view_model.setHelperEnabled(h, checked)
            )
            layout.addWidget(cb)

        layout.addWidget(QLabel("Shortcuts"))
        pacman_btn = QPushButton("Open Pacman Config")
        pacman_btn.clicked.connect(self._open_pacman_conf)
        layout.addWidget(pacman_btn)
        mirror_btn = QPushButton("Open Mirror List")
        mirror_btn.clicked.connect(self._open_mirror_list)
        layout.addWidget(mirror_btn)
        layout.addStretch()

    def _open_pacman_conf(self) -> None:
        path = self._view_model.getPacmanConfPath()
        if path and Path(path).exists():
            webbrowser.open(f"file://{path}")

    def _open_mirror_list(self) -> None:
        path = self._view_model.getMirrorListPath()
        if path and Path(path).exists():
            webbrowser.open(f"file://{path}")
