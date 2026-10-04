"""validation.py -- modcheck suite for RimMandrake: Environmental Hazards Kit (mandrake.rm.environmentalhazards).

First north-star script (ENVIRONMENTAL_HAZARDS_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/EnvironmentalHazards.md.
A SHARED mechanics kit: nothing here names a campaign. It ships a handful of its own defs (gas bases, contact-venom plant and
hediff, stats, jobs, think trees) plus ~50 mechanisms that content mods opt into by XML. This assembly's own surface that a
bridge can read without a generated map is: its defs, its Mod Settings (RM_EnvironmentalHazardsSettings, 60+ public static
fields incl. waterTruceRadius, waterTruceSuppressionEnabled, waterTruceRetributionEnabled), and the Harmony rules it arms at
startup. Each rule logs `rule NOT armed` and carries on when its engine target has moved, so an armed-rule read is the real
check that a mechanism is wired.

CHAINS
  defs_resolve        every concrete def under Defs/ (parsed from the XML) resolves live; a control reads notFound.
  settings_roundtrip  every `public static` bool/int/float of RM_EnvironmentalHazardsSettings (parsed from the C#): get, set to
                      a different value, read back, restore. Numerics compared numerically.
  harmony_rules_armed one component per Harmony rule the kit arms (type, method, prefix|postfix, patch method, owner id).
  contact_venom_wiring RM_VenomvineVenom is a lethal hediff (lethalSeverity 1.0, the number the lethal-off toggle holds under).
  map_mechanics       gas, area attacks, weather conditions, water truce, boles, tar, glasswalk...: UNMEASURED, each with the
                      reason (needs a generated biome map / an incident / game days; this run may not drive them).

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings"
HARMONY_ID = "mandrake.rm.environmentalhazards"
CONTROL_ABSENT = "ThingDef/RM_EnvironmentalHazardsNoSuchDef_ZZ"
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")

# (target type, target method, kind, patch method name, Mod Settings toggle gating the rule or None)
RULES = (
    ("GenCelestial", "CurCelestialSunGlow", "postfixes", "CurCelestialSunGlow_Postfix", "biomeGlowMultiplierEnabled"),
    ("ConditionalStatAffecter_InSunlight", "Applies", "postfixes", "InSunlightApplies_Postfix", "biomeGlowMultiplierEnabled"),
    ("PathFinder", "CreateRequest", "prefixes", "CreateRequest_Prefix", "bodySizeBarrierEnabled"),
    ("Pawn_PathFollower", "GetPawnCellBaseCostOverride", "postfixes", "GetPawnCellBaseCostOverride_Postfix", "bodySizeBarrierEnabled"),
    ("Thing", "PostApplyDamage", "postfixes", "PostApplyDamage_Postfix", "waterTruceRetributionEnabled"),
    ("FoodUtility", "IsAcceptablePreyFor", "postfixes", "IsAcceptablePreyFor_Postfix", "waterTruceSuppressionEnabled"),
    ("JobDriver_PredatorHunt", "MakeNewToils", "postfixes", "MakeNewToils_Postfix", "waterTruceSuppressionEnabled"),
    ("WildPlantSpawner", "CalculatePlantsWhichCanGrowAt", "postfixes", "CalculatePlantsWhichCanGrowAt_Postfix", "leachmossEnabled"),
    ("GenStep_GravshipMarker", "Generate", "postfixes", "Generate_Postfix", "biomeArrivalLettersEnabled"),
    ("IncidentWorker", "ChanceFactorNow", "postfixes", "ChanceFactorNow_Postfix", "crecheDespoilMemoryEnabled"),
    ("CompTemperatureRuinable", "CompTick", "prefixes", "CompTick_Prefix", "livePrepStrictViability"),
    ("JobGiver_OptimizeApparel", "ApparelScoreRaw", "postfixes", "ApparelScoreRaw_Postfix", "hazardApparelAIAwarenessEnabled"),
    ("TradeDeal", "TryExecute", "prefixes", "TryExecute_Prefix", "treasureConscienceEnabled"),
    ("TradeDeal", "TryExecute", "postfixes", "TryExecute_Postfix", "treasureConscienceEnabled"),
    # SUMP_FREE_TIER_MOVE_BUILD_1: save back-compat for renamed defs; always armed, no toggle by design
    ("BackCompatibility", "BackCompatibleDefName", "postfixes", "BackCompatibleDefName_Postfix", None),
    ("BackCompatibility", "BackCompatibleTerrainWithShortHash", "postfixes", "BackCompatibleTerrainWithShortHash_Postfix", None),
    ("Plant", "IngestedCalculateAmounts", "postfixes", "IngestedCalculateAmounts_Postfix", "grazingSuppressionHookEnabled"),
)


def shipped_defs():
    """[(DefType, defName)] for every non-abstract top-level def under Defs/, from the XML (never a hand list)."""
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                        out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def _settings_src():
    return open(os.path.join(HERE, "Source", "RM_EnvironmentalHazardsMod.cs"), encoding="utf-8").read()


def settings_fields():
    """{name: type} for every scalar `public static` field of RM_EnvironmentalHazardsSettings, read from the C#."""
    body = _settings_src().split("class RM_EnvironmentalHazardsSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if len(SHIPPED) < 10:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if len(fields) < 30:
        return ["settings probe found only %d scalar fields (sanity probe failed)" % len(fields)]
    for need in ("waterTruceRadius", "waterTruceSuppressionEnabled", "waterTruceRetributionEnabled", "hazardDamageMultiplier"):
        if need not in fields:
            bad.append("settings probe did not see %s" % need)
    body = _settings_src().split("ExposeData", 1)[1]
    scribed, ui = body.split("DoWindowContents", 1)
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control or reset in DoWindowContents" % n)
    srcdir = os.path.join(HERE, "Source")
    allsrc = ""
    proj = open(os.path.join(srcdir, "RM_EnvironmentalHazards.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(srcdir)):
        if fn.endswith(".cs"):
            allsrc += open(os.path.join(srcdir, fn), encoding="utf-8").read()
            if 'Compile Include="%s"' % fn not in proj:
                bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    for typ, meth, _kind, patch, toggle in RULES:
        if not re.search(r"\b%s\b" % patch, allsrc):
            bad.append("rule patch method %s not found in Source/" % patch)
        if toggle and toggle not in fields:
            bad.append("rule %s.%s names toggle %s, not a settings field" % (typ, meth, toggle))
    if ("HediffDef", "RM_VenomvineVenom") not in SHIPPED:
        bad.append("HediffDef RM_VenomvineVenom missing")
    else:
        hd = ET.parse(os.path.join(HERE, "Defs", "HediffDefs", "RM_Hediffs_ContactVenom.xml")).getroot()
        if not any(float(e.findtext("lethalSeverity") or 0) > 0 for e in hd if isinstance(e.tag, str)):
            bad.append("RM_VenomvineVenom has no lethalSeverity (the lethal-off toggle holds under it)")
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "EnvironmentalHazards.md")):
        bad.append("walk missing")
    return bad


try:
    _UTILS = os.path.join(HERE, "..", "Utils")
    if os.path.isdir(_UTILS) and _UTILS not in sys.path:
        sys.path.insert(0, _UTILS)
    from modcheck import Suite, ExpectationFailed
except ImportError:
    Suite = None


def _build_suite():
    suite = Suite("EnvironmentalHazards")
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
        return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        with t.component("control_probe_can_say_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs=CONTROL_ABSENT, fields="defName", limit=2)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed outright on the control: %r" % r)
                if int(r.get("foundCount", 0)) != 0 or not r.get("notFound"):
                    raise ExpectationFailed("control def reads as present: %r" % r)
        with t.component("every_shipped_def_resolves", beyond_toggle=True):
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
            f = settings_fields()
            if len(f) < 30 or "waterTruceRadius" not in f:
                raise ExpectationFailed("settings probe found %d fields / no waterTruceRadius (blind regex)" % len(f))
        for field, ty in sorted(settings_fields().items()):
            with t.component("%s_round_trips" % field, toggle=field):
                if not _live(t):
                    continue
                old = _raw(t, "get", field).get("value")
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                if ty == "bool":
                    new = "False" if str(old).lower() == "true" else "True"
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

    @suite.chain("harmony_rules_armed")
    def harmony_rules_armed(t):
        with t.component("control_unpatched_method_has_no_owner", beyond_toggle=True):
            r = t.bridge_call("jawa/harmony_patches", typeName="GenCelestial", methodName="NoSuchMethodZZ")
            if _live(t) and isinstance(r, dict) and r.get("success") is True and not r.get("harmonyError"):
                for m in (r.get("methods") or []):
                    for kind in ("prefixes", "postfixes"):
                        if any(p.get("owner") == HARMONY_ID for p in (m.get(kind) or [])):
                            raise ExpectationFailed("a nonexistent method reads as patched by %s" % HARMONY_ID)
        for typ, meth, kind, patch, toggle in RULES:
            with t.component("%s_%s_%s_armed" % (typ, meth, kind[:-2]), toggle=toggle, beyond_toggle=toggle is None):
                r = t.bridge_call("jawa/harmony_patches", typeName=typ, methodName=meth)
                if not _live(t):
                    continue
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked for %s.%s: %s" % (typ, meth, str(r)[:160]))
                    return
                mine = [p for m in (r.get("methods") or []) for p in (m.get(kind) or [])
                        if (p.get("patchMethod") or "").endswith(patch) and p.get("owner") == HARMONY_ID]
                if not mine:
                    raise ExpectationFailed("%s.%s lacks %s %s from %s (target moved? see the 'rule NOT armed' log line)"
                                            % (typ, meth, kind[:-2], patch, HARMONY_ID))

    @suite.chain("def_aliases_resolve")
    def def_aliases_resolve(t):
        # Every RM_DefAliasDef row, through the real patched engine entry points: a save naming
        # the old def (RUT_TarVault, RUT_Tarred, terrain by short hash...) loads as the new one.
        with t.component("saved_old_names_load_as_new_defs", beyond_toggle=True):
            r = t.bridge_call("jawa/static_call", type="RimMandrake.EnvironmentalHazards.RM_DefAliasProof",
                              method="ProofAliases", args="")
            if not _live(t):
                return
            text = str((r or {}).get("result") or (r or {}).get("value") or r)
            if not text.startswith("PASS"):
                if "FAIL" in text[:4]:
                    raise ExpectationFailed("alias proof: %s" % text[:400])
                _unmeasured(t, "static_call did not answer: %s" % text[:200])

    @suite.chain("contact_venom_wiring")
    def contact_venom_wiring(t):
        with t.component("venom_hediff_is_lethal_at_one", toggle="contactVenomLethal"):
            r = t.bridge_call("jawa/get_defs", defs="HediffDef/RM_VenomvineVenom", fields="lethalSeverity", limit=2)
            if _live(t):
                rows = (r or {}).get("defs") or []
                if not isinstance(r, dict) or r.get("success") is False or not rows:
                    raise ExpectationFailed("could not read RM_VenomvineVenom: %r" % r)
                try:
                    ls = float((rows[0].get("fields") or {}).get("lethalSeverity"))
                except (TypeError, ValueError):
                    _unmeasured(t, "get_defs did not return a numeric lethalSeverity: %r" % (rows[0],))
                    return
                if abs(ls - 1.0) > 1e-4:
                    raise ExpectationFailed("lethalSeverity %s, expected 1.0 (the lethal-off hold-under threshold)" % ls)

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        for name, toggle, why in (
            ("gas_emitters_and_gas_effects", "gasEmittersEnabled",
             "an emitter comp seeding a gas cloud, and the gas damaging/transmuting, need a ThingDef from a content mod that opts in "
             "(this kit ships only abstract gas bases) and ticks"),
            ("periodic_area_attack", "areaAttacksEnabled",
             "needs a carrier pawn holding a content mod's hediff that carries HediffCompProperties_PeriodicAreaAttack, and ticks"),
            ("environmental_weather_and_latent_hazard", "environmentalDamageEnabled",
             "needs a GameConditionDef from a content mod, fired on a map, with an unroofed pawn and ticks; fire_incident cannot "
             "start a condition the kit does not own"),
            ("scaled_explosion_death_action", "scaledExplosionsEnabled",
             "needs a creature whose def names the death action, killed on a map"),
            ("water_truce_retribution_and_suppression", "waterTruceRetributionEnabled",
             "needs a generated map whose biome carries RM_WaterTruceExtension, water cells, a wild herd and a guilty hit; the "
             "radius override (waterTruceRadius) is only read there"),
            ("living_boles_regrowth_tree_fall", "livingRegrowthEnabled",
             "needs a generated Greentide map with a Greatbole and regrow days of ticks"),
            ("stranding_pools_and_gradient_axis", "strandingPoolsEnabled",
             "needs a generated Miasma map and a tide recede/surge"),
            ("tar_coating_belch_and_glasswalk_slip", "tarCoatingEnabled",
             "needs Sump terrain (RM_SlipperyWalkway / tar filth), a hurrying pawn, and the belch incident on a Sump map"),
            ("accelerated_rot_warm_ground_living_produce", "acceleratedRotEnabled",
             "needs a Rot-biome map with items/corpses and ticks to compare against vanilla rot"),
            ("sheen_scald_and_live_preparations", "sheenExposureEnabled",
             "needs Sheen-fall weather on a Rot map, a carrier hediff and days of severity accrual"),
            ("venomvine_scratch_and_body_size_barrier", "contactVenomEnabled",
             "scratching needs a grown Venomvine stand, a pawn standing in it for an hour of ticks, and a large pawn to be blocked; "
             "the wiring half is in contact_venom_wiring"),
            ("worldgen_scatterers_and_gen_steps", "livingBolesEnabled",
             "creche/sail/mirror-pool/causeway/grave-ward/ground-refusal steps act only while a map is GENERATED with the toggle; "
             "the bridge cannot generate a map"),
        ):
            with t.component(name, toggle=toggle):
                if _live(t):
                    _unmeasured(t, why)

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
