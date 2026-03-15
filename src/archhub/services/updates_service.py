"""Updates: pacman-only vs all, download size, Arch News placeholder."""

from __future__ import annotations

from typing import List, Optional

from archhub.backends import BackendRegistry
from archhub.core.cache_repository import CacheRepository
from archhub.core.models import UpdateEntry


class UpdatesService:
    """Orchestrates update listing and metadata, with optional cache."""

    def __init__(self, registry: BackendRegistry, *, cache_repo: Optional[CacheRepository] = None):
        self._registry = registry
        self._cache = cache_repo

    def get_repo_updates(self) -> List[UpdateEntry]:
        """Updates from sync repos only. Read-through cache when available."""
        backend = self._registry.repo()
        if self._cache:
            cached = self._cache.get_updates(backend.id)
            if cached is not None:
                return cached
        out = backend.get_repo_updates()
        if self._cache:
            self._cache.set_updates(backend.id, out)
        return out

    def get_all_updates(self) -> List[UpdateEntry]:
        """Repo + AUR updates if helper enabled. Read-through cache when available."""
        aur_helper = self._registry.get_enabled_aur_helper()
        if aur_helper:
            if self._cache:
                cached = self._cache.get_updates(aur_helper.id)
                if cached is not None:
                    return cached
            out = aur_helper.get_all_updates()
            if self._cache:
                self._cache.set_updates(aur_helper.id, out)
            return out
        return self.get_repo_updates()

    def get_updates(self, include_aur: bool) -> List[UpdateEntry]:
        if include_aur:
            return self.get_all_updates()
        return self.get_repo_updates()

    def total_download_size(self, updates: List[UpdateEntry]) -> int:
        """Sum of download_size on entries (may be 0 if not computed)."""
        return sum(u.download_size for u in updates)

    def total_install_size_delta(self, updates: List[UpdateEntry]) -> int:
        """Placeholder: would need pacman/paru to report size delta. Return 0."""
        return 0
