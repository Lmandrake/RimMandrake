#!/usr/bin/env python3
"""Selftest: the planet's VEE landmarks are ported to our own LandmarkDefs, and the Ash'karr icons follow them.

Item VEE_LANDMARKS_MIGRATE_KEEP_THE_ICONS; plan design/RimMandrake/vee_port_plan_2026-10-22.md §1b (the 24 VEE
landmark defs on the planet) and §2 (VEE_<Stem> -> RM_<Stem>; VEE_QuicksandPits -> the existing RM_QuicksandPits).

Proves, offline and from the repo alone:
  1. every landmark of plan §1b has an RM_ LandmarkDef: RM_QuicksandPits in EnvironmentalHazards, the other 23 in
     TileFeatures' landmark file (and that file holds nothing else);
  2. each port requires exactly the ports of VEE's required mutators, its own RM_ mutator among them (a TileMutatorDef in src with chanceOnNonLandmarkTile 0; cactus fields
     require the four cactus ports and overgrowth, as VEE's did); only RM_CraterLake requires vanilla Lake instead, because the VEE_CraterLake mutator is on no planet tile and was never ported (§1a);
  3. every other name a port carries is ours (RM_, defined in src) or a vanilla/DLC def from the list below, and its
     icon and namer are vanilla ones (VEE's textures and namer RulePacks leave with VEE);
  4. no VEE_ name in the port file, and LandmarkIcons.xml targets no VEE_ def: each of the 18 VEE icons it carried
     now targets RM_<Stem> with the same Ash'karr texture, and that PNG is in the mod;
  5. the instrument can see: planted defects (a port removed, a VEE_ requirement, an unknown mutator, a foreign
     icon, a VEE_ patch target, a missing texture) are each caught.
When the game's Data folder is readable, the vanilla list itself is checked against the game's defs (else said so).

    python3 src/RimMandrake/Utils/selftest_tilefeatures_landmarks.py
"""
import copy
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PLAN = os.path.join(ROOT, "design", "RimMandrake", "vee_port_plan_2026-10-22.md")
PORTS = os.path.join(ROOT, "src", "RimMandrake", "TileFeatures", "Defs", "LandmarkDefs", "RM_TileFeatures_Landmarks.xml")
ART = os.path.join(ROOT, "src", "RimUtinni", "AshkarrLandmarkArt")
ICONS = os.path.join(ART, "Patches", "LandmarkIcons.xml")
GAME_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"

REUSED = {"QuicksandPits": "RM_QuicksandPits"}
# Each port's Required set is VEE's, renamed VEE_ -> RM_ (read from VEE's Landmarks.xml on 2026-11-05); a port not
# listed requires exactly RM_<Stem>. The VEE_CraterLake mutator is on no planet tile and was never ported (§1a; its
# landmark is on one); LandmarkDef.ConfigErrors still demands a chance >= 1 entry, so the vanilla Lake mutator stands in.
VANILLA_REQUIRED = {"RM_CraterLake": {"Lake"}}
OTHER_REQUIRED = {
    "RM_DustBowl": {"RM_DustBowl", "RM_PlantLife_Decimated", "RM_Fertility_Reduced", "RM_DustStorms"},
    "RM_SulfuricLake": {"RM_SulfuricLake", "PlantLife_Increased", "RM_RottenStench"},
    "RM_RedDesert": {"RM_RedDesert", "RM_RedDesertPlants", "RM_Sandstorms", "RM_Cactus_Barrel", "RM_Cactus_Hedgehog"},
}
# VEE's cactus fields have no landform of their own: the landmark requires the four cactus mutators and overgrowth.
REQUIRED_INSTEAD = {"RM_CactusFields": {"RM_Cactus_Barrel", "RM_Cactus_Beavertail", "RM_Cactus_Hedgehog",
                                        "RM_Cactus_OrganPipe", "RM_PlantLife_Overgrown"}}
# The 18 VEE landmarks AshkarrLandmarkArt repainted before this port (its LandmarkIcons.xml, 2026-11-05).
ASHKARR = ["AlluvialFan", "Cenotes", "DryRiver", "DustBowl", "FleshPits", "GravelBeach", "JaggedRocks", "MeteorCrater",
           "PebbleDunes", "QuicksandDunes", "RedDesert", "RockRidge", "SaltPlains", "SerpentineCanyons",
           "StagnantRivulet", "StoneForest", "SulfuricLake", "ToxicCrater"]
# Vanilla/DLC defs the ports name (read from the game's Data/*/Defs on 2026-11-05).
VANILLA_MUTATORS = {"AncientUplink", "AnimalHabitat", "AnimalLife_Decreased", "AnimalLife_Increased", "ArcheanTrees",
                    "Fertile", "FoggyMutator", "InsectMegahive", "Junkyard", "MineralRich", "MixedBiome", "Muddy",
                    "PlantGrove", "PlantLife_Decreased", "PlantLife_Increased", "Pollution_Increased", "Sandy",
                    "SteamGeysers_Increased", "Stockpile", "SunnyMutator", "WetClimate", "WildPlants",
                    "WildTropicalPlants", "WindyMutator", "Caves", "Fish_Increased", "Fish_Decreased", "Marshy",
                    "ObsidianDeposits", "DryGround", "HotSprings", "Lakeshore", "AncientRuins", "Wetland", "Pond",
                    "Mountain", "Cavern", "Valley", "Chasm", "Basin", "Cliffs", "Hollow", "Plateau", "Crevasse",
                    "Dunes", "TerraformingScar", "ToxicLake", "LavaCaves", "AncientToxVent", "AncientSmokeVent",
                    "AncientHeatVent", "CaveLakes", "UndergroundCave", "Coast", "River", "Lake"}
VANILLA_LANDMARKS = {"Valley", "Cavern", "Chasm", "TerraformingScar", "Basin", "Cliffs", "Hollow", "Plateau",
                     "Crevasse", "Dunes", "Wetland", "Pond", "DryLake", "ToxicLake", "HotSprings", "Lake", "Oasis"}
VANILLA_ICONS = {"World/Landmarks/" + n for n in ("Pond", "DryLake", "Cliffs", "Bay", "Chasm", "Basin", "Dunes",
                                                   "Wetland", "Crevasse", "Valley", "ToxicLake", "Lake", "Plateau",
                                                   "Hollow", "LavaLake")}
VANILLA_NAMERS = {"NamerLandmark_" + n for n in ("Pond", "DryLake", "Cliffs", "Bay", "Chasm", "Basin", "Dunes",
                                                  "Wetland", "Crevasse", "Valley", "ToxicLake", "Lake", "Plateau",
                                                  "Hollow", "LavaLake")}


def plan_landmarks(text):
    sec = re.search(r"### 1b\. Landmarks on R3.*?\n(.*?)That is (\d+) defs", text, re.S)
    names = re.findall(r"`VEE_(\w+)` \d+", sec.group(1)) if sec else []
    return names, int(sec.group(2)) if sec else -1


def src_defs():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "src", "**", "Defs", "**", "*.xml"), recursive=True):
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in r:
            n = d.findtext("defName")
            if n:
                out[(d.tag, n)] = (d, p)
    return out


def check(stems, ports_root, defs, icons_root, texture_exists):
    """Returns failure strings. ports_root: the TileFeatures landmark file; defs: src defs; icons_root: the patch."""
    fails = []
    ports = {d.findtext("defName"): d for d in ports_root if d.tag == "LandmarkDef"}
    want = set()
    for stem in stems:
        name = REUSED.get(stem, "RM_" + stem)
        if stem in REUSED:
            hit = defs.get(("LandmarkDef", name))
            if hit is None or os.sep + "EnvironmentalHazards" + os.sep not in hit[1]:
                fails.append("VEE_%s: reused port %s not found in EnvironmentalHazards" % (stem, name))
            continue
        want.add(name)
        if name not in ports:
            fails.append("VEE_%s: no LandmarkDef %s in TileFeatures" % (stem, name))
    for extra in sorted(set(ports) - want):
        fails.append("%s: in the port file but not a planet landmark of plan §1b" % extra)
    for name, d in sorted(ports.items()):
        if "VEE_" in ET.tostring(d, encoding="unicode"):
            fails.append("%s: names a VEE_ def" % name)
        mc = d.find("mutatorChances")
        kids = list(mc) if mc is not None else []
        req = [c.tag for c in kids if c.get("Required") == "True"]
        if name in VANILLA_REQUIRED:
            if set(req) != VANILLA_REQUIRED[name]:
                fails.append("%s: requires %s, expected the vanilla stand-in %s" % (name, sorted(req), sorted(VANILLA_REQUIRED[name])))
        elif name in REQUIRED_INSTEAD:
            if set(req) != REQUIRED_INSTEAD[name]:
                fails.append("%s: requires %s, VEE required the ports of %s" % (name, sorted(req), sorted(REQUIRED_INSTEAD[name])))
        elif set(req) != OTHER_REQUIRED.get(name, {"RM_" + name[3:]}):
            fails.append("%s: requires %s, VEE required the ports of %s"
                         % (name, sorted(req), sorted(OTHER_REQUIRED.get(name, {"RM_" + name[3:]}))))
        for c in kids:
            if c.tag.startswith("RM_"):
                hit = defs.get(("TileMutatorDef", c.tag))
                if hit is None:
                    fails.append("%s: names %s, no TileMutatorDef of ours" % (name, c.tag))
                elif c.get("Required") == "True" and (hit[0].findtext("chanceOnNonLandmarkTile") or "").strip() != "0":
                    fails.append("%s: required %s has chanceOnNonLandmarkTile != 0 (worldgen door)" % (name, c.tag))
            elif c.tag not in VANILLA_MUTATORS:
                fails.append("%s: names %s, neither ours nor a known vanilla mutator" % (name, c.tag))
        cb = d.find("comboLandmarkMutators")
        for c in (list(cb) if cb is not None else []):
            if c.tag not in VANILLA_LANDMARKS and ("LandmarkDef", c.tag) not in defs:
                fails.append("%s: combo names %s, no such landmark" % (name, c.tag))
        if (d.findtext("iconTexturePath") or "") not in VANILLA_ICONS:
            fails.append("%s: icon %s is not a vanilla landmark icon" % (name, d.findtext("iconTexturePath")))
        if (d.findtext("nameMaker") or "") not in VANILLA_NAMERS:
            fails.append("%s: namer %s is not a vanilla landmark namer" % (name, d.findtext("nameMaker")))
    targets = {}
    for op in icons_root.iter("Operation"):
        m = re.search(r'defName="([^"]+)"', op.findtext("xpath") or "")
        paths = {e.text.strip() for e in op.iter("iconTexturePath") if e.text}
        if m:
            targets[m.group(1)] = paths
    for t in sorted(targets):
        if t.startswith("VEE_"):
            fails.append("LandmarkIcons.xml still targets %s" % t)
    for stem in ASHKARR:
        paths = targets.get("RM_" + stem)
        expect = "World/Landmarks/Ashkarr/VEE_" + stem
        if paths != {expect}:
            fails.append("LandmarkIcons.xml: RM_%s icon is %s, expected %s" % (stem, sorted(paths or []), expect))
        elif not texture_exists(expect):
            fails.append("LandmarkIcons.xml: RM_%s texture %s.png is not in the mod" % (stem, expect))
    return fails


def vanilla_probe():
    """Checks the vanilla lists against the game's own defs when its Data folder is readable."""
    if not os.path.isdir(GAME_DATA):
        return None
    muts, lms, namers, icons = set(), set(), set(), set()
    for p in glob.glob(GAME_DATA + "/*/Defs/**/*.xml", recursive=True):
        try:
            r = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for d in r:
            n = d.findtext("defName")
            if d.tag == "TileMutatorDef" and n:
                muts.add(n)
            if d.tag == "LandmarkDef":
                if n:
                    lms.add(n)
                if d.findtext("iconTexturePath"):
                    icons.add(d.findtext("iconTexturePath"))
            if d.tag == "RulePackDef" and n:
                namers.add(n)
    return [("mutator", sorted(VANILLA_MUTATORS - muts)), ("landmark", sorted(VANILLA_LANDMARKS - lms)),
            ("namer", sorted(VANILLA_NAMERS - namers)), ("icon", sorted(VANILLA_ICONS - icons))]


def main():
    fails = []

    def ok(cond, msg):
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            fails.append(msg)

    stems, stated = plan_landmarks(open(PLAN, encoding="utf-8").read())
    ok(len(stems) == stated == 24, "plan §1b lists %d landmark defs and states %d (expected 24)" % (len(stems), stated))
    ports_root = ET.parse(PORTS).getroot()
    icons_root = ET.parse(ICONS).getroot()
    defs = src_defs()

    def tex(path):
        return os.path.isfile(os.path.join(ART, "Textures", path + ".png"))

    errs = check(stems, ports_root, defs, icons_root, tex)
    for e in errs:
        print("  " + e)
    ok(not errs, "%d landmark ports, their mutators, icons and namers, and the 18 Ash'karr icon targets (%d defects)"
       % (len([d for d in ports_root if d.tag == "LandmarkDef"]), len(errs)))

    probe = vanilla_probe()
    if probe is None:
        print("SKIP the vanilla lists are not re-read: the game's Data folder is not readable here")
    else:
        for kind, missing in probe:
            ok(not missing, "every vanilla %s the ports may name exists in the game's defs (missing: %s)" % (kind, missing))

    def planted(label, mutate_ports=None, mutate_icons=None, mutate_defs=None, tex_fn=tex, expect=""):
        p, i, d = copy.deepcopy(ports_root), copy.deepcopy(icons_root), dict(defs)
        if mutate_ports:
            mutate_ports(p)
        if mutate_icons:
            mutate_icons(i)
        if mutate_defs:
            mutate_defs(d)
        got = check(stems, p, d, i, tex_fn)
        ok(any(expect in g for g in got), "planted %s is caught" % label)

    def drop_port(p):
        p.remove(next(x for x in p if x.findtext("defName") == "RM_Cenotes"))

    def vee_req(p):
        x = next(x for x in p if x.findtext("defName") == "RM_DryRiver")
        x.find("mutatorChances").find("RM_DryRiver").tag = "VEE_DryRiver"

    def lost_required(p):
        x = next(x for x in p if x.findtext("defName") == "RM_DustBowl")
        mc = x.find("mutatorChances")
        mc.remove(mc.find("RM_DustStorms"))

    def unknown_mut(p):
        x = next(x for x in p if x.findtext("defName") == "RM_SaltPlains")
        ET.SubElement(x.find("mutatorChances"), "RM_NoSuchMutator").text = "0.1"

    def foreign_icon(p):
        next(x for x in p if x.findtext("defName") == "RM_RockRidge").find("iconTexturePath").text = "World/Landmarks/VEE_Ridge"

    def vee_target(i):
        for x in i.iter("xpath"):
            x.text = x.text.replace('defName="RM_FleshPits"', 'defName="VEE_FleshPits"')

    def no_reused(d):
        d.pop(("LandmarkDef", "RM_QuicksandPits"), None)

    planted("removed port", mutate_ports=drop_port, expect="no LandmarkDef RM_Cenotes")
    planted("VEE_ requirement", mutate_ports=vee_req, expect="RM_DryRiver: names a VEE_ def")
    planted("lost required mutator", mutate_ports=lost_required, expect="RM_DustBowl: requires")
    planted("unknown mutator", mutate_ports=unknown_mut, expect="RM_NoSuchMutator")
    planted("foreign icon", mutate_ports=foreign_icon, expect="not a vanilla landmark icon")
    planted("VEE_ patch target", mutate_icons=vee_target, expect="still targets VEE_FleshPits")
    planted("missing reused port", mutate_defs=no_reused, expect="reused port RM_QuicksandPits")
    planted("missing texture", tex_fn=lambda path: not path.endswith("VEE_Cenotes"), expect="RM_Cenotes texture")

    print("%s: %d failure(s)" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
