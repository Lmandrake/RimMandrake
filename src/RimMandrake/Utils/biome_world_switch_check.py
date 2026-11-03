#!/usr/bin/env python3
"""biome_world_switch_check.py -- is any tile of the canonical planet still on a donor or vanilla biome?

BIOME_WORLD_SWITCH_WAVE_1's verify line, read offline from the save players receive (the planet IS that
save; `world/ASHKARR_WORLDMAP_tiles.csv` is only a dated record of it):

    python3 src/RimMandrake/Utils/biome_world_switch_check.py [--save <rws>] [--probe <rws>]

Pass (exit 0) when, on the save named by `infrastructure/state/canon.yml` planet.start_savegame:
  * 0 tiles sit on any of the 23 donor/vanilla BiomeDefs the item measured on 2026-09-12;
  * every tile's biome resolves to an `RM_`/`RUT_` defName AND that defName is declared by a BiomeDef under
    src/ -- the item's "owned successor": a retired or renamed name still painted (RM_Wasteland, renamed
    RM_Wastes; RM_NightsideIce, renamed RM_SleepingIce) resolves to nothing on a load, so it FAILs;
  * tile 17007 (the player start, the owner's "GRiNDTerra" complaint) is on an owned def that some repo mod
    under src/ declares.
Exit 1 is a real FAIL (a donor or non-owned def painted wins over an unnamed hash). Exit 2 is UNMEASURED: a tile
hash no source can name, or the sanity probe failed.

Tiles hold a 2-byte BiomeDef shortHash. A hash is named from the offline def dump first; a def absent from the
dump (a retired or renamed defName still painted, a donor whose mod is not in the dump's set) is named by
RimWorld's own ShortHashGiver formula over a candidate list. The formula is checked against the dump on every
run, and the decoder must find donors on an older save that is known to hold them (`--probe`), or nothing this
script says about "zero donors" is evidence (instrument_traps.md: a zero is a query bug until a probe sees).
"""
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import worldmap  # noqa: E402

# The item's measured donor/vanilla set, 2026-09-12 live export (items/BIOME_WORLD_SWITCH_WAVE_1.md).
DONORS = (
    "ExtremeDesert AB_PropaneLakes Desert AB_MycoticJungle Wasteland AB_RockyCrags ZBiome_Badlands "
    "AridShrubland PoisonForest AB_MechanoidIntrusion BiomeCypreJungle ZBiome_DesertOasis ZBiome_Grasslands "
    "AB_OcularForest AB_FeraliskInfestedJungle AB_GelatinousSuperorganism AB_MiasmicMangrove Scarlands "
    "COMIGO_GreaterSwamp_Tropical AB_TarPits AB_PyroclasticConflagration LavaField Volcano"
).split()
START_TILE = 17007
PROBE_SAVE = os.path.join(REPO, "world", "ASHKARR_DRAFT_2026-08-24.rws")  # pre-switch: holds donors
OWNED = re.compile(r"^(RM|RUT)_")
DEFNAME = re.compile(r"\b(?:RM|RUT)_[A-Za-z0-9_]+\b")


def short_hash(name):
    """RimWorld ShortHashGiver's first pick: StableStringHash(defName) % 65535 as ushort (C# int arithmetic).
    A collision bumps the real hash, so a name is trusted to this only when the dump does not know it."""
    n = 23
    for ch in name:
        n = (n * 31 + ord(ch)) & 0xFFFFFFFF
    if n >= 2 ** 31:
        n -= 2 ** 32
    return (n - 65535 * int(n / 65535)) & 0xFFFF


def canonical_save():
    with open(os.path.join(REPO, "infrastructure", "state", "canon.yml"), encoding="utf-8") as fh:
        m = re.search(r"^\s*start_savegame:\s*(\S+)", fh.read(), re.M)
    if not m:
        raise SystemExit("UNMEASURED: canon.yml carries no planet.start_savegame")
    return os.path.join(REPO, "world", m.group(1))


def src_biome_defs():
    """defName -> repo mod folders that declare it as a BiomeDef."""
    out = {}
    for p in glob.glob(os.path.join(REPO, "src", "**", "BiomeDefs", "*.xml"), recursive=True):
        with open(p, encoding="utf-8", errors="replace") as fh:
            for n in re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", fh.read()):
                out.setdefault(n, set()).add(os.path.relpath(p, REPO).split(os.sep)[2])
    return out


def candidate_names(src_defs):
    """Names a tile may hold that the dump may not know: every src BiomeDef, every RM_/RUT_ name a world
    plan or the defName-migration item mentions (retired names stay painted until the save is repainted),
    and the donors."""
    names = set(src_defs) | set(DONORS)
    for p in (glob.glob(os.path.join(REPO, "world", "paint_inputs_*", "*.json"))
              + glob.glob(os.path.join(REPO, "infrastructure", "state", "items", "**",
                                       "BIOME_DEFNAME_MIGRATION_WAVE_1.md"), recursive=True)):
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                names |= set(DEFNAME.findall(fh.read()))
    return names


def decode(save, fwd, by_formula, conflict=frozenset()):
    g = worldmap.WorldGrid(save)
    names, unnamed = [], set()
    for h in g.arrays["tileBiome"]:
        n = None if h in conflict else (fwd.get(h) or by_formula.get(h))
        if n is None:
            unnamed.add(h)
        names.append(n or "?%d" % h)
    return names, unnamed, g.arrays["tileBiome"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--save", help="save to judge (default: canon.yml planet.start_savegame)")
    ap.add_argument("--probe", default=PROBE_SAVE, help="a save known to hold donors (sanity probe)")
    a = ap.parse_args(argv)
    save = a.save or canonical_save()
    if not os.path.exists(save):
        print("UNMEASURED: no save at %s" % save)
        return 2

    fwd, rev = worldmap.load_hash_table("BiomeDef")
    agree = sum(1 for h, n in fwd.items() if short_hash(n) == h)
    if not fwd or agree < 0.9 * len(fwd):
        print("UNMEASURED: hash formula agrees with the dump on %d of %d BiomeDefs" % (agree, len(fwd)))
        return 2
    src_defs = src_biome_defs()
    # A fallback hash two candidates share names neither: those tiles stay unnamed (UNMEASURED).
    groups = {}
    for n in candidate_names(src_defs):
        if n not in rev:
            groups.setdefault(short_hash(n), set()).add(n)
    by_formula = {h: next(iter(ns)) for h, ns in groups.items() if len(ns) == 1}
    # A fallback name whose formula hash the dump gives another def: the save's mod set may have given it to
    # the fallback instead, so neither name is trusted there.
    conflict = {h for h in groups if h in fwd}

    # Sanity probe: the instrument must SEE donors where they are known to be.
    if a.probe:
        pnames, _, _ = decode(a.probe, fwd, by_formula, conflict)
        seen = sum(1 for n in pnames if n in DONORS)
        print("probe %s: %d tiles on donor defs" % (os.path.basename(a.probe), seen))
        if seen == 0:
            print("UNMEASURED: the decoder sees no donor on a pre-switch save; a zero below would mean nothing")
            return 2

    names, unnamed, _ = decode(save, fwd, by_formula, conflict)
    # By decoded name only: a bare formula hash is not evidence (a collision makes it ambiguous).
    donor_tiles = [i for i, n in enumerate(names) if n in DONORS]
    foreign = sorted({n for n in names if not OWNED.match(n) and not n.startswith("?")})
    # Owned means declared by one of our mods today, not merely spelled with our prefix.
    dead = sorted({n for n in names if OWNED.match(n) and n not in src_defs})
    counts = {}
    for n in names:
        counts[n] = counts.get(n, 0) + 1
    print("save %s: %d tiles, %d defs" % (os.path.basename(save), len(names), len(counts)))
    for n, c in sorted(counts.items(), key=lambda t: -t[1]):
        print("  %-24s %6d%s" % (n, c, "" if n in src_defs else "  (no src BiomeDef: retired/renamed name)"))
    start = names[START_TILE] if START_TILE < len(names) else None
    print("tile %d: %s, declared by %s" % (START_TILE, start, sorted(src_defs.get(start, ())) or "no src mod"))
    print("donor tiles: %d   non-owned defs: %s   dead owned names: %s   unnamed hashes: %s"
          % (len(donor_tiles), foreign or "none",
             ", ".join("%s %d" % (n, counts[n]) for n in dead) or "none", sorted(unnamed) or "none"))

    if donor_tiles or foreign:
        print("FAIL: donor or non-owned defs still painted")
        return 1
    if dead:
        print("FAIL: %d tiles on %d RM_/RUT_ name(s) no src BiomeDef declares (retired/renamed; repaint them)"
              % (sum(counts[n] for n in dead), len(dead)))
        return 1
    if unnamed:
        print("UNMEASURED: %d tile hash(es) no source names" % len(unnamed))
        return 2
    if not start or not OWNED.match(start) or start not in src_defs:
        print("FAIL: tile %d is not on an owned def a src mod declares" % START_TILE)
        return 1
    print("PASS: 0 of %d tiles on the %d donor/vanilla defs; every tile on an RM_/RUT_ def a src mod declares"
          % (len(names), len(DONORS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
