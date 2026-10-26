"""validation.py -- first script for RimMandrake: Tile Features (mandrake.rm.tilefeatures). VEE_FLORA_VENTS_BUILD_XML_FIRST.

THE MOD: 21 world-tile features ported from Vanilla Exploration Expanded (design/RimMandrake/vee_port_plan_2026-10-22.md groups
F, W, V; the deadlife vents were dropped by owner card VEE_DEADLIFE_VENTS_ASK_ZOMBIES_AGAIN). Every port has
chanceOnNonLandmarkTile 0 and no biome lists (no worldgen). VEF stays and carries the cacti, mycelium, vent prefabs and disease
factor through its own workers; Source/ has three workers, a vent comp, the rotten stench condition, two Harmony postfixes and
the Mod Settings applier (RM_TileFeatureApplier) that makes a switched-off group inert.

STATIC (no game): `python3 validation.py` -> `STATIC: PASS (0 findings)`.
LIVE CHAIN (owed, needs the bridge; recorded here so the next poking session fills it in rather than inventing one):
  1. cold load with TileFeatures + VEF + Harmony: 0 config errors naming RM_TileFeature*, RM_CompGeyserGas, RM_Plant_*, RM_Day*,
     RM_*Vent*, RM_RottenStench, RM_DustStorm; the Harmony census line names no 'Poisonous flora' / 'More infestations' failure. [UNMEASURED]
  2. quicktest map on a tile given RM_Cactus_Barrel (world_* tools): RM_Plant_BarrelCactus is among the wild plants.          [UNMEASURED]
  3. tile given RM_ToxicVents: 6-12 RM_ToxicVent on the map; one dev-forced active cycle puts ToxGas in the gas grid.          [UNMEASURED]
  4. tile given RM_RottenStench: the permanent condition is active; a colonist gains RM_RottenStench within 2500 ticks; weather
     switch off: no new hediff.                                                                                                [UNMEASURED]
  5. tile given RM_DustStorms: WeatherDecider commonality of RM_DustStorm > 0 (it is 0 on the same biome without the feature). [UNMEASURED]
  6. tile given RM_PoisonousFlora: harvesting a wild plant raises ToxicBuildup by ~0.05 x (1 - ToxicResistance); a sown one does not. [UNMEASURED]
  7. tile given RM_IncreasedInfestations: IncidentDefOf.Infestation Worker.ChanceFactorNow(map) is x1.5 against an ordinary map. [UNMEASURED]
  8. RM_IncreasedDiseases: VEF reads diseaseMTBMultiplier from the extension at each roll (so the slider applies to an
     existing map), or caches it at startup (then only a restart applies it).                                                  [UNMEASURED]
  9. every group switch off + settings closed: a new map on each feature's tile equals a plain map of the biome.               [UNMEASURED]
OWED OUTSIDE THIS SCRIPT: own art for the six cacti (placeholder Things/Plant/SaguaroCactus) and the three vents (placeholder
Things/Building/AncientToxVent); the one world stamp at the end (VEE_WORLD_RENAME_ONE_STAMP_AT_END) that puts these on tiles.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))

SETTINGS = ["floraEnabled", "weatherEnabled", "ventsEnabled", "diseasesEnabled", "infestationsEnabled", "diseaseMtbMultiplier",
            "infestationFactor", "ventCountScale", "poisonSeverityPerHarvest"]
PORTS = {  # VEE donor -> our port (vee_port_plan_2026-10-22.md section 2, groups F, W, V)
    "VEE_Cactus_Barrel": "RM_Cactus_Barrel", "VEE_Cactus_Beavertail": "RM_Cactus_Beavertail",
    "VEE_Cactus_Hedgehog": "RM_Cactus_Hedgehog", "VEE_Cactus_OrganPipe": "RM_Cactus_OrganPipe",
    "VEE_RedDesertPlants": "RM_RedDesertPlants", "VEE_Mycelium": "RM_Mycelium",
    "VEE_PlantLife_Overgrown": "RM_PlantLife_Overgrown", "VEE_PlantLife_Decimated": "RM_PlantLife_Decimated",
    "VEE_NoTrees": "RM_NoTrees", "VEE_PoisonousFlora": "RM_PoisonousFlora", "VEE_Fertility_Reduced": "RM_Fertility_Reduced",
    "VEE_MarineSanctuary": "RM_MarineSanctuary", "VEE_MechanoidShipChunks": "RM_MechanoidShipChunks",
    "VEE_Sandstorms": "RM_Sandstorms", "VEE_DustStorms": "RM_DustStorms", "VEE_RottenStench": "RM_RottenStench",
    "VEE_IncreasedDiseases": "RM_IncreasedDiseases", "VEE_IncreasedInfestations": "RM_IncreasedInfestations",
    "VEE_ToxicVents": "RM_ToxicVents", "VEE_RotstinkVents": "RM_RotstinkVents", "VEE_SmokeVents": "RM_SmokeVents",
}
NS = "RimMandrake.TileFeatures."
GAS = {"ToxGas", "RotStink", "BlindSmoke"}
# Category strings are shared with VEE on purpose (they keep features of one kind from stacking on a tile); they name no def.
CATEGORY_PARENTS = {"categories", "overrideCategories"}


def _read(*p):
    return open(os.path.join(HERE, *p), encoding="utf-8").read()


def donor_refs(root):
    """Every 'VEE_' text in a def other than a category string: a reference to a def of the mod being retired."""
    out = []
    parent = {c: p for p in root.iter() for c in p}
    for e in root.iter():
        txt = (e.text or "").strip()
        if txt.startswith("VEE_") and parent.get(e) is not None and parent[e].tag not in CATEGORY_PARENTS:
            out.append("%s <%s>%s" % (root.findtext("defName"), e.tag, txt))
        for v in e.attrib.values():
            if v.startswith("VEE") or v.startswith("VanillaExplorationExpanded"):
                out.append("%s attribute %s" % (root.findtext("defName"), v))
    return out


def static_checks():
    bad = []
    # settings: declared, scribed, drawn
    src = _read("Source", "RM_TileFeaturesMod.cs")
    body = src.split("class RM_TileFeaturesSettings", 1)[1].split("private static float Slider", 1)[0]
    fields = re.findall(r"public\s+static\s+(?:bool|float|int)\s+(\w+)\s*=", re.sub(r"//[^\n]*", "", body))
    if fields != SETTINGS:
        bad.append("settings fields changed: %s" % fields)
    draw = src.split("public static void Draw", 1)[1]
    for n in fields:
        if '"%s"' % n not in body or n not in draw:
            bad.append("setting %s is not scribed or has no control" % n)
    # every .cs in the csproj; every class the defs name exists
    proj = _read("Source", "RimMandrake_TileFeatures.csproj")
    classes = set()
    for fn in os.listdir(os.path.join(HERE, "Source")):
        if fn.endswith(".cs"):
            if fn not in proj:
                bad.append("%s is not in the csproj" % fn)
            classes |= set(re.findall(r"\bclass (\w+)", _read("Source", fn)))
    if "RM_CompGeyserGas" not in classes:
        bad.append("sanity: the class scan cannot see RM_CompGeyserGas")
    # defs
    defs, ours = {}, set()
    for dp, _, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in files:
            if not fn.endswith(".xml"):
                continue
            for e in ET.parse(os.path.join(dp, fn)).getroot():
                dn = e.findtext("defName")
                if dn is None:
                    continue
                if not dn.startswith("RM_"):
                    bad.append("%s %s lacks the RM_ prefix" % (e.tag, dn))
                if (e.tag, dn) in defs:
                    bad.append("duplicate %s %s" % (e.tag, dn))
                defs[(e.tag, dn)] = e
                ours.add(dn)
                bad.extend("donor reference: " + r for r in donor_refs(e))
                for txt in (e.findtext("workerClass") or "", e.findtext("conditionClass") or "") + tuple(
                        li.get("Class") or "" for li in e.iter("li")):
                    if txt.startswith(NS) and txt[len(NS):] not in classes:
                        bad.append("%s names %s, which no Source class defines" % (dn, txt))
    if len(defs) < 40:
        bad.append("sanity: only %d defs seen (expected >= 40)" % len(defs))
    # every RM_ name a def mentions is defined here (plants, prefabs, gen step, condition, weather, hediff, thoughts)
    for (tag, dn), e in defs.items():
        for x in e.iter():
            t = (x.text or "").strip()
            if re.fullmatch(r"RM_\w+", t) and t not in ours:
                bad.append("%s %s names %s, which this mod does not define" % (tag, dn, t))
    muts = {dn: e for (tag, dn), e in defs.items() if tag == "TileMutatorDef"}
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
    extra = set(muts) - set(PORTS.values())
    if extra:
        bad.append("tile features not in PORTS: %s" % sorted(extra))
    # the settings applier covers exactly the ports, each once
    app = _read("Source", "RM_TileFeatureApplier.cs")
    grouped = re.findall(r'"(RM_\w+)"', app.split("private const string VefExtension", 1)[0])
    if sorted(grouped) != sorted(PORTS.values()):
        bad.append("applier groups != ports: missing %s, extra %s" % (
            sorted(set(PORTS.values()) - set(grouped)), sorted(set(grouped) - set(PORTS.values()))))
    if len(grouped) != len(set(grouped)):
        bad.append("a feature is in two applier groups")
    # vents: rare ticker, a vanilla grid gas, a prefab that places them
    for (tag, dn), e in defs.items():
        comp = e.find("comps/li[@Class='%sRM_CompProperties_GeyserGas']" % NS)
        if tag != "ThingDef" or comp is None:
            continue
        if e.findtext("tickerType") != "Rare":
            bad.append("%s: the vent comp ticks only rarely; tickerType must be Rare" % dn)
        if comp.findtext("gasType") not in GAS:
            bad.append("%s: gasType %r is not a vanilla grid gas" % (dn, comp.findtext("gasType")))
    for v in ("RM_ToxicVents", "RM_RotstinkVents", "RM_SmokeVents"):
        e = muts.get(v)
        pf = e.findtext("modExtensions/li/prefabsToSpawn/li") if e is not None else None
        if pf is None or ("PrefabDef", pf) not in defs:
            bad.append("%s spawns prefab %r, which this mod does not define" % (v, pf))
    # patches target what the design says
    pt = _read("Source", "RM_TileFeaturePatches.cs")
    for needle in ("[HarmonyPatch(typeof(Plant), nameof(Plant.PlantCollected))]", "__instance.sown",
                   "[HarmonyPatch(typeof(IncidentWorker), nameof(IncidentWorker.ChanceFactorNow))]", "IncidentWorker_Infestation"):
        if needle not in pt:
            bad.append("RM_TileFeaturePatches.cs lacks %s" % needle)
    # planted negative: the donor-reference check must see a VEE_ def name and must pass a category string
    probe = ET.fromstring("<TileMutatorDef><defName>RM_Probe</defName><categories><li>VEE_Fertility</li></categories>"
                          "<additionalGameConditions><li>VEE_RottenStench</li></additionalGameConditions></TileMutatorDef>")
    if len(donor_refs(probe)) != 1:
        bad.append("sanity: donor-reference check returned %r on the planted probe" % donor_refs(probe))
    return bad


if __name__ == "__main__":
    b = static_checks()
    print("STATIC: %s (%d findings)" % ("PASS" if not b else "FAIL", len(b)))
    for x in b:
        print("  -", x)
    sys.exit(1 if b else 0)
