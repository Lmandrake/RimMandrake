#!/usr/bin/env python3
"""selftest_salvage_lift_policy.py - the one lift list answers what its design promises.

Checks design/RimMandrake/salvage_lift_policy.json against the committed census of every Core+DLC
building, the owner-ruled categories, invented modded defs (the rules must be categories, not a def
list), the design doc, and the ledger items that build it. When the game's Data folder is present
the census is also re-derived from it, so a stale census fails.
"""
import copy
import glob
import json
import os
import re
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

# ---- the pin: the design's answer, written here by hand so that a change to the JSON alone cannot agree with itself ----
# id, in rule order: route, actor, adds_minified, degrade, grants, census rows
PIN = {
    "NATURAL": ("none", "none", False, "none", [], 24),
    "SHIP_FIXTURE": ("minify_reinstall", "colonist", True, "none", [], 9),
    "WRECKED_TIER": ("minify_reinstall", "droid", True, "none", [], 0),
    "WRECK": ("scrap_for_yield", "colonist", False, "none", [], 0),
    "TRAP": ("minify_reinstall", "colonist_after_claim", True, "none", ["claimable"], 11),
    "TURRET": ("minify_reinstall", "colonist_after_claim", True, "captured", ["claimable"], 12),
    "FORTIFICATION": ("minify_reinstall", "colonist_after_claim", True, "none", ["claimable"], 10),
    "HAZARD_NODE": ("minify_reinstall", "colonist_after_claim", True, "none", ["claimable"], 4),
    "KIT": ("minify_reinstall", "colonist_after_claim", False, "none", [], 163),
    "STRUCTURE": ("none", "none", False, "none", [], 22),
    "LOOP_ANCHOR": ("none", "none", False, "none", [], 9),
    "PLACE_NOT_THING": ("none", "none", False, "none", [], 22),
    "HEAVY_MACHINE": ("minify_reinstall", "droid", True, "none", [], 31),
    "HULK": ("scrap_for_yield", "colonist", False, "none", ["deconstructible", "alwaysDeconstructible"], 30),
    "RUIN_FIXED": ("none", "none", False, "none", [], 26),
    "RUIN": ("scrap_for_yield", "colonist", False, "none", ["alwaysDeconstructible"], 105),
    "UNLISTED": ("none", "none", False, "none", [], 110),
}
PIN_FIELDS = ("route", "actor", "adds_minified", "degrade", "grants")
# the design table's words for the two columns that carry the decision
ROUTE_WORD = {"none": "none", "minify": "minify_reinstall", "scrap": "scrap_for_yield"}
ACTOR_WORD = {"nobody": "none", "any colonist": "colonist", "colonist": "colonist", "droid only": "droid", "colonist after claim": "colonist_after_claim"}
# what each row must say it holds
HOLDS = {
    "NATURAL": "rock and ore", "SHIP_FIXTURE": "the nine fixtures", "WRECKED_TIER": "WreckedMachines tier 1", "WRECK": "our wreck families",
    "TRAP": "every `Building_Trap*`", "TURRET": "every `Building_Turret*`", "FORTIFICATION": "sandbags, barricades, fences",
    "HAZARD_NODE": "unstable fuel node", "KIT": "everything already minifiable", "STRUCTURE": "walls, doors, conduits, vents",
    "LOOP_ANCHOR": "scanners and anything of 10+ cells", "PLACE_NOT_THING": "spots, graves, fires, torches",
    "HEAVY_MACHINE": "every other buildable of up to 9 cells", "HULK": "ancient vehicles and war machines",
    "RUIN_FIXED": "ancient set dressing", "RUIN": "ruin furniture, broken ancient guns", "UNLISTED": "quest, entity, archotech",
}
# section heading -> (word floor, sentences that must stand verbatim, whitespace folded)
SECTIONS = {
    "The answer": (200, [
        "A building is *lifted* (the vanilla Uninstall designation, a crate, reinstall), *scrapped* (the Deconstruct designation, yield through the one salvage rule) or *left alone*.",
        "**The list is rules, not defs.**",
        "*\"no curation sheet is needed. The scope is a CATEGORY, not a list.\"*",
        "holds ordered category rules, first match wins",
        "**It only adds.** A def that declares its own `minifiedDef` keeps it.",
        "**Enemy gear is earned.** Battlefield categories need a claim first",
        "Only the droid lifts from a live site, and it pays for that with a `TakingEvent`.",
    ]),
    "The categories": (300, [
        "**Ruins scrap, they do not lift.**",
        "**Hulks are the heart of it, and vanilla locks them.**",
        "**The rest of the machines stay colonist-immovable.**",
    ]),
    "The hauler droid's role": (180, [
        "The droid is the only way to lift what colonists cannot, and the only way to lift from a site you do not hold.",
        "**Reach.** `HEAVY_MACHINE` and `WRECKED_TIER` are droid-only",
        "It may also take anything a colonist may lift.",
        "**Live targets.** No claim and no pacified map: it works under the owner's nose and fires `TakingEvent(Act=Strip)`",
        "**Carrying.** Crates are ordinary items; any hauler brings them home.",
        "A colonist may carry and install a stolen crate; only the lift is gated.",
        "**Not the stripper.** Wrecks are stripped by the separate strip droid",
        "`FloatMenuOptionProvider_TheftHaulUninstall` gates on `building.def.Minifiable`",
        "The fix is to give the droid classes a `minifiedDef` and take the colonist's Uninstall away from them",
    ]),
    "One list, one pass": (350, [
        "`salvage_lift_policy.json` is the source.",
        "nothing else states a membership.",
        "A Harmony prefix on `DefGenerator.GenerateImpliedDefs_PreResolve`.",
        "**Verdict first, writes after.** The pass classifies every def as authored, keeps the verdicts, then writes.",
        "Every def in a lift category gets the building tag `RM_Lift_<CATEGORY>` in `building.buildingTags`. That is the whole interface:",
        "**Grants.** `grants` fields are set on the def, for that category only.",
        "A toggle gates new lifting; it never removes the def fields",
        "| Colonist Uninstall | `RM_Lift_HEAVY_MACHINE`, `RM_Lift_WRECKED_TIER`, and any toggled-off category |",
        "| `RM_TheftHaulUninstall` | `Minifiable` |",
        "| Capture comp (WreckedMachines) | `RM_Lift_TURRET` |",
        "| Jawa disarm-and-take | `RM_Lift_TRAP` |",
        "| Scrap yield | `RM_Lift_RUIN`, `RM_Lift_WRECK` |",
    ]),
    "Capture, degraded": (200, [
        "Follow `convenience_replacements.md` §7 route (i): claim, then uninstall.",
        "The pass adds one comp to `TURRET` defs.",
        "`JobDriver_TheftHaulUninstall` sets the same mark before it minifies, because the droid never claims.",
    ]),
}
ALL_BUILD_ITEMS = BUILD_ITEMS + ["LIFT_PASS_BUILD_ONE_LIST", "THEFT_HAULER_WIDEN_MINIFY_GONE", "RUIN_SCRAP_BUILD_RUST_PAYS"]
# the only defs named like a wall, door, conduit or vent that the rules let off route none
LIFTABLE_LOOKALIKES = {"FenceGate": "owner-ruled fortification (trap_renaissance 2b)", "WallLamp": "a lamp, natively minifiable"}


def fold(text):
    return " ".join(text.split())


def section(text, heading):
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line == "## " + heading
            continue
        if inside:
            lines.append(line)
    return "\n".join(lines)


def policy_faults(p):
    """Everything wrong with a policy against the pin; the mutant battery below proves each one can fire."""
    out = []
    if [c["id"] for c in p["categories"]] != list(PIN):
        out.append("category set or rule order moved")
    if p.get("tag_prefix") != "RM_Lift_":
        out.append("tag_prefix moved")
    if p.get("max_droid_cells") != 9:
        out.append("max_droid_cells moved")
    for c in p["categories"]:
        for field, want in zip(PIN_FIELDS, PIN.get(c["id"], ())):
            if c.get(field) != want:
                out.append("%s.%s is %r, the design says %r" % (c["id"], field, c.get(field), want))
    return out


def census_faults(census, p):
    out = []
    route = {c["id"]: c["route"] for c in p["categories"]}
    for name, want in PIN.items():
        got = sum(1 for r in census if r["category"] == name)
        if got != want[5]:
            out.append("%s holds %d rows, pinned %d" % (name, got, want[5]))
    for r in census:
        looks = any(w in r["defName"].lower() for w in ("wall", "door", "conduit", "vent")) or any(w in r["thingClass"] for w in ("Door", "Vent"))
        if looks and r["defName"] not in LIFTABLE_LOOKALIKES and route.get(r["category"]) != "none":
            out.append("%s looks like a wall, door, conduit or vent and is on route %s" % (r["defName"], route.get(r["category"])))
    return out


def table_faults(text, p):
    """The design table, parsed cell by cell, against the policy: order, route, degrade, actor, what it holds."""
    out, seen = [], []
    by_id = {c["id"]: c for c in p["categories"]}
    for line in section(text, "The categories").splitlines():
        cell = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(cell) != 4 or not cell[0].startswith("`"):
            continue
        name = cell[0].strip("`")
        seen.append(name)
        c = by_id.get(name)
        if c is None:
            out.append("table row for unknown category " + name)
            continue
        words = [w.strip() for w in cell[1].replace("*", "").split(",")]
        if ROUTE_WORD.get(words[0]) != c["route"]:
            out.append("table route of %s is %r, the policy says %s" % (name, cell[1], c["route"]))
        if ("degraded" in words[1:]) != (c["degrade"] == "captured"):
            out.append("table degrade of %s is %r, the policy says %s" % (name, cell[1], c["degrade"]))
        actor = cell[2].replace("*", "").split(";")[0].strip()
        if ACTOR_WORD.get(actor) != c["actor"]:
            out.append("table actor of %s is %r, the policy says %s" % (name, cell[2], c["actor"]))
        if HOLDS[name] not in cell[3]:
            out.append("table row %s no longer says it holds %r" % (name, HOLDS[name]))
    if seen != [c["id"] for c in p["categories"]]:
        out.append("table rows are not the categories in rule order")
    return out


def prose_faults(text, p):
    """The sections the design owes: each must keep its substance, sentence by sentence, and agree with the policy."""
    out = []
    for heading, (floor, sentences) in SECTIONS.items():
        body = fold(section(text, heading))
        if len(body.split()) < floor:
            out.append("section %r has %d words, floor %d" % (heading, len(body.split()), floor))
        for sentence in sentences:
            if sentence not in body:
                out.append("section %r lost: %s" % (heading, sentence))
    by_id = {c["id"]: c for c in p["categories"]}
    droid = {c["id"] for c in p["categories"] if c["actor"] == "droid"}
    if set(re.findall(r"`([A-Z_]+)`", fold(section(text, "The hauler droid's role")).split(" are droid-only")[0])) != droid:
        out.append("the droid section's droid-only classes are not the policy's")
    one = section(text, "One list, one pass")
    tags = set(re.findall(r"`RM_Lift_([A-Z_]+)`", one))
    for name in tags:
        if by_id.get(name, {}).get("route", "none") == "none":
            out.append("the one-list section reads a tag with no lift or scrap route: " + name)
    for reader, want in (("Capture comp", lambda c: c["degrade"] == "captured"), ("Colonist Uninstall", lambda c: c["actor"] == "droid"),
                         ("Scrap yield", lambda c: c["route"] == "scrap_for_yield"), ("Jawa disarm", lambda c: c["route"] == "minify_reinstall")):
        for line in one.splitlines():
            if line.startswith("| " + reader):
                for name in re.findall(r"`RM_Lift_([A-Z_]+)`", line):
                    if name not in by_id or not want(by_id[name]):
                        out.append("%s reads %s, which the policy does not support" % (reader, name))
    build = section(text, "Build order")
    for item in ALL_BUILD_ITEMS:
        if "| `%s` |" % item not in build:
            out.append("build order omits " + item)
    return out


check(not policy_faults(policy), "policy against the pin: %s" % policy_faults(policy))
check(not census_faults(rows, policy), "census against the pin: %s" % census_faults(rows, policy))
for must_be_none in ("STRUCTURE", "LOOP_ANCHOR", "PLACE_NOT_THING", "NATURAL", "RUIN_FIXED", "UNLISTED"):
    check(cats[must_be_none]["route"] == "none" and cats[must_be_none]["actor"] == "none", must_be_none + " must lift nothing, by nobody")
doc_text = open(DOC, encoding="utf-8").read() if os.path.exists(DOC) else ""
check(not table_faults(doc_text, policy), "design table: %s" % table_faults(doc_text, policy))
check(not prose_faults(doc_text, policy), "design prose: %s" % prose_faults(doc_text, policy))
# the doc's one claim about our own code, read from that code
with open(os.path.join(REPO, "src", "RimMandrake", "RimProperty", "Source", "TheftHauler", "FloatMenuOptionProvider_TheftHaulUninstall.cs"), encoding="utf-8") as f:
    check("building.def.Minifiable" in f.read(), "the droid's gate moved: the design's defect section is stale")


# ---- the mutant battery: each clause goes red when it is broken, here and on every run ----
def mutated(mutate):
    p = copy.deepcopy(policy)
    mutate({c["id"]: c for c in p["categories"]}, p)
    return p


def must_redden(label, faults):
    check(bool(faults), "MUTANT SURVIVED: " + label)


OTHER = {"route": "scrap_for_yield", "actor": "droid", "adds_minified": None, "degrade": "captured", "grants": ["claimable", "x"]}
for name in PIN:
    for field in PIN_FIELDS:
        def flip(m, _p, name=name, field=field):
            m[name][field] = (not m[name][field]) if field == "adds_minified" else (OTHER[field] if m[name][field] != OTHER[field] else "minify_reinstall")
        must_redden("%s.%s" % (name, field), policy_faults(mutated(flip)))


def named(**fields):
    def apply(m, _p):
        for name, values in fields.items():
            m[name].update(values)
    return apply


for label, mutate in (
    ("walls lift", named(STRUCTURE=dict(route="minify_reinstall", actor="colonist", adds_minified=True))),
    ("fixture scraps", named(SHIP_FIXTURE=dict(route="scrap_for_yield", adds_minified=False))),
    ("ruin lifts", named(RUIN=dict(route="minify_reinstall", adds_minified=True))),
    ("wreck lifts", named(WRECK=dict(route="minify_reinstall"))),
    ("hulk left alone", named(HULK=dict(route="none", actor="none", grants=[]))),
    ("wrecked tier open to colonists", named(WRECKED_TIER=dict(actor="colonist"))),
    ("droid strips wrecks", named(WRECK=dict(actor="droid"))),
    ("rule order", lambda _m, p: p["categories"].reverse()),
    ("a category gone", lambda _m, p: p["categories"].pop(3)),
    ("droid cap", lambda _m, p: p.update(max_droid_cells=25)),
    ("tag prefix", lambda _m, p: p.update(tag_prefix="RM_X_")),
):
    must_redden(label, policy_faults(mutated(mutate)))

for name in PIN:
    moved = [dict(r, category="HULK" if r["category"] == name else r["category"]) for r in rows]
    if name != "HULK" and PIN[name][5]:
        must_redden("census count " + name, census_faults(moved, policy))
for name in ("Wall", "Door", "PowerConduit", "Vent", "AnimalFlap", "AncientHeatVent", "AncientFortifiedWall"):
    must_redden("a %s onto a lift route" % name, census_faults([dict(r, category="KIT" if r["defName"] == name else r["category"]) for r in rows], policy))

table = [line for line in section(doc_text, "The categories").splitlines() if line.startswith("| `")]
for line in table:
    cell = line.split("|")
    new_route = "scrap" if "scrap" not in cell[2] else "minify"
    must_redden("table route " + cell[1], table_faults(doc_text.replace(line, "|".join(cell[:2] + [" %s " % new_route] + cell[3:])), policy))
    new_actor = "nobody" if "nobody" not in cell[3] else "any colonist"
    must_redden("table actor " + cell[1], table_faults(doc_text.replace(line, "|".join(cell[:3] + [" %s " % new_actor] + cell[4:])), policy))
    must_redden("table holds " + cell[1], table_faults(doc_text.replace(line, "|".join(cell[:4] + [" things "] + cell[5:])), policy))
    must_redden("table row gone " + cell[1], table_faults(doc_text.replace(line + "\n", ""), policy))
must_redden("table degrade dropped", table_faults(doc_text.replace("minify, **degraded**", "minify"), policy))

for heading, (_floor, sentences) in SECTIONS.items():
    body = section(doc_text, heading)
    must_redden("section body gone: " + heading, prose_faults(doc_text.replace(body, "`RM_Lift_`\n"), policy))
    for sentence in sentences:
        must_redden("sentence gone: " + sentence, prose_faults(doc_text.replace(body, "\n" + fold(body).replace(sentence, "") + "\n"), policy))
must_redden("capture reads another tag", prose_faults(doc_text.replace("| Capture comp (WreckedMachines) | `RM_Lift_TURRET` |", "| Capture comp (WreckedMachines) | `RM_Lift_KIT` |"), policy))
must_redden("the droid's class", prose_faults(doc_text.replace("**Reach.** `HEAVY_MACHINE` and `WRECKED_TIER` are droid-only", "**Reach.** `HEAVY_MACHINE` are droid-only"), policy))
must_redden("the droid class leaves the JSON", prose_faults(doc_text, mutated(named(WRECKED_TIER=dict(actor="colonist")))))
for item in ALL_BUILD_ITEMS:
    must_redden("build order row " + item, prose_faults(doc_text.replace("| `%s` |" % item, "| dropped |"), policy))

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
            if event.get("id") in ALL_BUILD_ITEMS and event.get("event") == "file":
                filed[event["id"]] = line
for item in BUILD_ITEMS:
    check(item in filed, item + " not filed")
    check("salvage_lift_policy_2026-11-01.md" in filed.get(item, ""), item + " does not point at the design")
for item in ALL_BUILD_ITEMS:
    event = json.loads(filed[item]) if item in filed else {}
    check(event.get("event") == "file", item + " has no file event")
    check(event.get("spec") == "design/RimMandrake/salvage_lift_policy_2026-11-01.md", item + " spec is not the design")

print("selftest_salvage_lift_policy: %s (%d rows, %d categories)" % ("FAIL %d" % len(fails) if fails else "PASS", len(rows), len(cats)))
sys.exit(1 if fails else 0)
