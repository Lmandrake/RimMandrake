#!/usr/bin/env python3
"""Offline static selftest for River Works (SURFACE_RIVER_WEIRS_1). No game, no bridge.

Checks what goes silently wrong in this repo:
  * the csproj has EnableDefaultCompileItems=false, so a .cs missing a <Compile> line builds into nothing;
  * every Mod Settings bool must be in validation.py's suite.toggles (CLAUDE.md "superb Mod Settings");
  * About.xml carries the tier packageId;
  * every Defs/Patches XML parses, and RM_FordStones needs the RM_Fordable affordance the patch adds.
Sanity probe: the settings regex must find a field we know exists (surfaceCurrentEnabled).
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAILS.append(name)


def main():
    src = os.path.join(HERE, "Source")
    csproj = open(os.path.join(src, "RimMandrake_RiverWorks.csproj"), encoding="utf-8").read()
    listed = set(re.findall(r'<Compile Include="([^"]+)"', csproj))
    on_disk = {os.path.basename(p) for p in glob.glob(os.path.join(src, "*.cs"))}
    check("csproj compiles every .cs", on_disk <= listed, sorted(on_disk - listed))
    check("csproj lists no missing .cs", listed <= on_disk, sorted(listed - on_disk))

    settings = open(os.path.join(src, "RM_RiverWorksMod.cs"), encoding="utf-8").read()
    bools = set(re.findall(r"public static bool (\w+)\s*=(?!>)", settings))
    check("sanity: settings regex sees surfaceCurrentEnabled", "surfaceCurrentEnabled" in bools, sorted(bools))
    for b in sorted(bools):
        check("setting %s is scribed" % b, ('"%s"' % b) in settings)
    val = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    m = re.search(r"suite\.toggles\s*=\s*\[(.*?)\]", val, re.S)
    toggles = set(re.findall(r'"(\w+)"', m.group(1))) if m else set()
    check("suite.toggles == every settings bool", toggles == bools,
          "missing %s / extra %s" % (sorted(bools - toggles), sorted(toggles - bools)))

    about = ET.parse(os.path.join(HERE, "About", "About.xml")).getroot()
    check("packageId mandrake.rm.riverworks", about.findtext("packageId") == "mandrake.rm.riverworks")

    xmls = glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True) + \
        glob.glob(os.path.join(HERE, "Patches", "**", "*.xml"), recursive=True)
    check("sanity: found def/patch XML", len(xmls) >= 2, xmls)
    defs_text = ""
    for p in xmls:
        try:
            ET.parse(p)
            ok = True
        except ET.ParseError as ex:
            ok = False
            print("   ", ex)
        check("parses %s" % os.path.relpath(p, HERE), ok)
        defs_text += open(p, encoding="utf-8").read()
    check("RM_FordStones needs RM_Fordable", "<terrainAffordanceNeeded>RM_Fordable</terrainAffordanceNeeded>" in defs_text)
    check("RM_Fordable is defined and patched onto WaterMovingShallow",
          "<defName>RM_Fordable</defName>" in defs_text and 'defName="WaterMovingShallow"' in defs_text)

    # Slice 2: the works moved here from TerminalBiomes. A def defined in both mods is a clash.
    for dn in ("RM_BankStake", "RM_BankWeir", "RM_SiltTrap", "RM_FerryPost"):
        check("defines %s" % dn, "<defName>%s</defName>" % dn in defs_text)
    check("weir carries RM_PlaceWorker_RiverWeir", "RimMandrake.RiverWorks.RM_PlaceWorker_RiverWeir" in defs_text)
    check("silt-trap carries a swap table", "RimMandrake.RiverWorks.RM_SiltSwapExtension" in defs_text)
    check("drift defs exist (owner: biome-relevant drift)", defs_text.count("<RimMandrake.RiverWorks.RM_RiverDriftDef>") >= 3)
    check("no generic wood in drift (owner card 2)", "<thing>WoodLog</thing>" not in defs_text)
    tb = os.path.join(os.path.dirname(HERE), "TerminalBiomes")
    tb_text = ""
    for p in glob.glob(os.path.join(tb, "Defs", "**", "*.xml"), recursive=True):
        tb_text += open(p, encoding="utf-8").read()
    check("sanity: read TerminalBiomes defs", "RM_BankSilt" in tb_text)
    for dn in ("RM_BankStake", "RM_BankWeir", "RM_SiltTrap", "RM_FerryPost"):
        check("TerminalBiomes does not also define %s" % dn, "<defName>%s</defName>" % dn not in tb_text)
    tb_about = open(os.path.join(tb, "About", "About.xml"), encoding="utf-8").read()
    check("TerminalBiomes depends on River Works", "<packageId>mandrake.rm.riverworks</packageId>" in tb_about)
    tb_src = " ".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(tb, "Source", "*.cs")))
    for cls in ("class RM_Building_BankWeir", "class RM_Building_SiltTrap", "class CompChannelArrester"):
        check("TerminalBiomes no longer declares %s" % cls, cls not in tb_src)

    print("\n%s" % ("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s): %s" % (len(FAILS), FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
