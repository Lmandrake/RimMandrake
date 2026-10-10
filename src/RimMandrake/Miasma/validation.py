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
            "ambushFrogHunts": True, "flotsamEnabled": True, "flotsamAmount": 1.0, "youngCallEnabled": True,
            "attarEnabled": True, "decayCellsEnabled": True, "decayCellPowerMultiplier": 1.0,
            "rottingBedCorpsesEnabled": True, "rottingBedRotDays": 3.0,
            "mothersPriceEnabled": True, "youngPriceOffset": 1500.0}
# Every declared field round-trips (the first five were left out until 2026-10-06; the walk named the gap).
NEW = list(DEFAULTS)


def _same(got, want):
    """A bridge value string against a Python default: bools by name, numbers numerically ("1" == 1.0)."""
    g = str(got).strip().lower()
    if isinstance(want, bool):
        return g == str(want).lower()
    try:
        return abs(float(g) - float(want)) < 1e-6
    except ValueError:
        return False


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
    # MIASMA_YOUNG_CALL_1
    yc = os.path.join(HERE, "Source", "RM_MapComponent_YoungCall.cs")
    if not os.path.exists(yc):
        bad.append("RM_MapComponent_YoungCall.cs missing")
    else:
        yt = open(yc).read()
        for needle in ("youngCallEnabled", "RM_WardenMother", "RUT_StrandedDeformation", "IsWater", "JobDefOf.Goto"):
            if needle not in yt:
                bad.append("young call lacks %s" % needle)
    if "RM_MapComponent_YoungCall.cs" not in open(os.path.join(HERE, "Source", "RM_Miasma.csproj")).read():
        bad.append("RM_MapComponent_YoungCall.cs not in csproj Compile list")
    if "ApplyYoungCall" not in src or "callSound" not in src:
        bad.append("settings applier does not gate the shared cry (callSound)")
    kx = open(os.path.join(HERE, "Languages", "English", "Keyed", "RUT_Miasma_Mechanics.xml")).read()
    for k in ("RM_YoungCallLetterLabel", "RM_YoungCallLetterText"):
        if "<%s>" % k not in kx:
            bad.append("keyed %s missing" % k)
    # MIASMA_ATTAR_STILL_1
    items = open(os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_Attar.xml")).read()
    for d in ("RM_Attar", "RM_AttarStill"):
        if items.count("<defName>%s</defName>" % d) != 1:
            bad.append("%s ThingDef missing or duplicated" % d)
    rec = open(os.path.join(HERE, "Defs", "RecipeDefs", "RM_MakeAttar.xml")).read()
    for needle in ("<li>RM_DeltaSilt</li>", "<li>RM_RawSalt</li>", "<RM_Attar>1</RM_Attar>", "<li>RM_AttarStill</li>"):
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
            for old in ("RUT_" + n for n in ("FeverSwarm", "Karrobel", "DeltaLoam")):
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
    # MIASMA_DECAY_CELLS_1 part A
    dc = open(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_DecayCell.xml"), encoding="utf-8").read()
    for d in ("RM_DecayCell", "RM_RottingBed"):
        if dc.count("<defName>%s</defName>" % d) != 1:
            bad.append("%s ThingDef missing or duplicated" % d)
    for needle in ("RM_CompPowerPlantDecay", "<spentDef>RM_RottingBed</spentDef>", "<li>RM_DecayCells</li>",
                   "<RM_DeltaLoam>", "<RM_RawSalt>"):
        if needle not in dc:
            bad.append("RM_DecayCell lacks %s" % needle)
    rp = open(os.path.join(HERE, "Defs", "ResearchProjectDefs", "RM_DecayCells.xml"), encoding="utf-8").read()
    if "<li>RM_OldCurrentMeter</li>" not in rp:
        bad.append("RM_DecayCells is not gated on analyzing the old meter")
    mt = open(os.path.join(HERE, "Defs", "ThingDefs_Items", "RM_OldCurrentMeter.xml"), encoding="utf-8").read()
    if "CompProperties_CompAnalyzableUnlockResearch" not in mt or "<requiresMechanitor>false" not in mt:
        bad.append("old meter is not analyzable by any colonist")
    cs = open(os.path.join(HERE, "Source", "RM_DecayCells.cs"), encoding="utf-8").read()
    for needle in ("decayCellsEnabled", "decayCellPowerMultiplier", "BecomeRottingBed", "RM_OldCurrentMeter"):
        if needle not in cs:
            bad.append("RM_DecayCells.cs lacks %s" % needle)
    # output curve, mirrored from DecayCellMath.OutputFraction (lerp(min, 1, fullness), 0 when empty)
    def frac(full, mn=0.3):
        return 0.0 if full <= 0 else mn + (1 - mn) * min(1.0, full)
    if not (frac(0) == 0 and abs(frac(0.01) - 0.307) < 1e-3 and frac(1) == 1 and frac(0.5) < frac(1)):
        bad.append("decay output curve: empty must be 0 and output must fall as feed is spent")
    # MIASMA_ROTTING_BED_CORPSES_1: the bed is a corpse store with the rot-down class; bones exist; skull is vanilla
    bed = dc[dc.index("<defName>RM_RottingBed</defName>"):]
    bed = bed[:bed.index("</ThingDef>")]
    for needle in ("RimMandrake.Miasma.RM_Building_RottingBed", "<tickerType>Rare</tickerType>", "<li>Corpses</li>",
                   "<li>CorpsesMechanoid</li>", "<maxItemsInCell>1</maxItemsInCell>", "ITab_Storage",
                   "<bonesDef>RM_Bones</bonesDef>"):
        if needle not in bed:
            bad.append("RM_RottingBed lacks %s" % needle)
    if dc.count("<defName>RM_Bones</defName>") != 1:
        bad.append("RM_Bones ThingDef missing or duplicated")
    rb = open(os.path.join(HERE, "Source", "RM_RottingBed.cs"), encoding="utf-8").read()
    for needle in ("rottingBedCorpsesEnabled", "rottingBedRotDays", '"Skull"', "AddSource(inner.LabelShort)",
                   "BodyPartDefOf.Head", "corpse.Strip(", "TickRare"):
        if needle not in rb:
            bad.append("RM_RottingBed.cs lacks %s" % needle)
    if '<Compile Include="RM_RottingBed.cs" />' not in open(os.path.join(HERE, "Source", "RM_Miasma.csproj")).read():
        bad.append("RM_RottingBed.cs is not in the csproj (it would compile into nothing)")
    # bones curve, mirrored from RottingBedMath.BonesFor (round(size x 8), at least 1)
    def bones(size, per=8.0):
        return max(1, int(size * per + 0.5))
    if not (bones(1.0) == 8 and bones(0.05) == 1 and bones(2.4) == 19):
        bad.append("bones curve: a human must leave 8, a rat at least 1")
    # MIASMA_MOTHERS_PRICE_1 + MIASMA_WARDEN_MOTHER_ART_1
    mp = open(os.path.join(HERE, "Source", "RM_MothersPrice.cs"), encoding="utf-8").read()
    for needle in ("TradeAction.PlayerSells", "nameof(Pawn.PreTraded)", "nameof(Tradeable.TraderWillTrade)",
                   '"RevokeForever"', '"GrantColonyTolerance"', ".Betray(", "IncidentDefOf.TraderCaravanArrival",
                   "RM_MiasmaSettings.mothersPriceEnabled", "IsWater"):
        if needle not in mp:
            bad.append("RM_MothersPrice.cs lacks %s" % needle)
    if '<Compile Include="RM_MothersPrice.cs" />' not in open(os.path.join(HERE, "Source", "RM_Miasma.csproj")).read():
        bad.append("RM_MothersPrice.cs is not in the csproj (it would compile into nothing)")
    anchor = open(os.path.join(HERE, "..", "EnvironmentalHazards", "Source", "RM_CompTerritorialAnchor.cs"), encoding="utf-8").read()
    for m in ("public void RevokeForever()", "public bool GrantColonyTolerance()", "public bool Betrayed", "public bool ColonyTolerated"):
        if m not in anchor:
            bad.append("the reflection target %r is missing from RM_CompTerritorialAnchor" % m)
    if "if (p == null || betrayed)" not in anchor:
        bad.append("a betrayed mother must tolerate nobody (IsTolerated)")
    sd = open(os.path.join(HERE, "Defs", "HediffDefs", "RUT_StrandedDeformation.xml"), encoding="utf-8").read()
    if "RimMandrake.Miasma.RM_MothersPriceExtension" not in sd or "<priceOffset>" not in sd:
        bad.append("RUT_StrandedDeformation lacks the mother's price extension or its priceOffset")
    if "hd.priceOffset = RM_MiasmaSettings.mothersPriceEnabled" not in open(os.path.join(HERE, "Source", "RM_MiasmaMod.cs"), encoding="utf-8").read():
        bad.append("youngPriceOffset is not written to the hediff's priceOffset")
    led = open(os.path.join(HERE, "Source", "RM_WardenMotherSuccession.cs"), encoding="utf-8").read()
    kern = open(os.path.join(HERE, "Source", "RM_MiasmaKernel.cs"), encoding="utf-8").read()   # the ledger rules live in the kernel
    if "successionDone = true;" not in kern[kern.index("public void Betray("):].split("public void NoteReturned", 1)[0]:
        bad.append("Betray must void succession")
    if "ledger.Betray();" not in led:
        bad.append("the creche comp's Betray no longer calls the ledger's Betray")
    for f in ("south", "east", "north"):
        if not os.path.exists(os.path.join(HERE, "Textures", "Things", "Pawn", "Animal", "Miasma", "WardenMother", "WardenMother_%s.png" % f)):
            bad.append("warden mother art missing: %s" % f)
    wm = open(os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_WardenMother.xml"), encoding="utf-8").read()
    for tp in re.findall(r"<texPath>([^<]+)</texPath>", wm):
        if not os.path.exists(os.path.join(HERE, "Textures", *(tp + "_south.png").split("/"))):
            bad.append("RM_WardenMother texPath %s resolves to nothing" % tp)
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    import donor_plain_ports_check  # DONOR_CODE_PLAIN_PORTS_1: the duskfire port (RM_Thermadon)
    bad += donor_plain_ports_check.static_checks("Miasma")
    return bad


def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("Miasma")
    suite.toggles = ["decayCellsEnabled", "youngCallEnabled", "attarEnabled", "plantPredationEnabled", "pollinationGateEnabled", "strandedDeformationEnabled", "wardenSuccessionEnabled", "mothersPriceEnabled"]

    def _proof(t, method):
        r = t.bridge_call("jawa/static_call", type="RimMandrake.Miasma.RM_MiasmaProof", method=method, args="current")
        return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

    def _kv(text):
        return dict(m.groups() for m in re.finditer(r"(\w+)=(\S+)", text))

    def _loaded(t, pairs):
        """Live: every DefType/defName in pairs survived the loader (a def can parse and still be discarded)."""
        r = t.bridge_call("jawa/get_defs", defs=";".join(pairs), limit=len(pairs) + 1)
        if not isinstance(r, dict) or r.get("success") is False:
            _unmeasured(t, "get_defs could not be asked: %s" % str(r)[:160])
            return
        missing = r.get("notFound") or [d.get("defName") for d in (r.get("defs") or []) if not d.get("found")]
        if missing:
            raise ExpectationFailed("defs discarded or absent live: %s" % missing)

    def _unmeasured(t, why):
        """Record the component UNMEASURED (never FAIL) via the harness's upstream_failed route."""
        t.upstream_reason = "UNMEASURED: " + why
        t.upstream_failed = True

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
                if not _same((got or {}).get("value"), DEFAULTS[field]):
                    raise ExpectationFailed("%s default is not the shipped value: %r" % (field, got))
                flip = (not DEFAULTS[field]) if isinstance(DEFAULTS[field], bool) else 0.5
                try:
                    _call(t, "set", field, flip)
                    back = _call(t, "get", field)
                    if not _same((back or {}).get("value"), flip):
                        raise ExpectationFailed("%s did not take: %r" % (field, back))
                finally:
                    _call(t, "set", field, DEFAULTS[field])

    @suite.chain("switches_gate_mechanics")
    def switches_gate_mechanics(t):
        with t.component("mechanics_stop_with_switch_off", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "predation (plant beside a wild scuttler), the pollination gate "
                             "(worldgen plant pass) and stranded deformation (a stranding pool) each need "
                             "a live Miasma quicktest map")
            return

    @suite.chain("salt_crust_free_tier")
    def salt_crust_free_tier(t):
        with t.component("salt_crust_paints_without_campaign", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "no 'Could not resolve' for a salt crust and a surge recede "
                             "repainting land to RM_MiasmaSaltCrust need a tier without mandrake.rut.patches "
                             "and a live Miasma map (also a bar for MIASMA_FIRST_SCRIPT_1)")
            return

    @suite.chain("nursery_young_free_tier")
    def nursery_young_free_tier(t):
        with t.component("four_young_defs_load", beyond_toggle=True):
            if t.session is None:
                return
            _loaded(t, ["PawnKindDef/%s" % y for y in ("RM_CrimsonOpeeJuv", "RM_ThornbackColoJuv", "RM_ShaleGorgerJuv", "RM_ReefbackJuv")]
                    + ["ThingDef/%s" % y for y in ("RM_CrimsonOpeeJuv", "RM_ThornbackColoJuv", "RM_ShaleGorgerJuv", "RM_ReefbackJuv")])
        with t.component("young_strand_on_recede", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "a recede on a free-only tier stranding at least one young (spawn many) needs a live "
                             "Miasma map; the stranding pool is a map GenStep the bridge cannot regenerate")
            return

    @suite.chain("decay_cells")
    def decay_cells(t):
        """MIASMA_COVERAGE_GAPS_1: RM_MiasmaProof.ProofDecayCell drives the real comp on the current map:
        output by feed level, the switch-off arm, and the lifetime digestion (ObserveFuel, what CompTick runs)."""
        state = {}
        with t.component("output_falls_with_feed_and_stops_empty", toggle="decayCellsEnabled"):
            if t.session is None:
                return
            text = _proof(t, "ProofDecayCell")
            if text.startswith("UNMEASURED"):
                _unmeasured(t, text)
                return
            kv = _kv(text)
            state.update(kv)
            try:
                full, low, empty = float(kv["full"]), float(kv["low"]), float(kv["empty"])
            except (KeyError, ValueError):
                raise ExpectationFailed("decay cell proof unreadable: %s" % text[:200])
            if not (full > low > 0 and empty == 0):
                raise ExpectationFailed("want full > low > 0 and empty 0: %s" % text[:200])
        with t.component("switch_off_makes_no_power", toggle="decayCellsEnabled"):
            if t.session is None:
                return
            if state.get("off") != "0":
                raise ExpectationFailed("decayCellsEnabled off still powers: off=%s" % state.get("off"))
        with t.component("lifetime_feed_turns_cell_into_rotting_bed", toggle="decayCellsEnabled"):
            if t.session is None:
                return
            if state.get("becameBed") != "True":
                raise ExpectationFailed("a cell fed its lifetime did not become RM_RottingBed: %s" % state)

    @suite.chain("rotting_bed_corpses")
    def rotting_bed_corpses(t):
        """MIASMA_ROTTING_BED_CORPSES_1. Runs on the CURRENT map. Not proven here: haulers choosing the bed (a
        storage priority read, not a proof) and the timed rot-down over rottingBedRotDays -- first poke: build the
        bed, drop a corpse beside it, step 2 days, read its inspect string."""
        with t.component("corpse_leaves_bones_and_named_skull", toggle="rottingBedCorpsesEnabled"):
            if t.session is None:
                return
            r = t.bridge_call("jawa/static_call", type="RimMandrake.Miasma.RM_RottingBedProof", method="ProofCorpse",
                              args="current")
            text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
            for want in ("accepts=True", "corpseGone=True", "skull=True", "skullNamesSource=True"):
                if want not in text:
                    raise ExpectationFailed("rotting bed proof missing %s: %s" % (want, text[:200]))
            # bones follow BODY SIZE (round(size x 8)); the proof now kills an adult baseliner (size 1.00 -> 8). LIVE
            # run17 read 6: the generated colonist was a teen, the curve was right and the proof's victim was not.
            import re as _re
            got = _re.search(r"bones=(\d+)", text)
            exp = _re.search(r"expectBones=(\d+)", text)
            size = _re.search(r"bodySize=([\d.]+)", text)
            if not (got and exp and got.group(1) == exp.group(1)):
                raise ExpectationFailed("bones do not follow the body-size curve: %s" % text[:240])
            if size and size.group(1) == "1.00" and got.group(1) != "8":
                raise ExpectationFailed("an adult human (size 1.00) must leave 8 bones: %s" % text[:240])

    @suite.chain("mothers_price")
    def mothers_price(t):
        """MIASMA_MOTHERS_PRICE_1. Runs on the CURRENT map (RM_MothersPriceProof spawns a warden mother on any water
        cell if none is there, and stages its own held young). Return first, then sale: a held young in her water is
        taken back (goes wild, loses the deformation) and the colony is tolerated; a sold young revokes it for good and
        reprices at the fortune. NOT proven here: the buyer caravan (step 2 days on a home map holding a young), the
        trade dialog itself, and succession void on a real crèche (no RUT_CrecheMarker on a quicktest) -- first poke
        on a Miasma map: ProofSell, then read the crèche marker's inspect string."""
        def proof(t, method):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.Miasma.RM_MothersPriceProof", method=method, args="current")
            return str((r or {}).get("result", "")) if isinstance(r, dict) else ""

        with t.component("returning_a_young_wins_her_tolerance", toggle="mothersPriceEnabled"):
            if t.session is None:
                return
            text = proof(t, "ProofReturn")
            if text.startswith("ERROR no warden mother and no water cell"):
                # A site fact (this map has no water for the proof's mother), not a mod failure: UNMEASURED.
                _unmeasured(t, text)
                return
            for want in ("taken=1", "youngWild=True", "stillStranded=False", "tolerated=True", "betrayed=False"):
                if want not in text:
                    raise ExpectationFailed("return proof missing %s: %s" % (want, text[:240]))

        with t.component("selling_a_young_betrays_her_forever", toggle="mothersPriceEnabled"):
            if t.session is None:
                return
            text = proof(t, "ProofSell")
            if text.startswith("ERROR no warden mother and no water cell"):
                # A site fact (this map has no water for the proof's mother), not a mod failure: UNMEASURED.
                _unmeasured(t, text)
                return
            after = text[text.find("after["):]
            for want in ("betrayed=True", "tolerated=False"):
                if want not in after:
                    raise ExpectationFailed("sale proof missing %s after the sale: %s" % (want, text[:300]))
            m = re.search(r"price=(\d+)", after)
            if not m or int(m.group(1)) < 1000:
                raise ExpectationFailed("a held stranded young is not priced at a fortune: %s" % after[:200])
            if "ledger=True" in after and "successionVoid=True" not in after:
                raise ExpectationFailed("the crèche ledger was found but succession is not void: %s" % after[:200])

    @suite.chain("young_call")
    def young_call(t):
        with t.component("cry_and_mother_heads_for_water", toggle="youngCallEnabled"):
            if t.session is None:
                return
            _unmeasured(t, "a placed stranded young emitting the cry, and its warden mother's "
                             "CurJob target moving toward it and stopping at the water edge, need a live "
                             "Miasma quicktest map with the bridge")
            return

    @suite.chain("ambush_frog_free_tier")
    def ambush_frog_free_tier(t):
        with t.component("bozzuga_defs_load", beyond_toggle=True):
            if t.session is None:
                return
            _loaded(t, ["ThingDef/RM_Bozzuga", "PawnKindDef/RM_Bozzuga"])
        with t.component("bozzuga_hunts", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "a bozzuga hunting a karrolun needs both spawned on a Miasma map and a predator-hunt "
                             "job read over ticks (jawa/pawn_jobs); not wired yet")
            return

    @suite.chain("swarm_composter_free_tier")
    def swarm_composter_free_tier(t):
        with t.component("swarm_karrobel_loam_defs_load", beyond_toggle=True):
            if t.session is None:
                return
            _loaded(t, ["ThingDef/RM_FeverSwarm", "ThingDef/RM_Karrobel", "ThingDef/RM_DeltaLoam"])
        with t.component("mangal_gated_on_swarm", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "a gated mangal (RM_Thessamor) not spreading where no swarm lives needs a Miasma map's "
                             "wild plant pass (worldgen/map gen), which the bridge cannot regenerate")
            return

    @suite.chain("flotsam_yard")
    def flotsam_yard(t):
        with t.component("flotsam_after_surge_in_root_lines", beyond_toggle=True):
            if t.session is None:
                return
            _unmeasured(t, "flotsam stacks standing on root-line cells after a debug surge and "
                             "recede (and none on dry inland ground) need a live Miasma quicktest map")
            return

    @suite.chain("attar_glaze_and_balm")
    def attar_glaze_and_balm(t):
        """MIASMA_COVERAGE_GAPS_1: glaze and balm through RM_MiasmaProof on the current map."""
        with t.component("glaze_adds_beauty_and_only_once", toggle="attarEnabled"):
            if t.session is None:
                return
            text = _proof(t, "ProofGlaze")
            if text.startswith("UNMEASURED"):
                _unmeasured(t, text)
                return
            kv = _kv(text)
            try:
                before, after, off = float(kv["before"]), float(kv["after"]), float(kv["off"])
            except (KeyError, ValueError):
                raise ExpectationFailed("glaze proof unreadable: %s" % text[:200])
            if kv.get("glazable") != "True" or abs(after - before - 3.0) > 0.05 or kv.get("glazableAgain") != "False":
                raise ExpectationFailed("glaze did not add +3 Beauty once: %s" % text[:200])
            if abs(off - before) > 0.05:
                raise ExpectationFailed("attarEnabled off still applies the glaze: %s" % text[:200])
        with t.component("balm_fades_scar_not_fresh_wound", toggle="attarEnabled"):
            if t.session is None:
                return
            text = _proof(t, "ProofBalm")
            if text.startswith("UNMEASURED"):
                _unmeasured(t, text)
                return
            kv = _kv(text)
            if kv.get("freshStillThere") != "True" or kv.get("freshBefore") != kv.get("freshAfter"):
                raise ExpectationFailed("balm touched a non-permanent wound: %s" % text[:200])
            if kv.get("scarAfter") != "gone":
                try:
                    if float(kv["scarAfter"]) >= float(kv["scarBefore"]):
                        raise ExpectationFailed("balm did not fade the scar: %s" % text[:200])
                except (KeyError, ValueError):
                    raise ExpectationFailed("balm proof unreadable: %s" % text[:200])
        with t.component("attar_recipe_on_still", toggle="attarEnabled"):
            if t.session is None:
                return
            r = t.bridge_call("jawa/get_defs", defs="RecipeDef/RM_MakeAttar", fields="recipeUsers", limit=2)
            rows = (r or {}).get("defs") or [] if isinstance(r, dict) else []
            if not rows or not rows[0].get("found", True):
                raise ExpectationFailed("RM_MakeAttar not loaded: %s" % str(r)[:160])
            users = str((rows[0].get("fields") or {}).get("recipeUsers"))
            if "RM_AttarStill" not in users:
                raise ExpectationFailed("RM_MakeAttar is not made at RM_AttarStill: %s" % users[:160])

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
