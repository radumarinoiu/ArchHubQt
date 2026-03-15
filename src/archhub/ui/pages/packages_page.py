"""Packages page: list, search, filter, and package details."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from archhub.app.viewmodel import AppViewModel, PackageListModel


def _format_size(bytes_val: int) -> str:
    if bytes_val < 1024:
        return f"{bytes_val} B"
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KiB"
    return f"{bytes_val / (1024 * 1024):.1f} MiB"


class PackageDetailsWidget(QWidget):
    """Right-hand panel: selected package details and dependency lists."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._view_model = view_model
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self._name_label = QLabel()
        self._name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self._name_label)

        grid = QVBoxLayout()
        self._version_label = QLabel("Version: ")
        self._size_label = QLabel("Install size: ")
        self._updated_label = QLabel("Last updated: ")
        self._maintainer_label = QLabel("Maintainer: ")
        grid.addWidget(self._version_label)
        grid.addWidget(self._size_label)
        grid.addWidget(self._updated_label)
        grid.addWidget(self._maintainer_label)
        layout.addLayout(grid)

        self._desc_label = QLabel()
        self._desc_label.setWordWrap(True)
        layout.addWidget(self._desc_label)

        self._tabs = QTabWidget()
        self._deps_list = QListWidget()
        self._opt_deps_list = QListWidget()
        self._conflicts_list = QListWidget()
        self._tabs.addTab(self._deps_list, "Dependencies")
        self._tabs.addTab(self._opt_deps_list, "Optional Deps")
        self._tabs.addTab(self._conflicts_list, "Conflicts")
        layout.addWidget(self._tabs)

        self._back_btn = QPushButton("← Back")
        self._back_btn.clicked.connect(self._view_model.goBack)
        layout.addWidget(self._back_btn)

        layout.addStretch()
        self._update_content()
        self._refresh_detail_labels()

    def _connect_signals(self) -> None:
        self._view_model.selectedPackageNameChanged.connect(self._update_content)
        self._view_model.packageDetailsNameChanged.connect(self._update_content)
        self._view_model.packageDetailsVersionChanged.connect(self._refresh_detail_labels)
        self._view_model.packageDetailsInstallSizeChanged.connect(self._refresh_detail_labels)
        self._view_model.packageDetailsLastUpdatedChanged.connect(self._refresh_detail_labels)
        self._view_model.packageDetailsMaintainerChanged.connect(self._refresh_detail_labels)
        self._view_model.canGoBackChanged.connect(self._on_can_go_back_changed)

    def _refresh_detail_labels(self) -> None:
        self._version_label.setText("Version: " + self._view_model.packageDetailsVersion)
        self._size_label.setText(
            "Install size: " + _format_size(self._view_model.packageDetailsInstallSize)
        )
        self._updated_label.setText(
            "Last updated: " + self._view_model.packageDetailsLastUpdated
        )
        self._maintainer_label.setText(
            "Maintainer: " + self._view_model.packageDetailsMaintainer
        )

    def _on_can_go_back_changed(self) -> None:
        self._back_btn.setVisible(self._view_model.canGoBack)

    def _update_content(self) -> None:
        name = self._view_model.selectedPackageName
        self._back_btn.setVisible(self._view_model.canGoBack)
        if not name:
            self._name_label.setText("")
            self._desc_label.setText("")
            self._deps_list.clear()
            self._opt_deps_list.clear()
            self._conflicts_list.clear()
            return
        self._name_label.setText(self._view_model.packageDetailsName)
        self._desc_label.setText(self._view_model.packageDetailsDescription)
        self._deps_list.clear()
        for dep in self._view_model.getPackageDetailsDependencies():
            item = QListWidgetItem(dep)
            self._deps_list.addItem(item)
        self._opt_deps_list.clear()
        for dep in self._view_model.getPackageDetailsOptionalDeps():
            item = QListWidgetItem(dep)
            self._opt_deps_list.addItem(item)
        self._conflicts_list.clear()
        for c in self._view_model.getPackageDetailsConflicts():
            item = QListWidgetItem(c)
            self._conflicts_list.addItem(item)
        self._refresh_detail_labels()


class PackagesPage(QWidget):
    """Packages tab: package list, search bar, details pane."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._view_model = view_model
        self.showSearchBar = False
        self._build_ui()
        self._connect_signals()
        self._view_model.refreshPackageList()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._search_row = QWidget()
        search_layout = QHBoxLayout(self._search_row)
        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("Search packages...")
        search_layout.addWidget(self._search_field)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self._search_field.clear())
        search_layout.addWidget(clear_btn)
        layout.addWidget(self._search_row)
        self._search_row.setVisible(self.showSearchBar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._list_view = QListWidget()
        self._list_view.setMinimumWidth(280)
        model = self._view_model.getPackageModel()
        # QListWidget doesn't use QAbstractListModel directly; we need to sync from model
        self._package_model = model
        splitter.addWidget(self._list_view)

        self._details_widget = PackageDetailsWidget(self._view_model, self)
        self._details_widget.setMinimumWidth(320)
        splitter.addWidget(self._details_widget)
        layout.addWidget(splitter)

        self._loading_bar = QProgressBar()
        self._loading_bar.setRange(0, 0)
        self._loading_bar.setVisible(False)
        layout.addWidget(self._loading_bar)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        self._sync_list_from_model()

    def setShowSearchBar(self, visible: bool) -> None:
        self.showSearchBar = visible
        if hasattr(self, "_search_row"):
            self._search_row.setVisible(visible)

    def _connect_signals(self) -> None:
        self._search_field.textChanged.connect(self._on_search_changed)
        self._list_view.currentRowChanged.connect(self._on_list_selection_changed)
        self._view_model.loadingChanged.connect(self._on_loading_changed)
        self._view_model.errorMessageChanged.connect(self._on_error_changed)
        self._package_model.modelReset.connect(self._sync_list_from_model)
        self._details_widget._deps_list.itemClicked.connect(self._on_dep_clicked)
        self._details_widget._opt_deps_list.itemClicked.connect(self._on_dep_clicked)

    def _on_search_changed(self, text: str) -> None:
        self._view_model.setSearchQuery(text)

    def _on_list_selection_changed(self, row: int) -> None:
        if row < 0:
            return
        item = self._list_view.item(row)
        if item is None:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        if name is not None:
            self._view_model.setSelectedPackageName(name)

    def _on_dep_clicked(self, item: QListWidgetItem) -> None:
        name = item.text()
        if name:
            self._view_model.navigateToPackage(name)

    def _on_loading_changed(self) -> None:
        self._loading_bar.setVisible(self._view_model.loading)

    def _on_error_changed(self) -> None:
        msg = self._view_model.errorMessage
        self._error_label.setText(msg)
        self._error_label.setVisible(bool(msg))

    def _sync_list_from_model(self) -> None:
        self._list_view.clear()
        model = self._package_model
        for row in range(model.rowCount()):
            name = model.data(model.index(row, 0), PackageListModel.NameRole)
            display = model.data(model.index(row, 0), Qt.ItemDataRole.DisplayRole)
            item = QListWidgetItem(display or str(name))
            item.setData(Qt.ItemDataRole.UserRole, name)
            self._list_view.addItem(item)
        if self._view_model.selectedPackageName:
            for i in range(self._list_view.count()):
                if self._list_view.item(i).data(Qt.ItemDataRole.UserRole) == self._view_model.selectedPackageName:
                    self._list_view.setCurrentRow(i)
                    break
