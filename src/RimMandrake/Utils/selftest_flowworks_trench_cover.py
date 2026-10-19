#!/usr/bin/env python3
"""Wrapper for the C# selftest of FlowWorks trench cover (TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT).

Runs FlowWorks/Source/SelfTestTrench (net8.0, no RimWorld/Unity), which compiles the production
RM_TrenchCoverMath.cs directly: the canal_cover_design_2026-10-17.md section 4 table (0.22 / 0.44 / 0.66 for a 1.7 m
person at 0.5 / 1 / 1.5 m), enfilade 0, lip shooter x0.333, an intact pit cover and natural water reading 0, sandbag
stacking with the cap, and the HitReportFor fold. Same dotnet.exe discovery and staging as selftest_flowworks_stock.py.

    python3 selftest_flowworks_trench_cover.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "FlowWorks", "Source", "SelfTestTrench",
    "RimMandrakeFlowWorks.TrenchSelfTest.csproj",
)

DOTNET_CANDIDATES = [
    "/mnt/c/Users/Mandrake/.dotnet/dotnet.exe",
    "/mnt/c/Program Files/dotnet/dotnet.exe",
]


def _find_dotnet():
    for c in DOTNET_CANDIDATES:
        if os.path.isfile(c):
            return c
    return None


def _to_windows_path(posix_path):
    """/mnt/d/Luke/... -> D:\\Luke\\... . dotnet.exe cannot resolve /mnt/*."""
    p = os.path.abspath(posix_path)
    if p.startswith("/mnt/") and len(p) > 6 and p[6] == "/":
        drive = p[5].upper()
        rest = p[7:].replace("/", "\\")
        return "%s:\\%s" % (drive, rest)
    return p.replace("/", "\\")


import contextlib


@contextlib.contextmanager
def dotnet_lock():
    """Both FlowWorks selftest wrappers build the same SelfTest project; run_selftests.py runs them in parallel,
    so they take this lock around every dotnet call (a rebuild under a running dll raced before)."""
    import fcntl
    import tempfile
    with open(os.path.join(tempfile.gettempdir(), "flowworks_selftest_dotnet.lock"), "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def main():
    if not os.path.isfile(CSPROJ):
        sys.exit("RimMandrakeFlowWorks.TrenchSelfTest.csproj not found at %s — the "
                 "SelfTest project moved or was never built" % CSPROJ)

    dotnet = _find_dotnet()
    if dotnet is None:
        sys.exit(
            "dotnet.exe not found at any of %r — this selftest needs the "
            "user-local Windows-side .NET SDK (see CLAUDE.md's C# build "
            "toolchain note); UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)

    from selftest_winstage import windows_project_path  # an ext4 clone stages through winbuild
    win_csproj = windows_project_path(CSPROJ)
    cmd = [dotnet, "run", "--project", win_csproj, "-c", "Release"]
    with dotnet_lock():
        result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
