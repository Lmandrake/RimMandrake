"""validation.py -- first script for RimMandrake: Deep Drill (mandrake.rm.deepdrill). DEEP_DRILL_HOME_BIOME_1.

THE MOD: Harmony postfix on CompDeepScanner.ChooseLumpThingDef; off a deposit's home biome (Defs/RM_DeepHomeTable.xml, generated from
design/RimMandrake/mineral_abundance_registry_2026-10-03.csv) the pick becomes steel. One setting, homeFilterEnabled.

STATIC (no game): `python3 validation.py` -> `STATIC: PASS (0 findings)`.
LIVE CHAIN (owed, needs the bridge; recorded here so the next poking session fills it in rather than inventing one):
  1. new map on a biome that is nobody's home (e.g. RUT_AridShrubland): call CompDeepScanner.ChooseLumpThingDef 200x on a scanner
     building; every result is Steel.      [UNMEASURED: no live run yet]
  2. map on RM_LanternDeeps: results include Diamond/Ruby/Sapphire/DV_Pyrinth/RM_Lanternstone over 400 picks.   [UNMEASURED]
  3. homeFilterEnabled off: step 1 returns non-steel lumps again.                                              [UNMEASURED]
  4. the Harmony census line "Harmony: patched N, missing X" in Player.log names no 'Deep deposits follow the biome' failure. [UNMEASURED]
VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR (vee_port_plan_2026-10-22.md §2 group O; Source/RM_TileResources.cs) -- live chain, owed:
  5. on a quicktest map whose tile carries RM_DeepOreRich, dev "find now" on a deep scanner: every new deepResourceGrid cell holds
     round(1.25 x deepCountPerCell); on an ordinary tile exactly deepCountPerCell.                                   [UNMEASURED]
  6. on a RM_DeepOreDevoid tile the scanner's CanUseNow refuses with the "No deep ores" reason; setting off: it scans.  [UNMEASURED]
  7. a map generated on a RM_MineralDevoid tile has 0 resource-rock cells with mineableScatterCommonality > 0 (compacted machinery
     may stay); an ordinary map of the same biome has some (sanity).                                                  [UNMEASURED]
  8. a map generated on a RM_MineableComponentSpacer tile has >= 1 RM_MineableComponentsSpacer lump; mining one drops ComponentSpacer. [UNMEASURED]
  9. 0 config errors naming RM_TileResourceExtension / RM_TileMutatorWorker_* / RM_MineableComponentsSpacer.          [UNMEASURED]
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))


SETTINGS = ["homeFilterEnabled", "deepOreFactorsEnabled", "richDeepOreFactor", "mineralDevoidEnabled", "spacerDepositsEnabled",
            "spacerDepositScale"]
PORTS = {  # VEE donor -> our port (vee_port_plan_2026-10-22.md §2 group O)
    "VEE_DeepOreRich": "RM_DeepOreRich",
    "VEE_DeepOreDevoid": "RM_DeepOreDevoid",
    "VEE_MineralDevoid": "RM_MineralDevoid",
    "VEE_MineableComponentSpacer": "RM_MineableComponentSpacer",
}
NS = "RimMandrake.DeepDrill."


def _tile_resource_checks(bad):
    """The four ported resource mutators: present, worldgen-closed, number-free, each wired to a class that exists."""
    classes = set()
    for dp, _, files in os.walk(os.path.join(HERE, "Source")):
        if "SelfTest" in dp:
            continue
        for fn in files:
            if fn.endswith(".cs"):
                classes |= set(re.findall(r"\b(?:class|enum) (\w+)", open(os.path.join(dp, fn), encoding="utf-8").read()))
    if "RM_TileResourceExtension" not in classes:
        bad.append("sanity: the class scan cannot see RM_TileResourceExtension")
    muts, things = {}, {}
    for dp, _, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in files:
            if fn.endswith(".xml"):
                for e in ET.parse(os.path.join(dp, fn)).getroot():
                    dn = e.findtext("defName")
                    if e.tag == "TileMutatorDef":
                        muts[dn] = e
                    elif e.tag == "ThingDef":
                        things[dn] = e
                    for txt in (e.findtext("workerClass") or "",) + tuple(li.get("Class") or "" for li in e.iter("li")):
                        if txt.startswith(NS) and txt[len(NS):] not in classes:
                            bad.append("%s names %s, which no Source class defines" % (dn, txt))
    for donor, port in PORTS.items():
        e = muts.get(port)
        if e is None:
            bad.append("port %s of %s missing" % (port, donor))
            continue
        if (e.findtext("chanceOnNonLandmarkTile") or "").strip() != "0":
            bad.append("%s: chanceOnNonLandmarkTile must be 0 (no worldgen)" % port)
        for tag in ("biomeWhitelist", "biomeBlacklist"):
            if e.find(tag) is not None:
                bad.append("%s carries <%s> (no worldgen: the lists never act)" % (port, tag))
        if re.search(r"\d", (e.findtext("label") or "") + (e.findtext("description") or "")):
            bad.append("%s: label/description carries a number; numbers are Mod Settings" % port)
    kinds = {dn: (e.find("modExtensions/li/deepOre").text if e.find("modExtensions/li/deepOre") is not None else None)
             for dn, e in muts.items()}
    if kinds.get("RM_DeepOreRich") != "Rich" or kinds.get("RM_DeepOreDevoid") != "Devoid":
        bad.append("deep-ore kinds wrong: %r" % kinds)
    if (muts.get("RM_MineralDevoid") is not None
            and muts["RM_MineralDevoid"].findtext("workerClass") != NS + "RM_TileMutatorWorker_MineralDevoid"):
        bad.append("RM_MineralDevoid is not on its worker")
    sp = muts.get("RM_MineableComponentSpacer")
    if sp is not None and sp.findtext("modExtensions/li/scatterMineable") not in things:
        bad.append("RM_MineableComponentSpacer scatters %r, which this mod does not define" % sp.findtext("modExtensions/li/scatterMineable"))
    t = things.get("RM_MineableComponentsSpacer")
    if t is None:
        bad.append("ThingDef RM_MineableComponentsSpacer missing")
    else:
        if t.findtext("building/mineableThing") != "ComponentSpacer":
            bad.append("RM_MineableComponentsSpacer does not yield ComponentSpacer")
        if t.findtext("building/mineableScatterCommonality") != "0":
            bad.append("RM_MineableComponentsSpacer would be scattered by the ordinary ore scatter (commonality must be 0)")
        if "VEE" in (t.findtext("graphicData/texPath") or ""):
            bad.append("RM_MineableComponentsSpacer uses donor art")
    rt = open(os.path.join(HERE, "Source", "RM_TileResources.cs"), encoding="utf-8").read()
    for needle in ('[HarmonyPatch(typeof(CompDeepScanner), "DoFind")]', "[HarmonyPatch(typeof(DeepResourceGrid), nameof(DeepResourceGrid.SetAt))]",
                   "nameof(CompDeepScanner.CanUseNow), MethodType.Getter", "public static void Finalizer()",
                   "RM_TileResourceKernel.ScaledCount(count, f)", "RM_DeepDrillSettings.mineralDevoidEnabled",
                   "RM_DeepDrillSettings.spacerDepositsEnabled"):
        if needle not in rt:
            bad.append("RM_TileResources.cs lacks %s" % needle)


def static_checks():
    bad = []
    src = open(os.path.join(HERE, "Source", "RM_DeepDrillMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_DeepDrillSettings", 1)[1].split("public static void Draw", 1)[0]
    fields = re.findall(r"public\s+static\s+(?:bool|float|int)\s+(\w+)\s*=", re.sub(r"//[^\n]*", "", body))
    if fields != SETTINGS:
        bad.append("settings fields changed: %s" % fields)
    for n in fields:
        if '"%s"' % n not in body or n not in src.split("Draw", 1)[1]:
            bad.append("setting %s is not scribed or has no control" % n)
    proj = open(os.path.join(HERE, "Source", "RimMandrake_DeepDrill.csproj"), encoding="utf-8").read()
    for dp, _, files in os.walk(os.path.join(HERE, "Source")):
        if "SelfTest" in dp:
            continue
        for fn in files:
            if fn.endswith(".cs") and fn not in proj:
                bad.append("%s is not in the csproj" % fn)
    patch = open(os.path.join(HERE, "Source", "Patch_DeepHome.cs"), encoding="utf-8").read()
    for needle in ('[HarmonyPatch(typeof(CompDeepScanner), "ChooseLumpThingDef")]', "homeFilterEnabled", "ThingDefOf.Steel"):
        if needle not in patch:
            bad.append("Patch_DeepHome.cs lacks %s" % needle)
    t = ET.parse(os.path.join(HERE, "Defs", "RM_DeepHomeTable.xml")).getroot()
    rows = t.findall(".//rows/li")
    if len(rows) < 20:
        bad.append("table has %d rows (sanity probe: expected >= 20)" % len(rows))
    things = [r.findtext("thing") for r in rows]
    if "Steel" in things:
        bad.append("Steel must never be a table row (it is the planet-wide deep resource)")
    if len(things) != len(set(things)):
        bad.append("duplicate thing rows")
    for must in ("Gold", "RM_Lanternstone", "RM_LivePatternMetal", "Jade"):
        if must not in things:
            bad.append("table lacks %s" % must)
    _tile_resource_checks(bad)
    return bad


if __name__ == "__main__":
    b = static_checks()
    print("STATIC: %s (%d findings)" % ("PASS" if not b else "FAIL", len(b)))
    for x in b:
        print("  -", x)
    sys.exit(1 if b else 0)
