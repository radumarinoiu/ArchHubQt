"""Tests for domain models."""

import pytest
from archhub.core.models import (
    PackageSummary,
    PackageSource,
    PackageDetails,
    UpdateEntry,
    OrphanEntry,
    CacheStats,
    RunResult,
    OperationStatus,
)


def test_package_summary_source_default():
    p = PackageSummary(name="x", version="1.0")
    assert p.source == PackageSource.REPO


def test_run_result_success():
    r = RunResult(exit_code=0, stdout="ok", stderr="")
    assert r.success
    assert not r.timeout


def test_run_result_failure():
    r = RunResult(exit_code=1, stdout="", stderr="error")
    assert not r.success


def test_run_result_to_operation_status():
    r = RunResult(exit_code=0, stdout="done", stderr="")
    s = r.to_operation_status("OK")
    assert s.success
    assert s.exit_code == 0
