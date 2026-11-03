#!/usr/bin/env python3
# selftest-timeout: 600   (130-200 s alone, over the 240 s default under the 6-worker nightly sweep: CRASH [timeout] 2026-10-26)
"""Wrapper for the C# selftest of FlowWorks trench cover (TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT).

Runs FlowWorks/Source/SelfTestTrench (net8.0, no RimWorld/Unity), which compiles the production
RM_TrenchCoverMath.cs directly: the canal_cover_design_2026-10-17.md section 4 table (0.22 / 0.44 / 0.66 for a 1.7 m
person at 0.5 / 1 / 1.5 m), enfilade 0, lip shooter x0.333, an intact pit cover and natural water reading 0, sandbag
stacking with the cap, and the HitReportFor fold. Same dotnet.exe discovery and staging as selftest_flowworks_stock.py.

    python3 selftest_flowworks_trench_cover.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Utils -> RimMandrake -> src -> repo root.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSPROJ = os.path.join(
    REPO, "src", "RimMandrake", "FlowWorks", "Source", "SelfTestTrench",
    "RimMandrakeFlowWorks.TrenchSelfTest.csproj",
)

TRENCH_COVER_CS = os.path.join(REPO, "src", "RimMandrake", "FlowWorks", "Source", "RM_TrenchCover.cs")


def _method_body(src, signature_re):
    """The brace-balanced body of the first method whose header matches signature_re, or None."""
    m = re.search(signature_re, src)
    if m is None:
        return None
    i = src.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[i + 1:j]
    return None


def _strip_comments(src):
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    return re.sub(r"//[^\n]*", " ", src)


def _squash(s):
    return re.sub(r"\s+", "", s)


def wiring_checks(path=TRENCH_COVER_CS):
    """TRENCH_COVER_FIX_DECK_ERASES_UNDERPASS: the C# SelfTest compiles only RM_TrenchCoverMath.cs, so the CALLER half of
    the fix (RM_TrenchCover.cs, RimWorld-bound, not compilable off-game) is pinned here by reading its source. Each
    check names the mutant that brings the defect back. Returns a list of (ok, label)."""
    src = _strip_comments(open(path, encoding="utf-8").read())
    out = []
    gda = _method_body(src, r"static\s+int\s+GroundDepthAt\s*\(\s*Map\s+map\s*,\s*RM_MapComponent_Excavation\s+eng\s*,"
                            r"\s*int\s+x\s*,\s*int\s+z\s*,\s*bool\s+floorView\s*\)")
    out.append((gda is not None, "GroundDepthAt(map, eng, x, z, bool floorView) exists"))
    g = _squash(gda or "")
    m = re.search(r"RM_SpanMath\.DeckReadr=(?:Pits\.)?RM_SpanUtility\.ReadAt\(map,c\);", g)
    out.append((m is not None, "GroundDepthAt reads the deck: r = RM_SpanUtility.ReadAt(map, c)"))
    calls = re.findall(r"RM_TrenchCoverMath\.GroundDepth\(([^()]*)\)", g)
    out.append((calls == ["h,r.Decked,r.DeckNotches,r.FloorBandPassesUnder,floorView"],
                "GroundDepthAt passes (h, r.Decked, r.DeckNotches, r.FloorBandPassesUnder, floorView) "
                "to RM_TrenchCoverMath.GroundDepth (found %r)" % calls))
    # No return of the math that drops the deck read: every return is 0/-1 or the one GroundDepth call.
    rets = re.findall(r"return([^;]*);", g)
    bad = [r for r in rets if r not in ("0", "-1") and not r.startswith("RM_TrenchCoverMath.GroundDepth(")]
    out.append((not bad and any(r.startswith("RM_TrenchCoverMath.GroundDepth(") for r in rets),
                "GroundDepthAt returns only 0 / -1 / the GroundDepth call (found %r)" % rets))
    # No other early exit: an `if (r.Decked) return 0;` would erase the floor band's cover again.
    conds = re.findall(r"if\(([^{;]*)\)\{", g)
    out.append((conds == ["!c.InBounds(map)", "h<=0"] and g.count("if(") == 2 and "?" not in g,
                "GroundDepthAt's only early exits are out-of-bounds and no hollow (found %r)" % conds))
    fvo = _method_body(src, r"static\s+bool\s+FloorViewOf\s*\(\s*Pawn\s+p\s*,\s*IntVec3\s+cell\s*\)")
    f = _squash(fvo or "")
    out.append(("returnp.Position==cell?Pits.RM_SuspensionUnderpass.InFloorBand(p):Pits.RM_SuspensionUnderpass.UsesFloorView(p);"
                in f, "FloorViewOf: the pawn on the cell reads InFloorBand(p), a would-be occupant UsesFloorView(p)"))
    bf = _method_body(src, r"static\s+float\s+BlockFor\s*\(\s*LocalTargetInfo\s+target\s*,\s*IntVec3\s+shooterLoc\s*,\s*Map\s+map\s*\)")
    b = _squash(bf or "")
    out.append(("Pawnp=OccupantOf(target,map);boolfloorView=FloorViewOf(p,cell);" in b,
                "BlockFor: floorView = FloorViewOf(OccupantOf(target, map), cell)"))
    gcalls = re.findall(r"GroundDepthAt\(([^()]*)\)", b)
    out.append((len(gcalls) >= 2 and all(a == "map,eng,cell.x,cell.z,floorView" or a == "map,eng,x,z,floorView"
                                         for a in gcalls)
                and "map,eng,cell.x,cell.z,floorView" in gcalls and "map,eng,x,z,floorView" in gcalls,
                "BlockFor feeds floorView to GroundDepthAt at the target cell and in the TrenchBlock lambda (found %r)"
                % gcalls))
    out.append((re.search(r"floorView=", b.replace("boolfloorView=FloorViewOf(p,cell);", "")) is None,
                "BlockFor never reassigns floorView"))
    return out


# Mutants of RM_TrenchCover.cs that bring the defect back; each must turn wiring_checks red. Run on every invocation so
# a check that went blind (a reformatted source, a regex that matches anything) fails here instead of passing.
WIRING_MUTANTS = [
    ("blind checker's mutant: GroundDepth(h, r.Decked, 0, false, false)",
     "GroundDepth(h, r.Decked, r.DeckNotches, r.FloorBandPassesUnder, floorView)", "GroundDepth(h, r.Decked, 0, false, false)"),
    ("the math is handed floorView=false",
     "r.FloorBandPassesUnder, floorView)", "r.FloorBandPassesUnder, false)"),
    ("the deck notches are dropped", "r.Decked, r.DeckNotches,", "r.Decked, 0,"),
    ("ReadAt replaced by an empty read",
     "RM_SpanMath.DeckRead r = Pits.RM_SpanUtility.ReadAt(map, c);", "RM_SpanMath.DeckRead r = default;"),
    ("an early 0 on any deck (braced)",
     "RM_SpanMath.DeckRead r = Pits.RM_SpanUtility.ReadAt(map, c);",
     "RM_SpanMath.DeckRead r = Pits.RM_SpanUtility.ReadAt(map, c);\nif (r.Decked) { return 0; }"),
    ("an early 0 on any deck (unbraced)",
     "RM_SpanMath.DeckRead r = Pits.RM_SpanUtility.ReadAt(map, c);",
     "RM_SpanMath.DeckRead r = Pits.RM_SpanUtility.ReadAt(map, c);\nif (r.Decked) return 0;"),
    ("BlockFor ignores the occupant's band", "bool floorView = FloorViewOf(p, cell);", "bool floorView = false;"),
    ("FloorViewOf drops InFloorBand", "? Pits.RM_SuspensionUnderpass.InFloorBand(p) :", "? false :"),
    ("the target-cell read drops floorView",
     "GroundDepthAt(map, eng, cell.x, cell.z, floorView)", "GroundDepthAt(map, eng, cell.x, cell.z, false)"),
    ("the TrenchBlock lambda drops floorView", "GroundDepthAt(map, eng, x, z, floorView)", "GroundDepthAt(map, eng, x, z, false)"),
]


def mutant_selfcheck(path=TRENCH_COVER_CS):
    """[(red, label)] — red=True when the mutant made wiring_checks fail, as it must."""
    import tempfile
    src = open(path, encoding="utf-8").read()
    out = []
    for label, a, b in WIRING_MUTANTS:
        if src.count(a) != 1:
            out.append((False, "%s: anchor %r found %d times (source moved; re-anchor the mutant)" % (label, a, src.count(a))))
            continue
        fd, tmp = tempfile.mkstemp(suffix=".cs")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(src.replace(a, b))
            red = not all(ok for ok, _ in wiring_checks(tmp))
        finally:
            os.unlink(tmp)
        out.append((red, label))
    return out


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
    wiring_failed = 0
    for ok, label in wiring_checks():
        print("%s  wiring: %s" % ("PASS" if ok else "FAIL", label))
        wiring_failed += 0 if ok else 1
    for red, label in mutant_selfcheck():
        print("%s  wiring mutant goes red: %s" % ("PASS" if red else "FAIL", label))
        wiring_failed += 0 if red else 1
    if wiring_failed:
        sys.exit("%d RM_TrenchCover.cs wiring check(s) or mutant(s) FAILED" % wiring_failed)
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
