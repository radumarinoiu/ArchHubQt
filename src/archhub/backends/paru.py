"""Paru AUR helper backend."""

from __future__ import annotations

import shutil
from typing import List, Optional

from archhub.backends.base import AurHelperBackend
from archhub.core.models import (
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
    def is_available(self) -> bool:
        return shutil.which(self.BINARY) is not None

    @log_duration()
    def get_aur_installed(self) -> List[PackageSummary]:
        if not self.is_available():
            return []
        r = run([self.BINARY, "-Qm"], options=self._opts)
        if not r.success:
            return []
        return paru_parsing.parse_aur_installed(r.stdout)

    @log_duration()
    def get_all_updates(self) -> List[UpdateEntry]:
        if not self.is_available():
            return []
        r = run([self.BINARY, "-Qu"], options=self._opts)
        if not r.success:
            return []
        return paru_parsing.parse_updates(r.stdout)

    @log_duration()
    def search_aur(self, query: str) -> List[PackageSummary]:
        if not self.is_available() or not query.strip():
            return []
        r = run([self.BINARY, "-Ss", query.strip()], options=self._opts)
        if not r.success:
            return []
        return paru_parsing.parse_aur_search(r.stdout)

    @log_duration()
    def get_package_details(self, name: str) -> Optional[PackageDetails]:
        if not self.is_available():
            return None
        r = run([self.BINARY, "-Qi", name], options=self._opts)
        if not r.success:
            return None
        return paru_parsing.parse_details(r.stdout)
