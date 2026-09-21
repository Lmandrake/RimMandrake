#!/usr/bin/env python3
"""ecosystem_pyramid_check.py — enforce the food-pyramid law going forward.

WHY
===
`ECOSYSTEM_PYRAMID_LAW_1` (infrastructure/state/items/ECOSYSTEM_PYRAMID_LAW_1.md):
the owner ruled every biome's wildAnimals roster needs small fauna carrying
**>= 50% of the roster's total commonality**. 9 of our 24 biome rosters failed it
2026-09-20 and were lifted — but the lift was done with a one-off sweep script
that left no artifact, no selftest and nothing that runs again. The next roster
edit can silently break the law and nothing will say so. This is that checker.

THE RULE, exactly as canon.yml records it (`ecosystem_laws.food_pyramid`)
==========================================================================
    every biome's wildAnimals roster needs small fauna (race.baseBodySize < 1.0)
    carrying >= 50% of the roster's total commonality (weight = commonality,
    not def count)

This script reads the threshold FROM canon.yml rather than hardcoding 50 a
second time — a future re-ruling changes one file, not two.

WHAT "small" MEANS, AND ON WHAT AUTHORITY
==========================================
`race.baseBodySize` is a single scalar on the RACE, already the FULL-GROWN
("adult") size RimWorld itself uses for game mechanics — a pawn's actual
bodySize at a given age is `baseBodySize * currentLifeStage.bodySizeFactor`,
so baseBodySize is never a baby measurement to begin with. This is NOT the
`lifeStages[0]`-is-the-baby trap that bites TEXTURE reads (see
animal_contact_sheet.py) — that trap is about `PawnKindDef.lifeStages[]`, a
list of per-stage art, a completely different field. Verified against the live
dump 2026-08-20: `Rat` (a known-small vanilla animal) reads baseBodySize 0.2.
SMALL = baseBodySize < 1.0 (below a human). LARGE = >= 1.0. This is exactly the
band the item's own owner-reviewed sweep used, and the threshold ruling ("50%
small") was made by the owner looking AT that sweep's numbers — so re-deriving
the band any other way would silently invalidate the ruling it is enforcing.

⚠️ An animal whose ThingDef does not resolve, or resolves with no `race` block
(e.g. droids wandering as wildlife — see the item's "side finding"), is
UNRESOLVED: it is named in the roster but excluded from both bands, its
commonality does not enter the small/large sums, and it is reported by name.
Silently treating it as either band would be a guess this file forbids.

SCOPE: which biomes get checked
================================
Every `BiomeDef` we own — `defName` starting `RUT_` (RimUtinni tier; see
NAMING_SCHEME_PLAN.md). This is exactly the set the item's own sweep covered
(as RUT_*), re-derived live rather than pinned to the 24 names the sweep
happened to see — biomes get added (4 more exist today than the item's sweep
saw: RUT_BlueDesert, RUT_Jawa_BackgroundWater, RUT_LanternDeeps,
RUT_PropaneLake) and a pinned list would silently stop covering them.

⚠️ ZERO ROWS IS A FAILURE, NOT A FOOTNOTE. A biome with an empty wildAnimals
list (RUT_BlueDesert, RUT_Jawa_BackgroundWater today) has no small-fauna share
to report — 0/0 is undefined, not 100% and not "skip". The owner explicitly
ruled OUT an exemption for near-empty rosters ("a habitat with 1-6 animals is
judged by the same 50% bar as any other"), so an EMPTY roster is reported
loudly as its own verdict and FAILS the gate rather than being silently
skipped or silently passed.

SOURCE OF THE DATA
===================
`defs.sqlite` via the `measuring-large-artifacts` skill's `DumpDB`, through this
repo's one locator seam (`dump_manifest.dump_db`) — never a JSON directory walk,
never grep. If the skill or the built db is unavailable, this refuses with
UNMEASURED rather than reporting a false PASS or FAIL.

USAGE
    python3 src/RimMandrake/Utils/ecosystem_pyramid_check.py
    python3 src/RimMandrake/Utils/ecosystem_pyramid_check.py --dump <capture dir>

Exit codes: 0 all PASS, 1 one or more FAIL (including an EMPTY roster), 2
UNMEASURED (the dump/db/canon.yml could not be read at all).
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dump_manifest import dump_db                    # noqa: E402
from game_paths import DUMP_ROOT                       # noqa: E402

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CANON = os.path.join(ROOT, "infrastructure", "state", "canon.yml")

OWNED_PREFIX = "RUT_"                     # biome rosters WE own — see SCOPE above


@dataclass
class BiomeVerdict:
    biome: str
    verdict: str                          # PASS | FAIL | EMPTY
    small_pct: float | None               # None for EMPTY
    small_c: float
    large_c: float
    n_defs: int
    unresolved: list                      # [(animalName, commonality), ...]
    small_entries: list                   # [(animalName, commonality, bodySize), ...]
    large_entries: list                   # [(animalName, commonality, bodySize), ...]
    shortfall_small_c: float = 0.0        # additional SMALL commonality that would pass it


def load_threshold_pct(canon_path=CANON):
    """The ruled floor, read from canon.yml — never re-hardcoded. Raises on
    anything short of a clean read, on purpose: a checker enforcing a ruling
    must not silently invent one when the source of truth is missing."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "PyYAML is not installed, so canon.yml cannot be read.\n"
            "  pip install --user PyYAML") from exc
    with open(canon_path, encoding="utf-8") as fh:
        canon = yaml.safe_load(fh)
    try:
        law = canon["ecosystem_laws"]["food_pyramid"]
        return float(law["threshold_pct"])
    except (KeyError, TypeError) as exc:
        raise RuntimeError(
            "canon.yml has no ecosystem_laws.food_pyramid.threshold_pct — "
            "the law this checker enforces is not recorded there") from exc


def body_size_index(db):
    """{defName: baseBodySize} over every ThingDef carrying a race block.

    🔴 Never returns {} on a partial read without saying so — an empty index
    would make every animal look unresolved, which is the exact false-alarm
    shape this file's own docstring warns against for a missing cast patch.
    """
    recs = db.records("ThingDef")
    if not recs.ok:
        raise RuntimeError("ThingDef slice unavailable: %s" % recs.line())
    out = {}
    for r in recs.unwrap():
        race = (r.get("fields") or {}).get("race")
        if not isinstance(race, dict):
            continue
        bs = race.get("baseBodySize")
        if isinstance(bs, (int, float)):
            out[r["defName"]] = float(bs)
    if not out:
        raise RuntimeError(
            "ThingDef slice parsed to zero race.baseBodySize values — the "
            "field moved, or the capture never reached it. Refusing a run "
            "that would report every animal in every roster as unresolved.")
    return out


def owned_biome_rosters(db):
    """{biomeDefName: [(animal, commonality), ...]} for every BiomeDef we own.

    Includes biomes with an EMPTY wildAnimals list — see SCOPE above. Does not
    filter to a fixed name list, so a newly added RUT_* biome is picked up
    automatically rather than needing this file edited.
    """
    recs = db.records("BiomeDef")
    if not recs.ok:
        raise RuntimeError("BiomeDef slice unavailable: %s" % recs.line())
    out = {}
    for r in recs.unwrap():
        name = r.get("defName", "")
        if not name.startswith(OWNED_PREFIX):
            continue
        wa = (r.get("fields") or {}).get("wildAnimals") or []
        entries = [(e.get("animal"), e.get("commonality"))
                   for e in wa if isinstance(e, dict) and e.get("animal")]
        out[name] = entries
    return out


def evaluate(entries, sizes, threshold_pct):
    """Pure verdict logic over one biome's (animal, commonality) list — no I/O,
    unit-testable without a live dump. `entries` may be empty."""
    unresolved, small, large = [], [], []
    for animal, commonality in entries:
        c = float(commonality) if commonality is not None else 0.0
        bs = sizes.get(animal)
        if bs is None:
            unresolved.append((animal, c))
        elif bs < 1.0:
            small.append((animal, c, bs))
        else:
            large.append((animal, c, bs))

    small_c = sum(c for _, c, _ in small)
    large_c = sum(c for _, c, _ in large)
    total = small_c + large_c

    if not entries or total <= 0:
        return dict(verdict="EMPTY", small_pct=None, small_c=small_c,
                    large_c=large_c, n_defs=len(entries), unresolved=unresolved,
                    small=small, large=large, shortfall=0.0)

    pct = 100.0 * small_c / total
    passed = pct >= threshold_pct
    shortfall = 0.0
    if not passed:
        # Minimum ADDITIONAL small commonality that clears the floor if large_c
        # holds still: small_c' / (small_c' + large_c) >= t  =>
        # small_c' >= t/(1-t) * large_c  (t as a fraction). For t=0.5 this is
        # exactly large_c - small_c, i.e. "match the megafauna".
        t = threshold_pct / 100.0
        if t < 1.0:
            required = (t / (1.0 - t)) * large_c
            shortfall = max(0.0, required - small_c)
    return dict(verdict=("PASS" if passed else "FAIL"), small_pct=pct,
                small_c=small_c, large_c=large_c, n_defs=len(entries),
                unresolved=unresolved, small=small, large=large,
                shortfall=shortfall)


def run(dump_dir=None, threshold_pct=None):
    """Returns (list[BiomeVerdict], threshold_pct). Raises RuntimeError/exits
    UNMEASURED on anything short of a clean measurement — see module docstring."""
    if threshold_pct is None:
        threshold_pct = load_threshold_pct()
    # 🔴 `defs.sqlite` is DERIVED and lives at the DUMP ROOT, never inside a
    # dated capture folder (measure.dumpdb.split_capture_layout's own
    # docstring: "a dump can hold many captures, and the database is not one
    # of them"). `game_paths.DEF_DUMP` is the newest CAPTURE, the wrong thing
    # to hand `dump_db` — it always returns None there. Use DUMP_ROOT.
    dump_dir = dump_dir or DUMP_ROOT
    # 🔴 Do not raise from inside the `with dump_db(...)` block: dump_manifest's
    # contextmanager wraps its body in `except Exception: yield None`, so an
    # exception raised HERE is caught there and it tries to `yield None` a
    # second time — `RuntimeError: generator didn't stop after throw()`,
    # masking the real error entirely. Capture everything, raise after exit.
    db_unusable = False
    inner_error = None
    sizes = rosters = None
    with dump_db(dump_dir) as db:
        if db is None:
            db_unusable = True
        else:
            try:
                sizes = body_size_index(db)
                rosters = owned_biome_rosters(db)
            except RuntimeError as exc:
                inner_error = str(exc)

    if db_unusable:
        raise RuntimeError(
            "UNMEASURED: no usable defs.sqlite at %s (skill not installed, "
            "db not built, or the db is stale against its capture). Run "
            "`measure build` (measuring-large-artifacts skill) against a "
            "current DefDump capture, then re-run this checker." % dump_dir)
    if inner_error is not None:
        raise RuntimeError(inner_error)

    if not rosters:
        raise RuntimeError(
            "UNMEASURED: zero BiomeDef records with defName starting '%s' in "
            "this capture — the prefix changed, or the capture never reached "
            "BiomeDef at all. Refusing a run that would report a clean 0/0 "
            "biome sweep." % OWNED_PREFIX)

    out = []
    for biome in sorted(rosters):
        v = evaluate(rosters[biome], sizes, threshold_pct)
        out.append(BiomeVerdict(
            biome=biome, verdict=v["verdict"], small_pct=v["small_pct"],
            small_c=v["small_c"], large_c=v["large_c"], n_defs=v["n_defs"],
            unresolved=v["unresolved"], small_entries=v["small"],
            large_entries=v["large"], shortfall_small_c=v["shortfall"]))
    return out, threshold_pct


def report(verdicts, threshold_pct, out=sys.stdout):
    fails = [v for v in verdicts if v.verdict != "PASS"]
    print("ECOSYSTEM_PYRAMID_LAW_1 checker — floor %.0f%% small (canon.yml "
          "ecosystem_laws.food_pyramid)" % threshold_pct, file=out)
    print("%-28s %-6s %8s  %8s %8s  %4s %4s" %
          ("biome", "verdict", "small%", "smallC", "largeC", "defs", "unk"),
          file=out)
    for v in verdicts:
        pct_s = "%6.1f%%" % v.small_pct if v.small_pct is not None else "     —"
        print("%-28s %-6s %8s  %8.2f %8.2f  %4d %4d" %
              (v.biome, v.verdict, pct_s, v.small_c, v.large_c, v.n_defs,
               len(v.unresolved)), file=out)

    print("\n%d of %d owned biome roster(s) PASS the %.0f%% floor."
          % (len(verdicts) - len(fails), len(verdicts), threshold_pct), file=out)

    if fails:
        print("\nFAILING / EMPTY — what would fix each:", file=out)
        for v in fails:
            print("\n  %s — %s" % (v.biome, v.verdict), file=out)
            if v.verdict == "EMPTY":
                print("    no wildAnimals entries at all — this roster has no "
                      "small-fauna share to measure; it needs fauna, not a "
                      "reweight.", file=out)
                continue
            print("    %.1f%% small, needs %.0f%%. Existing SMALL entries "
                  "(boost these, don't cut the rest):" % (v.small_pct, ),
                  file=out)
            if v.small_entries:
                for a, c, bs in sorted(v.small_entries, key=lambda e: -e[1]):
                    print("      %-30s commonality %.2f  bodySize %.2f"
                          % (a, c, bs), file=out)
            else:
                print("      (none — this roster has zero small fauna wired)",
                      file=out)
            print("    LARGE entries pulling it down:", file=out)
            for a, c, bs in sorted(v.large_entries, key=lambda e: -e[1]):
                print("      %-30s commonality %.2f  bodySize %.2f"
                      % (a, c, bs), file=out)
            if v.shortfall_small_c > 0:
                print("    needs >= %.2f more small commonality (holding large "
                      "fauna still) to clear the floor." % v.shortfall_small_c,
                      file=out)
            if v.unresolved:
                names = ", ".join(a for a, _ in v.unresolved[:8])
                more = "" if len(v.unresolved) <= 8 else " ..."
                print("    %d unresolved defName(s), EXCLUDED from both bands: "
                      "%s%s" % (len(v.unresolved), names, more), file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dump", help="DefDump capture dir (default: newest)")
    args = ap.parse_args(argv)

    try:
        verdicts, threshold_pct = run(dump_dir=args.dump)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report(verdicts, threshold_pct)
    return 1 if any(v.verdict != "PASS" for v in verdicts) else 0


if __name__ == "__main__":
    sys.exit(main())
