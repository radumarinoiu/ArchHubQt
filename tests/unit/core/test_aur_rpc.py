"""Tests for AUR RPC client (get_package_info, parsing)."""

from unittest.mock import patch

import pytest

from archhub.core.models import PackageSource
from archhub.core.aur_rpc import (
    get_package_info,
    get_package_info_multi,
    _parse_info_result,
    AUR_RPC_BASE,
    AUR_RPC_VERSION,
)


def test_parse_info_result_minimal():
    data = {
        "Name": "foo",
        "Version": "1.0-1",
        "Description": "A package",
        "Maintainer": "someone",
        "Depends": ["bash", "glibc"],
        "OptDepends": ["python: for scripts"],
        "Conflicts": [],
    }
    r = _parse_info_result(data)
    assert r is not None
    assert r.name == "foo"
    assert r.version == "1.0-1"
    assert r.description == "A package"
    assert r.maintainer == "someone"
    assert r.source == PackageSource.AUR
    assert r.dependencies == ["bash", "glibc"]
    assert r.optional_deps == ["python: for scripts"]
    assert r.conflicts == []


def test_parse_info_result_uses_package_base_when_name_missing():
    data = {"PackageBase": "vlc-git", "Version": "4.0.0-1", "Description": "Player"}
    r = _parse_info_result(data)
    assert r is not None
    assert r.name == "vlc-git"


def test_parse_info_result_empty_returns_none():
    assert _parse_info_result({}) is None
    assert _parse_info_result({"Version": "1"}) is None


def test_parse_info_result_last_modified_to_iso():
    data = {
        "Name": "pkg",
        "Version": "1",
        "LastModified": 1770742736,
    }
    r = _parse_info_result(data)
    assert r is not None
    assert r.last_updated is not None
    assert "2026" in r.last_updated or "2025" in r.last_updated


@patch("archhub.core.aur_rpc._get")
def test_get_package_info_success(mock_get):
    mock_get.return_value = {
        "type": "multiinfo",
        "resultcount": 1,
        "results": [
            {
                "Name": "paru",
                "Version": "1.0-1",
                "Description": "AUR helper",
                "Maintainer": "morganamilo",
                "Depends": ["pacman"],
                "OptDepends": [],
                "Conflicts": [],
            }
        ],
    }
    r = get_package_info("paru")
    assert r is not None
    assert r.name == "paru"
    assert r.version == "1.0-1"
    assert r.description == "AUR helper"
    mock_get.assert_called_once()
    call_url = mock_get.call_args[0][0]
    assert AUR_RPC_BASE in call_url
    assert AUR_RPC_VERSION in call_url
    assert "paru" in call_url


@patch("archhub.core.aur_rpc._get")
def test_get_package_info_empty_results_returns_none(mock_get):
    mock_get.return_value = {"type": "multiinfo", "resultcount": 0, "results": []}
    assert get_package_info("nonexistent") is None


@patch("archhub.core.aur_rpc._get")
def test_get_package_info_rpc_error_returns_none(mock_get):
    mock_get.return_value = {"type": "error", "error": "Please specify an API version."}
    assert get_package_info("foo") is None


@patch("archhub.core.aur_rpc._get")
def test_get_package_info_multi_returns_list(mock_get):
    mock_get.return_value = {
        "type": "multiinfo",
        "resultcount": 2,
        "results": [
            {"Name": "a", "Version": "1", "Description": ""},
            {"Name": "b", "Version": "2", "Description": ""},
        ],
    }
    r = get_package_info_multi(["a", "b"])
    assert len(r) == 2
    assert r[0].name == "a" and r[1].name == "b"


def test_get_package_info_empty_name_returns_none():
    assert get_package_info("") is None
    assert get_package_info("   ") is None
