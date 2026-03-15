"""High-level package listing, filtering, search, and details."""

from __future__ import annotations

from typing import List, Optional

from archhub.backends import BackendRegistry
from archhub.core.cache_repository import CacheRepository
from archhub.core.models import PackageDetails, PackageSummary, PackageSource


def _normalize_search_key(query: str) -> str:
    """Normalize query for cache key (strip, lower)."""
    return query.strip().lower() if query else ""


class PackageService:
    """Orchestrates package data from repo and AUR backends, with optional cache."""

    def __init__(self, registry: BackendRegistry, *, cache_repo: Optional[CacheRepository] = None):
        self._registry = registry
        self._cache = cache_repo

    def get_installed_all(self) -> List[PackageSummary]:
        """All installed packages (repo + AUR). Read-through cache when available."""
        repo = self._get_installed_repo_cached()
        aur_helper = self._registry.get_enabled_aur_helper()
        aur = self._get_installed_aur_cached() if aur_helper else []
        seen = {p.name for p in repo}
        for p in aur:
            if p.name not in seen:
                seen.add(p.name)
                repo.append(p)
        return repo

    def _get_installed_repo_cached(self) -> List[PackageSummary]:
        backend = self._registry.repo()
        if self._cache:
            cached = self._cache.get_installed(backend.id)
            if cached is not None:
                return cached
        out = backend.get_installed()
        if self._cache:
            self._cache.set_installed(backend.id, out)
        return out

    def _get_installed_aur_cached(self) -> List[PackageSummary]:
        aur_helper = self._registry.get_enabled_aur_helper()
        if not aur_helper:
            return []
        if self._cache:
            cached = self._cache.get_installed(aur_helper.id)
            if cached is not None:
                return cached
        out = aur_helper.get_aur_installed()
        if self._cache:
            self._cache.set_installed(aur_helper.id, out)
        return out

    def get_installed_repo(self) -> List[PackageSummary]:
        """Only repo-installed packages."""
        return self._get_installed_repo_cached()

    def get_installed_aur(self) -> List[PackageSummary]:
        """Only AUR-installed packages."""
        return self._get_installed_aur_cached()

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
        """Search repo and optionally AUR. Results cached 1 minute by query."""
        query_key = _normalize_search_key(query)
        if not query_key:
            return []
        results: List[PackageSummary] = []
        repo_backend = self._registry.repo()
        if self._cache:
            cached = self._cache.get_search(repo_backend.id, query_key)
            if cached is not None:
                results.extend(cached)
            else:
                repo_list = repo_backend.search_repo(query.strip())
                self._cache.set_search(repo_backend.id, query_key, repo_list)
                results.extend(repo_list)
        else:
            results.extend(repo_backend.search_repo(query.strip()))
        if include_aur:
            aur_helper = self._registry.get_enabled_aur_helper()
            if aur_helper:
                if self._cache:
                    cached_aur = self._cache.get_search(aur_helper.id, query_key)
                    if cached_aur is not None:
                        results.extend(cached_aur)
                    else:
                        aur_list = aur_helper.search_aur(query.strip())
                        self._cache.set_search(aur_helper.id, query_key, aur_list)
                        results.extend(aur_list)
                else:
                    results.extend(aur_helper.search_aur(query.strip()))
        return results

    def get_package_details(self, name: str) -> Optional[PackageDetails]:
        """Get details for a package (repo or AUR). Read-through cache when available."""
        repo = self._registry.repo()
        if self._cache:
            details = self._cache.get_package_details(repo.id, name)
            if details is not None:
                return details
        details = repo.get_package_details(name)
        if details and self._cache:
            self._cache.set_package_details(repo.id, details)
        if details:
            return details
        aur_helper = self._registry.get_enabled_aur_helper()
        if aur_helper:
            if self._cache:
                details = self._cache.get_package_details(aur_helper.id, name)
                if details is not None:
                    return details
            details = aur_helper.get_package_details(name)
            if details and self._cache:
                self._cache.set_package_details(aur_helper.id, details)
            return details
        return None

    def refresh_installed_cache(self) -> None:
        """Invalidate installed-package cache for all backends so next read refetches."""
        if not self._cache:
            return
        self._cache.invalidate_installed(self._registry.repo().id)
        aur = self._registry.get_enabled_aur_helper()
        if aur:
            self._cache.invalidate_installed(aur.id)
