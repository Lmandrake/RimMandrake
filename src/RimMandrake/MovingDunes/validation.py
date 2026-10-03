"""validation.py -- modcheck suite for RimMandrake: Moving Dunes (mandrake.rm.movingdunes).

First north-star script (MOVING_DUNES_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/MovingDunes.md.
Sand that moves: a per-map MapComponent_DuneField (wind, erosion/hop/bank transport, influx, burial caches, plant choke)
riding Odyssey's SandGrid through four Harmony rules, opted into by biomes carrying a DuneFieldExtension (vanilla Desert and
ExtremeDesert are bound here by Patches/BiomeBindings.xml). Fold-aware: every read is by def name / Harmony id.

CHAINS
  defs_resolve       every def under Defs/ (parsed from the XML; includes the custom def classes) resolves live; a control
                     name reads notFound.
  settings_roundtrip every `public static` bool/float of MovingDunesSettings: default / write / restore (numerics numerically).
  harmony_rules      the four rules (CanHaveSand, AddDepth, SectionLayer_Sand.Regenerate, ClearSnowAndSand.MakeNewToils) each
                     carry a patch owned by mandrake.rm.movingdunes; a control method carries none. A missing Odyssey type
                     is UNMEASURED.
  biome_bindings     Desert and ExtremeDesert carry the DuneFieldExtension (a patch that matches nothing logs nothing).
  dune_field_report  needs the CURRENT map to be a dune-field biome: reads the mod's own debug-action report line (the three
                     armed flags, material, wind), shifts the wind and reads it change, runs 100 batches and reads the sand
                     total. Any other biome reads "not a dune field" and the chain is UNMEASURED with that reason.
  slow_*             one chain per slow mechanic (transport/banking, influx, burial, plant choke, wind lock, clear yield):
                     UNMEASURED, each with its own reason.

STATIC: `python3 validation.py` -> `STATIC: PASS (0 findings)`; needs no game.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS = "RimMandrake.MovingDunes.MovingDunesSettings"
HARMONY_ID = "mandrake.rm.movingdunes"
CONTROL_ABSENT = "ThingDef/RM_MovingDunesNoSuchDef_ZZ"
TAG = "[RimMandrake.MovingDunes]"
ACT_REPORT = "Actions\\Dune field: report"
ACT_SHIFT = "Actions\\Dune field: shift wind"
ACT_BATCHES = "Actions\\Dune field: run 100 batches"
# (typeName, methodName, rule) -- the four Apply() rules in MovingDunesMod.cs
RULES = (
    ("SandGrid", "CanHaveSand", "sand-holds-on-sand"),
    ("SandGrid", "AddDepth", "ambient-decay-suppression"),
    ("SectionLayer_Sand", "Regenerate", "vanilla-sand-layer-suppression"),
    ("JobDriver_ClearSnowAndSand", "MakeNewToils", "clear-sand-yield"),
)
CONTROL_METHOD = ("Thing", "SpawnSetup")
BOUND_BIOMES = ("Desert", "ExtremeDesert")
_FIELD = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def shipped_defs():
    """[(DefType, defName)] for every non-abstract top-level def under Defs/, from the XML. A def whose tag is a
    namespaced class (RimMandrake.MovingDunes.RM_DuneMaterialDef) is asked by its short class name."""
    out = []
    for dp, _d, files in os.walk(os.path.join(HERE, "Defs")):
        for fn in sorted(files):
            if fn.endswith(".xml"):
                for el in ET.parse(os.path.join(dp, fn)).getroot():
                    nm = el.find("defName") if isinstance(el.tag, str) else None
                    if nm is not None and nm.text and el.get("Abstract", "").lower() != "true":
                        out.append((el.tag.split(".")[-1], nm.text.strip()))
    return sorted(set(out))


SHIPPED = shipped_defs()


def settings_fields():
    src = open(os.path.join(HERE, "Source", "MovingDunesSettings.cs"), encoding="utf-8").read()
    body = src.split("class MovingDunesSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


def static_checks():
    bad = []
    if len(SHIPPED) < 3:
        return ["only %d defs parsed from Defs/ (sanity probe failed)" % len(SHIPPED)]
    fields = settings_fields()
    if not fields:
        return ["settings probe found no field (sanity probe failed)"]
    src = open(os.path.join(HERE, "Source", "MovingDunesSettings.cs"), encoding="utf-8").read()
    scribed = src.split("ExposeData", 1)[1]
    ui = scribed.split("DoWindowContents", 1)[1]
    for n in fields:
        if '"%s"' % n not in scribed:
            bad.append("settings field %s is not Scribed" % n)
        if not re.search(r"\b%s\b" % n, ui):
            bad.append("settings field %s has no control in DoWindowContents" % n)
    proj = open(os.path.join(HERE, "Source", "RimMandrake_MovingDunes.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    mod = open(os.path.join(HERE, "Source", "MovingDunesMod.cs"), encoding="utf-8").read()
    for ty, me, rule in RULES:
        if 'rule: "%s"' % rule not in mod or '"%s"' % me not in mod:
            bad.append("MovingDunesMod.cs no longer declares rule %s on %s.%s" % (rule, ty, me))
    dbg = open(os.path.join(HERE, "Source", "MovingDunesDebugActions.cs"), encoding="utf-8").read()
    for label in ("Dune field: report", "Dune field: shift wind", "Dune field: run 100 batches"):
        if '"%s"' % label not in dbg:
            bad.append("debug action %r is gone: the dune_field_report chain reads it" % label)
    bind = open(os.path.join(HERE, "Patches", "BiomeBindings.xml"), encoding="utf-8").read()
    for b in BOUND_BIOMES:
        if 'defName="%s"' % b not in bind:
            bad.append("BiomeBindings.xml no longer binds %s" % b)
    kinds = set(ty for ty, _n in SHIPPED)
    for need in ("ThingDef", "RM_DuneMaterialDef", "RM_DuneGlobalsDef"):
        if need not in kinds:
            bad.append("no %s parsed from Defs/" % need)
    if not os.path.isfile(os.path.join(HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "MovingDunes.md")):
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
    suite = Suite("MovingDunes")
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

    def _flat(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k)
                for s in _flat(v):
                    yield s
        elif isinstance(o, (list, tuple)):
            for v in o:
                for s in _flat(v):
                    yield s
        elif o is not None:
            yield str(o)

    def _owners(r):
        out = []
        for m in (r.get("methods") or []):
            for key in ("prefixes", "postfixes", "transpilers", "finalizers"):
                out.extend(p.get("owner") for p in (m.get(key) or []))
        return out

    def _act(t, path):
        """Run a debug action; return (ok, its own tagged log lines). Never drain_log (stale first message)."""
        r = t.bridge_call("rimworld/execute_debug_action", path=path)
        if not _live(t):
            return False, []
        if not isinstance(r, dict) or r.get("success") is not True:
            _unmeasured(t, "debug action %s did not succeed (the 'Actions\\<label>' path is the sibling-mod "
                           "convention, not yet proven for this menu): %s" % (path, str(r)[:160]))
            return False, []
        lines = []
        for row in ((r.get("effects") or {}).get("logs") or []):
            lines.append(row if isinstance(row, str) else str(row.get("text") or row.get("message") or ""))
        lines = [l for l in lines if TAG in l]
        if not lines:
            _unmeasured(t, "debug action %s succeeded but logged no %s line (check Player.log for 'Reached max "
                           "messages limit')" % (path, TAG))
            return False, []
        return True, lines

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
            r = t.bridge_call("jawa/get_defs", defs=";".join(names), fields="defName", limit=20)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is False:
                    raise ExpectationFailed("get_defs failed: %r" % r)
                if r.get("notFound") or int(r.get("foundCount", 0)) != len(names):
                    raise ExpectationFailed("%r of %d defs resolved; notFound=%r" % (r.get("foundCount"), len(names), r.get("notFound")))

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
                if old is None:
                    raise ExpectationFailed("%s: get returned no value" % field)
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else str(float(old) + 1.0)
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

    @suite.chain("harmony_rules")
    def harmony_rules(t):
        with t.component("control_method_carries_no_patch_of_ours", beyond_toggle=True):
            r = t.bridge_call("jawa/harmony_patches", typeName=CONTROL_METHOD[0], methodName=CONTROL_METHOD[1])
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                    _unmeasured(t, "harmony_patches could not be asked on the control: %s" % str(r)[:160])
                    return
                if HARMONY_ID in _owners(r):
                    raise ExpectationFailed("control %s.%s reads as patched by %s: the owner check cannot say absent"
                                            % (CONTROL_METHOD + (HARMONY_ID,)))
        for ty, me, rule in RULES:
            with t.component("rule_%s_attached" % rule.replace("-", "_"), beyond_toggle=True):
                r = t.bridge_call("jawa/harmony_patches", typeName=ty, methodName=me)
                if _live(t):
                    if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                        _unmeasured(t, "harmony_patches could not be asked for %s.%s (Odyssey type missing?): %s"
                                    % (ty, me, str(r)[:160]))
                        return
                    if HARMONY_ID not in _owners(r):
                        raise ExpectationFailed("%s.%s carries no patch from %s (owners: %s): rule '%s' is NOT in effect "
                                                "(the mod logs an error at startup when this happens)"
                                                % (ty, me, HARMONY_ID, sorted(set(o for o in _owners(r) if o))[:6], rule))

    @suite.chain("biome_bindings")
    def biome_bindings(t):
        for b in BOUND_BIOMES:
            with t.component("%s_carries_dune_field_extension" % b, beyond_toggle=True):
                r = t.bridge_call("jawa/get_defs", defs="BiomeDef/" + b, fields="modExtensions", limit=2)
                if _live(t):
                    rows = (r or {}).get("defs") or []
                    if not isinstance(r, dict) or r.get("success") is False or not rows:
                        raise ExpectationFailed("could not read BiomeDef %s: %r" % (b, r))
                    ext = (rows[0].get("fields") or {}).get("modExtensions")
                    if not isinstance(ext, list):
                        _unmeasured(t, "modExtensions of %s unreadable: %r" % (b, ext))
                        return
                    flat = " ".join(_flat(ext)).lower()
                    if "dunefieldextension" not in flat and "rm_dunes_sand" not in flat:
                        raise ExpectationFailed("%s has no DuneFieldExtension (the binding patch matched nothing, and a "
                                                "patch that matches nothing logs nothing): %s" % (b, str(ext)[:200]))

    @suite.chain("dune_field_report")
    def dune_field_report(t):
        state = {}
        with t.component("map_is_a_dune_field_and_rules_armed", beyond_toggle=True):
            ok, lines = _act(t, ACT_REPORT)
            if _live(t) and ok:
                line = lines[-1]
                if "not a dune field" in line or "this map is not a dune field" in line:
                    _unmeasured(t, "the current map's biome carries no DuneFieldExtension (needs a Desert/ExtremeDesert map "
                                   "or featureInOtherBiomes-style binding): %s" % line[:160])
                    return
                flags = dict(re.findall(r"(canHaveSand|decaySuppression|vanillaLayerSuppression)=(True|False)", line))
                if len(flags) != 3:
                    _unmeasured(t, "report line carries no armed flags: %s" % line[:200])
                    return
                off = [k for k, v in flags.items() if v != "True"]
                if off:
                    raise ExpectationFailed("rules not armed on a dune map: %s (%s)" % (off, line[:200]))
                state["wind"] = (re.search(r"wind=(\w+)", line) or [None, None])[1]
        with t.component("shift_wind_changes_the_wind", beyond_toggle=True):
            if _live(t):
                seen = set([state.get("wind")])
                for _ in range(6):
                    ok, _l = _act(t, ACT_SHIFT)
                    if not ok:
                        return
                    ok, lines = _act(t, ACT_REPORT)
                    if not ok:
                        return
                    seen.add((re.search(r"wind=(\w+)", lines[-1]) or [None, None])[1])
                    if len(seen) > 1:
                        break
                if len(seen) < 2:
                    raise ExpectationFailed("six wind shifts never changed the wind (still %s)" % list(seen))
        with t.component("batches_run_and_report_stays_readable", toggle="duneEngineEnabled"):
            if _live(t):
                ok, _l = _act(t, ACT_BATCHES)
                if not ok:
                    return
                ok, lines = _act(t, ACT_REPORT)
                if ok and not re.search(r"totalDepth=[\d.]+", lines[-1]):
                    raise ExpectationFailed("after 100 batches the report carries no totalDepth: %s" % lines[-1][:200])

    def _slow(name, toggle, why):
        @suite.chain(name)      # one chain each: an UNMEASURED reason must not bleed into the next mechanic
        def _chain(t):
            with t.component("state_read", toggle=toggle):
                if _live(t):
                    _unmeasured(t, why)

    for _n, _tg, _why in (
        ("slow_crests_hop_downwind_and_bank_in_shelter", "transportRateMultiplier",
         "sand depth changing by cell in the lee of a wall needs seeded drift (the seed debug action is a mouse-cell "
         "ToolMap the bridge cannot click) and many game hours of transport"),
        ("slow_upwind_influx_and_downwind_loss", "duneEngineEnabled",
         "influx and edge loss are day-scale accumulators (influxPerDay 25) and need a dune-field map"),
        ("slow_loose_gear_buried_and_returns", "burialEnabled",
         "burial needs >= 0.6 depth over an item outside stockpile/home area, then wind turning over game days; "
         "RM_Dunes_BuriedCache defs resolve in defs_resolve"),
        ("slow_deep_drift_kills_plants", "plantChokeEnabled",
         "plantChokeDays 3 on a plant under >= 0.5 depth: game days on a dune-field map"),
        ("slow_wind_locked_to_the_sun_on_stillsand", "windLockEnabled",
         "needs an RM_Stillsand map (owned by the Stillsand/biomes mods)"),
        ("slow_shovelled_drift_yields_sand", "clearYieldEnabled",
         "needs a drift cell, a clear-sand designation and a colonist job on an RM_Stillsand map"),
    ):
        _slow(_n, _tg, _why)

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
