#!/usr/bin/env python3
"""SPIRE_DUNGEONS_MERGE_DARK_TOWER: the Spire is one building, and its entry is the Cathedral's trust.

Offline. Reads the shipped defs and source, runs the layout audit against the committed XML, compiles and
runs the real SpireEntryKernel.cs and SpireEntry.cs (against engine stand-ins) through the
StructureInjectionsRUT selftest, then plants one defect at a time in a copy and requires the checks to catch
it, source defects by compiling and running the copy. The one-site scan walks every tier's xml, not this mod's.

    python3 src/RimMandrake/Utils/selftest_spire_one_building.py [--static-only]
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MOD = os.path.join(REPO, "src", "RimUtinni", "StructureInjectionsRUT")
DEFS = os.path.join(MOD, "Defs")
SPIRE = os.path.join(DEFS, "Spire")
SOURCE = os.path.join(MOD, "Source")
LAYOUT = os.path.join(SPIRE, "StructureLayoutDefs_Spire.xml")
AUDIT = os.path.join(SOURCE, "Spire", "audit_spire_layout.py")
LANDMARKS = os.path.join(REPO, "src", "RimUtinni", "UtinniPatches", "Defs", "LandmarkDefs")
# Every tier's mods: a second dark tower in a sibling mod is a second dark tower on the world.
TREE_ROOTS = ("RimUtinni", "RimMandrake", "RimStarWars")
SPIRE_NAMED = re.compile("spire|tower|ashfall", re.I)
SELFTEST = os.path.join(SOURCE, "SelfTest", "StructureInjectionsRUT.SelfTest.csproj")
ATTITUDE = os.path.join(REPO, "src", "RimMandrake", "RustCathedral", "Source", "Hum", "RM_MapComponent_BiomeAttitude.cs")
DOTNET_CANDIDATES = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]
OLD_NAMES = ("RUT_DarkTower", "RUT_Ashfall_Spire", "RUT_GenStep_DarkTower", "RUT_Symbol_DarkTower")
NS = "RimMandrake.Utinni.StructureInjectionsRUT."
# The layout audit reads symbol names; this is what each of them must build.
SYMBOL_THINGS = {
    "RUT_Symbol_SpireHull": "RUT_SpireHullWall",
    "RUT_Symbol_SpireSeal": "RUT_SpireSeal",
    "RUT_Symbol_RakatanCommandCodes": "RUT_RakatanCommandCodes",
    "RUT_Symbol_SpireCommandConsole": "RUT_SpireCommandConsole",
    "RUT_Symbol_SpireControlConsole": "RUT_SpireControlConsole",
}

failures = []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok:
        failures.append(what)


def xml_files(root):
    for base, _, names in os.walk(root):
        for name in names:
            if name.endswith(".xml"):
                yield os.path.join(base, name)


def named(root, tag):
    return [e.findtext("defName") for f in xml_files(root) for e in ET.parse(f).getroot().iter(tag)]


def text(path):
    return open(path, encoding="utf-8").read()


def uncommented(path):
    return re.sub(r"<!--.*?-->", "", text(path), flags=re.S)


def code_only(path):
    """C# with its comments gone, so a line commented out does not read as a line that runs."""
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", text(path), flags=re.S)


def stage_reads_minus_one_off_cathedral(source):
    """The component is on every map, so the stand-in's -1 is only true while the real GetStage says so."""
    body = re.search(r"public static int GetStage\(Map map\)\s*\{(.*?)\n\t\t\}", source, re.S)
    return bool(body and "GetDef() == null ? -1 : comp.stage" in body.group(1))


def comp_classes(thing):
    return [li.get("Class") for li in thing.findall("comps/li")]


def def_pins(defs, landmarks):
    """What the compiled half cannot see: it reads no Defs, and its stand-ins replace the XML. A def here is read
    element by element, so a defect moved onto the wrong def, or into a comment, does not pass."""
    symbols = {}
    for f in xml_files(defs):
        for e in ET.parse(f).getroot().iter("KCSG.SymbolDef"):
            symbols.setdefault(e.findtext("defName"), []).append(e.findtext("thing"))
    check(len(symbols) >= 10, "probe: symbols parse (%d seen)" % len(symbols))
    for symbol, thing in SYMBOL_THINGS.items():
        check(symbols.get(symbol) == [thing], "%s builds %s, and only it: %s" % (symbol, thing, symbols.get(symbol)))

    things = {}
    for f in xml_files(os.path.join(defs, "Spire")):
        for e in ET.parse(f).getroot().iter("ThingDef"):
            things[e.findtext("defName")] = e
    check(set(SYMBOL_THINGS.values()) <= set(things), "every pinned thing is a real def under Defs/Spire")

    seal, hull = things.get("RUT_SpireSeal"), things.get("RUT_SpireHullWall")
    if seal is None or hull is None:
        check(False, "the seal and the hull are defined")
        return
    # CompTick runs only under Normal: any other ticker leaves the seal shut at every trust.
    check(seal.findtext("tickerType") == "Normal", "the seal ticks, so CompSpireSeal can open it: %s" % seal.findtext("tickerType"))
    check(seal.findtext("passability") == "Impassable", "the shut seal stops a pawn")
    check(seal.findtext("building/deconstructible") == "false", "the seal's own def refuses deconstruction")
    check(comp_classes(seal) == [NS + "CompProperties_SpireSeal"], "the seal's def carries the gate comp: %s" % comp_classes(seal))
    check(comp_classes(hull) == [NS + "CompProperties_SpireHull"], "the hull's def carries the absorbing comp: %s" % comp_classes(hull))
    # Odyssey's AncientFortifiedWall is the parent that makes the hull unbuildable and undeconstructible.
    check(hull.get("ParentName") == "AncientFortifiedWall", "the hull is a fortified wall: %s" % hull.get("ParentName"))

    # commonality defaults above zero, so an absent element is a rollable Spire too.
    weights = [e.findtext("commonality") for f in xml_files(landmarks) for e in ET.parse(f).getroot().iter("LandmarkDef")
               if e.findtext("defName") == "RUT_AshfallSpire"]
    check(weights == ["0"], "the generator can roll no Spire, commonality 0: %s" % weights)


def settings_pins(source):
    """The compiled half runs a stand-in Settings class with its own default; these read the file that ships."""
    real = code_only(os.path.join(source, "StructureInjectionsRUTSettings.cs"))
    check("public static bool spireEntryGated = true;" in real, "the real Settings field ships the gate on")
    scribes = re.findall(r"Scribe_Values\.Look\(ref spireEntryGated,[^;]*;", real)
    check(scribes == ['Scribe_Values.Look(ref spireEntryGated, "spireEntryGated", true);'],
          "a save with no value loads the gate on: %s" % scribes)
    reset = re.search(r"static void ResetAll\(\)\s*\{(.*?)\}", real, re.S)
    check(bool(reset) and "spireEntryGated = true;" in reset.group(1), "reset puts the gate back on")
    writes = []
    for base, dirs, names in os.walk(source):
        dirs[:] = [n for n in dirs if n not in ("SelfTest", "obj", "bin")]
        for name in names:
            if name.endswith(".cs"):
                writes += re.findall(r"\bspireEntryGated\s*=(?!=)\s*([^;]*);", code_only(os.path.join(base, name)))
    check(writes == ["true", "true"], "only the field and the reset assign the setting: %s" % writes)


def roof_pins(source):
    """The compiled half never runs this step, and without it a pod or a shell comes in past the seal."""
    roof = code_only(os.path.join(source, "Spire", "GenStep_SpireRoof.cs"))
    check("class GenStep_SpireRoof : GenStep" in roof, "the roof step is a GenStep")
    check('GetNamed("RUT_SpireHullWall")' in roof and "ThingsOfDef(hull)" in roof, "the roof step measures the hull")
    for line in ("minX = System.Math.Min(minX, c.x);", "minZ = System.Math.Min(minZ, c.z);",
                 "maxX = System.Math.Max(maxX, c.x);", "maxZ = System.Math.Max(maxZ, c.z);"):
        check(line in roof, "the rect reaches every wall: %s" % line)
    check(re.search(r"foreach \(IntVec3 c in CellRect\.FromLimits\(minX, minZ, maxX, maxZ\)\)\s*\{\s*"
                    r"map\.roofGrid\.SetRoof\(c, RoofDefOf\.RoofRockThick\);\s*\}", roof),
          "every cell of the hull rect takes thick rock roof")


def tree_scan(roots):
    """Every def of the three kinds in every xml under the roots, Defs and Patches alike, by element."""
    found = {"SitePartDef": [], "KCSG.StructureLayoutDef": [], "LandmarkDef": []}
    unread, stale, builders = [], [], []
    for root in roots:
        for path in xml_files(root):
            try:
                parsed = ET.parse(path).getroot()
            except ET.ParseError:
                unread.append(path)
                continue
            for tag, seen in found.items():
                seen += [(root, e.findtext("defName"), e.findtext("label")) for e in parsed.iter(tag)]
            body = uncommented(path)
            stale += [n for n in OLD_NAMES if n in body]
            if "<li>RUT_Spire_HighCommand</li>" in body:
                builders.append(os.path.basename(path))
    return found, unread, stale, builders


# The only files in the whole tree that may name the codes: the item def and the symbol that places it in the
# Spire's isolated room. Matched by full path, so a sibling file of the same name is still a giver.
CODES_HOMES = {os.path.join(SPIRE, "ThingDefs_Items", "RUT_RakatanCommandCodes.xml"),
               os.path.join(SPIRE, "SymbolDefs_Spire.xml")}


def codes_givers(roots):
    """Every xml (comments stripped) or C# (comments stripped) under the roots that names the codes, but the homes."""
    givers = []
    for root in roots:
        for base, _, names in os.walk(root):
            for name in names:
                path = os.path.join(base, name)
                if name.endswith(".xml"):
                    body = uncommented(path)
                elif name.endswith(".cs"):
                    body = code_only(path)
                else:
                    continue
                if "RUT_RakatanCommandCodes" in body and path not in CODES_HOMES:
                    givers.append(os.path.relpath(path, REPO) if path.startswith(REPO) else name)
    return givers


def tree_checks(extra=()):
    """A dark tower anywhere in the tree fails, under any of these names, in defName or label."""
    roots = [os.path.join(REPO, "src", r) for r in TREE_ROOTS]
    found, unread, stale, builders = tree_scan(roots + list(extra))
    check(not unread, "every xml in the tree parses, so none hides a site: %s" % unread)
    # Sanity probe: the walk must see all three tiers, or "one Spire" only means it looked in one place.
    check(all(any(seen[0] == r for seen in found["LandmarkDef"]) for r in roots),
          "probe: the scan sees landmarks in all three tiers (%d)" % len(found["LandmarkDef"]))
    check(len(found["SitePartDef"]) >= 10 and len({s[0] for s in found["SitePartDef"]}) >= 2,
          "probe: the scan sees site parts across tiers (%d)" % len(found["SitePartDef"]))
    want = {"SitePartDef": "RUT_SpireSite", "KCSG.StructureLayoutDef": "RUT_Spire_HighCommand", "LandmarkDef": "RUT_AshfallSpire"}
    for tag, name in want.items():
        hits = [s[1] for s in found[tag] if SPIRE_NAMED.search(s[1] or "") or SPIRE_NAMED.search(s[2] or "")]
        check(hits == [name], "in all of src, the one %s of the Spire is %s: %s" % (tag, name, hits))
    check(builders == ["SitePartDefs_Spire.xml"], "in all of src, one site builds the Spire's layout: %s" % builders)
    check(not stale, "in all of src, no xml carries an old dungeon name: %s" % sorted(set(stale)))
    check(all(os.path.isfile(h) and "RUT_RakatanCommandCodes" in uncommented(h) for h in CODES_HOMES),
          "probe: the giver scan's two homes exist and name the codes, so it can see the name")
    givers = codes_givers(roots + list(extra))
    check(not givers, "in all of src (xml and C#), nothing outside the Spire hands out the codes: %s" % givers)


def static_checks(defs=DEFS, source=SOURCE, landmarks=LANDMARKS):
    sites = named(defs, "SitePartDef")
    # Sanity probe: the parse must see the sibling dungeons' sites before it may report one Spire.
    check("RUT_WarLabSite" in sites and len(sites) >= 3, "probe: site parts parse (%d seen)" % len(sites))
    spire_sites = [s for s in sites if re.search("Spire|Tower|Ashfall", s or "")]
    check(spire_sites == ["RUT_SpireSite"], "one Spire site, no second dark-tower site: %s" % spire_sites)
    layouts = [n for n in named(defs, "KCSG.StructureLayoutDef") if re.search("Spire|Tower|Ashfall", n or "")]
    check(layouts == ["RUT_Spire_HighCommand"], "one Spire layout: %s" % layouts)
    marks = [n for n in named(landmarks, "LandmarkDef") if re.search("Spire|Tower", n or "")]
    check(marks == ["RUT_AshfallSpire"], "one Spire landmark: %s" % marks)

    blob = "\n".join(text(f) for f in xml_files(defs))
    left = [n for n in OLD_NAMES if n in blob]
    check(not left, "no dungeon def carries an old name: %s" % left)

    site_xml = text(os.path.join(defs, "Spire", "SitePartDefs_Spire.xml"))
    check("<li>RUT_Spire_HighCommand</li>" in site_xml, "the site builds the one layout")
    check(re.search(r"<linkWithSite>RUT_SpireSite</linkWithSite>\s*<order>401</order>\s*"
                    r'<genStep Class="RimMandrake\.Utinni\.StructureInjectionsRUT\.GenStep_SpireRoof"', site_xml),
          "the roof step runs after the structure step on the same site")
    check("<gravShipsCanLandOn>false</gravShipsCanLandOn>" in site_xml, "no gravship lands on the Spire")

    seal_xml = text(os.path.join(defs, "Spire", "ThingDefs_Buildings", "RUT_SpireSeal.xml"))
    check('Class="RimMandrake.Utinni.StructureInjectionsRUT.CompProperties_SpireHull"' in seal_xml, "the hull absorbs damage")
    check('Class="RimMandrake.Utinni.StructureInjectionsRUT.CompProperties_SpireSeal"' in seal_xml, "the seal is the trust gate")
    check("<deconstructible>false</deconstructible>" in seal_xml, "the seal cannot be deconstructed")
    def_pins(defs, landmarks)
    settings_pins(source)
    roof_pins(source)

    entry = text(os.path.join(source, "Spire", "SpireEntry.cs"))
    kernel = text(os.path.join(source, "Spire", "SpireEntryKernel.cs"))
    check(re.search(r"PostPreApplyDamage\(ref DamageInfo dinfo, out bool absorbed\)\s*\{\s*absorbed = true;", entry),
          "the comps absorb every hit")
    check("SpireEntry.SealOpens" in entry and "SpireEntryKernel.SealOpens(StructureInjectionsRUTSettings.spireEntryGated" in entry,
          "the seal reads the trust rule and its Mod Setting")
    check("parent.IsHashIntervalTick(60) && SpireEntry.SealOpens)" in entry, "the seal opens on the rule, not against it")
    check("VouchedStage = 2" in kernel, "trust is VOUCHED, stage 2 of the arc")
    check("RimMandrake.RustCathedral.Hum.RM_MapComponent_BiomeAttitude" in entry, "the stage is read from the Cathedral's one attitude system")
    attitude = text(ATTITUDE)
    check("namespace RimMandrake.RustCathedral.Hum" in attitude, "the type name the reflection reads is the real one")
    check(stage_reads_minus_one_off_cathedral(attitude), "the real GetStage answers -1 off Cathedral ground")
    check(not stage_reads_minus_one_off_cathedral(attitude.replace("GetDef() == null ? -1 : comp.stage", "stage ?? -1")),
          "the GetStage pin catches the old read")
    csproj = text(os.path.join(source, "RimMandrake.Utinni.StructureInjectionsRUT.csproj"))
    for name in ("Spire\\SpireEntryKernel.cs", "Spire\\SpireEntry.cs", "Spire\\GenStep_SpireRoof.cs", "StructureInjectionsRUTSettings.cs"):
        check(name in csproj, "the mod compiles %s" % name)

    codes = ET.parse(os.path.join(defs, "Spire", "ThingDefs_Items", "RUT_RakatanCommandCodes.xml")).getroot()
    check(codes.find("ThingDef/tradeability").text == "None", "the codes cannot be bought or sold")
    givers = [f for f in xml_files(defs) if "RUT_RakatanCommandCodes" in uncommented(f)
              and os.path.basename(f) not in ("RUT_RakatanCommandCodes.xml", "SymbolDefs_Spire.xml")]
    check(not givers, "nothing else in the mod hands out the codes: %s" % givers)


def audit(path):
    return subprocess.run([sys.executable, AUDIT, path], capture_output=True, text=True)


def layout_checks():
    r = audit(LAYOUT)
    check(r.returncode == 0, "layout audit passes on the shipped XML")
    if r.returncode:
        print(r.stdout[-1500:])
    rows = text(LAYOUT)
    plants = [
        ("a gap in the hull", lambda s: s.replace("RUT_Symbol_SpireHull", ".", 1)),
        ("a plain wall where the seal stands", lambda s: s.replace("RUT_Symbol_SpireSeal", "RUT_Symbol_SpireHull", 1)),
        ("a hull cell of ordinary plasteel", lambda s: s.replace("RUT_Symbol_SpireHull", "Wall_Plasteel", 1)),
        ("codes on the command deck", lambda s: s.replace("RUT_Symbol_RakatanCommandCodes", ".", 1)
         .replace("Turret_MiniTurret", "RUT_Symbol_RakatanCommandCodes", 1)),
        ("a second set of codes", lambda s: s.replace("RUT_Symbol_SpireControlConsole", "RUT_Symbol_RakatanCommandCodes", 1)),
        ("the lake back in the terrain", lambda s: s.replace("<li>Gravel,", "<li>RM_ScaldWaterDeep,", 1)),
        ("a mech in the Helix's ward", lambda s: s.replace("RUT_Symbol_HelixGrunt", "RUT_Symbol_MechLancer", 1)),
    ]
    with tempfile.TemporaryDirectory() as d:
        for name, plant in plants:
            bad = plant(rows)
            check(bad != rows, "plant applies: %s" % name)
            path = os.path.join(d, "layout.xml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(bad)
            check(audit(path).returncode != 0, "audit catches: %s" % name)


SETTINGS = "Source/StructureInjectionsRUTSettings.cs"
ROOF = "Source/Spire/GenStep_SpireRoof.cs"
SEAL_DEF = "Defs/Spire/ThingDefs_Buildings/RUT_SpireSeal.xml"
SYMBOL_DEFS = "Defs/Spire/SymbolDefs_Spire.xml"
LANDMARK_DEF = "RUT_AshfallSpire.xml"


def plant_static():
    """Each planted tree must turn static_checks red; the list is restored around each one."""
    plants = [
        ("a second tower site", "Defs/Spire/SitePartDefs_Spire.xml", "<SitePartDef>\n    <defName>RUT_SpireSite",
         "<SitePartDef><defName>RUT_DarkTowerSite</defName></SitePartDef>\n  <SitePartDef>\n    <defName>RUT_SpireSite"),
        ("the roof step dropped", "Defs/Spire/SitePartDefs_Spire.xml", "<order>401</order>", "<order>399</order>"),
        ("the seal open to anyone", "Source/Spire/SpireEntryKernel.cs", "VouchedStage = 2", "VouchedStage = 0"),
        ("the gate inverted", "Source/Spire/SpireEntry.cs", "&& SpireEntry.SealOpens", "&& !SpireEntry.SealOpens"),
        ("the hull takes damage", "Source/Spire/SpireEntry.cs", "absorbed = true;", "absorbed = false;"),
        ("the codes for sale", "Defs/Spire/ThingDefs_Items/RUT_RakatanCommandCodes.xml",
         "<tradeability>None</tradeability>", "<tradeability>All</tradeability>"),
        ("the seal never ticks", SEAL_DEF, "<tickerType>Normal</tickerType>", ""),
        ("the seal ticks only rarely", SEAL_DEF, "<tickerType>Normal</tickerType>", "<tickerType>Rare</tickerType>"),
        ("the seal walks through", SEAL_DEF, "<passability>Impassable</passability>", "<passability>Standable</passability>"),
        ("the gate comp dropped", SEAL_DEF, '<li Class="RimMandrake.Utinni.StructureInjectionsRUT.CompProperties_SpireSeal" />', ""),
        ("the hull comp dropped", SEAL_DEF, '<li Class="RimMandrake.Utinni.StructureInjectionsRUT.CompProperties_SpireHull" />', ""),
        ("the hull a plain wall by parent", SEAL_DEF, 'ParentName="AncientFortifiedWall"', 'ParentName="Wall"'),
        ("no gate built", SYMBOL_DEFS, "<thing>RUT_SpireSeal</thing>", "<thing>RUT_SpireHullWall</thing>"),
        ("the hull builds a breakable wall", SYMBOL_DEFS, "<thing>RUT_SpireHullWall</thing>", "<thing>Wall</thing>"),
        ("no codes inside", SYMBOL_DEFS, "<thing>RUT_RakatanCommandCodes</thing>", "<thing>Steel</thing>"),
        ("the command console builds nothing of ours", SYMBOL_DEFS, "<thing>RUT_SpireCommandConsole</thing>", "<thing>Steel</thing>"),
        ("the generator may scatter Spires", LANDMARK_DEF, "<commonality>0</commonality>", "<commonality>1</commonality>"),
        ("commonality left to its default", LANDMARK_DEF, "<commonality>0</commonality>", ""),
        ("the gate ships off in the real field", SETTINGS, "public static bool spireEntryGated = true;", "public static bool spireEntryGated = false;"),
        ("a save loads the gate off", SETTINGS, '"spireEntryGated", true);', '"spireEntryGated", false);'),
        ("the Scribe line gone", SETTINGS, 'Scribe_Values.Look(ref spireEntryGated, "spireEntryGated", true);', ""),
        ("the Scribe line commented out", SETTINGS, 'Scribe_Values.Look(ref spireEntryGated', '// Scribe_Values.Look(ref spireEntryGated'),
        ("reset turns the gate off", SETTINGS, "            spireEntryGated = true;", "            spireEntryGated = false;"),
        ("some other code turns the gate off", "Source/Spire/SpireEntry.cs", "public static bool SealOpens =>",
         "static bool off = StructureInjectionsRUTSettings.spireEntryGated = false;\n        public static bool SealOpens =>"),
        ("the roof line deleted", ROOF, "map.roofGrid.SetRoof(c, RoofDefOf.RoofRockThick);", ""),
        ("the roof line commented out", ROOF, "map.roofGrid.SetRoof(c,", "// map.roofGrid.SetRoof(c,"),
        ("a thin roof a pod goes through", ROOF, "RoofDefOf.RoofRockThick", "RoofDefOf.RoofConstructed"),
        ("the roof short of the far wall", ROOF, "maxZ = System.Math.Max(maxZ, c.z);", ""),
        ("the roof over some other rect", ROOF, "CellRect.FromLimits(minX, minZ, maxX, maxZ)", "CellRect.FromLimits(minX, minZ, maxX, minZ)"),
        ("the roof measures the wrong thing", ROOF, 'GetNamed("RUT_SpireHullWall")', 'GetNamed("RUT_SpireSeal")'),
    ]
    with tempfile.TemporaryDirectory() as d:
        copy = os.path.join(d, "mod")
        shutil.copytree(MOD, copy, ignore=shutil.ignore_patterns("Textures", "Assemblies", "obj", "bin"))
        marks = os.path.join(d, "landmarks")
        shutil.copytree(LANDMARKS, marks)

        def run_on_copy():
            saved, failures[:] = failures[:], []
            stdout, sys.stdout = sys.stdout, open(os.devnull, "w")
            try:
                static_checks(os.path.join(copy, "Defs"), os.path.join(copy, "Source"), marks)
            finally:
                sys.stdout.close()
                sys.stdout = stdout
            red, failures[:] = list(failures), saved
            return red

        # A copy that is red unplanted would make every catch below free.
        red = run_on_copy()
        check(not red, "control: the unplanted copy is green: %s" % red)
        for name, rel, old, new in plants:
            path = os.path.join(marks, rel) if rel == LANDMARK_DEF else os.path.join(copy, rel)
            good = text(path)
            check(old in good, "plant applies: %s" % name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(good.replace(old, new))
            check(run_on_copy(), "static checks catch: %s" % name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(good)


SITE_DEF = "<Defs><SitePartDef><defName>%s</defName>%s</SitePartDef></Defs>"
TREE_PLANTS = [
    ("a dark-tower site in a sibling Utinni mod", "RimUtinni/UtinniPatches/Defs/Spare_Mutant.xml", SITE_DEF % ("RUT_DarkTowerSite", "")),
    ("a tower site in a Mandrake mod", "RimMandrake/Atlas/Defs/Spare_Mutant.xml", SITE_DEF % ("RM_ScaldTowerSite", "")),
    ("a tower site in a Star Wars mod", "RimStarWars/Spare/Defs/Spare_Mutant.xml", SITE_DEF % ("RSW_TowerSite", "")),
    ("a tower site named only in its label", "RimMandrake/Atlas/Defs/Spare_Mutant.xml", SITE_DEF % ("RM_ScaldKeep", "<label>the dark tower</label>")),
    ("a tower site added by a patch", "RimUtinni/UtinniPatches/Patches/Spare_Mutant.xml",
     '<Patch><Operation Class="PatchOperationAdd"><xpath>Defs</xpath><value><SitePartDef><defName>RUT_DarkTowerSite</defName>'
     "</SitePartDef></value></Operation></Patch>"),
    ("a quiet site that builds the Spire's layout", "RimMandrake/Atlas/Defs/Spare_Mutant.xml",
     SITE_DEF % ("RM_QuietSite", "<li>RUT_Spire_HighCommand</li>")),
    ("a second tower layout in a sibling mod", "RimUtinni/UtinniPatches/Defs/Spare_Mutant.xml",
     "<Defs><KCSG.StructureLayoutDef><defName>RUT_ScaldTower_Keep</defName></KCSG.StructureLayoutDef></Defs>"),
    ("a second tower landmark in a sibling mod", "RimMandrake/Atlas/Defs/Spare_Mutant.xml",
     "<Defs><LandmarkDef><defName>RM_DarkTower</defName></LandmarkDef></Defs>"),
    ("an old dungeon name in a sibling mod", "RimUtinni/UtinniPatches/Defs/Spare_Mutant.xml",
     "<Defs><ThingDef><defName>RUT_DarkTowerGate</defName></ThingDef></Defs>"),
    ("a sibling mod's ThingSetMaker that hands out the codes", "RimUtinni/UtinniPatches/Defs/Spare_Mutant.xml",
     "<Defs><ThingSetMakerDef><defName>RUT_SpareLoot</defName><root Class=\"ThingSetMaker_StackCount\"><fixedParams>"
     "<filter><thingDefs><li>RUT_RakatanCommandCodes</li></thingDefs></filter></fixedParams></root></ThingSetMakerDef></Defs>"),
    ("a trader stock patched to sell the codes", "RimMandrake/Atlas/Patches/Spare_Mutant.xml",
     '<Patch><Operation Class="PatchOperationAdd"><xpath>Defs/TraderKindDef/stockGenerators</xpath><value>'
     '<li Class="StockGenerator_SingleDef"><thingDef>RUT_RakatanCommandCodes</thingDef></li></value></Operation></Patch>'),
    ("a sibling file wearing the item def's name", "RimStarWars/Spare/Defs/RUT_RakatanCommandCodes.xml",
     "<Defs><ThingSetMakerDef><defName>RSW_Loot</defName><root><fixedParams><filter><thingDefs>"
     "<li>RUT_RakatanCommandCodes</li></thingDefs></filter></fixedParams></root></ThingSetMakerDef></Defs>"),
    ("C# in a sibling mod that spawns the codes", "RimMandrake/Atlas/Source/Spare_Mutant.cs",
     'class Spare { void Give() { GenSpawn.Spawn(ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RUT_RakatanCommandCodes")), c, m); } }'),
    ("a file the scan cannot read", "RimUtinni/UtinniPatches/Defs/Spare_Mutant.xml", "<Defs><SitePartDef>"),
]


def plant_tree():
    """Each sibling file, scanned as one more mod beside the real tree, must turn tree_checks red."""
    with tempfile.TemporaryDirectory() as d:
        def run_with_plant():
            saved, failures[:] = failures[:], []
            stdout, sys.stdout = sys.stdout, open(os.devnull, "w")
            try:
                tree_checks([d])
            finally:
                sys.stdout.close()
                sys.stdout = stdout
            red, failures[:] = list(failures), saved
            return red

        red = run_with_plant()
        check(not red, "control: the scan with an empty sibling is green: %s" % red)
        for name, rel, body in TREE_PLANTS:
            path = os.path.join(d, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(body)
            check(run_with_plant(), "tree scan catches: %s" % name)
            os.remove(path)


EXPECTED_SPIRE_LINES = 20
COMPILED_PLANTS = [
    ("the gate inverted", "Spire/SpireEntry.cs", "&& SpireEntry.SealOpens", "&& !SpireEntry.SealOpens"),
    ("the seal ignores the stage", "Spire/SpireEntry.cs", "SpireEntryKernel.SealOpens(StructureInjectionsRUTSettings.spireEntryGated, CathedralStage)",
     "!StructureInjectionsRUTSettings.spireEntryGated"),
    ("the poll throws its answer away", "Spire/SpireEntry.cs", "cathedralStage = SpireEntryKernel.Fold(", "SpireEntryKernel.Fold("),
    ("the attitude component never matched", "Spire/SpireEntry.cs", "comp.GetType().FullName != AttitudeType", "comp.GetType().FullName == AttitudeType"),
    ("the source map not saved", "Spire/SpireEntry.cs", 'Scribe_Values.Look(ref sourceMap, "rutSpireCathedralSourceMap", -1);', ""),
    ("any map may lower the reading", "Spire/SpireEntryKernel.cs", "if (best < 0 || !(sourceSeen || best > recorded))", "if (best < 0)"),
    ("a dark flip ignored", "Spire/SpireEntryKernel.cs", "if (best < 0 || !(sourceSeen || best > recorded))", "if (best <= recorded)"),
]


def find_dotnet():
    dotnet = next((c for c in DOTNET_CANDIDATES if os.path.isfile(c)), None)
    if dotnet is None:
        check(False, "UNMEASURED: no dotnet.exe at %s" % DOTNET_CANDIDATES)
    return dotnet


def run_project(dotnet, project):
    # WSL interop can drop the launch of a Windows exe (seen 2026-11-02): winbuild retries that, and only that.
    sys.path.insert(0, HERE)
    import winbuild
    return winbuild.run_interop_captured([dotnet, "run", "--project", project, "-c", "Release"],
                                         capture_output=True, text=True)


def kernel_run():
    dotnet = find_dotnet()
    if dotnet is None:
        return
    sys.path.insert(0, HERE)
    from selftest_winstage import windows_project_path
    out = run_project(dotnet, windows_project_path(SELFTEST, whole_src=False))
    spire = [ln.strip() for ln in out.stdout.splitlines() if "spire:" in ln]
    check(out.returncode == 0 and len(spire) == EXPECTED_SPIRE_LINES,
          "compiled chain passes (%d spire lines, exit %d)" % (len(spire), out.returncode))
    for line in spire:
        print("      " + line)
    if out.returncode:
        print(out.stdout[-800:], out.stderr[-800:])


def compiled_plants():
    """Plant each source defect in a copy of the selftest's sources and require the compiled run to go red.
    A copy that does not compile proves nothing, so a build failure is a FAIL, not a catch."""
    dotnet = find_dotnet()
    if dotnet is None:
        return
    sys.path.insert(0, HERE)
    import winbuild
    from selftest_winstage import stage_name_for, windows_project_path
    stage = os.path.join(winbuild.BUILD_ROOT, stage_name_for("spire_plants", REPO))
    shutil.rmtree(stage, ignore_errors=True)
    for sub in ("Spire", "SelfTest", "VaultDungeons"):
        shutil.copytree(os.path.join(SOURCE, sub), os.path.join(stage, sub), ignore=shutil.ignore_patterns("obj", "bin"))
    project = windows_project_path(os.path.join(stage, "SelfTest", os.path.basename(SELFTEST)))
    try:
        for name, rel, old, new in COMPILED_PLANTS:
            path = os.path.join(stage, rel)
            good = text(path)
            check(old in good, "plant applies: %s" % name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(good.replace(old, new))
            out = run_project(dotnet, project)
            built = "checks passed" in out.stdout
            check(built, "plant still compiles: %s" % name)
            if not built:
                print(out.stdout[-600:])
            check(built and out.returncode != 0, "compiled run catches: %s" % name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(good)
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main():
    static_checks()
    tree_checks()
    layout_checks()
    plant_static()
    plant_tree()
    if "--static-only" not in sys.argv:
        kernel_run()
        compiled_plants()
    print("FAIL %d" % len(failures) if failures else "OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
