#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""biome_wildbiomes_evictions.py - close the enforcement gap under the biome rosters.

🔴 THE GAP, found 2026-09-09 (BIOME_FAUNA_ASSIGNMENT_SITTING_1, "Enforcement gap the
build lane MUST close"). Replacing a BiomeDef's `wildAnimals` does NOT evict an animal
whose OWN `race.wildBiomes` names that biome with a weight above 0: the load-time padder
(WILD_ANIMALS_PADDED_LISTS_1, suspect kopp.biomecompatibilityproject) materializes those
weights straight back INTO `wildAnimals` at load. So the cast patch alone under-enforces
every eviction the sheets ruled - the roster says a creature is gone and the game spawns
it anyway, with nothing in any log to say so.

⇒ This emits the animal-side removal for every (race, painted biome) pair where the race
is NOT in that biome's roster. Same operation shape the de-dup already uses; the only
difference is which pairs it covers and why.

    python3 src/RimMandrake/Utils/biome_wildbiomes_evictions.py            # list
    python3 src/RimMandrake/Utils/biome_wildbiomes_evictions.py --xml OUT  # emit

WHAT IT IS *NOT*
  ⛔ It never touches a rostered creature. Those pairs are true DUPLICATES (both
     directions register the same key and BiomeDef.CommonalityOfAnimal throws), and they
     belong in AnimalBiomeDuplicates_Generated.xml, which accumulates as a union. Any
     pair already shipped there is skipped here rather than removed twice.
  ⛔ It writes nothing about biomes outside the painted set. An unpainted biome is not
     part of Ash'karr and its rosters are none of our business.

SOURCES, and why it needs both
  · the DISK walk over every installed mod's XML  - sees what a mod DECLARES
  · the newest def dump CAPTURE                   - sees what a PatchOperation CREATES,
    which exists in no file at all (27 such pairs shipped past a disk-only scan on
    2026-08-26)
  Both come from gen_cast_patch._animal_side_biomes(), which already unions them. The
  walk takes minutes over the workshop mount; `--cache FILE` saves and reuses its result
  so a re-run is instant. ⚠️ A cache is a snapshot of a mod set - delete it after any
  mod change or it will confidently describe a stack that no longer exists.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "design", "Jawa", "fauna"))

ROSTERS = os.path.join(REPO, "design", "Jawa", "worldbuilding", "biomes", "rosters")
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
DEDUP = os.path.join(REPO, "src", "RimUtinni", "UtinniPatches", "Patches",
                     "AnimalBiomeDuplicates_Generated.xml")
DEDUP_HAND = os.path.join(REPO, "src", "RimUtinni", "UtinniPatches", "Patches",
                          "AnimalBiomeDuplicates_Fix.xml")

PAIR_RE = re.compile(
    r'/Defs/ThingDef\[defName="([^"]+)"\]/race/wildBiomes/([A-Za-z0-9_]+)')


def painted_defs():
    """Every BiomeDef painted on Ash'karr, from the frozen tile CSV, plus the rosters'.

    🔑 The CSV wins over any doc (canon.yml rule 1) - it is the paint. The rosters add
    one name the paint no longer carries: `BiomeGRimond`, which `the_blue_desert.json`
    still binds alongside `RUT_BlueDesert` while the world switch settles. Including it
    costs nothing (an unpainted biome cannot appear in this world) and stops the
    eviction silently lapsing if the switch is rolled back.
    """
    import csv
    from verify_frozen import warn_if_stale
    warn_if_stale(TILES)
    with open(TILES, encoding="utf-8") as fh:
        out = {r["biome"] for r in csv.DictReader(fh)}
    out -= {"Ocean", "Lake"}
    for fp in sorted(glob.glob(os.path.join(ROSTERS, "*.json"))):
        if os.path.basename(fp).startswith("_"):
            continue
        with open(fp, encoding="utf-8") as fh:
            out |= set(json.load(fh).get("defNames") or [])
    return out


def rostered():
    """biome -> {pawnKind defName the roster admits}. Injection layers add, never replace."""
    out = collections.defaultdict(set)
    for fp in sorted(glob.glob(os.path.join(ROSTERS, "*.json"))):
        if os.path.basename(fp).startswith("_"):
            continue
        with open(fp, encoding="utf-8") as fh:
            d = json.load(fh)
        for b in d.get("defNames") or []:
            for f in d.get("fauna") or []:
                out[b].add(f["def"])
    return out


def already_removed():
    """{(race, biome)} the shipped de-dup files already strip."""
    out = set()
    for p in (DEDUP, DEDUP_HAND):
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as fh:
                out |= set(PAIR_RE.findall(fh.read()))
    return out


def race_to_kinds():
    """race ThingDef defName -> [PawnKindDef defName], from the newest usable capture.

    The roster names KINDS; `wildBiomes` lives on the RACE. A race whose kinds are all
    absent from the roster is evicted; a race with even ONE rostered kind is left alone,
    because removing its wildBiomes entry could starve a kind we did cast.
    """
    from dumppath import captures_newest_first
    for cap in captures_newest_first():
        f = os.path.join(cap, "defs", "PawnKindDef.json")
        if not os.path.isfile(f):
            continue
        with open(f, encoding="utf-8") as fh:
            pl = json.load(fh)
        pl = pl if isinstance(pl, list) else pl.get("defs") or []
        out = collections.defaultdict(list)
        for k in pl:
            if isinstance(k, dict) and isinstance(k["fields"].get("race"), str):
                out[k["fields"]["race"]].append(k["defName"])
        return out, os.path.basename(cap)
    return None, None


def live_races():
    """{ThingDef defName} the RUNNING game has, from the newest capture.

    🔴 WHY THIS FILTER EXISTS. The disk walk reads every INSTALLED mod, active or not -
    Animals Expanded is on disk here and not in the mod list, and its 127 races produced
    127 removals for defs no load will ever see. Harmless at runtime (a conditional
    whose xpath finds nothing is a no-op) but validate_patch.py counts each one as an
    error against the live dump, and 254 errors is a wall that hides a real one.

    Returns None if no capture carries ThingDef.json; the caller then keeps every pair
    rather than silently emitting an empty patch.
    """
    from dumppath import captures_newest_first
    for cap in captures_newest_first():
        f = os.path.join(cap, "defs", "ThingDef.json")
        if not os.path.isfile(f):
            continue
        with open(f, encoding="utf-8") as fh:
            td = json.load(fh)
        td = td if isinstance(td, list) else td.get("defs") or []
        return {t["defName"] for t in td if isinstance(t, dict)}
    return None


def animal_side(cache=None):
    if cache and os.path.isfile(cache):
        with open(cache, encoding="utf-8") as fh:
            print("   animal-side: reusing cache %s (delete it after any mod change)"
                  % cache)
            return {b: set(v) for b, v in json.load(fh).items()}
    from gen_cast_patch import _animal_side_biomes
    aside = _animal_side_biomes()
    if cache:
        with open(cache, "w", encoding="utf-8") as fh:
            json.dump({b: sorted(v) for b, v in aside.items()}, fh)
    return aside


HEADER = """<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  BiomeCastEvictions_WildBiomes.xml      GENERATED - do not hand-edit
  ============================================================================
  Regenerate:  python3 src/RimMandrake/Utils/biome_wildbiomes_evictions.py
               with the flag that names an output path (two hyphens, `xml`, which
               XML forbids inside a comment so it is named rather than written).

  SOURCE     design/Jawa/worldbuilding/biomes/rosters/*.json - every pair below is
             (a creature declaring a painted biome in its own race.wildBiomes) that
             (that biome's roster does not admit). Nothing here is a judgement call:
             the roster is the whole rule.
  AUTHORITY  BIOME_FAUNA_ASSIGNMENT_SITTING_1, owner cards 2026-09-09; the gap this
             closes is recorded in that item as "Enforcement gap the build lane MUST
             close", 2026-09-09.

  WHY IT IS NEEDED AT ALL. Replacing a BiomeDef's wildAnimals does not evict an animal
  whose own race.wildBiomes names that biome above 0: the load-time padder materializes
  those weights back INTO wildAnimals at load, so the cast patch alone under-enforces
  every eviction the sheets ruled. Removing the animal-side field is what actually
  starves it. Our own cast never reads wildBiomes - it writes wildAnimals directly - so
  this can never remove anything we cast.

  DIRECTION is always the ANIMAL side, never our roster. Rostered creatures are
  untouched here; where one collides from both directions that is a DUPLICATE and it
  lives in AnimalBiomeDuplicates_Generated.xml, which accumulates as a union. Pairs
  already shipped there are skipped rather than removed twice.

  Every operation is a PatchOperationConditional, so an absent mod or an author who
  fixes their def turns it into a no-op instead of a red error. ⚠️ Load this mod LAST:
  several of these entries are themselves created by another mod's PatchOperation, and
  the conditional must run after it. A xpath reporting 0 nodes on disk is EXPECTED for
  exactly those - their evidence is the capture, not the validator.
%(prov)s-->
<Patch>
%(ops)s</Patch>
"""

OP = """
  <!-- %(n)d. %(race)s x %(biome)s -->
  <Operation Class="PatchOperationConditional">
    <xpath>/Defs/ThingDef[defName="%(race)s"]/race/wildBiomes/%(biome)s</xpath>
    <match Class="PatchOperationRemove">
      <xpath>/Defs/ThingDef[defName="%(race)s"]/race/wildBiomes/%(biome)s</xpath>
    </match>
  </Operation>
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", default=None, help="write the patch file here")
    ap.add_argument("--cache", default=None,
                    help="save/reuse the animal-side scan (minutes) at this path")
    a = ap.parse_args(argv)

    kinds, cap = race_to_kinds()
    if kinds is None:
        print("UNMEASURED: no capture with a PawnKindDef.json - refusing to guess which "
              "kinds a race owns, because a wrong answer here EVICTS A CAST CREATURE.")
        return 2
    painted = painted_defs()
    roster = rostered()
    shipped = already_removed()
    aside = animal_side(a.cache)

    live = live_races()
    if live is None:
        print("⚠️ UNMEASURED: no capture carries ThingDef.json, so installed-but-inactive "
              "mods cannot be filtered out. Every pair is emitted.")

    rows, kept, dup, dead = [], 0, 0, 0
    for b in sorted(painted):
        for race in sorted(aside.get(b, ())):
            mine = roster.get(b, set())
            if any(k in mine for k in kinds.get(race, [race])) or race in mine:
                kept += 1                       # rostered: the de-dup file's business
                continue
            if (race, b) in shipped:
                dup += 1
                continue
            if live is not None and race not in live:
                dead += 1                       # installed on disk, not in the mod list
                continue
            rows.append((race, b))

    print("capture: %s · %d painted def(s) · %d roster admission(s)"
          % (cap, len(painted), sum(len(v) for v in roster.values())))
    print("%d eviction pair(s) across %d biome(s); %d rostered pair(s) left to the de-dup "
          "union; %d already shipped there; %d skipped as not in the live mod set"
          % (len(rows), len({b for _r, b in rows}), kept, dup, dead))
    per = collections.Counter(b for _r, b in rows)
    for b in sorted(per, key=lambda x: -per[x]):
        print("   %-32s %4d" % (b, per[b]))

    if a.xml:
        ops = [OP % {"n": i + 1, "race": r, "biome": b} for i, (r, b) in enumerate(rows)]
        prov = ("  Generated from capture %s plus the installed-mod XML walk.\n"
                "  %d operation(s) over %d painted biome def(s).\n"
                "  %d rostered pair(s) deliberately NOT here (de-dup union owns those);\n"
                "  %d pair(s) skipped because the race is installed on disk but not in the\n"
                "  live mod set - a removal for a def no load sees is dead weight.\n"
                % (cap, len(rows), len(per), kept, dead))
        with open(a.xml, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(HEADER % {"prov": prov, "ops": "".join(ops)})
        print("\nwrote %d operation(s) -> %s" % (len(ops), a.xml))
    return 0


if __name__ == "__main__":
    sys.exit(main())
