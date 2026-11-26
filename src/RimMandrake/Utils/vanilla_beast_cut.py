#!/usr/bin/env python3
"""vanilla_beast_cut.py — VANILLA_BEAST_EXCISION_1 wave 4: which official (Ludeon/DLC) animal ThingDefs can be cut
by Cherry Picker NOW, and which must wait, read from the def dump plus the shipped Cherry Picker list.

    python3 src/RimMandrake/Utils/vanilla_beast_cut.py [--db PATH] [--ship PATH] [--json OUT] [--keys] [--strict]
    python3 src/RimMandrake/Utils/vanilla_beast_cut.py --check-log [--wave 4] [--log PATH]   # live proof, read-only

--check-log is the live clause: exit 0 when the live Cherry Picker settings hold every key of the wave AND Player.log's
removal block (the load's runtime truth, cherrypicker.from_log) lists each of them; 1 when the settings hold them but the
load did not remove one; 2 (UNMEASURED) when the settings lack them (SHIP not deployed: cherrypicker_swap.py --ship
--apply, then a load) or the log has no removal block, or the log predates the settings file.

WHY A CHERRY PICKER ThingDef CUT CLOSES THE NON-ROSTER ROUTES. CherryPicker.dll (1.6) names, for a race it processes,
`tradeTags`, `tradeability`, `wildAnimals`, `pollutionWildAnimals`, `cachedAnimalCommonalities`, `wildBiomes`,
`stockGenerators` and `spawnablePawnKinds` (read from its string table, 2026-11-02). Trader stock
(StockGenerator_Animals: tradeTags ∩ tradeTagsSell, tradeability) and farm wander-in (tradeTags has AnimalFarm) both
select through the fields it clears. A ThingDef is NEUTERED, not deleted (design/Jawa/worldbuilding/cherrypick_resolved.md
§0c), so a DefOf or a GetNamed of the name still binds.

WHAT WAITS (the item: "a biome's cut lands when its own cast can carry it — do not strip a roster bare"):
  * roster-bound  — on an UNCUT BiomeDef's wildAnimals / pollutionWildAnimals / coastalWildAnimals with commonality > 0.
                    The dump is post-patch, so patch-added casts are seen. Vanilla biomes still on the frozen map
                    (AridShrubland, Lake: OWNER_EXCLUDE in cherrypick_build.py) count; their sitting is their cut.
  * carrier       — named in any FactionDef's pawnGroupMakers carriers: the faction names the kind directly, so a
                    ThingDef cut does not stop a caravan bringing it (wave 3: VanillaBeastExcision_Carriers.xml).
  * family        — dryads (the Gauranlen tree breeds them; not a beast a player meets wild), insects (owned by
                    STILLSAND_RM_MOD_BUILD_1: Dune-Sea infestations become sand busters), Anomaly entities.
LEAKS (reported, never blocking): a spawn-route def (ROUTE_TYPES: incident, quest, scenario, thing set, tile mutator,
gen step, structure symbol/layout, ranch list) that names the race, one of its kinds or one of its fertilized eggs
(CompProperties_Hatcher.hatcherPawn) spawns it BY NAME, and a neutered def is still spawnable — so the ThingDef cut is
still progress (it closes trade and wander-in) but that def is its own follow-up. RecipeDef/ThingCategoryDef filters
and the like are mentions, not routes, and are ignored. `leaks:` (route_leaks) watches EVERY official race cut in SHIP
or cut now, not only this wave's: a race cut in an earlier wave stays watched. Pairs that STRIKES removes are closed:
the dump is post-patch, so a dump taken after the strike file shipped no longer holds them anyway.
⚠️ The dump stops at a depth limit and writes "<maxdepth:ThingFilter>" there, so a ThingSetMaker's filter (where the
rare-catch eggs live) is unseen: the run prints how many route defs are cut off this way, and their source XML decides.

C#-ROUTES (they pick their kind in code, so no def read sees them; decompiled 1.6, 2026-11-26):
  * CLOSED by the race cut itself. CherryPicker 1.6 sets canArriveManhunter = false and combatPower = MaxValue on every
    PawnKindDef whose race it processes, so VEE_AnimalPodCrash (all kinds, canArriveManhunter) and the vanilla
    manhunter fallbacks (AggressiveAnimalIncidentUtility, all kinds, canArriveManhunter) cannot pick a cut race.
    VEE_BattleAnimalsWanderIn needs race tradeTags "AnimalFighter" (cleared by the cut). VEE_ManhunterSingleArrival
    and Odyssey's AnimalHabitat pick from the map biome's AllWildAnimals (the cut clears the rosters).
  * OPEN until cut: CSHARP_ROUTES below. VEE_CaravanAnimalsWanderIn (CaravanAnimalWI.PickPawnKindDef) takes every
    PawnKindDef whose race is packAnimal, a flag no cut clears, so it is a leak for each cut pack animal while the
    IncidentDef is in the dump and not cut.
⚠️ The dump is captured BEFORE Cherry Picker runs, so "already cut" is read from the SHIP list, never the dump.
Sanity probe: Muffalo must be a carrier (it is in 20+ factions) or the instrument is reading nothing.
"""
import argparse
import json
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from game_paths import DUMP_ROOT  # noqa: E402
from vanilla_beast_routes import rows, walk  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DB = os.path.join(DUMP_ROOT, "defs.sqlite")
SHIP = os.path.join(REPO, "infrastructure", "state", "cherrypicker", "CherryPicker.SHIP.xml")
ROSTER_FIELDS = ("wildAnimals", "pollutionWildAnimals", "coastalWildAnimals")
# Def types that can spawn a live animal by naming its race or kind. Everything else naming one (recipe and category
# filters, codex entries, songs, genome-extraction lists) is a mention, not a route. ⚠️ KCSG's SymbolDef is left out on
# purpose: KCSG generates one SymbolDef per ThingDef/PawnKindDef automatically, so every animal "has" two and the hit
# says nothing; a structure that really places one names the symbol in its StructureLayoutDef, which is counted.
ROUTE_TYPES = {"IncidentDef", "QuestScriptDef", "ScenarioDef", "ThingSetMakerDef", "TileMutatorDef", "GenStepDef",
               "StructureLayoutDef", "RanchAnimalsDef", "PawnGroupKindDef", "SitePartDef"}
# Routes that name the kind in C# (a DefOf), invisible to any def read: cut with the race.
# IncidentWorker_ThrumboPasses spawns PawnKindDefOf.Thrumbo; a neutered ThingDef does not stop it.
COMPANION_KEYS = {"Thrumbo": ["IncidentDef/ThrumboPasses"]}
# C# routes that select by a race flag no Cherry Picker cut clears: route key -> the animals[] flag it selects by.
CSHARP_ROUTES = {"IncidentDef/VEE_CaravanAnimalsWanderIn": "pack"}
# The Utinni patch that strikes cut races from route defs we do not own (VANILLA_BEAST_LEAKS_EXCISE_ESCAPEES_AT_LARGE).
STRIKES = os.path.join(REPO, "src", "RimUtinni", "UtinniPatches", "Patches", "VanillaBeastExcision_RouteStrikes.xml")


def keys_for(names, cut):
    """The Cherry Picker keys a wave adds for these races: ThingDef/<race> plus its C#-route companions, minus any
    key already in the list."""
    out = []
    for n in sorted(names):
        for k in ["ThingDef/" + n] + COMPANION_KEYS.get(n, []):
            if k not in cut:
                out.append(k)
    return out


# Keys each wave added to CherryPicker.SHIP.xml. Wave 4: 2026-11-02, dump captured 2026-11-02T17:59:18Z.
WAVES = {4: ["ThingDef/AlphaThrumbo", "ThingDef/Bear_Grizzly", "ThingDef/Caribou", "ThingDef/Chicken", "ThingDef/Cow",
             "ThingDef/Deer", "ThingDef/Duck", "ThingDef/Elk", "ThingDef/Fox_Red", "ThingDef/Goat", "ThingDef/Goose",
             "ThingDef/Ibex", "ThingDef/Monkey", "ThingDef/Sheep", "ThingDef/Squirrel", "ThingDef/Thrumbo",
             "IncidentDef/ThrumboPasses", "ThingDef/Turkey", "ThingDef/Wolf_Great", "ThingDef/Wolf_Timber",
             "ThingDef/Wolverine", "ThingDef/Yak"]}


def check_log(wave, log=None):
    """The live proof. -> (exit code, message); see the module doc."""
    import cherrypicker as cp
    import game_paths as gp
    want = WAVES[wave]
    if not os.path.exists(cp.SETTINGS):
        return 2, "UNMEASURED: no live Cherry Picker settings at %s" % cp.SETTINGS
    live = ship_keys(cp.SETTINGS)
    gone = [k for k in want if k not in live]
    if gone:
        return 2, "UNMEASURED: the live settings lack %d wave-%d key(s) (%s): deploy SHIP with " \
                  "cherrypicker_swap.py --ship --apply, then load" % (len(gone), wave, ", ".join(gone[:3]))
    log = log or gp.PLAYER_LOG
    if not os.path.exists(log):
        return 2, "UNMEASURED: no Player.log at %s" % log
    if os.path.getmtime(log) < os.path.getmtime(cp.SETTINGS):
        return 2, "UNMEASURED: Player.log is older than the settings file, so its load never read these keys"
    try:
        removed = cp.from_log(log).keys
    except IOError as e:
        return 2, "UNMEASURED: %s" % e
    miss = [k for k in want if k not in removed]
    if miss:
        return 1, "FAIL: the load removed %d defs but not %d wave-%d key(s): %s" % (len(removed), len(miss), wave,
                                                                                   ", ".join(miss))
    return 0, "PASS: all %d wave-%d keys in Player.log's Cherry Picker removal block (%d removed)" % (
        len(want), wave, len(removed))


def ship_keys(path):
    return set(re.findall(r"<li>\s*([^<\s]+)\s*</li>", open(path, encoding="utf-8").read()))


def truncated(o):
    """Every string leaf the dump cut off at its depth limit ("<maxdepth:ThingFilter>"): names below it are unseen."""
    if isinstance(o, str):
        if o.startswith("<maxdepth:"):
            yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from truncated(v)
    elif isinstance(o, list):
        for v in o:
            yield from truncated(v)


def mentions(o, names):
    """Every string leaf in a record that is exactly one of names."""
    if isinstance(o, str):
        if o in names:
            yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from mentions(v, names)
    elif isinstance(o, list):
        for v in o:
            yield from mentions(v, names)


_DEF_PRED = re.compile(r'^/Defs/(\w+)\[defName="([^"]+)"\]/[\w/]*li\[([^\]]+)\]$')
_NAME_TERM = re.compile(r'^\s*([\w/]+|\.)\s*=\s*"([^"]+)"\s*$')


def struck_pairs_text(text):
    """{(route key, name)} that a strike patch removes. Models one op shape only, PatchOperationConditional on an xpath
    with a PatchOperationRemove of the same xpath, the xpath /Defs/<Type>[defName="X"]/<path>/li[<f>="N" or ...];
    any other shape raises ValueError, so a strike the simulation cannot read is never silently counted."""
    import xml.etree.ElementTree as ET
    out = set()
    for op in ET.fromstring(text).findall("Operation"):
        xp = (op.findtext("xpath") or "").strip()
        m = op.find("match")
        if op.get("Class") != "PatchOperationConditional" or m is None or m.get("Class") != "PatchOperationRemove" \
                or (m.findtext("xpath") or "").strip() != xp or op.find("nomatch") is not None:
            raise ValueError("strike op shape not modelled: %s" % xp)
        g = _DEF_PRED.match(xp)
        if not g:
            raise ValueError("strike xpath not modelled: %s" % xp)
        key = "%s/%s" % (g.group(1), g.group(2))
        for term in g.group(3).split(" or "):
            t = _NAME_TERM.match(term)
            if not t:
                raise ValueError("strike predicate term not modelled: %s" % term)
            out.add((key, t.group(2)))
    return out


def struck_pairs(path):
    return struck_pairs_text(open(path, encoding="utf-8").read()) if path and os.path.exists(path) else set()


def route_leaks(animals, kinds_of, namers, cut, struck=frozenset(), eggs=None, present=frozenset()):
    """Pure core of `leaks:`. For every official race cut in `cut` (Type/name keys; pass the wave's cut-now keys in
    too), the uncut route defs that still name it, one of its kinds or one of its eggs (eggs: {egg ThingDef: race}),
    less the (route key, name) pairs in `struck`; plus each CSHARP_ROUTES key in `present` (route keys in the dump)
    and not cut, for each cut race whose animals[] flag it selects by. -> {race: [route key, ...]}."""
    to_race = {k: r for r, ks in kinds_of.items() for k in ks}
    to_race.update(eggs or {})
    gone = {n for n, a in animals.items() if a.get("official") and "ThingDef/" + n in cut}
    out = {}
    for (t, n), leaves in namers.items():
        key = "%s/%s" % (t, n)
        if t not in ROUTE_TYPES or key in cut:
            continue
        for s in leaves:
            r = to_race.get(s, s)
            if r in gone and (key, s) not in struck:
                out.setdefault(r, set()).add(key)
    for key, flag in CSHARP_ROUTES.items():
        if key in present and key not in cut:
            for r in gone:
                if animals[r].get(flag):
                    out.setdefault(r, set()).add(key)
    return {r: sorted(v) for r, v in out.items()}


def classify(animals, kinds_of, biomes, factions, namers, cut):
    """Pure core. animals: {name: {official, dryad, insect, pkg}}; kinds_of: {race: {kind,...}};
    biomes: {biome: {field: [(animal, commonality)]}}; factions: {faction: {kind,...}};
    namers: {(defType, defName): {string leaves}}; cut: set of 'Type/name' keys.
    Returns ({name: reason}, {name: [route def keys]}) for every official, not-yet-cut animal; reason 'cut' means cut
    it now; the second map lists the uncut spawn-route defs still naming it (leaks a ThingDef cut does not close)."""
    kind_race = {k: r for r, ks in kinds_of.items() for k in ks}
    roster = {}
    for b, fields in biomes.items():
        if "BiomeDef/" + b in cut:
            continue
        for f in ROSTER_FIELDS:
            for a, com in fields.get(f) or []:
                if com and float(com) > 0:
                    roster.setdefault(kind_race.get(a, a), set()).add(b)
    carrier = {}
    for fac, ks in factions.items():
        for k in ks:
            carrier.setdefault(kind_race.get(k, k), set()).add(fac)
    named = {}
    for (t, n), leaves in namers.items():
        if t not in ROUTE_TYPES or "%s/%s" % (t, n) in cut:
            continue
        for s in leaves:
            named.setdefault(kind_race.get(s, s), set()).add("%s/%s" % (t, n))
    out = {}
    for n, v in sorted(animals.items()):
        if not v["official"] or "ThingDef/" + n in cut:
            continue
        if v["dryad"]:
            out[n] = "family: dryad (Gauranlen)"
        elif v["insect"]:
            out[n] = "family: insect (STILLSAND_RM_MOD_BUILD_1)"
        elif v["pkg"] == "ludeon.rimworld.anomaly":
            out[n] = "family: Anomaly entity"
        elif n in carrier:
            out[n] = "carrier: %d factions (e.g. %s)" % (len(carrier[n]), sorted(carrier[n])[0])
        elif n in roster:
            out[n] = "roster: %s" % ", ".join(sorted(roster[n])[:4]) + (" +%d" % (len(roster[n]) - 4) if len(roster[n]) > 4 else "")
        else:
            out[n] = "cut"
    leaks = {n: sorted(named[n]) for n in out if n in named}
    return out, leaks


def load(db):
    c = sqlite3.connect("file:%s?mode=ro" % db, uri=True)
    cap = dict(c.execute("select key, value from provenance").fetchall()).get("captured_utc")
    animals = {}
    hatch = {}
    for name, pkg, d in rows(c, "ThingDef"):
        for cp in d.get("comps") or []:
            hp = cp.get("hatcherPawn") if isinstance(cp, dict) else None
            hp = hp.get("defName") if isinstance(hp, dict) else hp
            if hp:
                hatch[name] = hp
        race = d.get("race")
        if not isinstance(race, dict) or race.get("intelligence") != "Animal" or d.get("category") != "Pawn":
            continue
        ft = race.get("fleshType")
        ft = ft.get("defName") if isinstance(ft, dict) else ft
        # race.dryad is not in the dump's record; the Ideology dryads are all Dryad_<caste>.
        animals[name] = dict(pkg=pkg, official=pkg.startswith("ludeon.rimworld"),
                             dryad=bool(race.get("dryad")) or name.startswith("Dryad_"),
                             insect=(ft == "Insectoid"), pack=bool(race.get("packAnimal")))
    kinds_of = {}
    for name, pkg, d in rows(c, "PawnKindDef"):
        r = d.get("race")
        r = r.get("defName") if isinstance(r, dict) else r
        if r in animals:
            kinds_of.setdefault(r, set()).add(name)
    biomes = {}
    for name, pkg, d in rows(c, "BiomeDef"):
        biomes[name] = {f: [(li.get("animal"), li.get("commonality")) for li in (d.get(f) or []) if isinstance(li, dict)]
                        for f in ROSTER_FIELDS}
    factions = {}
    for name, pkg, d in rows(c, "FactionDef"):
        for car in walk(d, "carriers"):
            for li in car or []:
                k = li.get("kind") if isinstance(li, dict) else li
                k = k.get("defName") if isinstance(k, dict) else k
                if k:
                    factions.setdefault(name, set()).add(k)
    official = {n for n, v in animals.items() if v["official"]}
    kind_race = {k: r for r, ks in kinds_of.items() for k in ks}
    eggs = {e: kind_race.get(k, k) for e, k in hatch.items() if kind_race.get(k, k) in official}
    names = official | {k for r in official for k in kinds_of.get(r, ())} | set(eggs)
    namers = {}
    present = set()
    cut_off = set()
    for t in sorted(ROUTE_TYPES):
        for name, pkg, d in rows(c, t):
            present.add("%s/%s" % (t, name))
            hit = set(mentions(d, names))
            if hit:
                namers[(t, name)] = hit
            if any(True for _ in truncated(d)):
                cut_off.add("%s/%s" % (t, name))
    # The egg map and the route keys present are side outputs (the 6-tuple is load()'s contract with its callers).
    global LAST_EGGS, LAST_PRESENT, LAST_TRUNCATED
    LAST_EGGS, LAST_PRESENT, LAST_TRUNCATED = eggs, present, cut_off
    return cap, animals, kinds_of, biomes, factions, namers


LAST_EGGS, LAST_PRESENT, LAST_TRUNCATED = {}, set(), set()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--ship", default=SHIP)
    ap.add_argument("--json")
    ap.add_argument("--keys", action="store_true", help="print only the Cherry Picker keys to add, one per line")
    ap.add_argument("--check-log", action="store_true", help="live proof: the wave's keys were removed by the load")
    ap.add_argument("--wave", type=int, default=max(WAVES))
    ap.add_argument("--log")
    ap.add_argument("--strikes", default=STRIKES, help="the strike patch whose removals count as closed ('' = none)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when leaks > 0")
    a = ap.parse_args(argv)
    if a.check_log:
        code, msg = check_log(a.wave, a.log)
        print(msg)
        return code
    cap, animals, kinds_of, biomes, factions, namers = load(a.db)
    cut = ship_keys(a.ship)
    res, leaks = classify(animals, kinds_of, biomes, factions, namers, cut)
    carriers = {k for ks in factions.values() for k in ks}
    probe = "Muffalo" in carriers
    now = sorted(n for n, r in res.items() if r == "cut")
    if a.keys:
        print("\n".join(keys_for(now, cut)))
        return 0 if probe else 2
    print("dump captured %s; sanity probe (Muffalo is a carrier): %s" % (cap, "OK" if probe else "FAILED"))
    off = sum(1 for v in animals.values() if v["official"])
    print("official animal ThingDefs %d; already cut %d; open %d" % (off, off - len(res), len(res)))
    by = {}
    for n, r in res.items():
        by.setdefault(r.split(":")[0], []).append(n)
    for k in sorted(by):
        print("  %-8s %3d  %s" % (k, len(by[k]), " ".join(sorted(by[k]))))
    struck = struck_pairs(a.strikes)
    gone = cut | {"ThingDef/" + n for n in now}
    lk = route_leaks(animals, kinds_of, namers, gone, struck=struck, eggs=LAST_EGGS, present=LAST_PRESENT)
    print("leaks: %d cut or cut-now animals still named by an uncut spawn route (%d pairs struck by %s)" % (
        len(lk), len(struck), os.path.relpath(a.strikes, REPO) if a.strikes else "nothing"))
    for n in sorted(lk):
        print("  %-14s %s" % (n, ", ".join(lk[n][:6]) + (" +%d" % (len(lk[n]) - 6) if len(lk[n]) > 6 else "")))
    print("UNMEASURED below the dump's depth limit: %d route defs hold a <maxdepth:...> field (a ThingFilter's eggs, "
          "for one); read their source XML" % len(LAST_TRUNCATED))
    if a.json:
        json.dump({"captured_utc": cap, "probe_ok": probe, "open": res, "leaks": lk}, open(a.json, "w"), indent=1)
    if not probe:
        return 2
    return 1 if (a.strict and lk) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
