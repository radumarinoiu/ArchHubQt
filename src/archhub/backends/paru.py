"""Paru AUR helper backend."""

from __future__ import annotations

import shutil
from typing import List, Optional

from archhub.backends.base import AurHelperBackend
from archhub.core.aur_rpc import get_package_info
from archhub.core.models import (
    CacheStats,
    PackageDetails,
    PackageSummary,
    UpdateEntry,
)
from archhub.core.parsing import paru as paru_parsing
from archhub.core.runner import run, RunnerOptions
from tools.performance_tools import log_duration


class ParuBackend(AurHelperBackend):
    """AUR backend using paru."""

    BINARY = "paru"

    def __init__(self, runner_options: Optional[RunnerOptions] = None):
        self._opts = runner_options or RunnerOptions()

    @property
    def id(self) -> str:
        return "paru"

    @log_duration()
    def get_installed(self) -> List[PackageSummary]:
        r = run([self.BINARY, "-Qma"], options=self._opts)
        if not r.success:
            return []
        return paru_parsing.parse_aur_installed(r.stdout)

    @log_duration()
    def get_updates(self) -> List[UpdateEntry]:
        r = run([self.BINARY, "-Qua"], options=self._opts)
        if not r.success:
            return []
        return paru_parsing.parse_updates(r.stdout)

    # @log_duration()
    # def get_cache_stats(self) -> CacheStats:
    #     r = run([self.BINARY, "-Sc"], options=self._opts)
    #     if not r.success:
    #         return CacheStats()
    #     return paru_parsing.parse_cache_stats(r.stdout)

    @log_duration()
    def search(self, query: str) -> List[PackageSummary]:
        r = run([self.BINARY, "-Ssa", query.strip()], options=self._opts)
        if not r.success:
            print(r.stderr)
            return []
        return paru_parsing.parse_aur_search(r.stdout)

    @log_duration()
    def is_available(self) -> bool:
        return shutil.which(self.BINARY) is not None

    @log_duration()
    def get_package_comments(self, name: str) -> List[str]:
        r = run([self.BINARY, "-Qca", name], options=self._opts)
        if not r.success:
            return []
        return r.stdout.splitlines()  # TODO: Needs regex parsing to separate comments