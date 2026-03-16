"""Qt view-models and list models for QtWidgets binding."""

from __future__ import annotations

from typing import Any, List, Optional

from PySide6.QtCore import (
    QAbstractListModel,
    QObject,
    QModelIndex,
    Qt,
    Signal,
    Property,
    Slot,
    QThread,
)

from archhub.backends import BackendRegistry
from archhub.core.cache_repository import CacheRepository
from archhub.core.models import (
    CacheStats,
    OrphanEntry,
    PackageDetails,
    PackageSource,
    PackageSummary,
    UpdateEntry,
)
from archhub.app.ui_loader import UiLoader
from archhub.services.maintenance_service import MaintenanceService
from archhub.services.package_service import PackageService
from archhub.services.settings_service import SettingsService
from archhub.services.updates_service import UpdatesService

class PackageListModel(QAbstractListModel):
    """List model for package summaries (name, version, source)."""

    NameRole = Qt.UserRole
    VersionRole = Qt.UserRole + 1
    SourceRole = Qt.UserRole + 2

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._packages: List[PackageSummary] = []

    def roleNames(self):
        return {
            PackageListModel.NameRole: b"name",
            PackageListModel.VersionRole: b"version",
            PackageListModel.SourceRole: b"source",
        }

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._packages) if not parent.isValid() else 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._packages)):
            return None
        p = self._packages[index.row()]
        if role == Qt.DisplayRole:
            return f"{p.name}  {p.version}"
        if role == PackageListModel.NameRole:
            return p.name
        if role == PackageListModel.VersionRole:
            return p.version
        if role == PackageListModel.SourceRole:
            return p.source.value
        return None

    def setPackages(self, packages: List[PackageSummary]) -> None:
        self.beginResetModel()
        self._packages = list(packages)
        self.endResetModel()


class UpdateListModel(QAbstractListModel):
    """List model for update entries."""

    NameRole = Qt.UserRole
    CurrentVersionRole = Qt.UserRole + 1
    NewVersionRole = Qt.UserRole + 2
    SourceRole = Qt.UserRole + 3

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._updates: List[UpdateEntry] = []

    def roleNames(self):
        return {
            UpdateListModel.NameRole: b"name",
            UpdateListModel.CurrentVersionRole: b"currentVersion",
            UpdateListModel.NewVersionRole: b"newVersion",
            UpdateListModel.SourceRole: b"source",
        }

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._updates) if not parent.isValid() else 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._updates)):
            return None
        u = self._updates[index.row()]
        if role == Qt.DisplayRole:
            return f"{u.name}  {u.current_version} → {u.new_version}"
        if role == UpdateListModel.NameRole:
            return u.name
        if role == UpdateListModel.CurrentVersionRole:
            return u.current_version
        if role == UpdateListModel.NewVersionRole:
            return u.new_version
        if role == UpdateListModel.SourceRole:
            return u.source.value
        return None

    def setUpdates(self, updates: List[UpdateEntry]) -> None:
        self.beginResetModel()
        self._updates = list(updates)
        self.endResetModel()


class OrphanListModel(QAbstractListModel):
    """List model for orphan entries."""

    NameRole = Qt.UserRole
    VersionRole = Qt.UserRole + 1

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._orphans: List[OrphanEntry] = []

    def roleNames(self):
        return {
            OrphanListModel.NameRole: b"name",
            OrphanListModel.VersionRole: b"version",
        }

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._orphans) if not parent.isValid() else 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._orphans)):
            return None
        o = self._orphans[index.row()]
        if role == Qt.DisplayRole:
            return f"{o.name}  {o.version}"
        if role == OrphanListModel.NameRole:
            return o.name
        if role == OrphanListModel.VersionRole:
            return o.version
        return None

    def setOrphans(self, orphans: List[OrphanEntry]) -> None:
        self.beginResetModel()
        self._orphans = list(orphans)
        self.endResetModel()


class StringListModel(QAbstractListModel):
    """Simple list model for string list (e.g. dependencies)."""

    TextRole = Qt.UserRole

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._items: List[str] = []

    def roleNames(self):
        return {StringListModel.TextRole: b"text"}

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._items) if not parent.isValid() else 0

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or not (0 <= index.row() < len(self._items)):
            return None
        if role == Qt.DisplayRole or role == StringListModel.TextRole:
            return self._items[index.row()]
        return None

    def setItems(self, items: List[str]) -> None:
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()


class AppViewModel(QObject):
    """Main view-model: sidebar counters, package/updates/orphans models, settings."""

    # Emitted to request background load (connected to UiLoader in worker thread)
    requestLoadInstalled = Signal(str)
    requestLoadSearch = Signal(str, bool)
    requestLoadDetails = Signal(str)
    requestLoadUpdates = Signal(bool)
    requestLoadOrphans = Signal()
    requestLoadCounts = Signal()
    requestCacheStats = Signal()

    def __init__(
        self,
        registry: BackendRegistry,
        parent: Optional[QObject] = None,
        *,
        cache_repo: Optional[CacheRepository] = None,
    ):
        super().__init__(parent)
        self._registry = registry
        self._cache_repo = cache_repo
        self._package_service = PackageService(registry, cache_repo=cache_repo)
        self._updates_service = UpdatesService(registry, cache_repo=cache_repo)
        self._maintenance_service = MaintenanceService(registry)
        self._settings_service = SettingsService(registry)

        self._package_model = PackageListModel(self)
        self._update_model = UpdateListModel(self)
        self._orphan_model = OrphanListModel(self)
        self._deps_model = StringListModel(self)
        self._optional_deps_model = StringListModel(self)
        self._conflicts_model = StringListModel(self)

        self._total_packages = 0
        self._aur_packages = 0
        self._updates_count = 0
        self._updates_include_aur = False
        self._selected_package_name: str = ""
        self._package_details: Optional[PackageDetails] = None
        self._selection_stack: List[str] = []  # history for Back when navigating via dependencies
        self._cache_stats = CacheStats()
        self._loading = False
        self._error_message: str = ""
        self._search_query: str = ""
        self._package_filter: str = "all"  # "all" | "pacman" | "aur"

        # Background loader (runs in worker thread)
        self._loader = UiLoader(
            self._package_service,
            self._updates_service,
            self._maintenance_service,
        )
        self._loader_thread = QThread(self)
        self._loader.moveToThread(self._loader_thread)
        self._loader_thread.start()
        queued = Qt.ConnectionType.QueuedConnection
        self._loader.installedReady.connect(self._on_installed_ready, queued)
        self._loader.searchReady.connect(self._on_search_ready, queued)
        self._loader.detailsReady.connect(self._on_details_ready, queued)
        self._loader.updatesReady.connect(self._on_updates_ready, queued)
        self._loader.orphansReady.connect(self._on_orphans_ready, queued)
        self._loader.countsReady.connect(self._on_counts_ready, queued)
        self._loader.cacheStatsReady.connect(self._on_cache_stats_ready, queued)
        self._loader.loadError.connect(self._on_load_error, queued)
        # Request signals (emitted from main thread -> loader runs in worker thread)
        self.requestLoadInstalled.connect(self._loader.load_installed, queued)
        self.requestLoadSearch.connect(self._loader.load_search, queued)
        self.requestLoadDetails.connect(self._loader.load_details, queued)
        self.requestLoadUpdates.connect(self._loader.load_updates, queued)
        self.requestLoadOrphans.connect(self._loader.load_orphans, queued)
        self.requestLoadCounts.connect(self._loader.load_counts, queued)
        # self.requestCacheStats.connect(self._loader.load_cache_stats, queued)
        self.destroyed.connect(self._on_destroyed)

    def _on_destroyed(self) -> None:
        if self._loader_thread.isRunning():
            self._loader_thread.quit()
            self._loader_thread.wait(2000)

    def _on_installed_ready(self, packages: List[PackageSummary]) -> None:
        self._package_model.setPackages(packages)
        self.setLoading(False)

    def _on_search_ready(self, packages: List[PackageSummary]) -> None:
        self._package_model.setPackages(packages)
        self.setLoading(False)

    def _on_details_ready(self, details: Optional[PackageDetails]) -> None:
        self._package_details = details
        if details:
            self._deps_model.setItems(details.dependencies)
            self._optional_deps_model.setItems(details.optional_deps)
            self._conflicts_model.setItems(details.conflicts)
        else:
            self._deps_model.setItems([])
            self._optional_deps_model.setItems([])
            self._conflicts_model.setItems([])
        self._emitDetailsChanged()
        self.depsModelChanged.emit()
        self.optionalDepsModelChanged.emit()
        self.conflictsModelChanged.emit()

    def _on_updates_ready(self, updates: List[UpdateEntry]) -> None:
        self._update_model.setUpdates(updates)
        self.setUpdatesCount(len(updates))

    def _on_orphans_ready(self, orphans: List[OrphanEntry]) -> None:
        self._orphan_model.setOrphans(orphans)

    def _on_counts_ready(self, total: int, aur: int, updates: int) -> None:
        self.setTotalPackages(total)
        self.setAurPackages(aur)
        self.setUpdatesCount(updates)

    def _on_cache_stats_ready(self, stats: CacheStats) -> None:
        self._cache_stats = stats
        self.cacheStatsChanged.emit()

    def _on_load_error(self, message: str) -> None:
        self.setErrorMessage(message)
        self.setLoading(False)
        self._package_model.setPackages([])

    def _request_load_installed(self) -> None:
        self.requestLoadInstalled.emit(self._package_filter)

    def _request_load_search(self) -> None:
        include_aur = self._registry.get_enabled_aur_helper() is not None
        self.requestLoadSearch.emit(self._search_query, include_aur)

    def _request_load_details(self, name: str) -> None:
        self.requestLoadDetails.emit(name)

    def _request_load_updates(self) -> None:
        self.requestLoadUpdates.emit(self._updates_include_aur)

    def _request_load_orphans(self) -> None:
        self.requestLoadOrphans.emit()

    def _request_load_counts(self) -> None:
        self.requestLoadCounts.emit()

    def _request_cache_stats(self) -> None:
        self.requestCacheStats.emit()

    # --- Counts (for sidebar) ---
    def getTotalPackages(self) -> int:
        return self._total_packages

    def setTotalPackages(self, value: int) -> None:
        if self._total_packages != value:
            self._total_packages = value
            self.totalPackagesChanged.emit()

    totalPackagesChanged = Signal()
    totalPackages = Property(int, getTotalPackages, setTotalPackages, notify=totalPackagesChanged)

    def getAurPackages(self) -> int:
        return self._aur_packages

    def setAurPackages(self, value: int) -> None:
        if self._aur_packages != value:
            self._aur_packages = value
            self.aurPackagesChanged.emit()

    aurPackagesChanged = Signal()
    aurPackages = Property(int, getAurPackages, setAurPackages, notify=aurPackagesChanged)

    def getUpdatesCount(self) -> int:
        return self._updates_count

    def setUpdatesCount(self, value: int) -> None:
        if self._updates_count != value:
            self._updates_count = value
            self.updatesCountChanged.emit()

    updatesCountChanged = Signal()
    updatesCount = Property(int, getUpdatesCount, setUpdatesCount, notify=updatesCountChanged)

    # --- Models (Qt Property for UI binding) ---
    packageModelChanged = Signal()
    updateModelChanged = Signal()
    orphanModelChanged = Signal()

    def getPackageModel(self) -> PackageListModel:
        return self._package_model

    def getUpdateModel(self) -> UpdateListModel:
        return self._update_model

    def getOrphanModel(self) -> OrphanListModel:
        return self._orphan_model

    def getDepsModel(self) -> StringListModel:
        return self._deps_model

    def getOptionalDepsModel(self) -> StringListModel:
        return self._optional_deps_model

    def getConflictsModel(self) -> StringListModel:
        return self._conflicts_model

    packageModel = Property(QObject, getPackageModel, notify=packageModelChanged)
    updateModel = Property(QObject, getUpdateModel, notify=updateModelChanged)
    orphanModel = Property(QObject, getOrphanModel, notify=orphanModelChanged)
    depsModelChanged = Signal()
    optionalDepsModelChanged = Signal()
    conflictsModelChanged = Signal()
    depsModel = Property(QObject, getDepsModel, notify=depsModelChanged)
    optionalDepsModel = Property(QObject, getOptionalDepsModel, notify=optionalDepsModelChanged)
    conflictsModel = Property(QObject, getConflictsModel, notify=conflictsModelChanged)

    # --- Package filter and selection ---
    def getPackageFilter(self) -> str:
        return self._package_filter

    def setPackageFilter(self, value: str) -> None:
        if self._package_filter != value:
            self._package_filter = value
            self.packageFilterChanged.emit()
            self.refreshPackageList()

    packageFilterChanged = Signal()
    packageFilter = Property(str, getPackageFilter, setPackageFilter, notify=packageFilterChanged)

    def getSelectedPackageName(self) -> str:
        return self._selected_package_name

    def setSelectedPackageName(self, value: str) -> None:
        """Set selected package (e.g. from list). Does not push onto back stack."""
        if self._selected_package_name != value:
            self._selected_package_name = value
            self.selectedPackageNameChanged.emit()
            self._loadPackageDetails(value)

    selectedPackageNameChanged = Signal()
    selectedPackageName = Property(
        str, getSelectedPackageName, setSelectedPackageName, notify=selectedPackageNameChanged
    )

    # --- Back navigation (only when opening a dependency from the details pane) ---
    def getCanGoBack(self) -> bool:
        return len(self._selection_stack) > 0

    canGoBackChanged = Signal()
    canGoBack = Property(bool, getCanGoBack, notify=canGoBackChanged)

    @Slot(str)
    def navigateToPackage(self, name: str) -> None:
        """Select a package from the details pane (e.g. clicked a dependency). Pushes current onto back stack."""
        if not name or name == self._selected_package_name:
            return
        if self._selected_package_name:
            self._selection_stack.append(self._selected_package_name)
            self.canGoBackChanged.emit()
        self._selected_package_name = name
        self.selectedPackageNameChanged.emit()
        self._loadPackageDetails(name)

    @Slot()
    def goBack(self) -> None:
        """Go back to the previous package in selection history (after clicking a dependency)."""
        if not self._selection_stack:
            return
        prev = self._selection_stack.pop()
        self.canGoBackChanged.emit()
        self._selected_package_name = prev
        self.selectedPackageNameChanged.emit()
        self._loadPackageDetails(prev)

    def getPackageDetailsName(self) -> str:
        return self._package_details.name if self._package_details else ""

    def getPackageDetailsVersion(self) -> str:
        return self._package_details.version if self._package_details else ""

    def getPackageDetailsDescription(self) -> str:
        return self._package_details.description if self._package_details else ""

    def getPackageDetailsInstallSize(self) -> int:
        return self._package_details.install_size if self._package_details else 0

    def getPackageDetailsLastUpdated(self) -> str:
        return self._package_details.last_updated or "" if self._package_details else ""

    def getPackageDetailsMaintainer(self) -> str:
        return self._package_details.maintainer or "" if self._package_details else ""

    def getPackageDetailsDependencies(self) -> List[str]:
        return self._package_details.dependencies if self._package_details else []

    def getPackageDetailsOptionalDeps(self) -> List[str]:
        return self._package_details.optional_deps if self._package_details else []

    def getPackageDetailsConflicts(self) -> List[str]:
        return self._package_details.conflicts if self._package_details else []

    packageDetailsNameChanged = Signal()
    packageDetailsVersionChanged = Signal()
    packageDetailsDescriptionChanged = Signal()
    packageDetailsInstallSizeChanged = Signal()
    packageDetailsLastUpdatedChanged = Signal()
    packageDetailsMaintainerChanged = Signal()
    packageDetailsDependenciesChanged = Signal()
    packageDetailsOptionalDepsChanged = Signal()
    packageDetailsConflictsChanged = Signal()

    packageDetailsName = Property(
        str, getPackageDetailsName, notify=packageDetailsNameChanged
    )
    packageDetailsVersion = Property(
        str, getPackageDetailsVersion, notify=packageDetailsVersionChanged
    )
    packageDetailsDescription = Property(
        str, getPackageDetailsDescription, notify=packageDetailsDescriptionChanged
    )
    packageDetailsInstallSize = Property(
        int, getPackageDetailsInstallSize, notify=packageDetailsInstallSizeChanged
    )
    packageDetailsLastUpdated = Property(
        str, getPackageDetailsLastUpdated, notify=packageDetailsLastUpdatedChanged
    )
    packageDetailsMaintainer = Property(
        str, getPackageDetailsMaintainer, notify=packageDetailsMaintainerChanged
    )

    def _emitDetailsChanged(self) -> None:
        self.packageDetailsNameChanged.emit()
        self.packageDetailsVersionChanged.emit()
        self.packageDetailsDescriptionChanged.emit()
        self.packageDetailsInstallSizeChanged.emit()
        self.packageDetailsLastUpdatedChanged.emit()
        self.packageDetailsMaintainerChanged.emit()
        self.packageDetailsDependenciesChanged.emit()
        self.packageDetailsOptionalDepsChanged.emit()
        self.packageDetailsConflictsChanged.emit()

    def _loadPackageDetails(self, name: str) -> None:
        if not name:
            self._package_details = None
            self._deps_model.setItems([])
            self._optional_deps_model.setItems([])
            self._conflicts_model.setItems([])
            self._emitDetailsChanged()
            self.depsModelChanged.emit()
            self.optionalDepsModelChanged.emit()
            self.conflictsModelChanged.emit()
            return
        self._request_load_details(name)

    # --- Updates toggle ---
    def getUpdatesIncludeAur(self) -> bool:
        return self._updates_include_aur

    def setUpdatesIncludeAur(self, value: bool) -> None:
        if self._updates_include_aur != value:
            self._updates_include_aur = value
            self.updatesIncludeAurChanged.emit()
            self.refreshUpdatesList()

    updatesIncludeAurChanged = Signal()
    updatesIncludeAur = Property(
        bool, getUpdatesIncludeAur, setUpdatesIncludeAur, notify=updatesIncludeAurChanged
    )

    @Slot(result=int)
    def getTotalDownloadSize(self) -> int:
        updates = self._updates_service.get_updates(self._updates_include_aur)
        return self._updates_service.total_download_size(updates)

    @Slot(result=int)
    def getCacheStatsSize(self) -> int:
        return self._cache_stats.total_size_bytes

    @Slot(result=int)
    def getCacheStatsCount(self) -> int:
        return self._cache_stats.package_count

    # --- Search ---
    def getSearchQuery(self) -> str:
        return self._search_query

    def setSearchQuery(self, value: str) -> None:
        if self._search_query != value:
            self._search_query = value
            self.searchQueryChanged.emit()
            self.refreshPackageList()

    searchQueryChanged = Signal()
    searchQuery = Property(str, getSearchQuery, setSearchQuery, notify=searchQueryChanged)

    # --- Loading / error ---
    def getLoading(self) -> bool:
        return self._loading

    def setLoading(self, value: bool) -> None:
        if self._loading != value:
            self._loading = value
            self.loadingChanged.emit()

    loadingChanged = Signal()
    loading = Property(bool, getLoading, setLoading, notify=loadingChanged)

    def getErrorMessage(self) -> str:
        return self._error_message

    def setErrorMessage(self, value: str) -> None:
        if self._error_message != value:
            self._error_message = value
            self.errorMessageChanged.emit()

    errorMessageChanged = Signal()
    errorMessage = Property(str, getErrorMessage, setErrorMessage, notify=errorMessageChanged)
    cacheStatsChanged = Signal()

    # --- Settings: helper enabled ---
    @Slot(str, result=bool)
    def getHelperEnabled(self, helper_id: str) -> bool:
        return self._registry.is_helper_enabled(helper_id)

    @Slot(str, bool)
    def setHelperEnabled(self, helper_id: str, enabled: bool) -> None:
        self._registry.set_helper_enabled(helper_id, enabled)
        self.refreshCounts()
        self.refreshPackageList()

    @Slot(result=str)
    def getPacmanConfPath(self) -> str:
        return self._settings_service.get_pacman_conf_path()

    @Slot(result=str)
    def getMirrorListPath(self) -> str:
        return self._settings_service.get_mirror_list_path()

    @Slot(result=list)
    def getAvailableHelperIds(self) -> List[str]:
        """Return list of AUR helper ids for settings UI."""
        return [h.id for h in self._settings_service.get_available_helpers()]

    # --- Refresh methods (request background load; results arrive via loader signals) ---
    @Slot()
    def refreshCounts(self) -> None:
        self._request_load_counts()

    @Slot()
    def refreshPackageList(self) -> None:
        self.setLoading(True)
        self.setErrorMessage("")
        if self._search_query.strip():
            self._request_load_search()
        else:
            self._request_load_installed()

    @Slot()
    def refreshInstalledCache(self) -> None:
        """Invalidate installed-package and updates cache, then refresh lists (e.g. bound to F5)."""
        self._package_service.refresh_installed_cache()
        if self._cache_repo:
            self._cache_repo.invalidate_updates(self._registry.repo().id)
            aur = self._registry.get_enabled_aur_helper()
            if aur:
                self._cache_repo.invalidate_updates(aur.id)
        self.refreshPackageList()
        self._request_load_updates()
        self._request_load_counts()

    @Slot()
    def refreshUpdatesList(self) -> None:
        self._request_load_updates()

    @Slot()
    def refreshOrphans(self) -> None:
        self._request_load_orphans()

    @Slot()
    def refreshCacheStats(self) -> None:
        self._request_cache_stats()

    @Slot()
    def refreshAll(self) -> None:
        self._request_load_counts()
        self.refreshPackageList()
        self._request_load_updates()
        self._request_load_orphans()
        self._request_cache_stats()
