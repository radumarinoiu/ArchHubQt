"""Application entry point: Qt app and main window setup."""

from __future__ import annotations

import logging
import os
import sys

from PySide6.QtWidgets import QApplication

from archhub.app.viewmodel import AppViewModel
from archhub.backends import BackendRegistry
from archhub.core.cache_db import cache_session, create_cache_engine, init_cache_tables
from archhub.core.cache_repository import CacheRepository
from archhub.ui.main_window import MainWindow


def _setup_logging() -> None:
    """Configure logging for the app. Level can be set via ARCHHUB_LOG_LEVEL (e.g. DEBUG, INFO, WARNING)."""
    level_name = os.environ.get("ARCHHUB_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
        force=True,
    )


def main() -> None:
    """Console script entry point (e.g. from PKGBUILD or `archhub` command)."""
    _setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName("ArchHub")
    app.setOrganizationName("ArchHub")

    cache_engine = create_cache_engine()
    init_cache_tables(cache_engine)

    def session_factory():
        return cache_session(cache_engine)

    cache_repo = CacheRepository(session_factory)
    registry = BackendRegistry()
    view_model = AppViewModel(registry, cache_repo=cache_repo)
    window = MainWindow(view_model)
    window.show()

    sys.exit(app.exec())
