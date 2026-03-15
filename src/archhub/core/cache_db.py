"""SQLite cache DB: engine, session factory, and table creation."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from archhub.core.cache_models import (
    CacheSnapshot,
    PackageDetailsRow,
    PackageSummaryRow,
    UpdateEntryRow,
)


def cache_db_path() -> Path:
    """Return the cache DB path under XDG cache (or ~/.cache/archhub)."""
    xdg = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    base = Path(xdg) / "archhub"
    base.mkdir(parents=True, exist_ok=True)
    return base / "cache.db"


def create_cache_engine(path: Path | None = None):
    """Create the SQLModel engine for the cache DB."""
    p = path or cache_db_path()
    url = f"sqlite:///{p}"
    return create_engine(url, connect_args={"check_same_thread": False}, echo=False)


def init_cache_tables(engine) -> None:
    """Create all cache tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def cache_session(engine) -> Generator[Session, None, None]:
    """Yield a session for the cache engine."""
    with Session(engine) as session:
        yield session

