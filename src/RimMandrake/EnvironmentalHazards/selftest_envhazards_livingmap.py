#!/usr/bin/env python3
"""Offline selftest for EnvironmentalHazards static_checks + the SUMP_TAR_LIVING_SYSTEMS_1 living-map first script.

Green on the shipped tree; each deliberate break turns _living_map_findings red for its own reason.
Run: python3 src/RimMandrake/EnvironmentalHazards/selftest_envhazards_livingmap.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation as V  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


rd = lambda f: open(os.path.join(HERE, "Source", f), encoding="utf-8").read()
COMP, DREAD, MOD = rd("RM_MapComponent_SumpLivingMap.cs"), rd("RM_MapComponent_DreadField.cs"), V._settings_src()

bad = V.static_checks()
check("shipped tree: static_checks green", not bad, "; ".join(bad))
check("shipped living map green", V._living_map_findings(COMP, DREAD, MOD) == [])
check("sanity: all 12 constants parse", COMP.count("// PROVISIONAL") >= 12)


def red(name, needle, comp=COMP, dread=DREAD, mod=MOD):
    f = V._living_map_findings(comp, dread, mod)
    check("break: " + name, any(needle in x for x in f), "findings=%r" % f)


red("constant loses PROVISIONAL",
    "not marked PROVISIONAL", comp=COMP.replace("= 6;                 // PROVISIONAL: stalks per ring", "= 6;  // stalks per ring"))
red("crust sets before mice re-route", "fresh crust sets before mice",
    comp=COMP.replace("CrustSetTicks = 360000;", "CrustSetTicks = 1000;"))
red("margin can never reach crust", "mirrelin can never reach",
    comp=COMP.replace("MarginDelayTicks = 120000;", "MarginDelayTicks = 999999;"))
red("tick ignores the toggle", "not gated",
    comp=COMP.replace("if (!RM_EnvironmentalHazardsSettings.sumpLivingMapEnabled || !BiomeCarriesSumpFlora())",
                      "if (!BiomeCarriesSumpFlora())"))
red("dread field never asks", "never consults IsFreshCrust",
    dread=DREAD.replace("living.IsFreshCrust(cell, Find.TickManager.TicksGame)", "false"))
red("tooltip drops PROVISIONAL", "does not say PROVISIONAL",
    mod=MOD.replace('list.Label("PROVISIONAL first-guess pacing', 'list.Label("First-guess pacing'))
red("proof hook removed", "proof hook", comp=COMP.replace("public static string ProofRewrite(string mode)", "static string X()"))
print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
