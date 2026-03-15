"""Tests for UiLoader: async task dispatch and result/error signals."""

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QCoreApplication

from archhub.core.models import (
    CacheStats,
    OrphanEntry,
    PackageDetails,
    PackageSource,
    PackageSummary,
    UpdateEntry,
)
from archhub.app.ui_loader import UiLoader


@pytest.fixture
def app():
    """Ensure Qt app exists for QObject/signals."""
    return QCoreApplication.instance() or QCoreApplication([])


@pytest.fixture
def mock_services():
    pkg = MagicMock()
    updates = MagicMock()
    maint = MagicMock()
    return pkg, updates, maint


def test_load_installed_emits_installed_ready(app, mock_services):
    pkg, updates, maint = mock_services
    packages = [
        PackageSummary(name="a", version="1", source=PackageSource.REPO),
        PackageSummary(name="b", version="2", source=PackageSource.AUR),
    ]
    pkg.get_installed.return_value = packages

    loader = UiLoader(pkg, updates, maint)
    received = []

    def capture(lst):
        received.append(lst)

    loader.installedReady.connect(capture)
    loader.load_installed("all")

    assert len(received) == 1
    assert len(received[0]) == 2
    assert received[0][0].name == "a" and received[0][1].name == "b"


def test_load_installed_on_error_emits_load_error(app, mock_services):
    pkg, updates, maint = mock_services
    pkg.get_installed.side_effect = RuntimeError("pacman failed")

    loader = UiLoader(pkg, updates, maint)
    errors = []

    loader.loadError.connect(errors.append)
    loader.load_installed("all")

    assert len(errors) == 1
    assert "pacman failed" in errors[0]


def test_load_search_emits_search_ready(app, mock_services):
    pkg, updates, maint = mock_services
    packages = [PackageSummary(name="foo", version="1", source=PackageSource.REPO)]
    pkg.search.return_value = packages

    loader = UiLoader(pkg, updates, maint)
    received = []

    loader.searchReady.connect(received.append)
    loader.load_search("foo", False)

    assert len(received) == 1
    assert received[0][0].name == "foo"


def test_load_details_emits_details_ready(app, mock_services):
    pkg, updates, maint = mock_services
    details = PackageDetails(
        name="pkg",
        version="1",
        source=PackageSource.REPO,
        description="desc",
        install_size=100,
        dependencies=[],
        optional_deps=[],
        conflicts=[],
    )
    pkg.get_package_details.return_value = details

    loader = UiLoader(pkg, updates, maint)
    received = []

    loader.detailsReady.connect(received.append)
    loader.load_details("pkg")

    assert len(received) == 1
    assert received[0].name == "pkg" and received[0].version == "1"


def test_load_updates_emits_updates_ready(app, mock_services):
    pkg, updates, maint = mock_services
    upd = [UpdateEntry(name="u", current_version="1", new_version="2", source=PackageSource.REPO)]
    updates.get_updates.return_value = upd

    loader = UiLoader(pkg, updates, maint)
    received = []

    loader.updatesReady.connect(received.append)
    loader.load_updates(False)

    assert len(received) == 1
    assert received[0][0].name == "u"


def test_load_orphans_emits_orphans_ready(app, mock_services):
    pkg, updates, maint = mock_services
    orphans = [OrphanEntry(name="o", version="1")]
    maint.get_orphans.return_value = orphans

    loader = UiLoader(pkg, updates, maint)
    received = []

    loader.orphansReady.connect(received.append)
    loader.load_orphans()

    assert len(received) == 1
    assert received[0][0].name == "o"


def test_load_counts_emits_counts_ready(app, mock_services):
    pkg, updates, maint = mock_services
    pkg.get_installed_all.return_value = [object()] * 10
    pkg.get_installed_aur.return_value = [object()] * 3
    updates.get_all_updates.return_value = [object()] * 2

    loader = UiLoader(pkg, updates, maint)
    received = []

    def capture(t, a, u):
        received.append((t, a, u))

    loader.countsReady.connect(capture)
    loader.load_counts()

    assert len(received) == 1
    assert received[0] == (10, 3, 2)


def test_load_cache_stats_emits_cache_stats_ready(app, mock_services):
    pkg, updates, maint = mock_services
    stats = CacheStats(package_count=5, total_size_bytes=100 * 1024 * 1024)
    maint.get_cache_stats.return_value = stats

    loader = UiLoader(pkg, updates, maint)
    received = []

    loader.cacheStatsReady.connect(received.append)
    loader.load_cache_stats()

    assert len(received) == 1
    assert received[0].package_count == 5
    assert received[0].total_size_bytes == 100 * 1024 * 1024
