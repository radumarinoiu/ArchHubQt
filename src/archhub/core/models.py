"""Pydantic models for Package, Repo, OperationResult, and related domain models."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PackageSource(str, Enum):
    """Origin of a package: repo (sync db) or AUR."""

    REPO = "repo"
    AUR = "aur"


class PackageSummary(BaseModel):
    """Minimal package info for list views."""

    model_config = ConfigDict(frozen=True)

    name: str
    version: str
    source: PackageSource = PackageSource.REPO


class PackageDetails(BaseModel):
    """Full package metadata for details view."""

    name: str
    version: str
    source: PackageSource
    description: str = ""
    install_size: int = 0  # bytes
    last_updated: Optional[str] = None
    maintainer: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)
    optional_deps: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)


class UpdateEntry(BaseModel):
    """One upgradable package."""

    name: str
    current_version: str
    new_version: str
    source: PackageSource = PackageSource.REPO
    download_size: int = 0  # bytes, 0 if unknown


class OrphanEntry(BaseModel):
    """Orphaned (unrequired) package."""

    name: str
    version: str


class CacheStats(BaseModel):
    """Cache directory statistics."""

    total_size_bytes: int = 0
    package_count: int = 0
    old_versions_count: int = 0
    old_versions_size_bytes: int = 0
    uninstalled_count: int = 0
    uninstalled_size_bytes: int = 0


class HelperSettings(BaseModel):
    """Per-helper configuration (e.g. enabled, parallel downloads)."""

    helper_id: str  # e.g. "paru"
    enabled: bool = True
    parallel_downloads: Optional[int] = None  # None = use default


class OperationStatus(BaseModel):
    """Result of a run: success/failure and optional message."""

    success: bool
    message: str = ""
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""

    @property
    def failed(self) -> bool:
        return not self.success


class RunResult(BaseModel):
    """Structured result from the command runner."""

    exit_code: int
    stdout: str
    stderr: str
    timeout: bool = False

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timeout

    def to_operation_status(self, default_message: str = "") -> OperationStatus:
        return OperationStatus(
            success=self.success,
            message=default_message or (self.stderr or self.stdout) if not self.success else "",
            exit_code=self.exit_code,
            stdout=self.stdout,
            stderr=self.stderr,
        )
