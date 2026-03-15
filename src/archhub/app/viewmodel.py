"""Qt view-models and list models for QML binding."""

from __future__ import annotations

from typing import Any, List, Optional

from PySide6.QtCore import QAbstractListModel, QObject, QModelIndex, Qt, Signal, Property, Slot

from archhub.backends import BackendRegistry
from archhub.core.models import (
    CacheStats,
    OrphanEntry,
    PackageDetails,
    PackageSource,
    PackageSummary,
    UpdateEntry,
)
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
        if role == StringListModel.TextRole:
            return self._items[index.row()]
        return None

    def setItems(self, items: List[str]) -> None:
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()


class AppViewModel(QObject):
    """Main view-model: sidebar counters, package/updates/orphans models, settings."""

    def __init__(self, registry: BackendRegistry, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._registry = registry
        self._package_service = PackageService(registry)
        self._updates_service = UpdatesService(registry)
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
        self._cache_stats = CacheStats()
        self._loading = False
        self._error_message: str = ""
        self._search_query: str = ""
        self._package_filter: str = "all"  # "all" | "pacman" | "aur"

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

    # --- Models (Qt Property so QML ListView can use them) ---
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
        if self._selected_package_name != value:
            self._selected_package_name = value
            self.selectedPackageNameChanged.emit()
            self._loadPackageDetails(value)

    selectedPackageNameChanged = Signal()
    selectedPackageName = Property(
        str, getSelectedPackageName, setSelectedPackageName, notify=selectedPackageNameChanged
    )

    @Slot(result=str)
    def getPackageDetailsName(self) -> str:
        return self._package_details.name if self._package_details else ""

    @Slot(result=str)
    def getPackageDetailsVersion(self) -> str:
        return self._package_details.version if self._package_details else ""

    @Slot(result=str)
    def getPackageDetailsDescription(self) -> str:
        return self._package_details.description if self._package_details else ""

    @Slot(result=int)
    def getPackageDetailsInstallSize(self) -> int:
        return self._package_details.install_size if self._package_details else 0

    @Slot(result=str)
    def getPackageDetailsLastUpdated(self) -> str:
        return self._package_details.last_updated or "" if self._package_details else ""

    @Slot(result=str)
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
        self._package_details = self._package_service.get_package_details(name)
        if self._package_details:
            self._deps_model.setItems(self._package_details.dependencies)
            self._optional_deps_model.setItems(self._package_details.optional_deps)
            self._conflicts_model.setItems(self._package_details.conflicts)
        else:
            self._deps_model.setItems([])
            self._optional_deps_model.setItems([])
            self._conflicts_model.setItems([])
        self._emitDetailsChanged()
        self.depsModelChanged.emit()
        self.optionalDepsModelChanged.emit()
        self.conflictsModelChanged.emit()

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

    # --- Refresh methods (call from QML or on load) ---
    @Slot()
    def refreshCounts(self) -> None:
        all_pkgs = self._package_service.get_installed_all()
        aur_pkgs = self._package_service.get_installed_aur()
        updates = self._updates_service.get_all_updates()
        self.setTotalPackages(len(all_pkgs))
        self.setAurPackages(len(aur_pkgs))
        self.setUpdatesCount(len(updates))

    @Slot()
    def refreshPackageList(self) -> None:
        self.setLoading(True)
        self.setErrorMessage("")
        try:
            if self._search_query.strip():
                include_aur = self._registry.get_enabled_aur_helper() is not None
                packages = self._package_service.search(self._search_query, include_aur=include_aur)
                # Filter by installed if we want only installed search results; for now show search
                self._package_model.setPackages(packages)
            else:
                source = None
                if self._package_filter == "aur":
                    source = PackageSource.AUR
                elif self._package_filter == "pacman":
                    source = PackageSource.REPO
                packages = self._package_service.get_installed(filter_source=source)
                self._package_model.setPackages(packages)
        except Exception as e:
            self.setErrorMessage(str(e))
            self._package_model.setPackages([])
        finally:
            self.setLoading(False)

    @Slot()
    def refreshUpdatesList(self) -> None:
        updates = self._updates_service.get_updates(self._updates_include_aur)
        self._update_model.setUpdates(updates)
        self.setUpdatesCount(len(updates))

    @Slot()
    def refreshOrphans(self) -> None:
        orphans = self._maintenance_service.get_orphans()
        self._orphan_model.setOrphans(orphans)

    @Slot()
    def refreshCacheStats(self) -> None:
        self._cache_stats = self._maintenance_service.get_cache_stats()

    @Slot()
    def refreshAll(self) -> None:
        self.refreshCounts()
        self.refreshPackageList()
        self.refreshUpdatesList()
        self.refreshOrphans()
        self.refreshCacheStats()
