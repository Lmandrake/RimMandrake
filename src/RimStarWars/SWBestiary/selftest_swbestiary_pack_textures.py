#!/usr/bin/env python3
"""selftest_swbestiary_pack_textures.py -- every SWBestiary pack animal ships its `<texPath>Pack` art.

Run bare: python3 src/RimStarWars/SWBestiary/selftest_swbestiary_pack_textures.py   (exit 0 = clean)

Why (DONOR_PACK_TEX_REPAIR_SEVEN_LEFT_BEHIND): with packAnimal=true the engine's
PawnRenderNode_AnimalPack.GraphicFor (rw16 decomp, Verse/PawnRenderNode_AnimalPack.cs) loads
`GraphicDatabase.Get<Graphic_Multi>(graphic.path + "Pack")`, where graphic is the current
PawnKindLifeStage's femaleGraphicData (female pawn, if set) else its bodyGraphicData. A donor port
that keeps only the base facings logs "Failed to find any textures at <texPath>Pack" at startup
(r5: Thranta, Runyip, Reek, Dalgo, Dactillion, Bolotaur, Orray; Ronto was repaired in 4c3071cca3,
Behemoth in 1a2d740184). Every life stage counts, not just the adult the startup log happened to hit.

The rule checked: for every PawnKindDef whose race (through ParentName) has packAnimal=true, every
bodyGraphicData/femaleGraphicData texPath P that resolves in this mod's Textures/ has, for each
facing file P_<facing>.png it ships, a matching PPack_<facing>.png. A texPath that does not resolve
here at all is its own FAIL row (the bestiary must stand alone).

Instrument probes: the census must see RSW_Ronto (a known pack animal) and at least 30 pack
races (43 on 2026-10-31); hiding one RontoPack facing must redden; a fake race with no Pack art
must redden.

`--list-missing` prints the missing Pack files and their base source, one per line, for
pack_placeholder_repair.py.
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "Textures")
FACINGS = ("north", "east", "south", "west")
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def _parse_defs(root_dir):
    """Return (things, kinds): name->element maps for ThingDef and PawnKindDef (by defName and by Name)."""
    things, kinds = {}, {}
    for path in sorted(glob.glob(os.path.join(root_dir, "Defs", "**", "*.xml"), recursive=True)):
        try:
            tree = ET.parse(path)
        except ET.ParseError as e:
            check("parses %s" % os.path.relpath(path, HERE), False, str(e))
            continue
        for el in tree.getroot():
            if el.tag not in ("ThingDef", "PawnKindDef"):
                continue
            bucket = things if el.tag == "ThingDef" else kinds
            dn = el.findtext("defName")
            nm = el.get("Name")
            if dn:
                bucket[("def", dn)] = el
            if nm:
                bucket[("name", nm)] = el
    return things, kinds


def _chain(el, bucket):
    seen = []
    while el is not None and len(seen) < 20:
        seen.append(el)
        parent = el.get("ParentName")
        el = bucket.get(("name", parent)) if parent else None
    return seen


def _pack_flag(race_el, things):
    for el in _chain(race_el, things):
        v = el.findtext("race/packAnimal")
        if v is not None:
            return v.strip().lower() == "true"
    return False


def census(root_dir=HERE):
    """[(kindDefName, raceDefName, texPath)] for every pack-animal life-stage body/female graphic."""
    things, kinds = _parse_defs(root_dir)
    pack_races = set()
    rows = []
    for key, el in kinds.items():
        if key[0] != "def" or el.get("Abstract", "").lower() == "true":
            continue
        chain = _chain(el, kinds)
        race = next((c.findtext("race") for c in chain if c.findtext("race")), None)
        race_el = things.get(("def", race)) if race else None
        if race_el is None or not _pack_flag(race_el, things):
            continue
        pack_races.add(race)
        paths = set()
        for c in chain:
            for li in c.findall("lifeStages/li"):
                for tag in ("bodyGraphicData", "femaleGraphicData"):
                    p = li.findtext(tag + "/texPath")
                    if p:
                        paths.add(p.strip())
        for p in sorted(paths):
            rows.append((key[1], race, p))
    return pack_races, rows


def problems(rows, exists):
    """[(kind, texPath, problem, base_file, pack_file)] -- base_file/pack_file set for a missing facing."""
    out = []
    for kind, _race, p in rows:
        have = [f for f in FACINGS if exists("%s_%s.png" % (p, f))]
        if not have:
            out.append((kind, p, "base texPath has no facing files in this mod", None, None))
            continue
        for f in have:
            base, pack = "%s_%s.png" % (p, f), "%sPack_%s.png" % (p, f)
            if not exists(pack):
                out.append((kind, p, "missing " + pack, base, pack))
    return out


def disk_exists(rel):
    return os.path.isfile(os.path.join(TEX, rel))


def main(argv):
    pack_races, rows = census()
    probs = problems(rows, disk_exists)
    if "--list-missing" in argv:
        seen = set()
        for _k, _p, _why, base, pack in probs:
            if pack and pack not in seen:
                seen.add(pack)
                print("%s\t%s" % (base, pack))
        return 0

    check("census sees RSW_Ronto as a pack animal (instrument can see)", "RSW_Ronto" in pack_races, sorted(pack_races))
    check("census sees >= 30 pack races (43 on 2026-10-31)", len(pack_races) >= 30, len(pack_races))

    ronto = [r for r in rows if r[1] == "RSW_Ronto"]
    hidden = "RimStarWars/SWBestiary/Ronto/RontoPack_south.png"
    got = problems(ronto, lambda rel: rel != hidden and disk_exists(rel))
    check("break: hiding %s reddens Ronto" % hidden, any(g[4] == hidden for g in got), got)
    fake = [("RSW_FakeKind", "RSW_Fake", "fake/Beast")]
    got = problems(fake, lambda rel: rel in ("fake/Beast_south.png", "fake/Beast_east.png"))
    check("break: a race with base facings and no Pack art reddens",
          sorted(g[4] for g in got) == ["fake/BeastPack_east.png", "fake/BeastPack_south.png"], got)

    by_path = {}
    for kind, p, why, _b, _pk in probs:
        by_path.setdefault((p, why), []).append(kind)
    for (p, why), ks in sorted(by_path.items()):
        check("pack art %s" % p, False, "%s (kinds: %s)" % (why, ", ".join(sorted(set(ks)))))
    check("every pack-animal life-stage graphic has its Pack facings (%d graphics, %d races)"
          % (len(set(r[2] for r in rows)), len(pack_races)), not probs, "%d problem(s)" % len(probs))

    if FAILS:
        print("\n%d SWBestiary pack-texture check(s) FAILED" % len(FAILS))
        return 1
    print("\nall SWBestiary pack-texture checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
