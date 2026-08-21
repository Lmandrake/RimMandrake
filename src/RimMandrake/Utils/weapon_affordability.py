#!/usr/bin/env python3
"""
weapon_affordability.py — will this pawn kind actually spawn holding something?

VERSION 1.0  (2026-08-20)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

WHY THIS EXISTS
---------------
`gen_pawnkind_roster.py` says *"Re-check with the affordability pass whenever a tag
or a price changes."* **There was no affordability pass.** This is it.

🔴 THE MECHANISM, read out of `PawnWeaponGenerator.TryGenerateWeaponFor` rather
than assumed — it has already been mis-stated twice in this project's own notes:

    float randomInRange = pawn.kindDef.weaponMoney.RandomInRange;   // ONE roll
    for each candidate w:
        if (!(w.Price > randomInRange) && <a tag matches> && ...)
            workingWeapons.Add(w);
    if (workingWeapons.Count == 0) return;        // <- THE PAWN GETS NOTHING

So `weaponMoney` is a **CEILING**, rolled once, and every weapon priced at or below
that roll is eligible.

⇒ **`min` IS NOT A FLOOR ON ELIGIBILITY — but it IS what decides whether the kind
arms RELIABLY.** Two different questions, and the roster item conflated them:

    max >= cheapest  ->  the kind CAN arm.   Below that it never arms at all.
    min >= cheapest  ->  the kind ALWAYS arms. Between the two it arms sometimes,
                         with probability (max - cheapest) / (max - min).

**The roster's acceptance criterion is 5 out of 5 spawns armed, for all 48 kinds.**
That is the second question, so `min >= cheapest` is the bar this tool holds them
to, and SOMETIMES is reported as a failure with its odds, not as a pass.

⚠️ **THE PRICES HERE ARE A FLOOR, NEVER THE TRUTH.** The engine compares
`ThingStuffPair.Price`, which includes the STUFF cost; this reads `MarketValue`
off the def, which is the unstuffed value. A stuffed weapon is dearer, never
cheaper — so a kind that looks marginal here is worse in game, and headroom above
the cheapest price is not padding.

⚠️ **A WEAPON WITH NO `MarketValue` STATBASE IS REPORTED UNMEASURED, NOT FREE.**
Several modded weapons inherit their value from a parent the dump does not
resolve. Treating a missing number as 0 would make an empty pool look like the
cheapest possible one, which is the exact failure this tool exists to catch.

USAGE
-----
    python3 src/RimMandrake/Utils/weapon_affordability.py
    python3 src/RimMandrake/Utils/weapon_affordability.py --verbose
    python3 src/RimMandrake/Utils/weapon_affordability.py --dump <path to DefDump/defs>

Exit 0 = every kind always arms. Exit 1 = at least one kind can spawn bare.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
from game_paths import DEF_DUMP  # noqa: E402
ROSTER_GEN = os.path.join(HERE, "gen_pawnkind_roster.py")

_DUMPS = [
    os.path.join(DEF_DUMP, "defs"),
]


def die(msg):
    print("FAIL: " + msg, file=sys.stderr)
    sys.exit(2)


def find_dump(explicit):
    for p in ([explicit] if explicit else []) + _DUMPS:
        if p and os.path.isdir(p):
            return p
    die("no def dump found; pass --dump")


VALUE_PER_WORK = 0.0036          # StatWorker_MarketValue.ValuePerWork
DEFAULT_GUESS_STUFF_COST = 2.0   # StatWorker_MarketValue.DefaultGuessStuffCost


def _stat(fields, name):
    for sb in fields.get("statBases") or []:
        if isinstance(sb, dict) and sb.get("stat") == name:
            return sb.get("value")
    return None


def base_market_value(defname, index, memo, stack=None):
    """
    A def's BaseMarketValue, DECLARED or COMPUTED, mirroring
    StatWorker_MarketValue.CalculatedBaseMarketValue:

        num = SUM(costList[i].count * ingredient.BaseMarketValue)
              + (CostStuffCount > 0 ? CostStuffCount * 2 : 0)     # no stuff chosen
        if (workToMake > 2) num += workToMake * 0.0036
        return num / productCount

    🔑 WHY THIS IS NEEDED AT ALL. Every Outer Rim weapon declares MaxHitPoints,
    Flammability, DeteriorationRate and Beauty and **no MarketValue**, so the
    engine computes the price from the recipe instead. Reading the def gives you
    nothing, which is why nine pawn kinds were previously UNMEASURABLE and the
    roster item said to "read them off the weapon defs directly" - there is
    nothing there to read.

    ⚠️ Still a FLOOR, not the truth: the engine prices a ThingStuffPair, so a
    stuffed weapon costs more. And with no stuff chosen the engine guesses 2 per
    unit, which is what is used here.

    Returns None only when a value genuinely cannot be derived.
    """
    if defname in memo:
        return memo[defname]
    stack = stack or set()
    if defname in stack:      # cyclic recipe; refuse rather than loop
        return None
    d = index.get(defname)
    if d is None:
        return None
    f = d.get("fields") or {}

    declared = _stat(f, "MarketValue")
    if declared is not None:
        memo[defname] = float(declared)
        return memo[defname]

    stack = stack | {defname}
    total = 0.0
    resolved_any = False
    for c in f.get("costList") or []:
        if not isinstance(c, dict):
            continue
        ing = base_market_value(c.get("thingDef"), index, memo, stack)
        if ing is None:
            return None                      # one unpriceable ingredient poisons it
        total += float(c.get("count", 0)) * ing
        resolved_any = True

    stuff_count = f.get("costStuffCount") or 0
    if stuff_count and stuff_count > 0:
        total += float(stuff_count) * DEFAULT_GUESS_STUFF_COST
        resolved_any = True

    if not resolved_any:
        return None                          # no recipe inputs at all

    work = max(float(_stat(f, "WorkToMake") or 0), float(_stat(f, "WorkToBuild") or 0))
    if work > 2:
        total += work * VALUE_PER_WORK

    count = 1
    rm = f.get("recipeMaker")
    if isinstance(rm, dict) and rm.get("productCount"):
        try:
            count = max(1, int(rm["productCount"]))
        except Exception:
            count = 1

    memo[defname] = total / count
    return memo[defname]


def load_weapons(dump):
    """-> {tag: [(defName, price or None, was_computed), ...]}"""
    path = os.path.join(dump, "ThingDef.json")
    if not os.path.isfile(path):
        die("no ThingDef.json at " + path)
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    defs = data.get("defs", [])
    index = {d["defName"]: d for d in defs}
    memo = {}
    by_tag = {}
    for d in defs:
        f = d.get("fields") or {}
        tags = f.get("weaponTags")
        if not tags:
            continue
        declared = _stat(f, "MarketValue")
        mv = float(declared) if declared is not None else base_market_value(d["defName"], index, memo)
        for t in tags:
            by_tag.setdefault(t, []).append((d["defName"], mv, declared is None))
    return by_tag


def load_roster():
    """Read the R table out of the generator, which is its source of truth."""
    src = open(ROSTER_GEN, "r", encoding="utf-8").read()
    m = re.search(r"^R = \[$(.*?)^\]$", src, re.S | re.M)
    if not m:
        die("could not find the `R = [` table in " + ROSTER_GEN)
    rows = eval("[" + m.group(1) + "]", {"__builtins__": {}}, {})   # a literal table
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dump", help="path to DefDump/defs")
    ap.add_argument("--verbose", action="store_true",
                    help="list every kind, not only the failures")
    args = ap.parse_args()

    dump = find_dump(args.dump)
    by_tag = load_weapons(dump)
    rows = load_roster()
    print("weapon tags known: %d, from %s" % (len(by_tag), dump))
    print("pawn kinds in the roster: %d\n" % len(rows))

    always, sometimes, never, notags, unmeasured = [], [], [], [], []

    for row in rows:
        faction, role, label, wm, am, quality, tags, apparel = row
        defname = "Jawa_%s_%s" % (faction, role)
        lo, hi = float(wm), float(wm) * 1.2          # the generator emits wm ~ wm*1.2

        if not tags:
            notags.append((defname, label))
            continue

        priced, unpriced = [], []
        computed = 0
        for t in tags:
            for dn, mv, was_computed in by_tag.get(t, []):
                if mv is None:
                    unpriced.append((dn, mv))
                else:
                    priced.append((dn, mv))
                    computed += 1 if was_computed else 0

        if not priced and not unpriced:
            never.append((defname, label, lo, hi, None, "no weapon carries any of its tags"))
            continue
        if not priced:
            unmeasured.append((defname, label, lo, hi, len(unpriced)))
            continue

        cheapest_name, cheapest = min(priced, key=lambda x: x[1])
        if lo >= cheapest:
            always.append((defname, label, lo, hi, cheapest, cheapest_name, len(unpriced)))
        elif hi >= cheapest:
            odds = (hi - cheapest) / (hi - lo) if hi > lo else 0.0
            sometimes.append((defname, label, lo, hi, cheapest, cheapest_name, odds))
        else:
            never.append((defname, label, lo, hi, cheapest,
                          "cheapest tagged weapon is %s at %g" % (cheapest_name, cheapest)))

    def show(title, items, fmt):
        if not items:
            return
        print("%s (%d)" % (title, len(items)))
        for it in items:
            print("   " + fmt(it))
        print()

    show("🔴 NEVER ARMS - the ceiling is below every weapon it can hold", never,
         lambda i: "%-30s %-26s money %g~%g   %s" % (i[0], i[1], i[2], i[3], i[5]))
    show("🟠 ARMS ONLY SOMETIMES - fails a 5/5 criterion", sometimes,
         lambda i: "%-30s %-26s money %g~%g   cheapest %s at %g   armed %.0f%% of rolls"
                   % (i[0], i[1], i[2], i[3], i[5], i[4], i[6] * 100))
    show("🔴 NO weaponTags AT ALL - needs a tag chosen, not a range widened", notags,
         lambda i: "%-30s %-26s" % (i[0], i[1]))
    show("⚠️ UNMEASURED - tagged weapons exist but none reports a MarketValue", unmeasured,
         lambda i: "%-30s %-26s money %g~%g   %d tagged weapon(s), no price in the dump"
                   % (i[0], i[1], i[2], i[3], i[4]))
    if args.verbose:
        show("✅ ALWAYS ARMS", always,
             lambda i: "%-30s %-26s money %g~%g   cheapest %s at %g%s"
                       % (i[0], i[1], i[2], i[3], i[5], i[4],
                          ("   (+%d unpriced)" % i[6]) if i[6] else ""))

    bad = len(never) + len(sometimes) + len(notags)
    print("always arms %d · sometimes %d · never %d · no tags %d · unmeasured %d"
          % (len(always), len(sometimes), len(never), len(notags), len(unmeasured)))
    if unmeasured:
        print("⚠️ UNMEASURED kinds are NOT counted as failures and NOT counted as passes. "
              "Read those weapon defs directly.")
    if bad == 0:
        print("\nEvery measurable kind arms on every roll.")
    else:
        print("\n%d kind(s) can spawn bare. The roster's criterion is 5/5 armed." % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
