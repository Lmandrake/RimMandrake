#!/usr/bin/env python3
"""AnimalBiomeDuplicates_Generated.xml carries no orphaned removal, and its generator
drops one instead of carrying it (ANIMALDUPES_ORPHAN_OPS_AUDIT_SOLE_SPAWN_CUT).

Why: the file removes the ANIMAL side of a (race, biome) pair registered from both
sides. Once the biome side stops listing the race (our cast moved to the RUT_ twins),
the removal strips the race's only registration: an eviction dressed as a de-dup.
Measured on capture 2026-11-04T13-15-53Z: 67 such RSW_ pairs over vanilla Desert,
AridShrubland and ExtremeDesert, none painted on Ash'karr, so they were cut, not moved
to BiomeCastEvictions_WildBiomes.xml (which writes painted biomes only).

Checks, all offline:
  1. none of the 67 measured pairs is in the shipped file;
  2. orphaned() on a synthetic capture drops a live race the biome side no longer
     lists, keeps one it still lists, keeps a race the capture does not know, keeps a
     biome the capture does not know, ignores a non-race ThingDef of the same name, and
     counts our own cast as biome side;
  3. a --xml regeneration against that capture drops the orphan and keeps the rest;
  4. the header's op count equals the real op count, and the header no longer says
     "nothing is lost" without its condition.
Sanity probe: the shipped file must parse to at least 50 pairs, or the reader is blind.
"""
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import biome_animal_conflicts as bac  # noqa: E402

SHIPPED = os.path.join(ROOT, "src", "RimUtinni", "UtinniPatches", "Patches",
                       "AnimalBiomeDuplicates_Generated.xml")

CUT = [
    ("RSW_Nuna", "AridShrubland"), ("RSW_Porg", "AridShrubland"),
    ("RSW_Vulptex", "AridShrubland"), ("RSW_Nuna", "Desert"), ("RSW_Wampa", "ExtremeDesert"),
    ("RSW_FeralNerf", "AridShrubland"), ("RSW_FrilledGorg", "AridShrubland"),
    ("RSW_Gizka", "AridShrubland"), ("RSW_Gorg", "AridShrubland"),
    ("RSW_Grank", "AridShrubland"), ("RSW_KowakianMonkeyLizard", "AridShrubland"),
    ("RSW_Kreetle", "AridShrubland"), ("RSW_Kybuck", "AridShrubland"),
    ("RSW_LongtailGorg", "AridShrubland"), ("RSW_Lothcat", "AridShrubland"),
    ("RSW_Massiff", "AridShrubland"), ("RSW_Pikobis", "AridShrubland"),
    ("RSW_Pufferpig", "AridShrubland"), ("RSW_Qormot", "AridShrubland"),
    ("RSW_Ronto", "AridShrubland"), ("RSW_Scavrat", "AridShrubland"),
    ("RSW_Scurrier", "AridShrubland"), ("RSW_Skalder", "AridShrubland"),
    ("RSW_Sketto", "AridShrubland"), ("RSW_Strill", "AridShrubland"),
    ("RSW_Voorpak", "AridShrubland"), ("RSW_Whisperbird", "AridShrubland"),
    ("RSW_WompRat", "AridShrubland"), ("RSW_Worrt", "AridShrubland"),
    ("RSW_Falumpaset", "Desert"), ("RSW_FeralGrazer", "Desert"), ("RSW_FrilledGorg", "Desert"),
    ("RSW_Gizka", "Desert"), ("RSW_Gorg", "Desert"), ("RSW_Gutkurr", "Desert"),
    ("RSW_Horax", "Desert"), ("RSW_Hrumph", "Desert"), ("RSW_IridonianReek", "Desert"),
    ("RSW_Jakobeast", "Desert"), ("RSW_Jamel", "Desert"), ("RSW_Jimvu", "Desert"),
    ("RSW_Kreetle", "Desert"), ("RSW_Krykna", "Desert"), ("RSW_Kwi", "Desert"),
    ("RSW_LongtailGorg", "Desert"), ("RSW_Nerf", "Desert"), ("RSW_Ronto", "Desert"),
    ("RSW_Runyip", "Desert"), ("RSW_Scavrat", "Desert"), ("RSW_Shaak", "Desert"),
    ("RSW_Shyrack", "Desert"), ("RSW_Skalder", "Desert"), ("RSW_Sketto", "Desert"),
    ("RSW_TeeMuss", "Desert"), ("RSW_Uvak", "Desert"), ("RSW_Varactyl", "Desert"),
    ("RSW_Voorpak", "Desert"), ("RSW_WompRat", "Desert"), ("RSW_Worrt", "Desert"),
    ("RSW_Wraid", "Desert"), ("RSW_Zeer", "Desert"), ("RSW_Gizka", "ExtremeDesert"),
    ("RSW_GraniteSlug", "ExtremeDesert"), ("RSW_GreaterKraytDragon", "ExtremeDesert"),
    ("RSW_Kreetle", "ExtremeDesert"), ("RSW_Scavrat", "ExtremeDesert"),
    ("RSW_WompRat", "ExtremeDesert"),
]


def capture(tmp, biomes, kinds, things):
    d = os.path.join(tmp, "cap", "defs")
    os.makedirs(d)
    for name, defs in (("BiomeDef.json", biomes), ("PawnKindDef.json", kinds),
                       ("ThingDef.json", things)):
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            json.dump({"defs": defs}, fh)
    return os.path.join(tmp, "cap")


def main():
    bad = []
    pairs = bac.existing_pairs(SHIPPED)
    if len(pairs) < 50:
        bad.append("sanity: shipped file parses to only %d pairs - reader blind?" % len(pairs))
    if len(CUT) != 67:
        bad.append("CUT list holds %d pairs, expected the 67 measured" % len(CUT))
    back = sorted(set(CUT) & set(pairs))
    if back:
        bad.append("%d cut orphan pair(s) are back in the shipped file: %s" % (len(back), back[:5]))

    tmp = tempfile.mkdtemp(prefix="abd_orphan_")
    try:
        cap = capture(
            tmp,
            [{"defName": "B1", "fields": {"wildAnimals": [{"animal": "KeepKind"}]}},
             {"defName": "B2", "fields": {"wildAnimals": []}}],
            [{"defName": "KeepKind", "fields": {"race": "KeepRace"}},
             {"defName": "OrphanKind", "fields": {"race": "OrphanRace"}},
             {"defName": "CastKind", "fields": {"race": "CastRace"}},
             {"defName": "NotRaceKind", "fields": {"race": "NotRace"}}],
            [{"defName": "KeepRace", "fields": {"race": {}}},
             {"defName": "OrphanRace", "fields": {"race": {}}},
             {"defName": "CastRace", "fields": {"race": {}}},
             {"defName": "NotRace", "fields": {}}])
        cast = os.path.join(tmp, "cast.xml")
        with open(cast, "w", encoding="utf-8") as fh:
            fh.write('<Defs><BiomeDef><defName>B2</defName><wildAnimals><CastKind>1</CastKind>'
                     '</wildAnimals></BiomeDef></Defs>')
        given = [("KeepRace", "B1"), ("OrphanRace", "B1"), ("GoneRace", "B1"),
                 ("CastRace", "B2"), ("OrphanRace", "UnloadedBiome"), ("NotRace", "B1")]
        got = bac.orphaned(cap, given, [cast])
        if got != [("OrphanRace", "B1")]:
            bad.append("orphaned() returned %r, expected [('OrphanRace', 'B1')]" % (got,))
        if bac.orphaned(os.path.join(tmp, "nope"), given) is not None:
            bad.append("orphaned() on an unreadable capture must return None")

        out = os.path.join(tmp, "out.xml")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("".join(bac.OP % {"n": i, "kind": "(carried)", "race": r, "biome": b}
                             for i, (r, b) in enumerate(given, 1)))
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            rc = bac.main(["--capture", cap, "--xml", out, "--cast", cast])
        kept = bac.existing_pairs(out)
        if rc != 0 or kept != [p for p in given if p != ("OrphanRace", "B1")]:
            bad.append("regeneration rc=%s kept %r" % (rc, kept))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    with open(SHIPPED, encoding="utf-8") as fh:
        txt = fh.read()
    head = txt.split("<Patch>", 1)[0]
    m = re.search(r"(\d+) operation\(s\)", head)
    n_ops = txt.count("<Operation ")
    if not m or int(m.group(1)) != n_ops:
        bad.append("header op count %s != %d operations in the file"
                   % (m.group(1) if m else "missing", n_ops))
    if re.search(r"so\s+nothing is lost", head):
        bad.append("header still claims 'so nothing is lost' unconditionally")

    for b in bad:
        print("FAIL " + b)
    print("animal dupes orphan carry: %d shipped pairs, %d cut pairs checked, %d failures -> %s"
          % (len(pairs), len(CUT), len(bad), "OK" if not bad else "FAILED"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
