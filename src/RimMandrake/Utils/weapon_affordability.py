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
import dump_projection  # noqa: E402
ROSTER_GEN = os.path.join(HERE, "gen_pawnkind_roster.py")
ROSTER_XML = os.path.join(
    ROOT, "src", "Jawa", "Jawa_Patches", "Defs", "PawnKindDefs", "JawaFactionRoster.xml")

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
    """-> {tag: [(defName, price or None, was_computed), ...]}

    🔴 A PROJECTION, NOT A GRAPH LOAD. This used to `json.load` the whole of
    `defs/ThingDef.json` — 24,904 records, ~316 MB of text — for five fields.
    Measured cost of that: **2.7 s and 1.50 GB resident**.

    ⚠️ Unlike `weapon_tag_audit`, this one genuinely needs EVERY def and not just
    the weapons: `base_market_value` recurses through `costList` into arbitrary
    materials and cannot know in advance which it will reach. So the win here is
    memory, not the clock — six fields per record instead of the whole record.
    `dump_projection.cost_graph` carries the numbers, and falls back to reading
    the JSON when no `defs.sqlite` exists.
    """
    path = os.path.join(dump, "ThingDef.json")
    if not os.path.isfile(path):
        die("no ThingDef.json at " + path)
    index, tagged = dump_projection.weapon_cost_index(dump)
    memo = {}
    by_tag = {}
    for defname, tags in tagged:
        f = (index.get(defname) or {}).get("fields") or {}
        declared = _stat(f, "MarketValue")
        mv = float(declared) if declared is not None else base_market_value(defname, index, memo)
        for t in tags:
            by_tag.setdefault(t, []).append((defname, mv, declared is None))
    return by_tag


def load_roster():
    """Read weaponMoney and weaponTags off the EMITTED XML - the file that deploys.

    🔴 THIS USED TO READ THE GENERATOR'S `R` TABLE AND THAT WAS WRONG, measured
    2026-08-27. `gen_pawnkind_roster.py` has TWO tables and only one of them is
    emitted: `KIT` carries "everything from <weaponMoney> onward, verbatim" and is
    what lands in the XML, while `R` supplies only defName/label/combatPower. `R`'s
    `wm` and `weaponTags` fields are a SHADOW - nothing reads them into the game -
    and they had drifted on 9 of 48 kinds' budgets and 1 kind's tags, including the
    documented `Jawa_Empire_Grunt` fix (950~1150 with `ORImperialLight` dropped,
    which `R` still recorded as 650~780 with the tag present).

    ⇒ This tool reported `always arms 48 · unmeasured 0` off numbers the game had
    not used since 2026-08-23. It was not wrong about what it read; it was reading
    an artifact the game never loads.

    🔑 The emitted XML is the right source for three reasons: it is what deploys, it
    declares min AND max explicitly so no `wm * 1.2` has to be inferred, and it
    cannot drift from itself. `drift_vs_shadow()` still reads `R` - only to report
    that the shadow has rotted, never to compute an answer from it.
    """
    import xml.etree.ElementTree as ET
    if not os.path.isfile(ROSTER_XML):
        die("no emitted roster at " + ROSTER_XML)
    rows = []
    for d in ET.parse(ROSTER_XML).getroot():
        dn = d.findtext("defName")
        if not dn or not dn.startswith("Jawa_"):
            continue
        wm = d.findtext("weaponMoney")
        wt = d.find("weaponTags")
        tags = [li.text for li in wt] if wt is not None else []
        if not wm or "~" not in wm:
            continue
        lo, hi = (float(x) for x in wm.split("~", 1))
        rows.append((dn, d.findtext("label") or dn, lo, hi, tags))
    if not rows:
        die("parsed no Jawa_ kinds out of " + ROSTER_XML)
    return rows


def drift_vs_shadow(rows):
    """Report where the generator's dead `R` table disagrees with what is emitted.

    ⚠️ This computes NOTHING. It exists because a stale shadow table is exactly how
    this tool came to publish a clean bill about the wrong numbers, and because the
    next reader will otherwise trust `R` the same way. A drift line is a note, not a
    failure: `R`'s wm/weaponTags are unused, so drift costs nothing until somebody
    reads them - which is precisely what happened.
    """
    try:
        src = open(ROSTER_GEN, "r", encoding="utf-8").read()
        m = re.search(r"^R = \[$(.*?)^\]$", src, re.S | re.M)
        if not m:
            return ["could not find the `R = [` table - shadow check skipped"]
        shadow = eval("[" + m.group(1) + "]", {"__builtins__": {}}, {})
    except Exception as e:                                        # noqa: BLE001
        return ["shadow check UNMEASURED (%s)" % e]
    live = {dn: (lo, hi, tags) for dn, _lab, lo, hi, tags in rows}
    out = []
    for fac, role, _label, wm, _am, _q, tags, _req in shadow:
        dn = "Jawa_%s_%s" % (fac, role)
        if dn not in live:
            out.append("%-28s in R, absent from the emitted XML" % dn)
            continue
        lo, hi, ltags = live[dn]
        if abs(float(wm) - lo) > 0.5 or abs(float(wm) * 1.2 - hi) > 0.5:
            out.append("%-28s money  R %g~%g   emitted %g~%g"
                       % (dn, float(wm), float(wm) * 1.2, lo, hi))
        if sorted(tags) != sorted(ltags):
            out.append("%-28s tags   R %s   emitted %s" % (dn, tags, ltags))
    return out


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
    print("pawn kinds in the roster: %d, read from the EMITTED XML\n" % len(rows))
    drift = drift_vs_shadow(rows)
    if drift:
        print("\u26a0\ufe0f  the generator's dead `R` shadow table disagrees with what is "
              "emitted, on %d point(s).\n   Nothing here is computed from `R` - this is a "
              "note so the next reader does not trust it:" % len(drift))
        for line in drift:
            print("   " + line)
        print()

    always, sometimes, never, notags, unmeasured = [], [], [], [], []

    for row in rows:
        defname, label, lo, hi, tags = row

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

    # 🔴 THIN HEADROOM IS THE ONLY SIGNAL LEFT, AND THIS TOOL WAS THROWING IT AWAY.
    # A kind passes "always arms" on `lo >= cheapest`, but this file's own header says
    # the prices here are a FLOOR: the engine compares `ThingStuffPair.Price`, which
    # carries the stuff cost, while these are unstuffed `MarketValue`. So a PASS with
    # a 1% margin is not the same answer as a PASS with a 900% one, and printing both
    # as "always arms" is what let 16 kinds roll bare live under a clean bill.
    # ⚠️ THIS IS AN ASSOCIATION, NOT A PROVEN MECHANISM. It is offered as the shortlist
    # to look at first, never as the cause. The measured cause of 13 of 21 bare pawns
    # is a violence-disabling backstory, which has nothing to do with money.
    thin = []
    for defname, label, lo, hi, cheapest, cheapest_name, _unp in always:
        margin = (lo - cheapest) / cheapest if cheapest else float("inf")
        if margin < 0.25:
            thin.append((defname, label, lo, cheapest, cheapest_name, margin))
    thin.sort(key=lambda x: x[5])
    show("\u26a0\ufe0f THIN HEADROOM - passes, but by less than 25% over the cheapest "
         "UNSTUFFED price", thin,
         lambda i: "%-30s %-26s min %g vs %s at %g   margin %+.1f%%"
                   % (i[0], i[1], i[2], i[4], i[3], i[5] * 100))

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
