#!/usr/bin/env python3
"""Tree crowns cast Direct Sun shade by the sun's geometry: the defs and source half (offline, seconds).

Items: TREE_SHADE_BUILD_CROWNS_ON_STILTS, TREE_SHADE_SELFTEST_PROVE_FOREST_IS_SHADE. Design:
design/RimMandrake/tree_shade_model_2026-10-19.md §4, §6. Page: design/specs/2026-11-26-tree-crowns/boundary.md.
The geometry (T1, T2 offline, T4, T5, T6 of design §6) is the C# half: `python3 src/RimMandrake/Utils/selftest_sun_heat.py`,
cases named "tree crowns: ...". This file reads defs and source:

  no_biome_field   no BiomeDef under src/, and no patch value aimed at a BiomeDef, carries an element whose name holds
                   a crown or canopy joined to a shade number (WORD), nor RM_TreeCrownExtension (XML parsed as
                   elements): a tree shades the same in every biome.
  giants           Patches/RM_TreeCrowns_Giants.xml gives each of the six day-side giants the crown factors measured
                   from its art (src/RimMandrake/HugeThings/tree_crowns_measured.json, rounded to 0.01), aimed at a
                   ThingDef that exists under src/ with a <plant> node; nothing else.
  plant_only       every RM_TreeCrownExtension in XML under src/ sits on a ThingDef (a def or a patch xpath on ThingDef).
  settings         Creature Behaviors has the canopy rows of design §4.6: treeCanopyShadeEnabled (on),
                   canopyShadeStrength (1), shadeOverlayButton (on), canopyGroundTint (on), each saved with that default
                   and named in the Direct Sun group; no per-biome canopy switch.
  wiring           the shade grid casts each tree's crown in Recompute through RM_SunHeatMath.CastCrown (growth-aware
                   drawn size), folds it into the cast layer, and a shade tree's DeSpawn asks for a recompute; the
                   readout, the sun-load line and the overlay read the grid's cause and exposure.

Then each check is shown to fire on a planted fault in a temp copy (--no-mutate skips that).

    python3 src/RimMandrake/Utils/selftest_tree_crowns.py [--only giants,...] [--no-mutate]
Exit 0: all chosen checks pass. 1: a check failed (named). 2: could not look (a file it needs is missing).
"""
import argparse
import glob
import json
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
EXT = "RimMandrake.CreatureBehaviors.RM_TreeCrownExtension"
GIANTS = ("RM_Greatbole", "RM_Nogtyl", "RSW_Plant_HydenockTree_Wild", "RM_CorriskTree", "RM_Veluthar", "RM_Kaddrath")
CB = "src/RimMandrake/CreatureBehaviors"
GIANTS_XML = CB + "/Patches/RM_TreeCrowns_Giants.xml"
CROWNS_JSON = "src/RimMandrake/HugeThings/tree_crowns_measured.json"
SETTINGS = {"treeCanopyShadeEnabled": "true", "canopyShadeStrength": "1f", "shadeOverlayButton": "true",
            "canopyGroundTint": "true"}
# A crown or canopy SHADE field (a field name, not a plant's defName used as a roster key, and not a def reference such as
# the Leaning Scrub's venomvine crownDef): crown/canopy joined to a shade number, either way round.
WORD = re.compile(r"(canopy|crown)\w*(shade|radius|height|opacity|factor|strength)|shade\w*(canopy|crown)", re.I)


class CouldNotLook(Exception):
    pass


def _p(root, *a):
    return os.path.join(root, *a)


def _read(root, rel):
    path = _p(root, rel)
    if not os.path.isfile(path):
        raise CouldNotLook("missing %s" % rel)
    with open(path, encoding="utf-8") as f:
        return f.read()


def xml_files(root):
    for path in glob.glob(_p(root, "src", "**", "*.xml"), recursive=True):
        if os.sep + "About" + os.sep in path or os.sep + "Languages" + os.sep in path:
            continue
        yield path


def parse(path):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        return None   # a broken XML file is another test's finding; it carries no def we can read


def _rel(root, path):
    return os.path.relpath(path, root)


def _patch_values(r):
    """-> [(xpath, value element)] for every operation under a <Patch> root, nested ones included."""
    out = []
    for op in r.iter():
        xp = op.find("xpath")
        val = op.find("value")
        if xp is not None and val is not None and xp.text:
            out.append((xp.text.strip(), val))
    return out


def check_no_biome_field(root, rows, fails):
    n = 0
    for path in xml_files(root):
        r = parse(path)
        if r is None:
            continue
        if r.tag == "Defs":
            for b in r.iter("BiomeDef"):
                n += 1
                for el in b.iter():
                    if WORD.search(el.tag) or el.get("Class") == EXT:
                        fails.append("no_biome_field: %s BiomeDef %s carries <%s>" % (
                            _rel(root, path), b.findtext("defName"), el.tag))
        elif r.tag == "Patch":
            for xp, val in _patch_values(r):
                if "BiomeDef" not in xp:
                    continue
                for el in val.iter():
                    if WORD.search(el.tag) or el.get("Class") == EXT:
                        fails.append("no_biome_field: %s patches <%s> onto %s" % (_rel(root, path), el.tag, xp))
    if n == 0:
        raise CouldNotLook("no BiomeDef found under src/ (the instrument is blind)")
    if not any(f.startswith("no_biome_field") for f in fails):
        rows.append("PASS no_biome_field: %d BiomeDefs and every BiomeDef patch carry no crown or canopy field" % n)


def _thingdefs(root):
    out = {}
    for path in xml_files(root):
        r = parse(path)
        if r is None or r.tag != "Defs":
            continue
        for t in r.iter("ThingDef"):
            name = t.findtext("defName")
            if name:
                out.setdefault(name, t)
    return out


def check_giants(root, rows, fails):
    try:
        measured = json.loads(_read(root, CROWNS_JSON))["plants"]
    except (ValueError, KeyError) as e:
        raise CouldNotLook("%s unreadable: %s" % (CROWNS_JSON, e))
    r = parse(_p(root, GIANTS_XML)) if os.path.isfile(_p(root, GIANTS_XML)) else None
    if r is None:
        fails.append("giants: %s is missing or not XML" % GIANTS_XML)
        return
    defs = _thingdefs(root)
    seen = {}
    for xp, val in _patch_values(r):
        m = re.fullmatch(r'Defs/ThingDef\[defName="([^"]+)"\]', xp)
        li = val.find("li")
        if m is None or li is None or li.get("Class") != EXT:
            continue
        seen[m.group(1)] = li
    for name in GIANTS:
        li = seen.get(name)
        if li is None:
            fails.append("giants: %s has no crown override in %s" % (name, GIANTS_XML))
            continue
        if name not in measured:
            fails.append("giants: %s is not measured in %s" % (name, CROWNS_JSON))
            continue
        for field in ("crownRadiusFactor", "crownHeightFactor"):
            want = round(measured[name][field], 2)
            got = li.findtext(field)
            if got is None or abs(float(got) - want) > 1e-6:
                fails.append("giants: %s %s is %s, measured %s" % (name, field, got, want))
        d = defs.get(name)
        if d is None or d.find("plant") is None:
            fails.append("giants: %s is not a plant ThingDef under src/" % name)
    extra = sorted(set(seen) - set(GIANTS))
    if extra:
        fails.append("giants: %s overrides more than the six giants: %s" % (GIANTS_XML, ", ".join(extra)))
    rows.append("PASS giants: the six giants carry their measured crown factors" if not any(
        f.startswith("giants") for f in fails) else "FAIL giants")


def check_plant_only(root, rows, fails):
    n = 0
    for path in xml_files(root):
        r = parse(path)
        if r is None:
            continue
        if r.tag == "Defs":
            for d in r:
                for el in d.iter("li"):
                    if el.get("Class") == EXT:
                        n += 1
                        if d.tag != "ThingDef":
                            fails.append("plant_only: %s puts the crown extension on a %s" % (_rel(root, path), d.tag))
        elif r.tag == "Patch":
            for xp, val in _patch_values(r):
                for el in val.iter("li"):
                    if el.get("Class") == EXT:
                        n += 1
                        if not xp.startswith("Defs/ThingDef["):
                            fails.append("plant_only: %s aims the crown extension at %s" % (_rel(root, path), xp))
    if n == 0:
        fails.append("plant_only: no RM_TreeCrownExtension found under src/")
    if not any(f.startswith("plant_only") for f in fails):
        rows.append("PASS plant_only: %d crown extensions, each on a ThingDef" % n)


def check_settings(root, rows, fails):
    src = _read(root, CB + "/Source/RM_CreatureBehaviorsMod.cs")
    group = re.search(r'Group\(list, "Direct Sun", new\[\] \{([^}]*)\}', src)
    names = group.group(1) if group else ""
    for name, default in SETTINGS.items():
        typ = "float" if default.endswith("f") else "bool"
        if not re.search(r"public static %s %s = %s;" % (typ, name, re.escape(default)), src):
            fails.append("settings: %s does not default to %s" % (name, default))
        scribe_default = default.rstrip("f") + ("f" if typ == "float" else "")
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s", %s\);' % (name, name, re.escape(scribe_default)), src):
            fails.append("settings: %s is not saved with its default %s" % (name, scribe_default))
        if '"%s"' % name not in names:
            fails.append("settings: %s is not named in the Direct Sun group" % name)
    if re.search(r"canopy\w*biome|biome\w*canopy", src, re.I):
        fails.append("settings: a per-biome canopy switch exists")
    rows.append("PASS settings: the canopy rows match design §4.6" if not any(
        f.startswith("settings") for f in fails) else "FAIL settings")


WIRING = [
    ("RM_MapComponent_ShadeGrid.cs", r"CastCrownOf\(tree, width, height\)", "Recompute casts each tree's crown"),
    ("RM_MapComponent_ShadeGrid.cs", r"RM_SunHeatMath\.CastCrown\(canopyShade,", "the crown goes through RM_SunHeatMath.CastCrown"),
    ("RM_MapComponent_ShadeGrid.cs", r"if \(canopyShade\[k\] > castShade\[k\]\)", "the crowns fold into the cast layer"),
    ("RM_MapComponent_ShadeGrid.cs", r"DrawnSize\(drawX, p\.visualSizeRange\.min, p\.visualSizeRange\.max, plant\.Growth\)",
     "the drawn size is growth-aware"),
    ("RM_TreeCrownPatches.cs", r"typeof\(Plant\), nameof\(Plant\.DeSpawn\)", "Plant.DeSpawn is patched"),
    ("RM_TreeCrownPatches.cs", r"RequestPlantRecompute\(\)", "a shade tree's despawn asks for a recompute"),
    ("RM_TreeCrownPatches.cs", r"grid\.ShadeCauseAt\(c\)", "the readout names the cause"),
    ("RM_Gizmo_SunLoad.cs", r"grid\.ShadeCauseAt\(pawn\.Position\)", "the sun-load line names the cause"),
    ("RM_ShadeOverlay.cs", r"grid\.OverlayShade\(i\)", "the overlay reads the grid"),
    ("RM_MapComponent_ShadeGrid.cs", r"return 1f - exposure\[i\];", "the overlay is the exposure ExposureAt reads"),
]


def check_wiring(root, rows, fails):
    for f, pat, what in WIRING:
        rel = CB + "/Source/" + f
        if not os.path.isfile(_p(root, rel)):
            fails.append("wiring: %s (%s is missing)" % (what, f))
            continue
        if not re.search(pat, _read(root, rel)):
            fails.append("wiring: %s (%s lacks /%s/)" % (what, f, pat))
    rows.append("PASS wiring: %d links" % len(WIRING) if not any(f.startswith("wiring") for f in fails) else "FAIL wiring")


# The promises of design/specs/2026-11-26-tree-crowns/boundary.md (boundary_check.py: a test of each name).
t_no_biome_carries_a_crown_field = check_no_biome_field
t_the_giants_carry_their_measured_crowns = check_giants
t_the_extension_sits_on_plant_thingdefs_only = check_plant_only
t_the_canopy_settings_match_the_design = check_settings
t_the_grid_casts_crowns_and_clears_on_despawn = check_wiring

CHECKS = [("no_biome_field", check_no_biome_field), ("giants", check_giants), ("plant_only", check_plant_only),
          ("settings", check_settings), ("wiring", check_wiring)]


def run(root, only):
    rows, fails = [], []
    for name, fn in CHECKS:
        if only and name not in only:
            continue
        fn(root, rows, fails)
    return rows, fails


def _copy(root, tmp):
    shutil.copytree(_p(root, "src"), _p(tmp, "src"), ignore=shutil.ignore_patterns(
        "*.dll", "*.png", "*.jpg", "*.ogg", "*.wav", "Textures", "Sounds", "bin", "obj", "Assemblies", "*.pdb", "*.psd"))


def _edit(path, old, new):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    if old not in s:
        raise CouldNotLook("planted fault: %r not in %s" % (old[:60], path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(s.replace(old, new, 1))


PLANTS = [
    ("no_biome_field", "src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml", "<defName>RM_Pyrelands</defName>",
     "<defName>RM_Pyrelands</defName>\n    <canopyShadeFactor>0.5</canopyShadeFactor>"),
    ("giants", GIANTS_XML, "<crownRadiusFactor>0.97</crownRadiusFactor>", "<crownRadiusFactor>0.8</crownRadiusFactor>"),
    # One giant's AddModExtension aimed at a BiomeDef (its Conditional still matches the ThingDef).
    ("plant_only", GIANTS_XML, '<match Class="PatchOperationAddModExtension">\n      <xpath>Defs/ThingDef[defName="RM_Kaddrath"]',
     '<match Class="PatchOperationAddModExtension">\n      <xpath>Defs/BiomeDef[defName="RM_Greentide"]'),
    ("settings", CB + "/Source/RM_CreatureBehaviorsMod.cs", "public static bool canopyGroundTint = true;",
     "public static bool canopyGroundTint = false;"),
    ("wiring", CB + "/Source/RM_MapComponent_ShadeGrid.cs", "CastCrownOf(tree, width, height);", "// crowns not cast"),
]


def mutate(root, only):
    out = []
    for name, rel, old, new in PLANTS:
        if only and name not in only:
            continue
        tmp = tempfile.mkdtemp(prefix="tc_mut_")
        try:
            _copy(root, tmp)
            _edit(_p(tmp, rel), old, new)
            try:
                _, fails = run(tmp, {name})
            except CouldNotLook as e:
                fails = [name + ": could not look: %s" % e]
            caught = any(f.startswith(name) for f in fails)
            out.append(("CAUGHT" if caught else "NOT CAUGHT", name, rel))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", default="", help="comma list of checks: " + ",".join(n for n, _ in CHECKS))
    ap.add_argument("--no-mutate", action="store_true", help="skip the planted-fault pass")
    ap.add_argument("--root", default=REPO, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    # Every promise's test runs by default; --only narrows a run by hand.
    promised = (t_no_biome_carries_a_crown_field, t_the_giants_carry_their_measured_crowns,
                t_the_extension_sits_on_plant_thingdefs_only, t_the_canopy_settings_match_the_design,
                t_the_grid_casts_crowns_and_clears_on_despawn)
    assert all(fn in dict(CHECKS).values() for fn in promised)
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    unknown = only - {n for n, _ in CHECKS}
    if unknown:
        print("COULD NOT LOOK: unknown check(s) %s" % ",".join(sorted(unknown)))
        return 2
    try:
        rows, fails = run(a.root, only)
    except CouldNotLook as e:
        print("COULD NOT LOOK: %s" % e)
        return 2
    for r in rows:
        print(r)
    for f in fails:
        print("FAIL " + f)
    if fails:
        print("%d check(s) failed" % len(fails))
        return 1
    if not a.no_mutate:
        try:
            muts = mutate(a.root, only)
        except CouldNotLook as e:
            print("COULD NOT LOOK: %s" % e)
            return 2
        for verdict, name, rel in muts:
            print("%s planted fault: %s (%s)" % (verdict, name, rel))
        if any(v != "CAUGHT" for v, _, _ in muts):
            print("FAIL a planted fault was not caught")
            return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
