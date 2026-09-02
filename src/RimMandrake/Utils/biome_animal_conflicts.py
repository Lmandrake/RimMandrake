# -*- coding: utf-8 -*-
"""biome_animal_conflicts.py - every (biome, animal) pair registered TWICE.

WHY THIS EXISTS WHEN animal_inventory.py ALREADY DID THIS
========================================================
RimWorld builds each biome's animal table in `BiomeDef.CommonalityOfAnimal()` by
adding to a Dictionary keyed on PawnKindDef. An animal reaches a biome from two
directions - the biome's `wildAnimals`, and the animal's `race.wildBiomes` - and
if the same pair arrives from BOTH, `Dictionary.Add` throws
`ArgumentException: An item with the same key has already been added`.

That exception is not contained. Measured on this stack: Choose Wild Animal
Spawns DIES in its static constructor, Giddy-Up's biome cache never completes,
and Biome Compatibility Project aborts the rest of the post-load queue.

`Utils/animal_inventory.py` answers this question by reading mod XML, and on
2026-08-26 it reported **3** conflicts while the game was throwing on
**JRWTorosaurus**, which was not one of them. The reason is structural and it is
not a bug in that script: **the collisions are created by PatchOperations.**
`More Vanilla Biomes/Patches/Jurassic Rimworld.xml` adds ZBiome_Badlands to the
Torosaurus's wildBiomes; our own generated `BiomeCast_Ashkarr.xml` adds the
Torosaurus to ZBiome_Badlands's wildAnimals. Neither def says so on disk. A
pre-patch reader cannot see either.

So this one reads the DEF DUMP CAPTURE, which is taken from the running game
after every patch has applied. It is the same question asked of the only source
that can answer it.

VALIDATED AGAINST A KNOWN ANSWER, which is the rule for any instrument here:
the 2026-08-26 log names 12 duplicate keys, one per biome (each biome's cache
throws at its FIRST collision and stops). This script finds all 12, in the same
12 biomes - plus 15 more the game never reached. Fixing only what the log names
would have surfaced those one load at a time.

USAGE
    python3 src/RimMandrake/Utils/biome_animal_conflicts.py            # list them
    python3 src/RimMandrake/Utils/biome_animal_conflicts.py --xml OUT  # emit the patch
    python3 src/RimMandrake/Utils/biome_animal_conflicts.py --capture <dir>
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

CAPTURES = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
            "RimWorld by Ludeon Studios/DefDump/captures")


def newest_capture(root=CAPTURES):
    if not os.path.isdir(root):
        return None
    subs = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    return os.path.join(root, subs[-1]) if subs else None


def conflicts(capture):
    """[(biome, pawnKind, raceDefName)] for every pair registered twice.

    Returns None if the capture cannot be read - the caller must report
    UNMEASURED rather than "no conflicts".
    """
    def load(name):
        p = os.path.join(capture, "defs", name)
        if not os.path.isfile(p):
            return None
        try:
            with open(p, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return None

    bio, kinds, things = load("BiomeDef.json"), load("PawnKindDef.json"), load("ThingDef.json")
    if not bio or not kinds or not things:
        return None

    # (a) the biome's own list
    a_side = collections.defaultdict(set)
    for r in bio["defs"]:
        for rec in (r["fields"].get("wildAnimals") or []):
            if isinstance(rec, dict) and rec.get("animal"):
                a_side[r["defName"]].add(rec["animal"])

    # every PawnKindDef of a race, because the dictionary key is the KIND
    race_kinds = collections.defaultdict(list)
    for k in kinds["defs"]:
        race = k["fields"].get("race")
        if isinstance(race, str):
            race_kinds[race].append(k["defName"])

    # (b) the animal's own list, mapped back to kinds
    #
    # 🔑 CHECKED 2026-09-02 (DUMP_DERIVED_SHEETS_SHOW_CUT_1 sweep): this capture is
    # pre-Cherry-Picker in general, but Cherry Picker neuters a cut animal's
    # `race.wildBiomes` to empty IN PLACE (same pattern as `weapon_tag_audit.py`
    # stripping `weaponTags`) - measured on the 2026-09-02T19-36-08Z capture, 0 of
    # 281 cut animals with a `race` block carry any `wildBiomes` entry, while the
    # BIOME side (`a_side` above, `wildAnimals`) still lists 21,870 cut-pawnkind
    # entries untouched. Since a reported conflict requires BOTH sides to name the
    # same pair, a cut animal can never source the `b_side` half and this join
    # cannot manufacture a phantom conflict from cut content - no cherrypicker.py
    # filter is needed here. Re-measure before trusting this if Cherry Picker's
    # neuter behaviour ever changes what it strips.
    b_side = collections.defaultdict(dict)      # biome -> {kind: raceDefName}
    for t in things["defs"]:
        race = t["fields"].get("race")
        if not isinstance(race, dict):
            continue
        wb = race.get("wildBiomes")
        if not wb:
            continue
        biomes = wb.keys() if isinstance(wb, dict) else [
            x.get("biome") for x in wb if isinstance(x, dict)]
        for b in biomes:
            for kd in race_kinds.get(t["defName"], []):
                b_side[b][kd] = t["defName"]

    out = []
    for b, kinds_a in a_side.items():
        for kd in sorted(kinds_a & set(b_side.get(b, {}))):
            out.append((b, kd, b_side[b][kd]))
    return sorted(out)


HEADER = """<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  AnimalBiomeDuplicates_Generated.xml    GENERATED - do not hand-edit
  ============================================================================
  Regenerate with biome_animal_conflicts.py, flag `xml`, writing to this path:
      python3 src/RimMandrake/Utils/biome_animal_conflicts.py
  (⛔ the flags are spelled with two hyphens, which XML forbids inside a comment,
   so they are named rather than written out here. See the script's docstring.)

  Companion to AnimalBiomeDuplicates_Fix.xml, which holds the three
  hand-verified pairs from 2026-08-10 and is still correct. This file holds the
  rest, computed from the def dump CAPTURE - i.e. from the game after every
  PatchOperation has applied, which is the only place these are visible.

  THE BUG: BiomeDef.CommonalityOfAnimal() adds to a Dictionary keyed on
  PawnKindDef. An animal listed by BOTH the biome (wildAnimals) and itself
  (race.wildBiomes) is added twice and Add() throws ArgumentException. It is not
  contained: Choose Wild Animal Spawns dies in its static constructor, Giddy-Up's
  biome cache never completes, Biome Compatibility Project aborts the post-load
  queue.

  THE FIX, unchanged from the hand-written file: always remove the ANIMAL side.
  The animal still spawns in that biome, at the biome's own commonality, so
  nothing is lost - only the duplicate registration.

  Every op is a PatchOperationConditional, so a mod that is not loaded, or an
  author who fixes their def, turns it into a no-op instead of a red error.
  ⚠️ Load Jawa_Patches LAST: several of these pairs are themselves created by
  another mod's patch, and the conditional must run after it.
%(prov)s-->
<Patch>
%(ops)s</Patch>
"""

OP = """
  <!-- %(n)d. %(kind)s x %(biome)s   (race %(race)s) -->
  <Operation Class="PatchOperationConditional">
    <xpath>/Defs/ThingDef[defName="%(race)s"]/race/wildBiomes/%(biome)s</xpath>
    <match Class="PatchOperationRemove">
      <xpath>/Defs/ThingDef[defName="%(race)s"]/race/wildBiomes/%(biome)s</xpath>
    </match>
  </Operation>
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", default=None)
    ap.add_argument("--xml", default=None, help="write the patch file here")
    a = ap.parse_args(argv)

    cap = a.capture or newest_capture()
    if not cap:
        print("UNMEASURED: no def dump capture found under\n  " + CAPTURES)
        return 2
    rows = conflicts(cap)
    if rows is None:
        print("UNMEASURED: capture " + cap + " could not be read "
              "(BiomeDef.json, PawnKindDef.json and ThingDef.json are all required).")
        return 2

    print("capture: " + os.path.basename(cap))
    print("%d duplicate (biome, pawnKind) pair(s) across %d biome(s)"
          % (len(rows), len({r[0] for r in rows})))
    for b, k, race in rows:
        print("  %-30s %-30s race=%s" % (b, k, race))

    if a.xml:
        # One op per RACE+biome: two kinds of the same race collide on the same
        # node, and removing it twice is an error, not a double fix.
        seen, ops, n = set(), [], 0
        for b, k, race in rows:
            if (race, b) in seen:
                continue
            seen.add((race, b))
            n += 1
            ops.append(OP % {"n": n, "kind": k, "biome": b, "race": race})
        prov = ("  Generated from capture %s\n  %d pair(s) -> %d operation(s).\n"
                % (os.path.basename(cap), len(rows), n))
        with open(a.xml, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(HEADER % {"prov": prov, "ops": "".join(ops)})
        print("\nwrote %d operation(s) -> %s" % (n, a.xml))
    return 0


if __name__ == "__main__":
    sys.exit(main())
