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
  map_mechanics_wiring each of the 12 mechanics: toggle gates its Source file (offline), toggle live-readable, kit-shipped defs resolve.
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


LIVING_MAP_CONSTS = ("ScanIntervalTicks", "MinRewriteCells", "SoffethDelayTicks", "SoffethIntervalTicks", "SoffethRingSize",
                     "SoffethRingInner", "SoffethRingOuter", "MouseRerouteDelayTicks", "CrustSetTicks", "MarginDelayTicks",
                     "MarginSproutChancePerScan", "MaxMarginSproutsPerScan")


def _living_map_findings(comp_src=None, dread_src=None, mod_src=None):
    """SUMP_TAR_LIVING_SYSTEMS_1 part 1 first script (offline): the responders are wired, gated, PROVISIONAL-marked and
    their pacing is internally consistent. Red on any of those, so a toggle that gates nothing, a mouse-line that never
    re-routes, or a margin that can never reach the crust before it sets is caught without a game."""
    src = os.path.join(HERE, "Source")
    rd = lambda f: open(os.path.join(src, f), encoding="utf-8").read()
    comp_src = comp_src if comp_src is not None else rd("RM_MapComponent_SumpLivingMap.cs")
    dread_src = dread_src if dread_src is not None else rd("RM_MapComponent_DreadField.cs")
    mod_src = mod_src if mod_src is not None else _settings_src()
    bad, vals = [], {}
    for name in LIVING_MAP_CONSTS:
        m = re.search(r"public const (?:int|float) %s = ([0-9.]+)f?;([^\n]*)" % name, comp_src)
        if not m:
            bad.append("living map: constant %s not found" % name)
            continue
        vals[name] = float(m.group(1))
        if "PROVISIONAL" not in m.group(2):
            bad.append("living map: %s is not marked PROVISIONAL (owner ruling 2026-10-03)" % name)
    if len(vals) == len(LIVING_MAP_CONSTS):
        if not 1 <= vals["SoffethRingSize"] <= 12:
            bad.append("living map: SoffethRingSize %g outside 1..12" % vals["SoffethRingSize"])
        if not 0 < vals["SoffethRingInner"] < vals["SoffethRingOuter"]:
            bad.append("living map: soffeth ring inner/outer radius not 0 < inner < outer")
        if not 0 < vals["MouseRerouteDelayTicks"] < vals["CrustSetTicks"]:
            bad.append("living map: fresh crust sets before mice ever re-route (MouseRerouteDelayTicks >= CrustSetTicks)")
        if not vals["MarginDelayTicks"] < vals["CrustSetTicks"]:
            bad.append("living map: mirrelin can never reach new glass before the crust drops out (MarginDelayTicks >= CrustSetTicks)")
        if not 0 < vals["MarginSproutChancePerScan"] <= 1:
            bad.append("living map: MarginSproutChancePerScan not in (0,1]")
        if vals["ScanIntervalTicks"] <= 0 or vals["MinRewriteCells"] < 1:
            bad.append("living map: scan interval / rewrite threshold not positive")
    tick = comp_src.split("MapComponentTick", 1)[1].split("public void Step", 1)[0] if "MapComponentTick" in comp_src else ""
    if "sumpLivingMapEnabled" not in tick or "BiomeCarriesSumpFlora" not in tick:
        bad.append("living map: MapComponentTick is not gated on sumpLivingMapEnabled AND the Sump-flora biome gate")
    isd = dread_src.split("public bool IsDreaded", 1)[1].split("private void Rebuild", 1)[0] if "public bool IsDreaded" in dread_src else ""
    if "IsFreshCrust" not in isd:
        bad.append("living map: DreadField.IsDreaded never consults IsFreshCrust -- mouse-lines cannot re-route")
    ui = mod_src.split("DoWindowContents", 1)[-1]
    m = re.search(r'"Sump living map pace: "[^;]*;\s*list\.Label\(([^;]*)\);', ui)
    if not m or "PROVISIONAL" not in m.group(1):
        bad.append("living map: the pace setting's explanation does not say PROVISIONAL")
    if "public static string ProofRewrite(string mode)" not in comp_src:
        bad.append("living map: live proof hook RM_SumpLivingMapProof.ProofRewrite missing")
    return bad


# map_mechanics wiring: (component, Mod Settings toggle, Source file that must consult it in a branch, defs that must resolve live)
MECHANICS = (
    ("gas_emitters", "gasEmittersEnabled", "CompActiveGasEmitter.cs", ()),
    ("periodic_area_attack", "areaAttacksEnabled", "HediffComp_PeriodicAreaAttack.cs", ()),
    ("environmental_weather", "environmentalDamageEnabled", "GameCondition_EnvironmentalWeather.cs", ()),
    ("scaled_explosion_death_action", "scaledExplosionsEnabled", "DeathActionWorker_ScaledExplosion.cs", ()),
    ("water_truce_retribution", "waterTruceRetributionEnabled", "RM_MapComponent_WaterTruce.cs",
     ("MentalStateDef/RM_WaterTruceRetribution",)),
    ("living_boles_regrowth", "livingRegrowthEnabled", "RM_MapComponent_LivingRegrowth.cs", ()),
    ("stranding_pools", "strandingPoolsEnabled", "RM_MapComponent_StrandingPools.cs",
     ("ThinkTreeDef/RM_ThinkTree_StrandingBehaviors",)),
    ("tar_coating", "tarCoatingEnabled", "RM_Comp_TarCoatingSource.cs", ()),
    ("accelerated_rot", "acceleratedRotEnabled", "RM_MapComponent_AcceleratedRot.cs", ()),
    ("sheen_scald", "sheenExposureEnabled", "RUT_HediffComp_SheenExposure.cs",
     ("StatDef/RM_ScaldProtection", "StatDef/RM_ArmorRating_Scald", "DamageArmorCategoryDef/RM_ScaldArmor")),
    ("venomvine_scratch", "contactVenomEnabled", "MapComponent_ContactVenom.cs",
     ("DamageDef/RM_VenomvineScratch", "ThingDef/RM_Venomvine", "ThingDef/RM_VenomvineThicket", "HediffDef/RM_VenomvineVenom")),
    ("living_boles_genstep", "livingBolesEnabled", "RM_GenStep_LivingBoles.cs", ()),
)


def gate_findings(comp_name=None):
    """Offline: each mechanic's Source file consults its toggle inside a branch (if/return/&&/||), so a toggle that gates
    nothing is red. Returns [message]."""
    bad = []
    for name, toggle, fn, _defs in MECHANICS:
        if comp_name and name != comp_name:
            continue
        try:
            src = open(os.path.join(HERE, "Source", fn), encoding="utf-8").read()
        except IOError:
            bad.append("%s: Source/%s not found" % (name, fn))
            continue
        if not re.search(r"(?:if|return|while)[^;{\n]*\b%s\b|(?:&&|\|\|)[^;\n]*\b%s\b|\b%s\b[^;\n]*(?:&&|\|\||\?)"
                         % (toggle, toggle, toggle), re.sub(r"//[^\n]*", "", src)):
            bad.append("%s: Source/%s never branches on %s (the toggle gates nothing there)" % (name, fn, toggle))
    return bad


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
    bad.extend(_living_map_findings())
    bad.extend(gate_findings())
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
                              method="ProofAliases", args="all")
            if not _live(t):
                return
            text = str((r or {}).get("result") or (r or {}).get("value") or r)
            if not text.startswith("PASS"):
                if "FAIL" in text[:4]:
                    raise ExpectationFailed("alias proof: %s" % text[:400])
                _unmeasured(t, "static_call did not answer: %s" % text[:200])

    @suite.chain("sump_living_map")
    def sump_living_map(t):
        # SUMP_TAR_LIVING_SYSTEMS_1: the real component on the current map, synthetic clock, terrain/plants restored.
        for mode in ("on", "off"):
            with t.component("living_map_responders_" + mode, toggle="sumpLivingMapEnabled"):
                r = t.bridge_call("jawa/static_call", type="RimMandrake.EnvironmentalHazards.RM_SumpLivingMapProof",
                                  method="ProofRewrite", args=mode)
                if not _live(t):
                    return
                text = str((r or {}).get("result") or (r or {}).get("value") or r)
                if text.startswith("FAIL"):
                    raise ExpectationFailed("living map proof (%s): %s" % (mode, text[:400]))
                if not text.startswith("PASS"):
                    _unmeasured(t, "proof did not answer PASS/FAIL: %s" % text[:200])

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

    @suite.chain("map_mechanics_wiring")
    def map_mechanics_wiring(t):
        # What a bridge CAN read for each of the 12 mechanics with no generated map: its toggle is a live, readable setting, its
        # Source file really branches on it (offline), and the kit-shipped defs the mechanism drives resolve (control proves
        # get_defs can say absent). The effect itself stays UNMEASURED in map_mechanics, each naming the instrument it lacks.
        for name, toggle, _fn, defs in MECHANICS:
            with t.component(name + "_toggle_gates_and_wiring_resolves", toggle=toggle):
                bad = gate_findings(name)
                if bad:
                    raise ExpectationFailed(bad[0])
                if not _live(t):
                    continue
                r = _raw(t, "get", toggle)
                if r.get("success") is False or str(r.get("value")).lower() not in ("true", "false"):
                    raise ExpectationFailed("%s: toggle not readable as a bool: %r" % (toggle, r))
                if defs:
                    d = t.bridge_call("jawa/get_defs", defs=";".join(defs), fields="defName", limit=len(defs) + 2)
                    if not isinstance(d, dict) or d.get("success") is False:
                        _unmeasured(t, "get_defs could not be asked for %s: %s" % (defs, str(d)[:160]))
                        return
                    if int(d.get("foundCount", 0)) != len(defs) or d.get("notFound"):
                        raise ExpectationFailed("%s: %d of %d wiring defs resolved; notFound=%r"
                                                % (name, int(d.get("foundCount", 0)), len(defs), d.get("notFound")))

    @suite.chain("map_mechanics")
    def map_mechanics(t):
        for name, toggle, why in (
            ("gas_emitters_and_gas_effects", "gasEmittersEnabled",
             "missing instrument: a spawnable emitter ThingDef (this kit ships only abstract gas bases; content mods own the concrete ones) "
             "plus a gas-cell reader (no jawa tool lists Gas things per cell by gas type or concentration)"),
            ("periodic_area_attack", "areaAttacksEnabled",
             "missing instrument: a kit-owned hediff carrying HediffCompProperties_PeriodicAreaAttack (none ships) and a hediff-adder tool; "
             "damage_log could then read the pulse"),
            ("environmental_weather_and_latent_hazard", "environmentalDamageEnabled",
             "missing instrument: a kit-owned GameConditionDef using GameCondition_EnvironmentalWeather (none ships); jawa/game_condition "
             "could start a content mod's and damage_log read it, but that is the content mod's script"),
            ("scaled_explosion_death_action", "scaledExplosionsEnabled",
             "missing instrument: a kit-owned creature naming DeathActionWorker_ScaledExplosion (none ships); a static_call proof hook "
             "(like RM_SumpLivingMapProof) is the way, and does not exist yet"),
            ("water_truce_retribution_and_suppression", "waterTruceRetributionEnabled",
             "missing instrument: a map whose biome carries RM_WaterTruceExtension (the bridge cannot generate one) and a static_call proof "
             "hook that reports suppression/retribution; harmony_rules_armed covers the wiring half"),
            ("living_boles_regrowth_tree_fall", "livingRegrowthEnabled",
             "missing instrument: a static_call proof hook on RM_MapComponent_LivingRegrowth with a synthetic clock (as RM_SumpLivingMapProof does) "
             "and a Greentide map"),
            ("stranding_pools_and_gradient_axis", "strandingPoolsEnabled",
             "missing instrument: a static_call proof hook on RM_MapComponent_StrandingPools (recede/surge on a synthetic clock) and a Miasma map"),
            ("tar_coating_belch_and_glasswalk_slip", "tarCoatingEnabled",
             "missing instrument: a static_call proof hook for tar-coat/belch and a pawn-speed reader on slippery terrain "
             "(get_terrain_batch reads the floor, nothing reads the slip)"),
            ("accelerated_rot_warm_ground_living_produce", "acceleratedRotEnabled",
             "missing instrument: a static_call proof hook on RM_MapComponent_AcceleratedRot returning the rot multiplier for a cell; "
             "jawa/comp_read could read CompRottable progress but needs a Rot map and days of ticks"),
            ("sheen_scald_and_live_preparations", "sheenExposureEnabled",
             "missing instrument: a static_call proof hook on RUT_HediffComp_SheenExposure severity accrual (needs a content mod's carrier hediff and Sheen weather)"),
            ("venomvine_scratch_and_body_size_barrier", "contactVenomEnabled",
             "missing instrument: a static_call proof hook on MapComponent_ContactVenom/RM_CompBodySizeBarrier (scratch roll, barrier cost); "
             "damage_log could read the scratch but a grown stand and an hour of ticks are needed; wiring is in contact_venom_wiring"),
            ("worldgen_scatterers_and_gen_steps", "livingBolesEnabled",
             "missing instrument: map generation (no bridge tool runs a GenStep; start_debug_game_ready generates only the stock steps) "
             "and a static_call hook for RM_GenStep_*"),
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
