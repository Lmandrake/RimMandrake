"""validation.py -- modcheck suite for RimMandrake: Miasma (mandrake.rm.miasma).

Item MIASMA_SETTINGS_SWITCHES_1. Covers the Mod Settings only; the biome's other mechanics have no script yet.

WHAT IT PROVES: every Miasma setting round-trips (set -> get -> restore) through `jawa/mod_settings_field`, and
the three switches this item added (plantPredationEnabled, pollinationGateEnabled, strandedDeformationEnabled
+ strandedDeformationChance) exist, default to shipped behaviour, and are Scribed and drawn.
NOT PROVEN HERE: that the mechanic stops firing with its switch off in a quicktest (criterion of the item):
predation needs a plant beside a wild scuttler, the gate needs a worldgen plant pass, deformation needs a
stranding pool. Each says UNMEASURED rather than passing.

STATIC (offline): `python3 validation.py` runs static_checks() without a game.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_TYPE = "RimMandrake.Miasma.RM_MiasmaSettings"
DEFAULTS = {"biomeRarityFactor": 1.0, "wardenSuccessionEnabled": True, "selfTameChancePerCheck": 0.12,
            "plantPredationEnabled": True, "pollinationGateEnabled": True,
            "strandedDeformationEnabled": True, "strandedDeformationChance": 0.25,
            "ambushFrogHunts": True, "flotsamEnabled": True, "flotsamAmount": 1.0}
NEW = ["plantPredationEnabled", "pollinationGateEnabled", "strandedDeformationEnabled", "strandedDeformationChance",
       "ambushFrogHunts", "attarEnabled"]


def static_checks():
    bad = []
    src = open(os.path.join(HERE, "Source", "RM_MiasmaMod.cs")).read()
    body = src.split("DoWindowContents(Rect")[1]
    for f, d in DEFAULTS.items():
        if '"%s"' % f not in src:
            bad.append("settings field %s is not Scribed" % f)
        if not re.search(r"\b%s\b" % f, body):
            bad.append("settings field %s has no control in DoWindowContents" % f)
        m = re.search(r"public static \w+ %s = ([^;]+);" % f, src)
        if not m:
            bad.append("settings field %s is not a public static" % f)
        elif m.group(1).lower().rstrip("f") != str(d).lower().rstrip("0").rstrip(".") and float(m.group(1).rstrip("f").replace("true", "1").replace("false", "0")) != float(d):
            bad.append("settings field %s default %s != shipped %s" % (f, m.group(1), d))
    pred = open(os.path.join(HERE, "Source", "RM_CompPlantPredator.cs")).read()
    if "RM_MiasmaSettings.plantPredationEnabled" not in pred:
        bad.append("RM_CompPlantPredator does not read plantPredationEnabled")
    for needle in ("strandedDeformationChance", "RM_PollinationGateExtension", "WriteSettings"):
        if needle not in src:
            bad.append("RM_MiasmaMod.cs lacks %s" % needle)
    proj = open(os.path.join(HERE, "Source", "RM_Miasma.csproj")).read()
    for cs in os.listdir(os.path.join(HERE, "Source")):
        if cs.endswith(".cs") and 'Compile Include="%s"' % cs not in proj:
            bad.append("%s missing from RM_Miasma.csproj" % cs)
    biome = open(os.path.join(HERE, "Defs", "BiomeDefs", "RM_Miasma.xml")).read()
    if "<strandedDeformationChance>0.25<" not in biome:
        bad.append("biome's shipped strandedDeformationChance is no longer 0.25 (default drift)")
    if "RM_MiasmaSaltCrust" not in biome:
        bad.append("RM_Miasma does not name RM_MiasmaSaltCrust (MIASMA_FREE_SALT_CRUST_1)")
    for m in re.finditer(r"<(landTerrain|dryTerrain)>([^<]*)<", biome):
        if m.group(2).startswith("RUT_"):
            bad.append("%s names campaign def %s" % (m.group(1), m.group(2)))
    tdef = os.path.join(HERE, "Defs", "TerrainDefs", "RM_MiasmaSaltCrust.xml")
    if not os.path.exists(tdef) or "<defName>RM_MiasmaSaltCrust</defName>" not in open(tdef).read():
        bad.append("RM_MiasmaSaltCrust TerrainDef missing")
    young = ["RM_CrimsonOpeeJuv", "RM_ThornbackColoJuv", "RM_ShaleGorgerJuv", "RM_ReefbackJuv"]
    races = open(os.path.join(HERE, "..", "TerminalBiomes", "Defs", "ThingDefs_Races", "RM_SeaBeasts_Invented.xml")).read()
    creche = open(os.path.join(HERE, "Defs", "MapGeneration", "RUT_Miasma_CrecheScatterer.xml")).read()
    for y in young:  # MIASMA_FREE_NURSERY_YOUNG_1
        if races.count("<defName>%s</defName>" % y) != 2:
            bad.append("%s needs exactly a ThingDef and a PawnKindDef in RM_SeaBeasts_Invented.xml" % y)
        if not re.search(r"<%s>[\d.]+</%s>" % (y, y), biome):
            bad.append("%s not in RM_Miasma wildAnimals" % y)
        if "<li>%s</li>" % y not in biome:
            bad.append("%s not in the stranding-pool strandedSpawnList" % y)
        if "<li>%s</li>" % y not in creche:
            bad.append("%s not in the creche youngKinds" % y)
    # MIASMA_AMBUSH_FROG_REMAKE_1
    frog = open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Bozzuga.xml")).read()
    if frog.count("<defName>RM_Bozzuga</defName>") != 2:
        bad.append("RM_Bozzuga needs exactly a ThingDef and a PawnKindDef")
    if "<predator>true</predator>" not in frog or "<maxPreyBodySize>" not in frog:
        bad.append("RM_Bozzuga is not a vanilla predator with a prey size cap")
    if not re.search(r"<RM_Bozzuga>[\d.]+</RM_Bozzuga>", biome):
        bad.append("RM_Bozzuga not in RM_Miasma wildAnimals")
    if not os.path.exists(os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "RM_Bozzuga", "RM_Bozzuga_south.png")):
        bad.append("RM_Bozzuga placeholder texture missing")
    if "RM_Bozzuga" not in open(os.path.join(HERE, "Source", "RM_AmbushFrogHunting.cs")).read():
        bad.append("RM_AmbushFrogHunting does not target RM_Bozzuga")
    # MIASMA_FLOTSAM_YARD_1
    fl = os.path.join(HERE, "Source", "RM_MapComponent_FlotsamYard.cs")
    if not os.path.exists(fl):
        bad.append("RM_MapComponent_FlotsamYard.cs missing")
    else:
        ft = open(fl).read()
        for needle in ("flotsamEnabled", "flotsamAmount", "LastRecedeCompletedTick", "RM_Thessamor", "RM_Thrannock"):
            if needle not in ft:
                bad.append("flotsam yard lacks %s" % needle)
    # MIASMA_ATTAR_STILL_1
    items = open(os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_Attar.xml")).read()
    for d in ("RM_Attar", "RM_AttarStill"):
        if items.count("<defName>%s</defName>" % d) != 1:
            bad.append("%s ThingDef missing or duplicated" % d)
    rec = open(os.path.join(HERE, "Defs", "RecipeDefs", "RM_MakeAttar.xml")).read()
    for needle in ("<li>RM_DeltaSilt</li>", "<li>RM_DeltaSalt</li>", "<RM_Attar>1</RM_Attar>", "<li>RM_AttarStill</li>"):
        if needle not in rec:
            bad.append("RM_MakeAttar lacks %s" % needle)
    if "<Medicine" in rec or "Medicine" in items:
        bad.append("attar must not be medicine (ban 3)")
    jobs = open(os.path.join(HERE, "Defs", "JobDefs", "RM_Jobs_Attar.xml")).read()
    for j in ("RM_GlazeArtwork", "RM_BalmScar"):
        if "<defName>%s</defName>" % j not in jobs:
            bad.append("JobDef %s missing" % j)
    att = open(os.path.join(HERE, "Source", "RM_Attar.cs")).read()
    if "attarEnabled" not in att or "IsPermanent()" not in att:
        bad.append("RM_Attar.cs must gate on attarEnabled and balm only permanent scars")
    for t in ("Textures/Things/Item/Resource/RM_Attar/RM_Attar.png", "Textures/Things/Building/RM_AttarStill/RM_AttarStill.png"):
        if not os.path.exists(os.path.join(HERE, t)):
            bad.append("missing texture " + t)
    if "StatPart_Glazed" not in open(os.path.join(HERE, "Patches", "RM_Attar_BeautyPart.xml")).read():
        bad.append("Beauty StatPart patch missing")
    # MIASMA_SWARM_COMPOSTER_PORT_1
    for root, _d, fs in os.walk(os.path.join(HERE, "Defs")):
        for f in fs:
            t = open(os.path.join(root, f), encoding="utf-8").read()
            for old in ("RUT_FeverSwarm", "RUT_Karrobel", "RUT_DeltaLoam"):
                if old in t:
                    bad.append("%s still names %s" % (f, old))
    if 'MayRequire="mandrake.rut.patches"' in biome:
        bad.append("RM_Miasma.xml still gates a row on mandrake.rut.patches")
    sw = open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_Miasma_FeverSwarmKarrobel.xml"), encoding="utf-8").read()
    for d in ("RM_FeverSwarm", "RM_Karrobel"):
        if sw.count("<defName>%s</defName>" % d) != 2:
            bad.append("%s needs exactly a ThingDef and a PawnKindDef" % d)
    if "<gatherDef>RM_DeltaLoam</gatherDef>" not in sw or "<defName>RM_DeltaLoam</defName>" not in open(os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_DeltaLoam.xml"), encoding="utf-8").read():
        bad.append("RM_DeltaLoam item or the karrobel's gatherDef missing")
    for r in ("RM_FeverSwarm", "RM_Karrobel"):
        if not re.search(r"<%s>[\d.]+</%s>" % (r, r), biome):
            bad.append("%s not in RM_Miasma wildAnimals" % r)
    mg = open(os.path.join(HERE, "Defs", "ThingDefs_Plants", "RM_Miasma_Mangals.xml"), encoding="utf-8").read()
    if mg.count("<pollinatorRace>RM_FeverSwarm</pollinatorRace>") != 2:
        bad.append("RM_Thessamor and RM_Quennath must each carry the pollination gate naming RM_FeverSwarm")
    for t in ("Pawn/Animal/RM_FeverSwarm/RM_FeverSwarm_south.png", "Pawn/Animal/RM_Karrobel/RM_Karrobel_south.png",
              "Item/Resource/RM_DeltaLoam/RM_DeltaLoam_a.png"):
        if not os.path.exists(os.path.join(HERE, "Textures", "Things", *t.split("/"))):
            bad.append("missing texture " + t)
    return bad


def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("Miasma")
    suite.toggles = ["attarEnabled", "plantPredationEnabled", "pollinationGateEnabled", "strandedDeformationEnabled", "wardenSuccessionEnabled"]

    def _call(t, action, field, value=None):
        kw = dict(typeName=SETTINGS_TYPE, action=action, field=field)
        if value is not None:
            kw["value"] = str(value)
        return t.bridge_call("jawa/mod_settings_field", **kw)

    @suite.chain("settings_roundtrip")
    def settings_roundtrip(t):
        for field in NEW:
            toggle = field if field.endswith("Enabled") else None
            with t.component("roundtrip_" + field, toggle=toggle) if toggle else t.component("roundtrip_" + field):
                if t.session is None:
                    continue
                got = _call(t, "get", field)
                if str((got or {}).get("value")).lower() != str(DEFAULTS[field]).lower().rstrip("0").rstrip(".") and \
                        str((got or {}).get("value")).lower() not in (str(DEFAULTS[field]).lower(), "0.25"):
                    raise ExpectationFailed("%s default is not the shipped value: %r" % (field, got))
                flip = (not DEFAULTS[field]) if isinstance(DEFAULTS[field], bool) else 0.5
                try:
                    _call(t, "set", field, flip)
                    back = _call(t, "get", field)
                    if str((back or {}).get("value")).lower() != str(flip).lower():
                        raise ExpectationFailed("%s did not take: %r" % (field, back))
                finally:
                    _call(t, "set", field, DEFAULTS[field])

    @suite.chain("switches_gate_mechanics")
    def switches_gate_mechanics(t):
        with t.component("mechanics_stop_with_switch_off", beyond_toggle=True):
            if t.session is None:
                return
            raise ExpectationFailed("UNMEASURED: predation (plant beside a wild scuttler), the pollination gate "
                                    "(worldgen plant pass) and stranded deformation (a stranding pool) each need "
                                    "a live Miasma quicktest map")

    @suite.chain("salt_crust_free_tier")
    def salt_crust_free_tier(t):
        with t.component("salt_crust_paints_without_campaign", beyond_toggle=True):
            if t.session is None:
                return
            raise ExpectationFailed("UNMEASURED: no 'Could not resolve' for a salt crust and a surge recede "
                                    "repainting land to RM_MiasmaSaltCrust need a tier without mandrake.rut.patches "
                                    "and a live Miasma map (also a bar for MIASMA_FIRST_SCRIPT_1)")

    @suite.chain("nursery_young_free_tier")
    def nursery_young_free_tier(t):
        with t.component("four_young_def_and_strand", beyond_toggle=True):
            if t.session is None:
                return
            raise ExpectationFailed("UNMEASURED: jawa/get_defs foundCount 4 on the four *Juv PawnKindDefs, and a "
                                    "recede on a free-only tier stranding at least one of them (spawn many), need "
                                    "a live Miasma map with the bridge")

    @suite.chain("ambush_frog_free_tier")
    def ambush_frog_free_tier(t):
        with t.component("bozzuga_defs_and_hunts", beyond_toggle=True):
            if t.session is None:
                return
            raise ExpectationFailed("UNMEASURED: jawa/get_defs foundCount 2 on RM_Bozzuga (ThingDef+PawnKindDef), "
                                    "spawn on a free-only Miasma map, and a bozzuga hunting a karrolun, need a live "
                                    "Miasma quicktest map with the bridge")

    @suite.chain("swarm_composter_free_tier")
    def swarm_composter_free_tier(t):
        with t.component("swarm_karrobel_spawn_and_gate", beyond_toggle=True):
            if t.session is None:
                return
            raise ExpectationFailed("UNMEASURED: jawa/get_defs foundCount 3 on RM_FeverSwarm/RM_Karrobel/RM_DeltaLoam, "
                                    "both creatures spawning on a free-only Miasma map, and a gated mangal (RM_Thessamor) "
                                    "not spreading where no swarm lives, need a live Miasma quicktest map")

    @suite.chain("flotsam_yard")
    def flotsam_yard(t):
        with t.component("flotsam_after_surge_in_root_lines", beyond_toggle=True):
            if t.session is None:
                return
            raise ExpectationFailed("UNMEASURED: flotsam stacks standing on root-line cells after a debug surge and "
                                    "recede (and none on dry inland ground) need a live Miasma quicktest map")

    @suite.chain("attar_glaze_and_balm")
    def attar_glaze_and_balm(t):
        with t.component("attar_recipe_glaze_balm", toggle="attarEnabled"):
            if t.session is None:
                return
            raise ExpectationFailed("UNMEASURED: RM_MakeAttar resolves on RM_AttarStill, a glazed sculpture's Beauty "
                                    "stat rises by 3, and a balmed pawn's permanent scar fades while no non-permanent "
                                    "injury changes; each needs a live Miasma quicktest map with an artwork and a scarred pawn")

    return suite


try:
    suite = _build_suite()
except ImportError:
    suite = None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
