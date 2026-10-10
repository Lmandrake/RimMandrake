#!/usr/bin/env python3
"""vanilla_beast_routes.py — VANILLA_BEAST_EXCISION_1 wave 2: which NON-roster routes can still put an official
(Ludeon/DLC) animal in front of a player, read from the def dump (defs.sqlite).

    python3 src/RimMandrake/Utils/vanilla_beast_routes.py [--db PATH] [--json OUT]

Selection rules are the decompiled 1.6 engine's own (RimSage, 2026-10-10):
  * farm wander-in  IncidentWorker_FarmAnimalsWanderIn: Animal, Wildness < 0.35, tradeTags has "AnimalFarm", not Dryad,
                    not neverIncludeInQuests (temperature gate ignored here: a census of the possible, not of one map).
  * trader stock    StockGenerator_Animals.PawnKindAllowed: race tradeTags ∩ a TraderKindDef's tradeTagsSell, wildness
                    inside that generator's [minWildness, maxWildness], race tradeability TraderCanSell (All|Buyable).
  * caravan carrier FactionDef pawnGroupMakers[*].carriers kinds.
  * manhunter       AggressiveAnimalIncidentUtility: map-biome rosters only (AllWildAnimals, coastal, pollution) — its
                    global fallback is still filtered by biome commonality, so it is the roster route, covered in wave 1.
Sanity probe: Muffalo must appear as a caravan carrier AND in trader stock, or the instrument is reading nothing.
Records are the dump's `fields` object; a missing Wildness statBase reads as 0 (flagged in the output).
"""
import argparse
import json
import os
import sqlite3
import sys

DB = "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite"


def rows(c, t):
    for name, pkg, js in c.execute("select def_name, package_id, json from defs where def_type=?", (t,)):
        yield name, (pkg or ""), json.loads(js).get("fields") or {}


def walk(o, key):
    """Every value under a key anywhere in a nested record."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                yield v
            yield from walk(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, key)


def stat(d, name):
    for sb in walk(d, "statBases"):
        if isinstance(sb, dict) and name in sb:
            return sb[name]
        if isinstance(sb, list):
            for s in sb:
                if isinstance(s, dict) and s.get("stat") == name:
                    return s.get("value")
    return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    c = sqlite3.connect("file:%s?mode=ro" % a.db, uri=True)
    cap = dict(c.execute("select key, value from provenance").fetchall()).get("captured_utc")

    animals = {}
    for name, pkg, d in rows(c, "ThingDef"):
        race = d.get("race")
        if not isinstance(race, dict) or race.get("intelligence") != "Animal" or d.get("category") != "Pawn":
            continue
        animals[name] = dict(pkg=pkg, official=pkg.startswith("ludeon.rimworld"), tags=d.get("tradeTags") or [],
                             wild=stat(d, "Wildness"), tradeability=d.get("tradeability"),
                             dryad=bool(race.get("dryad")), noquest=bool(race.get("neverIncludeInQuests")),
                             pack=bool(race.get("packAnimal")))
    kind_race = {}
    for name, pkg, d in rows(c, "PawnKindDef"):
        r = d.get("race")
        kind_race[name] = r.get("defName") if isinstance(r, dict) else r

    def wildv(x):
        return 0.0 if x is None else float(x)

    farm = sorted(n for n, v in animals.items() if "AnimalFarm" in v["tags"] and wildv(v["wild"]) < 0.35 and not v["dryad"] and not v["noquest"])

    trade = {}
    for tname, pkg, d in rows(c, "TraderKindDef"):
        for g in d.get("stockGenerators") or []:
            if not isinstance(g, dict) or "Animals" not in str(g.get("$type") or g.get("Class") or g.get("class") or ""):
                continue
            sell = set(g.get("tradeTagsSell") or [])
            lo, hi = wildv(g.get("minWildness")), float(g.get("maxWildness", 1.0) if g.get("maxWildness") is not None else 1.0)
            for n, v in animals.items():
                w = wildv(v["wild"])
                if sell & set(v["tags"]) and lo <= w <= min(hi, 1.0) and str(v["tradeability"]) in ("All", "Buyable", "None_unset"):
                    trade.setdefault(n, set()).add(tname)

    carry = {}
    for fname, pkg, d in rows(c, "FactionDef"):
        for car in walk(d, "carriers"):
            for li in car or []:
                k = li.get("kind") if isinstance(li, dict) else li
                k = k.get("defName") if isinstance(k, dict) else k
                r = kind_race.get(k, k)
                if r:
                    carry.setdefault(r, set()).add(fname)

    probe_ok = "Muffalo" in trade and "Muffalo" in carry
    out = {"captured_utc": cap, "probe_muffalo_farm_and_carrier": probe_ok,
           "official_animals": sum(1 for v in animals.values() if v["official"]),
           "farm_wanderin": [n for n in farm if animals[n]["official"]],
           "farm_wanderin_ours": [n for n in farm if not animals[n]["official"]],
           "trader_stock": {n: sorted(t) for n, t in sorted(trade.items()) if animals[n]["official"]},
           "trader_stock_ours_count": sum(1 for n in trade if not animals[n]["official"]),
           "carriers": {n: sorted(f) for n, f in sorted(carry.items()) if animals.get(n, {}).get("official")},
           "official_without_wildness_stat": sorted(n for n, v in animals.items() if v["official"] and v["wild"] is None),
           "carriers_ours": {n: sorted(f) for n, f in sorted(carry.items()) if n in animals and not animals[n]["official"]}}
    print("dump captured %s; sanity probe (Muffalo trader+carrier): %s" % (cap, "OK" if probe_ok else "FAILED — instrument reads nothing"))
    print("official animal ThingDefs: %d" % out["official_animals"])
    print("farm wander-in eligible, official: %d  (ours: %d)" % (len(out["farm_wanderin"]), len(out["farm_wanderin_ours"])))
    print("trader-stock sellable, official: %d  (ours: %d)" % (len(out["trader_stock"]), out["trader_stock_ours_count"]))
    print("faction caravan carriers, official: %d  (ours: %d)" % (len(out["carriers"]), len(out["carriers_ours"])))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=sorted)
    return 0 if probe_ok else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
