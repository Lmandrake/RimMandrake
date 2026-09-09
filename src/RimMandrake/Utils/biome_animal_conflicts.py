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
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_paths import CAPTURES  # noqa: E402


def newest_capture(root=CAPTURES):
    if not os.path.isdir(root):
        return None
    subs = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    return os.path.join(root, subs[-1]) if subs else None


def conflicts(capture, cast_paths=()):
    """[(biome, pawnKind, raceDefName)] for every pair registered twice.

    Returns None if the capture cannot be read - the caller must report
    UNMEASURED rather than "no conflicts".

    `cast_paths` are OUR OWN cast XML files; their entries are unioned into the biome
    side so a cast that has been regenerated but never loaded is still covered. See
    our_cast().
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
    for _b, _kinds in our_cast(cast_paths).items():
        a_side[_b] |= _kinds

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


def our_cast(paths):
    """biome -> {pawnKind defName} read from OUR OWN shipped XML, not from a capture.

    🔴 WHY A CAPTURE IS NOT ENOUGH, and it cost a shipped regression on 2026-08-27.
    conflicts() builds its biome side from the capture's BiomeDef.wildAnimals - i.e.
    from the cast the game loaded LAST TIME. The moment the cast is regenerated, every
    (biome, animal) pair the NEW rows introduce is invisible to every capture until
    someone loads the game, which is exactly the window in which the last regression
    shipped 25 uncovered collisions. Reading our own XML closes it: the union is
    computed against the cast we are about to ship, not the one that already ran.

    Handles both shapes we author:
      · a Patch file - PatchOperationReplace/Add into /Defs/BiomeDef[defName=X]/wildAnimals
      · a Defs file  - a BiomeDef declaring <wildAnimals> directly (the RUT_ tier)
    A path that does not exist is skipped silently; a path that exists but parses to
    nothing is REPORTED, because that is what a shape change looks like.
    """
    import xml.etree.ElementTree as ET
    xp_re = re.compile(r'/Defs/BiomeDef\[defName="([^"]+)"\]/wildAnimals')
    out = collections.defaultdict(set)
    for p in paths:
        if not os.path.isfile(p):
            continue
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError as exc:
            print("⚠️ %s does not parse (%s) - its cast is NOT in this union" % (p, exc))
            continue
        found = nodes = 0
        for bd in root.iter("BiomeDef"):                       # a Defs file
            dn = bd.findtext("defName")
            wa = bd.find("wildAnimals")
            if not dn or wa is None:
                continue
            nodes += 1
            for kid in wa:
                if isinstance(kid.tag, str):
                    out[dn].add(kid.tag)
                    found += 1
        for op in root.iter("Operation"):                      # a Patch file
            xp = op.findtext("xpath") or ""
            m = xp_re.fullmatch(xp.strip())
            if not m:
                continue
            for val in op.iter("value"):
                # ⚠️ TWO SHAPES, and missing the second one silently halved this union
                # the first time. A Replace carries <value><wildAnimals>…</wildAnimals>;
                # a donor-gated Add carries the animal nodes DIRECTLY in <value>,
                # because its xpath already points AT wildAnimals. Reading only the
                # first shape found 9 of 361 entries and reported success.
                wrapped = val.find("wildAnimals")
                holder = wrapped if wrapped is not None else val
                nodes += 1
                for kid in holder:
                    if isinstance(kid.tag, str):
                        out[m.group(1)].add(kid.tag)
                        found += 1
        print("   our cast: %4d entry(ies) from %s" % (found, os.path.basename(p)))
        if not nodes and "wildAnimals" in open(p, encoding="utf-8").read():
            print("      ⚠️ this file names wildAnimals but nothing parsed out of it - "
                  "its SHAPE changed and this union is short.")
    return out


PAIR_RE = re.compile(
    r'/Defs/ThingDef\[defName="([^"]+)"\]/race/wildBiomes/([A-Za-z0-9_]+)')


def existing_pairs(path):
    """[(race, biome)] already shipped in `path`, in file order. [] if it is not there.

    🔴 THE SHIPPED SET MUST BE THE UNION OF EVERY PAIR EVER FOUND, and this function is
    the whole reason it can be. BIOME_DUPLICATES_STILL_LIVE_1, measured 2026-08-26: the
    capture is taken AFTER every PatchOperation, so a pair OUR OWN REMOVAL ALREADY FIXED
    is invisible to conflicts() - the fix hides its own evidence. Five shipped removals
    were absent from a 56-pair run for exactly that reason. Regenerating from the capture
    alone would have dropped them and the five collisions would have come back on the
    next load with nothing in any log naming them.

    So this file is APPENDED TO, never replaced. A pair leaves it only when a human
    deletes the line and says why.
    """
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            txt = fh.read()
    except OSError:
        return []
    out, seen = [], set()
    for race, biome in PAIR_RE.findall(txt):
        if (race, biome) not in seen:
            seen.add((race, biome))
            out.append((race, biome))
    return out


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
    ap.add_argument("--cast", action="append", default=None,
                    help="our own cast XML, unioned into the biome side (repeatable). "
                         "Defaults to every file this repo casts animals from.")
    a = ap.parse_args(argv)

    # .../src/RimMandrake/Utils/<this file> -> four levels up is the repo root.
    repo = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "..", "..", ".."))
    casts = a.cast if a.cast is not None else [
        os.path.join(repo, "src", "RimUtinni", "UtinniPatches", "Patches",
                     "BiomeCast_Ashkarr.xml"),
    ] + sorted(glob.glob(os.path.join(
        repo, "src", "RimUtinni", "UtinniPatches", "Defs", "BiomeDefs", "*.xml")))

    cap = a.capture or newest_capture()
    if not cap:
        print("UNMEASURED: no def dump capture found under\n  " + CAPTURES)
        return 2
    rows = conflicts(cap, casts)
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
        #
        # 🔴 UNION, NOT REPLACE. The pairs already in the target file come first and
        # are never dropped - see existing_pairs() for the measurement that makes this
        # non-negotiable. Only pairs this run found that are NOT already shipped are
        # appended.
        kind_of = {(race, b): k for b, k, race in rows}
        carried = existing_pairs(a.xml)
        seen, ops, n = set(), [], 0
        for race, b in carried:
            seen.add((race, b))
            n += 1
            ops.append(OP % {"n": n, "kind": kind_of.get((race, b), "(carried)"),
                             "biome": b, "race": race})
        added = 0
        for b, k, race in rows:
            if (race, b) in seen:
                continue
            seen.add((race, b))
            n += 1
            added += 1
            ops.append(OP % {"n": n, "kind": k, "biome": b, "race": race})
        gone = [p for p in carried if p not in {(r, b) for b, _k, r in rows}]
        print("\nunion: %d pair(s) already shipped + %d new from this capture = %d "
              "operation(s)" % (len(carried), added, n))
        if gone:
            print("   %d shipped pair(s) this capture no longer sees - KEPT, because a "
                  "removal that already works is invisible to a post-patch capture:"
                  % len(gone))
            for race, b in gone:
                print("     %-30s x %s" % (race, b))
        prov = ("  Generated from capture %s\n"
                "  %d pair(s) found this run; %d carried from the previous file that this\n"
                "  capture can no longer see (our own removals hide their own evidence).\n"
                "  %d operation(s), the UNION of every pair ever found.\n"
                % (os.path.basename(cap), len(rows), len(gone), n))
        with open(a.xml, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(HEADER % {"prov": prov, "ops": "".join(ops)})
        print("\nwrote %d operation(s) -> %s" % (n, a.xml))
    return 0


if __name__ == "__main__":
    sys.exit(main())
