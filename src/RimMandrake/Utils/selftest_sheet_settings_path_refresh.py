#!/usr/bin/env python3
"""WADING_SETTINGS_FIX_STALE_PATH_COSTS: a settings write re-reads standing water's path costs.

The sheet's wading cost (RM_MapComponent_Sheet.PathCostAt) reads RM_SheetSettings.pawnEffectsEnabled and
sheetPathCost, but the path grid re-read a square only when its tier changed (EnginePulse), so toggling pawn
effects or moving the wading-cost slider left every standing pool on its old cost. The fix:
RimMandrakeFlowWorksMod.WriteSettings calls RM_MapComponent_Sheet.ReapplyPathCosts, which fingerprints the two
settings and, when the fingerprint moved, re-reads every sheet/pool square on every map.

This reads the PRODUCTION source (Verse-bound, so the dotnet SelfTest project cannot compile it) and requires
that shape, so a revert fails here; and it checks the committed DLL's .srchash covers the sources as they are.
NOT proven here: a live map's path grid actually changing (that is the engine's RecalculatePerceivedPathCostAt).

    python3 selftest_sheet_settings_path_refresh.py
"""
from __future__ import annotations

import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.normpath(os.path.join(HERE, "..", "FlowWorks"))
SRC = os.path.join(FW, "Source")
SRCHASH = os.path.join(FW, "Assemblies", "RimMandrakeFlowWorks.dll.srchash")

fails = 0


def check(ok, what):
    global fails
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails += 1


def read(rel):
    with open(os.path.join(SRC, rel), encoding="utf-8-sig") as f:
        return f.read()


def collapse(s):
    return re.sub(r"\s+", " ", s)


def between(src, start, end):
    i = src.find(start)
    if i < 0:
        return ""
    j = src.find(end, i + len(start))
    return src[i:] if j < 0 else src[i:j]


def main():
    mod = collapse(read("RimMandrakeFlowWorksMod.cs"))
    ws = between(mod, "public override void WriteSettings()", "}")
    check("base.WriteSettings();" in ws, "WriteSettings found (and still saves)")
    check("Sheet.RM_MapComponent_Sheet.ReapplyPathCosts();" in ws, "WriteSettings re-applies the sheet's path costs")

    sheet = collapse(read(os.path.join("Sheet", "RM_MapComponent_Sheet.cs")))
    fp = between(sheet, "public static int PathCostFingerprint()", ";")
    check("RM_SheetSettings.pawnEffectsEnabled" in fp and "RM_SheetSettings.sheetPathCost" in fp,
          "the fingerprint reads both settings PathCostAt reads")
    pc = between(sheet, "public static int PathCostAt(Map map, IntVec3 c)", "public static int PathCostFingerprint()")
    used = set(re.findall(r"RM_SheetSettings\.(\w+)", pc))
    check(used and used <= {"pawnEffectsEnabled", "sheetPathCost"},
          "PathCostAt reads no setting the fingerprint misses (reads %s)" % sorted(used))
    body = between(sheet, "public static void ReapplyPathCosts()", "// ──")
    check(bool(body), "ReapplyPathCosts found")
    check("if (fp == appliedPathCostFingerprint)" in body and "appliedPathCostFingerprint = fp;" in body,
          "an unchanged fingerprint does nothing; a changed one is recorded")
    check("foreach (Map m in Find.Maps)" in body, "every map is visited")
    check("t == Tier.Sheet || t == Tier.Pool" in body and "m.pathing.RecalculatePerceivedPathCostAt(c);" in body,
          "every sheet/pool square's perceived path cost is re-read")
    i_rec = body.find("appliedPathCostFingerprint = fp;")
    i_play = body.find("Current.ProgramState != ProgramState.Playing")
    check(0 <= i_rec < i_play, "the fingerprint is recorded before the not-playing early return (a menu change is not re-read later as a change)")

    # the committed DLL was built from these sources
    hashes = {}
    with open(SRCHASH, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            h, _, rel = line.rstrip("\n").partition(" ")
            hashes[rel] = h
    for rel in ("RimMandrakeFlowWorksMod.cs", "Sheet/RM_MapComponent_Sheet.cs"):
        with open(os.path.join(SRC, rel), "rb") as f:
            have = hashlib.sha256(f.read()).hexdigest()
        check(hashes.get(rel) == have, "RimMandrakeFlowWorks.dll.srchash covers " + rel + " as committed")

    print("RESULT: %s (%d failure(s))" % ("PASS" if fails == 0 else "FAIL", fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
