"""Abstract base classes for repo and AUR backends.

Define PackageBackend (pacman) and AurHelperBackend (paru, yay, etc.)
so adding a new helper is just implementing this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from archhub.core.models import (
    CacheStats,
    OrphanEntry,
    PackageDetails,
    PackageSummary,
    UpdateEntry,
)


class PackageBackend(ABC):
    """Abstract backend for repo/sync operations (pacman)."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Backend identifier, e.g. 'pacman'."""
        ...

    @abstractmethod
    def get_installed(self) -> List[PackageSummary]:
        """Return all installed packages from sync repos (no AUR)."""
        ...

    @abstractmethod
    def get_package_details(self, name: str) -> Optional[PackageDetails]:
        """Return full details for an installed package, or None."""
        ...

    @abstractmethod
    def get_repo_updates(self) -> List[UpdateEntry]:
        """Return list of repo packages that have updates available."""
        ...

    @abstractmethod
    def get_orphans(self) -> List[OrphanEntry]:
        """Return orphaned (unrequired) packages."""
        ...

    @abstractmethod
    def get_cache_stats(self) -> CacheStats:
        """Return cache directory statistics."""
        ...

    @abstractmethod
    def search_repo(self, query: str) -> List[PackageSummary]:
        """Search sync database; returns package summaries (for 'search packages' in repo)."""
        ...


class AurHelperBackend(ABC):
    """Abstract backend for AUR helper (paru, yay, etc.)."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Helper identifier, e.g. 'paru'."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the helper binary is installed and usable."""
        ...

    @abstractmethod
    def get_aur_installed(self) -> List[PackageSummary]:
        """Return installed packages that come from AUR."""
        ...

    @abstractmethod
    def get_all_updates(self) -> List[UpdateEntry]:
        """Return repo + AUR updates (e.g. paru -Qu)."""
        ...

    @abstractmethod
    def search_aur(self, query: str) -> List[PackageSummary]:
        """Search AUR; returns package summaries."""
        ...

    @abstractmethod
    def get_package_details(self, name: str) -> Optional[PackageDetails]:
        """Return full details for an AUR-installed package, or None."""
        ...
