"""Tests for the command runner."""

import pytest
from archhub.core.runner import run, RunnerOptions


def test_run_echo():
    r = run(["echo", "hello"], options=RunnerOptions(timeout_seconds=5.0))
    assert r.success
    assert "hello" in r.stdout
    assert r.exit_code == 0
    assert r.timeout is False


def test_run_false_exit_code():
    r = run(["false"], options=RunnerOptions(timeout_seconds=5.0))
    assert not r.success
    assert r.exit_code != 0


def test_run_nonexistent():
    r = run(["nonexistent_binary_xyz_123"])
    assert not r.success
    assert r.exit_code == -1
    assert len(r.stderr) > 0
