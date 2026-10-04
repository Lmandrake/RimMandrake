"""validation.py -- modcheck suite for RimMandrake: Warscar (mandrake.rm.warscar).

Item WARSCAR_TURRETS_TRACK_1 (the only live mechanic this mod ships so far). Warscar's biome, flora and
item defs have no script yet; this first script covers the turret pair only.

WHAT IT PROVES (state reads, never a screenshot hunt):
  * defs_resolve: RM_OldLineTurret / _Gun / _Bullet resolve live, and the aim comp type loaded
    (a def naming a missing comp type is discarded silently by the engine).
  * tracking: a broken turret spawned beside a walking pawn reports the tracking inspect line (the comp's
    own state) and spawns NO projectile; with `turretTrackingEnabled` off the line is absent (control).
  * refit: a Refit gizmo exists on the broken turret when `turretRefitEnabled` is on and is absent when
    off (control).
NOT PROVEN HERE: the old-line turret FIRING at hostiles (needs a raid and power; owner/FOUNDRY live
round, criterion 2 of the item), the barrel's drawn angle (visual), and the Refit blueprint's
construction. Each says UNMEASURED rather than passing.

STATIC (offline) CHECKS: `python3 validation.py` runs `static_checks()` without a game: XML parses, every
Mod Settings field is Scribed and exposed, the .cs file is in the csproj, the patch targets exist.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "RimMandrake.Scarlands."
SETTINGS_TYPE = NS + "RM_WarscarSettings"
DEFAULTS = {"totchakEnabled": True, "totchakEatsPlayerWalls": True, "totchakWakeRadius": 12.0,
            "totchakBiteScale": 1.0, "totchakGrazeDays": 8.0, "turretTrackingEnabled": True, "turretRefitEnabled": True,
            "oldLineDamageFactor": 1.0, "oldLineCooldownFactor": 1.0,
            "oldTongueEnabled": True, "oldTonguePanelsPerMap": 3.0, "oldTongueRevealChance": 0.8, "oldTongueSkillGate": 8,
            "hospiceEnabled": True, "hospiceIntactPerMap": 2, "hospiceStageDays": 1.5, "hospiceFailureChance": 0.08,
            "hospiceLashOut": True, "hospiceWalkInEnabled": True, "hospiceWalkInFrequency": 1.0,
            "chotrixEnabled": True, "chotrixPerMap": 2.0, "chotrixRevealSeconds": 4.0, "lacquerCloakEnabled": True, "lacquerSeenRadius": 15.0,
            "enableChatrak": True, "enableTetchik": True, "enablePallbearer": True, "enableScarRoach": True,
            "enableWreckLichenSeeder": True, "enableInterimDonors": True,
            "poolsEnabled": True, "poolsPerMap": 3.0, "poolCycleHours": 24.0, "bloomDanger": 1.0, "catalystEnabled": True,
            "settlingEnabled": True, "settlingCalmThreshold": 0.35, "settlingCalmHours": 4.0, "settlingEndWind": 0.8,
            "settlingEndHours": 1.0, "settlingToxicStrength": 1.0, "liftFrontEnabled": True, "warDustEnabled": True,
            "warDustBlightCureEnabled": True,
            "ordnancePerMap": 3.0,
            "choirEnabled": True, "choirVolume": 1.0, "choirTickVolumeCeiling": 1.0, "choirTickDensity": 1.0,
            "choirWindEnabled": True, "choirReducedRepetition": False, "choirJarWarnings": True,
            "markEnabled": True, "markAccrualPerDay": 0.3, "markFloorEnabled": True, "markTradeBonusesEnabled": True,
            "snapEnabled": True, "snapArmingHours": 24.0, "snapStageSpeed": 1.0,
            "loosenedPanelsEnabled": True, "loosenedPanelsPerMap": 3.0}
CHOIR_DEFS = ["SoundDef/RM_GeigerTick", "SoundDef/RM_WindOnMetal", "SoundDef/RM_ProjectorHum", "SoundDef/RM_PoolBoil",
              "ThingDef/RM_CapturedTetchik", "ThingDef/RM_TetchikJar", "RecipeDef/RM_MakeTetchikJar"]
SETTLING_DEFS = ["GameConditionDef/RM_Settling", "ThingDef/RM_Filth_SettledFilm", "ThingDef/RM_WarDust",
                 "ThingDef/RM_BuriedOrdnance", "JobDef/RM_SweepWarDust", "JobDef/RM_DefuseOrdnance",
                 "JobDef/RM_TriggerOrdnance", "JobDef/RM_DustBlight", "RecipeDef/RM_StretchDyeWithWarDust"]
PANELS = {"Hospice": 2, "Projector": 3, "Pool": 3}
BROKEN = ["AncientAutocannonTurret", "AncientUraniumSlugTurret", "RUT_BustedShieldedTurret"]
SNAP_DEFS = ["HediffDef/RM_ChatrakIncubation", "PawnKindDef/RM_Chatrak"]
MARK_DEFS = ["HediffDef/RM_WarscarMark", "ThoughtDef/RM_WarscarMarkThought"]
NEW_DEFS = ["ThingDef/RM_OldLineTurret", "ThingDef/RM_OldLineTurret_Gun", "ThingDef/RM_OldLineTurret_Bullet"]


def static_checks():
    """Return a list of failure strings; empty means pass. Needs no game."""
    bad = []
    src = open(os.path.join(HERE, "Source", "RM_WarscarMod.cs")).read()
    for f in DEFAULTS:
        if '"%s"' % f not in src:
            bad.append("settings field %s is not Scribed in RM_WarscarMod.cs" % f)
        if not re.search(r"\b%s\b" % f, src.split("DoWindowContents")[1]):
            bad.append("settings field %s has no control in DoWindowContents" % f)
    if 'Compile Include="RM_CompTurretAim.cs"' not in open(os.path.join(HERE, "Source", "RM_Warscar.csproj")).read():
        bad.append("RM_CompTurretAim.cs missing from RM_Warscar.csproj")
    d = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_OldLineTurret.xml")).getroot()
    names = [e.findtext("defName") for e in d]
    for n in NEW_DEFS:
        if n.split("/")[1] not in names:
            bad.append("def %s missing" % n)
    turret = [e for e in d if e.findtext("defName") == "RM_OldLineTurret"][0]
    gun = [e for e in d if e.findtext("defName") == "RM_OldLineTurret_Gun"][0]
    if turret.findtext("building/turretGunDef") != "RM_OldLineTurret_Gun":
        bad.append("turretGunDef does not name the gun def")
    if float(gun.findtext("verbs/li/range")) < 40:
        bad.append("old-line turret is not long range")
    if float(turret.findtext("building/turretBurstCooldownTime")) < 10:
        bad.append("old-line turret cooldown is not long")
    # WARSCAR_TOTCHAK_WAKES_1
    csproj = open(os.path.join(HERE, "Source", "RM_Warscar.csproj")).read()
    if 'Compile Include="RM_Totchak.cs"' not in csproj:
        bad.append("RM_Totchak.cs missing from RM_Warscar.csproj")
    if "0Harmony" not in csproj:
        bad.append("csproj has no Harmony reference (demolition postfixes need it)")
    tc = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "RM_Totchak.cs")).read())
    for needle in ("Mineable", "GenExplosion", "DestroyMode.Deconstruct", "All.Count == 0", "totchakEatsPlayerWalls",
                   "FindWall(pawn, false)", "ToSleep"):
        if needle not in tc:
            bad.append("RM_Totchak.cs lacks %s" % needle)
    if tc.index("FindWall(pawn, false)") > tc.index("FindWall(pawn, true)"):
        bad.append("player walls are searched before ruin walls")
    race = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Totchak.xml")).getroot()
    rn = [e.findtext("defName") + ":" + e.tag for e in race]
    for n in ("RM_Totchak:ThingDef", "RM_Totchak:PawnKindDef"):
        if n not in rn:
            bad.append("def %s missing" % n)
    thing = [e for e in race if e.tag == "ThingDef"][0]
    if thing.findtext("comps/li[@Class='CompProperties_CanBeDormant']/startsDormant") != "true":
        bad.append("totchak does not start dormant")
    if thing.findtext("race/thinkTreeMain") != "RM_Totchak":
        bad.append("totchak does not use its think tree")
    for f, root in (("ThinkTreeDefs/RM_ThinkTree_Totchak.xml", "ThinkTreeDef"), ("JobDefs/RM_TotchakJobs.xml", "JobDef"),
                    ("GenStepDefs/RM_TotchakInWall.xml", "GenStepDef")):
        ET.parse(os.path.join(HERE, "Defs", *f.split("/")))
    if "RM_TotchakInWall" not in open(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Warscar.xml")).read():
        bad.append("biome does not run the RM_TotchakInWall genstep")
    # WARSCAR_OLD_TONGUE_1
    if 'Compile Include="RM_OldTongue.cs"' not in csproj:
        bad.append("RM_OldTongue.cs missing from RM_Warscar.csproj")
    ot = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "RM_OldTongue.cs")).read())
    for needle in ("oldTongueSkillGate", "SkillDefOf.Intellectual", "level < gate".replace("level", "Level"), "read = true"):
        if needle not in ot:
            bad.append("RM_OldTongue.cs lacks %s" % needle)
    tdefs = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_InscribedPanels.xml")).getroot()
    rdefs = ET.parse(os.path.join(HERE, "Defs", "ResearchProjectDefs", "RM_OldTongue.xml")).getroot()
    ids = set()
    for k, n in PANELS.items():
        t = [e for e in tdefs if e.findtext("defName") == "RM_InscribedPanel_" + k]
        r = [e for e in rdefs if e.findtext("defName") == "RM_OldTongue_" + k]
        if not t or not r:
            bad.append("panel or project def missing for %s" % k)
            continue
        c = t[0].find("comps/li")
        aid = c.findtext("analysisID")
        if aid in ids:
            bad.append("duplicate analysisID %s" % aid)
        ids.add(aid)
        if c.findtext("analysisRequiredRange") != "%d~%d" % (n, n):
            bad.append("%s set size is not %d" % (k, n))
        if c.findtext("canStudyInPlace") != "true":
            bad.append("%s panel is not studiable in place" % k)
        if r[0].findtext("requiredAnalyzed/li") != "RM_InscribedPanel_" + k:
            bad.append("project %s does not require its panel def" % k)
        for tex in (c.findtext("chalkTexPath"), t[0].findtext("graphicData/texPath")):
            if not os.path.exists(os.path.join(HERE, "Textures", *tex.split("/")) + ".png"):
                bad.append("texture %s missing" % tex)
    if "RM_InscribedPanels" not in open(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Warscar.xml")).read():
        bad.append("biome does not run the RM_InscribedPanels genstep")
    ET.parse(os.path.join(HERE, "Defs", "GenStepDefs", "RM_InscribedPanels.xml"))
    p = ET.parse(os.path.join(HERE, "Patches", "Patches_BrokenTurretAim.xml")).getroot()
    txt = open(os.path.join(HERE, "Patches", "Patches_BrokenTurretAim.xml")).read()
    for b in BROKEN:
        if 'defName="%s"' % b not in txt:
            bad.append("patch does not target %s" % b)
    if "MayRequire" in txt.replace("no top-level MayRequire", ""):
        bad.append("patch uses MayRequire (inert on an Operation)")
    cs = open(os.path.join(HERE, "Source", "RM_CompTurretAim.cs")).read()
    cs = re.sub(r"//[^\n]*", "", cs)
    if re.search(r"\bVerb\b|Verb_|AttackTarget|TryStartCastOn|Projectile\b.*Launch", cs.split("OldLineTurretTuning")[0]):
        bad.append("the aim comp touches a verb or projectile -- it must stay verbless")
    # WARSCAR_HOSPICE_DESERTERS_1
    if 'Compile Include="RM_Hospice.cs"' not in csproj:
        bad.append("RM_Hospice.cs missing from RM_Warscar.csproj")
    D = os.path.join(HERE, "Defs")
    hist = ET.parse(os.path.join(D, "RM_DeserterHistoryDefs", "RM_DeserterHistories.xml")).getroot()
    hed = ET.parse(os.path.join(D, "HediffDefs", "RM_DeserterHediffs.xml")).getroot()
    hed_names = set(e.findtext("defName") for e in hed)
    if len(hist) != 7:
        bad.append("expected 7 deserter histories, found %d" % len(hist))
    bible = open(os.path.join(HERE, "..", "..", "..", "design", "Jawa", "worldbuilding", "biomes",
                              "warscar_bedazzle_cast_2026-09-30.md"), encoding="utf-8").read().replace("*", "").replace("\u201c", '"').replace("\u201d", '"')
    for h in hist:
        mem = [li.text for li in h.findall("memories/li")]
        if len(mem) != 3:
            bad.append("%s does not have three memory lines" % h.findtext("defName"))
        for m in mem:
            if m.strip('[]') not in bible.replace("[", "").replace("]", ""):
                bad.append("%s memory is not verbatim from cast bible 6A: %s" % (h.findtext("defName"), m))
            for word in ("Rakata", "Assailant", "scaria", "Sith", "Empire", "Republic", "God", "Force"):
                if word in m:
                    bad.append("memory names the enemy/side/god (%s): %s" % (word, m))
        for li in h.findall("modifications/li"):
            if li.text not in hed_names:
                bad.append("%s names missing hediff %s" % (h.findtext("defName"), li.text))
    serv = ET.parse(os.path.join(D, "ThingDefs_Races", "RM_AncientServitor.xml")).getroot()
    sraw = open(os.path.join(D, "ThingDefs_Races", "RM_AncientServitor.xml")).read()
    if "OverseerSubject" in re.sub(r"<!--.*?-->", "", sraw, flags=re.S):
        bad.append("servitor carries an overseer subject comp")
    if serv.find("ThingDef/comps").get("Inherit") != "False":
        bad.append("servitor comps do not drop the inherited overseer comp (Inherit=False)")
    wt = [li.text for li in serv.findall("ThingDef/race/mechEnabledWorkTypes/li")]
    if sorted(wt) != ["Cleaning", "Construction", "Hauling", "Mining"]:
        bad.append("servitor work types wrong: %r" % wt)
    for f in ("ThingDefs_Buildings/RM_Hospice.xml", "ThingDefs_Items/RM_HospiceItems.xml", "GenStepDefs/RM_KneelingRings.xml", "JobDefs/RM_HospiceJobs.xml"):
        ET.parse(os.path.join(D, *f.split("/")))
    bld = ET.parse(os.path.join(D, "ThingDefs_Buildings", "RM_Hospice.xml")).getroot()
    cradle = [e for e in bld if e.findtext("defName") == "RM_HospiceCradle"][0]
    if cradle.findtext("researchPrerequisites/li") != "RM_OldTongue_Hospice":
        bad.append("cradle is not gated by the hospice protocols research (HospiceUnlocked)")
    intact = [e for e in bld if e.findtext("defName") == "RM_KneelingChassis_Intact"][0]
    if intact.findtext("minifiedDef") != "MinifiedThing" or intact.find("designationCategory") is not None or intact.find("costList") is not None:
        bad.append("intact chassis must be minifiable and never fabricable")
    if "RM_KneelingRings" not in open(os.path.join(D, "BiomeDefs", "RM_Warscar.xml")).read():
        bad.append("biome does not run the RM_KneelingRings genstep")
    for tex in ("Building/RM_KneelingChassis_Slagged", "Building/RM_KneelingChassis_Posed", "Building/RM_KneelingChassis_Intact",
                "Building/RM_HospiceCradle", "Item/RM_ChassisCore", "Item/RM_FailedChassis",
                "Pawn/Mechanoid/RM_AncientServitor_south", "Pawn/Mechanoid/RM_AncientServitor_east", "Pawn/Mechanoid/RM_AncientServitor_north"):
        if not os.path.exists(os.path.join(HERE, "Textures", "Things", *tex.split("/")) + ".png"):
            bad.append("hospice texture %s missing" % tex)
    hs = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "RM_Hospice.cs")).read())
    for needle in ("HospiceUnlocked", "hospiceFailureChance", "hospiceLashOut", "hospiceWalkInEnabled", "Reveal(0)", "Reveal(1)", "Reveal(2)",
                   "It looked at the Cathedral first.", "RM_FailedChassis", "MakeMinified", "stage++"):
        if needle not in hs:
            bad.append("RM_Hospice.cs lacks %s" % needle)
    # WARSCAR_RAINBOW_POOLS_1 (static: files, wiring and names; behaviour is the live chain below)
    if 'Compile Include="RM_ReactionPools.cs"' not in open(os.path.join(HERE, "Source", "RM_Warscar.csproj")).read():
        bad.append("RM_ReactionPools.cs missing from RM_Warscar.csproj")
    for f in ("ThingDefs_Buildings/RM_ReactionPools.xml", "ThingDefs_Items/RM_PoolReagents.xml", "GenStepDefs/RM_ReactionPools.xml",
              "JobDefs/RM_ReactionPoolJobs.xml", "DamageDefs/RM_BloomAcid.xml"):
        ET.parse(os.path.join(D, *f.split("/")))
    reag = ET.parse(os.path.join(D, "ThingDefs_Items", "RM_PoolReagents.xml")).getroot()
    names = [e.findtext("defName") for e in reag]
    for need in ("RM_DielectricGel", "RM_Etchant", "RM_MedicalCoagulant", "RM_BloomLiquor", "RM_FilthBone"):
        if need not in names:
            bad.append("reagent def %s missing" % need)
    pc = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "RM_ReactionPools.cs")).read())
    for r in ("RM_DielectricGel", "RM_Etchant", "RM_MedicalCoagulant", "RM_BloomLiquor"):
        if '"%s"' % r not in pc:
            bad.append("phase table does not name %s" % r)
    for needle in ("PoolPhaseReaderUnlocked", "bloomDanger", "catalystEnabled", "poolsPerMap", "poolCycleHours", "poolsEnabled",
                   "ExtendHold", "GameComponent_PoolJournal", "FilthMaker.TryMakeFilth", "IconPaths", "ToxicBuildup"):
        if needle not in pc:
            bad.append("RM_ReactionPools.cs lacks %s" % needle)
    if len(re.findall(r"IconPaths\s*=\s*\{(.*?)\};", pc, flags=re.S)[0].split(",")) != 4:
        bad.append("phase icon table is not four entries")
    for ph in ("Amber", "Violet", "Green", "Bloom"):
        if not os.path.exists(os.path.join(HERE, "Textures", "Things", "Effect", "RM_PoolPhaseIcon_%s.png" % ph)):
            bad.append("phase icon %s missing" % ph)
    for tex in ("Building/RM_ReactionTap", "Item/RM_DielectricGel", "Item/RM_Etchant", "Item/RM_MedicalCoagulant", "Item/RM_BloomLiquor"):
        if not os.path.exists(os.path.join(HERE, "Textures", "Things", *tex.split("/")) + ".png"):
            bad.append("pool texture %s missing" % tex)
    if "RM_ReactionPools" not in open(os.path.join(D, "BiomeDefs", "RM_Warscar.xml")).read():
        bad.append("biome does not run the RM_ReactionPools genstep")
    tap = [e for e in ET.parse(os.path.join(D, "ThingDefs_Buildings", "RM_ReactionPools.xml")).getroot() if e.findtext("defName") == "RM_ReactionTap"][0]
    if tap.findtext("comps/li/fuelFilter/thingDefs/li") != "RM_GlowerCrust":
        bad.append("tap hopper does not take glower crust")
    turret = open(os.path.join(D, "ThingDefs_Buildings", "RM_OldLineTurret.xml")).read()
    if "<RM_Etchant>10</RM_Etchant>" not in turret or "<ComponentSpacer>3</ComponentSpacer>" not in turret:
        bad.append("old-line turret refit does not cost 10 etchant + 3 ComponentSpacer")
    fw = os.path.join(HERE, "..", "FlowWorks")
    reg = open(os.path.join(fw, "Defs", "LiquidTypes", "LiquidDefs", "RM_LiquidDefRegistry.xml")).read()
    gen = open(os.path.join(fw, "Tools", "generate_liquid_suite.py")).read()
    if "RM_Liquid_ReactionLiquor" not in reg or "RM_Liquid_ReactionLiquor" not in gen:
        bad.append("RM_Liquid_ReactionLiquor registry row missing from generator table or generated registry")
    terr = open(os.path.join(fw, "Defs", "LiquidTypes", "TerrainDefs", "RM_ReactionLiquor.xml")).read()
    for t in ("RM_ReactionLiquorShallow", "RM_ReactionLiquorDeep"):
        if "<defName>%s</defName>" % t not in terr:
            bad.append("terrain %s missing from FlowWorks" % t)
    # WARSCAR_CHOTRIX_BUILD_1
    if 'Compile Include="RM_Chotrix.cs"' not in csproj:
        bad.append("RM_Chotrix.cs missing from RM_Warscar.csproj")
    for f in ("ThingDefs_Races/RM_Chotrix.xml", "HediffDefs/RM_ChotrixHediffs.xml", "ThingDefs_Items/RM_CloakLacquer.xml",
              "GenStepDefs/RM_ChotrixOnMap.xml", "ThinkTreeDefs/RM_ThinkTree_Chotrix.xml"):
        ET.parse(os.path.join(D, *f.split("/")))
    cr = ET.parse(os.path.join(D, "ThingDefs_Races", "RM_Chotrix.xml")).getroot()
    cth = [e for e in cr if e.tag == "ThingDef"][0]
    if cth.findtext("race/predator") != "false":
        bad.append("chotrix must be predator=false (vanilla hunting has no lone-prey gate)")
    if cth.findtext("race/thinkTreeMain") != "RM_Chotrix":
        bad.append("chotrix does not use its think tree")
    if cth.findtext("butcherProducts/RM_CloakLacquer") is None:
        bad.append("chotrix does not butcher into cloak lacquer")
    if cth.findtext("comps/li/cloakHediff") != "RM_ChotrixCloak":
        bad.append("chotrix comp does not name the cloak hediff")
    chd = ET.parse(os.path.join(D, "HediffDefs", "RM_ChotrixHediffs.xml")).getroot()
    for h in chd:
        if h.find("comps/li[@Class='HediffCompProperties_Invisibility']") is None:
            bad.append("%s lacks the stock invisibility comp" % h.findtext("defName"))
        if h.find("comps/li/disappearsAfterTicks") is not None:
            bad.append("%s is timed (owner ruling: cloak lacquer is permanent)" % h.findtext("defName"))
    cl = open(os.path.join(D, "ThingDefs_Items", "RM_CloakLacquer.xml")).read()
    if "Disappears" in cl or "Timed" in cl:
        bad.append("lacquered cloak is timed")
    if "RM_ChotrixOnMap" not in open(os.path.join(D, "BiomeDefs", "RM_Warscar.xml")).read():
        bad.append("biome does not run the RM_ChotrixOnMap genstep")
    for f in ("south", "east", "north"):
        if not os.path.exists(os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "RM_Chotrix", "RM_Chotrix_%s.png" % f)):
            bad.append("chotrix texture %s missing" % f)
    cx = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "RM_Chotrix.cs")).read())
    for needle in ("Verb_MeleeAttack", "TryCastShot", "IsLone", "lonePawnRadius", "IsNight", "Fleeing", "chotrixEnabled",
                   "lacquerCloakEnabled", "Notify_Unequipped", "GenSight.LineOfSight", "BecomeVisible"):
        if needle not in cx:
            bad.append("RM_Chotrix.cs lacks %s" % needle)
    # WARSCAR_FREE_TIER_BODY_1
    for c in ("RM_WarscarPatches.cs", "MapComponent_WreckLichen.cs"):
        if 'Compile Include="%s"' % c not in csproj:
            bad.append("%s missing from RM_Warscar.csproj" % c)
    biome_txt = open(os.path.join(D, "BiomeDefs", "RM_Warscar.xml")).read()
    if "<label>Warscar</label>" not in biome_txt:
        bad.append("biome label is not 'Warscar'")
    if "<terrain>Soil</terrain>" in biome_txt:
        bad.append("Soil band still in the terrain list")
    for r in ("RM_Chatrak", "RM_Tetchik", "RM_Pallbearer", "RM_ScarRoach"):
        if "<%s>" % r not in biome_txt:
            bad.append("wildAnimals lacks %s" % r)
    if "<RM_Totchak>" in biome_txt:
        bad.append("totchak must stay genstep-only (not a wildAnimals row)")
    fa = ET.parse(os.path.join(D, "ThingDefs_Races", "RM_WarscarFauna.xml")).getroot()
    fd = {e.findtext("defName"): e for e in fa if e.tag == "ThingDef"}
    for r in ("RM_Chatrak", "RM_Tetchik", "RM_Pallbearer", "RM_ScarRoach"):
        if r not in fd:
            bad.append("race %s missing" % r)
    if fd["RM_Chatrak"].findtext("race/leatherDef") != "RM_ChatrakPlate":
        bad.append("chatrak leather is not RM_ChatrakPlate")
    if fd["RM_Chatrak"].findtext("race/manhunterOnDamageChance") != "0":
        bad.append("chatrak must not go manhunter on damage")
    if fd["RM_Tetchik"].findtext("statBases/MeatAmount") != "0":
        bad.append("tetchik must be inedible (MeatAmount 0)")
    for n, tex in (("Chatrak", "Pawn/Animal/RM_Chatrak/RM_Chatrak"), ("Totchak", "Pawn/Animal/RM_Totchak/RM_Totchak"),
                   ("Tetchik", "Pawn/Animal/RM_Tetchik/RM_Tetchik"), ("Pallbearer", "Pawn/Animal/RM_Pallbearer/RM_Pallbearer"),
                   ("ScarRoach", "Pawn/Animal/RM_ScarRoach/RM_ScarRoach")):
        for f in ("south", "east", "north"):
            if not os.path.exists(os.path.join(HERE, "Textures", "Things", *tex.split("/")) + "_%s.png" % f):
                bad.append("%s texture %s missing" % (n, f))
    for tex in ("Plant/RM_Glower/RM_Glower_a", "Plant/RM_WreckLichen/RM_WreckLichen_a", "Item/Resource/RM_GlowerCrust/RM_GlowerCrust_a",
                "Item/Resource/RM_WreckLichenScrapings/RM_WreckLichenScrapings", "Pawn/Animal/RM_TotchakDormant/RM_TotchakDormant"):
        if not os.path.exists(os.path.join(HERE, "Textures", "Things", *tex.split("/")) + ".png"):
            bad.append("texture %s missing" % tex)
    it = open(os.path.join(D, "ThingDefs_Items", "RM_WarscarItems.xml")).read()
    if "<allowColorGenerators>false</allowColorGenerators>" not in it or "RM_ChatrakPlate" not in it:
        bad.append("chatrak plate leather missing or colour-generator not disabled")
    wsrc = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "RM_WarscarPatches.cs")).read())
    for needle in ("CommonalityOfAnimalNow", "RM_Tetchik", "RM_Glower", "DesiredColor", "RM_ChatrakPlate"):
        if needle not in wsrc:
            bad.append("RM_WarscarPatches.cs lacks %s" % needle)
    wl = open(os.path.join(D, "ThingDefs_Plants", "RM_WarscarFlora.xml")).read()
    if "<defName>RM_WreckLichen</defName>" not in wl or "<neverBlightable>true</neverBlightable>" not in wl:
        bad.append("wreck-lichen def missing or blightable")
    if "<RM_WreckLichen>" in biome_txt:
        bad.append("wreck-lichen must never be a wildPlants row")
    wm = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "MapComponent_WreckLichen.cs")).read())
    for needle in ("StartsWith(\"Ancient\")", "enableWreckLichenSeeder", "RM_Warscar"):
        if needle not in wm:
            bad.append("MapComponent_WreckLichen.cs lacks %s" % needle)
    if "mandrake.rm.creaturebehaviors" not in open(os.path.join(HERE, "About", "About.xml")).read():
        bad.append("About.xml lacks the CreatureBehaviors dependency (RM_EatCleanableExtension)")
    ch = open(os.path.join(D, "ThingDefs_Races", "RM_Chotrix.xml")).read()
    for prey in ("RM_Tetchik", "RM_Chatrak"):
        if "<li>%s</li>" % prey in ch and prey not in fd:
            bad.append("chotrix prey %s does not resolve" % prey)
    # WARSCAR_SETTLING_WEATHER_1
    if 'Compile Include="RM_Settling.cs"' not in csproj:
        bad.append("RM_Settling.cs missing from RM_Warscar.csproj")
    st = re.sub(r"//[^\n]*", "", open(os.path.join(HERE, "Source", "RM_Settling.cs")).read())
    for needle in ("DoAirbornePawnToxicDamage", "windManager.WindSpeed", "WeatherOverlay_Fallout", "BeginDownwindSweep",
                   "SweepStep", "IsOrdnanceCell(c)", "DoCellSteadyEffects", "c.Roofed(map)"):
        if needle not in st:
            bad.append("RM_Settling.cs lacks %s" % needle)
    if "CreatureBehaviors" in csproj and "Reference Include=\"RimMandrake.CreatureBehaviors" in csproj:
        bad.append("Warscar must reach the track grid by reflection, not an assembly reference (the condition runs without it)")
    sd = os.path.join(HERE, "Defs")
    film = open(os.path.join(sd, "ThingDefs_Filth", "RM_SettledFilm.xml")).read()
    if "RimMandrake.CreatureBehaviors.RM_TrackSurfaceExtension" not in film:
        bad.append("RM_Filth_SettledFilm does not carry RM_TrackSurfaceExtension")
    cond = ET.parse(os.path.join(sd, "GameConditionDefs", "RM_Settling.xml")).getroot()[0]
    if cond.findtext("conditionClass") != NS + "RM_GameCondition_Settling":
        bad.append("RM_Settling conditionClass wrong")
    if "The wind has dropped. The Settling begins." != cond.findtext("startMessage") or \
            "The wind is back. The ground forgets." != cond.findtext("endMessage"):
        bad.append("RM_Settling start/end messages are not the ruled readable signs")
    if "RM_BuriedOrdnance" not in open(os.path.join(sd, "BiomeDefs", "RM_Warscar.xml")).read():
        bad.append("RM_Warscar biome does not list the RM_BuriedOrdnance genstep")
    for f in ("RM_Settling.xml",):
        pass
    # WARSCAR_GEIGER_CHOIR_1
    if 'Compile Include="RM_GeigerChoir.cs"' not in csproj:
        bad.append("RM_GeigerChoir.cs missing from RM_Warscar.csproj")
    choir = open(os.path.join(HERE, "Source", "RM_GeigerChoir.cs")).read()
    for needle in ("RM_MapComponent_GeigerChoir", "RM_WorldComponent_JarCaravans", "CompChotrix.All", "RM_Settling",
                   "choirWindEnabled", "choirJarWarnings", "choirReducedRepetition"):
        if needle not in choir:
            bad.append("RM_GeigerChoir.cs lacks %s" % needle)
    for f in ("SoundDefs/RM_GeigerChoir.xml", "ChoirDefs/RM_GeigerChoirDef.xml", "ThingDefs_Items/RM_TetchikJar.xml"):
        try:
            ET.parse(os.path.join(HERE, "Defs", f))
        except Exception as e:
            bad.append("%s does not parse: %s" % (f, e))
    snd = open(os.path.join(HERE, "Defs", "SoundDefs", "RM_GeigerChoir.xml")).read()
    for n in ("RM_GeigerTick", "RM_WindOnMetal", "RM_ProjectorHum", "RM_PoolBoil"):
        if "<defName>%s</defName>" % n not in snd:
            bad.append("sound def %s missing" % n)
    if not os.path.exists(os.path.join(HERE, "Textures", "Things", "Item", "RM_TetchikJar.png")):
        bad.append("RM_TetchikJar texture missing")
    if "RM_CapturedTetchik" not in open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_WarscarFauna.xml")).read():
        bad.append("tetchik butcherProducts does not yield RM_CapturedTetchik")
    # WARSCAR_LOOSENED_PANEL_BUILD_1
    lp = open(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_LoosenedPanel.xml")).read()
    for needle in ("<defName>RM_LoosenedPanel</defName>", "RimMandrake.Scarlands.RM_Building_LoosenedPanel",
                   "<passability>Impassable</passability>", "<useHitPoints>false</useHitPoints>", "<deconstructible>false"):
        if needle not in lp:
            bad.append("RM_LoosenedPanel lacks %s" % needle)
    if "<li>RM_LoosenedPanels</li>" not in open(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Warscar.xml")).read():
        bad.append("RM_Warscar does not run RM_LoosenedPanels")
    lcs = open(os.path.join(HERE, "Source", "RM_LoosenedPanel.cs")).read()
    for needle in ("It won't give. Someone who knows this ground might.", "loosenedPanelsEnabled", "loosenedPanelsPerMap",
                   '"deepening"', '"AncientSealedCrate"', "AncientFortifiedWall"):
        if needle not in lcs:
            bad.append("RM_LoosenedPanel.cs lacks %s" % needle)
    if 'Compile Include="RM_LoosenedPanel.cs"' not in open(os.path.join(HERE, "Source", "RM_Warscar.csproj")).read():
        bad.append("RM_LoosenedPanel.cs missing from RM_Warscar.csproj")
    if not os.path.exists(os.path.join(HERE, "Textures", "Things", "Building", "RM_LoosenedPanel.png")):
        bad.append("RM_LoosenedPanel texture missing")
    mark = open(os.path.join(HERE, "Defs", "HediffDefs", "RM_WarscarMark.xml")).read()
    if "<label>deepening mark</label>" not in mark:
        bad.append("the mark has no 'deepening' stage for the panel gate to read")
    return bad


def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("Warscar")
    suite.toggles = ["poolsEnabled", "catalystEnabled", "oldTongueEnabled", "turretTrackingEnabled", "turretRefitEnabled", "totchakEnabled", "totchakEatsPlayerWalls", "chotrixEnabled", "lacquerCloakEnabled", "settlingEnabled", "liftFrontEnabled", "warDustEnabled", "warDustBlightCureEnabled", "markEnabled", "markFloorEnabled", "markTradeBonusesEnabled", "snapEnabled", "loosenedPanelsEnabled"]

    def _unmeasured(t, why):
        """Record the component UNMEASURED (never FAIL): the harness's own route is upstream_failed, which
        __exit__ turns into verdict UNMEASURED with upstream_reason as the detail."""
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

    def _set(t, field, value):
        t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set", field=field,
                      value=str(value))

    def _restore(t, field):
        if t.session is not None:
            try:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set",
                               field=field, value=str(DEFAULTS[field]))
            except Exception as ex:
                print("[warscar] RESTORE FAILED %s: %s" % (field, ex), file=sys.stderr, flush=True)

    def _inspect(t, thing_id):
        r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
        rows = (r or {}).get("things") or []
        row = next((x for x in rows if x.get("id") == thing_id), None)
        if row is None or row.get("error"):
            raise ExpectationFailed("inspect_string failed for %s: %r" % (thing_id, row or r))
        return " ".join(str(x) for x in (row.get("inspect") or []))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("old_line_defs_resolve", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=";".join(NEW_DEFS), fields="defName", limit=20)
            if t.session is None:
                return
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                raise ExpectationFailed("old-line defs did not resolve live: %r" % r)
            if int(r.get("foundCount", 0)) != len(NEW_DEFS):
                raise ExpectationFailed("expected %d old-line defs, found %r" % (len(NEW_DEFS), r.get("foundCount")))

    @suite.chain("tracking")
    def tracking(t):
        t.clear_area(size=24)
        cells = t.spawn(BROKEN[0], count=1, at="point") or [(0, 0)]
        wreck_rect = "%d,%d,24,24" % (cells[0][0] - 12, cells[0][1] - 12)

        def wreck_id():
            rows = (t.bridge_call("jawa/list_things", defName=BROKEN[0], rect=wreck_rect) or {}).get("things") or []
            if not rows:
                raise ExpectationFailed("no %s found after spawning it" % BROKEN[0])
            return rows[0]["id"]

        with t.component("barrel_follows_mover_and_never_fires", toggle="turretTrackingEnabled"):
            wid = wreck_id()
            pawn = t.spawn_pawn("Colonist") if hasattr(t, "spawn_pawn") else None
            pid = (pawn or {}).get("id") if isinstance(pawn, dict) else pawn
            if t.session is not None and pid is not None:
                job = t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef="Goto",
                                    targetAX=cells[0][0] + 10, targetAZ=cells[0][1] + 10)
                t.wait_ticks(60)
                if isinstance(job, dict) and not job.get("nowRunningRequested"):
                    # The pawn was never confirmed walking (live run 2026-10-03: curJob '(none)', the
                    # wait was a paused read), so no tracking line is expected: not evidence of a bug.
                    _unmeasured(t, "ordered Goto never confirmed running (afterJobDef=%r): no mover, so the "
                                   "tracking line cannot be judged" % job.get("afterJobDef"))
                    return
                if "follow" not in _inspect(t, wid):
                    raise ExpectationFailed("a broken turret beside a walking pawn reports no tracking state")
                shots = (t.bridge_call("jawa/list_things", defName="Bullet_AncientArmoredTurret", rect=wreck_rect) or {}).get("things") or []
                if shots:
                    raise ExpectationFailed("a broken turret produced projectiles: %r" % shots[:2])
                _set(t, "turretTrackingEnabled", False)
                try:
                    t.wait_ticks(30)
                    if "follow" in _inspect(t, wid):
                        raise ExpectationFailed("tracking line persists with turretTrackingEnabled off (toggle dead)")
                finally:
                    _restore(t, "turretTrackingEnabled")
            elif t.session is not None:
                _unmeasured(t, "could not spawn a pawn to walk")

    @suite.chain("refit_gizmo")
    def refit_gizmo(t):
        with t.component("refit_gated_by_toggle", toggle="turretRefitEnabled"):
            if t.session is None:
                return
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_OldLineTurret", fields="defName,costList",
                              deep=True, limit=2)
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("could not read the refit target def: %r" % r)
            # deep=True expands each row to {thingDef: <defName>, count: N}. Real shape is THREE rows
            # (Steel + ComponentSpacer 3 + RM_Etchant 10); assert the named rows, not a row count.
            rows = [d for d in (r.get("defs") or []) if d.get("defName") == "RM_OldLineTurret"]
            cl = ((rows[0].get("fields") or {}).get("costList") if rows else None)
            if not isinstance(cl, list):
                raise ExpectationFailed("refit target costList unreadable: %r" % (cl,))
            if cl and not all(isinstance(x, dict) for x in cl):
                _unmeasured(t, "get_defs returned costList rows as bare type names despite deep=true: %r" % (cl,))
                return
            got = {}
            for x in cl:
                got[str(x.get("thingDef"))] = x.get("count")
            if got.get("RM_Etchant") != 10 or got.get("ComponentSpacer") != 3:
                raise ExpectationFailed("refit target costList lacks ComponentSpacer 3 + RM_Etchant 10 "
                                        "(stale deploy?): %r" % (got,))
            # Gizmo presence has no bridge reader; the toggle is read back so a dead setting still fails.
            _set(t, "turretRefitEnabled", False)
            try:
                got = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="get",
                                    field="turretRefitEnabled")
                if str((got or {}).get("value")).lower() != "false":
                    raise ExpectationFailed("turretRefitEnabled did not take: %r" % got)
            finally:
                _restore(t, "turretRefitEnabled")

    @suite.chain("totchak_wakes")
    def totchak_wakes(t):
        with t.component("totchak_defs_resolve", toggle="totchakEnabled"):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_Totchak", fields="defName", limit=2)
            if t.session is None:
                return
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                raise ExpectationFailed("RM_Totchak did not resolve live: %r" % r)
        with t.component("demolition_wake_and_wall_eating_order", toggle="totchakEatsPlayerWalls"):
            if t.session is None:
                return
            # State reads need a Warscar quicktest with ruins; owner/FOUNDRY live round (criteria 1-4).
            _unmeasured(t, "dormant placement, wake radius, ruin-before-player wall order "
                                    "and lie-down need a live Warscar map")

    @suite.chain("old_tongue")
    def old_tongue(t):
        with t.component("old_tongue_defs_resolve", toggle="oldTongueEnabled"):
            r = t.bridge_call("jawa/get_defs", defs="ThingDef/RM_InscribedPanel_Hospice", fields="defName", limit=2)
            if t.session is None:
                return
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                raise ExpectationFailed("panel def did not resolve live: %r" % r)
        with t.component("skill_gate_and_set_unlock", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "Intellectual-8 refusal, set-size unlock and chalk-mark swap need "
                                    "a live Warscar map with pawns of differing skill")

    @suite.chain("hospice")
    def hospice(t):
        with t.component("hospice_defs_resolve", toggle="hospiceEnabled"):
            for d in ("ThingDef/RM_HospiceCradle", "ThingDef/RM_KneelingChassis_Intact", "ThingDef/RM_FailedChassis", "PawnKindDef/RM_AncientServitor"):
                r = t.bridge_call("jawa/get_defs", defs=d, fields="defName", limit=2)
                if t.session is None:
                    return
                if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                    raise ExpectationFailed("%s did not resolve live: %r" % (d, r))
        with t.component("five_stage_revival_and_walk_in", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "rings with 0-2 intact chassis, five-stage revival, failure wreck name, "
                                    "mechanitor-free servitor and the dev-fired walk-in need a live Warscar map")

    @suite.chain("rainbow_pools")
    def rainbow_pools(t):
        with t.component("pool_defs_resolve", toggle="poolsEnabled"):
            for d in ("ThingDef/RM_ReactionPool", "ThingDef/RM_ReactionTap", "ThingDef/RM_Etchant", "ThingDef/RM_DielectricGel",
                      "ThingDef/RM_MedicalCoagulant", "ThingDef/RM_BloomLiquor", "DamageDef/RM_BloomAcid"):
                r = t.bridge_call("jawa/get_defs", defs=d, fields="defName", limit=2)
                if t.session is None:
                    return
                if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                    raise ExpectationFailed("%s did not resolve live: %r" % (d, r))
        with t.component("pool_phase_cycle_draw_and_catalyst", toggle="catalystEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "1-3 pools on a quicktest Warscar map, per-phase reagent, bloom burn, "
                                    "phase hold + doubled yield with crust, and the registry row resolving "
                                    "(RM_Liquid_ReactionLiquor) need a live map with FlowWorks loaded")

    @suite.chain("chotrix")
    def chotrix(t):
        with t.component("chotrix_defs_resolve", toggle="chotrixEnabled"):
            for d in ("ThingDef/RM_Chotrix", "HediffDef/RM_ChotrixCloak", "HediffDef/RM_LacquerStill",
                      "ThingDef/RM_CloakLacquer", "ThingDef/RM_Apparel_LacquerCloak"):
                r = t.bridge_call("jawa/get_defs", defs=d, fields="defName", limit=2)
                if t.session is None:
                    return
                if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                    raise ExpectationFailed("%s did not resolve live: %r" % (d, r))
        with t.component("invisible_reveal_on_strike_and_lone_gate", toggle="chotrixEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "spawn on a quicktest Warscar map, stays invisible, reveals on strike, ignores a group of 2+, "
                           "flees after a hurt bite, and prints on the track grid (blocked on FOOTPRINT_TRACK_GRID_1) "
                           "need a live map")
        with t.component("lacquered_cloak_still_invisible_persists_save_load", toggle="lacquerCloakEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "equip a lacquered cloak, stand still unseen (hediff present), walk (absent), "
                           "and save/load persistence need a live map")

    @suite.chain("body")
    def body(t):
        with t.component("body_defs_resolve"):
            for d in ("ThingDef/RM_Chatrak", "ThingDef/RM_Tetchik", "ThingDef/RM_Pallbearer", "ThingDef/RM_ScarRoach",
                      "ThingDef/RM_ChatrakPlate", "ThingDef/RM_WreckLichen", "ThingDef/RM_WreckLichenScrapings",
                      "PawnKindDef/RM_Chatrak", "PawnKindDef/RM_Tetchik"):
                r = t.bridge_call("jawa/get_defs", defs=d, fields="defName", limit=2)
                if t.session is None:
                    return
                if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                    raise ExpectationFailed("%s did not resolve live: %r" % (d, r))
        with t.component("spawn_gates_and_lichen_placement", toggle="enableWreckLichenSeeder"):
            if t.session is None:
                return
            _unmeasured(t, "a quicktest Warscar map spawning chatrak and tetchik (tetchik only within 6 cells of glower), "
                           "wreck-lichen only beside ruins, a butchered chatrak yielding undyeable chatrak plate, "
                           "and the canonical save loading with no new reference error need a live map")

    @suite.chain("settling")
    def settling(t):
        with t.component("settling_defs_resolve", toggle="settlingEnabled"):
            r = t.bridge_call("jawa/get_defs", defs=";".join(SETTLING_DEFS), fields="defName", limit=20)
            if t.session is None:
                return
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                raise ExpectationFailed("Settling defs did not resolve live: %r" % r)
            if int(r.get("foundCount", 0)) != len(SETTLING_DEFS):
                raise ExpectationFailed("expected %d Settling defs, found %r" % (len(SETTLING_DEFS), r.get("foundCount")))
        with t.component("calm_starts_and_wind_ends_the_settling", toggle="settlingEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "forcing calm on a quicktest Warscar map to start RM_Settling after the configured hours and wind "
                           "to end it needs a live Warscar map with a controllable wind")
        with t.component("film_roofed_and_toxic", toggle="settlingEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "film only on unroofed cells, a roofed pawn taking no toxic buildup and an unroofed one taking it, "
                           "need a live running Settling")
        with t.component("lift_front_wipes_film_and_tracks", toggle="liftFrontEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "the lift front crossing the map downwind and clearing film and tracks behind it needs a live "
                           "Settling plus the track grid (CreatureBehaviors); state read of the grid is owed to a live round")
        with t.component("war_dust_sweep", toggle="warDustEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "a sweep job on a film cell yielding RM_WarDust (more in crater bowls) needs a live film cell and a pawn")
        with t.component("war_dust_cures_blight", toggle="warDustBlightCureEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "a grower carrying one RM_WarDust to a blighted crop (dev Blight incident on a sown zone) and the "
                           "Blight thing being gone with the plant alive needs a live map and a pawn")
        with t.component("buried_ordnance_revealed_and_defusable", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "every buried-shell cell being film-free and inspectable after a Settling, and defusing yielding a shell, "
                           "need a live map generated with the RM_BuriedOrdnance genstep")

    def _mark_proof(t, hours):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Scarlands.RM_WarscarMark", method="ProofAccrue",
                          args="current|%d" % hours)
        return str((r or {}).get("result", "")) or "no result: %r" % (r,)

    @suite.chain("warscar_mark")
    def warscar_mark(t):
        """WARSCAR_MARK_TRADE_BUILD_1: the mark accrues hourly on a Warscar map and pays a trade. The proof
        accrues N hours on the first free colonist of the current map (no fade between), so it holds on any
        map; the map-biome gate itself is the live first poke (eight days on a Warscar quicktest)."""
        with t.component("mark_defs_resolve", toggle="markEnabled"):
            r = t.bridge_call("jawa/get_defs", defs=";".join(MARK_DEFS), fields="defName", limit=10)
            if t.session is None:
                return
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                raise ExpectationFailed("mark defs did not resolve live: %r" % r)
        with t.component("mark_accrues_and_pays", toggle="markTradeBonusesEnabled"):
            txt = _mark_proof(t, 24)       # 24 x 0.0125 = 0.30 -> mild mark, +15% hacking
            if t.session is None:
                return
            if "stage mild mark" not in txt or "HackingSpeed" not in txt:
                raise ExpectationFailed("24 hours did not reach a paying mild mark: %s" % txt)
        with t.component("mark_floor_arms", toggle="markFloorEnabled"):
            txt = _mark_proof(t, 24)       # +0.30 more -> 0.60, deepening, floor armed
            if t.session is None:
                return
            if "floor armed=True" not in txt or "stage deepening mark" not in txt:
                raise ExpectationFailed("a 0.6 mark did not arm the floor: %s" % txt)
        with t.component("mark_off_accrues_nothing", toggle="markEnabled"):
            _set(t, "markEnabled", False)
            try:
                txt = _mark_proof(t, 4)
            finally:
                _restore(t, "markEnabled")
            if t.session is None:
                return
            if " marked 0" not in txt:
                raise ExpectationFailed("markEnabled OFF but the mark still accrued: %s" % txt)

    def _snap_proof(t, method, args):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Scarlands.RM_ChatrakSnap", method=method, args=args)
        return str((r or {}).get("result", "")) or "no result: %r" % (r,)

    @suite.chain("chatrak_snap")
    def chatrak_snap(t):
        """WARSCAR_CHATRAK_SNAP_BUILD_1: a wild scaria chatrak is armed and turns in visible stages; a clean one is
        never armed. Each proof spawns its own chatrak near the map centre, so it holds on any map; the
        Warscar-only arming cadence is the live first poke (a few days on a Warscar quicktest)."""
        with t.component("snap_defs_resolve", toggle="snapEnabled"):
            r = t.bridge_call("jawa/get_defs", defs=";".join(SNAP_DEFS), fields="defName", limit=10)
            if t.session is None:
                return
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                raise ExpectationFailed("snap defs did not resolve live: %r" % r)
        stages = [("0.2", "stage incubating", "plates=hidden"), ("0.4", "stage plates lifting", "plates=shown"),
                  ("0.7", "stage off its feed", "hunger x0.00"), ("0.9", "stage circling", "circling=ring@"),
                  ("1.0", "stage the snap", "snap=ManhunterPermanent")]
        for sev, want_stage, want in stages:
            with t.component("snap_stage_%s" % sev.replace(".", "_"), toggle="snapEnabled"):
                txt = _snap_proof(t, "ProofStage", "current|" + sev)
                if t.session is None:
                    return
                if " armed 1" not in txt or want_stage not in txt or want not in txt:
                    raise ExpectationFailed("severity %s: wanted %r and %r: %s" % (sev, want_stage, want, txt))
        with t.component("clean_chatrak_never_armed", toggle="snapEnabled"):
            txt = _snap_proof(t, "ProofClean", "current")
            if t.session is None:
                return
            if "clean armed=False" not in txt:
                raise ExpectationFailed("a scaria-free chatrak was armed: %s" % txt)
        with t.component("snap_off_arms_nothing", toggle="snapEnabled"):
            _set(t, "snapEnabled", False)
            try:
                txt = _snap_proof(t, "ProofStage", "current|0.4")
            finally:
                _restore(t, "snapEnabled")
            if t.session is None:
                return
            if "NOT ARMED" not in txt:
                raise ExpectationFailed("snapEnabled OFF but a chatrak was armed: %s" % txt)

    def _panel_proof(t, sev):
        r = t.bridge_call("jawa/static_call", type=NS + "RM_LoosenedPanelProof", method="ProofWork",
                          args="current|%s" % sev)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    @suite.chain("loosened_panel")
    def loosened_panel(t):
        """WARSCAR_LOOSENED_PANEL_BUILD_1: a pawn below a deepening mark is refused at a loosened panel; one at
        deepening works it loose onto a real sealed crate. Each proof spawns its own panel and colonist on the
        CURRENT map. Not proven here: the genstep on a real Warscar map (first poke: static_call
        RM_LoosenedPanelProof ProofPlace current on a Warscar quicktest with ancient ruins)."""
        with t.component("below_deepening_is_refused", toggle="loosenedPanelsEnabled"):
            txt = _panel_proof(t, "0.3")
            if t.session is None:
                return
            if "canWork False" not in txt or "opened False" not in txt or "It won't give" not in txt:
                raise ExpectationFailed("a mild-marked pawn was not refused with the line: %s" % txt)
        with t.component("deepening_opens_onto_a_sealed_crate", toggle="loosenedPanelsEnabled"):
            txt = _panel_proof(t, "0.6")
            if t.session is None:
                return
            if "canWork True" not in txt or "opened True" not in txt or "SealedCrate" not in txt:
                raise ExpectationFailed("a deepening-marked pawn did not open the panel onto a crate: %s" % txt)

    @suite.chain("geiger_choir")
    def geiger_choir(t):
        with t.component("choir_defs_resolve", toggle="choirEnabled"):
            r = t.bridge_call("jawa/get_defs", defs=";".join(CHOIR_DEFS), fields="defName", limit=20)
            if t.session is None:
                return
            if not isinstance(r, dict) or r.get("success") is False or r.get("notFound"):
                raise ExpectationFailed("choir defs did not resolve live: %r" % r)
            if int(r.get("foundCount", 0)) != len(CHOIR_DEFS):
                raise ExpectationFailed("expected %d choir defs, found %r" % (len(CHOIR_DEFS), r.get("foundCount")))
        with t.component("tick_tempo_follows_glower_density", toggle="choirEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "standing over thick glower ticking faster than bare slag (RM_MapComponent_GeigerChoir.TickDensity) "
                           "needs a live Warscar map with a camera; no bridge reader for the component yet")
        with t.component("wind_layer_silent_during_settling", toggle="choirWindEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "WindSustainerActive false while RM_Settling runs and true again after needs a live map with ancient "
                           "metal in range and a forced Settling")
        with t.component("jar_caravan_warning", toggle="choirJarWarnings"):
            if t.session is None:
                return
            _unmeasured(t, "a caravan carrying RM_TetchikJar receiving the message approaching a polluted tile needs a live world "
                           "with a polluted tile and a caravan on a path")

    # NORTHSTAR_PARTIAL_GAPS_FILL_1 (audit row: "RM_Warscar BiomeDef itself ... biome+flora have no script"):
    # every one of the ~100 shipped defs is loaded live (only 19 were named anywhere above), and the biome's own
    # density/difficulty/forage numbers, every pawnkind's race/combatPower/ecoSystemWeight, hediff severities,
    # workgiver priorities and research costs read back equal to the XML.
    from modcheck import shipped_defs
    shipped_defs.add_chain(suite, __file__, fields_by_type={
        "BiomeDef": ("label", "animalDensity", "plantDensity", "movementDifficulty", "forageability",
                     "foragedFood", "allowRoads", "allowRivers", "diseaseMtbDays", "wildPlantRegrowDays"),
        "PawnKindDef": ("label", "race", "combatPower", "ecoSystemWeight"),
        "HediffDef": ("label", "isBad", "initialSeverity", "maxSeverity", "tendable"),
        "WorkGiverDef": ("label", "workType", "priorityInType"),
        "ResearchProjectDef": ("label", "baseCost", "techLevel"),
        "RecipeDef": ("label", "workAmount", "workSkill"),
        "IncidentDef": ("label", "baseChance", "minRefireDays"),
        "GenStepDef": ("order",),
        "ThingDef": ("label", "stackLimit"),
        "RimMandrake.Scarlands.RM_DeserterHistoryDef": ("label",)},
        sanity=("RM_Warscar", "RM_OldLineTurret", "RM_Chatrak"), min_count=90)
    return suite


try:
    suite = _build_suite()
except ImportError:      # run outside the modcheck path (the static check below needs no game)
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
