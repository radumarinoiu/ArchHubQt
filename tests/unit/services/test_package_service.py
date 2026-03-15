"""Tests for PackageService."""

from unittest.mock import MagicMock

import pytest
from archhub.core.models import PackageSummary, PackageSource, PackageDetails

from archhub.backends import BackendRegistry
from archhub.services.package_service import PackageService


def _make_registry(repo_packages, aur_packages=None, aur_available=True):
    repo = MagicMock()
    repo.get_installed.return_value = repo_packages
    repo.get_package_details.return_value = None
    repo.search_repo.return_value = []

    registry = MagicMock(spec=BackendRegistry)
    registry.repo.return_value = repo
    if aur_packages is None:
        aur_packages = []
    aur = MagicMock()
    aur.get_aur_installed.return_value = aur_packages
    aur.get_package_details.return_value = None
    aur.search_aur.return_value = []
    aur.is_available.return_value = aur_available
    aur.id = "paru"
    registry.get_enabled_aur_helper.return_value = aur if aur_available else None
    registry.aur_helpers.return_value = [aur]
    registry.is_helper_enabled.return_value = True
    return registry


def test_get_installed_all_merged():
    repo = [
        PackageSummary(name="a", version="1", source=PackageSource.REPO),
        PackageSummary(name="b", version="2", source=PackageSource.REPO),
    ]
    aur = [PackageSummary(name="c", version="3", source=PackageSource.AUR)]
    reg = _make_registry(repo, aur)
    svc = PackageService(reg)
    all_pkgs = svc.get_installed_all()
    assert len(all_pkgs) == 3
    names = [p.name for p in all_pkgs]
    assert "a" in names and "b" in names and "c" in names


def test_get_installed_repo_only():
    repo = [PackageSummary(name="a", version="1", source=PackageSource.REPO)]
    reg = _make_registry(repo, [])
    svc = PackageService(reg)
    assert len(svc.get_installed_repo()) == 1
    assert svc.get_installed_repo()[0].name == "a"


def test_get_installed_aur_only():
    reg = _make_registry([], [PackageSummary(name="x", version="1", source=PackageSource.AUR)])
    svc = PackageService(reg)
    assert len(svc.get_installed_aur()) == 1
    assert svc.get_installed_aur()[0].name == "x"


def test_get_installed_filter_source():
    repo = [PackageSummary(name="a", version="1", source=PackageSource.REPO)]
    aur = [PackageSummary(name="b", version="2", source=PackageSource.AUR)]
    reg = _make_registry(repo, aur)
    svc = PackageService(reg)
    assert len(svc.get_installed(filter_source=PackageSource.REPO)) == 1
    assert len(svc.get_installed(filter_source=PackageSource.AUR)) == 1
    assert len(svc.get_installed(filter_source=None)) == 2
