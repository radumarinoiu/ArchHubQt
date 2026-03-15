"""Subprocess runner: timeout, env, exit code, structured result. Single place for all process execution."""

from __future__ import annotations

import logging
import subprocess
from typing import Optional, Sequence, Union

from pydantic import BaseModel

from archhub.core.models import RunResult

logger = logging.getLogger(__name__)


class RunnerOptions(BaseModel):
    """Options for a single run."""

    timeout_seconds: Optional[float] = 60.0
    env: Optional[dict[str, str]] = None
    cwd: Optional[str] = None


def run(
    args: Sequence[Union[str, bytes]],
    options: Optional[RunnerOptions] = None,
) -> RunResult:
    """Run a command; return structured result. No shell—pass args as list."""
    opts = options or RunnerOptions()
    try:
        proc = subprocess.run(
            [str(a) for a in args],
            capture_output=True,
            text=True,
            timeout=opts.timeout_seconds,
            env=opts.env,
            cwd=opts.cwd,
        )
        return RunResult(
            exit_code=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            timeout=False,
        )
    except subprocess.TimeoutExpired as e:
        logger.warning("Command timed out: %s", args)
        return RunResult(
            exit_code=-1,
            stdout=e.stdout.decode("utf-8", errors="replace") if e.stdout else "",
            stderr="Command timed out",
            timeout=True,
        )
    except FileNotFoundError as e:
        logger.warning("Command not found: %s", e)
        return RunResult(
            exit_code=-1,
            stdout="",
            stderr=str(e),
            timeout=False,
        )
    except Exception as e:
        logger.exception("Run failed: %s", args)
        return RunResult(
            exit_code=-1,
            stdout="",
            stderr=str(e),
            timeout=False,
        )
