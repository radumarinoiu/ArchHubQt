"""Pacman backend: repo packages, updates, orphans, cache, search."""

from __future__ import annotations

from typing import List, Optional

from archhub.backends.base import PackageBackend
from archhub.core.models import (
    CacheStats,
    OrphanEntry,
    PackageDetails,
    PackageSummary,
    UpdateEntry,
)
from archhub.core.parsing import pacman as pacman_parsing
from archhub.core.runner import run, RunnerOptions
from tools.performance_tools import log_duration


class PacmanBackend(PackageBackend):
    """Backend using pacman for repo operations."""

    def __init__(self, runner_options: Optional[RunnerOptions] = None):
        self._opts = runner_options or RunnerOptions()

    @property
    def id(self) -> str:
        return "pacman"

    @log_duration()
    def get_installed(self) -> List[PackageSummary]:
        r = run(["pacman", "-Qn"], options=self._opts)
        if not r.success:
            return []
        return pacman_parsing.parse_installed(r.stdout)

    @log_duration()
    def get_package_details(self, name: str) -> Optional[PackageDetails]:
        r = run(["pacman", "-Qi", name], options=self._opts)
        if not r.success:
            return None
        return pacman_parsing.parse_details(r.stdout)

    @log_duration()
    def get_repo_updates(self) -> List[UpdateEntry]:
        r = run(["pacman", "-Qu"], options=self._opts)
        if not r.success:
            return []
        return pacman_parsing.parse_updates(r.stdout)

    @log_duration()
    def get_orphans(self) -> List[OrphanEntry]:
        r = run(["pacman", "-Qdt"], options=self._opts)
        if not r.success:
            return []
        return pacman_parsing.parse_orphans(r.stdout)

    @log_duration()
    def get_cache_stats(self) -> CacheStats:
        # Use paccache from pacman-contrib if available; else fallback
        r = run(["paccache", "-s"], options=self._opts)
        if r.success and r.stdout.strip():
            return pacman_parsing.parse_cache_stats(r.stdout)
        # Fallback: count files and size under /var/cache/pacman/pkg
        r2 = run(
            ["sh", "-c", "du -sb /var/cache/pacman/pkg 2>/dev/null | cut -f1"],
            options=self._opts,
        )
        r3 = run(
            ["sh", "-c", "find /var/cache/pacman/pkg -maxdepth 1 -name '*.pkg.tar*' 2>/dev/null | wc -l"],
            options=self._opts,
        )
        size = 0
        count = 0
        if r2.success and r2.stdout.strip():
            try:
                size = int(r2.stdout.strip().split()[0])
            except (ValueError, IndexError):
                pass
        if r3.success and r3.stdout.strip():
            try:
                count = int(r3.stdout.strip())
            except ValueError:
                pass
        return CacheStats(total_size_bytes=size, package_count=count)

    @log_duration()
    def search_repo(self, query: str) -> List[PackageSummary]:
        if not query.strip():
            return []
        r = run(["pacman", "-Ss", query.strip()], options=self._opts)
        if not r.success:
            return []
        return pacman_parsing.parse_search(r.stdout)
