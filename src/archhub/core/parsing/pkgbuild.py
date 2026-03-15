"""Parse PKGBUILD content (no execution/sourcing)."""

from __future__ import annotations

import re
from typing import List, Optional

from archhub.core.models import PackageDetails, PackageSource


# key=value (value: unquoted, single-quoted, or double-quoted)
_ASSIGN_RE = re.compile(
    r"^(\w+)\s*=\s*(.*)$"
)
# key=(item1 item2 'item with spaces')  - capture the inner part
_ARRAY_RE = re.compile(
    r"^(\w+)\s*=\s*\(\s*(.*)\s*\)\s*$",
    re.DOTALL,
)


def _unquote(s: str) -> str:
    s = s.strip()
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        return s[1:-1].strip()
    return s


def _parse_array_content(inner: str) -> List[str]:
    """Parse array inner (space-separated, quoted items allowed)."""
    result: List[str] = []
    inner = inner.strip()
    if not inner:
        return result
    # Simple approach: split by whitespace but respect quotes
    current = []
    in_quote = None
    for c in inner:
        if in_quote:
            if c == in_quote:
                in_quote = None
                result.append("".join(current).strip())
                current = []
            else:
                current.append(c)
        elif c in ("'", '"'):
            in_quote = c
            if current:
                result.append("".join(current).strip())
                current = []
        elif c in (" ", "\t", "\n"):
            if current:
                result.append("".join(current).strip())
                current = []
        else:
            current.append(c)
    if current:
        result.append("".join(current).strip())
    return [x for x in result if x]


def _resolve_vars(text: str, vars: dict[str, str]) -> str:
    """Replace ${var} and $var with values from vars (no nesting)."""
    out = text
    for k, v in vars.items():
        out = out.replace("${" + k + "}", v)
        # $var at word boundary
        out = re.sub(r"\$" + re.escape(k) + r"(?:\s|$|[^\w])", v + " ", out)
    return out.strip()


def parse_pkgbuild(content: str, source: PackageSource = PackageSource.AUR) -> Optional[PackageDetails]:
    """
    Parse PKGBUILD text into PackageDetails. Does not execute or source the file.
    Extracts: pkgname, pkgver, pkgrel, description, depends, optdepends, conflicts.
    """
    # Join line continuations
    content = content.replace("\\\n", "\n")
    lines = content.splitlines()
    raw: dict[str, str | List[str]] = {}
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        # Array: key=( ... ) possibly multiline
        m = _ARRAY_RE.match(line)
        if m:
            key, inner = m.group(1), m.group(2)
            raw[key] = _parse_array_content(inner)
            i += 1
            continue
        # Start of multiline array: key=(
        if re.match(r"^(\w+)\s*=\s*\(\s*$", line):
            key_m = re.match(r"^(\w+)\s*=\s*\(\s*$", line)
            if key_m:
                key = key_m.group(1)
                acc = []
                i += 1
                while i < len(lines):
                    rest = lines[i].strip()
                    if rest.rstrip().endswith(")"):
                        acc.append(rest.rstrip()[:-1].strip())
                        i += 1
                        break
                    acc.append(rest)
                    i += 1
                raw[key] = _parse_array_content(" ".join(acc))
                continue
        # Simple assignment
        m = _ASSIGN_RE.match(line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            value = _unquote(value)
            raw[key] = value
        i += 1

    # Resolve common variables for version and description
    vars_map: dict[str, str] = {}
    for k in ("pkgver", "pkgrel", "pkgname", "pkgbase"):
        v = raw.get(k)
        if isinstance(v, str):
            vars_map[k] = v
    description = raw.get("pkgdesc") or raw.get("description")
    if isinstance(description, str):
        description = _resolve_vars(description, vars_map)
    else:
        description = ""

    # Package name: prefer pkgbase (e.g. split packages), else pkgname (string or first element)
    pkgbase = raw.get("pkgbase")
    pkgname_raw = raw.get("pkgname")
    if isinstance(pkgbase, str) and pkgbase.strip():
        name = _resolve_vars(pkgbase.strip(), vars_map)
    elif isinstance(pkgname_raw, str):
        name = _resolve_vars(pkgname_raw, vars_map)
    elif isinstance(pkgname_raw, list) and pkgname_raw:
        first = pkgname_raw[0]
        name = first.strip() if isinstance(first, str) else ""
    else:
        name = ""
    if not name:
        return None

    pkgver = vars_map.get("pkgver", "")
    pkgrel = vars_map.get("pkgrel", "1")
    version = f"{pkgver}-{pkgrel}" if pkgver else pkgrel

    def _deps(key: str) -> List[str]:
        val = raw.get(key)
        if isinstance(val, list):
            return [x for x in val if x]
        if isinstance(val, str) and val.strip():
            return _parse_array_content(val) if "(" in val else [x.strip() for x in val.split() if x.strip()]
        return []

    depends = _deps("depends")
    optdepends = _deps("optdepends")
    conflicts = _deps("conflicts")

    return PackageDetails(
        name=name,
        version=version,
        source=source,
        description=description,
        install_size=0,
        last_updated=None,
        maintainer=None,
        dependencies=depends,
        optional_deps=optdepends,
        conflicts=conflicts,
    )
