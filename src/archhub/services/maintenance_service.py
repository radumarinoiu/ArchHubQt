"""Orphans and cache stats."""

from __future__ import annotations

from archhub.backends import BackendRegistry
from archhub.core.models import CacheStats, OrphanEntry


class MaintenanceService:
    """Orphan discovery and cache statistics."""

    def __init__(self, registry: BackendRegistry):
        self._registry = registry

    def get_orphans(self) -> list[OrphanEntry]:
        return self._registry.repo().get_orphans()

    def get_cache_stats(self) -> CacheStats:
        return self._registry.repo().get_cache_stats()
