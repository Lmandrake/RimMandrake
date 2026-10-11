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
SADDLES = os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "PackAnimals_RestoreSaddles.xml")
FAILS = []
RAN = []


def check(name, cond):
    RAN.append(name)
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

# PACK_ANIMALS_RESTORE_EMPTY_SADDLES: the allowedPackAnimals conditional shape
g4, a4 = v.apply_patch(groups, allowed, {}, [], [("Bare", "RSW_Bantha"), ("Dunes", "RSW_Bantha")])
check("pack add fills an empty biome and opens it", a4["Bare"] == ["RSW_Bantha"]
      and v.matrix(g4, a4, KR, OFF)["Bare"]["Hutt"]["can_trade"])
check("pack add of an already-allowed race is a no-op", a4["Dunes"] == ["RSW_Bantha"])
try:
    v.apply_patch(groups, allowed, {}, [], [("Nowhere", "RSW_Bantha")])
    check("pack add on an unknown biome raises", False)
except ValueError:
    check("pack add on an unknown biome raises", True)
COND = ('<Patch><Operation Class="PatchOperationConditional"><xpath>/Defs/BiomeDef[defName="B"]/allowedPackAnimals</xpath>'
        '<match Class="PatchOperationAdd"><xpath>/Defs/BiomeDef[defName="B"]/allowedPackAnimals</xpath>'
        '<value><li>%s</li></value></match><nomatch Class="PatchOperationAdd"><xpath>/Defs/BiomeDef[defName="B"]</xpath>'
        '<value><allowedPackAnimals><li>%s</li></allowedPackAnimals></value></nomatch></Operation></Patch>')
check("conditional parsed to pack adds", v.parse_patch(COND % ("X", "X"))[2] == [("B", "X")])
try:
    v.parse_patch(COND % ("X", "Y"))
    check("conditional whose branches disagree refused", False)
except ValueError:
    check("conditional whose branches disagree refused", True)

pa, pr, pk = v.parse_patch(open(PATCH, encoding="utf-8").read())
pk_ = v.kinds(pa)
check("shipped patch: 9 owned carrier kinds, none official, no RM_ (those moved to the free tier)",
      len(pk_) == 9 and not (set(pk_) & {"Muffalo", "Alpaca", "Dromedary", "Elephant"}) and not any(k.startswith("RM_") for k in pk_))
sa, sr, sk = v.parse_patch(open(SADDLES, encoding="utf-8").read())
check("saddles patch: only pack adds, every race carried by the carriers patch", not sa and not sr and sk
      and {r for _, r in sk} <= set(pk_))
check("shipped patch: RM_LanternDeeps keeps Muffalo and Alpaca (its beetles were cut; no removal strands it)", pr == [])
check("shipped patch's not() guard names a kind it adds", pa == [("RSW_Bantha", pk_)] and "not(RSW_Bantha)" in v.ADD_XPATH)

# PACK_ANIMALS_RESTORE_EMPTY_SADDLES free tier (card 2026-10-11): the gate -> conditional -> add shape
FREE = ('<Patch><Operation Class="RimMandrake.Biomes.RM_PatchOperationBiomesSettingGate"><setting>ownedCaravanCarriers</setting>'
        '<match Class="PatchOperationConditional"><xpath>/Defs/FactionDef/pawnGroupMakers/li[kindDef="Trader"]/carriers[not(%s)]</xpath>'
        '<match Class="PatchOperationAdd"><xpath>/Defs/FactionDef/pawnGroupMakers/li[kindDef="Trader"]/carriers[not(%s)]</xpath>'
        '<value><RM_Tirbak>2</RM_Tirbak><RM_Vellak>2</RM_Vellak></value></match></match></Operation></Patch>')
check("free-tier gate+conditional parsed to one guarded carriers add",
      v.parse_patch(FREE % ("RM_Tirbak", "RM_Tirbak"))[0] == [("RM_Tirbak", {"RM_Tirbak": 2.0, "RM_Vellak": 2.0})])
try:
    v.parse_patch(FREE % ("RM_Ghost", "RM_Ghost"))
    check("a not() sentinel the add does not add is refused (not idempotent)", False)
except ValueError:
    check("a not() sentinel the add does not add is refused (not idempotent)", True)
g5, _ = v.apply_patch({"V": [["Muffalo"]], "U": [["RM_Tirbak"]]}, {}, [("RM_Tirbak", {"RM_Tirbak": 2.0, "RM_Vellak": 2.0})], [])
check("guarded add skips a group already listing the sentinel, fills the others", g5 == {"V": [["Muffalo", "RM_Tirbak", "RM_Vellak"]], "U": [["RM_Tirbak"]]})
FKR = {"Muffalo": "Muffalo", "RM_Tirbak": "RM_Tirbak", "RM_Vellak": "RM_Vellak", "RM_Ghost": "RM_Ghost"}
fg = {"OutlanderCivil": [["Muffalo"]], "TribeCivil": [["Muffalo"]]}
fa = {"RM_WeepingStones": ["RM_Tirbak", "RM_Vellak"], "RM_Plain": ["Muffalo"], "RM_Bare": []}
src_k = {"RM_Tirbak": "RM_Tirbak", "RM_Vellak": "RM_Vellak"}
lines, bad = v.free_tier_core(fg, fa, FKR, {"Muffalo"}, src_k, [FREE % ("RM_Tirbak", "RM_Tirbak")])
check("free tier: the carriers file opens the Weeping Stones to every vanilla trader", bad == []
      and any("RM_WeepingStones" in l and "0 -> 2 of 2" in l for l in lines))
_, bad = v.free_tier_core(fg, fa, FKR, {"Muffalo"}, src_k, [])
check("free tier planted: no carriers file -> the Weeping Stones reads closed", any("RM_WeepingStones" in b for b in bad))
_, bad = v.free_tier_core(fg, fa, FKR, {"Muffalo"}, {"RM_Tirbak": "RM_Tirbak"}, [FREE % ("RM_Tirbak", "RM_Tirbak")])
check("free tier planted: a carrier kind cut from src is reported (the RM_BovineBeetle trap)", any("not defined in src" in b for b in bad))
sk_now = v.src_pawnkinds()
check("src kind census sanity: sees RM_Tirbak, RM_Vaalok and RSW_Bantha; not RM_BovineBeetle (cut 2026-10-05)",
      {"RM_Tirbak", "RM_Vaalok", "RSW_Bantha"} <= set(sk_now) and "RM_BovineBeetle" not in sk_now)
ff = v.free_tier_files()
fk = v.kinds([a for f in ff for a in v.parse_patch(open(f, encoding="utf-8").read())[0]])
check("shipped free-tier files: RM_Tirbak, RM_Vellak, RM_Vaalok, each defined in src", sorted(fk) == ["RM_Tirbak", "RM_Vaalok", "RM_Vellak"]
      and set(fk) <= set(sk_now))
check("no Utinni carriers list still names a cut kind", all(k in sk_now for k in pk_))

print("%d/%d failed" % (len(FAILS), len(RAN)) if FAILS else "all %d passed" % len(RAN))
sys.exit(1 if FAILS else 0)
