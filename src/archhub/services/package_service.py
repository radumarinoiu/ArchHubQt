"""High-level package listing, filtering, search, and details."""

from __future__ import annotations

from typing import List, Optional

from archhub.backends import BackendRegistry
from archhub.core.models import PackageDetails, PackageSummary, PackageSource


class PackageService:
    """Orchestrates package data from repo and AUR backends."""

    def __init__(self, registry: BackendRegistry):
        self._registry = registry

    def get_installed_all(self) -> List[PackageSummary]:
        """All installed packages (repo + AUR)."""
        repo = self._registry.repo().get_installed()
        aur_helper = self._registry.get_enabled_aur_helper()
        aur = aur_helper.get_aur_installed() if aur_helper else []
        # Merge: repo first, then AUR (no duplicates by name)
        seen = {p.name for p in repo}
        for p in aur:
            if p.name not in seen:
                seen.add(p.name)
                repo.append(p)
        return repo

    def get_installed_repo(self) -> List[PackageSummary]:
        """Only repo-installed packages."""
        return self._registry.repo().get_installed()

    def get_installed_aur(self) -> List[PackageSummary]:
        """Only AUR-installed packages."""
        aur_helper = self._registry.get_enabled_aur_helper()
        if not aur_helper:
            return []
        return aur_helper.get_aur_installed()

    def get_installed(
        self,
        filter_source: Optional[PackageSource] = None,
    ) -> List[PackageSummary]:
        """Get installed packages, optionally filtered by source."""
        if filter_source == PackageSource.AUR:
            return self.get_installed_aur()
        if filter_source == PackageSource.REPO:
            return self.get_installed_repo()
        return self.get_installed_all()

    def search(self, query: str, include_aur: bool = True) -> List[PackageSummary]:
        """Search repo and optionally AUR. For 'installed' search, filter in UI or here."""
        results: List[PackageSummary] = []
        results.extend(self._registry.repo().search_repo(query))
        if include_aur:
            aur_helper = self._registry.get_enabled_aur_helper()
            if aur_helper:
                results.extend(aur_helper.search_aur(query))
        return results

    def get_package_details(self, name: str) -> Optional[PackageDetails]:
        """Get details for a package (repo or AUR)."""
        details = self._registry.repo().get_package_details(name)
        if details:
            return details
        aur_helper = self._registry.get_enabled_aur_helper()
        if aur_helper:
            return aur_helper.get_package_details(name)
        return None
