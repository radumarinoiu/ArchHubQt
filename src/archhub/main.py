"""Application entry point: Qt app and QML engine setup."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from archhub.app.viewmodel import AppViewModel
from archhub.backends import BackendRegistry
from archhub.core.cache_db import cache_session, create_cache_engine, init_cache_tables
from archhub.core.cache_repository import CacheRepository


def _qml_dir() -> Path:
    """Return the directory containing main.qml, for source or installed layout."""
    # When run as module or script from repo: __file__ is in src/archhub/main.py
    # so ui/qml is next to archhub package.
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent
    # Try package-relative: archhub/ui/qml
    qml = base / "ui" / "qml"
    if qml.is_dir():
        return qml
    # Installed: e.g. /usr/share/archhub/qml or prefix/share/archhub/qml
    for prefix in [Path(sys.prefix), Path("/usr")]:
        qml = prefix / "share" / "archhub" / "qml"
        if qml.is_dir():
            return qml
    return base / "ui" / "qml"


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
    app = QGuiApplication(sys.argv)
    app.setApplicationName("ArchHub")
    app.setOrganizationName("ArchHub")

    qml_dir = _qml_dir()
    main_qml = qml_dir / "main.qml"
    if not main_qml.exists():
        print(f"Fatal: main.qml not found at {main_qml}", file=sys.stderr)
        sys.exit(1)

    engine = QQmlApplicationEngine()
    engine.addImportPath(str(qml_dir))

    cache_engine = create_cache_engine()
    init_cache_tables(cache_engine)

    def session_factory():
        return cache_session(cache_engine)

    cache_repo = CacheRepository(session_factory)
    registry = BackendRegistry()
    view_model = AppViewModel(registry, cache_repo=cache_repo)
    engine.rootContext().setContextProperty("appModel", view_model)
    # Expose models directly so QML ListView can use them (nested Property can be unreliable)
    engine.rootContext().setContextProperty("packageModel", view_model.getPackageModel())
    engine.rootContext().setContextProperty("updateModel", view_model.getUpdateModel())
    engine.rootContext().setContextProperty("orphanModel", view_model.getOrphanModel())

    engine.load(QUrl.fromLocalFile(str(main_qml)))
    if not engine.rootObjects():
        print("Fatal: QML root object not created", file=sys.stderr)
        sys.exit(1)

    sys.exit(app.exec())
