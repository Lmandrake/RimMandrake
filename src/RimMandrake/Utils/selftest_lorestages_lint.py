#!/usr/bin/env python3
"""Planted-defect selftest for lint_lorestages_defs.py: clean on the real tree, then one planted break at a time (in memory, nothing
written) must be caught with the expected ERROR/WARN kind. A lint that cannot fail proves nothing.

    python3 src/RimMandrake/Utils/selftest_lorestages_lint.py
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_lorestages_defs as L  # noqa: E402

LAD = "RimUtinni/ScarlandsLadder/Defs/LoreStageTableDefs/RUT_ScarlandsLadder.xml"
M = "RimMandrake/LoreStages/Source/"
PLANTS = [
    # (label, store, file, old, new, expected "ERROR ls-x" / "WARN  ls-x" prefix)
    ("table child typo", "xml", LAD, "<maxStage>5</maxStage>", "<maxStag>5</maxStag>", "ERROR ls-fields"),
    ("target child typo", "xml", LAD, "<defType>BiomeDef</defType>", "<defTyp>BiomeDef</defTyp>", "ERROR ls-fields"),
    ("rung child typo", "xml", LAD, "<stage>1</stage>", "<stag>1</stag>", "ERROR ls-fields"),
    ("stage not an integer", "xml", LAD, "<stage>3</stage>", "<stage>three</stage>", "ERROR ls-fields"),
    ("maxStage not an integer", "xml", LAD, "<maxStage>5</maxStage>", "<maxStage>five</maxStage>", "ERROR ls-fields"),
    ("duplicate rung", "xml", LAD, "<stage>2</stage>\n            <text>Crater fields", "<stage>1</stage>\n            <text>Crater fields", "ERROR ls-rules"),
    ("negative rung", "xml", LAD, "<stage>1</stage>", "<stage>-1</stage>", "ERROR ls-rules"),
    ("rung above maxStage", "xml", LAD, "<stage>5</stage>", "<stage>6</stage>", "ERROR ls-rules"),
    ("rung with no text", "xml", LAD, "<stage>3</stage>\n            <text>", "<stage>3</stage>\n            <txt>", "ERROR ls-fields"),
    ("no defType", "xml", LAD, "<defType>BiomeDef</defType>", "<defType></defType>", "ERROR ls-rules"),
    ("target names a def that does not exist", "xml", LAD, "<defName>RUT_Scarlands</defName>\n        <field>description</field>", "<defName>RUT_Scarland</defName>\n        <field>description</field>", "ERROR ls-target"),
    ("field typo", "xml", LAD, "<field>settleWarning</field>", "<field>settleWarnin</field>", "ERROR ls-target"),
    ("field is not a string", "xml", LAD, "<field>description</field>", "<field>workerClass</field>", "ERROR ls-target"),
    ("R25: names the Rakata", "xml", LAD, "<stage>5</stage>\n            <text>", "<stage>5</stage>\n            <text>The Rakata built this. ", "ERROR ls-r25"),
    ("R25: names the Assailants", "xml", LAD, "<stage>1</stage>\n            <text>", "<stage>1</stage>\n            <text>The Assailants fell here. ", "ERROR ls-r25"),
    ("kernel imports Verse", "cs", M + "Kernel/RM_LoreStageKernel.cs", "using System.Collections.Generic;", "using System.Collections.Generic;\nusing Verse;", "ERROR ls-kernel"),
    ("mod csproj drops the kernel", "csproj", M + "RM_LoreStages.csproj", '<Compile Include="Kernel\\RM_LoreStageKernel.cs" />', "", "ERROR ls-kernel"),
    ("applier stops using the kernel", "cs", M + "LoreStageApplier.cs", "RM_LoreStageKernel.ChooseRung(", "ChooseRungX(", "ERROR ls-kernel"),
    ("table def stops using the kernel", "cs", M + "RM_LoreStageTableDef.cs", "RM_LoreStageKernel.RungProblems(", "RungProblemsX(", "ERROR ls-kernel"),
    ("game component stops clamping", "cs", M + "GameComponent_LoreStage.cs", "RM_LoreStageKernel.ClampStage(", "ClampX(", "ERROR ls-kernel"),
    ("a placeholder warning is flagged", "xml", LAD, "<stage>1</stage>\n            <text>Crater", "<stage>1</stage>\n            <text>[[PLACEHOLDER stage 1]] Crater", "WARN  ls-placeholder"),
]


def dup_ladder(inp):
    """a second ladder file that targets the same field and reuses the table defName"""
    inp["xml"]["Fake/Dup.xml"] = inp["xml"][LAD]


def main():
    inp = L.collect()
    errs, warns, counts = L.check(inp)
    bad = 0
    ok = not errs and counts["tables"] >= 1 and counts["rungs"] >= 5 and counts["engine fields checked"] >= 2
    print(("ok   " if ok else "FAIL ") + "real tree is clean (%s)" % counts + ("" if ok else " " + "; ".join(errs[:2])))
    bad += not ok
    for label, store, rel, old, new, want in PLANTS:
        i2 = copy.deepcopy(inp)
        d = i2[store]
        if rel not in d or old not in d[rel]:
            print("FAIL %s: pattern not found in %s" % (label, rel))
            bad += 1
            continue
        d[rel] = d[rel].replace(old, new, 1)
        e2, w2, _ = L.check(i2)
        hit = any(x.startswith(want) for x in (e2 + w2))
        print(("ok   " if hit else "FAIL ") + label + ("" if hit else " | wanted %s, got %s" % (want, (e2 + w2)[:2])))
        bad += not hit
    # a second file defining the same table and addressing the same fields: duplicate defName (ERROR) and field collisions (WARN)
    i2 = copy.deepcopy(inp)
    dup_ladder(i2)
    e2, w2, _ = L.check(i2)
    hit = any(x.startswith("ERROR ls-ladder") for x in e2) and any(x.startswith("WARN  ls-collision") for x in w2)
    print(("ok   " if hit else "FAIL ") + "duplicate table + field collision" + ("" if hit else " | got %s" % (e2 + w2)[:3]))
    bad += not hit
    n = len(PLANTS) + 2
    print("lorestages lint planted-defect selftest: %d/%d ok" % (n - bad, n))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
