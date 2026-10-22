"""validation.py -- modcheck suite for RimMandrake: The Rot (mandrake.rm.therot).

First north-star script (THE_ROT_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/TheRot.md (DRAFT).
The Rot biome (RM_TheRot): Sheen weather exposure, accelerated rot and warm living ground, live food preparations,
guardian groves, the spore-cloud incident, health sharing, the pale tree, plus an opt-in cross-biome mode; the whole Spore Kit
(plants, hediffs, recipes, drugs, buildings, research) ships as defs. No file is held from deploy.

CHAINS
  defs_resolve       every def parsed from the mod's own XML that actually DEPLOYS resolves live; a control name reads
                     notFound; no file of this mod is named in DEPLOY_HOLD.txt.
  settings_roundtrip every `public static` bool/float/string of RM_TheRotSettings: default / write / restore (numerics compared numerically).
  biome_wiring       RM_TheRot's animalDensity and plantDensity are > 0 and its workerClass names RM_BiomeWorker_TheRot.
  gut_mother         ROT_GUT_MOTHER_VAT_1: studied sac unlocks the research; a fed vat returns a bionic arm, rifle and parka
                     and consumes the body; an unfed vat does not progress; the starter keeps, trades, and a split makes one.
  navigator_log      ROT_NAVIGATOR_LOG_SITES_1: 4 pings read one log entry, 8 read two and reveal one salvage site; after the
                     carrier dies, pings do not move the log. Landing ping UNMEASURED (needs a gravship landing).
  unjoining          ROT_UNJOINING_DRAUGHT_1: the draught purges parasites + a symbiont (one husk, one scar, purge), only purges
                     a clean patient, and forces a metalhorror implant to emerge.
  dustveil           DUSTVEIL_FLIGHT_BUILD_A_MOTH_THAT_WALKED: MaxFlightTime > 0 live and the silk defs resolve; A2 is a
                     Pawn_FlightTracker STATE read (jawa/pawn_flight action=report) on a moth spawned while PAUSED and
                     destroyed before any tick, against a non-flier control; the flip-book cycle is UNMEASURED (flight is
                     seen only with the owner present).
  living_mat_root    ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD: a fed root spreads and eats, its room warms toward
                     min(outdoor+18, 21 C) and never past 21, a starved root dies back (RM_LivingMatRootProof).
  wound_link         ROT_WOUNDLINK_FIX_DROPPED_AT_THE_DOOR A2/A3: RM_Chittik (and RM_Durrok/RM_Mullgoth, when
                     mandrake.rsw.swbestiary loads) carry CompProperties_WoundLink live, a control reads notFound; a Cut
                     on one chittik's carapace mirrors to kin 2 cells away with woundLinkEnabled ON and not with it OFF.
  map_mechanics      the ten toggled mechanics: UNMEASURED, each naming what it needs (a generated RM_TheRot map, ticks, a game condition).

STATIC (also): ambrosyx_checks -- AMBROSYX_SOURCE_BUILD_DISH_BEFORE_SHROOM: some non-abstract plant of this mod has
                     plant.harvestedThingDef RM_AmbrosyxShroom, a positive yield, a texture folder that exists, a positive row
                     in RM_TheRot's wildPlants (element form) and the ambrosyxSpawn gate; `python3 validation.py --planted`
                     proves the bar goes red on three planted defects (harvest renamed, row removed, gate removed).
STATIC (also): dustveil_checks -- DUSTVEIL_FLIGHT_BUILD_A_MOTH_THAT_WALKED: RM_Dustveil flies (MaxFlightTime > 0,
                     FlightCooldown, flightSpeedFactor, a takeoff chance), no Spastic node, a flip-book prefix only with
                     every frame on disk, fungus-grown text with no laboratory/donor origin, shearing still yields
                     RM_MothSilk (a Fabric); --planted also turns it red on four planted defects.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game. Nothing here has been run live.
MOCK:   `python3 validation.py --mock` -> runs wound_link, dustveil and living_mat_root against a fake game, clean and
        with 12 planted defects (MOCK_EXPECT); each defect must turn ITS row FAIL, or UNMEASURED when it blinds the
        instrument (control reads present, clock running, wrong map).
"""
import fnmatch
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = "TheRot"
SETTINGS = "RimMandrake.TheRot.RM_TheRotSettings"
BIOME = "RM_TheRot"
WORKER = "RM_BiomeWorker_TheRot"
CONTROL_ABSENT = "ThingDef/TheRotNoSuchDef_ZZ"
LINK_DAMAGE, LINK_AMOUNT, LINK_PART = "Cut", 14, "RM_CarapaceTheRot"   # wound_link: 14 > the 8 gate; carapace 60 HP
_FIELD = re.compile(r"public\s+static\s+(bool|int|float|string)\s+(\w+)\s*=\s*([^;]+);")
_HOLD_FILE = os.path.join(HERE, "..", "..", "DEPLOY_HOLD.txt")


def held_globs():
    """Globs from src/DEPLOY_HOLD.txt that name this mod (relative to custom_patches/, '*' crosses '/')."""
    out = []
    if not os.path.isfile(_HOLD_FILE):
        return out
    for line in open(_HOLD_FILE, encoding="utf-8"):
        g = line.split("#", 1)[0].strip()
        if g.startswith(MOD + "/"):
            out.append(g)
    return out


HELD = held_globs()


def is_held(rel):
    return any(fnmatch.fnmatchcase(MOD + "/" + rel.replace(os.sep, "/"), g) for g in HELD)


def parse_defs():
    """([(DefType, defName)] deployed, [(DefType, defName, file)] held) from every non-abstract top-level def under Defs/."""
    deployed, held = [], []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, HERE)
            for el in ET.parse(full).getroot():
                nm = el.find("defName") if isinstance(el.tag, str) else None
                if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                    (held if is_held(rel) else deployed).append((el.tag, nm.text.strip(), rel) if is_held(rel) else (el.tag, nm.text.strip()))
    return sorted(set(deployed)), sorted(set(held))


SHIPPED, HELD_DEFS = parse_defs()


def settings_fields():
    """{name: type} for every scalar `public static` field of the settings class, read from the C# ({} when none)."""
    src = open(os.path.join(HERE, "Source", "RM_TheRotMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_TheRotSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if len(SHIPPED) + len(HELD_DEFS) < 40:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % (len(SHIPPED) + len(HELD_DEFS))]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    src = open(os.path.join(HERE, "Source", "RM_TheRotMod.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    # ROT_MOD_SETTINGS_WIRING_1: every field needs a READER outside its own Scribe line and the settings UI
    # (declaration + one reader = 2 mentions).
    # ROT_WOUND_SHARING_WIRING_1: five bodies carry the wound-link / kin-mending wiring. Since the 2026-10-18 donor
    # retirement they are our RM_ ports: chittik, gromma, rennok carry it NATIVELY in Defs/Fauna; mullgoth and durrok
    # (defs in mandrake.rsw.swbestiary) get it by an xpath-guarded patch. RED 2026-10-22 for the reported reason: the
    # retirement deleted the AA_ FindMod block and the wiring reached only RM_Agaripod/RM_Agaripawn (chittik, durrok and
    # mullgoth silently lost the promised sharing; the toggle's strip list still named the AA_ bodies).
    fauna = ""
    for fn in ("RM_Chittik.xml", "RM_AgariPorts.xml"):
        fauna += open(os.path.join(HERE, "Defs", "Fauna", fn), encoding="utf-8").read()
    for body in ("RM_Chittik", "RM_Agaripod", "RM_Agaripawn"):
        m = re.search(r"<ThingDef[^>]*>\s*<defName>%s</defName>(.*?)</ThingDef>" % body, fauna, re.S)
        if not m or "CompProperties_WoundLink" not in m.group(1) or "<tag>RotNetwork</tag>" not in m.group(1):
            bad.append("%s ThingDef does not carry a native wound link with the RotNetwork tag" % body)
    ws = open(os.path.join(HERE, "Patches", "RotSpecies_WoundSharing.xml"), encoding="utf-8").read()
    for body in ("RM_Durrok", "RM_Mullgoth"):
        if 'defName="%s"' % body not in ws:
            bad.append("wound-sharing patch does not target %s" % body)
    if ws.count("<tag>RotNetwork</tag>") < 2 or ws.count("CompProperties_WoundLink") < 4:
        bad.append("wound-sharing patch lacks the shared RotNetwork tag or a wound link per patched body")
    if re.search(r"<Operation[^>]*MayRequire", ws):
        bad.append("wound-sharing patch must never use a top-level MayRequire (ignored by 1.6)")
    if ws.count("<hediff>RM_KinMendingNetwork</hediff>") != 4:
        bad.append("exactly the two mending bodies (mullgoth, durrok) carry the kin-mending hediff")
    # ROT_NORTHSTAR_BARS_DRAFT bar 1 (kin mending): the live threshold is derived from these defaults, so they are pinned here.
    cb = os.path.join(HERE, "..", "CreatureBehaviors", "Source")
    kp = open(os.path.join(cb, "CompProperties_KinMending.cs"), encoding="utf-8").read()
    ke = open(os.path.join(cb, "RM_WoundLinkExtension.cs"), encoding="utf-8").read()
    for pat, what in ((r"int\s+tickIntervalTicks\s*=\s*2500\b", "cycle 2500 ticks"),
                      (r"float\s+healPerDayPerBodySize\s*=\s*3f\b", "heal 3 per day per body size")):
        if not re.search(pat, kp):
            bad.append("kin mending default changed (%s): bar 1's live threshold in rot_northstar_bars_draft must be re-derived" % what)
    for pat, what in ((r"float\s+radius\s*=\s*12f\b", "radius 12"), (r"int\s+kinMendingMinKin\s*=\s*2\b", "min kin 2")):
        if not re.search(pat, ke):
            bad.append("wound-link default changed (%s): bar 1's live threshold in rot_northstar_bars_draft must be re-derived" % what)
    hs = re.search(r"HealthSharingBodies\s*=\s*\{([^}]*)\}", src)
    hs_names = set(re.findall(r'"(\w+)"', hs.group(1))) if hs else set()
    if hs_names != {"RM_Chittik", "RM_Agaripod", "RM_Agaripawn", "RM_Durrok", "RM_Mullgoth"}:
        bad.append("Health sharing toggle strips %s, not the five RM_ bodies" % sorted(hs_names))
    reader_text = re.sub(r"Scribe_Values\.Look\([^\n]*\n", "", src)
    ui_start = reader_text.index("public void DoWindowContents")
    ui_end = reader_text.index("public class RM_TheRotFront") if "public class RM_TheRotFront" in reader_text else reader_text.index("static class RM_TheRotFront")
    reader_text = reader_text[:ui_start] + reader_text[ui_end:]
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):   # readers may live in the mechanism's own file
        if fn.endswith(".cs") and fn != "RM_TheRotMod.cs":
            reader_text += open(os.path.join(HERE, "Source", fn), encoding="utf-8").read()
    for n in fields:
        if len(re.findall(r"\b%s\b" % n, reader_text)) < 2:
            bad.append("settings field %s has a control but no reader (moves and does nothing)" % n)
    # ROT_SPORE_ALLERGY_PORT_1: the free Rot and Contagion name OUR two incidents and no donor disease; the four defs ship in EH.
    eh = os.path.join(HERE, "..", "EnvironmentalHazards", "Defs")
    ehtxt = "".join(open(os.path.join(dp, f), encoding="utf-8").read()
                    for dp, _d, fs in os.walk(eh) for f in fs if f.endswith(".xml"))
    for dn in ("RM_SporeAllergy", "RM_AnimalSporeAllergy", "RM_Disease_SporeAllergy", "RM_Disease_AnimalSporeAllergy"):
        if "<defName>%s</defName>" % dn not in ehtxt:
            bad.append("%s is not shipped by EnvironmentalHazards" % dn)
    for rel in (("Defs", "BiomeDefs", "RM_TheRot_Biome.xml"), ("..", "Contagion", "Defs", "BiomeDefs", "RM_Contagion.xml")):
        bt = re.sub(r"<!--.*?-->", "", open(os.path.join(HERE, *rel), encoding="utf-8").read(), flags=re.S)
        if "AB_Disease" in bt or "<diseaseInc>RM_Disease_SporeAllergy</diseaseInc>" not in bt \
                or "<diseaseInc>RM_Disease_AnimalSporeAllergy</diseaseInc>" not in bt:
            bad.append("%s diseases must name the RM_ spore-allergy pair and no AB_ def" % rel[-1])
    if "RM_KitFronts" not in src:
        bad.append("RM_TheRotFront does not register into RM_KitFronts")
    proj = open(os.path.join(HERE, "Source", "RM_TheRot.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    kinds = set(ty for ty, _n in SHIPPED) | set(h[0] for h in HELD_DEFS)
    for need in ("BiomeDef", "ThingDef", "HediffDef", "RecipeDef", "GameConditionDef", "TerrainDef", "WeatherDef"):
        if need not in kinds:
            bad.append("no %s parsed" % need)
    if not any(n == BIOME for _t, n in SHIPPED) and not any(h[1] == BIOME for h in HELD_DEFS):
        bad.append("BiomeDef %s missing" % BIOME)
    biome = ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheRot_Biome.xml")).getroot()
    if not float(biome.findtext(".//animalDensity") or 0) > 0:
        bad.append("animalDensity is 0: the roster is dead content")
    if "class " + WORKER not in open(os.path.join(HERE, "Source", "RM_BiomeWorker_TheRot.cs"), encoding="utf-8").read():
        bad.append("biome worker class %s not found" % WORKER)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", MOD + ".md")):
        bad.append("walk missing")
    hw = open(os.path.join(HERE, "Defs", "Fauna", "RM_Hwelgrue.xml"), encoding="utf-8").read()
    if "CompProperties_RM_GutSwallow" not in hw or "CompProperties_Devourer" in hw:
        bad.append("RM_Hwelgrue must carry RM_CompGutSwallow and never CompDevourer (ROT_STILL_ALIVE_SWALLOW_1)")
    if "<defName>RM_GutKnocking</defName>" not in hw:
        bad.append("SoundDef RM_GutKnocking missing")
    gp = open(os.path.join(HERE, "Patches", "RM_SwallowedCore_Gravship.xml"), encoding="utf-8").read()
    if "RM_StatPart_SwallowedCore" not in gp or "<li>RM_SwallowedDriveCore</li>" not in gp:
        bad.append("the gravship patch must link the core to GravEngine and add the range stat part")
    if "CompProperties_RM_SwallowedCore" not in hw:
        bad.append("RM_Hwelgrue must carry RM_CompSwallowedCore (ROT_SWALLOWED_NAVIGATOR_1)")
    gm = open(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_GutMother.xml"), encoding="utf-8").read()
    for need in ("RM_GutMotherSac", "RM_GutMotherVat", "RM_GutMotherStarter", "RM_GutMotherCulture", "RM_SplitGutMother",
                 "<requiredAnalyzed>", "CompProperties_CompAnalyzableUnlockResearch", "RM_DoBillsGutMother"):
        if need not in gm:
            bad.append("RM_GutMother.xml lacks %s (ROT_GUT_MOTHER_VAT_1)" % need)
    starter = gm.split("<defName>RM_GutMotherStarter</defName>", 1)[1].split("</ThingDef>", 1)[0]
    if "CompProperties_Rottable" in starter or "RM_LivePrepExtension" in starter:
        bad.append("RM_GutMotherStarter must never rot or lose viability (ROT_GUT_MOTHER_VAT_1 ruled exception)")
    if "RM_GutMother.DropSac" not in open(os.path.join(HERE, "Source", "RM_Hwelgrue.cs"), encoding="utf-8").read():
        bad.append("a dead hwelgrue must drop the gut-mother sac (RM_CompGutDigest.Notify_Killed)")
    nl = open(os.path.join(HERE, "Defs", "Misc", "RM_NavigatorLog.xml"), encoding="utf-8").read()
    n_entries = nl.split("<entries>", 1)[1].split("</entries>", 1)[0].count("<li>") if "<entries>" in nl else 0
    if n_entries != 8 or "RM_NavigatorSalvageSite" not in nl:
        bad.append("RM_NavigatorLog must carry 8 entries and the RM_NavigatorSalvageSite quest (ROT_NAVIGATOR_LOG_SITES_1), found %d" % n_entries)
    # ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD: the portable mat root (owner ruling 2026-10-22).
    mr = re.sub(r"<!--.*?-->", "", open(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_LivingMatRoot.xml"),
                                          encoding="utf-8").read(), flags=re.S)
    for need in ("<defName>RM_LivingMatRoot</defName>", "CompProperties_RM_LivingMatRoot", "CompProperties_Refuelable",
                 "<li>FoodRaw</li>", "<consumeFuelOnlyWhenUsed>true</consumeFuelOnlyWhenUsed>", "<tickerType>Rare</tickerType>",
                 "<maxRoomTemperature>21</maxRoomTemperature>", "<matTerrain>RM_MycelialMatting</matTerrain>",
                 "<minifiedDef>MinifiedThing</minifiedDef>"):
        if need not in mr:
            bad.append("RM_LivingMatRoot.xml lacks %s (ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD)" % need)
    if "<designationCategory>" in mr or "<costList>" in mr or "Substructure" in mr:
        bad.append("RM_LivingMatRoot must be a reward (no designator/cost) and must not require substructure ('make it work anywhere')")
    rot_warm = biome.find(".//li[@Class='RimMandrake.EnvironmentalHazards.RM_WarmGroundExtension']/warmTerrains")
    root_warm = ET.fromstring(mr.encode("utf-8")).find(".//warmTerrains")
    if rot_warm is None or root_warm is None or sorted(e.text for e in rot_warm) != sorted(e.text for e in root_warm):
        bad.append("RM_LivingMatRoot's warmTerrains must equal RM_TheRot's RM_WarmGroundExtension list (same mat)")
    lm = open(os.path.join(HERE, "Source", "RM_LivingMatRoot.cs"), encoding="utf-8").read()
    for need in ("RM_TheRotFront.IsRotBiome", "ThermalPowerDivisor = 36f", "RemoveTopLayer", "BiomeHeatsMat"):
        if need not in lm:
            bad.append("RM_LivingMatRoot.cs lacks %s" % need)
    eh = open(os.path.join(HERE, "..", "EnvironmentalHazards", "Source", "RM_MapComponent_WarmGround.cs"), encoding="utf-8").read()
    if "ThermalPowerDivisor = 36f" not in eh:
        bad.append("RM_MapComponent_WarmGround's ramp moved: re-derive RM_LivingMatRoot's copy of ThermalPowerDivisor")
    core = open(os.path.join(HERE, "Source", "RM_SwallowedCore.cs"), encoding="utf-8").read()
    for need in ("RM_NavigatorLog.Notify_Ping", "RM_NavigatorLog.Notify_CarrierDied", "engineSeen"):
        if need not in core:
            bad.append("RM_SwallowedCore.cs lacks %s (ROT_NAVIGATOR_LOG_SITES_1)" % need)
    uj = open(os.path.join(HERE, "Defs", "Drugs", "RM_UnjoiningDraught.xml"), encoding="utf-8").read()
    for need in ("RM_UnjoiningPurge", "RM_SymbiontHusk", "RM_Make_UnjoiningDraught", "IngestionOutcomeDoer_RM_Unjoining",
                 "CompProperties_Drug", "<li>MuscleParasites</li>", "<li>GutWorms</li>", "<li>RM_SheenSymbiosis</li>"):
        if need not in uj:
            bad.append("RM_UnjoiningDraught.xml lacks %s (ROT_UNJOINING_DRAUGHT_1)" % need)
    bad += cast_checks()
    bad += ambrosyx_checks()
    bad += dustveil_checks()
    # Phase 0: RM_SwarmlingImplantation's donor comps (AlphaBehavioursAndEvents TurnWhenDead + RemoveFromMechsAndGhouls)
    # are ours now. A donor Class here fails def load with the donor off and takes the hediff (and the Chittik bite) with it.
    ck = open(os.path.join(HERE, "Defs", "Fauna", "RM_Chittik.xml"), encoding="utf-8").read()
    if "AlphaBehavioursAndEvents" in ck:
        bad.append("RM_Chittik.xml still names an AlphaBehavioursAndEvents class")
    for need in ("RimMandrake.TheRot.RM_HediffCompProperties_SpawnOnDeath", "<pawnKind>RM_Chittik</pawnKind>",
                 "RimMandrake.TheRot.RM_HediffCompProperties_NotOnMechsOrGhouls"):
        if need not in ck:
            bad.append("RM_SwarmlingImplantation lacks %s" % need)
    return bad


AMBROSYX_PRODUCT = "RM_AmbrosyxShroom"


def ambrosyx_checks(flora_text=None, biome_text=None, mod_cs=None):
    """The shroom the slime pit's dish needs must have a wild source (AMBROSYX_SOURCE_BUILD_DISH_BEFORE_SHROOM).
    Texts may be passed in to plant a defect; by default every Defs/ThingDefs_Plants file is read."""
    bad = []
    plants_dir = os.path.join(HERE, "Defs", "ThingDefs_Plants")
    texts = [flora_text] if flora_text is not None else [
        open(os.path.join(plants_dir, f), encoding="utf-8").read() for f in sorted(os.listdir(plants_dir)) if f.endswith(".xml")]
    sources = []
    for txt in texts:
        for el in ET.fromstring(txt):
            if el.tag == "ThingDef" and el.get("Abstract", "").lower() != "true" \
                    and (el.findtext("plant/harvestedThingDef") or "").strip() == AMBROSYX_PRODUCT:
                sources.append(el)
    if not sources:
        return ["no plant of this mod harvests %s: the slime pit's ambrosyx dish can never be cooked" % AMBROSYX_PRODUCT]
    biome = ET.fromstring(biome_text if biome_text is not None else
                          open(os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheRot_Biome.xml"), encoding="utf-8").read())
    wild = dict((e.tag, e.text) for e in biome.find(".//wildPlants"))
    cs = mod_cs if mod_cs is not None else open(os.path.join(HERE, "Source", "RM_TheRotMod.cs"), encoding="utf-8").read()
    for el in sources:
        n = el.findtext("defName")
        if not float(el.findtext("plant/harvestYield") or 0) > 0:
            bad.append("%s harvests %s with no yield" % (n, AMBROSYX_PRODUCT))
        tp = el.findtext("graphicData/texPath") or ""
        if not os.path.isdir(os.path.join(HERE, "Textures", tp)):
            bad.append("%s texPath %s has no texture folder in this mod" % (n, tp))
        if not float(wild.get(n) or 0) > 0:
            bad.append("%s is not a positive wildPlants row of %s: nothing ever spawns it" % (n, BIOME))
        if not re.search(r'ambrosyxSpawn\)\s*\{\s*rot\.wildPlants\.RemoveAll\([^;]*"%s"' % n, cs):
            bad.append("%s's wild row is not gated by RM_TheRotSettings.ambrosyxSpawn" % n)
    return bad


def planted_ambrosyx():
    """Each planted defect must turn ambrosyx_checks red; the clean tree must be green."""
    flora = open(os.path.join(HERE, "Defs", "ThingDefs_Plants", "RM_RotSporeKit_Flora.xml"), encoding="utf-8").read()
    biome = open(os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheRot_Biome.xml"), encoding="utf-8").read()
    cs = open(os.path.join(HERE, "Source", "RM_TheRotMod.cs"), encoding="utf-8").read()
    out = [("clean", not ambrosyx_checks(flora, biome, cs))]
    out.append(("harvest renamed", bool(ambrosyx_checks(
        flora.replace("<harvestedThingDef>RM_AmbrosyxShroom<", "<harvestedThingDef>RawFungus<"), biome, cs))))
    out.append(("wild row removed", bool(ambrosyx_checks(
        flora, re.sub(r"\s*<RM_AmbrosyxFungus>[^<]*</RM_AmbrosyxFungus>", "", biome), cs))))
    out.append(("gate removed", bool(ambrosyx_checks(flora, biome, cs.replace('"RM_AmbrosyxFungus"', '"RM_Nothing"')))))
    return out


# ROT_RM_CAST_MIGRATION_1: the ten ratified residents are owned RM_ defs, wired inline, hybrid, textured.
CAST = ["Thozzik", "ThozzikColony", "ThozzikQueen", "ThozzikColonyQueen",
        "Illoth", "Brullith", "Brogg", "Grellik", "Skerrith"]
_BANNED = re.compile(r"wasp|hornet|moth|camel|llama|genetics|experiment|Force", re.I)
# art owed: none (thozzik and illoth south frames landed from artpipe 2026-10-03)
ART_OWED = set()


def cast_checks():
    bad = []
    fauna = os.path.join(HERE, "Defs", "Fauna")
    if not os.path.isdir(fauna):
        return ["Defs/Fauna missing: the ten RM_ residents are not shipped"]
    races, kinds = {}, {}
    for fn in os.listdir(fauna):
        for el in ET.parse(os.path.join(fauna, fn)).getroot():
            nm = el.findtext("defName") if isinstance(el.tag, str) else None
            if el.tag == "ThingDef" and nm:
                races[nm] = el
            elif el.tag == "PawnKindDef" and nm:
                kinds[nm] = el
    if len(races) < 20:
        bad.append("only %d fauna ThingDefs parsed (sanity probe failed)" % len(races))
    biome = ET.parse(os.path.join(HERE, "Defs", "BiomeDefs", "RM_TheRot_Biome.xml")).getroot()
    roster = set(e.tag for e in biome.find(".//wildAnimals"))
    for c in CAST:
        n = "RM_" + c
        if n not in races or n not in kinds:
            bad.append("%s: ThingDef/PawnKindDef missing" % n)
            continue
        if n not in roster:
            bad.append("%s not in RM_TheRot wildAnimals" % n)
        desc = (races[n].findtext("description") or "") + " " + (races[n].findtext("label") or "")
        if _BANNED.search(desc):
            bad.append("%s description names a banned franchise/lab word" % n)
        if c in ("Thozzik", "Illoth", "Brogg") and not re.search(r"fung|mycel|spore", desc):
            bad.append("%s description is not a fungus hybrid" % n)
        for tp in set(e.text for e in kinds[n].iter("texPath") if e.text and e.text.startswith("RM_TheRot/")):
            for fc in ("south", "east", "north"):
                rel = "%s_%s" % (tp, fc)
                tail = "/".join(rel.split("/")[-2:])
                if tail in ART_OWED:
                    continue
                if not os.path.isfile(os.path.join(HERE, "Textures", rel + ".png")) and "essicated" not in tp:
                    bad.append("%s: texture %s.png missing" % (n, rel))
    il = races.get("RM_Illoth")
    if il is not None:
        if float(il.findtext("statBases/MaxFlightTime") or 0) <= 0:
            bad.append("RM_Illoth cannot fly: MaxFlightTime is not > 0")
        if il.findtext("race/canFlyIntoMap") != "true":
            bad.append("RM_Illoth race lacks canFlyIntoMap")
    for fn in os.listdir(fauna):
        if "RSW_" in open(os.path.join(fauna, fn), encoding="utf-8").read():
            bad.append("Defs/Fauna/%s still names an RSW_ def (free mod must stand alone)" % fn)
    patch = os.path.join(HERE, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "WildAnimals_TheRot.xml")
    if os.path.isfile(patch):
        txt = open(patch, encoding="utf-8").read()
        for retired in ("RSW_PustuleHornet", "RSW_SmogMoth", "RSW_Thrumbungus", "RSW_Yooka", "RSW_FungalWeevil", "RSW_FungalMantis"):
            if retired in re.sub(r"<!--.*?-->", "", txt, flags=re.S):
                bad.append("campaign patch still adds %s to RM_TheRot" % retired)
        for op in ET.parse(patch).getroot().iter("Operation"):
            if op.get("MayRequire"):
                bad.append("campaign patch has a top-level <Operation MayRequire> (inert in 1.6)")
        if "RSW_ShiroTrap" not in txt or "Snoruuk" not in txt:
            bad.append("campaign patch lost RSW_ShiroTrap or Snoruuk")
    return bad


# DUSTVEIL_FLIGHT_BUILD_A_MOTH_THAT_WALKED (owner, by question card 2026-10-22, Rot Q5 option 1): the dustveil really
# flies (the MaxFlightTime STAT; CanEverFly reads it), is a fungus-grown Rot hybrid, carries no laboratory/waste-disposal
# origin, and still sheds moth silk on shearing. Its flip-book frames are owed art: the prefix may be set only once
# every frame exists, and never a Spastic wing node.
DUSTVEIL_FILE = os.path.join(HERE, "Defs", "Fauna", "RM_Dustveil.xml")
_DUSTVEIL_ORIGIN = re.compile(r"laborator|waste|engineer|genetic|experiment|project|bred long ago|angel moth|Feroxiious", re.I)


def dustveil_checks(text=None):
    bad = []
    root = ET.fromstring(text if text is not None else open(DUSTVEIL_FILE, encoding="utf-8").read())
    defs = {(e.tag, e.findtext("defName")): e for e in root if isinstance(e.tag, str)}
    th, kind = defs.get(("ThingDef", "RM_Dustveil")), defs.get(("PawnKindDef", "RM_Dustveil"))
    if th is None or kind is None:
        return ["RM_Dustveil ThingDef/PawnKindDef missing from Defs/Fauna/RM_Dustveil.xml"]
    try:
        mft = float(th.findtext("statBases/MaxFlightTime"))
    except (TypeError, ValueError):
        mft = 0.0
    if not mft > 0:
        bad.append("RM_Dustveil cannot fly: MaxFlightTime is not > 0 (CanEverFly reads the stat)")
    if th.find("statBases/FlightCooldown") is None or not float(th.findtext("race/flightSpeedFactor") or 0) > 0:
        bad.append("RM_Dustveil needs FlightCooldown and race flightSpeedFactor")
    if not float(th.findtext("race/flightStartChanceOnJobStart") or 0) > 0:
        bad.append("RM_Dustveil race flightStartChanceOnJobStart is not > 0: it would never take off")
    body = re.sub(r"<!--.*?-->", "", ET.tostring(root, encoding="unicode"), flags=re.S)
    if "Spastic" in body:
        bad.append("RM_Dustveil file carries a Spastic node: flight is a whole-body flip-book, never a wing render-tree")
    prefix = kind.findtext("flyingAnimationFramePathPrefix")
    if prefix:
        n = int(kind.findtext("flyingAnimationFrameCount") or 0)
        if n < 1:
            bad.append("RM_Dustveil flip-book prefix set with no flyingAnimationFrameCount")
        for i in range(1, n + 1):
            for fc in ("east", "north", "south"):
                if not os.path.isfile(os.path.join(HERE, "Textures", "%s%d_%s.png" % (prefix, i, fc))):
                    bad.append("RM_Dustveil flip-book frame %s%d_%s.png missing (every flight would draw pink)" % (prefix, i, fc))
    for key, e in defs.items():
        words = " ".join((e.findtext(f) or "") for f in ("label", "description"))
        if _DUSTVEIL_ORIGIN.search(words):
            bad.append("%s %s text keeps a donor/laboratory origin or name: %r" % (key[0], key[1], _DUSTVEIL_ORIGIN.search(words).group(0)))
    if not re.search(r"fung|mycel|spore", th.findtext("description") or ""):
        bad.append("RM_Dustveil description is not a fungus-grown hybrid")
    prod = [c for c in th.iter("li") if (c.get("Class") or "").endswith("CompProperties_AnimalProduct")]
    if not prod or prod[0].findtext("resourceDef") != "RM_MothSilk" or not int(prod[0].findtext("resourceAmount") or 0) > 0:
        bad.append("RM_Dustveil lost its shearing: no AnimalProduct comp yielding RM_MothSilk")
    silk = defs.get(("ThingDef", "RM_MothSilk"))
    if silk is None or "Fabric" not in [c.text for c in silk.iter("li")]:
        bad.append("RM_MothSilk ThingDef missing or no longer a Fabric stuff")
    return bad


def planted_dustveil():
    """[(name, red?)]: each planted defect must turn dustveil_checks red; 'clean' must be green."""
    txt = open(DUSTVEIL_FILE, encoding="utf-8").read()
    out = [("dv clean", not dustveil_checks(txt))]
    out.append(("dv grounded", bool(dustveil_checks(re.sub(r"<MaxFlightTime>[^<]*<", "<MaxFlightTime>0<", txt)))))
    out.append(("dv lab origin", bool(dustveil_checks(txt.replace("A broad-winged moth of the Rot,",
                                                                 "A moth bred in a laboratory,", 1)))))
    out.append(("dv no silk", bool(dustveil_checks(txt.replace("<resourceDef>RM_MothSilk<", "<resourceDef>Cloth<")))))
    out.append(("dv pink flip", bool(dustveil_checks(txt.replace(
        "<alternateGraphicChance>", "<flyingAnimationFramePathPrefix>RotSpecies/AngelMoth/Flying/NoSuch_Flying_"
        "</flyingAnimationFramePathPrefix><flyingAnimationFrameCount>5</flyingAnimationFrameCount><alternateGraphicChance>", 1)))))
    return out


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite(MOD)
    suite.toggles = sorted(settings_fields())

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _unmeasured(t, why):
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _raw(t, action, field, value=None):
        if value is not None:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field, value=str(value))
        else:
            r = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action=action, field=field)
        return r if isinstance(r, dict) else {}

    def _same(ty, a, b):
        if ty == "bool":
            return str(a).lower() == str(b).lower()
        if ty == "string":
            if a is None and str(b) == "":
                return True
            return str(a) == str(b)
        try:
            return abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))
        except (TypeError, ValueError):
            return False

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_deployed_def_resolves", beyond_toggle=True):
            names = ["%s/%s" % p for p in SHIPPED]
            missing, ok = [], 0
            for i in range(0, len(names), 40):      # batches: a long defs string risks the 30 s reply timeout
                chunk = names[i:i + 40]
                r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields="defName", limit=60)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                missing.extend(r.get("notFound") or [])
                ok += int(r.get("foundCount", 0))
            if _live(t) and (missing or ok != len(names)):
                raise ExpectationFailed("%d of %d defs resolved; notFound=%r" % (ok, len(names), missing[:8]))


    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        with t.component("settings_probe_finds_fields", beyond_toggle=True):
            if len(settings_fields()) < 1:
                raise ExpectationFailed("settings probe found no field (blind regex)")
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None and ty == "string":
                    old = ""               # an empty-string setting reads back null (2026-10-07); restore writes ""
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
                elif ty == "string":
                    new = "zz_probe" if str(old) != "zz_probe" else "zz_probe2"
                elif ty == "int":
                    new = str(int(float(old)) + 1)       # an Int32 field refuses "25.0" (LIVE 2026-10-03)
                else:
                    new = str(float(old) + 1.0)
                try:
                    if not _raw(t, "set", field, new).get("success"):
                        raise ExpectationFailed("%s: set failed" % field)
                    back = _raw(t, "get", field).get("value")
                    if not _same(ty, back, new):
                        raise ExpectationFailed("%s: wrote %s, read %r" % (field, new, back))
                finally:
                    _raw(t, "set", field, old)
                back = _raw(t, "get", field).get("value")
                if not _same(ty, back, old):
                    raise ExpectationFailed("%s did not restore to %r (read %r)" % (field, old, back))

    @suite.chain("biome_wiring")
    def biome_wiring(t):
        with t.component("animal_and_plant_density_positive", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + BIOME, fields="animalDensity,plantDensity,workerClass", limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read %s: %r" % (BIOME, r))
                f = rows[0].get("fields") or {}
                try:
                    ad, pd = float(f.get("animalDensity")), float(f.get("plantDensity"))
                except (TypeError, ValueError):
                    _unmeasured(t, "get_defs did not return numeric densities: %r" % (f,))
                    return
                if not ad > 0:
                    raise ExpectationFailed("animalDensity %s: the roster would never spawn" % ad)
                if not pd > 0:
                    raise ExpectationFailed("plantDensity %s: the flora would never spawn" % pd)
        with t.component("biome_worker_class_loaded", beyond_toggle=True):
            # jawa/get_defs cannot serialise System.Type fields (LIVE 2026-10-03: '(no such field)'), so the
            # worker is read by static_call on the live BiomeDef instead.
            r = t.bridge_call("jawa/static_call", type="RimMandrake.TheRot.RM_TheRotBiomeProof", method="ProofWorker")
            if _live(t):
                wc = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
                if not wc.startswith("WORKER "):
                    _unmeasured(t, "static_call ProofWorker gave no answer: %r" % (r,))
                    return
                if WORKER not in wc.split("|")[0] or ("instance " + WORKER) not in wc:
                    raise ExpectationFailed("workerClass reads %r, expected %s" % (wc, WORKER))

    @suite.chain("dustveil")
    def dustveil(t):
        # DUSTVEIL_FLIGHT_BUILD_A_MOTH_THAT_WALKED. State reads only: flight is NEVER driven or filmed unattended
        # (owner, said three times 2026-09-25); the visual flip-book check is a joint session with him.
        with t.component("flight_stat_live", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Dustveil", fields="statBases", deep=True, limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read ThingDef/RM_Dustveil: %r" % (r,))
                sb = (rows[0].get("fields") or {}).get("statBases")
                live = None
                if isinstance(sb, list):
                    for m in sb:
                        if isinstance(m, dict) and "MaxFlightTime" in str(m.get("stat")):
                            live = m.get("value")
                elif isinstance(sb, dict):
                    live = sb.get("MaxFlightTime")
                if live is None:
                    _unmeasured(t, "statBases not serialised with MaxFlightTime: %s" % str(sb)[:120])
                    return
                if not float(live) > 0:
                    raise ExpectationFailed("RM_Dustveil MaxFlightTime %r live: CanEverFly is false" % live)
        with t.component("silk_defs_live", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_MothSilk;ThingDef/RM_Dustveil", fields="defName", limit=4)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False or int(r.get("foundCount", 0)) != 2:
                    raise ExpectationFailed("RM_MothSilk / RM_Dustveil do not both resolve: %r" % (r,))
        with t.component("flight_tracker_state_read", beyond_toggle=True):
            # DUSTVEIL A2. `jawa/pawn_flight action=report` is READ-ONLY (JawaBenchFlightTools.cs): Pawn_FlightTracker
            # CanEverFly / Flying / flightState, no write. The moth is spawned with the game PAUSED, read and destroyed
            # before any tick; a non-flier (RM_Chittik) is the control that proves the instrument can say false.
            # Owner ruling: no flight is started, no tick runs with the moth spawned, no screenshot is taken.
            if _live(t):
                _flight_state_read(t)
        with t.component("flip_book_frames_cycle", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "frames Dustveil_Flying_1..5 are queued in artpipe; the cycle is judged live only WITH the owner")

    def _ticks(t):
        r = t.session.call("rimworld/get_game_info")
        try:
            return int((r or {}).get("ticksGame"))
        except (TypeError, ValueError):
            return None

    def _spawn_one(t, kind, x, z):
        r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction="none", count=1)
        pid = ((((r or {}).get("pawns") or [{}])[0]) or {}).get("id") if isinstance(r, dict) else None
        if pid and hasattr(t.session, "track"):
            t.session.track("pawn", pid, x=x, z=z)
        return pid

    def _remove(t, pid):
        """Vanish one pawn (no death, no corpse). destroy_batch NEVER removes pawns (JawaBenchTerrainTools.cs)."""
        r = t.session.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
        return isinstance(r, dict) and r.get("success") is not False and r.get("destroyedAfter", True) is not False

    def _flight_state_read(t):
        t.session.call("rimworld/pause_game", pause=True)
        x, z = t.anchor
        t0 = _ticks(t)
        if t0 is None or _ticks(t) != t0:
            _unmeasured(t, "the game is not provably paused before the spawn (ticksGame %r, then moving or unreadable); "
                           "the moth was NOT spawned (owner ruling: no tick with it on the map)" % (t0,))
            return
        moth = ctrl = None
        rows = {}
        gone = True
        try:
            moth = _spawn_one(t, "RM_Dustveil", x, z)
            ctrl = _spawn_one(t, "RM_Chittik", x + 3, z)
            for pid in (moth, ctrl):
                if pid:
                    r = t.session.call("jawa/pawn_flight", action="report", pawn=pid)
                    got = ((r or {}).get("pawns") or []) if isinstance(r, dict) else []
                    rows[pid] = got[0] if got and isinstance(got[0], dict) else None
        finally:
            for pid in (moth, ctrl):
                if pid:
                    gone = _remove(t, pid) and gone
        t1 = _ticks(t)
        if t0 is None or t1 is None:
            _unmeasured(t, "ticksGame unreadable, so 'no tick with the moth spawned' is unproven (%r, %r)" % (t0, t1))
            return
        if t1 != t0:
            _unmeasured(t, "the game was NOT paused: %d tick(s) ran with RM_Dustveil spawned (owner ruling: state read "
                           "only); the read is void" % (t1 - t0))
            return
        if not gone:
            _unmeasured(t, "pawn_force_incapacitate vanish did not report the moth/control destroyed: remove it before "
                           "ANY unpause")
            return
        if not moth or not ctrl:
            _unmeasured(t, "spawn_pawn gave no id (moth %r, control %r)" % (moth, ctrl))
            return
        m, c = rows.get(moth), rows.get(ctrl)
        if not m or not c or "canEverFly" not in m or "canEverFly" not in c or not m.get("hasTracker", True):
            _unmeasured(t, "pawn_flight report carries no canEverFly / tracker: moth %r control %r"
                           % (str(m)[:120], str(c)[:120]))
            return
        if c.get("canEverFly") is not False:
            _unmeasured(t, "the non-flier control RM_Chittik reads canEverFly=%r: the instrument cannot say false"
                           % (c.get("canEverFly"),))
            return
        if m.get("canEverFly") is not True:
            raise ExpectationFailed("RM_Dustveil spawned with canEverFly=%r (maxFlightTimeStat %r, maxFlightTicks %r): "
                                    "the tracker says the moth cannot fly" % (m.get("canEverFly"),
                                                                              m.get("maxFlightTimeStat"),
                                                                              m.get("maxFlightTicks")))

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        with t.component("sheen_exposure_ladder", toggle="sheenExposure"):
            if _live(t):
                _unmeasured(t, 'the Sheen weather rotation bootstrapping a spore-coating hediff needs an RM_TheRot map with a colonist under the Sheen weather and game hours of ticks; weather_set is drivable but the biome-scoped rotation is not')
        with t.component("accelerated_rot_on_living_ground", toggle="acceleratedRot"):
            if _live(t):
                _unmeasured(t, "faster decay of items/corpses on the biome's ground needs a generated RM_TheRot map (or a cross-biome map) and ticks; the rot MapComponent asks this screen through RM_KitFronts; needs a debug [Tool] to flip the setting")
        with t.component("living_produce_heat", toggle="livingProduceHeat"):
            if _live(t):
                _unmeasured(t, 'live-preparation warmth needs a spawned live preparation and a temperature read after ticks on an RM_TheRot map')
        with t.component("warm_living_ground", toggle="warmMat"):
            if _live(t):
                _unmeasured(t, 'ambient warmth of the biome terrain needs a generated RM_TheRot map and a temperature read')
        with t.component("live_preparations_viability", toggle="livePreparations"):
            if _live(t):
                _unmeasured(t, 'viability lapsing on mishandling needs a live preparation thing and game days of ticks')
        with t.component("guardian_groves_lure_ring", toggle="guardianGroves"):
            if _live(t):
                _unmeasured(t, 'wild-spawned defended mushrooms with the false-fruit ring exist only on a map generated with the toggle on; the bridge cannot generate a map')
        with t.component("health_sharing", toggle="healthSharing"):
            if _live(t):
                _unmeasured(t, 'bar 1 (design/RimMandrake/rot_northstar_bars_draft_2026-10-22.md): a bruise on a mullgoth with 2+ RotNetwork kin within 12 cells heals at least 0.5 x BodySize more over 15,000 ticks than the same bruise on an isolated one; needs a bridge wound tool and RSW bestiary spawns')
        with t.component("pale_tree_wild_spawn", toggle="paleTreeSpawn"):
            if _live(t):
                _unmeasured(t, 'a rare wild-spawned oddity exists only on a generated map; it is also Royalty-gated')
        with t.component("spore_cloud_incident", toggle="sporeCloudIncidentWeight"):
            if _live(t):
                _unmeasured(t, 'fire_incident dry-run reports success=False with canFireNow=False and gives no weight read; a real firing needs a map and changes the game')
        with t.component("cross_biome_opt_in", toggle="crossBiomeEnabled"):
            if _live(t):
                _unmeasured(t, 'the cross-biome mechanics apply once right after a NEW map generates on a non-Rot biome; the bridge cannot generate a map')

    HWEL = "RimMandrake.TheRot.RM_HwelgrueProof"

    def _hp(t, method, args=None):
        kw = dict(type=HWEL, method=method)
        if args is not None:
            kw["args"] = args
        r = t.bridge_call("jawa/static_call", **kw)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    def _hp_s(t, method, args=None):
        kw = dict(type="RimMandrake.TheRot.RM_HwelgrueSwallowProof", method=method)
        if args is not None:
            kw["args"] = args
        r = t.bridge_call("jawa/static_call", **kw)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    @suite.chain("hwelgrue")
    def hwelgrue(t):
        """ROT_HWELGRUE_GIANT_BUILD_1. Runs on the CURRENT map (any map: the mechanism is the comp, not the
        biome). Not proven here: graze pathing over 30,000 ticks, the stockpile/roof exclusion, rest rot, the
        never-starts-a-fight read -- first poke: ProofGrazeTarget with a knife on open ground vs in a stockpile."""
        with t.component("map_cap_holds", toggle="hwelgrueMapCap"):
            text = _hp(t, "ProofSpawn", "3")
            if _live(t) and not text.startswith("HWELGRUE alive 1"):
                raise ExpectationFailed("three spawn attempts did not leave exactly one hwelgrue: %s" % text)
        with t.component("digest_keeps_metal_only", toggle="hwelgrue"):
            text = _hp(t, "ProofDigest")
            if _live(t) and not ("kept 1" in text and "wood destroyed True" in text):
                raise ExpectationFailed("digest did not keep the steel knife and destroy the wood: %s" % text)
        with t.component("casting_polishes_contents", toggle="hwelgrueCastingDays"):
            text = _hp(t, "ProofCasting")
            if _live(t) and not ("castings on map 1" in text and "all full hp True" in text and "gut now 0" in text):
                raise ExpectationFailed("the casting did not hold and polish the gut's metal: %s" % text)
        with t.component("swallow_then_cut_out", toggle="hwelgrueSwallow"):
            text = _hp_s(t, "ProofSwallow")
            if _live(t) and not (text.startswith("SWALLOW held") and "spawned False" in text and "still alive in there" in text):
                raise ExpectationFailed("a downed drifter was not swallowed with a naming inspect line: %s" % text)
            # ProofCut hits the BELLY (core part) first, then the other parts: the release rule is CUMULATIVE (150 summed) and a belly hit alone caps at its own 100 hp (load 13: 'dealt 100, not released').
            text = _hp_s(t, "ProofCut", "200")
            if _live(t) and not ("released True" in text and "spawned True" in text):
                raise ExpectationFailed("cutting the hwelgrue (200 a hit, belly first, at most six parts) did not cut the swallowed pawn out alive: %s" % text)
        with t.component("knocking_louder_early", toggle="swallowLoudness"):
            hi, lo = _hp_s(t, "ProofKnock", "0.8"), _hp_s(t, "ProofKnock", "0.2")
            try:
                vh, vl = float(hi.split("volume ")[1]), float(lo.split("volume ")[1])
            except (IndexError, ValueError):
                vh = vl = None
            if _live(t) and not (vh is not None and vh > vl and "RM_GutKnocking " in hi + " " and "RM_GutKnocking_Failing" in lo):
                raise ExpectationFailed("knocking is not louder/stronger early: %s || %s" % (hi, lo))
        with t.component("one_core_per_world", toggle="navigatorCore"):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.TheRot.RM_SwallowedCoreProof", method="ProofClaim", args="3")
            text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
            if _live(t) and not (text.startswith("CORE carriers 1 ") or "spent True" in text):
                raise ExpectationFailed("spawning hwelgrue did not leave exactly one core carrier: %s" % text)
        with t.component("ruined_below_threshold", toggle="navigatorRuinThreshold"):
            outs = []
            for integ in ("80", "10"):
                r = t.bridge_call("jawa/static_call", type="RimMandrake.TheRot.RM_SwallowedCoreProof", method="ProofDrop", args=integ)
                outs.append(str((r or {}).get("result", "")) if isinstance(r, dict) else "")
            if _live(t) and outs != ["DROP RM_SwallowedDriveCore", "DROP RM_RuinedDriveCore"]:
                raise ExpectationFailed("integrity 80/10 should drop the core / the ruin: %r" % outs)
        with t.component("core_multiplies_total_range", toggle="navigatorRangeBonus"):
            if _live(t):
                _unmeasured(t, "needs a gravship (engine + thrusters) with an installed, linked core; read RM_SwallowedCoreProof.ProofRange before and after installing it")
        with t.component("ship_guns_wreck_the_core", toggle="navigatorShipDamageFactor"):
            if _live(t):
                _unmeasured(t, "needs a turret on gravship substructure firing at the carrier; read the carrier's inspect integrity before/after, and a rifle hit for the control")
        with t.component("rest_accelerates_rot", toggle="hwelgrueRotMultiplier"):
            if _live(t):
                _unmeasured(t, "needs an idle hwelgrue, two meat stacks at 3 and 20 cells, and ticks; RotProgress read per stack")

    GM = "RimMandrake.TheRot.RM_GutMotherProof"

    def _gm(t, method):
        r = t.bridge_call("jawa/static_call", type=GM, method=method)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    @suite.chain("gut_mother")
    def gut_mother(t):
        """ROT_GUT_MOTHER_VAT_1. Runs on the CURRENT map, which should NOT be a Rot map (the vat grows anywhere).
        Not proven here: the feed bill's hauling path, the sac dropping from a killed hwelgrue, a 30-day carry of a
        starter beside a tea -- first poke: kill a hwelgrue (ProofSpawn 1 then dev kill) and look for the sac."""
        with t.component("research_needs_studied_sac", toggle="gutMother"):
            text = _gm(t, "ProofResearch")
            if _live(t) and "after studied True" not in text:
                raise ExpectationFailed("forcing the sac's analysis did not satisfy RM_GutMotherCulture: %s" % text)
        with t.component("digest_returns_implants_and_gear", toggle="gutMotherRecoveryChance"):
            text = _gm(t, "ProofDigest")
            if _live(t) and not ("BionicArm True" in text and "rifle True" in text and "parka True" in text and "corpse gone True" in text):
                raise ExpectationFailed("the vat did not return arm, rifle and parka and consume the body: %s" % text)
        with t.component("hungry_vat_is_dormant", toggle="gutMotherDigestHours"):
            text = _gm(t, "ProofDormant")
            if _live(t) and not (text.startswith("DORMANT progress 0 -> 0") and "dormant True" in text):
                raise ExpectationFailed("an unfed vat progressed its body: %s" % text)
        with t.component("starter_keeps_and_trades", toggle="gutMotherStarterValue"):
            text = _gm(t, "ProofStarter")
            if _live(t) and not ("rottable False" in text and "viability False" in text and "tradeable True" in text and "split makes 1" in text):
                raise ExpectationFailed("the starter rots, cannot trade, or the split is not exactly one: %s" % text)

    @suite.chain("navigator_log")
    def navigator_log(t):
        """ROT_NAVIGATOR_LOG_SITES_1. Needs a FRESH world (or one whose RM_WorldComponent_SwallowedCore has 0 pings) and a
        player home map: pings are added straight to the world component (no engine). The landing ping is not proven
        here -- first poke: stand a carrier on a map, land a gravship there, read ProofClaim's pings before/after."""
        with t.component("entry_every_n_pings", toggle="navigatorPingsPerEntry"):
            # The log is WORLD state and ProofPings ADDS pings, so a second TheRot run in the same game read 'pings 20 |
            # entries 2' and FAILED a working mechanic (load 14): a non-empty log is a precondition, not a verdict.
            r0 = t.bridge_call("jawa/static_call", type="RimMandrake.TheRot.RM_NavigatorLogProof", method="ProofPings", args="0")
            t0 = str((r0 or {}).get("result", "")) if isinstance(r0, dict) else ""
            import re as _re
            m0 = _re.search(r"pings (\d+)", t0)
            if _live(t) and (not m0 or int(m0.group(1)) != 0):
                _unmeasured(t, "precondition: the world's navigator log already holds pings (%s); needs a fresh world or a game "
                               "with no earlier TheRot run" % (t0 or "unreadable"))
            r = t.bridge_call("jawa/static_call", type="RimMandrake.TheRot.RM_NavigatorLogProof", method="ProofPings", args="4")
            text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
            if _live(t) and "entries 1 " not in text + " ":
                raise ExpectationFailed("4 pings did not read exactly one entry: %s" % text)
            r = t.bridge_call("jawa/static_call", type="RimMandrake.TheRot.RM_NavigatorLogProof", method="ProofPings", args="4")
            text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
            if _live(t) and not ("entries 2 " in text + " " and "sites 1 " in text + " " and "quests 1" in text):
                raise ExpectationFailed("8 pings did not read 2 entries and reveal one salvage site: %s" % text)
        with t.component("carrier_death_cuts_log", toggle="navigatorCore"):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.TheRot.RM_NavigatorLogProof", method="ProofKillThenPing", args="8")
            text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
            if _live(t) and not ("entries 2 -> 2" in text and "cut True" in text):
                raise ExpectationFailed("pings after the carrier died moved the log: %s" % text)
        with t.component("landing_pings_at_once", toggle="navigatorCore"):
            if _live(t):
                _unmeasured(t, "needs a living carrier on a map and a gravship landing there; RM_SwallowedCoreProof.ProofClaim pings 0 -> 1, and 0 with no carrier")

    @suite.chain("unjoining")
    def unjoining(t):
        """ROT_UNJOINING_DRAUGHT_1. Any map. Each call generates a fresh player colonist and runs the draught's outcome
        doer on it. Not proven here: the drug-lab bill, the metalhorror actually bursting out (vanilla emergence delay),
        the campaign rite finishing the research -- first poke: ProofDraught horror, then step ~2,500 ticks and count
        Metalhorror pawns."""
        def _uj(mode):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.TheRot.RM_UnjoiningProof", method="ProofDraught", args=mode)
            return str((r or {}).get("result", "")) if isinstance(r, dict) else ""
        with t.component("purges_parasites_and_symbionts", toggle="unjoiningDraught"):
            text = _uj("parasites")
            if _live(t) and not ("left 0 " in text and "purge True" in text and "husks 1 " in text and "scars 1 " in text):
                raise ExpectationFailed("the draught did not purge 3, drop one husk and leave one scar: %s" % text)
        with t.component("clean_patient_only_purges", toggle="unjoiningOrganDamage"):
            text = _uj("none")
            if _live(t) and not ("purge True" in text and "husks 0 " in text):
                raise ExpectationFailed("a clean patient got more than the purge: %s" % text)
        with t.component("forces_metalhorror_out", toggle="unjoiningPurgeHours"):
            text = _uj("horror")
            if _live(t) and "horror emerging True" not in text:
                raise ExpectationFailed("the metalhorror implant was not forced to emerge: %s" % text)

    @suite.chain("living_mat_root")
    def living_mat_root(t):
        """ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD. A NON-Rot map with open bare ground near the centre (a quicktest map).
        ProofStage builds a sealed, roofed 5x5 wood room with a full root at its centre; ProofSweeps runs hurried
        sweeps (every timer elapsed) on it and reads food, grown cells, room and outdoor temperature."""
        def _mr(method, args=None):
            kw = {"type": "RimMandrake.TheRot.RM_LivingMatRootProof", "method": method}
            if args is not None:
                kw["args"] = args
            r = t.bridge_call("jawa/static_call", **kw)
            return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

        def _num(text, pat):
            m = re.search(pat, text)
            return [float(x) for x in m.groups()] if m else None

        with t.component("fed_root_spreads_and_eats", toggle="portableWarmMatSpread"):
            staged = _mr("ProofStage")
            if _live(t):
                if not staged.startswith("STAGED"):
                    _unmeasured(t, "ProofStage could not stage a room: %s" % staged)
                elif "rot True" in staged:
                    _unmeasured(t, "staged on an RM_TheRot map; this chain needs a non-Rot map")
            text = _mr("ProofSweeps", "5|fed")
            if _live(t):
                ate = _num(text, r"ate (-?[\d.]+)")
                grown = _num(text, r"grown (\d+)->(\d+)")
                if not ate or not grown:
                    raise ExpectationFailed("unreadable ProofSweeps: %s" % text)
                if not grown[1] - grown[0] == 5:
                    raise ExpectationFailed("5 fed sweeps did not lay 5 mat cells: %s" % text)
                if not ate[0] > 0:
                    raise ExpectationFailed("a fed root off the Rot ate nothing: %s" % text)
        with t.component("mat_room_warms_to_cap", toggle="portableWarmMatWarmth"):
            text = _mr("ProofSweeps", "40|fed")
            if _live(t):
                mat = _num(text, r"mat (\d+)/(\d+)")
                temp = _num(text, r"room (-?[\d.]+)->(-?[\d.]+)")
                out = _num(text, r"outdoor (-?[\d.]+)")
                if not mat or not temp or not out:
                    raise ExpectationFailed("unreadable ProofSweeps: %s" % text)
                if mat[0] < 0.6 * mat[1]:
                    raise ExpectationFailed("40 more sweeps left the room under 60%% mat: %s" % text)
                target = min(out[0] + 18.0, 21.0)
                if temp[1] > 21.05:
                    raise ExpectationFailed("the mat pushed a room past the 21 C cap: %s" % text)
                if temp[0] < target - 0.5 and not temp[1] > temp[0]:
                    raise ExpectationFailed("a fed, mat-floored room below its target did not warm: %s" % text)
        with t.component("starved_root_dies_back", toggle="portableWarmMatDieBack"):
            text = _mr("ProofSweeps", "3|empty")
            if _live(t):
                grown = _num(text, r"grown (\d+)->(\d+)")
                if not grown:
                    raise ExpectationFailed("unreadable ProofSweeps: %s" % text)
                if not (grown[0] - grown[1] == 3 and "starving" in text):
                    raise ExpectationFailed("3 starved sweeps did not uncover 3 grown cells: %s" % text)
        with t.component("rot_root_eats_nothing", toggle="portableWarmMat"):
            if _live(t):
                _unmeasured(t, "needs an RM_TheRot map; first poke: ProofStage then ProofSweeps 5|fed there, food must not move")


    CB_SETTINGS = "RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings"
    LINK_CONTROL = "ThingDef/ZZ_NoSuchDef_Probe"

    def _cuts(row, part=None):
        """Total severity of the Cut injuries on a list_pawns health row (optionally on one BodyPartDef)."""
        hs = ((row or {}).get("health") or {}).get("hediffs") or []
        return sum(float(h.get("severity") or 0) for h in hs
                   if isinstance(h, dict) and h.get("def") == LINK_DAMAGE and (part is None or h.get("part") == part))

    def _link_defs(t, names):
        r = t.bridge_call("jawa/get_defs", defs=";".join(["ThingDef/" + n for n in names] + [LINK_CONTROL]),
                          fields="comps", deep=False, limit=len(names) + 2)
        # deep=False on purpose: a shallow list item is its TYPE name (CompProperties_WoundLink); deep=True renders a
        # comp as a dict of its public fields, whose only class trace is compClass (RM_CompWoundLink).
        if not _live(t):
            return None
        if not isinstance(r, dict) or r.get("success") is False:
            raise ExpectationFailed("get_defs failed: %r" % (r,))
        if not any("ZZ_NoSuchDef_Probe" in str(x) for x in (r.get("notFound") or [])):
            _unmeasured(t, "the control %s did not read notFound: the instrument cannot say absent (%r)"
                           % (LINK_CONTROL, r.get("notFound")))
            return None
        rows = dict((d.get("defName"), json.dumps((d.get("fields") or {}).get("comps"), default=str))
                    for d in (r.get("defs") or []) if isinstance(d, dict))
        if rows and not any(("CompProperties" in b or "compClass" in b) for b in rows.values()):
            _unmeasured(t, "get_defs comps carry no class names, so a missing WoundLink comp is invisible: %s"
                           % str(rows)[:160])
            return None
        return rows

    def _has_link(blob):
        return "CompProperties_WoundLink" in blob or "RM_CompWoundLink" in blob

    def _wound_pair(t, dz):
        """Two wild RM_Chittik 2 cells apart (kin radius 12); one Cut of LINK_AMOUNT to A's carapace (no brain, so it
        mirrors); both health rows read back. Returns a dict, or None after an UNMEASURED."""
        x, z = t.anchor
        z += dz
        a = _spawn_one(t, "RM_Chittik", x, z)
        b = _spawn_one(t, "RM_Chittik", x + 2, z)
        t._wound_pawns = getattr(t, "_wound_pawns", []) + [p for p in (a, b) if p]
        if not _live(t):
            return None
        if not a or not b:
            _unmeasured(t, "spawn_pawn gave no RM_Chittik id (%r, %r)" % (a, b))
            return None

        def rows():
            r = t.bridge_call("jawa/list_pawns", limit=50, includeHealth=True, rect="%d,%d,6,3" % (x - 1, z - 1))
            return dict((p.get("id"), p) for p in ((r or {}).get("pawns") or []) if isinstance(p, dict))
        base = rows()
        if a not in base or b not in base:
            _unmeasured(t, "list_pawns did not read back both chittiks (%s)" % sorted(base)[:6])
            return None
        if "health" not in base[b]:
            _unmeasured(t, "list_pawns returned no health block: the instrument is blind to injuries")
            return None
        d = t.bridge_call("jawa/damage", damageDef=LINK_DAMAGE, amount=LINK_AMOUNT, thingId=a, armorPenetration=1.0,
                          bodyPart=LINK_PART)
        after = rows()
        out = {"a": a, "b": b, "aCut": _cuts(after.get(a), LINK_PART), "bCut": _cuts(after.get(b), LINK_PART),
               "bCutAny": _cuts(after.get(b)), "bBefore": _cuts(base.get(b)), "damage": str(d)[:200]}
        t._record("wound pair dz=%d" % dz, out)
        if out["bBefore"] > 0:
            _unmeasured(t, "the recipient carried a Cut before the hit: %r" % (out,))
            return None
        if out["aCut"] + out["bCutAny"] < 8.0:
            _unmeasured(t, "the hit left under the 8-severity gate on the victim (it never mirrors by design): %r" % (out,))
            return None
        return out

    @suite.chain("wound_link")
    def wound_link(t):
        """ROT_WOUNDLINK_FIX_DROPPED_AT_THE_DOOR A2/A3 (runbook 2026-10-22 rows 2.1, 2.2). The comp is
        CreatureBehaviors' RM_CompWoundLink; the live switch is RM_CreatureBehaviorsSettings.woundLinkEnabled
        (TheRot's healthSharing strips the comps at STARTUP only, so it cannot be flipped live)."""
        state = {}
        with t.component("chittik_carries_wound_link", beyond_toggle=True):
            rows = _link_defs(t, ["RM_Chittik"])
            if rows is not None and _live(t):
                if "RM_Chittik" not in rows:
                    raise ExpectationFailed("ThingDef/RM_Chittik does not resolve live")
                if not _has_link(rows["RM_Chittik"]):
                    raise ExpectationFailed("RM_Chittik carries no CompProperties_WoundLink live (healthSharing off at "
                                            "startup strips it; else the def lost it): %s" % rows["RM_Chittik"][:200])
        try:
            _wound_arms(t, state)
        finally:
            if t.session is not None:
                if state.get("prev") is not None:
                    t.session.call("jawa/mod_settings_field", typeName=CB_SETTINGS, action="set",
                                   field="woundLinkEnabled", value=str(state["prev"]))
                for pid in getattr(t, "_wound_pawns", []):
                    _remove(t, pid)
                t._wound_pawns = []
        with t.component("bestiary_kin_carry_wound_link", beyond_toggle=True):
            rows = _link_defs(t, ["RM_Durrok", "RM_Mullgoth"])
            if rows is not None and _live(t):
                absent = [n for n in ("RM_Durrok", "RM_Mullgoth") if n not in rows]
                lacking = [n for n in ("RM_Durrok", "RM_Mullgoth") if n in rows and not _has_link(rows[n])]
                if lacking:
                    raise ExpectationFailed("%s resolve but carry no CompProperties_WoundLink (Patches/"
                                            "RotSpecies_WoundSharing.xml did not apply)" % lacking)
                if absent:
                    _unmeasured(t, "%s not loaded: they live in mandrake.rsw.swbestiary, absent from this tier" % absent)

    def _wound_arms(t, state):
        """A3's two arms. The caller restores woundLinkEnabled and removes the pawns, whatever happens here."""
        with t.component("wound_shared_with_kin_when_on", beyond_toggle=True):
            if _live(t):
                g = t.session.call("jawa/mod_settings_field", typeName=CB_SETTINGS, action="get", field="woundLinkEnabled")
                state["prev"] = (g or {}).get("value") if isinstance(g, dict) else None
                if state["prev"] is None:
                    _unmeasured(t, "woundLinkEnabled unreadable on %s: %r" % (CB_SETTINGS, g))
                else:
                    t.set_setting(CB_SETTINGS, {"woundLinkEnabled": "true"})
            res = _wound_pair(t, 0) if _live(t) else None
            if res is not None and _live(t):
                if res["aCut"] <= 0:
                    _unmeasured(t, "the victim shows no Cut on %s after the hit: the damage did not land where read %r"
                                   % (LINK_PART, res))
                elif not res["bCut"] > 0:
                    raise ExpectationFailed("sharing ON: the kin 2 cells away received no %s on %s: %r"
                                            % (LINK_DAMAGE, LINK_PART, res))
        with t.component("no_share_when_off", beyond_toggle=True):
            if _live(t):
                if state.get("prev") is None:
                    _unmeasured(t, "woundLinkEnabled was never read, so it is not flipped off (it could not be restored)")
                else:
                    t.set_setting(CB_SETTINGS, {"woundLinkEnabled": "false"})
            res = _wound_pair(t, 4) if _live(t) else None
            if res is not None and _live(t):
                if res["aCut"] <= 0:
                    _unmeasured(t, "the victim shows no Cut after the OFF-arm hit: %r" % (res,))
                elif res["bCutAny"] > 0:
                    raise ExpectationFailed("sharing OFF: the kin still received a wound: %r" % (res,))

    return suite


suite = _build_suite() if Suite is not None else None

class _MockRotSession(object):
    """--mock: answers like a game where wound_link, dustveil and living_mat_root work. `broken` plants ONE defect:
    nocomp (chittik lost the comp), noshare (ON arm mirrors nothing), offleaks (OFF arm still mirrors), blindctrl
    (get_defs control reads present), nobestiary (Durrok/Mullgoth absent), grounded (moth canEverFly false),
    ctrlflies (the non-flier control reads true), ticking (the clock runs while the moth is spawned), nospread
    (5 fed sweeps lay 4 cells), hot (the mat room passes 21 C), nodieback (a starved root keeps its cells),
    rotmap (staged on an RM_TheRot map)."""

    def __init__(self, broken=None):
        self.broken, self.calls, self.ticks, self.n = broken, [], 1000, 0
        self.pawns, self.link_on, self.grown, self.room = {}, True, 0, 5.0

    def track(self, *a, **k):
        return None

    def sweep(self):
        return None

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        b = self.broken
        if b == "ticking" and any(p["kind"] == "RM_Dustveil" for p in self.pawns.values()):
            self.ticks += 60       # an unpaused game: the clock runs between any two calls while the moth is spawned
        if tool == "rimworld/get_game_info":
            return {"success": True, "ticksGame": self.ticks}
        if tool == "jawa/get_defs":
            names = [d.split("/", 1)[1] for d in (kw.get("defs") or "").split(";") if d]
            if kw.get("fields") == "statBases":
                return {"success": True, "foundCount": 1, "notFound": [],
                        "defs": [{"defName": "RM_Dustveil", "fields": {"statBases": [{"stat": "MaxFlightTime", "value": 6}]}}]}
            known = {"RM_Chittik", "RM_MothSilk", "RM_Dustveil"} | (set() if b == "nobestiary" else {"RM_Durrok", "RM_Mullgoth"})
            if b == "blindctrl":
                known.add("ZZ_NoSuchDef_Probe")
            rows, nf = [], []
            for n in names:
                if n not in known:
                    nf.append("ThingDef/" + n)
                    continue
                comps = ["CompProperties_Milkable"]                     # shallow get_defs: list items are TYPE names
                if not (b == "nocomp" and n == "RM_Chittik"):
                    comps.append("CompProperties_WoundLink")
                rows.append({"defName": n, "fields": {"comps": comps, "defName": n}})
            return {"success": True, "foundCount": len(rows), "notFound": nf, "defs": rows}
        if tool == "jawa/mod_settings_field":
            if kw.get("action") == "set":
                self.link_on = str(kw.get("value")).lower() == "true"
                return {"success": True}
            return {"success": True, "value": "True" if self.link_on else "False"}
        if tool == "jawa/spawn_pawn":
            self.n += 1
            pid = "Mock%d" % self.n
            self.pawns[pid] = {"kind": kw.get("kindDef"), "x": kw.get("x"), "z": kw.get("z"), "hediffs": []}
            return {"success": True, "pawns": [{"id": pid, "kindDef": kw.get("kindDef"), "name": pid}]}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": k, "kindDef": v["kind"], "health": {"hediffs": list(v["hediffs"])}}
                                               for k, v in self.pawns.items()]}
        if tool == "jawa/damage":
            a = self.pawns[kw["thingId"]]
            sev = float(kw.get("amount"))
            kin = [v for k, v in self.pawns.items() if k != kw["thingId"] and v["kind"] == a["kind"]
                   and abs(v["x"] - a["x"]) <= 12 and abs(v["z"] - a["z"]) <= 1]
            share = 0.6 * sev if ((self.link_on and b != "noshare") or (not self.link_on and b == "offleaks")) and kin else 0.0
            a["hediffs"].append({"def": kw.get("damageDef"), "part": kw.get("bodyPart"), "severity": sev - share})
            for v in kin if share else []:
                v["hediffs"].append({"def": kw.get("damageDef"), "part": kw.get("bodyPart"), "severity": share})
            return {"success": True}
        if tool == "jawa/destroy_batch":
            return {"success": True, "skippedPawns": len(self.pawns)}     # like the real tool: pawns are never destroyed
        if tool == "jawa/pawn_force_incapacitate":
            gone = self.pawns.pop(kw.get("pawn"), None) is not None and kw.get("action") == "vanish"
            return {"success": gone, "destroyedAfter": gone}
        if tool == "jawa/pawn_flight":
            p = self.pawns.get(kw.get("pawn"))
            fly = p is not None and ((p["kind"] == "RM_Dustveil" and b != "grounded") or b == "ctrlflies")
            return {"success": True, "pawns": [{"id": kw.get("pawn"), "hasTracker": True, "canEverFly": fly,
                                                "flying": False, "flightState": "Grounded", "maxFlightTimeStat": 6 if fly else 0}]}
        if tool == "jawa/static_call" and kw.get("type") == "RimMandrake.TheRot.RM_LivingMatRootProof":
            m, a = kw.get("method"), (kw.get("args") or "").split("|")
            if m == "ProofStage":
                return {"success": True, "result": "STAGED at 50,50 | rot %s | food 10.0" % (b == "rotmap")}
            n, fed = int(a[0]), a[1] == "fed"
            g0, r0 = self.grown, self.room
            if fed:
                self.grown = min(25, self.grown + (n - 1 if b == "nospread" and n == 5 else n))
                if self.grown >= 15:
                    self.room = 23.0 if b == "hot" else min(21.0, self.room + 0.5 * n)
                status = "fed; warming this room toward 21C"
            else:
                self.grown = self.grown if b == "nodieback" else max(0, self.grown - n)
                status = "starving; dying back"
            return {"success": True, "result": "ROOT 0 | rot False | food 10.00->8.00 ate %.3f | grown %d->%d | room %.1f->%.1f "
                    "(mat %d/25) | outdoor 5.0 | %s" % (2.0 if fed else 0.0, g0, self.grown, r0, self.room, self.grown, status)}
        return {"success": True}


MOCK_EXPECT = {
    # broken -> {chain/component: verdict it MUST read}; every other listed row of a clean run must PASS.
    None: {"wound_link/chittik_carries_wound_link": "PASS", "wound_link/wound_shared_with_kin_when_on": "PASS",
           "wound_link/no_share_when_off": "PASS", "wound_link/bestiary_kin_carry_wound_link": "PASS",
           "dustveil/flight_stat_live": "PASS", "dustveil/silk_defs_live": "PASS",
           "dustveil/flight_tracker_state_read": "PASS", "dustveil/flip_book_frames_cycle": "UNMEASURED",
           "living_mat_root/fed_root_spreads_and_eats": "PASS", "living_mat_root/mat_room_warms_to_cap": "PASS",
           "living_mat_root/starved_root_dies_back": "PASS", "living_mat_root/rot_root_eats_nothing": "UNMEASURED"},
    "nocomp": {"wound_link/chittik_carries_wound_link": "FAIL"},
    "noshare": {"wound_link/chittik_carries_wound_link": "PASS", "wound_link/wound_shared_with_kin_when_on": "FAIL"},
    "offleaks": {"wound_link/wound_shared_with_kin_when_on": "PASS", "wound_link/no_share_when_off": "FAIL"},
    "blindctrl": {"wound_link/chittik_carries_wound_link": "UNMEASURED"},
    "nobestiary": {"wound_link/no_share_when_off": "PASS", "wound_link/bestiary_kin_carry_wound_link": "UNMEASURED"},
    "grounded": {"dustveil/flight_tracker_state_read": "FAIL"},
    "ctrlflies": {"dustveil/flight_tracker_state_read": "UNMEASURED"},
    "ticking": {"dustveil/flight_tracker_state_read": "UNMEASURED"},
    "nospread": {"living_mat_root/fed_root_spreads_and_eats": "FAIL"},
    "hot": {"living_mat_root/fed_root_spreads_and_eats": "PASS", "living_mat_root/mat_room_warms_to_cap": "FAIL"},
    "nodieback": {"living_mat_root/mat_room_warms_to_cap": "PASS", "living_mat_root/starved_root_dies_back": "FAIL"},
    "rotmap": {"living_mat_root/fed_root_spreads_and_eats": "UNMEASURED"},
}
MOCK_CHAINS = ("wound_link", "dustveil", "living_mat_root")


def mock_run():
    """Each planted defect turns ITS row red (or UNMEASURED when it blinds the instrument); a clean mock is green.
    Also checks the moth never sees a tick and every spawned pawn is destroyed again, and the wound-link switch is
    restored to what it read."""
    from runner import run_suite
    chains = list(suite.chains)
    bad = []
    try:
        for broken, want in MOCK_EXPECT.items():
            sess = _MockRotSession(broken)
            suite.chains[:] = [c for c in chains if c[0] in MOCK_CHAINS]
            res = run_suite(suite, sess, anchor=(50, 50))
            got = dict(("%s/%s" % (ch.get("name"), c.get("name")), str(c.get("verdict", "")).upper())
                       for ch in res.get("chains", []) for c in (ch.get("components") or []))
            for row, v in want.items():
                if got.get(row) != v:
                    bad.append("%s: %s read %s, want %s" % (broken, row, got.get(row), v))
            if broken is None:
                if sess.pawns:
                    bad.append("clean: %d mock pawn(s) left spawned: %s" % (len(sess.pawns), sorted(sess.pawns)))
                if not sess.link_on:
                    bad.append("clean: woundLinkEnabled not restored to True")
                if [c for c in sess.calls if c[0] == "jawa/pawn_flight" and c[1].get("action") != "report"]:
                    bad.append("clean: a pawn_flight call other than action=report")
                if [c for c in sess.calls if c[0] in ("rimworld/step_game_ticks", "jawa/safe_advance", "rimworld/take_screenshot")]:
                    bad.append("clean: the chains advanced the clock or took a screenshot")
    finally:
        suite.chains[:] = chains
    print("MOCK: %s (%d planted cases)%s" % ("FAIL" if bad else "PASS", len(MOCK_EXPECT), "".join("\n  - " + b for b in bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    if "--mock" in sys.argv:
        sys.path.insert(0, os.path.join(HERE, "..", "Utils", "modcheck"))
        sys.exit(mock_run())
    if "--planted" in sys.argv:
        res = planted_ambrosyx() + planted_dustveil()
        for name, ok in res:
            print("PLANTED %-16s %s" % (name, "RED as expected" if ok and name not in ("clean", "dv clean") else ("GREEN" if ok else "MISSED")))
        sys.exit(0 if all(ok for _n, ok in res) else 1)
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
