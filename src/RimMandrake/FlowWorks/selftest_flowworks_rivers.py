#!/usr/bin/env python3
"""Offline static selftest for FlowWorks Rivers (River Works, SURFACE_RIVER_WEIRS_1; merged into FlowWorks
2026-10-05). No game, no bridge.

Checks what goes silently wrong in this repo:
  * the csproj has EnableDefaultCompileItems=false, so a .cs missing a <Compile> line builds into nothing;
  * every Rivers settings bool must be in northstar/extensions_rivers.py's suite.toggles, every field is
    scribed, the scribe keys are unique across FlowWorks' one settings file, and FlowWorks' settings
    class actually calls RM_RiversSettings.ExposeData and draws the section;
  * no RiverWorks mod folder or packageId survives the merge;
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
    csproj = open(os.path.join(src, "RimMandrake_FlowWorks.csproj"), encoding="utf-8").read()
    listed = {p.replace("\\", "/") for p in re.findall(r'<Compile Include="([^"]+)"', csproj)}
    listed_riv = {p for p in listed if p.startswith("Rivers/")}
    on_disk = {"Rivers/" + os.path.basename(p) for p in glob.glob(os.path.join(src, "Rivers", "*.cs"))}
    check("sanity: Rivers/ holds .cs files", len(on_disk) >= 10, sorted(on_disk))
    check("csproj compiles every Rivers .cs", on_disk <= listed_riv, sorted(on_disk - listed_riv))
    check("csproj lists no missing Rivers .cs", listed_riv <= on_disk, sorted(listed_riv - on_disk))

    settings = open(os.path.join(src, "Rivers", "RM_RiversSettings.cs"), encoding="utf-8").read()
    fw = open(os.path.join(src, "RimMandrakeFlowWorksMod.cs"), encoding="utf-8").read()
    key = re.compile(r'Scribe_Values\.Look\(ref \w+, "(\w+)"')
    k_fw, k_riv = key.findall(fw), key.findall(settings)
    check("sanity: scribe-key regex sees swaleEnabled", "swaleEnabled" in k_fw)
    check("Rivers scribe keys unique within FlowWorks' settings file",
          not (set(k_fw) & set(k_riv)) and len(k_riv) == len(set(k_riv)), sorted(set(k_fw) & set(k_riv)))
    check("FlowWorks settings scribe the Rivers section", "RM_RiversSettings.ExposeData()" in fw)
    check("FlowWorks settings window draws the Rivers section", "RM_RiversSettingsWindow.DoSettingsSection" in fw)
    bools = set(re.findall(r"public static bool (\w+)\s*=(?!>)", settings))
    check("sanity: settings regex sees surfaceCurrentEnabled", "surfaceCurrentEnabled" in bools, sorted(bools))
    for b in sorted(bools):
        check("setting %s is scribed" % b, ('"%s"' % b) in settings)
    # FLOWWORKS_QUARRY_DIGGING_1: the sluice/panning section's bools are claimed by the same suite
    quarry = open(os.path.join(src, "Quarry", "RM_QuarrySettings.cs"), encoding="utf-8").read()
    qbools = set(re.findall(r"public static bool (\w+)\s*=(?!>)", quarry))
    check("sanity: quarry settings regex sees sluiceBoxEnabled", "sluiceBoxEnabled" in qbools, sorted(qbools))
    for b in sorted(qbools):
        check("quarry setting %s is scribed" % b, ('"%s"' % b) in quarry)
    check("quarry scribe keys unique within FlowWorks' settings file",
          not (set(key.findall(quarry)) & (set(k_fw) | set(k_riv))), sorted(set(key.findall(quarry)) & (set(k_fw) | set(k_riv))))
    bools |= qbools
    val = open(os.path.join(HERE, "northstar", "extensions_rivers.py"), encoding="utf-8").read()
    m = re.search(r"suite\.toggles\s*=\s*\[(.*?)\]", val, re.S)
    toggles = set(re.findall(r'"(\w+)"', m.group(1))) if m else set()
    check("suite.toggles == every settings bool", toggles == bools,
          "missing %s / extra %s" % (sorted(bools - toggles), sorted(toggles - bools)))

    about = ET.parse(os.path.join(HERE, "About", "About.xml")).getroot()
    check("packageId mandrake.rm.flowworks", about.findtext("packageId") == "mandrake.rm.flowworks")
    check("the RiverWorks mod folder is gone (merged)",
          not os.path.exists(os.path.join(os.path.dirname(HERE), "RiverWorks", "About", "About.xml")))

    xmls = glob.glob(os.path.join(HERE, "Defs", "Rivers", "*.xml")) + \
        glob.glob(os.path.join(HERE, "Patches", "Rivers", "*.xml"))
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
    check("weir carries RM_PlaceWorker_RiverWeir", "RimMandrake.FlowWorks.Rivers.RM_PlaceWorker_RiverWeir" in defs_text)
    check("silt-trap carries a swap table", "RimMandrake.FlowWorks.Rivers.RM_SiltSwapExtension" in defs_text)
    check("drift defs exist (owner: biome-relevant drift)", defs_text.count("<RimMandrake.FlowWorks.Rivers.RM_RiverDriftDef>") >= 3)
    check("no generic wood in drift (owner card 2)", "<thing>WoodLog</thing>" not in defs_text)
    # Owner card 2026-10-23 07:19 "Yes, occasional flotsam": every vanilla drift group also carries dead fish of ITS
    # biomes' freshwater fish (Odyssey BiomeDef fishTypes freshwater_*, read 2026-10-23) and rare lost cargo.
    fresh = {"TemperateForest": {"Fish_Salmon", "Fish_Bass", "Fish_Catfish"}, "Grasslands": {"Fish_Bass", "Fish_Catfish"},
             "TemperateSwamp": {"Fish_Bass", "Fish_Catfish"}, "ColdBog": {"Fish_Salmon", "Fish_Frostfish"},
             "BorealForest": {"Fish_Salmon", "Fish_Frostfish"}, "Tundra": {"Fish_Salmon", "Fish_Frostfish"},
             "GlacialPlain": {"Fish_Salmon", "Fish_Frostfish"}, "AridShrubland": {"Fish_Tilapia", "Fish_Catfish"},
             "Desert": {"Fish_Guppy", "Fish_Tilapia"}, "ExtremeDesert": {"Fish_Guppy", "Fish_Tilapia"},
             "TropicalRainforest": {"Fish_Tilapia", "Fish_Piranha"},
             "TropicalSwamp": {"Fish_Tilapia", "Fish_Catfish", "Fish_Piranha"}}
    cargo = {"Beer", "Cloth", "MedicineHerbal", "Pemmican", "SmokeleafLeaves", "PsychoidLeaves"}
    pools = {}
    for p in glob.glob(os.path.join(HERE, "Defs", "Rivers", "RM_RiverDrift*.xml")):
        for d in ET.parse(p).getroot().iter("RimMandrake.FlowWorks.Rivers.RM_RiverDriftDef"):
            rows = [(li.findtext("thing"), float(li.findtext("weight") or 0)) for li in d.find("drift")]
            for b in d.find("biomes"):
                pools.setdefault(b.text, []).extend(rows)
    check("sanity: drift pools for every vanilla river biome", set(fresh) <= set(pools), sorted(set(fresh) - set(pools)))
    for b, fish in sorted(fresh.items()):
        rows = pools.get(b, [])
        got = {t for t, w in rows if t and t.startswith("Fish_")}
        check("%s drifts dead fish, only its own" % b, got and got <= fish, sorted(got))
        check("%s drifts rare lost cargo" % b, any(t in cargo and w <= 0.25 for t, w in rows))
    tb = os.path.join(os.path.dirname(HERE), "TerminalBiomes")
    tb_text = ""
    for p in glob.glob(os.path.join(tb, "Defs", "**", "*.xml"), recursive=True):
        tb_text += open(p, encoding="utf-8").read()
    check("sanity: read TerminalBiomes defs", "RM_BankSilt" in tb_text)
    for dn in ("RM_BankStake", "RM_BankWeir", "RM_SiltTrap", "RM_FerryPost"):
        check("TerminalBiomes does not also define %s" % dn, "<defName>%s</defName>" % dn not in tb_text)
    tb_about = open(os.path.join(tb, "About", "About.xml"), encoding="utf-8").read()
    check("TerminalBiomes depends on FlowWorks", "<packageId>mandrake.rm.flowworks</packageId>" in tb_about)
    check("TerminalBiomes names no riverworks packageId", "mandrake.rm.riverworks" not in tb_about)
    tb_csproj = open(os.path.join(tb, "Source", "RM_TerminalBiomes.csproj"), encoding="utf-8").read()
    check("TerminalBiomes references the FlowWorks assembly", "RimMandrakeFlowWorks.dll" in tb_csproj
          and "RiverWorks" not in tb_csproj)
    tb_src = " ".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(tb, "Source", "*.cs")))
    for cls in ("class RM_Building_BankWeir", "class RM_Building_SiltTrap", "class CompChannelArrester"):
        check("TerminalBiomes no longer declares %s" % cls, cls not in tb_src)

    # P10 (GPT G4.3): the breach wash's drop-failed path is proven BEHAVIOURALLY in the FlowWorks SelfTest
    # (Source/SelfTest/RiverWashChecks.cs, run by src/RimMandrake/Utils/selftest_flowworks_stock.py) against
    # RM_RiverMath.WashHeld with fake things. Here: only that the case is compiled and run, so it cannot drop out.
    st = os.path.join(HERE, "Source", "SelfTest")
    check("P10 RiverWashChecks.cs is in the SelfTest compile list",
          '<Compile Include="RiverWashChecks.cs" />' in open(os.path.join(st, "RimMandrakeFlowWorks.SelfTest.csproj"), encoding="utf-8").read())
    check("P10 RiverWashChecks runs from Program.Main",
          "RiverWashChecks.Run(Case);" in open(os.path.join(st, "Program.cs"), encoding="utf-8").read())

    print("\n%s" % ("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s): %s" % (len(FAILS), FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
