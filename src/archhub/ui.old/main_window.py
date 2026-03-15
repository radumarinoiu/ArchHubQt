"""Main application window: sidebar navigation and stacked pages."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from archhub.app.viewmodel import AppViewModel


class SidebarWidget(QWidget):
    """Left sidebar: counters and navigation buttons."""

    def __init__(
        self,
        view_model: AppViewModel,
        parent: Optional[QWidget] = None,
        *,
        on_page_requested: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent)
        self._view_model = view_model
        self._on_page_requested = on_page_requested or (lambda _: None)
        self._current_page = "packages"
        self._package_filter = "all"
        self._nav_buttons: list[tuple[QPushButton, str, str]] = []  # (btn, page, filter)
        self._page_buttons: list[tuple[QPushButton, str]] = []  # (btn, page)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Counters
        counters = QVBoxLayout()
        counters.setSpacing(4)
        self._pkg_count_label = QLabel(str(self._view_model.totalPackages))
        self._aur_count_label = QLabel(str(self._view_model.aurPackages))
        self._updates_count_label = QLabel(str(self._view_model.updatesCount))
        counters.addWidget(self._counter_card("Packages", self._pkg_count_label))
        counters.addWidget(self._counter_card("AUR", self._aur_count_label))
        counters.addWidget(self._counter_card("Updates", self._updates_count_label))
        layout.addLayout(counters)
        aur_btn = self._nav_button("AUR", "packages", "aur")
        self._view_model.totalPackagesChanged.connect(
            lambda: self._pkg_count_label.setText(str(self._view_model.totalPackages))
        )
        self._view_model.aurPackagesChanged.connect(
            lambda: self._aur_count_label.setText(str(self._view_model.aurPackages))
        )
        self._view_model.aurPackagesChanged.connect(
            lambda: aur_btn.setVisible(self._view_model.aurPackages > 0)
        )
        self._view_model.updatesCountChanged.connect(
            lambda: self._updates_count_label.setText(str(self._view_model.updatesCount))
        )

        # Packages section
        layout.addWidget(self._section_label("Packages"))
        layout.addWidget(self._nav_button("All Packages", "packages", "all"))
        layout.addWidget(self._nav_button("Pacman", "packages", "pacman"))
        layout.addWidget(aur_btn)
        layout.addWidget(self._page_button("Search Packages", "packages-search"))

        # System section
        layout.addWidget(self._section_label("System"))
        layout.addWidget(self._page_button("Updates", "updates"))
        layout.addWidget(self._page_button("Mirrors", "mirrors"))
        layout.addWidget(self._page_button("Find Orphans", "orphans"))
        layout.addWidget(self._page_button("Clear Cache", "cache"))
        layout.addWidget(self._page_button("Settings", "settings"))

        layout.addStretch()
        self._update_checked()

    def _counter_card(self, label: str, value_label: QLabel) -> QWidget:
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.addWidget(QLabel(label))
        lay.addWidget(value_label)
        return card

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: bold; font-size: 11px;")
        return lbl

    def _nav_button(self, text: str, page: str, pkg_filter: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFlat(True)
        btn.setCheckable(True)
        self._nav_buttons.append((btn, page, pkg_filter))

        def on_click():
            self._package_filter = pkg_filter
            self._view_model.setPackageFilter(pkg_filter)
            self._current_page = page
            self._on_page_requested(page)
            self._update_checked()

        btn.clicked.connect(on_click)
        return btn

    def _page_button(self, text: str, page: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFlat(True)
        btn.setCheckable(True)
        self._page_buttons.append((btn, page))

        def on_click():
            self._current_page = page
            self._on_page_requested(page)
            self._update_checked()

        btn.clicked.connect(on_click)
        return btn

    def _update_checked(self) -> None:
        for btn, page, pkg_filter in self._nav_buttons:
            btn.setChecked(
                self._current_page == page and self._package_filter == pkg_filter
            )
        for btn, page in self._page_buttons:
            btn.setChecked(self._current_page == page)

    def setCurrentPage(self, page: str) -> None:
        self._current_page = page
        self._update_checked()


class MainWindow(QMainWindow):
    """Main window: sidebar + stacked content area."""

    def __init__(self, view_model: AppViewModel, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._view_model = view_model
        self._current_page = "packages"
        self._stack: Optional[QStackedWidget] = None
        self._pages: dict[str, QWidget] = {}
        self.setWindowTitle("ArchHub")
        self.resize(1000, 700)
        self._build_ui()
        self._setup_shortcuts()
        self._view_model.refreshAll()
        self._view_model.setPackageFilter("all")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = SidebarWidget(
            self._view_model,
            self,
            on_page_requested=self.setCurrentPage,
        )
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: palette(base); border-right: 1px solid palette(mid);")
        layout.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._stack.setMinimumWidth(400)
        self._stack.setMinimumHeight(300)
        layout.addWidget(self._stack, 1)

        self._sidebar = sidebar

        from archhub.ui.pages import (
            CachePage,
            MirrorsPage,
            OrphansPage,
            PackagesPage,
            SettingsPage,
            UpdatesPage,
        )
        self._pages["packages"] = PackagesPage(self._view_model, self)
        self._pages["packages-search"] = self._pages["packages"]
        self._pages["updates"] = UpdatesPage(self._view_model, self)
        self._pages["mirrors"] = MirrorsPage(self._view_model, self)
        self._pages["orphans"] = OrphansPage(self._view_model, self)
        self._pages["cache"] = CachePage(self._view_model, self)
        self._pages["settings"] = SettingsPage(self._view_model, self)

        for name, widget in self._pages.items():
            if name == "packages-search":
                continue
            self._stack.addWidget(widget)

        self._stack.setCurrentWidget(self._pages["packages"])

    def setCurrentPage(self, page: str) -> None:
        if page == "packages-search":
            page = "packages"
            if hasattr(self._pages["packages"], "setShowSearchBar"):
                self._pages["packages"].setShowSearchBar(True)
        else:
            if hasattr(self._pages.get("packages"), "setShowSearchBar"):
                self._pages["packages"].setShowSearchBar(False)
        self._current_page = page
        if page in self._pages:
            self._stack.setCurrentWidget(self._pages[page])
        if self._sidebar:
            self._sidebar.setCurrentPage(page)

    def _setup_shortcuts(self) -> None:
        refresh = QAction(self)
        refresh.setShortcut(QKeySequence("F5"))
        refresh.triggered.connect(self._view_model.refreshInstalledCache)
        self.addAction(refresh)

    def closeEvent(self, event: QCloseEvent) -> None:
        thread = getattr(self._view_model, "_loader_thread", None)
        if thread is not None and thread.isRunning():
            thread.quit()
            thread.wait(2000)
        super().closeEvent(event)
