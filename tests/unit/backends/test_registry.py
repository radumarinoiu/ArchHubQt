"""Tests for backend registry."""

import pytest
from archhub.backends import BackendRegistry, get_repo_backend, get_aur_backends


def test_get_repo_backend():
    b = get_repo_backend()
    assert b.id == "pacman"


def test_get_aur_backends_non_empty():
    backends = get_aur_backends()
    assert len(backends) >= 1
    ids = [b.id for b in backends]
    assert "paru" in ids


def test_registry_repo():
    r = BackendRegistry()
    assert r.repo().id == "pacman"


def test_registry_helpers():
    r = BackendRegistry()
    helpers = r.aur_helpers()
    assert isinstance(helpers, list)


def test_registry_set_helper_enabled():
    r = BackendRegistry()
    r.set_helper_enabled("paru", False)
    assert r.is_helper_enabled("paru") is False
    r.set_helper_enabled("paru", True)
    assert r.is_helper_enabled("paru") is True
