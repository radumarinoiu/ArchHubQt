"""Updates: pacman-only vs all, download size, Arch News placeholder."""

from __future__ import annotations

from typing import List

from archhub.backends import BackendRegistry
from archhub.core.models import UpdateEntry


class UpdatesService:
    """Orchestrates update listing and metadata."""

    def __init__(self, registry: BackendRegistry):
        self._registry = registry

    def get_repo_updates(self) -> List[UpdateEntry]:
        """Updates from sync repos only."""
        return self._registry.repo().get_repo_updates()

    def get_all_updates(self) -> List[UpdateEntry]:
        """Repo + AUR updates if helper enabled."""
        aur_helper = self._registry.get_enabled_aur_helper()
        if aur_helper:
            return aur_helper.get_all_updates()
        return self._registry.repo().get_repo_updates()

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
