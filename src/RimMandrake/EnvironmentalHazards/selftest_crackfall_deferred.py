#!/usr/bin/env python3
"""MIRRELBOLE_FIX_TICK_NRE_THIRTY_FIVE_TIMES: RM_CompCrackFall never fells inside Plant.TickLong.

Vanilla Plant.TickLong runs comps in base.TickLong(), then reads base.Map with no second Destroyed check, so a comp that
destroys its plant is the NRE under PlantUtility.GrowthSeasonNow (35 times in session ee0fbaa8).
Green on the shipped tree; each deliberate break turns _crackfall_findings red for its own reason.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402
import prove_crackfall_deferred as P  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


SRC = open(os.path.join(HERE, "Source", "RM_CompCrackFall.cs"), encoding="utf-8").read().replace("\r\n", "\n")
DUE = "tree.Map.GetComponent<RM_MapComponent_DeferredTreeFall>()?.Enqueue(tree);"
check("shipped source green", V._crackfall_findings(SRC) == [], repr(V._crackfall_findings(SRC)))


def red(name, needle, src):
    check("sanity: the break changed the source: " + name, src != SRC)
    f = V._crackfall_findings(src)
    check("break: " + name, any(needle in x for x in f), "findings=%r" % f)


red("the fell goes back inside the tick", "inside the tick",
    SRC.replace(DUE, "RM_TreeFallUtility.FellTree(tree, Rot4.Random, RM_TreeFallUtility.FallCause.Cracked);"))
red("the comp stops queueing", "never queues", SRC.replace(DUE, ""))
red("the drain never fells", "never fells", SRC.replace(
    "RM_TreeFallUtility.FellTree(tree, Rot4.Random, RM_TreeFallUtility.FallCause.Cracked);\n                }\n            }\n            draining.Clear();",
    "}\n            }\n            draining.Clear();"))
red("the countdown goes negative again", "negative",
    SRC.replace("warnTicksRemaining = Mathf.Max(0, warnTicksRemaining - elapsedTicks);", "warnTicksRemaining -= elapsedTicks;"))
red("the proof hook is removed", "proof hook", SRC.replace("public static string Stage(string unused)", "static string X()"))

check("judge: a clean run passes", P.judge("STAGED at (1, 0, 1)", "READ felled=True")[0] == 0)
check("judge: a tree still standing fails", P.judge("STAGED at (1, 0, 1)", "READ felled=False")[0] == 1)
check("judge: a throw in the tick fails", P.judge("FAIL: Plant.TickLong threw NullReferenceException", "")[0] == 1)
check("judge: no map is unmeasured", P.judge("UNMEASURED: no current map", "")[0] == 2)
check("judge: a silent probe is unmeasured", P.judge("", "")[0] == 2)

dll = os.path.join(HERE, "Assemblies", "RimMandrake.EnvironmentalHazards.dll")
blob = open(dll, "rb").read()
check("the committed DLL holds the deferred fall", b"RM_MapComponent_DeferredTreeFall" in blob)
check("the committed DLL holds the proof hook", b"RM_CrackFallProof" in blob)

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
