"""Parse paru (and compatible AUR helper) command output."""

from __future__ import annotations

from typing import List, Optional

from archhub.core.models import (
    PackageDetails,
    PackageSummary,
    PackageSource,
    UpdateEntry,
)

from archhub.core.parsing.pacman import LINE_RE
from archhub.core.parsing.pkgbuild import parse_pkgbuild


def parse_aur_installed(stdout: str) -> List[PackageSummary]:
    """Parse 'paru -Qm' (foreign packages) output: 'name version'."""
    result: List[PackageSummary] = []
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = LINE_RE.match(line)
        if m:
            result.append(
                PackageSummary(name=m.group(1), version=m.group(2), source=PackageSource.AUR)
            )
    return result


def parse_updates(stdout: str) -> List[UpdateEntry]:
    """Parse 'paru -Qu' output: 'name current -> new' (repo and AUR)."""
    result: List[UpdateEntry] = []
    arrow = " -> "
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if arrow in line:
            left, new_ver = line.split(arrow, 1)
            parts = left.split(None, 1)
            if len(parts) >= 2:
                # We cannot distinguish repo vs AUR from this line alone; treat as repo
                # unless we add --repo and run twice. For "all updates" we show both.
                result.append(
                    UpdateEntry(
                        name=parts[0],
                        current_version=parts[1].strip(),
                        new_version=new_ver.strip(),
                        source=PackageSource.REPO,
                    )
                )
    return result


def parse_aur_search(stdout: str) -> List[PackageSummary]:
    """Parse 'paru -Ss pattern' output. Only lines starting with 'aur/' are AUR packages."""
    result: List[PackageSummary] = []
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line or line.startswith(" "):
            continue
        parts = line.split(None, 1)
        if len(parts) >= 2:
            name_part = parts[0]
            version = parts[1]
            if name_part.startswith("aur/"):
                name = name_part.split("/", 1)[1]
                result.append(
                    PackageSummary(name=name, version=version, source=PackageSource.AUR)
                )
    return result


def parse_details(pkgbuild_content: str) -> Optional[PackageDetails]:
    """Parse PKGBUILD content (no execution/sourcing) into PackageDetails for AUR."""
    return parse_pkgbuild(pkgbuild_content, source=PackageSource.AUR)
