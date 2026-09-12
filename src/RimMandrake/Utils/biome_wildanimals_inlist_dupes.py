# -*- coding: utf-8 -*-
"""biome_wildanimals_inlist_dupes.py - one BiomeDef's OWN wildAnimals list, holding
the SAME PawnKindDef twice (or more).

A DIFFERENT bug from biome_animal_conflicts.py's cross-registration class (biome
side x race.wildBiomes side). This one is a literal double record WITHIN a single
BiomeDef's own <wildAnimals> list - RimWorld's own BiomeDef.ConfigErrors() flags it
directly ("Duplicate animal record: X"), and it hits the exact same
`Dictionary.Add` throw in `BiomeDef.CommonalityOfAnimal()` as the cross-registration
class, in the FIRST loop (over the biome's own wildAnimals), before the animal-side
check even runs. See AnimalBiomeDuplicates_Fix.xml's file header for the full crash
chain (Giddy-Up / Choose Wild Animal Spawns / Biome Compatibility Project).

WHY THIS KEEPS HAPPENING: a donor mod's own patch adds an animal to a biome, and
our OWN `BiomeCast_Ashkarr.xml` additively adds it AGAIN without checking or
replacing. Neither def says so on disk - only a post-patch capture shows it, same
reasoning as biome_animal_conflicts.py's own docstring.

🔴 LOAD ORDER, MEASURED (not guessed) via RimSage against the shipped game DLL:
`ModContentPack.LoadPatches()` builds its patch list from
`DirectXmlLoader.XmlAssetsInModFolder(this, "Patches/")`, which enumerates a single
mod's Patches/ folder with `DirectoryInfo.GetFiles(..., AllDirectories)` - i.e. in
filesystem enumeration order (NTFS's case-insensitive collation, which behaves as
ordinal-uppercase for plain ASCII names) - and applies every mod's patches strictly
in that per-mod file order (`LoadedModManager`, `runningMods.SelectMany(m =>
m.Patches)`). There is no independent sort pass. So a same-mod removal that targets
an index CREATED by another same-mod file only works if its own filename sorts
AFTER that file's. `AnimalBiomeDuplicates_Fix.xml` sorts BEFORE `BiomeCast_Ashkarr.xml`
(A < B) - so its Block-4 in-list-duplicate removals ran before BiomeCast_Ashkarr.xml
had appended its own second copy, found only one record, no-opped (a
PatchOperationConditional matching 0 nodes is a silent no-op), and the duplicate
that BiomeCast_Ashkarr.xml then created survived uncaught. Confirmed live 2026-09-12
against capture 2026-09-12T19-16-27Z: exactly the 7 pairs Block 4 targeted (plus the
Anooba pair separately retired) were STILL duplicated despite the removal entries
existing.

THE FIX: this file's own name, `BiomeWildAnimalDuplicates_Generated.xml`, is chosen
to sort AFTER `BiomeCast_Ashkarr.xml` ("BiomeW..." > "BiomeC...") within the SAME
mod's Patches/ folder, so its removals run after BiomeCast_Ashkarr.xml's own
additions have already landed.

USAGE
    python3 src/RimMandrake/Utils/biome_wildanimals_inlist_dupes.py                # list them
    python3 src/RimMandrake/Utils/biome_wildanimals_inlist_dupes.py --xml OUT      # emit the patch
    python3 src/RimMandrake/Utils/biome_wildanimals_inlist_dupes.py --capture <dir>
"""
from __future__ import annotations

import argparse
import collections
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


def conflicts(capture):
    """[(biome, animal, count)] for every BiomeDef whose OWN wildAnimals list holds
    the same PawnKindDef more than once. `count` is the total number of records
    (2 for a single duplicate). Returns None if the capture cannot be read.
    """
    p = os.path.join(capture, "defs", "BiomeDef.json")
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding="utf-8") as fh:
            bio = json.load(fh)
    except (OSError, ValueError):
        return None

    out = []
    for r in bio.get("defs", []):
        wa = r["fields"].get("wildAnimals")
        if not wa:
            continue
        cnt = collections.Counter(
            x["animal"] for x in wa if isinstance(x, dict) and x.get("animal"))
        for animal, n in sorted(cnt.items()):
            if n > 1:
                out.append((r["defName"], animal, n))
    return sorted(out)


PAIR_RE = re.compile(
    r'/Defs/BiomeDef\[defName="([^"]+)"\]/wildAnimals/([A-Za-z0-9_]+)\[(\d+)\]')


def existing_triples(path):
    """[(biome, animal, index)] already shipped in `path`, one per removal op.

    Same union discipline as biome_animal_conflicts.py's existing_pairs(): a pair our
    own removal already fixes is invisible to the NEXT capture (the fix hides its own
    evidence), so this file is a UNION, appended to, never replaced from a fresh scan.
    """
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            txt = fh.read()
    except OSError:
        return []
    out, seen = [], set()
    for biome, animal, idx in PAIR_RE.findall(txt):
        key = (biome, animal, int(idx))
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


HEADER = """<?xml version="1.0" encoding="utf-8"?>
<!--
  ============================================================================
  BiomeWildAnimalDuplicates_Generated.xml    GENERATED - do not hand-edit
  ============================================================================
  Regenerate with biome_wildanimals_inlist_dupes.py, flag `xml`, writing to this path:
      python3 src/RimMandrake/Utils/biome_wildanimals_inlist_dupes.py
  (⛔ the flags are spelled with two hyphens, which XML forbids inside a comment,
   so they are named rather than written out here. See the script's docstring.)

  Companion to AnimalBiomeDuplicates_Generated.xml (cross-registration: biome
  wildAnimals x animal race.wildBiomes) and AnimalBiomeDuplicates_Fix.xml's Blocks
  1-3 (same class, hand-verified). This file is the THIRD, DIFFERENT class: one
  BiomeDef's own <wildAnimals> list holding the SAME PawnKindDef twice - RimWorld's
  own BiomeDef.ConfigErrors() calls this out directly ("Duplicate animal record: X"),
  and it hits BiomeDef.CommonalityOfAnimal()'s Dictionary.Add() throw in the FIRST
  loop, before the cross-registration check even runs.

  🔴 THIS FILE'S NAME IS LOAD-BEARING, not cosmetic. RimWorld enumerates a single
  mod's Patches/ folder in filesystem order (DirectXmlLoader.XmlAssetsInModFolder,
  confirmed via RimSage against ModContentPack.LoadPatches / DirectoryInfo.GetFiles)
  and applies that mod's patches strictly in that order - no independent sort pass.
  Every pair here is created by OUR OWN BiomeCast_Ashkarr.xml (same mod) adding an
  animal a donor mod's own patch already added, so the removal MUST run after
  BiomeCast_Ashkarr.xml appends it. "BiomeWildAnimalDuplicates_Generated.xml" sorts
  after "BiomeCast_Ashkarr.xml" (W > C); the previous home for these removals,
  AnimalBiomeDuplicates_Fix.xml's Block 4, sorted BEFORE it (A < B) and silently
  no-opped on every one of its 7 live pairs - confirmed 2026-09-12 against capture
  %(cap)s. Do not rename this file to anything sorting at or before "BiomeCast_".

  Each removal targets the SECOND (or later) occurrence by XPath index, e.g.
  wildAnimals/Foo[2] - the biome's own commonality (our cast) is always kept, the
  donor's duplicate record is what goes. Multiple duplicates of the same pair remove
  from the HIGHEST index down, so an earlier removal never shifts a later target's
  index out from under it.

  Every op is a PatchOperationConditional: an absent mod, or a def that no longer
  collides, turns it into a silent no-op instead of a red error.
%(prov)s-->
<Patch>
%(ops)s</Patch>
"""

OP = """
  <!-- %(n)d. %(animal)s x %(biome)s (record %(idx)d of %(count)d) -->
  <Operation Class="PatchOperationConditional">
    <xpath>/Defs/BiomeDef[defName="%(biome)s"]/wildAnimals/%(animal)s[%(idx)d]</xpath>
    <match Class="PatchOperationRemove">
      <xpath>/Defs/BiomeDef[defName="%(biome)s"]/wildAnimals/%(animal)s[%(idx)d]</xpath>
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
        print("UNMEASURED: capture " + cap + " could not be read (BiomeDef.json required).")
        return 2

    print("capture: " + os.path.basename(cap))
    print("%d duplicated (biome, animal) pair(s)" % len(rows))
    for b, k, n in rows:
        print("  %-30s %-20s x%d" % (b, k, n))

    if a.xml:
        # Every index from `count` down to 2, per pair - descending so an earlier
        # removal never shifts a later target's index.
        fresh = set()
        for biome, animal, count in rows:
            for idx in range(count, 1, -1):
                fresh.add((biome, animal, idx))

        carried = existing_triples(a.xml)
        seen, ops, n = set(), [], 0
        count_of = {(b, k): c for b, k, c in rows}
        for biome, animal, idx in carried:
            key = (biome, animal, idx)
            if key in seen:
                continue
            seen.add(key)
            n += 1
            ops.append(OP % {"n": n, "biome": biome, "animal": animal, "idx": idx,
                             "count": count_of.get((biome, animal), idx)})
        added = 0
        for biome, animal, idx in sorted(fresh):
            key = (biome, animal, idx)
            if key in seen:
                continue
            seen.add(key)
            n += 1
            added += 1
            ops.append(OP % {"n": n, "biome": biome, "animal": animal, "idx": idx,
                             "count": count_of.get((biome, animal), idx)})
        gone = [t for t in carried if t not in fresh]
        print("\nunion: %d triple(s) already shipped + %d new from this capture = %d "
              "operation(s)" % (len(carried), added, n))
        if gone:
            print("   %d shipped triple(s) this capture no longer sees - KEPT, because a "
                  "removal that already works is invisible to a post-patch capture:"
                  % len(gone))
            for biome, animal, idx in gone:
                print("     %-30s %-20s [%d]" % (biome, animal, idx))
        prov = ("  Generated from capture %s\n"
                "  %d pair(s) found this run; %d triple(s) carried from the previous file\n"
                "  that this capture can no longer see (our own removals hide their own\n"
                "  evidence once they take effect). %d operation(s), the UNION of every\n"
                "  triple ever found.\n"
                % (os.path.basename(cap), len(rows), len(gone), n))
        with open(a.xml, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(HEADER % {"cap": os.path.basename(cap), "prov": prov, "ops": "".join(ops)})
        print("\nwrote %d operation(s) -> %s" % (n, a.xml))
    return 0


if __name__ == "__main__":
    sys.exit(main())
