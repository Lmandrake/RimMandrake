#!/usr/bin/env python3
"""RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES (owner cards 2026-11-12 23:52 and 2026-11-13 00:15 PST: "Delete it";
"Wet from -> above 5 cm"): water has ONE number, exact decilitres / metres. This source guard keeps "fill N" from coming back:

- no `FillAt(`, `TrySetDriverFill(` or the Mod Setting `levelExactEnabled` anywhere in src/ C# (comments aside);
- the save holds one water grid (`RM_excavationWaterGrid`), never `RM_excavationFillGrid` / `RM_excavationPartGrid` /
  `RM_levelModel`;
- the kernel's working split (`fillGrid` / `partGrid`) is named only in RM_MapComponent_Excavation.cs;
- every yes/no "is it wet?" reader asks `WetAt` (wet = above 5 cm, `WetDl = U / 10`).

Each check is shown able to fail on a planted break. Run: python3 src/RimMandrake/FlowWorks/selftest_flowworks_one_water_number.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))   # src/RimMandrake
FW = os.path.join(HERE, "Source")
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def code(text):
    """C# text with // and /* */ comments and string literals blanked (a comment may name the old API)."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r'@"(?:[^"]|"")*"', '""', text)
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    return re.sub(r"//[^\n]*", " ", text)


def cs_files():
    for dp, _, files in os.walk(SRC):
        p = dp.replace("\\", "/")
        if "/obj/" in p + "/" or "/bin/" in p + "/":
            continue
        for f in files:
            if f.endswith(".cs"):
                yield os.path.join(dp, f)


GONE = re.compile(r"\b(FillAt|TrySetDriverFill|TrySetDriverFillOutcome)\s*\(|RimMandrakeFlowWorksSettings\.levelExactEnabled\b"
                  r"|\bstatic bool levelExactEnabled\b|\bRM_MapComponent_Excavation\.LevelExact\b|\bstatic bool LevelExact\b")
SPLIT = re.compile(r"\b(fillGrid|partGrid)\b")
OLD_SAVE = re.compile(r'"(RM_excavationFillGrid|RM_excavationPartGrid|RM_levelModel)"')


def gone_hits(name, text):
    hits = [m.group(0) for m in GONE.finditer(code(text))]
    if "/SelfTest/" in name.replace("\\", "/"):
        hits = [h for h in hits if "LevelExact" not in h]   # PumpOutflowHarness's own engine double
    return hits


def split_hits(name, text):
    if os.path.basename(name) == "RM_MapComponent_Excavation.cs":
        return []
    return [m.group(0) for m in SPLIT.finditer(code(text))]


gone, split, saves = [], [], []
for p in cs_files():
    t = open(p, encoding="utf-8", errors="replace").read()
    rel = os.path.relpath(p, SRC)
    gone += ["%s: %s" % (rel, h) for h in gone_hits(p, t)]
    split += ["%s: %s" % (rel, h) for h in split_hits(p, t)]
    saves += ["%s: %s" % (rel, m.group(1)) for m in OLD_SAVE.finditer(t)]
check("no FillAt / TrySetDriverFill / levelExactEnabled setting / LevelExact in src C#", gone == [], "; ".join(gone[:12]))
check("fillGrid/partGrid named only in RM_MapComponent_Excavation.cs", split == [], "; ".join(split[:12]))
check("no old save field (RM_excavationFillGrid/PartGrid/RM_levelModel)", saves == [], "; ".join(saves))

ex = open(os.path.join(FW, "RM_MapComponent_Excavation.cs"), encoding="utf-8").read()
check("the save holds one water grid", '"RM_excavationWaterGrid"' in ex)
check("wet = above 5 cm (WetDl = U / 10)", re.search(r"public const long WetDl = RM_LevelSolve\.U / 10;", ex) is not None)
check("WetAt compares water with WetDl", "WaterDl(i) > WetDl" in ex)
mod = open(os.path.join(FW, "RimMandrakeFlowWorksMod.cs"), encoding="utf-8").read()
check("the Mod Setting 'Water stands exactly level' is gone", "Water stands exactly level" not in mod)

# every yes/no reader of 'is liquid standing here' asks WetAt (owner card: wet from above 5 cm)
READERS = {
    "RM_LiquidFire.cs": r"if \(!ex\.WetAt\(c\)\)",
    "RM_SlimeSlip.cs": r"ex\.IsExcavated\(c\) && ex\.WetAt\(c\);",
    "Superdeep/RM_PitStepCost.cs": r"\(to > 0 && eng\.WetAt\(c\)\)",
    "Superdeep/RM_PitScorch.cs": r"eng\.ExcavatedDepthAt\(c\) == 0 \|\| eng\.WetAt\(c\)",
    "Superdeep/RM_FlowDoors.cs": r"bool wet = eng\.WetAt\(cell\);",
    "Pits/Suspension/RM_SuspensionPatches.cs": r"sunkenBridges && !ex\.WetAt\(c\);",
    "Pits/Suspension/Designator_SuspensionBridge.cs": r"bool dryClear = !ex\.WetAt\(c\)",
    "Swale/RM_Swale.cs": r"engine\.WetAt\(cell\) && fluid != null",
}
for rel, pat in READERS.items():
    t = open(os.path.join(FW, rel), encoding="utf-8").read()
    check("reader %s asks WetAt" % rel, re.search(pat, t) is not None, pat)

# ── the guard can fail ──
check("break: a FillAt call -> red", gone_hits("X.cs", "int f = ex.FillAt(c);") != [])
check("break: a bool TrySetDriverFill -> red", gone_hits("X.cs", "ex.TrySetDriverFill(c, 2, f);") != [])
check("break: the setting back -> red", gone_hits("X.cs", "public static bool levelExactEnabled = true;") != [])
check("break: a reader asking the setting -> red", gone_hits("X.cs", "if (RM_MapComponent_Excavation.LevelExact) { }") != [])
check("stay green: the kernel's own field", gone_hits("X.cs", "flowKernel.levelExactEnabled = true;") == [])
check("stay green: FillAt in a comment", gone_hits("X.cs", "// FillAt(c) was whole notches") == [])
check("stay green: FillAtFaucet (another name)", gone_hits("X.cs", "JobDef RM_FillAtFaucet;") == [])
check("break: fillGrid read outside the component -> red", split_hits("RM_Other.cs", "byte f = fillGrid[i];") != [])
check("break: old save field -> red", OLD_SAVE.search('Scribe_Values.Look(ref m, "RM_levelModel", 0);') is not None)
print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
