#!/usr/bin/env python3
# selftest-timeout: 720   (the full ~1000-case run took 302 s on 2026-10-25, staging and build included; 240 s timed out)
"""Wrapper for the C# selftest of the FlowWorks source stock model (§5).

`selftest_*.py` is the established convention for fast, offline, pre-commit
tests (see selftest_validate_patch.py for the canonical example). What this
covers - FlowWorks/Source/RM_StockMath.cs, the arithmetic of
design/RimMandrake/flowworks_mod_definition.md section 5's source stock model,
and FlowWorks/Source/RM_PitTrapMath.cs, the pit-width trap rule
(SUPERDEEP_HOLDER_RETIRE_1) - is C#, not Python, and this project has no xUnit/NUnit precedent. So the
actual test lives in a small standalone net8.0 console app needing no
RimWorld/Unity assemblies: FlowWorks/Source/SelfTest/.

WHAT MAKES THIS ONE STRONG: the retired Pits selftest (selftest_pit_logic.py,
deleted with the building pit 2026-10-02) hand-extracted its escape-chance
formula, so it kept passing against the old formula if the real method changed.
This project extracts NOTHING. RM_StockMath.cs is the production file the shipping mod
compiles, pulled into the test project directly, so the 5:1 budget, the
seepage/rain/season refill, the supported-cell floor, the recession ordering
and the credit/debit primitives are all covered for real.

dotnet is WINDOWS-NATIVE (see RimMandrake_FlowWorks.csproj's own build comment)
and cannot take a /mnt/d path, so this script finds dotnet.exe and hands it the
project path from selftest_winstage.windows_project_path (a D-drive path on the
/mnt tree; a staged copy under D:\\ClaudeWork\\rimmandrake\\build from an ext4 clone).
The SelfTest project now also carries the hose suites and every other Verse-free
FlowWorks check (325+ cases), not only the stock and pit-trap math.
_to_windows_path stays: selftest_flowworks_kernel_oracle.py imports it.

    python3 selftest_flowworks_stock.py
    python3 selftest_flowworks_stock.py --only RiverSwitchFlip_*,LadderWall_call_sites [--no-build]

`--only` (SELFTEST_FILTER_BUILD_SERIAL_DLL) runs only the named cases (a trailing * is a prefix); modcheck's
validation.py passes each chain's case names, and `--no-build` after the first call of a suite run. Staging, build
and run all sit inside dotnet_lock, so two wrappers in one seat never rsync a stage under each other's build.
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "FlowWorks", "Source", "SelfTest",
    "RimMandrakeFlowWorks.SelfTest.csproj",
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


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="FlowWorks C# SelfTest")
    ap.add_argument("--only", default=None, help="comma list of case names; a trailing * is a prefix")
    ap.add_argument("--no-build", action="store_true", help="run the exe the last build left (same source)")
    a = ap.parse_args(argv)
    if not os.path.isfile(CSPROJ):
        sys.exit("RimMandrakeFlowWorks.SelfTest.csproj not found at %s — the "
                 "SelfTest project moved or was never built" % CSPROJ)

    dotnet = _find_dotnet()
    if dotnet is None:
        sys.exit(
            "dotnet.exe not found at any of %r — this selftest needs the "
            "user-local Windows-side .NET SDK (see CLAUDE.md's C# build "
            "toolchain note); UNMEASURED, not a pass or a fail" % DOTNET_CANDIDATES)

    from selftest_winstage import windows_project_path  # an ext4 clone stages through winbuild
    with dotnet_lock():     # the stage rsync too: a peer wrapper's rsync must not land under this build or run
        win_csproj = windows_project_path(CSPROJ, restage=not a.no_build)    # --no-build reuses the last stage
        cmd = [dotnet, "run", "--project", win_csproj, "-c", "Release"] + (["--no-build"] if a.no_build else [])
        if a.only:
            cmd += ["--", "--only", a.only]
        result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        # The nightly log keeps only the last lines of a failing test; the failing check is mid-output.
        # Echo every FAIL line (and its detail line) last so the tail names it. (FLOWWORKS_STOCK_BISECT_RED_CHECK)
        lines = result.stdout.splitlines()
        bad = []
        for i, ln in enumerate(lines):
            if ln.startswith("FAIL") or "FAILED" in ln or ln.lstrip().startswith("MISMATCH"):
                bad.append(ln)
                if i + 1 < len(lines) and lines[i + 1].startswith(" " * 4):
                    bad.append(lines[i + 1])
        print("\nFAILING CHECKS (rc %d)%s" % (result.returncode, ": none found in stdout - see stderr/crash" if not bad else ":"))
        for ln in bad[:20]:
            print("  " + ln.strip())
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
