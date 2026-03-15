"""SQLModel table definitions for the package cache."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utc_now_naive() -> datetime:
    """Return current UTC time as naive datetime for SQLite compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CacheSnapshot(SQLModel, table=True):
    """Metadata for one cached fetch (installed list or search result)."""

    __tablename__ = "cache_snapshot"

    id: Optional[int] = Field(default=None, primary_key=True)
    backend_id: str = Field(index=True)
    scope: str = Field(index=True)  # "installed" | "search" | "updates"
    query_key: Optional[str] = Field(default=None, index=True)  # normalized query for search
    fetched_at: datetime = Field(default_factory=_utc_now_naive)
    expires_at: Optional[datetime] = None


class PackageSummaryRow(SQLModel, table=True):
    """One package summary (installed or search result) linked to a snapshot."""

    __tablename__ = "package_summary_row"

    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_id: int = Field(foreign_key="cache_snapshot.id", index=True)
    name: str = Field(index=True)
    version: str = ""
    source: str = "repo"  # "repo" | "aur"


class PackageDetailsRow(SQLModel, table=True):
    """Cached package details per backend and package name."""

    __tablename__ = "package_details_row"

    id: Optional[int] = Field(default=None, primary_key=True)
    backend_id: str = Field(index=True)
    package_name: str = Field(index=True)
    version: str = ""
    source: str = "repo"
    description: str = ""
    install_size: int = 0
    last_updated: Optional[str] = None
    maintainer: Optional[str] = None
    dependencies_json: str = "[]"  # JSON array of strings
    optional_deps_json: str = "[]"
    conflicts_json: str = "[]"
    fetched_at: datetime = Field(default_factory=_utc_now_naive)


class UpdateEntryRow(SQLModel, table=True):
    """One update entry linked to an updates snapshot."""

    __tablename__ = "update_entry_row"

    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_id: int = Field(foreign_key="cache_snapshot.id", index=True)
    name: str = Field(index=True)
    current_version: str = ""
    new_version: str = ""
    source: str = "repo"  # "repo" | "aur"
    download_size: int = 0
