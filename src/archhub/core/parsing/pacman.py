"""Parse pacman command output into domain models."""

from __future__ import annotations

import re
from typing import List, Optional

from archhub.core.models import (
    CacheStats,
    OrphanEntry,
    PackageDetails,
    PackageSummary,
    PackageSource,
    UpdateEntry,
)


# pacman -Q: "name version" per line
LINE_RE = re.compile(r"^(\S+)\s+(\S+)\s*$")


def parse_installed(stdout: str) -> List[PackageSummary]:
    """Parse 'pacman -Q' / 'pacman -Qn' output. Returns repo packages."""
    result: List[PackageSummary] = []
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = LINE_RE.match(line)
        if m:
            result.append(
                PackageSummary(name=m.group(1), version=m.group(2), source=PackageSource.REPO)
            )
    return result


def parse_updates(stdout: str) -> List[UpdateEntry]:
    """Parse 'pacman -Qu' output: 'name current-version -> new-version'."""
    result: List[UpdateEntry] = []
    # Format: "package 1.0-1 -> 1.1-1"
    arrow = " -> "
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if arrow in line:
            left, new_ver = line.split(arrow, 1)
            parts = left.split(None, 1)
            if len(parts) >= 2:
                result.append(
                    UpdateEntry(
                        name=parts[0],
                        current_version=parts[1].strip(),
                        new_version=new_ver.strip(),
                        source=PackageSource.REPO,
                    )
                )
    return result


def parse_orphans(stdout: str) -> List[OrphanEntry]:
    """Parse 'pacman -Qdt' output: 'name version'."""
    result: List[OrphanEntry] = []
    for line in stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = LINE_RE.match(line)
        if m:
            result.append(OrphanEntry(name=m.group(1), version=m.group(2)))
    return result


def parse_search(stdout: str) -> List[PackageSummary]:
    """Parse 'pacman -Ss pattern' output. Format: 'repo/name version' then optional '    desc'."""
    result: List[PackageSummary] = []
    for line in stdout.strip().splitlines():
        # Skip description lines (indented with spaces)
        if line.startswith(" ") or line.startswith("\t"):
            continue
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) >= 2:
            name_part = parts[0]
            version = parts[1]
            # Only include lines that look like repo/name (pacman -Ss)
            if "/" in name_part:
                name = name_part.split("/", 1)[1]
                result.append(
                    PackageSummary(name=name, version=version, source=PackageSource.REPO)
                )
    return result


# pacman -Qi block: Key : Value (key can contain spaces, e.g. "Depends On")
_KEY_VALUE = re.compile(r"^([\w\s]+?)\s*:\s*(.*)$")


def parse_details(stdout: str, source: PackageSource = PackageSource.REPO) -> Optional[PackageDetails]:
    """Parse 'pacman -Qi name' or 'pacman -Si name' block into PackageDetails."""
    fields: dict[str, str] = {}
    for line in stdout.strip().splitlines():
        m = _KEY_VALUE.match(line.strip())
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()
            fields[key] = value

    if not fields.get("Name"):
        return None

    def _parse_installed_size(s: str) -> int:
        """Parse '6.25 MiB', '123 KiB', '456 B' etc. into bytes."""
        if not s or s == "None":
            return 0
        s = s.strip()
        try:
            parts = s.split(None, 1)
            num_str = parts[0].replace(",", ".")
            num = float(num_str)
            if len(parts) == 1:
                return int(num)
            unit = (parts[1] or "").strip().upper()
            if unit.startswith("KIB"):
                return int(num * 1024)
            if unit.startswith("MIB"):
                return int(num * 1024 * 1024)
            if unit.startswith("GIB"):
                return int(num * 1024 * 1024 * 1024)
            if unit.startswith("KB"):
                return int(num * 1000)
            if unit.startswith("MB"):
                return int(num * 1000 * 1000)
            if unit.startswith("GB"):
                return int(num * 1000 * 1000 * 1000)
            return int(num)
        except (ValueError, TypeError, IndexError):
            return 0

    raw_size = fields.get("Installed Size", fields.get("InstalledSize", "0"))
    install_size = _parse_installed_size(raw_size)

    last_updated = (
        fields.get("Build Date")
        or fields.get("BuildDate")
        or fields.get("Install Date")
        or fields.get("InstallDate")
        or None
    )

    return PackageDetails(
        name=fields.get("Name", ""),
        version=fields.get("Version", ""),
        source=source,
        description=fields.get("Description", ""),
        install_size=install_size,
        last_updated=last_updated,
        maintainer=fields.get("Packager") or None,
        dependencies=_split_deps(fields.get("Depends On", fields.get("DependsOn", ""))),
        optional_deps=_split_deps(fields.get("Optional Deps", fields.get("OptionalDepends", ""))),
        conflicts=_split_deps(fields.get("Conflicts With", fields.get("ConflictsWith", ""))),
    )


def _split_deps(raw: str) -> List[str]:
    if not raw:
        return []
    return [x.strip() for x in re.split(r"\s+", raw) if x.strip()]


def parse_cache_stats(stdout: str) -> CacheStats:
    """Parse cache stats. Expect format from a custom script or paccache -s.
    If we use 'du -sb' and 'find | wc -l', we need two numbers. For simplicity
    accept stdout that has total size and count (e.g. one line 'size count' or
    two lines). Default: empty stats.
    """
    # Flexible: first line total bytes, second line count (or single line "bytes count")
    lines = [l.strip() for l in stdout.strip().splitlines() if l.strip()]
    total_size = 0
    count = 0
    for line in lines:
        parts = line.split()
        for p in parts:
            try:
                n = int(p)
                if n > 1_000_000:  # likely bytes
                    total_size = n
                else:
                    count = n
            except ValueError:
                pass
    if count == 0 and len(lines) >= 1 and lines[0].isdigit():
        count = int(lines[0])
    return CacheStats(total_size_bytes=total_size, package_count=count)
