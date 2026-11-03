#!/usr/bin/env python3
"""Offline proof of PLAYER_START_SITE_1's start-site build: Zeddo's Salvage Yard (RUT_ZeddosYard).

    python3 src/RimMandrake/Utils/selftest_zeddos_yard.py

Bars (each prints PASS/FAIL; exit 1 on any FAIL):
  B1 the committed plan is exactly the generator's output (gen_zeddos_yard_plan.py --check)
  B2 the plan passes the StructureInjections template lint (the GenStep's own reader grammar)
  B3 a CLEAR all rect >= hull 92x86 + 2 margin (96x90) sits at the footprint centre and NO thing's
     occupied cells and NO terrain cell fall inside it (the landing clearing)
  B4 both skylines: >= 60 ship-wreck buildings of >= 6 kinds (ruined ships) and >= 400
     AncientMegastructure terrain cells plus wall stubs (old megastructures)
  B5 every THING is a non-abstract ThingDef and every TERRAIN a TerrainDef of the base game or a DLC (the
     game's own Data/*/Defs XML, parsed; sanity probe: Steel and AncientMegastructure must be found, else UNMEASURED=FAIL)
  B6 the defs: RUT_GenStep_ZeddosYard runs this plan at order < 600 (before ReserveGravshipArea), and
     TileMutatorDef RUT_ZeddosYard carries it
  B7 canon.yml pins it: planet.start_tile == 17007 (read by a YAML loader that REFUSES a duplicate key;
     plain safe_load keeps the last silently) and planet.start_tile_mutator == RUT_ZeddosYard; the final-paint list names it
  B8 planted defects are caught: a thing in the clearing fails B3; a non-DLC def and a ThingDef used as
     terrain fail B5; a duplicate canon key fails B7's loader
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
MOD = os.path.join(REPO, "src", "RimUtinni", "StructureInjectionsRUT")
sys.path.insert(0, os.path.join(MOD, "Source", "ZeddosYard"))
sys.path.insert(0, HERE)
import gen_zeddos_yard_plan as gen  # noqa: E402

PLAN = os.path.join(MOD, "Templates", "zeddos_yard.txt")
DEFS = os.path.join(MOD, "Defs", "GenStepDefs_ZeddosYard.xml")
CANON = os.path.join(REPO, "infrastructure", "state", "canon.yml")
PAINT = os.path.join(REPO, "infrastructure", "state", "items", "BIOME_PAINT_ONCE_AT_THE_END_1.md")
GAME_DATA = os.environ.get("RIMWORLD_DATA", "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data")
NEED_W, NEED_H = gen.HULL_W + 2 * gen.MARGIN, gen.HULL_H + 2 * gen.MARGIN

fails = []


def bar(name, ok, detail=""):
    print("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


def parse(text):
    p = {"foot": None, "clears": [], "things": [], "terrain": []}
    for raw in text.splitlines():
        if not raw or raw.startswith("#"):
            continue
        f = raw.split("\t")
        if f[0] == "FOOTPRINT":
            p["foot"] = tuple(int(v) for v in f[1:5])
        elif f[0] == "CLEAR":
            p["clears"].append((int(f[1]), int(f[2]), int(f[3]), int(f[4]), f[5]))
        elif f[0] == "THING":
            p["things"].append((f[1], int(f[2]), int(f[3]), int(f[4])))
        elif f[0] == "TERRAIN":
            p["terrain"].append((int(f[1]), int(f[2]), f[3]))
    return p


def clearing_violations(p):
    """-> (clearing rect or None, [violations])."""
    fx, fz, fw, fh = p["foot"]
    cx, cz = fx + fw / 2.0, fz + fh / 2.0
    best = None
    for (x, z, w, h, mode) in p["clears"]:
        if mode == "all" and w >= NEED_W and h >= NEED_H and (w, h) != (fw, fh) \
                and abs(x + w / 2.0 - cx) <= 1 and abs(z + h / 2.0 - cz) <= 1:
            best = (x, z, w, h)
    if best is None:
        return None, ["no centred CLEAR all rect >= %dx%d" % (NEED_W, NEED_H)]
    x0, z0, w, h = best
    inside = lambda a, b: x0 <= a < x0 + w and z0 <= b < z0 + h  # noqa: E731
    bad = []
    for d, x, z, rot in p["things"]:
        if d not in gen.SIZES:
            bad.append("unknown size for %s" % d)
            continue
        if any(inside(a, b) for a, b in gen.occupied(d, x, z, rot)):
            bad.append("%s@%d,%d" % (d, x, z))
    bad += ["terrain %s@%d,%d" % (d, x, z) for x, z, d in p["terrain"] if inside(x, z)]
    return best, bad


_DLC_DEFS = None


def dlc_defnames():
    """-> {"ThingDef": set, "TerrainDef": set} of every NON-abstract def under the game's Data/*/Defs
    (base game + the five DLC), parsed as XML (comments are not defs; a ThingDef name is not a
    TerrainDef). None if the folder is unreadable."""
    global _DLC_DEFS
    if _DLC_DEFS is not None:
        return _DLC_DEFS
    if not os.path.isdir(GAME_DATA):
        return None
    names = {"ThingDef": set(), "TerrainDef": set()}
    for top in os.listdir(GAME_DATA):
        for dp, _, fs in os.walk(os.path.join(GAME_DATA, top, "Defs")):
            for f in fs:
                if not f.endswith(".xml"):
                    continue
                try:
                    root = ET.parse(os.path.join(dp, f)).getroot()
                except (ET.ParseError, OSError):
                    continue
                for el in root:
                    if el.tag in names and str(el.get("Abstract", "")).lower() != "true":
                        dn = (el.findtext("defName") or "").strip()
                        if dn:
                            names[el.tag].add(dn)
    _DLC_DEFS = names
    return names


def missing_defs(p):
    """-> sorted names the plan uses under the wrong type or not at all; None when the instrument is blind."""
    names = dlc_defnames()
    if names is None or "Steel" not in names["ThingDef"] or "AncientMegastructure" not in names["TerrainDef"]:
        return None
    miss = ["THING " + d for d in {t[0] for t in p["things"]} if d not in names["ThingDef"]]
    miss += ["TERRAIN " + d for d in {t[2] for t in p["terrain"]} if d not in names["TerrainDef"]]
    return sorted(miss)


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that refuses a duplicate mapping key (plain safe_load silently keeps the last one)."""


def _no_dup_mapping(loader, node, deep=False):
    seen = set()
    for k, _ in node.value:
        key = loader.construct_object(k, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, "duplicate key %r" % (key,), k.start_mark)
        seen.add(key)
    return loader.construct_mapping(node, deep)


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_dup_mapping)


def load_planet(path):
    """-> (planet dict or None, error or None)."""
    try:
        doc = yaml.load(open(path, encoding="utf-8"), Loader=_UniqueKeyLoader) or {}
    except yaml.YAMLError as e:
        return None, str(e).splitlines()[0] if str(e) else repr(e)
    return doc.get("planet") or {}, None


def main():
    text = open(PLAN, encoding="utf-8").read()
    bar("B1 plan == generator output", text == gen.render())

    import lint_structureinjections_defs as lint
    errs = [e for e in lint.template_findings(MOD) if "zeddos_yard" in e]
    bar("B2 template lint", not errs, "; ".join(errs[:3]))

    p = parse(text)
    rect, bad = clearing_violations(p)
    bar("B3 landing clearing", rect is not None and not bad,
        "rect=%s need>=%dx%d violations=%s" % (rect, NEED_W, NEED_H, bad[:5]))

    ships = [t for t in p["things"] if t[0] in gen.SHIP_DEFS]
    kinds = {t[0] for t in ships}
    mega = sum(1 for t in p["terrain"] if t[2] == gen.MEGA_TERRAIN)
    walls = sum(1 for t in p["things"] if t[0] == gen.MEGA_WALL)
    bar("B4 both skylines", len(ships) >= 60 and len(kinds) >= 6 and mega >= 400 and walls >= 10,
        "ship wrecks=%d kinds=%d megastructure cells=%d wall stubs=%d" % (len(ships), len(kinds), mega, walls))

    miss = missing_defs(p)
    bar("B5 defs are base game / DLC", miss == [], "UNMEASURED (game Data unreadable)" if miss is None else "missing=%s" % miss)

    root = ET.parse(DEFS).getroot()
    gs = [g for g in root.findall("GenStepDef") if g.findtext("defName") == "RUT_GenStep_ZeddosYard"]
    tm = [m for m in root.findall("TileMutatorDef") if m.findtext("defName") == "RUT_ZeddosYard"]
    ok6 = (len(gs) == 1 and gs[0].findtext("genStep/planFile") == "Templates/zeddos_yard.txt"
           and int(gs[0].findtext("order") or 9999) < 600
           and len(tm) == 1 and [li.text for li in tm[0].findall("extraGenSteps/li")] == ["RUT_GenStep_ZeddosYard"])
    bar("B6 GenStepDef + TileMutatorDef", ok6)

    planet, yerr = load_planet(CANON)
    paint = open(PAINT, encoding="utf-8").read()
    bar("B7 canon pins the start", yerr is None and planet.get("start_tile") == 17007
        and planet.get("start_tile_mutator") == "RUT_ZeddosYard" and "RUT_ZeddosYard" in paint,
        "yaml error=%r start_tile=%r start_tile_mutator=%r" % (yerr, (planet or {}).get("start_tile"),
                                                               (planet or {}).get("start_tile_mutator")))

    # B8 planted defects: the instruments must be able to see a failure.
    planted = dict(p, things=p["things"] + [("ShipChunk", gen.W // 2, gen.H // 2, 0)])
    _, bad8 = clearing_violations(planted)
    planted2 = dict(p, things=p["things"] + [("RSW_WreckedSkiff", 3, 3, 0)])
    miss8 = missing_defs(planted2)
    planted3 = dict(p, terrain=p["terrain"] + [(3, 3, "Steel")])        # a ThingDef named as terrain
    miss8b = missing_defs(planted3)
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as tf:
        tf.write("planet:\n  start_tile: 1\n  start_tile: 17007\n  start_tile_mutator: RUT_ZeddosYard\n")
    _, dup_err = load_planet(tf.name)
    os.unlink(tf.name)
    bar("B8 planted defects caught", bool(bad8) and miss8 is not None and "THING RSW_WreckedSkiff" in miss8
        and miss8b is not None and "TERRAIN Steel" in miss8b and dup_err is not None,
        "clearing=%s defs=%s terrain-type=%s dup-key=%r" % (bad8[:1], miss8, miss8b, dup_err))

    print("RESULT: %s" % ("GREEN" if not fails else "RED " + ", ".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
