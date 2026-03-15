"""Package manager backends: pacman, paru, and registry."""

from typing import Dict, List, Optional

from archhub.backends.base import AurHelperBackend, PackageBackend
from archhub.backends.pacman import PacmanBackend
from archhub.backends.paru import ParuBackend
from archhub.core.runner import RunnerOptions


def _default_runner_options() -> RunnerOptions:
    return RunnerOptions(timeout_seconds=120.0)


def get_repo_backend() -> PackageBackend:
    """Return the repo (pacman) backend."""
    return PacmanBackend(runner_options=_default_runner_options())


def get_aur_backends() -> List[AurHelperBackend]:
    """Return all known AUR helper backends (availability checked at runtime)."""
    opts = _default_runner_options()
    return [
        ParuBackend(runner_options=opts),
        # Future: YayBackend(runner_options=opts), etc.
    ]


class BackendRegistry:
    """Holds repo backend and enabled AUR helpers for service use."""

    def __init__(
        self,
        repo_backend: Optional[PackageBackend] = None,
        enabled_helpers: Optional[Dict[str, bool]] = None,
    ):
        self._repo = repo_backend or get_repo_backend()
        self._aur_backends = get_aur_backends()
        # Helper id -> enabled (default True for available helpers)
        self._enabled = dict(enabled_helpers) if enabled_helpers else {}

    def repo(self) -> PackageBackend:
        return self._repo

    def aur_helpers(self) -> List[AurHelperBackend]:
        return self._aur_backends

    def get_enabled_aur_helper(self) -> Optional[AurHelperBackend]:
        """Return the first enabled and available AUR helper, or None."""
        for h in self._aur_backends:
            if self._enabled.get(h.id, True) and h.is_available():
                return h
        return None

    def set_helper_enabled(self, helper_id: str, enabled: bool) -> None:
        self._enabled[helper_id] = enabled

    def is_helper_enabled(self, helper_id: str) -> bool:
        return self._enabled.get(helper_id, True)
