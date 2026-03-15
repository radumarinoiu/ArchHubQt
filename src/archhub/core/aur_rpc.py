"""AUR RPC client: fetch package details from https://aur.archlinux.org/rpc/ (v5 API)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from archhub.core.models import PackageDetails, PackageSource

logger = logging.getLogger(__name__)

AUR_RPC_BASE = "https://aur.archlinux.org/rpc"
AUR_RPC_VERSION = "v5"


def _get(url: str, timeout: float = 10.0) -> Optional[dict[str, Any]]:
    """GET URL and return parsed JSON, or None on error."""
    try:
        req = Request(url, headers={"User-Agent": "ArchHubQt/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError, json.JSONDecodeError, OSError) as e:
        logger.warning("AUR RPC request failed: %s", e)
        return None


def _parse_info_result(data: dict[str, Any]) -> Optional[PackageDetails]:
    """Map a single AUR RPC info result to PackageDetails."""
    if not data:
        return None
    name = data.get("Name") or data.get("PackageBase")
    if not name:
        return None
    version = data.get("Version") or ""
    description = data.get("Description") or ""
    maintainer = data.get("Maintainer")
    if maintainer is None:
        maintainer = None
    else:
        maintainer = str(maintainer).strip() or None

    def _list(val: Any) -> List[str]:
        if val is None:
            return []
        if isinstance(val, list):
            return [str(x).strip() for x in val if x is not None]
        return []

    depends = _list(data.get("Depends"))
    optdepends = _list(data.get("OptDepends"))
    conflicts = _list(data.get("Conflicts"))

    last_modified = data.get("LastModified")
    last_updated: Optional[str] = None
    if last_modified is not None:
        try:
            ts = int(last_modified)
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            last_updated = dt.isoformat()
        except (TypeError, ValueError, OSError):
            last_updated = str(last_modified) if last_modified else None

    return PackageDetails(
        name=name,
        version=version,
        source=PackageSource.AUR,
        description=description,
        install_size=0,
        last_updated=last_updated,
        maintainer=maintainer,
        dependencies=depends,
        optional_deps=optdepends,
        conflicts=conflicts,
    )


def get_package_info(
    name: str,
    *,
    base_url: str = AUR_RPC_BASE,
    version: str = AUR_RPC_VERSION,
    timeout: float = 10.0,
) -> Optional[PackageDetails]:
    """
    Fetch package details from the AUR RPC (v5) info endpoint.

    Uses GET /rpc/v5/info/{arg} (path-based) for a single package.
    See https://aur.archlinux.org/rpc/ and /rpc/openapi.json.
    """
    if not name or not name.strip():
        return None
    name = name.strip()
    url = f"{base_url.rstrip('/')}/{version}/info/{quote(name, safe='')}"
    data = _get(url, timeout=timeout)
    if data is None:
        return None
    if data.get("type") == "error":
        logger.warning("AUR RPC error: %s", data.get("error", "unknown"))
        return None
    results = data.get("results")
    if not results or not isinstance(results, list):
        return None
    first = results[0] if results else None
    return _parse_info_result(first)


def get_package_info_multi(
    names: List[str],
    *,
    base_url: str = AUR_RPC_BASE,
    version: str = AUR_RPC_VERSION,
    timeout: float = 10.0,
) -> List[PackageDetails]:
    """
    Fetch details for multiple packages in one request.

    Uses GET /rpc/v5/info?arg[]=pkg1&arg[]=pkg2 (query style).
    Returns a list in the same order as names (missing packages omitted).
    """
    if not names:
        return []
    names = [n.strip() for n in names if n and n.strip()]
    if not names:
        return []
    query = urlencode([("arg[]", n) for n in names])
    url = f"{base_url.rstrip('/')}/{version}/info?{query}"
    data = _get(url, timeout=timeout)
    if data is None:
        return []
    if data.get("type") == "error":
        return []
    results = data.get("results")
    if not results or not isinstance(results, list):
        return []
    out: List[PackageDetails] = []
    for r in results:
        details = _parse_info_result(r)
        if details is not None:
            out.append(details)
    return out
