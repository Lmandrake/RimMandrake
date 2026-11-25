#!/usr/bin/env python3
"""selftest_flowworks_humanlike_height.py — RIMMANDRAKE_CLASS_DROID_AND_JAWA_GONE_IN_SHALLOW_TAR.

WHY: on the pawn-in-liquid grid (PAWN_IN_LIQUID_GRID.png, read 2026-11-22 and 2026-11-24) a T3 droid and a Jawa stood
wholly hidden in 0.5 m tar while a colonist showed almost whole. Class: MOD WRONG, and the matrix CHECK WRONG with it.
  - mod: RM_Drowning.HeightOf gave every pawn its climb band's height (RM_RelativeRulesMath.HeightByBand). Body size
    under 0.75 is band 1, the rat's 0.5 m: a Jawa (0.5) and a T3 droid (astromech family, 0.65) read height=0.5 in the
    matrix log, so 0.5 m of tar was over their crowns (mode Hidden; in water, Tinted whole), and the drowning law put
    their heads under at 0.45 m. Their pictures are 0.78 and 1.01 cells tall against a colonist's 1.22 (about 1.1 and
    1.45 m).
  - check: the matrix row `_mode` wanted the mode the rule gives for the pawn's OWN printed height, so it agreed with the
    wrong height. The matrix now also has `_shows_in_line_with_her_picture`, which reads her picture's span.
The fix: a humanlike's height is a person's 1.75 m scaled by sqrt(body size) (relative climb design §8.2, the rule
RM_TrenchCoverMath.HeightMetres already uses); animals and mechanoids keep the band table.

This test (python twin of HeightOf for a humanlike + the pawn-cut twin of selftest_flowworks_pawn_own_picture_cut.py):
  1. HeightOf branches on RaceProps.Humanlike and returns RM_RelativeRulesMath.HumanlikeHeightMetres(body size × m²);
  2. HumanlikeHeightMetres is HeightByBand[2] × sqrt(b): body size 1 stays 1.75 m;
  3. a Jawa (0.5) and a T3 droid (0.65) standing in 0.5 m tar are Cut, with most of the picture above the line, and
     their heads are not under; a colonist reads as before.
The C# SelfTest case Relative_humanlike_height_follows_body_size_not_rat_band checks the same (--dotnet).

CAN IT FAIL: RED on the parent commit (no humanlike branch: the Jawa is 0.5 m, Hidden). --mutate plants each fault.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_humanlike_height.py [--rev <sha>] [--mutate] [--dotnet]
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FILL = "src/RimMandrake/FlowWorks/Source/RM_PitFillEffects.cs"
REL = "src/RimMandrake/FlowWorks/Source/RM_RelativeRulesMath.cs"
TRAP = "src/RimMandrake/FlowWorks/Source/RM_PitTrapMath.cs"

_spec = importlib.util.spec_from_file_location("pawncut", HERE / "selftest_flowworks_pawn_own_picture_cut.py")
pawncut = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pawncut)

BODIES = {"Jawa": 0.5, "T3 droid": 0.65}
TAR_M = 0.5
HEAD_FRACTION = 0.9   # RM_RelativeRulesMath.DefaultHeadFraction


def read(rel: str, rev: str | None) -> str:
    return pawncut.read(rel, rev)


def body(src: str, signature: str) -> str:
    i = src.find(signature)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth, k = 0, j
    while k < len(src):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
        k += 1
    return ""


def twin(fill: str, rel: str, trap: str):
    """-> (height_of(body_size, humanlike), problems): the python twin of RM_Drowning.HeightOf, read from the sources."""
    probs = []
    bands = pawncut.table(rel, "HeightByBand")
    edges = pawncut.table(trap, "ClimbBandEdges")
    if not bands or not edges:
        return None, ["UNMEASURED: HeightByBand or ClimbBandEdges not read"]
    hof = pawncut.mask_comments(body(fill, "public static float HeightOf(Pawn p)"))
    hl = pawncut.mask_comments(body(rel, "public static float HumanlikeHeightMetres(float effectiveBodySize)"))
    branch = re.search(r"if\s*\(\s*p\?\.RaceProps\s*!=\s*null\s*&&\s*p\.RaceProps\.Humanlike\s*\)\s*\{[^}]*return\s+RM_RelativeRulesMath\.HumanlikeHeightMetres\(\s*p\.BodySize\s*\*\s*m\s*\*\s*m\s*\)", hof)
    if not hof:
        probs.append("RM_Drowning.HeightOf not found")
    elif not branch:
        probs.append("HeightOf gives a humanlike its climb band's height (no RaceProps.Humanlike branch to HumanlikeHeightMetres)")
    sq = re.search(r"return\s+HeightByBand\[2\]\s*\*\s*\(float\)Math\.Sqrt\(\s*b\s*\)", hl)
    if branch and not sq:
        probs.append("HumanlikeHeightMetres is not HeightByBand[2] x sqrt(body size)")

    def band_height(b):
        k = 1
        for i, e in enumerate(edges):
            if b >= e:
                k = i + 2
        return bands[min(max(k, 1), len(bands) - 1)]

    def height_of(b, humanlike):
        if humanlike and branch and sq:
            return bands[2] * math.sqrt(max(b, 0.01))
        return band_height(b)

    return height_of, probs


def check(fill: str, rel: str, trap: str, tables: dict) -> list[str]:
    height_of, bad = twin(fill, rel, trap)
    if height_of is None:
        return bad
    person = height_of(1.0, True)
    if abs(person - 1.75) > 1e-4:
        bad.append("a colonist (body size 1) is %.3f m, not 1.75 m" % person)
    for name, b in BODIES.items():
        h = height_of(b, True)
        mode, share, _ = pawncut.decide(tables, False, False, True, TAR_M, h, tables["CorpseMetres"], 0.0)
        if mode != "Cut" or not (0.0 < share < 0.5):
            bad.append("a %s (body size %.2f) in %.1f m tar: height %.2f m -> %s, share under %.3f (want Cut, most of "
                       "her picture showing)" % (name, b, TAR_M, h, mode, share))
        if TAR_M >= HEAD_FRACTION * h:
            bad.append("a %s (height %.2f m) has her head under in %.1f m" % (name, h, TAR_M))
    for b, want in ((0.3, 0.5), (2.4, 2.5), (4.0, 3.5)):   # hare, muffalo, thrumbo: the animal table is unchanged
        if abs(height_of(b, False) - want) > 1e-4:
            bad.append("an animal of body size %.1f is %.2f m, not the band's %.2f m" % (b, height_of(b, False), want))
    return bad


def run(rev: str | None) -> list[str]:
    fill, rel, trap = read(FILL, rev), read(REL, rev), read(TRAP, rev)
    tables = pawncut.load_tables(read(pawncut.MATH, rev), read(pawncut.UL, rev))
    return check(fill, rel, trap, tables)


def mutate() -> int:
    fill, rel, trap = read(FILL, None), read(REL, None), read(TRAP, None)
    tables = pawncut.load_tables(read(pawncut.MATH, None), read(pawncut.UL, None))
    faults = {
        "no humanlike branch (the band for all)": lambda: check(fill.replace("p.RaceProps.Humanlike)", "p.RaceProps.Humanlike && false)", 1), rel, trap, tables),
        "humanlike branch returns the band": lambda: check(fill.replace("return RM_RelativeRulesMath.HumanlikeHeightMetres(p.BodySize * m * m);", "return RM_RelativeRulesMath.HeightMetres(1);", 1), rel, trap, tables),
        "height straight in body size": lambda: check(fill, rel.replace("return HeightByBand[2] * (float)Math.Sqrt(b);", "return HeightByBand[2] * b;", 1), trap, tables),
        "a person no longer 1.75 m": lambda: check(fill, rel.replace("1.75f, 2.5f", "1.7f, 2.5f", 1), trap, tables),
    }
    missed = 0
    for name, f in faults.items():
        red = f()
        print(("RED   " if red else "MISSED") + f"  planted: {name}" + (f"  -> {red[0]}" if red else ""))
        missed += 0 if red else 1
    clean = run(None)
    print(("GREEN " if not clean else "RED   ") + " unplanted (the real build)")
    return 1 if missed or clean else 0


def dotnet() -> int:
    b = subprocess.run([sys.executable, str(REPO / "src/RimMandrake/Utils/winbuild.py"),
                        "src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj"], capture_output=True, text=True)
    if b.returncode != 0:
        print("UNMEASURED: the SelfTest did not build:\n" + b.stdout[-800:] + b.stderr[-400:])
        return 2
    exe = next((p for p in (Path.home() / ".dotnet/dotnet", Path("/mnt/c/Users/Mandrake/.dotnet/dotnet.exe"),
                            Path("/mnt/c/Program Files/dotnet/dotnet.exe")) if p.exists()), None)
    d = Path("/mnt/d/ClaudeWork/rimmandrake/build/FlowWorks/src/RimMandrake/FlowWorks/Source/SelfTest")
    if exe is None or not (d / "bin/Release/net8.0/RimMandrakeFlowWorks.SelfTest.dll").exists():
        print("UNMEASURED: no dotnet or no built SelfTest dll")
        return 2
    r = subprocess.run([str(exe), "bin/Release/net8.0/RimMandrakeFlowWorks.SelfTest.dll", "--only",
                        "Relative_humanlike_height_follows_body_size_not_rat_band,Relative_drowning_head_under_not_hole_depth,PawnCut_*"],
                       cwd=str(d), capture_output=True, text=True)
    print("\n".join(l for l in r.stdout.splitlines() if l.startswith(("ok", "FAIL", "fail")) or "passed" in l))
    return 0 if r.returncode == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rev", help="check the files as they are at this commit (the parent must be RED)")
    ap.add_argument("--mutate", action="store_true", help="plant each fault and require RED")
    ap.add_argument("--dotnet", action="store_true", help="also run the C# SelfTest cases on Windows dotnet")
    a = ap.parse_args()
    if a.mutate:
        return mutate()
    bad = run(a.rev)
    for b in bad:
        print("FAIL  " + b)
    rc = 1 if bad else 0
    if not bad:
        print("PASS  a humanlike's height follows its body size: a Jawa and a T3 droid show above 0.5 m of tar")
    if a.dotnet and rc == 0:
        rc = dotnet()
    return rc


if __name__ == "__main__":
    sys.exit(main())
