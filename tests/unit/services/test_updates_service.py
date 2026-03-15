"""Tests for UpdatesService."""

from unittest.mock import MagicMock

import pytest
from archhub.core.models import UpdateEntry, PackageSource

from archhub.backends import BackendRegistry
from archhub.services.updates_service import UpdatesService


def _make_registry(repo_updates, all_updates=None):
    repo = MagicMock()
    repo.get_repo_updates.return_value = repo_updates
    registry = MagicMock(spec=BackendRegistry)
    registry.repo.return_value = repo
    if all_updates is None:
        all_updates = repo_updates
    aur = MagicMock()
    aur.get_all_updates.return_value = all_updates
    registry.get_enabled_aur_helper.return_value = aur
    return registry


def test_get_repo_updates():
    u = [UpdateEntry(name="a", current_version="1", new_version="2", source=PackageSource.REPO)]
    reg = _make_registry(u)
    svc = UpdatesService(reg)
    assert len(svc.get_repo_updates()) == 1
    assert svc.get_repo_updates()[0].name == "a"


def test_get_updates_include_aur():
    repo_u = [UpdateEntry(name="a", current_version="1", new_version="2", source=PackageSource.REPO)]
    all_u = repo_u + [UpdateEntry(name="b", current_version="1", new_version="2", source=PackageSource.AUR)]
    reg = _make_registry(repo_u, all_u)
    svc = UpdatesService(reg)
    assert len(svc.get_updates(include_aur=True)) == 2
    assert len(svc.get_updates(include_aur=False)) == 1


def test_total_download_size():
    u = [
        UpdateEntry(name="a", current_version="1", new_version="2", download_size=100),
        UpdateEntry(name="b", current_version="1", new_version="2", download_size=200),
    ]
    reg = _make_registry(u)
    svc = UpdatesService(reg)
    assert svc.total_download_size(u) == 300
