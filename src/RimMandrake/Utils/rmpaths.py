#!/usr/bin/env python3
r"""rmpaths.py — the ONE answer to "where does RimMandrake keep runtime data outside git?"

Scratch, build stages, artpipe queue state, the art store, observatory logs and RimPulse
digests live under ONE data root, never in `D:\Luke\dev`. Owner, 2026-10-19: *"Could you
please stop putting things in Luke\dev\_(filename) directories? dev is my special directory
for Lodestar-managed projects, not a temp dir for your stuff. Find another storage place for
yourself permanently and use it."*

Resolution (no default path, on purpose — a default is how a scratch dir inside the owner's dev tree happened):
  1. `$RM_DATA_ROOT` (systemd units and the Windows scheduled tasks set it; a `/mnt/<d>/...`
     value is translated to `<D>:\...` under Windows python).
  2. POSIX: Lodestar's machine-wide agent storage root —
     `python3 ~/dev/Lodestar/bin/lib/agent_storage.py rimmandrake`
     (archmagi: `/mnt/d/ClaudeWork/rimmandrake` = `D:\ClaudeWork\rimmandrake`).
     Windows: `$AGENT_STORAGE_ROOT\rimmandrake`.
  3. Otherwise raise `RmDataRootUnset`, naming both variables.

Layout (old -> new, moved 2026-10-20): `_artpipe`->`artpipe`, `_artstore`->`artstore`,
`_rmscratch`->`scratch`, `_rmbuild`->`build`, `_obs`->`obs`, `_rmdashboard`->`dashboard`.

    python3 src/RimMandrake/Utils/rmpaths.py            # the root
    python3 src/RimMandrake/Utils/rmpaths.py build      # <root>/build
    python3 src/RimMandrake/Utils/rmpaths.py --native scratch
"""
from __future__ import annotations

import functools
import os
import re
import subprocess
import sys
from pathlib import Path

ENV_VAR = "RM_DATA_ROOT"
LODESTAR_ENV = "AGENT_STORAGE_ROOT"
PROJECT = "rimmandrake"
AGENT_STORAGE = os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")
IS_WIN = os.name == "nt"


class RmDataRootUnset(RuntimeError):
    """No data root could be resolved; there is deliberately no fallback."""


def _to_win(p: str) -> str:
    m = re.match(r"^/mnt/([a-zA-Z])(/.*)?$", p)
    if not m:
        return p
    return m.group(1).upper() + ":" + (m.group(2) or "/").replace("/", "\\")


def to_win(p) -> str:
    """`/mnt/d/X/y` -> `D:\\X\\y`; anything else unchanged."""
    return _to_win(str(p))


def _check(p: str) -> str:
    low = p.replace("\\", "/").lower().rstrip("/")
    if re.search(r"(^|/)luke/dev(/|$)", low) or "/home/mandrake/dev" in low:
        raise RmDataRootUnset(f"data root {p!r} is inside the owner's dev tree (D:\\Luke\\dev / ~/dev), "
                              "which holds Lodestar-managed git projects only")
    return p


@functools.lru_cache(maxsize=None)
def _resolve(env_value: str, lodestar_value: str) -> str:
    if env_value:
        return _check(_to_win(env_value) if IS_WIN else env_value)
    if IS_WIN:
        if lodestar_value:
            return _check(os.path.join(_to_win(lodestar_value), PROJECT))
        raise RmDataRootUnset(f"set {ENV_VAR} (e.g. D:\\ClaudeWork\\rimmandrake) or {LODESTAR_ENV} "
                              "in the user environment; Windows python cannot run Lodestar's helper")
    if not os.path.isfile(AGENT_STORAGE):
        raise RmDataRootUnset(f"{ENV_VAR} unset and Lodestar's {AGENT_STORAGE} is absent")
    r = subprocess.run([sys.executable or "python3", AGENT_STORAGE, PROJECT],
                       capture_output=True, text=True, timeout=30)
    out = r.stdout.strip()
    if r.returncode != 0 or not out:
        raise RmDataRootUnset(f"{ENV_VAR} unset and agent_storage.py failed: {r.stderr.strip()}")
    return _check(out)


def rm_data_root() -> Path:
    return Path(_resolve(os.environ.get(ENV_VAR, "").strip(), os.environ.get(LODESTAR_ENV, "").strip()))


def rm_path(name: str, *parts) -> Path:
    """`<root>/<name>/<parts...>`; `name` is a plain word (no `_` prefix — that was the old layout)."""
    if not name or name.startswith(("_", ".", "/", "\\")) or "/" in name or "\\" in name:
        raise ValueError(f"rm_path name must be a plain word, got {name!r}")
    return rm_data_root().joinpath(name, *[str(p) for p in parts])


def rm_str(name: str, *parts) -> str:
    return str(rm_path(name, *parts))


def rm_win(name: str, *parts) -> str:
    """The Windows spelling (`D:\\ClaudeWork\\rimmandrake\\...`), for python.exe/codex.exe/dotnet args."""
    return to_win(rm_path(name, *parts))


if __name__ == "__main__":
    args = sys.argv[1:]
    native = "--native" in args
    args = [a for a in args if a != "--native"]
    try:
        p = rm_path(*args) if args else rm_data_root()
    except RmDataRootUnset as e:
        sys.stderr.write(f"rmpaths: {e}\n")
        sys.exit(2)
    print(to_win(p) if native else p)
