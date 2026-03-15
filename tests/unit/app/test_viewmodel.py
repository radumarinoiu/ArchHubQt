"""Tests for AppViewModel: result handlers, error propagation, and back-navigation state."""

from unittest.mock import MagicMock

import pytest
from pytestqt.qtbot import QtBot

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from archhub.backends import BackendRegistry
from sqlmodel import create_engine

from archhub.core.cache_repository import CacheRepository
from archhub.core.cache_db import init_cache_tables, cache_session
from archhub.core.models import (
    CacheStats,
    PackageDetails,
    PackageSource,
    PackageSummary,
)
from archhub.app.viewmodel import AppViewModel


def _make_registry():
    repo = MagicMock()
    repo.get_installed.return_value = []
    repo.get_package_details.return_value = None
    repo.search_repo.return_value = []
    registry = MagicMock(spec=BackendRegistry)
    registry.repo.return_value = repo
    aur = MagicMock()
    aur.get_aur_installed.return_value = []
    aur.get_package_details.return_value = None
    aur.search_aur.return_value = []
    aur.is_available.return_value = False
    aur.id = "paru"
    registry.get_enabled_aur_helper.return_value = None
    registry.aur_helpers.return_value = [aur]
    registry.is_helper_enabled.return_value = False
    return registry


def _make_cache_repo():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    init_cache_tables(engine)
    def session_factory():
        return cache_session(engine)
    return CacheRepository(session_factory)


@pytest.fixture
def view_model(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    registry = _make_registry()
    cache_repo = _make_cache_repo()
    vm = AppViewModel(registry, cache_repo=cache_repo)
    yield vm
    if vm._loader_thread.isRunning():
        vm._loader_thread.quit()
        vm._loader_thread.wait(2000)


def test_on_installed_ready_updates_package_model_and_clears_loading(view_model):
    view_model.setLoading(True)
    packages = [
        PackageSummary(name="a", version="1", source=PackageSource.REPO),
        PackageSummary(name="b", version="2", source=PackageSource.AUR),
    ]
    view_model._on_installed_ready(packages)
    assert view_model.packageModel.rowCount() == 2
    assert view_model.loading is False


def test_on_search_ready_updates_package_model_and_clears_loading(view_model):
    view_model.setLoading(True)
    packages = [PackageSummary(name="foo", version="1", source=PackageSource.REPO)]
    view_model._on_search_ready(packages)
    assert view_model.packageModel.rowCount() == 1
    assert view_model.loading is False


def test_on_details_ready_updates_details_and_deps_models(view_model):
    details = PackageDetails(
        name="pkg",
        version="1",
        source=PackageSource.REPO,
        description="desc",
        install_size=100,
        dependencies=["dep1", "dep2"],
        optional_deps=["opt1"],
        conflicts=[],
    )
    view_model._on_details_ready(details)
    assert view_model.packageDetailsName == "pkg"
    assert view_model.packageDetailsVersion == "1"
    assert view_model.getDepsModel().rowCount() == 2
    assert view_model.getOptionalDepsModel().rowCount() == 1


def test_on_load_error_sets_message_and_clears_loading(view_model):
    view_model.setLoading(True)
    view_model._on_load_error("Something failed")
    assert view_model.errorMessage == "Something failed"
    assert view_model.loading is False
    assert view_model.packageModel.rowCount() == 0


def test_on_cache_stats_ready_updates_cache_stats(view_model):
    stats = CacheStats(package_count=10, total_size_bytes=1024 * 1024)
    view_model._on_cache_stats_ready(stats)
    assert view_model.getCacheStatsCount() == 10
    assert view_model.getCacheStatsSize() == 1024 * 1024


def test_navigate_to_package_pushes_stack_and_sets_can_go_back(view_model):
    view_model.setSelectedPackageName("pkg-a")
    assert view_model.canGoBack is False
    view_model.navigateToPackage("pkg-b")
    assert view_model.selectedPackageName == "pkg-b"
    assert view_model.canGoBack is True


def test_go_back_restores_previous_selection(view_model):
    view_model.setSelectedPackageName("pkg-a")
    view_model.navigateToPackage("pkg-b")
    view_model.goBack()
    assert view_model.selectedPackageName == "pkg-a"
    assert view_model.canGoBack is False


def test_go_back_no_op_when_stack_empty(view_model):
    view_model.setSelectedPackageName("pkg-a")
    assert view_model.canGoBack is False
    view_model.goBack()
    assert view_model.selectedPackageName == "pkg-a"
