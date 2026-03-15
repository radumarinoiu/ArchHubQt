"""Abstract base classes for repo and AUR backends.

Define PackageBackend (pacman) and AurHelperBackend (paru, yay, etc.)
so adding a new helper is just implementing this interface.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, Optional

from archhub.core.aur_rpc import get_package_info
from archhub.core.models import (
    CacheStats,
    OrphanEntry,
    PackageDetails,
    PackageSummary,
    UpdateEntry,
)
from tools.performance_tools import log_duration


class PackageBackend(metaclass=ABCMeta):
    """Abstract backend for package manager operations. (Common for repo and AUR helpers.)"""

    @property
    @abstractmethod
    def id(self) -> str:
        """Backend identifier, e.g. 'pacman' or 'paru'."""
        ...

    @abstractmethod
    def get_installed(self) -> List[PackageSummary]:
        """Return all installed packages."""
        ...

    @abstractmethod
    def get_package_details(self, name: str) -> Optional[PackageDetails]:
        """Return full details for an installed package, or None."""
        ...

    @abstractmethod
    def get_updates(self) -> List[UpdateEntry]:
        """Return list of packages that have updates available."""
        ...

    # TODO: Implement this later as it's a bit more complex to implement
    # @abstractmethod
    # def get_cache_stats(self) -> CacheStats:
    #     """Return cache directory statistics."""
    #     ...

    @abstractmethod
    def search(self, query: str) -> List[PackageSummary]:
        """Search database; returns package summaries."""
        ...


class RepoBackend(PackageBackend, metaclass=ABCMeta):
    """Abstract backend for repo/sync operations (pacman)."""

    @abstractmethod
    def get_orphans(self) -> List[OrphanEntry]:
        """Return orphaned (unrequired) packages."""
        ...


class AurHelperBackend(PackageBackend, metaclass=ABCMeta):
    """Abstract backend for AUR helper (paru, yay, etc.)."""

    @log_duration()
    def get_package_details(self, name: str) -> Optional[PackageDetails]:
        return get_package_info(name)

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the helper binary is installed and usable."""
        ...
    
    @abstractmethod
    def get_package_comments(self, name: str) -> List[str]:
        """Return comments for a package."""
        ...
