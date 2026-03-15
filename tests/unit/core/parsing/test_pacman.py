"""Tests for pacman output parsers."""

import pytest
from archhub.core.models import PackageSource
from archhub.core.parsing import pacman as pacman_parsing


def test_parse_installed_empty():
    assert pacman_parsing.parse_installed("") == []
    assert pacman_parsing.parse_installed("\n\n") == []


def test_parse_installed_single():
    out = "pacman 6.1.0-1"
    r = pacman_parsing.parse_installed(out)
    assert len(r) == 1
    assert r[0].name == "pacman"
    assert r[0].version == "6.1.0-1"
    assert r[0].source == PackageSource.REPO


def test_parse_installed_multiple():
    out = """glibc 2.39-1
linux 6.10.1-1
"""
    r = pacman_parsing.parse_installed(out)
    assert len(r) == 2
    assert r[0].name == "glibc"
    assert r[1].name == "linux"


def test_parse_updates_empty():
    assert pacman_parsing.parse_updates("") == []


def test_parse_updates():
    out = """pacman 6.0.0-1 -> 6.1.0-1
glibc 2.38-1 -> 2.39-1
"""
    r = pacman_parsing.parse_updates(out)
    assert len(r) == 2
    assert r[0].name == "pacman"
    assert r[0].current_version == "6.0.0-1"
    assert r[0].new_version == "6.1.0-1"
    assert r[1].name == "glibc"


def test_parse_orphans():
    out = "old-thing 1.0-1"
    r = pacman_parsing.parse_orphans(out)
    assert len(r) == 1
    assert r[0].name == "old-thing"
    assert r[0].version == "1.0-1"


def test_parse_search():
    out = """core/pacman 6.1.0-1
    Library-based package manager
extra/something 2.0-1
    Something else
"""
    r = pacman_parsing.parse_search(out)
    assert len(r) == 2
    assert r[0].name == "pacman"
    assert r[0].version == "6.1.0-1"
    assert r[1].name == "something"


def test_parse_details_empty():
    assert pacman_parsing.parse_details("") is None


def test_parse_details_minimal():
    out = """Name            : foo
Version         : 1.0-1
Description     : A package
Installed Size  : 1024
Depends On      : bar baz
Optional Deps   : opt: desc
Conflicts With  : conflict
"""
    r = pacman_parsing.parse_details(out)
    assert r is not None
    assert r.name == "foo"
    assert r.version == "1.0-1"
    assert r.description == "A package"
    assert r.install_size == 1024
    assert "bar" in r.dependencies
    assert "baz" in r.dependencies
    assert len(r.optional_deps) >= 1
    assert "conflict" in r.conflicts


def test_parse_cache_stats_empty():
    s = pacman_parsing.parse_cache_stats("")
    assert s.total_size_bytes == 0
    assert s.package_count == 0


def test_parse_cache_stats_numbers():
    s = pacman_parsing.parse_cache_stats("1234567890\n42")
    assert s.total_size_bytes == 1234567890
    assert s.package_count == 42
