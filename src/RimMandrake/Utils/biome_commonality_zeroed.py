# -*- coding: utf-8 -*-
"""biome_commonality_zeroed.py - which animals are SWITCHED OFF in the live game.

WHAT IT ANSWERS
===============
A `BiomeAnimalRecord` whose `commonality` is **0** is registered in the biome and
can never be chosen: `BiomeDef.AllWildAnimals` only yields kinds whose commonality
is `> 0f`. So an animal at 0 is not in the biome's animal list at all, and nothing
anywhere reports it - the def is present, the patch applied, the entry exists.

This script names every one of them, from the def dump CAPTURE, which is the only
source taken after every PatchOperation has applied.

🔴 WHAT IT IS NOT, AND WHY THAT MATTERS
=======================================
⛔ **This is NOT the duplicate-key crash and NOT a dumper defect.** Both were
proposed for these zeros on 2026-08-26 and both are wrong:

  * `BiomeDef.CommonalityOfAnimal` never writes back into a record - it only reads
    `wildAnimals[i].commonality` into its cache (`RimWorld/BiomeDef.cs`). A broken
    cache cannot produce a zero in the record, and the record is where these are.
  * `DefDumper.cs`'s `CommonalityOfAnimal` call writes `animals.json`'s
    `biomeAnimals` block. These zeros are in `defs/BiomeDef.json`, under
    `fields.wildAnimals[].commonality`, from plain reflection over the field.

✅ **IT IS CHERRY PICKER, AND IT IS THE OWNER'S OWN CUT LIST.** Answered 2026-08-26.
`Config/Mod_3521312241_Mod_CherryPicker.xml` holds the owner's cuts — see
`cherrypicker.load().provenance()` below for the CURRENT count, which grows every
review pass and would go stale as a number fixed in this docstring. Cherry Picker
suppresses a cut animal by REPLACING its biome commonality with 0 rather than
removing the entry.

Validated over the population, not on a sample:

    always-off animals (all 67 biomes)   168   in the cut list  167  (99.4%)
    always-alive animals                 414   in the cut list    0   (0.0%)

⛔ **Its cuts are INVISIBLE to the def dump** - every cut animal is still PRESENT as
both ThingDef and PawnKindDef in the capture. That is why every earlier theory
reached for the engine: the defs were all there, so the value looked corrupted. It
was not corrupted; it was switched off on purpose.

🔑 **So a zero here is INTENDED, and the defect is ours:** our cast roster writes
those animals at 1.0 expecting them to spawn. Use this to find what to design
around, not to "fix" the zeros. `gen_cast_patch.py` now refuses to cast one.

USAGE
    python3 src/RimMandrake/Utils/biome_commonality_zeroed.py
    python3 src/RimMandrake/Utils/biome_commonality_zeroed.py --ours     # only the biomes our patch writes
    python3 src/RimMandrake/Utils/biome_commonality_zeroed.py --animal   # per-ANIMAL census
    python3 src/RimMandrake/Utils/biome_commonality_zeroed.py --capture <dir>
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
CAST_PATCH = os.path.join(REPO, "src", "Jawa", "Jawa_Patches", "Patches", "BiomeCast_Ashkarr.xml")

sys.path.insert(0, os.path.join(REPO, "design", "Jawa", "fauna"))
import cherrypicker                                            # noqa: E402 — same dir


def newest_capture():
    import dumppath                                            # noqa: E402
    return dumppath.dump_root()


def load_biomes(capture):
    """{biome: {animal: commonality}} from the capture's RECORD field.

    ⛔ Refuses rather than returning {} when the file is missing - an empty result
    here would read as "no biome carries a zero", which is the opposite of unknown.
    """
    path = os.path.join(capture, "defs", "BiomeDef.json")
    if not os.path.isfile(path):
        sys.exit("UNMEASURED: no defs/BiomeDef.json in %s" % capture)
    raw = json.load(open(path, encoding="utf-8"))
    entries = raw["defs"] if isinstance(raw, dict) and "defs" in raw else raw
    out = {}
    for e in entries:
        records = (e.get("fields") or {}).get("wildAnimals")
        if not records:
            continue
        out[e["defName"]] = {
            r["animal"]: r.get("commonality")
            for r in records if isinstance(r, dict) and r.get("animal")
        }
    if not out:
        sys.exit("UNMEASURED: BiomeDef.json carried no wildAnimals lists at all - "
                 "the capture is from a load that never got there, or the field moved.")
    return out


def ours():
    """{biome: {animal: commonality}} that OUR cast patch writes, or {} if absent."""
    if not os.path.isfile(CAST_PATCH):
        return {}
    text = open(CAST_PATCH, encoding="utf-8").read()
    out = {}
    for m in re.finditer(
            r'PatchOperationReplace">\s*<xpath>/Defs/BiomeDef\[defName="([^"]+)"\]'
            r'/wildAnimals</xpath>\s*<value>\s*<wildAnimals>(.*?)</wildAnimals>',
            text, re.S):
        out[m.group(1)] = {
            e.group(1): float(e.group(2))
            for e in re.finditer(r"<(\w+)>([\d.]+)</\1>", m.group(2))
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capture", help="capture dir; default is the newest")
    ap.add_argument("--ours", action="store_true",
                    help="only the biomes BiomeCast_Ashkarr.xml writes")
    ap.add_argument("--animal", action="store_true",
                    help="per-ANIMAL census instead of per-biome")
    args = ap.parse_args(argv)

    capture = args.capture or newest_capture()
    live = load_biomes(capture)
    mine = ours()
    scope = {b: v for b, v in live.items() if b in mine} if args.ours else live

    print("capture: %s" % capture)
    print("biomes with a wildAnimals list: %d   (our cast patch writes %d)"
          % (len(live), len(mine)))
    try:
        cuts = cherrypicker.load()
        print(cuts.provenance())
    except IOError as exc:
        print("⚠️ cherrypicker: %s — always-off animals cannot be cross-checked "
              "against the live cut list" % exc)
        cuts = None

    zero_in = collections.Counter()
    live_in = collections.Counter()
    for biome, animals in scope.items():
        for a, c in animals.items():
            (zero_in if c == 0 else live_in)[a] += 1

    if args.animal:
        print("\nanimal                          zeroed  alive   verdict")
        for a in sorted(set(zero_in) | set(live_in)):
            z, n = zero_in[a], live_in[a]
            if not z:
                continue
            # 🔑 ALWAYS-OFF is the one worth acting on: the animal cannot spawn
            # anywhere in scope, so a roster naming it is designing around a ghost.
            verdict = "ALWAYS OFF" if not n else "mixed"
            print("  %-30s %5d  %5d   %s" % (a, z, n, verdict))
        always = sum(1 for a in zero_in if not live_in[a])
        print("\n%d animal(s) carry a zero; %d are ALWAYS OFF in this scope."
              % (len(zero_in), always))
        if cuts is not None:
            off = [a for a in zero_in if not live_in[a]]
            explained = sum(1 for a in off if cuts.cut_name(a))
            print("%d of %d ALWAYS OFF names are on the live cut list; "
                  "%d zeroed for a different reason." % (explained, len(off),
                                                          len(off) - explained))
        return 0

    total_z = total_n = 0
    for biome in sorted(scope):
        animals = scope[biome]
        z = sorted(a for a, c in animals.items() if c == 0)
        total_z += len(z)
        total_n += len(animals) - len(z)
        if not z:
            continue
        # Flag the ones WE asked for, because those are the roster's own losses.
        marked = ["%s%s" % (a, "*" if a in mine.get(biome, {}) else "") for a in z]
        print("\n%-28s %d of %d switched off" % (biome, len(z), len(animals)))
        print("   " + ", ".join(marked))

    print("\n%d entry(s) at commonality 0, %d alive, across %d biome(s)."
          % (total_z, total_n, len(scope)))
    if mine:
        print("* = an entry OUR cast patch writes at a non-zero weight. Those are the "
              "roster designing around an animal something else switched off.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
