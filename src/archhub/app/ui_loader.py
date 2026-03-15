"""Background data loader: runs service calls in a worker thread and emits results."""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QObject, Signal

from archhub.core.models import (
    CacheStats,
    OrphanEntry,
    PackageDetails,
    PackageSummary,
    UpdateEntry,
)
from archhub.services.maintenance_service import MaintenanceService
from archhub.services.package_service import PackageService
from archhub.services.updates_service import UpdatesService


class UiLoader(QObject):
    """Runs in a worker thread; calls services and emits results for the UI thread."""

    installedReady = Signal(object)  # List[PackageSummary]
    searchReady = Signal(object)  # List[PackageSummary]
    detailsReady = Signal(object)  # Optional[PackageDetails]
    updatesReady = Signal(object)  # List[UpdateEntry]
    orphansReady = Signal(object)  # List[OrphanEntry]
    countsReady = Signal(int, int, int)  # total, aur, updates
    cacheStatsReady = Signal(object)  # CacheStats
    loadError = Signal(str)

    def __init__(
        self,
        package_service: PackageService,
        updates_service: UpdatesService,
        maintenance_service: MaintenanceService,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._package_service = package_service
        self._updates_service = updates_service
        self._maintenance_service = maintenance_service

    def load_installed(self, pkg_filter: str) -> None:
        """Load installed packages (filter: all, pacman, aur). Runs in worker thread."""
        try:
            from archhub.core.models import PackageSource
            source = None
            if pkg_filter == "aur":
                source = PackageSource.AUR
            elif pkg_filter == "pacman":
                source = PackageSource.REPO
            packages = self._package_service.get_installed(filter_source=source)
            self.installedReady.emit(packages)
        except Exception as e:
            self.loadError.emit(str(e))

    def load_search(self, query: str, include_aur: bool) -> None:
        """Load search results. Runs in worker thread."""
        try:
            packages = self._package_service.search(query, include_aur=include_aur)
            self.searchReady.emit(packages)
        except Exception as e:
            self.loadError.emit(str(e))

    def load_details(self, name: str) -> None:
        """Load package details. Runs in worker thread."""
        try:
            details = self._package_service.get_package_details(name)
            self.detailsReady.emit(details)
        except Exception as e:
            self.loadError.emit(str(e))

    def load_updates(self, include_aur: bool) -> None:
        """Load updates list. Runs in worker thread."""
        try:
            updates = self._updates_service.get_updates(include_aur)
            self.updatesReady.emit(updates)
        except Exception as e:
            self.loadError.emit(str(e))

    def load_orphans(self) -> None:
        """Load orphans. Runs in worker thread."""
        try:
            orphans = self._maintenance_service.get_orphans()
            self.orphansReady.emit(orphans)
        except Exception as e:
            self.loadError.emit(str(e))

    def load_counts(self) -> None:
        """Load total/aur/updates counts. Runs in worker thread."""
        try:
            all_pkgs = self._package_service.get_installed_all()
            aur_pkgs = self._package_service.get_installed_aur()
            updates = self._updates_service.get_all_updates()
            self.countsReady.emit(len(all_pkgs), len(aur_pkgs), len(updates))
        except Exception as e:
            self.loadError.emit(str(e))

    def load_cache_stats(self) -> None:
        """Load cache stats. Runs in worker thread."""
        try:
            stats = self._maintenance_service.get_cache_stats()
            self.cacheStatsReady.emit(stats)
        except Exception as e:
            self.loadError.emit(str(e))
