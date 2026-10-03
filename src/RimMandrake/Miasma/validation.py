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
            "strandedDeformationEnabled": True, "strandedDeformationChance": 0.25}
NEW = ["plantPredationEnabled", "pollinationGateEnabled", "strandedDeformationEnabled", "strandedDeformationChance"]


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
    return bad


def _build_suite():
    from modcheck import Suite, ExpectationFailed
    suite = Suite("Miasma")
    suite.toggles = ["plantPredationEnabled", "pollinationGateEnabled", "strandedDeformationEnabled", "wardenSuccessionEnabled"]

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
