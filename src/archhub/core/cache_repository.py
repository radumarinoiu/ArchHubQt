"""Cache repository: read/write cached package data, translating to/from domain models."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlmodel import Session, select

from archhub.core.cache_models import (
    CacheSnapshot,
    PackageDetailsRow,
    PackageSummaryRow,
    UpdateEntryRow,
)
from archhub.core.models import (
    PackageDetails,
    PackageSource,
    PackageSummary,
    UpdateEntry,
)

logger = logging.getLogger(__name__)

SCOPE_INSTALLED = "installed"
SCOPE_SEARCH = "search"
SCOPE_UPDATES = "updates"
SEARCH_TTL_SECONDS = 60


def _summary_row_to_domain(row: PackageSummaryRow) -> PackageSummary:
    source = PackageSource.AUR if row.source == "aur" else PackageSource.REPO
    return PackageSummary(name=row.name, version=row.version, source=source)


def _details_row_to_domain(row: PackageDetailsRow) -> PackageDetails:
    source = PackageSource.AUR if row.source == "aur" else PackageSource.REPO
    deps = json.loads(row.dependencies_json) if row.dependencies_json else []
    opt = json.loads(row.optional_deps_json) if row.optional_deps_json else []
    conf = json.loads(row.conflicts_json) if row.conflicts_json else []
    return PackageDetails(
        name=row.package_name,
        version=row.version,
        source=source,
        description=row.description or "",
        install_size=row.install_size or 0,
        last_updated=row.last_updated,
        maintainer=row.maintainer,
        dependencies=deps,
        optional_deps=opt,
        conflicts=conf,
    )


def _update_row_to_domain(row: UpdateEntryRow) -> UpdateEntry:
    source = PackageSource.AUR if row.source == "aur" else PackageSource.REPO
    return UpdateEntry(
        name=row.name,
        current_version=row.current_version,
        new_version=row.new_version,
        source=source,
        download_size=row.download_size or 0,
    )


def _domain_to_details_row(
    backend_id: str,
    d: PackageDetails,
) -> PackageDetailsRow:
    return PackageDetailsRow(
        backend_id=backend_id,
        package_name=d.name,
        version=d.version,
        source=d.source.value,
        description=d.description or "",
        install_size=d.install_size or 0,
        last_updated=d.last_updated,
        maintainer=d.maintainer,
        dependencies_json=json.dumps(d.dependencies),
        optional_deps_json=json.dumps(d.optional_deps),
        conflicts_json=json.dumps(d.conflicts),
    )


class CacheRepository:
    """Read/write package cache; translates between SQLModel rows and Pydantic models."""

    def __init__(self, session_factory):
        """session_factory: callable that returns a context manager yielding Session."""
        self._session_factory = session_factory

    def get_installed(self, backend_id: str) -> Optional[List[PackageSummary]]:
        """Return cached installed list for backend, or None if miss/expired."""
        with self._session_factory() as session:
            snapshot = session.exec(
                select(CacheSnapshot)
                .where(CacheSnapshot.backend_id == backend_id)
                .where(CacheSnapshot.scope == SCOPE_INSTALLED)
                .order_by(CacheSnapshot.fetched_at.desc())
                .limit(1)
            ).first()
            if not snapshot:
                return None
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            if snapshot.expires_at and now_utc > snapshot.expires_at:
                return None
            rows = session.exec(
                select(PackageSummaryRow).where(PackageSummaryRow.snapshot_id == snapshot.id)
            ).all()
            return [_summary_row_to_domain(r) for r in rows]

    def set_installed(self, backend_id: str, packages: List[PackageSummary]) -> None:
        """Store installed package list for backend (long-lived, no TTL)."""
        with self._session_factory() as session:
            snapshot = CacheSnapshot(
                backend_id=backend_id,
                scope=SCOPE_INSTALLED,
                query_key=None,
                expires_at=None,
            )
            session.add(snapshot)
            session.commit()
            session.refresh(snapshot)
            for p in packages:
                row = PackageSummaryRow(
                    snapshot_id=snapshot.id,
                    name=p.name,
                    version=p.version,
                    source=p.source.value,
                )
                session.add(row)
            session.commit()

    def invalidate_installed(self, backend_id: str) -> None:
        """Remove cached installed snapshots for backend (so next read refetches)."""
        with self._session_factory() as session:
            snapshots = session.exec(
                select(CacheSnapshot).where(
                    CacheSnapshot.backend_id == backend_id,
                    CacheSnapshot.scope == SCOPE_INSTALLED,
                )
            ).all()
            for sn in snapshots:
                rows = session.exec(select(PackageSummaryRow).where(PackageSummaryRow.snapshot_id == sn.id)).all()
                for r in rows:
                    session.delete(r)
                session.delete(sn)
            session.commit()

    def get_search(
        self,
        backend_id: str,
        query_key: str,
    ) -> Optional[List[PackageSummary]]:
        """Return cached search results if not expired (1 min TTL)."""
        with self._session_factory() as session:
            snapshot = session.exec(
                select(CacheSnapshot)
                .where(CacheSnapshot.backend_id == backend_id)
                .where(CacheSnapshot.scope == SCOPE_SEARCH)
                .where(CacheSnapshot.query_key == query_key)
                .order_by(CacheSnapshot.fetched_at.desc())
                .limit(1)
            ).first()
            if not snapshot:
                return None
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            if snapshot.expires_at and now_utc > snapshot.expires_at:
                return None
            rows = session.exec(
                select(PackageSummaryRow).where(PackageSummaryRow.snapshot_id == snapshot.id)
            ).all()
            return [_summary_row_to_domain(r) for r in rows]

    def set_search(
        self,
        backend_id: str,
        query_key: str,
        packages: List[PackageSummary],
        ttl_seconds: int = SEARCH_TTL_SECONDS,
    ) -> None:
        """Store search results with TTL."""
        with self._session_factory() as session:
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            expires_at = now_utc + timedelta(seconds=ttl_seconds)
            snapshot = CacheSnapshot(
                backend_id=backend_id,
                scope=SCOPE_SEARCH,
                query_key=query_key,
                expires_at=expires_at,
            )
            session.add(snapshot)
            session.commit()
            session.refresh(snapshot)
            for p in packages:
                row = PackageSummaryRow(
                    snapshot_id=snapshot.id,
                    name=p.name,
                    version=p.version,
                    source=p.source.value,
                )
                session.add(row)
            session.commit()

    def get_package_details(self, backend_id: str, package_name: str) -> Optional[PackageDetails]:
        """Return cached package details or None."""
        with self._session_factory() as session:
            row = session.exec(
                select(PackageDetailsRow).where(
                    PackageDetailsRow.backend_id == backend_id,
                    PackageDetailsRow.package_name == package_name,
                )
            ).first()
            if not row:
                return None
            return _details_row_to_domain(row)

    def set_package_details(self, backend_id: str, details: PackageDetails) -> None:
        """Store or replace package details for backend/package."""
        with self._session_factory() as session:
            existing = session.exec(
                select(PackageDetailsRow).where(
                    PackageDetailsRow.backend_id == backend_id,
                    PackageDetailsRow.package_name == details.name,
                )
            ).first()
            if existing:
                session.delete(existing)
                session.commit()
            row = _domain_to_details_row(backend_id, details)
            session.add(row)
            session.commit()

    def invalidate_package_details(self, backend_id: str, package_name: str) -> None:
        """Remove cached details for one package (e.g. after upgrade)."""
        with self._session_factory() as session:
            row = session.exec(
                select(PackageDetailsRow).where(
                    PackageDetailsRow.backend_id == backend_id,
                    PackageDetailsRow.package_name == package_name,
                )
            ).first()
            if row:
                session.delete(row)
                session.commit()

    def get_updates(self, backend_id: str) -> Optional[List[UpdateEntry]]:
        """Return cached updates list for backend, or None if miss."""
        with self._session_factory() as session:
            snapshot = session.exec(
                select(CacheSnapshot)
                .where(CacheSnapshot.backend_id == backend_id)
                .where(CacheSnapshot.scope == SCOPE_UPDATES)
                .order_by(CacheSnapshot.fetched_at.desc())
                .limit(1)
            ).first()
            if not snapshot:
                return None
            now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
            if snapshot.expires_at and now_utc > snapshot.expires_at:
                return None
            rows = session.exec(
                select(UpdateEntryRow).where(UpdateEntryRow.snapshot_id == snapshot.id)
            ).all()
            return [_update_row_to_domain(r) for r in rows]

    def set_updates(self, backend_id: str, entries: List[UpdateEntry]) -> None:
        """Store updates list for backend (long-lived, no TTL)."""
        with self._session_factory() as session:
            snapshot = CacheSnapshot(
                backend_id=backend_id,
                scope=SCOPE_UPDATES,
                query_key=None,
                expires_at=None,
            )
            session.add(snapshot)
            session.commit()
            session.refresh(snapshot)
            for e in entries:
                row = UpdateEntryRow(
                    snapshot_id=snapshot.id,
                    name=e.name,
                    current_version=e.current_version,
                    new_version=e.new_version,
                    source=e.source.value,
                    download_size=e.download_size or 0,
                )
                session.add(row)
            session.commit()

    def invalidate_updates(self, backend_id: str) -> None:
        """Remove cached updates snapshots for backend (so next read refetches)."""
        with self._session_factory() as session:
            snapshots = session.exec(
                select(CacheSnapshot).where(
                    CacheSnapshot.backend_id == backend_id,
                    CacheSnapshot.scope == SCOPE_UPDATES,
                )
            ).all()
            for sn in snapshots:
                rows = session.exec(
                    select(UpdateEntryRow).where(UpdateEntryRow.snapshot_id == sn.id)
                ).all()
                for r in rows:
                    session.delete(r)
                session.delete(sn)
            session.commit()
