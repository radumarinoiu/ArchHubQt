"""Tests for paru output parsers."""

import pytest
from archhub.core.models import PackageSource
from archhub.core.parsing import paru as paru_parsing


def test_parse_aur_installed_empty():
    assert paru_parsing.parse_aur_installed("") == []


def test_parse_aur_installed():
    out = "paru 1.0-1"
    r = paru_parsing.parse_aur_installed(out)
    assert len(r) == 1
    assert r[0].name == "paru"
    assert r[0].source == PackageSource.AUR


def test_parse_updates():
    out = "pacman 6.0.0-1 -> 6.1.0-1"
    r = paru_parsing.parse_updates(out)
    assert len(r) == 1
    assert r[0].name == "pacman"
    assert r[0].new_version == "6.1.0-1"


def test_parse_aur_search_only_aur():
    out = """aur/paru 1.0-1
    AUR helper
core/pacman 6.1.0-1
    Package manager
"""
    r = paru_parsing.parse_aur_search(out)
    assert len(r) == 1
    assert r[0].name == "paru"
    assert r[0].source == PackageSource.AUR


def test_parse_details_parses_pkgbuild():
    pkgbuild = """
# Maintainer: Someone <someone@archlinux.org>
pkgname=foo
pkgver=1.0
pkgrel=2
pkgdesc="AUR package"
depends=(bash glibc)
optdepends=('python: for scripts')
conflicts=(foo-legacy)
"""
    r = paru_parsing.parse_details(pkgbuild)
    assert r is not None
    assert r.name == "foo"
    assert r.version == "1.0-2"
    assert r.description == "AUR package"
    assert r.source == PackageSource.AUR
    assert r.dependencies == ["bash", "glibc"]
    assert r.optional_deps == ["python: for scripts"]
    assert r.conflicts == ["foo-legacy"]
