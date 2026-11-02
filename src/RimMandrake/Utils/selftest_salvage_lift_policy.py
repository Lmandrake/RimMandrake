#!/usr/bin/env python3
"""selftest_salvage_lift_policy.py - the one lift list answers what its design promises.

Checks design/RimMandrake/salvage_lift_policy.json against the committed census of every Core+DLC
building, the owner-ruled categories, invented modded defs (the rules must be categories, not a def
list), the design doc, and the ledger items that build it. When the game's Data folder is present
the census is also re-derived from it, so a stale census fails.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import salvage_lift_policy as slp

REPO = slp.REPO
DOC = os.path.join(REPO, "design", "RimMandrake", "salvage_lift_policy_2026-11-01.md")
BUILD_ITEMS = ["BATTLEFIELD_CAPTURE_BUILD_REDEPLOY", "SHIP_FIXTURES_WIDEN_MINIFY"]
fails = []


def check(cond, what):
    if not cond:
        fails.append(what)
        print("FAIL", what)


def row(name, **kw):
    base = dict(defName=name, pack="X", thingClass="Building", designation="", minifiedDef="", cells="1", flags="", comps="", modExtensions="", hasCost="")
    base.update(kw)
    return base


policy = slp.load_policy()
cats = {c["id"]: c for c in policy["categories"]}
rows = slp.read_census()
by = {r["defName"]: r for r in rows}

# shape
check(len(cats) == len(policy["categories"]), "duplicate category id")
for c in policy["categories"]:
    check(c["route"] in slp.ROUTES, "bad route " + c["id"])
    check(c["actor"] in slp.ACTORS, "bad actor " + c["id"])
    check(bool(c.get("why")), "no why " + c["id"])
    check((c["route"] == "none") == (c["actor"] == "none"), "route/actor disagree " + c["id"])
    if c["adds_minified"]:
        check(c["route"] == "minify_reinstall", "adds minifiedDef off the minify route " + c["id"])
check(policy["categories"][-1]["match"] == [{}], "the last category must catch everything")

# sanity probe: the census can see (the figures measured in convenience_replacements.md 1.3)
check(len(rows) == 588, "census rows %d != 588" % len(rows))
check(sum(1 for r in rows if r["designation"]) == 249, "buildable count moved")
check(sum(1 for r in rows if r["designation"] and r["minifiedDef"]) == 149, "buildable minifiable count moved")
check(len({(r["defName"]) for r in rows}) == len(rows), "a def appears twice in the census")

# every building lands exactly once, and the committed column is what the rules say
for r in rows:
    check(slp.classify(r, policy) == r["category"], "census column stale for " + r["defName"])
if os.path.isdir(slp.GAME_DATA):
    live = slp.facts_from_game()
    committed = [{k: r[k] for k in slp.FIELDS} for r in rows]
    check(live == committed, "census differs from the installed game's Data")

# owner-ruled categories
ruled = {
    "SHIP_FIXTURE": ["Cooler", "HydroponicsBasin", "CommsConsole", "HiTechResearchBench", "FabricationBench", "ChemfuelPoweredGenerator", "WoodFiredGenerator", "MoisturePump", "ChemfuelTank"],
    "TURRET": ["Turret_Autocannon", "Turret_Sniper", "Turret_RocketswarmLauncher", "Turret_MiniTurret", "Turret_Mortar"],
    "TRAP": ["TrapSpike", "TrapIED_HighExplosive"],
    "FORTIFICATION": ["Sandbags", "Barricade", "Fence", "FenceGate", "AncientTankTrap"],
    "HAZARD_NODE": ["AncientFuelNode", "UnstablePowerCell"],
    "STRUCTURE": ["Wall", "Door", "Autodoor", "PowerConduit", "WaterproofConduit", "HiddenConduit", "Vent", "GravshipHull"],
    "LOOP_ANCHOR": ["SolarGenerator", "WindTurbine", "GeothermalGenerator", "GroundPenetratingScanner"],
}
for category, names in ruled.items():
    for name in names:
        check(by[name]["category"] == category, "%s is %s, not %s" % (name, by[name]["category"], category))
check(sum(1 for r in rows if r["category"] == "SHIP_FIXTURE") == 9, "the fixture floor grew past nine")
check([c["id"] for c in policy["categories"] if c["degrade"] == "captured"] == ["TURRET"], "only a captured gun degrades (trap_renaissance 2b)")
for r in rows:
    c = cats[r["category"]]
    if c["adds_minified"] and c["actor"] == "droid":
        check(int(r["cells"]) <= policy["max_droid_cells"], "droid list holds an oversize def " + r["defName"])
    if r["category"] in ("STRUCTURE", "LOOP_ANCHOR", "PLACE_NOT_THING", "NATURAL"):
        check(not r["minifiedDef"], "a never-lift category holds a natively minifiable def " + r["defName"])
for category in ("TRAP", "TURRET", "FORTIFICATION", "HAZARD_NODE"):
    check(cats[category]["actor"] == "colonist_after_claim", category + " must stay an earned act (claim first)")
check(cats["HEAVY_MACHINE"]["actor"] == "droid", "the droid-only class lost its gate")

# a route the engine would refuse is no route: claimable=false defs need the grant, and every
# scrap row must be deconstructible or be granted it (measured: most ancient defs are neither)
for r in rows:
    c = cats[r["category"]]
    flags = r["flags"].split(";")
    if c["actor"] == "colonist_after_claim" and r["category"] != "KIT" and c["route"] == "minify_reinstall" and "noClaim" in flags:
        check("claimable" in c["grants"], r["defName"] + " cannot be claimed and its category grants nothing")
    if c["route"] == "scrap_for_yield":
        check("noDeconstruct" not in flags or "deconstructible" in c["grants"], r["defName"] + " is on the scrap route but vanilla forbids deconstructing it")
        check("alwaysDeconstructible" in c["grants"] or "noClaim" not in flags, r["defName"] + " can be neither claimed nor deconstructed")
check(by["AncientTankTrap"]["category"] == "FORTIFICATION" and "noClaim" in by["AncientTankTrap"]["flags"], "the probe for the claim gap went blind")
check(by["AncientBlastDoor"]["category"] == "RUIN_FIXED", "set dressing leaked onto the scrap route")
check(by["AncientRustedTruck"]["category"] == "HULK" and by["AncientWarwalkerTorso"]["category"] == "HULK", "a hulk fell out of the strip route")

# the rules are categories: invented modded defs land by structure, not by name
cases = [
    (row("Mod_PlasmaTurret", thingClass="Building_TurretGun", designation="Security", cells="4"), "TURRET"),
    (row("Mod_BearTrap", thingClass="Building_TrapDamager", designation="Security"), "TRAP"),
    (row("Mod_Sandwall", designation="Security"), "FORTIFICATION"),
    (row("Mod_Press", designation="Production", cells="6"), "HEAVY_MACHINE"),
    (row("Mod_Press2", designation="Production", cells="6", minifiedDef="MinifiedThing"), "KIT"),
    (row("Mod_Hangar", designation="Production", cells="25"), "LOOP_ANCHOR"),
    (row("RM_Hulk", comps="RM_CompProperties_SalvageLoot", cells="20"), "WRECK"),
    (row("RM_WM_Wreck", designation="Production", modExtensions="WreckedMachineGrade:Wrecked"), "WRECKED_TIER"),
    (row("Mod_Relic"), "UNLISTED"),
    (row("Mod_GateMachine", designation="Security", thingClass="Building_Door"), "HEAVY_MACHINE"),
    (row("Mod_Tank", designation="Security", cells="16"), "LOOP_ANCHOR"),
    (row("RM_BuildableHulk", comps="RM_CompProperties_SalvageLoot", designation="Production", cells="4"), "WRECK"),
]
for fake, expected in cases:
    check(slp.classify(fake, policy) == expected, "%s classified %s, expected %s" % (fake["defName"], slp.classify(fake, policy), expected))

# the evaluator can fail: reversing the order must change answers, and an unknown field must raise
flipped = dict(policy, categories=list(reversed(policy["categories"])))
check(any(slp.classify(r, flipped) != r["category"] for r in rows), "order does not matter: the instrument is blind")
try:
    slp.classify(row("x"), dict(policy, categories=[dict(policy["categories"][0], match=[{"nonsense": 1}])]))
    check(False, "an unknown match field passed silently")
except ValueError:
    pass

# the design states the routes, the droid's role and the one list
if not os.path.exists(DOC):
    check(False, "design doc missing")
else:
    with open(DOC, encoding="utf-8") as f:
        text = f.read()
    for c in policy["categories"]:
        check("`%s`" % c["id"] in text, "design omits category " + c["id"])
    for needle in ("## The hauler droid's role", "salvage_lift_policy.json", "BATTLEFIELD_CAPTURE_BUILD_REDEPLOY", "SHIP_FIXTURES_WIDEN_MINIFY", "`RM_Lift_"):
        check(needle in text, "design omits " + needle)

# the build items exist and point at the design
filed = {}
for path in glob.glob(os.path.join(REPO, "infrastructure", "state", "ledger", "events", "*.jsonl")):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if '"file"' not in line:
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("id") in BUILD_ITEMS:
                filed[event["id"]] = line
for item in BUILD_ITEMS:
    check(item in filed, item + " not filed")
    check("salvage_lift_policy_2026-11-01.md" in filed.get(item, ""), item + " does not point at the design")

print("selftest_salvage_lift_policy: %s (%d rows, %d categories)" % ("FAIL %d" % len(fails) if fails else "PASS", len(rows), len(cats)))
sys.exit(1 if fails else 0)
