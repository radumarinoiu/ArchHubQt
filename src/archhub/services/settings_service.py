"""Settings: enabled helpers, parallel downloads, config shortcuts."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from archhub.backends import BackendRegistry
from archhub.backends.base import AurHelperBackend


class SettingsService:
    """Helper enable/disable, parallel downloads, and path shortcuts."""

    PACMAN_CONF = Path("/etc/pacman.conf")
    MIRRORLIST = Path("/etc/pacman.d/mirrorlist")

    def __init__(self, registry: BackendRegistry):
        self._registry = registry

    def get_available_helpers(self) -> List[AurHelperBackend]:
        return self._registry.aur_helpers()

    def get_helper_enabled_map(self) -> Dict[str, bool]:
        return {
            h.id: self._registry.is_helper_enabled(h.id)
            for h in self._registry.aur_helpers()
        }

    def set_helper_enabled(self, helper_id: str, enabled: bool) -> None:
        self._registry.set_helper_enabled(helper_id, enabled)

    def get_pacman_conf_path(self) -> str:
        return str(self.PACMAN_CONF)

    def get_mirror_list_path(self) -> str:
        return str(self.MIRRORLIST)

    def get_parallel_downloads(self) -> int:
        """Placeholder: read from pacman.conf or default. Return default."""
        return 0  # 0 means use pacman default

    def set_parallel_downloads(self, value: int) -> None:
        """Placeholder: would write to config. No-op for now."""
        pass
