#!/usr/bin/env python3
"""label_collision_check.py — no CAST animal may share a `label` with another
CAST animal under a different `defName`.

WHY
===
`DUPLICATE_CANON_DEFNAME_PAIRS_1`: four canon animals (gizka, kreetle, nuna,
worrt) shipped under TWO defNames each — the donor mod's own bare defName
(`Gizka`) AND our `RSW_` port (`RSW_Gizka`) — wired into different biomes'
`wildAnimals` at the same time. Same creature, same label, same texPath,
reachable under two identities. The forensic pass that found this
(`Transient/duplicate_canon_pairs_desktop_2026-09-23.md`) had to read four
donor def bodies by hand against four of ours; nothing caught it earlier
because nothing checked for it. This is that check, extended to every animal
rather than four names.

THE RULE
========
Build the set of animal defNames actually CAST by any BiomeDef we can see in
the dump (wildAnimals + coastalWildAnimals + pollutionWildAnimals — the three
arrays `BiomeDef.CommonalityOfAnimal()` walks). Group that cast set by each
defName's `ThingDef.label`. Any label backed by more than one distinct
defName is a collision: the player can meet "the same creature" twice under
different names, exactly the DUPLICATE_CANON_DEFNAME_PAIRS_1 defect shape.

An uncast ThingDef (e.g. the donor's bare `Gizka`, kept installed but no
longer wired into anything per that item's own ruling: "Mlie's mod stays
installed; its defs simply stop being cast by us") is NOT a collision — it is
inert. Only CAST duplicates are reachable by a player, which is what this
checker exists to catch; a raw label scan over every ThingDef in the dump
would permanently false-positive on every donor mod we keep installed but
stop casting.

SOURCE OF THE DATA
===================
`defs.sqlite` via `dump_manifest.dump_db`, same locator seam as
`ecosystem_pyramid_check.py` — never a JSON directory walk, never grep. If the
db is unavailable this refuses with UNMEASURED rather than reporting a false
clean sweep.

USAGE
    python3 src/RimMandrake/Utils/label_collision_check.py
    python3 src/RimMandrake/Utils/label_collision_check.py --dump <capture dir>

Exit codes: 0 no collision, 1 one or more collisions found, 2 UNMEASURED (the
dump/db could not be read at all).
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dump_manifest import dump_db                    # noqa: E402
from game_paths import DUMP_ROOT                       # noqa: E402

CAST_FIELDS = ("wildAnimals", "coastalWildAnimals", "pollutionWildAnimals")


@dataclass
class Collision:
    label: str
    defnames: list                        # sorted list of defNames sharing this label
    cast_in: dict = field(default_factory=dict)   # defName -> sorted [biomeDefName, ...]


def animal_label_index(db):
    """{defName: label} for every ThingDef carrying a `race` block (i.e. a
    pawn race, the only kind CommonalityOfAnimal() cares about)."""
    recs = db.records("ThingDef")
    if not recs.ok:
        raise RuntimeError("ThingDef slice unavailable: %s" % recs.line())
    out = {}
    for r in recs.unwrap():
        fields = r.get("fields") or {}
        if not isinstance(fields.get("race"), dict):
            continue
        label = r.get("label") or fields.get("label")
        if label:
            out[r["defName"]] = label
    if not out:
        raise RuntimeError(
            "ThingDef slice parsed to zero race-bearing labels — the field "
            "moved, or the capture never reached it. Refusing a run that "
            "would report every biome as collision-free for the wrong reason.")
    return out


def cast_animals(db):
    """{defName: [biomeDefName, ...]} for every animal wired into ANY
    BiomeDef's wildAnimals/coastalWildAnimals/pollutionWildAnimals, across
    every BiomeDef in the dump — donor and ours alike, since a player can
    walk into either."""
    recs = db.records("BiomeDef")
    if not recs.ok:
        raise RuntimeError("BiomeDef slice unavailable: %s" % recs.line())
    out = defaultdict(set)
    n_biomes = 0
    for r in recs.unwrap():
        n_biomes += 1
        biome = r.get("defName", "")
        fields = r.get("fields") or {}
        for field_name in CAST_FIELDS:
            for e in (fields.get(field_name) or []):
                if isinstance(e, dict) and e.get("animal"):
                    out[e["animal"]].add(biome)
    if n_biomes == 0:
        raise RuntimeError(
            "zero BiomeDef records in this capture — refusing a run that "
            "would report a clean 0-collision sweep over nothing.")
    return {k: sorted(v) for k, v in out.items()}


def find_collisions(labels, cast):
    """Pure logic, unit-testable without a live dump.

    `labels`: {defName: label} (need not cover every cast defName — an
    unresolved defName is excluded, same UNRESOLVED handling as
    ecosystem_pyramid_check.py, never guessed into a group).
    `cast`: {defName: [biomeDefName, ...]}
    Returns sorted [Collision, ...].
    """
    by_label = defaultdict(list)
    for defname in cast:
        label = labels.get(defname)
        if label is None:
            continue
        by_label[label].append(defname)

    out = []
    for label, defnames in by_label.items():
        distinct = sorted(set(defnames))
        if len(distinct) < 2:
            continue
        out.append(Collision(
            label=label, defnames=distinct,
            cast_in={d: cast[d] for d in distinct}))
    return sorted(out, key=lambda c: c.label)


def run(dump_dir=None):
    """Returns list[Collision]. Raises RuntimeError (UNMEASURED-prefixed on
    an unusable dump) otherwise — same shape as ecosystem_pyramid_check.run()."""
    dump_dir = dump_dir or DUMP_ROOT
    db_unusable = False
    inner_error = None
    labels = cast = None
    # Do not raise from inside `with dump_db(...)` — see ecosystem_pyramid_check.py's
    # comment on the same trap (dump_manifest swallows an exception raised in the
    # block and re-yields, masking the real error).
    with dump_db(dump_dir) as db:
        if db is None:
            db_unusable = True
        else:
            try:
                labels = animal_label_index(db)
                cast = cast_animals(db)
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

    return find_collisions(labels, cast)


def report(collisions, out=sys.stdout):
    if not collisions:
        print("ok    no CAST animal shares a label with another CAST animal "
              "under a different defName.", file=out)
        return
    print("FAIL  %d label collision(s) — the same creature is reachable "
          "under two defNames:" % len(collisions), file=out)
    for c in collisions:
        print("\n  label %r:" % c.label, file=out)
        for d in c.defnames:
            print("    %-24s cast in: %s" % (d, ", ".join(c.cast_in[d])), file=out)
    print("\n  Pick a survivor defName, repoint every wildAnimals row (and any "
          "generated patch) from the loser to the survivor, and see "
          "DUPLICATE_CANON_DEFNAME_PAIRS_1 for the worked example.", file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dump", help="DefDump capture dir (default: newest / DUMP_ROOT)")
    args = ap.parse_args(argv)

    try:
        collisions = run(dump_dir=args.dump)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report(collisions)
    return 1 if collisions else 0


if __name__ == "__main__":
    sys.exit(main())
