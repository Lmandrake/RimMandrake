"""validation.py -- first script for RimMandrake: Wreckage (mandrake.rm.wreckage), composed into
mandrake.rm.biomes as an engine entry.

SALVAGE_WRECKAGE_EVERYWHERE_1, slice 1: the loot half of design step 1;
slice 2: the family parents and the weathering row, the Scald reparented as the template;
slice 3: the weighted wreck-field GenStep + density classes, the Scald's three steps merged into one
(S6 folded into the field key "Scald", alias Scald.S6), and the Riddled/High weathering rows
(design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md §3c, §3d, §6). Walk:
design/validation_walks/RimMandrake/Wreckage.md. Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Wreckage

Offline: `python3 src/RimMandrake/Wreckage/validation.py` runs static_checks() only.
Not proven here: the drop itself (no bridge verb deconstructs with a pawn yet; the walk says so).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
SCALD = os.path.join(HERE, "..", "TerminalBiomes", "Defs", "ThingDefs_Buildings", "RUT_ScaldWrecks.xml")
suite = Suite("Wreckage")
suite.toggles = ["salvageLoot", "lootGenerosity", "skillScalesRare", "wreckFields", "wreckDensity", "disabledFields", "wreckFalls"]

TIERS = ("Scrap", "Hull", "Tank", "Carapace", "Sealed")
RARE_TIERS = ("Hull", "Tank", "Carapace", "Sealed")
TABLES = ["RM_SalvageLoot_%s" % t for t in TIERS] + ["RM_SalvageLoot_%s_Rare" % t for t in RARE_TIERS]
SCALD_WRECKS = {"RUT_ScaldWreckHull": "Hull", "RUT_ScaldWreckTank": "Tank", "RUT_ScaldWreckFrame": "Scrap"}
COMP_CLASS = "RimMandrake.Wreckage.RM_CompProperties_SalvageLoot"
EXT_CLASS = "RimMandrake.Wreckage.RM_WreckWeathering"
WDEF_TAG = "RimMandrake.Wreckage.RM_WreckWeatheringDef"
FAMILIES_XML = os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_WreckFamilies.xml")
WEATHER_XML = os.path.join(HERE, "Defs", "RM_WreckWeatheringDefs", "RM_WreckWeatherings.xml")
FAMILY_NAMES = ["RM_WreckFamily_%s" % f for f in ("Hull", "Tank", "Frame", "Speeder", "Carapace", "Tread")]
# What the Scald shipped before slice 2 reparented it (96f8113e9): costList and deconstruct fraction.
SCALD_SHIPPED = {
    "RUT_ScaldWreckHull": ({"Steel": 30, "ComponentIndustrial": 1}, 0.75),
    "RUT_ScaldWreckTank": ({"Steel": 20, "GravlitePanel": 5}, 0.75),
    "RUT_ScaldWreckFrame": ({"Steel": 15}, 0.75),
}
DENSITY_XML = os.path.join(HERE, "Defs", "RM_WreckDensityClassDefs", "RM_WreckDensityClasses.xml")
DCLASS_TAG = "RimMandrake.Wreckage.RM_WreckDensityClassDef"
FIELD_CLASS = "RimMandrake.Wreckage.RM_GenStep_WreckField"
FIELD_CS = os.path.join(HERE, "Source", "RM_GenStep_WreckField.cs")
TB = os.path.join(HERE, "..", "TerminalBiomes")
SCALD_FIELD_XML = os.path.join(TB, "Defs", "MapGeneration", "RUT_ScaldWreckScatter.xml")
SCALD_REGISTER_XML = os.path.join(TB, "Patches", "RUT_ScaldWreckScatter_Register.xml")
SCALD_TERRAIN_XML = os.path.join(TB, "Defs", "TerrainDefs", "RUT_ScaldWater.xml")
TB_MOD_CS = os.path.join(TB, "Source", "RM_TerminalBiomesMod.cs")
OLD_SCALD_STEPS = ["RUT_Jawa_ScatterScaldWreck%s" % k for k in ("Hull", "Tank", "Frame")]
# Expected per the placement law (design §3d-i): ordered by persistence, Riddled densest.
DENSITY_ORDER = ["RM_WreckDensity_Riddled", "RM_WreckDensity_High", "RM_WreckDensity_Moderate", "RM_WreckDensity_Low"]
# Design §4 numbers for the rows this script pins (yieldFactor, lootTierShift).
WEATHER_PINNED = {"RM_WreckWeathering_Cooked": (0.75, 0), "RM_WreckWeathering_Frozen": (1.0, 1),
                  "RM_WreckWeathering_Picked": (0.2, -2), "RM_WreckWeathering_CrystalJacketed": (1.0, 1),
                  "RM_WreckWeathering_Stripped": (0.35, -1), "RM_WreckWeathering_Irradiated": (0.9, 0),
                  "RM_WreckWeathering_SandScoured": (0.6, 0), "RM_WreckWeathering_Sealed": (1.0, 1),
                  "RM_WreckWeathering_IceLocked": (0.9, 0), "RM_WreckWeathering_Eroded": (0.2, -2),
                  "RM_WreckWeathering_Brined": (0.7, 0), "RM_WreckWeathering_FloodBuried": (0.8, 0),
                  "RM_WreckWeathering_Overgrown": (0.8, 0), "RM_WreckWeathering_Digested": (0.6, 0),
                  "RM_WreckWeathering_StormTorn": (0.8, 0)}
# Fields that must exist planet-wide once steps 3-4 landed (design §7): {field: registered-in}.
PLANET_FIELDS = {"RM_WreckField_Scald": "biome", "RM_WreckField_NightsideIce": "biome",
                 "RM_WreckField_LanternDeeps": "biome", "RM_WreckField_Warscar": "biome",
                 "RM_WreckField_Wasteland": "biome", "RM_WreckField_GreyFloor": "floor",
                 "RM_WreckField_TwilightFloor": "floor", "RM_WreckField_ScaldFloor": "floor",
                 "RM_WreckField_BlueDesert": "biome", "RM_WreckField_Miasma": "biome",
                 "RM_WreckField_FloodedCanyon": "biome", "RM_WreckField_FeverWood": "biome",
                 "RM_WreckField_TheRot": "biome", "RM_WreckField_Abyss": "biome",
                 "RM_WreckField_Stillsand": "biome", "RM_WreckField_Contagion": "biome"}
# Step 7, the placement law's Cleaned class (design §3d-i): travelled or inhabited land scatters nothing.
CLEANED_BIOMES = {"RM_Greentide", "RM_LeaningScrub", "RM_LongShade", "RM_RustCathedral", "RM_TheForge", "RM_TheSump",
                  "Desert", "AridShrubland"}
# Every family must have at least one child by step 6 (design §3a's six families).
FAMILIES_WITH_CHILDREN = FAMILY_NAMES
SRC_ROOT = os.path.normpath(os.path.join(HERE, ".."))
LICHEN_CS = os.path.join(HERE, "..", "Scarlands", "Source", "MapComponent_WreckLichen.cs")
# Public fields of the base class GenStep_Scatterer (RimSage Verse/GenStep_Scatterer.cs), so an XML field
# that is neither ours nor the base's is a typo the loader would only warn about at load.
SCATTERER_FIELDS = {"count", "countPer10kCellsRange", "nearPlayerStart", "nearMapCenter", "minSpacing",
                    "spotMustBeStandable", "minDistToPlayerStart", "minDistToPlayerStartPct", "minEdgeDist",
                    "minEdgeDistPct", "extraNoBuildEdgeDist", "validators", "fallbackValidators", "allowInWaterBiome",
                    "allowFoggedPositions", "allowRoofed", "onlyOnStartingMap", "minPollution",
                    "allowMechanoidDatacoreReadOrLost", "isJunk", "warnOnFail"}
NEEDLES = ("mandrake.rm.wreckage", "RimMandrake.Wreckage", "RM_SalvageLoot", "RM_CompSalvageLoot",
           "RM_WreckFamily", "RM_WreckWeathering", "RM_WreckField", "RM_WreckDensity", "[Wreckage]")


@suite.chain("load")
def load(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("UNMEASURED: drain_log did not answer")
            msgs = [m.get("text", "") for m in (r.get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


def _get_defs(t, want):
    r = t.bridge_call("jawa/get_defs", defs=";".join(want), fields="defName")
    if not isinstance(r, dict) or not r.get("success"):
        raise ExpectationFailed("UNMEASURED: get_defs failed: %r" % (r,))
    if r.get("notFound"):
        raise ExpectationFailed("defs missing: %r" % r.get("notFound"))


@suite.chain("defs")
def defs(t):
    with t.component("loot_tables_resolve", beyond_toggle=True):
        if t._guard():
            _get_defs(t, ["ThingSetMakerDef/%s" % d for d in TABLES])
    with t.component("scald_wrecks_resolve", beyond_toggle=True):
        if t._guard():
            # A ThingDef whose comp Class cannot resolve is discarded whole, so presence is the check.
            _get_defs(t, ["ThingDef/%s" % d for d in SCALD_WRECKS])
    with t.component("scald_field_resolves", beyond_toggle=True):
        if t._guard():
            # One step now; a GenStepDef whose genStep Class cannot resolve is an error at load.
            _get_defs(t, ["GenStepDef/RM_WreckField_Scald"])


@suite.chain("mapgen")
def mapgen(t):
    for comp, tog, why in (
            ("scald_field_on_shallows_only", None,
             "needs a FRESH Scald map; list_things RUT_ScaldWreck* then every occupied cell's terrain must carry "
             "RUT_ScaldShallow"),
            ("wreck_fields_off_new_map_empty", "wreckFields",
             "needs a fresh Scald map generated with wreckFields false (and one with disabledFields \"Scald\")"),
            ("density_scales_count", "wreckDensity",
             "needs two fresh Scald maps at density 0 and 2; zero at 0, more at 2 (ratio, not exact)")):
        with t.component(comp, toggle=tog, beyond_toggle=tog is None):
            if t._guard():
                raise ExpectationFailed("UNMEASURED: " + why)


def _shift(tier, shift):
    """Mirror of RM_WreckWeathering.ShiftTier (C#)."""
    rank = 0 if tier == "Scrap" else 2 if tier == "Sealed" else 1
    to = max(0, min(2, rank + shift))
    if to == rank:
        return tier
    return "Scrap" if to == 0 else "Sealed" if to == 2 else ("Hull" if rank == 0 else tier)


def _families(bad):
    """{family: (tier, rareChance, costList, fraction)} with the base's fraction inherited."""
    out = {}
    root = ET.parse(FAMILIES_XML).getroot()
    base = [e for e in root if e.get("Name") == "RM_WreckFamilyBase"]
    if len(base) != 1 or base[0].get("ParentName") != "ShipChunkBase" or base[0].get("Abstract") != "True":
        bad.append("RM_WreckFamilyBase missing, not abstract, or not on ShipChunkBase")
        return out
    b = base[0]
    if b.findtext("terrainAffordanceNeeded") != "Walkable":
        bad.append("RM_WreckFamilyBase does not set Walkable (shallows fail on inherited Light)")
    bfrac = float(b.findtext("resourcesFractionWhenDeconstructed") or "0.5")
    for e in root:
        n = e.get("Name")
        if n == "RM_WreckFamilyBase":
            continue
        if e.get("Abstract") != "True" or e.get("ParentName") != "RM_WreckFamilyBase" or e.findtext("defName"):
            bad.append("%s is not an abstract child of RM_WreckFamilyBase" % n)
            continue
        comps = [li for li in e.findall("comps/li") if li.get("Class") == COMP_CLASS]
        if len(comps) != 1:
            bad.append("%s carries %d salvage-loot comps (want 1)" % (n, len(comps)))
            continue
        if e.find("comps").get("Inherit") == "False":
            bad.append("%s drops ShipChunkBase's inherited comps" % n)
        cl = e.find("costList")
        if cl is None or cl.get("Inherit") != "False" or e.find("killedLeavings") is None \
                or e.find("killedLeavings").get("Inherit") != "False":
            bad.append("%s must set costList and killedLeavings Inherit=False (else ShipChunk's 11 components ride along)" % n)
            continue
        cost = {c.tag: int(c.text) for c in cl}
        frac = float(e.findtext("resourcesFractionWhenDeconstructed") or bfrac)
        out[n] = (comps[0].findtext("lootTier"), float(comps[0].findtext("rareChance") or "0.05"), cost, frac)
    if sorted(out) != sorted(FAMILY_NAMES):
        bad.append("families parsed %s, want %s" % (sorted(out), sorted(FAMILY_NAMES)))
    return out


NO_LOOT = set()


def _weatherings(bad):
    """{defName: (yieldFactor, lootTierShift)}"""
    out = {}
    for e in ET.parse(WEATHER_XML).getroot():
        if e.tag != WDEF_TAG:
            bad.append("weathering file holds a <%s>" % e.tag)
            continue
        yf = float(e.findtext("yieldFactor") or "1")
        sh = int(e.findtext("lootTierShift") or "0")
        if not 0 < yf <= 1.5 or not -2 <= sh <= 2:
            bad.append("%s out of range (yieldFactor %s, shift %s)" % (e.findtext("defName"), yf, sh))
        out[e.findtext("defName")] = (yf, sh)
        if (e.findtext("noLoot") or "").strip() == "true":
            NO_LOOT.add(e.findtext("defName"))
    if not out:
        bad.append("no weathering rows parsed")
    return out


def _density_classes(bad):
    """{defName: (min, max, clusterChance)}"""
    out = {}
    for e in ET.parse(DENSITY_XML).getroot():
        if e.tag != DCLASS_TAG:
            bad.append("density file holds a <%s>" % e.tag)
            continue
        dn = e.findtext("defName")
        try:
            lo, hi = [float(x) for x in (e.findtext("countPer10kCellsRange") or "").split("~")]
        except ValueError:
            bad.append("%s countPer10kCellsRange unparseable" % dn)
            continue
        cc = float(e.findtext("clusterChance") or "0")
        if lo < 0 or hi < lo or not 0 <= cc <= 1:
            bad.append("%s out of range (%s~%s, cluster %s)" % (dn, lo, hi, cc))
        cs = e.findtext("clusterSizeRange")
        if cs and int(cs.split("~")[0]) < 2:
            bad.append("%s clusterSizeRange below 2" % dn)
        out[dn] = (lo, hi, cc)
    missing = [d for d in DENSITY_ORDER + ["RM_WreckDensity_Eroded"] if d not in out]
    if missing:
        bad.append("density classes missing: %s" % missing)
        return out
    mids = [sum(out[d][:2]) / 2 for d in DENSITY_ORDER]
    if mids != sorted(mids, reverse=True):
        bad.append("density classes break the persistence law (Riddled > High > Moderate > Low): mids %s" % mids)
    return out


def _cs_fields(path):
    src = open(path, encoding="utf-8").read().split("class RM_GenStep_WreckField")[1].split("RM_WreckFieldStartup")[0]
    return set(re.findall(r"^\s*public (?!override|static)[\w<>.,\s]+? (\w+)\s*(?:=[^;]*)?;", src, flags=re.M))


def _field_checks(bad, weathers):
    """The wreck-field GenStep(s): shape, refs, the Scald merge and the S6 fold."""
    for dn, want in WEATHER_PINNED.items():
        if weathers.get(dn) != want:
            bad.append("weathering %s is %s, design §4 pins %s" % (dn, weathers.get(dn), want))
    classes = _density_classes(bad)
    ours = _cs_fields(FIELD_CS) | SCATTERER_FIELDS
    wreck_defs = {e.findtext("defName") for e in ET.parse(SCALD).getroot() if e.findtext("defName")}
    tags = set(li.text for li in ET.parse(SCALD_TERRAIN_XML).getroot().iter("li") if li.text)
    fields = {}
    for e in ET.parse(SCALD_FIELD_XML).getroot():
        gs = e.find("genStep")
        if e.tag != "GenStepDef" or gs is None:
            continue
        dn = e.findtext("defName")
        if gs.get("Class") != FIELD_CLASS:
            bad.append("%s is %s, not the wreck field" % (dn, gs.get("Class")))
            continue
        fields[dn] = gs
        for child in gs:
            if child.tag not in ours:
                bad.append("%s sets <%s>, which is no field of RM_GenStep_WreckField or GenStep_Scatterer" % (dn, child.tag))
        if not gs.findtext("settingsKey"):
            bad.append("%s has no settingsKey (no checkbox, no gate)" % dn)
        dc = gs.findtext("densityClass")
        if dc not in classes:
            bad.append("%s names density class %s, not defined" % (dn, dc))
        w = gs.find("wrecks")
        rows = list(w) if w is not None else []
        if not rows or any(r.tag == "li" for r in rows):
            bad.append("%s wrecks list empty or in <li> form (the custom loader reads element names)" % dn)
        for r in rows:
            if r.tag not in wreck_defs:
                bad.append("%s lists %s, which no Scald wreck def defines" % (dn, r.tag))
            try:
                if float(r.text) <= 0:
                    bad.append("%s gives %s weight %s" % (dn, r.tag, r.text))
            except (TypeError, ValueError):
                bad.append("%s gives %s a non-number weight %r" % (dn, r.tag, r.text))
        for li in gs.findall("terrainValidationAllowed/li"):
            if li.text not in tags:
                bad.append("%s validates on tag %s, which no Scald terrain carries" % (dn, li.text))
        if float(gs.findtext("terrainValidationRadius") or "0") <= 0 and gs.find("terrainValidationAllowed") is not None:
            bad.append("%s has allowed tags but radius 0: the tags are never read" % dn)
    if sorted(fields) != ["RM_WreckField_Scald"]:
        bad.append("Scald wreck fields: %s, want exactly RM_WreckField_Scald (three steps merged into one)" % sorted(fields))
        return
    gs = fields["RM_WreckField_Scald"]
    if sorted(r.tag for r in gs.find("wrecks")) != sorted(SCALD_WRECKS):
        bad.append("RM_WreckField_Scald does not list all three Scald wrecks")
    if gs.findtext("settingsKey") != "Scald" or [li.text for li in gs.findall("gateAliases/li")] != ["Scald.S6"]:
        bad.append("RM_WreckField_Scald must key on Scald with the Scald.S6 alias (design §6)")
    if gs.findtext("countPer10kCellsRange") != "1.2~1.8" or gs.findtext("allowInWaterBiome") != "true":
        bad.append("RM_WreckField_Scald changed the shipped ceiling (3 x 0.4~0.6) or dropped allowInWaterBiome")
    reg = ET.parse(SCALD_REGISTER_XML).getroot()
    for biome in ("RM_TheScald", "RUT_TheScald"):
        ops = [op for op in reg if biome in (op.findtext("xpath") or "")]
        got = [li.text for op in ops for li in op.iter("li")]
        if got.count("RM_WreckField_Scald") != 2:  # the match and the nomatch arms
            bad.append("register patch does not add RM_WreckField_Scald to %s on both arms" % biome)
    stale = []
    root = os.path.normpath(os.path.join(HERE, ".."))
    for dp, dns, fns in os.walk(os.path.normpath(os.path.join(HERE, "..", ".."))):
        dns[:] = [d for d in dns if d not in (".git", "obj", "bin", "__pycache__")]
        for fn in fns:
            if fn.endswith((".xml", ".cs")):
                txt = open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()
                if any(o in txt for o in OLD_SCALD_STEPS) and fn != "RUT_ScaldWreckScatter.xml":
                    stale.append(os.path.relpath(os.path.join(dp, fn), root))
                if "scaldS6WreckSalvage" in txt or "ScaldS6WreckSalvage" in txt or "RM_GenStep_ScaldWreckScatter" in txt:
                    stale.append(os.path.relpath(os.path.join(dp, fn), root) + " (S6 bool/class)")
    if stale:
        bad.append("old three-step Scald scatter or S6 bool still referenced: %s" % sorted(set(stale)))
    tb = open(TB_MOD_CS, encoding="utf-8").read()
    if re.search(r'Register\("Scald\.S6"', tb):
        bad.append("TerminalBiomes still registers Scald.S6 (the alias is Wreckage's now)")
    if not re.search(r'Register\("Scald", \(\) => RM_TerminalBiomesSettings\.ScaldActive\)', tb):
        bad.append("TerminalBiomes does not register the bare Scald gate: the field would ignore the biome switch")


FALL_WORKER = "RimMandrake.Wreckage.RM_IncidentWorker_WreckFall"
FALL_EXT = "RimMandrake.Wreckage.RM_WreckFallExtension"
LIST_TAG = "RimMandrake.Wreckage.RM_WreckListDef"


def _wreckfall_checks(bad):
    """Design §3e (step 5): the wreck-fall IncidentDef names a defined list with element-name rows
    and a defined skyfaller; the worker and list types exist in the source."""
    d = os.path.join(HERE, "Defs")
    lists = {}
    for e in ET.parse(os.path.join(d, "RM_WreckListDefs", "RM_WreckLists.xml")).getroot():
        if e.tag == LIST_TAG:
            rows = list(e.find("wrecks")) if e.find("wrecks") is not None else []
            if any(r.tag == "li" for r in rows):
                bad.append("%s uses <li> rows; the loader reads element names" % e.findtext("defName"))
            ok = []
            for r in rows:
                try:
                    if float(r.text or 0) > 0:
                        ok.append(r.tag)
                except ValueError:
                    bad.append("%s row <%s> weight %r is not a number" % (e.findtext("defName"), r.tag, r.text))
            lists[e.findtext("defName")] = ok
    for n, rows in lists.items():
        if not rows:
            bad.append("wreck list %s has no row with weight > 0" % n)
    falls = [e.findtext("defName") for e in ET.parse(os.path.join(d, "ThingDefs_Skyfallers", "RM_WreckFallIncoming.xml")).getroot()
             if e.tag == "ThingDef"]
    incs = [e for e in ET.parse(os.path.join(d, "IncidentDefs", "RM_WreckFall.xml")).getroot() if e.tag == "IncidentDef"]
    if not incs:
        bad.append("no wreck-fall IncidentDef")
    for e in incs:
        dn = e.findtext("defName")
        if e.findtext("workerClass") != FALL_WORKER:
            bad.append("%s worker is %s" % (dn, e.findtext("workerClass")))
        ext = [li for li in e.findall("modExtensions/li") if li.get("Class") == FALL_EXT]
        if len(ext) != 1:
            bad.append("%s carries %d wreck-fall extensions (want 1)" % (dn, len(ext)))
            continue
        if ext[0].findtext("wreckList") not in lists:
            bad.append("%s names wreck list %s, not defined" % (dn, ext[0].findtext("wreckList")))
        sky = ext[0].findtext("skyfaller") or "RM_WreckFallIncoming"
        if sky not in falls and sky != "ShipChunkIncoming":
            bad.append("%s skyfaller %s not defined here" % (dn, sky))
    src = open(os.path.join(HERE, "Source", "RM_IncidentWorker_WreckFall.cs"), encoding="utf-8").read()
    for t in ("class RM_IncidentWorker_WreckFall", "class RM_WreckListDef", "class RM_WreckFallExtension",
              "RM_WreckageSettings.wreckFalls"):
        if t not in src:
            bad.append("wreck-fall source lacks %r" % t)


def _xml_roots():
    for dp, dns, fns in os.walk(SRC_ROOT):
        dns[:] = [d for d in dns if d not in (".git", "obj", "bin", "__pycache__", "Textures", "Assemblies")]
        for fn in fns:
            if fn.endswith(".xml"):
                path = os.path.join(dp, fn)
                try:
                    yield path, ET.parse(path).getroot()
                except ET.ParseError as ex:
                    yield path, ex


def _planet_checks(bad, fams, weathers, tables):
    """Steps 3-4: every wreck field on the planet, its children and its registration."""
    children, fields, biome_regs, floor_regs = {}, {}, {}, {}
    classes = _density_classes([])
    ours = _cs_fields(FIELD_CS) | SCATTERER_FIELDS
    for path, root in _xml_roots():
        if isinstance(root, ET.ParseError):
            if any(n in open(path, encoding="utf-8", errors="replace").read() for n in ("RM_WreckField", "RM_WreckFamily")):
                bad.append("%s does not parse: %s" % (os.path.relpath(path, SRC_ROOT), root))
            continue
        for e in root:
            dn = e.findtext("defName")
            if e.tag == "ThingDef" and (e.get("ParentName") or "") in fams and dn:
                children[dn] = e
            elif e.tag == "GenStepDef" and e.find("genStep") is not None and e.find("genStep").get("Class") == FIELD_CLASS:
                fields[dn] = e.find("genStep")
            elif e.tag == "BiomeDef":
                for li in e.findall("extraGenSteps/li"):
                    biome_regs.setdefault(li.text, []).append(dn)
                    if dn in CLEANED_BIOMES and (li.text or "").startswith("RM_WreckField_"):
                        bad.append("Cleaned biome %s registers %s: travelled land scatters no wrecks (design §3d-i)" % (dn, li.text))
            elif e.tag == "MapGeneratorDef":
                for li in e.findall("genSteps/li"):
                    floor_regs.setdefault(li.text, []).append(dn)
        if root.tag == "Patch":  # the Scald and the Fever Wood register by patch
            ptxt = open(path, encoding="utf-8", errors="replace").read()
            for li in root.iter("li"):
                if li.text and li.text.startswith("RM_WreckField_"):
                    biome_regs.setdefault(li.text, []).append("(patch)")
                    hit = [b for b in CLEANED_BIOMES if 'defName="%s"' % b in ptxt]
                    if hit:
                        bad.append("%s patches %s onto Cleaned biome(s) %s (design §3d-i)" % (os.path.basename(path), li.text, hit))
    # Sanity probe: the instrument must see the Scald's known field and its three children.
    if "RM_WreckField_Scald" not in fields or not set(SCALD_WRECKS) <= set(children):
        bad.append("planet sweep cannot see the Scald field/children: the sweep is blind, nothing below is evidence")
        return
    for want, kind in PLANET_FIELDS.items():
        if want not in fields:
            bad.append("planet field %s missing (design §7 steps 3-4)" % want)
            continue
        regs = biome_regs.get(want, []) if kind == "biome" else floor_regs.get(want, [])
        if not regs:
            bad.append("%s is defined but registered in no %s" % (want, "BiomeDef/patch" if kind == "biome" else "floor generator"))
        if kind == "floor":
            gens = sorted(regs)
            if not (any(g.startswith("RM_SeabedGenerator_") for g in gens) and any(g.startswith("RM_SeaDiveGenerator_") for g in gens)):
                bad.append("%s must be in the Seabed generator AND its SeaDive twin, got %s" % (want, gens))
    for fdn, gs in fields.items():
        for child in gs:
            if child.tag not in ours:
                bad.append("%s sets <%s>, which is no field of RM_GenStep_WreckField or GenStep_Scatterer" % (fdn, child.tag))
        if not gs.findtext("settingsKey"):
            bad.append("%s has no settingsKey" % fdn)
        if gs.findtext("densityClass") not in classes:
            bad.append("%s names density class %s, not defined" % (fdn, gs.findtext("densityClass")))
        rows = list(gs.find("wrecks")) if gs.find("wrecks") is not None else []
        if not rows or any(r.tag == "li" for r in rows):
            bad.append("%s wrecks list empty or in <li> form" % fdn)
        floor = fdn in floor_regs
        for r in rows:
            c = children.get(r.tag)
            if c is None:
                bad.append("%s lists %s, which is no wreck-family child" % (fdn, r.tag))
                continue
            if floor and (c.findtext("terrainAffordanceNeeded") or "Walkable") == "Walkable":
                bad.append("%s (floor field %s) needs Walkable, which RM_SeaFloorGround lacks: nothing would place" % (r.tag, fdn))
    keys = [gs.findtext("settingsKey") for gs in fields.values()]
    if len(keys) != len(set(keys)):
        bad.append("two wreck fields share a settingsKey: %s" % sorted(keys))
    for dn, c in children.items():
        ext = [li for li in c.findall("modExtensions/li") if li.get("Class") == EXT_CLASS]
        if len(ext) != 1:
            bad.append("%s carries %d weathering extensions (want 1)" % (dn, len(ext)))
            continue
        w = ext[0].findtext("weathering")
        if w not in weathers:
            bad.append("%s names weathering %s, not defined" % (dn, w))
            continue
        if [li for li in c.findall("comps/li") if li.get("Class") == COMP_CLASS]:
            bad.append("%s restates the salvage comp (two rolls)" % dn)
        if w in NO_LOOT:
            continue
        tier = _shift(fams[c.get("ParentName")][0], weathers[w][1])
        if "RM_SalvageLoot_%s" % tier not in tables:
            bad.append("%s resolves to tier %s with no table" % (dn, tier))
    # Step 8 art: a child naming its own texPath must have Graphic_Random PNGs there and its own
    # measured shadow box (the family's guess box is for the vanilla ShipChunk placeholder).
    # Sanity probe: the Scald's shipped art must resolve, or the lookup is blind.
    tex_roots = [os.path.join(SRC_ROOT, m, "Textures") for m in os.listdir(SRC_ROOT)]
    has_png = lambda tp: any(os.path.isdir(os.path.join(r, tp)) and
                             any(f.endswith(".png") for f in os.listdir(os.path.join(r, tp))) for r in tex_roots)
    if not has_png("Things/Building/Ruins/RUT_ScaldWreckHull"):
        bad.append("texture lookup cannot see the Scald hull art: the art check is blind")
    else:
        for dn, c in children.items():
            tp = c.findtext("graphicData/texPath")
            if not tp:
                continue
            if not has_png(tp):
                bad.append("%s texPath %s has no PNG in any mod's Textures" % (dn, tp))
            if c.find("graphicData/shadowData/volume") is None:
                bad.append("%s has its own art but no measured shadowData" % dn)
    used = {c.get("ParentName") for c in children.values()}
    for fam in FAMILIES_WITH_CHILDREN:
        if fam not in used:
            bad.append("family %s has no child anywhere (design §3a)" % fam)
    fam_xml = open(FAMILIES_XML, encoding="utf-8").read()
    if "<li>RM_WreckSurface</li>" not in fam_xml.split('Name="RM_WreckFamily_Hull"')[0]:
        bad.append("RM_WreckFamilyBase does not carry the RM_WreckSurface building tag (design §3b)")
    if '"RM_WreckSurface"' not in open(LICHEN_CS, encoding="utf-8").read():
        bad.append("MapComponent_WreckLichen does not read RM_WreckSurface: the Warscar lichen ignores our wrecks")
    for f, needle in ((os.path.join(HERE, "Source", "RM_CompSalvageLoot.cs"), "Props.noLoot"),
                      (os.path.join(HERE, "Source", "RM_WreckWeathering.cs"), "public bool noLoot")):
        if needle not in open(f, encoding="utf-8").read():
            bad.append("%s lacks %s (Picked's no-roll)" % (os.path.basename(f), needle))
    if "RM_WreckWeathering_Picked" not in NO_LOOT:
        bad.append("Picked weathering does not set noLoot (design §4: no loot roll)")


def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    root = ET.parse(os.path.join(HERE, "Defs", "ThingSetMakerDefs", "RM_SalvageLoot.xml")).getroot()
    got = [e.findtext("defName") for e in root if e.tag == "ThingSetMakerDef"]
    if sorted(got) != sorted(TABLES):
        bad.append("loot tables parsed %s, want %s" % (sorted(got), sorted(TABLES)))
    for e in root:
        if e.tag != "ThingSetMakerDef":
            continue
        opts = e.findall("root/options/li")
        if not opts:
            bad.append("%s has no options" % e.findtext("defName"))
        for li in opts:
            if not li.findall("thingSetMaker/fixedParams/filter/thingDefs/li"):
                bad.append("%s option has no thingDefs" % e.findtext("defName"))
    fams = _families(bad)
    weathers = _weatherings(bad)
    if not os.path.isfile(SCALD):
        bad.append("Scald wrecks file missing: %s" % SCALD)
    else:
        seen = {}
        for e in ET.parse(SCALD).getroot():
            dn = e.findtext("defName")
            if dn not in SCALD_WRECKS:
                continue
            parent = e.get("ParentName")
            if parent not in fams:
                bad.append("%s parent %s is not a wreck family" % (dn, parent))
                continue
            if [li for li in e.findall("comps/li") if li.get("Class") == COMP_CLASS]:
                bad.append("%s restates the salvage comp its family already carries (two rolls)" % dn)
            ext = [li for li in e.findall("modExtensions/li") if li.get("Class") == EXT_CLASS]
            if len(ext) != 1:
                bad.append("%s carries %d weathering extensions (want 1)" % (dn, len(ext)))
                continue
            w = ext[0].findtext("weathering")
            if w not in weathers:
                bad.append("%s names weathering %s, not defined" % (dn, w))
                continue
            for field in ("costList", "resourcesFractionWhenDeconstructed", "terrainAffordanceNeeded", "killedLeavings"):
                if e.find(field) is not None:
                    bad.append("%s restates %s; the family/weathering own it" % (dn, field))
            if not e.findtext("graphicData/texPath"):
                bad.append("%s has no texPath" % dn)
            tier, rare, cost, frac = fams[parent]
            tier = _shift(tier, weathers[w][1])
            seen[dn] = tier
            if tier != SCALD_WRECKS[dn]:
                bad.append("%s resolves to tier %s, want %s" % (dn, tier, SCALD_WRECKS[dn]))
            if "RM_SalvageLoot_%s" % tier not in got:
                bad.append("%s resolves to tier %s with no table" % (dn, tier))
            if rare > 0 and tier != "Scrap" and "RM_SalvageLoot_%s_Rare" % tier not in got:
                bad.append("%s has rareChance %s but no %s_Rare table" % (dn, rare, tier))
            eff = round(frac * weathers[w][0], 4)
            if dn in SCALD_SHIPPED and (cost, eff) != SCALD_SHIPPED[dn]:
                bad.append("%s resolves to cost %r x %s, shipped %r x %s (the reparent changed a yield)"
                           % (dn, cost, eff, SCALD_SHIPPED[dn][0], SCALD_SHIPPED[dn][1]))
        if set(seen) != set(SCALD_WRECKS):
            bad.append("Scald wrecks wired: %s, want %s" % (sorted(seen), sorted(SCALD_WRECKS)))
    _field_checks(bad, weathers)
    _planet_checks(bad, fams, weathers, got)
    _wreckfall_checks(bad)
    src_dir = os.path.join(HERE, "Source")
    proj = open(os.path.join(src_dir, "RM_Wreckage.csproj"), encoding="utf-8").read()
    for f in os.listdir(src_dir):
        if f.endswith(".cs") and ('Compile Include="%s"' % f) not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % f)
    mod = open(os.path.join(src_dir, "RM_WreckageMod.cs"), encoding="utf-8").read()
    for f in suite.toggles:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), mod):
            bad.append("toggle %s is not Scribed" % f)
    keyed = open(os.path.join(HERE, "Languages", "English", "Keyed", "RM_Wreckage.xml"), encoding="utf-8").read()
    used = set()
    for f in os.listdir(src_dir):
        if f.endswith(".cs"):
            used |= set(re.findall(r'"(RM_Wreckage_[A-Za-z_]+)"', open(os.path.join(src_dir, f), encoding="utf-8").read()))
    used |= {"RM_Wreckage_Tier_%s" % t for t in TIERS}
    for k in sorted(used):
        if "<%s>" % k not in keyed and not k.endswith("_"):
            bad.append("keyed string %s missing" % k)
    asm = os.path.join(HERE, "Assemblies", "RimMandrake.Wreckage.dll")
    if not os.path.isfile(asm):
        bad.append("no DLL at %s" % asm)
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
