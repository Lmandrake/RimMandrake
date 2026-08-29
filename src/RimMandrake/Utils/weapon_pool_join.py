#!/usr/bin/env python3
"""
weapon_pool_join.py — for the 23 bare-producing kinds, which mechanism actually empties
their pool: no ranged fallback, or a generateAllowChance coin-flip on a thin pool?

VERSION 1.0  (2026-08-29)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

WHY THIS EXISTS
---------------
PAWN_WEAPON_GEN_TAG_POOL_READ_1 read `PawnWeaponGenerator.TryGenerateWeaponFor` from 1.6
source and found the eligibility predicate has TWO more filters than the roster's own
affordability pass checks (`weapon_affordability.py`, budget only):

    (!w.IsRangedWeapon || !pawn.WorkTagIsDisabled(WorkTags.Shooting))
    (generateAllowChance >= 1f || Rand.ChanceSeeded(generateAllowChance, ...))

Either one can empty a kind's pool for a fraction of its pawns with NO shared trait or
backstory — exactly what `roll_arm_harvest_2026-08-28.json` measured (25 distinct
backstory pairs, no repeated cause). That item named the mechanism but could not
attribute which of the 23 affected kinds fails which way; this is the join that does.

THIS REUSES weapon_affordability.py'S PRICING, NOT REINVENTS IT
-----------------------------------------------------------------
`base_market_value` (recipe-recursive, UNMEASURED-not-zero on a missing MarketValue) and
`load_roster` (the EMITTED XML, not the generator's dead `R` shadow table — see that
file's own docstring for why) are imported directly. Re-deriving BaseMarketValue offline
from scratch was considered and rejected: it needs `costList` recursion through arbitrary
materials, which that file already solved and calibrated. This script only adds the two
fields that file never needed: `verbs` (-> IsRangedWeapon) and `generateAllowChance`,
fetched by name for just the weapons that actually appear in one of the 23 kinds' tag
pools (dozens, not the full ~1,500-weapon roster).

WHAT "WITHIN BUDGET" MEANS HERE
--------------------------------
Per-pawn eligibility is `price <= Rand.RangeInclusive(min, max)`, a fresh roll per pawn.
A STATIC per-kind answer needs one threshold, not a distribution: this uses `price <=
max` — the pool that is EVER reachable on the most generous roll. If that pool is
ranged-only, no roll at any budget makes it not-ranged-only; the Shooting-incapable
exclusion is unconditional. Unpriced (UNMEASURED) weapons are excluded from this pool
- not proven affordable, not proven not - and reported separately so an unmeasured
weapon is never mistaken for confirmed-safe headroom.

WHAT "RANGED" MEANS HERE
-------------------------
`ThingDef.IsRangedWeapon` (Verse/ThingDef.cs): a weapon whose `verbs` list is non-empty
and contains at least one verb NOT assignable from `Verb_MeleeAttack`. Read from the
dump's `verbs[].verbClass` field: melee weapons in this game (vanilla and every mod
checked) carry NO `verbs` entry at all - they attack via `tools`, a different field this
script never reads - so `bool(verbs)` is the actual discriminator; the verbClass check on
top only guards the rare weapon that defines a genuinely melee-classed verb.

USAGE
-----
    python3 src/RimMandrake/Utils/weapon_pool_join.py
    python3 src/RimMandrake/Utils/weapon_pool_join.py --kinds Jawa_Hutt_Grunt,Jawa_Junkers_Grunt
    python3 src/RimMandrake/Utils/weapon_pool_join.py --json out.json

Exit 0 always (this attributes, it does not pass/fail) unless the dump/roster cannot be
read at all.
"""
from __future__ import annotations
import argparse
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from game_paths import DUMP_ROOT  # noqa: E402
import weapon_affordability as WA  # noqa: E402

# The 23 kinds roll_arm_harvest_2026-08-28.json measured bare (>0 of 5 rolls bare).
# Frozen here as the item's own scope, not re-derived at run time - the source JSON is a
# point-in-time sample and could roll differently on a re-run; this join is about THESE
# 23 kind's tag pools, which do not change roll to roll.
BARE_23 = [
    "Jawa_Hutt_Grunt", "Jawa_Geonosian_Grunt", "Jawa_Empire_Grunt", "Jawa_Empire_Heavy",
    "Jawa_Empire_Specialist", "Jawa_Empire_Leader", "Jawa_Hutt_Heavy", "Jawa_Hutt_Specialist",
    "Jawa_Homestead_Specialist", "Jawa_Homestead_Leader", "Jawa_DeepDesert_Heavy",
    "Jawa_DeepDesert_Specialist", "Jawa_Wildsteam_Specialist", "Jawa_Wildsteam_Leader",
    "Jawa_Deepwater_Specialist", "Jawa_Deepwater_Leader", "Jawa_Geonosian_Heavy",
    "Jawa_Geonosian_Specialist", "Jawa_Helix_Heavy", "Jawa_Helix_Leader",
    "Jawa_TradeMoot_Heavy", "Jawa_Junkers_Grunt", "Jawa_Homestead_DesertRanger",
]


def _sqlite_defs_path():
    # defs.sqlite lives at DUMP_ROOT, the flat root - NOT under DEF_DUMP, which
    # `game_paths.py` resolves to the newest dated captures/<id>/ subfolder.
    # FLAT_MANIFEST_READER_SWEEP_1 is the general form of this trap; this file
    # had it too on first write, caught by every kind reading "ranged 0".
    p = os.path.join(DUMP_ROOT, "defs.sqlite")
    if not os.path.isfile(p):
        return None
    return p


class _VerbChanceLookup:
    """IsRangedWeapon + generateAllowChance, fetched by name, cached. Same shape as
    weapon_affordability._LazyCostIndex - a name is queried at most once."""

    def __init__(self, db_path):
        self._conn = sqlite3.connect("file:%s?mode=ro" % db_path, uri=True) if db_path else None
        self._cache = {}

    def get(self, defname):
        if defname in self._cache:
            return self._cache[defname]
        if self._conn is None:
            rec = (None, None)
        else:
            row = self._conn.execute(
                "select json_extract(json, '$.fields.verbs'), "
                "json_extract(json, '$.fields.generateAllowChance') "
                "from defs where def_type = 'ThingDef' and def_name = ?",
                (defname,)).fetchone()
            if row is None:
                rec = (None, None)
            else:
                verbs_raw, gac = row
                is_ranged = False
                if verbs_raw:
                    try:
                        verbs = json.loads(verbs_raw)
                    except ValueError:
                        verbs = []
                    for v in verbs or []:
                        vc = (v or {}).get("verbClass") or ""
                        if "MeleeAttack" not in vc:
                            is_ranged = True
                            break
                rec = (is_ranged, 1.0 if gac is None else float(gac))
        self._cache[defname] = rec
        return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kinds", help="comma-separated defName subset; default all 23")
    ap.add_argument("--json", help="also write the full per-kind data as JSON to this path")
    args = ap.parse_args()

    want = set(args.kinds.split(",")) if args.kinds else set(BARE_23)

    dump = WA.find_dump(None)
    by_tag = WA.load_weapons(dump)               # {tag: [(defName, price|None, computed)]}
    roster = {dn: (label, lo, hi, tags) for dn, label, lo, hi, tags in WA.load_roster()}

    db = _sqlite_defs_path()
    if db is None:
        print("⚠️  no defs.sqlite at %s/defs.sqlite - IsRangedWeapon/generateAllowChance "
              "cannot be read; run refresh.py." % DUMP_ROOT, file=sys.stderr)
    vc = _VerbChanceLookup(db)

    missing_from_roster = [k for k in want if k not in roster]
    if missing_from_roster:
        print("⚠️  not in the emitted roster XML (skipped): %s\n"
              % ", ".join(sorted(missing_from_roster)))
    want = [k for k in want if k in roster]

    results = {}
    ranged_only_count = 0
    thin_low_chance_count = 0

    for dn in sorted(want, key=lambda k: (roster[k][0])):
        label, lo, hi, tags = roster[dn]

        # every weapon carrying ANY of this kind's tags, deduped by defName
        pool_by_name = {}
        for t in tags:
            for wn, price, was_computed in by_tag.get(t, []):
                pool_by_name.setdefault(wn, (price, was_computed))

        within_budget = [wn for wn, (price, _c) in pool_by_name.items()
                          if price is not None and price <= hi]
        unpriced = [wn for wn, (price, _c) in pool_by_name.items() if price is None]

        ranged = []
        melee = []
        low_chance = []
        for wn in within_budget:
            is_ranged, gac = vc.get(wn)
            (ranged if is_ranged else melee).append(wn)
            if gac is not None and gac < 1.0:
                low_chance.append((wn, gac))

        ranged_only = len(within_budget) > 0 and len(melee) == 0
        thin_pool = len(within_budget) <= 2
        thin_low_chance = thin_pool and len(low_chance) > 0

        if ranged_only:
            ranged_only_count += 1
        if thin_low_chance:
            thin_low_chance_count += 1

        results[dn] = {
            "label": label, "weaponMoney": [lo, hi], "tags": tags,
            "poolSize": len(pool_by_name), "withinBudget": len(within_budget),
            "unpriced": len(unpriced), "rangedInPool": len(ranged), "meleeInPool": len(melee),
            "rangedOnly": ranged_only, "thinPool": thin_pool,
            "lowGenerateAllowChance": [{"def": wn, "chance": gac} for wn, gac in low_chance],
            "thinPoolWithLowChance": thin_low_chance,
            "meleeSample": melee[:5], "rangedSample": ranged[:5],
        }

        flag = []
        if ranged_only:
            flag.append("RANGED-ONLY (no melee fallback -> Shooting-incapable = bare)")
        if thin_low_chance:
            flag.append("THIN POOL (%d) WITH generateAllowChance<1 (%s)"
                        % (len(within_budget),
                           ", ".join("%s@%.2f" % (n, c) for n, c in low_chance)))
        if not flag:
            flag.append("neither mechanism implicated by this join")

        print("%-30s %-22s money %g~%g  pool %d (budget %d, unpriced %d, ranged %d, melee %d)"
              % (dn, label, lo, hi, len(pool_by_name), len(within_budget), len(unpriced),
                 len(ranged), len(melee)))
        for f in flag:
            print("    -> " + f)

    print("\n%d/%d kinds are ranged-only within budget (no melee fallback at all)."
          % (ranged_only_count, len(want)))
    print("%d/%d kinds have a within-budget pool of <=2 with a generateAllowChance<1 entry."
          % (thin_low_chance_count, len(want)))
    both = sum(1 for r in results.values() if r["rangedOnly"] and r["thinPoolWithLowChance"])
    neither = sum(1 for r in results.values()
                  if not r["rangedOnly"] and not r["thinPoolWithLowChance"])
    print("%d kind(s) match BOTH candidate mechanisms; %d match NEITHER (needs another look)."
          % (both, neither))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print("\nwrote " + args.json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
