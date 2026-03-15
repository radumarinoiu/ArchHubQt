"""Unit tests for cache repository: hit/miss, refresh, serialization."""

from __future__ import annotations

import pytest
from sqlmodel import create_engine

from archhub.core.cache_db import cache_session, init_cache_tables
from archhub.core.cache_repository import CacheRepository
from archhub.core.models import PackageDetails, PackageSource, PackageSummary, UpdateEntry


def _make_repo():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    init_cache_tables(engine)

    def session_factory():
        return cache_session(engine)

    return CacheRepository(session_factory)


def test_get_installed_miss():
    repo = _make_repo()
    assert repo.get_installed("pacman") is None
    assert repo.get_installed("paru") is None


def test_set_installed_then_get():
    repo = _make_repo()
    packages = [
        PackageSummary(name="a", version="1.0", source=PackageSource.REPO),
        PackageSummary(name="b", version="2.0", source=PackageSource.AUR),
    ]
    repo.set_installed("pacman", packages)
    out = repo.get_installed("pacman")
    assert out is not None
    assert len(out) == 2
    assert out[0].name == "a" and out[0].version == "1.0" and out[0].source == PackageSource.REPO
    assert out[1].name == "b" and out[1].version == "2.0" and out[1].source == PackageSource.AUR


def test_invalidate_installed_then_get_miss():
    repo = _make_repo()
    packages = [PackageSummary(name="x", version="1", source=PackageSource.REPO)]
    repo.set_installed("pacman", packages)
    assert repo.get_installed("pacman") is not None
    repo.invalidate_installed("pacman")
    assert repo.get_installed("pacman") is None


def test_get_search_miss():
    repo = _make_repo()
    assert repo.get_search("pacman", "foo") is None


def test_set_search_then_get_hit():
    repo = _make_repo()
    packages = [PackageSummary(name="pkg", version="1", source=PackageSource.REPO)]
    repo.set_search("pacman", "foo", packages, ttl_seconds=60)
    out = repo.get_search("pacman", "foo")
    assert out is not None
    assert len(out) == 1
    assert out[0].name == "pkg"


def test_search_expired_returns_none():
    repo = _make_repo()
    packages = [PackageSummary(name="pkg", version="1", source=PackageSource.REPO)]
    repo.set_search("pacman", "q", packages, ttl_seconds=-1)
    assert repo.get_search("pacman", "q") is None


def test_get_package_details_miss():
    repo = _make_repo()
    assert repo.get_package_details("pacman", "linux") is None


def test_set_package_details_then_get_roundtrip():
    repo = _make_repo()
    details = PackageDetails(
        name="linux",
        version="6.0",
        source=PackageSource.REPO,
        description="Kernel",
        install_size=100,
        dependencies=["a", "b"],
        optional_deps=["c"],
        conflicts=["old-kernel"],
    )
    repo.set_package_details("pacman", details)
    out = repo.get_package_details("pacman", "linux")
    assert out is not None
    assert out.name == "linux"
    assert out.version == "6.0"
    assert out.dependencies == ["a", "b"]
    assert out.optional_deps == ["c"]
    assert out.conflicts == ["old-kernel"]


def test_invalidate_package_details_then_miss():
    repo = _make_repo()
    details = PackageDetails(name="x", version="1", source=PackageSource.REPO)
    repo.set_package_details("pacman", details)
    assert repo.get_package_details("pacman", "x") is not None
    repo.invalidate_package_details("pacman", "x")
    assert repo.get_package_details("pacman", "x") is None


def test_installed_isolated_by_backend():
    repo = _make_repo()
    repo.set_installed("pacman", [PackageSummary(name="a", version="1", source=PackageSource.REPO)])
    repo.set_installed("paru", [PackageSummary(name="b", version="2", source=PackageSource.AUR)])
    pacman = repo.get_installed("pacman")
    paru = repo.get_installed("paru")
    assert pacman is not None and len(pacman) == 1 and pacman[0].name == "a"
    assert paru is not None and len(paru) == 1 and paru[0].name == "b"


def test_get_updates_miss():
    repo = _make_repo()
    assert repo.get_updates("pacman") is None
    assert repo.get_updates("paru") is None


def test_set_updates_then_get():
    repo = _make_repo()
    entries = [
        UpdateEntry(name="a", current_version="1", new_version="2", source=PackageSource.REPO),
        UpdateEntry(name="b", current_version="1", new_version="3", source=PackageSource.AUR, download_size=100),
    ]
    repo.set_updates("pacman", entries)
    out = repo.get_updates("pacman")
    assert out is not None
    assert len(out) == 2
    assert out[0].name == "a" and out[0].new_version == "2"
    assert out[1].name == "b" and out[1].download_size == 100


def test_invalidate_updates_then_miss():
    repo = _make_repo()
    entries = [UpdateEntry(name="x", current_version="1", new_version="2", source=PackageSource.REPO)]
    repo.set_updates("pacman", entries)
    assert repo.get_updates("pacman") is not None
    repo.invalidate_updates("pacman")
    assert repo.get_updates("pacman") is None
