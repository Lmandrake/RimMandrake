#!/usr/bin/env python3
"""selftest for vanilla_beast_carriers.py — offline, fixtures only, plus a shape check of the shipped patch.

    python3 src/RimMandrake/Utils/selftest_vanilla_beast_carriers.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vanilla_beast_carriers as v  # noqa: E402

PATCH = os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "VanillaBeastExcision_Carriers.xml")
FAILS = []


def check(name, cond):
    print("%s  %s" % ("ok  " if cond else "FAIL", name))
    if not cond:
        FAILS.append(name)


OFF = {"Muffalo", "Alpaca"}
KR = {"Muffalo": "Muffalo", "Alpaca": "Alpaca", "BanthaK": "RSW_Bantha", "RSW_Bantha": "RSW_Bantha", "Beetle": "Beetle"}
groups = {"Vanillaish": [["Muffalo", "Alpaca"]], "Droids": [[]], "Hutt": [["BanthaK"]], "NoTrade": []}
allowed = {"Cave": ["Muffalo", "Beetle"], "Dunes": ["RSW_Bantha"], "Bare": []}

m = v.matrix(groups, allowed, KR, OFF)
check("NoTrade (no trader group) is not a row", "NoTrade" not in m["Cave"])
check("empty carriers never trade (Any over nothing is false)", not m["Cave"]["Droids"]["can_trade"])
check("official carrier reachable where allowed", m["Cave"]["Vanillaish"]["official"] == ["Muffalo"])
check("kind resolves to race before matching", m["Dunes"]["Hutt"]["can_trade"] and m["Dunes"]["Hutt"]["owned"] == ["RSW_Bantha"])
check("biome with empty allowedPackAnimals admits nobody", not any(c["can_trade"] for c in m["Bare"].values()))
check("no intersection, no caravan", not m["Dunes"]["Vanillaish"]["can_trade"])

added = {"RSW_Bantha": 2.0, "Beetle": 2.0}
g2, a2 = v.apply_patch(groups, allowed, added, [("Cave", "Muffalo")])
check("empty group stays empty (node modelled absent)", g2["Droids"] == [[]])
check("group already listing RSW_Bantha is skipped (the not() predicate)",
      v.apply_patch({"X": [["RSW_Bantha"]]}, {}, added, [])[0]["X"] == [["RSW_Bantha"]])
check("other groups gain the added kinds once", g2["Vanillaish"][0] == ["Muffalo", "Alpaca", "RSW_Bantha", "Beetle"])
check("removal applied", a2["Cave"] == ["Beetle"] and allowed["Cave"] == ["Muffalo", "Beetle"])
try:
    v.apply_patch(groups, allowed, {}, [("Cave", "Elephant")])
    check("remove matching nothing raises", False)
except ValueError:
    check("remove matching nothing raises", True)

m2 = v.matrix(g2, a2, KR, OFF)
lost, left = v.regressions(m, m2, ["Cave"])
check("no lost pair when owned carriers replace the cut", lost == [])
check("no official left in touched biome", left == [])
# a cut with no replacement must be caught
g3, a3 = v.apply_patch(groups, allowed, {}, [("Cave", "Muffalo")])
lost3, _ = v.regressions(m, v.matrix(g3, a3, KR, OFF), ["Cave"])
check("a cut that strands a faction is reported as lost", ("Cave", "Vanillaish") in lost3)

try:
    v.parse_patch('<Patch><Operation Class="PatchOperationReplace"><xpath>/Defs/X</xpath><value/></Operation></Patch>')
    check("unmodelled op refused", False)
except ValueError:
    check("unmodelled op refused", True)

pa, pr = v.parse_patch(open(PATCH, encoding="utf-8").read())
check("shipped patch: 8 owned carrier kinds, none official", len(pa) == 8 and not (set(pa) & {"Muffalo", "Alpaca", "Dromedary", "Elephant"}))
check("shipped patch: RM_LanternDeeps loses Muffalo and Alpaca",
      sorted(pr) == [("RM_LanternDeeps", "Alpaca"), ("RM_LanternDeeps", "Muffalo")])
check("shipped patch's not() guard names a kind it adds", "RSW_Bantha" in pa and "not(RSW_Bantha)" in v.ADD_XPATH)

print("%d/%d failed" % (len(FAILS), 19) if FAILS else "all passed")
sys.exit(1 if FAILS else 0)
