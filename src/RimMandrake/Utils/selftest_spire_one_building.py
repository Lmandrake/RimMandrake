#!/usr/bin/env python3
"""SPIRE_DUNGEONS_MERGE_DARK_TOWER: the Spire is one building, and its entry is the Cathedral's trust.

Offline. Reads the shipped defs and source, runs the layout audit against the committed XML, compiles and
runs the real SpireEntryKernel.cs and SpireEntry.cs (against engine stand-ins) through the
StructureInjectionsRUT selftest, then plants one defect at a time in a copy and requires the checks to catch
it, source defects by compiling and running the copy.

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
SELFTEST = os.path.join(SOURCE, "SelfTest", "StructureInjectionsRUT.SelfTest.csproj")
ATTITUDE = os.path.join(REPO, "src", "RimMandrake", "RustCathedral", "Source", "Hum", "RM_MapComponent_BiomeAttitude.cs")
DOTNET_CANDIDATES = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]
OLD_NAMES = ("RUT_DarkTower", "RUT_Ashfall_Spire", "RUT_GenStep_DarkTower", "RUT_Symbol_DarkTower")

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


def stage_reads_minus_one_off_cathedral(source):
    """The component is on every map, so the stand-in's -1 is only true while the real GetStage says so."""
    body = re.search(r"public static int GetStage\(Map map\)\s*\{(.*?)\n\t\t\}", source, re.S)
    return bool(body and "GetDef() == null ? -1 : comp.stage" in body.group(1))


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
    for name in ("Spire\\SpireEntryKernel.cs", "Spire\\SpireEntry.cs", "Spire\\GenStep_SpireRoof.cs"):
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
        ("the lake back in the terrain", lambda s: s.replace("<li>Gravel,", "<li>RUT_ScaldWaterDeep,", 1)),
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
    ]
    global failures
    with tempfile.TemporaryDirectory() as d:
        copy = os.path.join(d, "mod")
        shutil.copytree(MOD, copy, ignore=shutil.ignore_patterns("Textures", "Assemblies", "obj", "bin"))
        for name, rel, old, new in plants:
            path = os.path.join(copy, rel)
            good = text(path)
            check(old in good, "plant applies: %s" % name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(good.replace(old, new))
            saved, failures = failures, []
            stdout, sys.stdout = sys.stdout, open(os.devnull, "w")
            try:
                static_checks(os.path.join(copy, "Defs"), os.path.join(copy, "Source"))
            finally:
                sys.stdout.close()
                sys.stdout = stdout
            caught, failures = bool(failures), saved
            check(caught, "static checks catch: %s" % name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(good)


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
    return subprocess.run([dotnet, "run", "--project", project, "-c", "Release"], capture_output=True, text=True)


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
    layout_checks()
    plant_static()
    if "--static-only" not in sys.argv:
        kernel_run()
        compiled_plants()
    print("FAIL %d" % len(failures) if failures else "OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
