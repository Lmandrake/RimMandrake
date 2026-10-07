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
  slow_*             one chain per slow mechanic (transport/banking, influx, burial, plant choke, wind lock, clear yield),
                     MOVINGDUNES_COVERAGE_GAPS_1: MovingDunesProof (static_call) reads the SHIPPED pure rules (attempts,
                     influx debt, choke sizing, wind-lock gate + bearing, yield) against values derived from the material
                     XML, drives the real burial API and (on a dune map) the real burial gate on/off and real transport
                     batches. Every setting's gate is also checked statically (gate_findings). What needs game days or a
                     colonist stays an UNMEASURED component placed last in its chain, naming the missing instrument.

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
    namespaced class keeps the FULL name (RimMandrake.MovingDunes.RM_DuneMaterialDef): get_defs resolves a
    custom def type only by its full name (measured live 2026-10-07)."""
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


def settings_fields():
    src = open(os.path.join(HERE, "Source", "MovingDunesSettings.cs"), encoding="utf-8").read()
    body = src.split("class MovingDunesSettings", 1)[1].split("ExposeData", 1)[0]
    return dict((m.group(2), m.group(1)) for m in _FIELD.finditer(re.sub(r"//[^\n]*", "", body)))


GATES = (   # (setting, file, method) -- the setting must be read INSIDE the method that does the work
    ("duneEngineEnabled", "MapComponent_DuneField.cs", "MapComponentTick"),
    ("transportRateMultiplier", "MapComponent_DuneField.cs", "MapComponentTick"),
    ("transportRateMultiplier", "MapComponent_DuneField.cs", "DebugRunBatches"),
    ("burialEnabled", "MapComponent_DuneField.cs", "TryBuryAt"),
    ("plantChokeEnabled", "MapComponent_DuneField.cs", "RunPlantChoke"),
    ("windLockEnabled", "MapComponent_DuneField.cs", "ApplyWindLock"),
    ("clearYieldEnabled", "Patch_ClearSandYield.cs", "Pay"),
    ("clearYieldMultiplier", "Patch_ClearSandYield.cs", "Pay"),
)
USES = (    # (shipped function the proof reads, file, method that must call it) -- else the proof proves a dead copy
    ("TransportAttempts(", "MapComponent_DuneField.cs", "RunTransportBatch"),
    ("InfluxDebtDelta(", "MapComponent_DuneField.cs", "RunInflux"),
    ("ChokeSamples(", "MapComponent_DuneField.cs", "RunPlantChoke"),
    ("ChokeDamage(", "MapComponent_DuneField.cs", "RunPlantChoke"),
    ("WindLockApplies(", "MapComponent_DuneField.cs", "ApplyWindLock"),
    ("YieldAmount(", "Patch_ClearSandYield.cs", "Pay"),
)


def load_sources():
    out = {}
    d = os.path.join(HERE, "Source")
    for fn in os.listdir(d):
        if fn.endswith(".cs"):
            out[fn] = open(os.path.join(d, fn), encoding="utf-8").read()
    return out


def method_body(src, name):
    """The brace-matched body of the first method called `name` (a declaration, not a call), or None."""
    for m in re.finditer(r"(?:public|private|internal|protected)[^;{=]*?\b%s\s*\([^)]*\)\s*\{" % re.escape(name), src):
        i, depth = m.end(), 1
        while i < len(src) and depth:
            depth += {"{": 1, "}": -1}.get(src[i], 0)
            i += 1
        return src[m.end():i]
    return None


def gate_findings(srcs):
    """Findings, each tagged [setting] or [function]: a setting no longer read where it does its job, or a proof-read
    function the shipped method no longer calls. Pure over {filename: text}, so the selftest can plant breaks."""
    bad = []
    for setting, fn, meth in GATES:
        body = method_body(re.sub(r"//[^\n]*", "", srcs.get(fn, "")), meth)
        if body is None:
            bad.append("[%s] %s: method %s not found" % (setting, fn, meth))
        elif "MovingDunesSettings.%s" % setting not in body:
            bad.append("[%s] %s.%s no longer reads MovingDunesSettings.%s (the toggle gates nothing)" % (setting, fn, meth, setting))
    for fnc, fn, meth in USES:
        body = method_body(re.sub(r"//[^\n]*", "", srcs.get(fn, "")), meth)
        if body is None or fnc not in body:
            bad.append("[%s] %s.%s no longer calls %s (the live proof would read a dead copy)" % (fnc.rstrip("("), fn, meth, fnc))
    return bad


def material_params():
    """Numbers of the shipped RM_Dunes_Sand material: the def's XML over the C# field defaults."""
    src = open(os.path.join(HERE, "Source", "RM_DuneMaterialDef.cs"), encoding="utf-8").read()
    out = dict((m.group(1), float(m.group(2))) for m in re.finditer(r"public float (\w+) = ([0-9.]+)f?;", src))
    for el in ET.parse(os.path.join(HERE, "Defs", "DuneMaterialDefs", "Materials.xml")).getroot():
        nm = el.find("defName")
        if nm is not None and nm.text == "RM_Dunes_Sand":
            for ch in el:
                if ch.tag in out and ch.text:
                    out[ch.tag] = float(ch.text)
    return out


def expected_attempts(mat, factor, cells=62500):
    """K = max(1, round(attemptsPerCellPerDay x cells / 240)); attempts = round(K x max(0.01, factor))."""
    k = max(1, int(round(mat["attemptsPerCellPerDay"] * cells / 240.0)))
    return int(round(k * max(0.01, factor)))


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
    bad.extend(gate_findings(load_sources()))
    if "MovingDunesProof.cs" not in proj or 'Compile Include="MovingDunesProof.cs"' not in proj:
        bad.append("MovingDunesProof.cs is not compiled: the proof chains read a method that does not exist")
    kinds = set(ty.split(".")[-1] for ty, _n in SHIPPED)
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
                new = ("False" if str(old).lower() == "true" else "True") if ty == "bool" else (str(int(float(old)) + 1) if ty == "int" else str(float(old) + 1.0))
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

    # MOVINGDUNES_COVERAGE_GAPS_1: the slow mechanics now carry offline-provable bars. MovingDunesProof (jawa/static_call)
    # runs the SHIPPED pure rules (transport attempts, influx debt, plant-choke sizing, wind-lock gate/bearing, clear
    # yield) under fixed numbers and drives the real burial API / real transport batches on a dune-field map. Expected
    # values are derived HERE from the material XML + documented formulas, never read back from the C#. What a proof
    # cannot show (game-day accumulators, a colonist's shovel job, an RM_Stillsand map) stays an explicit UNMEASURED
    # component placed LAST in its chain, naming the missing instrument.
    PROOF = "RimMandrake.MovingDunes.MovingDunesProof"
    mat = material_params()

    def _proof(t, method, args="x"):   # ProofMath/ProofBury take (string args); "" is rejected (LIVE 2026-10-07)
        r = t.bridge_call("jawa/static_call", type=PROOF, method=method, args=args)
        if not _live(t):
            return None, ""
        text = (r or {}).get("result") if isinstance(r, dict) else None
        if text in (None, ""):
            _unmeasured(t, "MovingDunesProof.%s answered nothing (DLL not rebuilt/deployed yet?): success=%s %s"
                        % (method, (r or {}).get("success"), str((r or {}).get("message") or (r or {}).get("error"))[:120]))
            return None, ""
        text = str(text)
        if text.startswith("ERROR"):
            raise ExpectationFailed("MovingDunesProof.%s: %s" % (method, text))
        return dict(re.findall(r"(\w+)=(\S+)", text)), text

    def _near(a, b, tol=0.01):
        return a is not None and abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))

    def _gates(t, setting):
        """The setting must be read inside the method that does the work (static, runs offline too)."""
        bad = [f for f in gate_findings(load_sources()) if ("[%s]" % setting) in f]
        if bad:
            raise ExpectationFailed("; ".join(bad))

    @suite.chain("slow_crests_hop_downwind_and_bank_in_shelter")
    def slow_transport(t):
        with t.component("transport_attempts_scale_with_the_drift_slider", toggle="transportRateMultiplier"):
            _gates(t, "transportRateMultiplier")
            kv, text = _proof(t, "ProofMath")
            if kv:
                a1, a2, a5 = expected_attempts(mat, 1.0), expected_attempts(mat, 2.0), expected_attempts(mat, 0.5)
                for key, want in (("att1", a1), ("att2", a2), ("att05", a5)):
                    if not _near(kv.get(key), want, 0.002):
                        raise ExpectationFailed("%s: %s attempts, XML-derived formula says %s (%s)" % (key, kv.get(key), want, text[:200]))
                if int(kv["att2"]) <= int(kv["att1"]) or int(kv["att05"]) >= int(kv["att1"]):
                    raise ExpectationFailed("drift slider does not scale transport attempts monotonically: %s" % text[:200])
        with t.component("sand_actually_moves_on_a_dune_field", beyond_toggle=True):
            kv, text = _proof(t, "ProofMove", "300")
            if kv:
                if kv.get("field") != "True":
                    _unmeasured(t, "the current map is not a dune field (needs a Desert/ExtremeDesert/Stillsand map)")
                elif float(kv.get("wind", "0")) < float(kv.get("thr", "0")):
                    _unmeasured(t, "wind %s is under the material threshold %s: a calm map moves nothing by design; "
                                   "retry in a gust" % (kv.get("wind"), kv.get("thr")))
                elif int(kv.get("changed", "0")) < 1:
                    raise ExpectationFailed("300 batches under wind >= threshold changed no cell's sand depth: %s" % text)
        with t.component("banking_in_a_wall_lee_state_read", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "sand depth changing by cell in the lee of a wall needs seeded drift (the seed debug action "
                               "is a mouse-cell ToolMap the bridge cannot click); instrument missing: a [Tool] that seeds "
                               "a slab and reads the lee cell")

    @suite.chain("slow_upwind_influx_and_downwind_loss")
    def slow_influx(t):
        with t.component("influx_baseline_scales_with_the_drift_slider_once", beyond_toggle=True):
            kv, text = _proof(t, "ProofMath")
            if kv:
                base = mat["influxPerDay"] / 240.0
                if not _near(kv.get("infl_base1"), base, 0.002) or not _near(kv.get("infl_base2"), 2 * base, 0.002):
                    raise ExpectationFailed("baseline influx %s / %s, want %s / %s (flat per-day term x weather x slider, once): %s"
                                            % (kv.get("infl_base1"), kv.get("infl_base2"), base, 2 * base, text[:200]))
        with t.component("loss_term_is_not_squared_by_the_slider", beyond_toggle=True):
            kv, text = _proof(t, "ProofMath")
            if kv:
                want = 10.0 * mat["influxLossRatio"]
                for key in ("infl_loss1", "infl_loss2"):
                    if not _near(kv.get(key), want, 0.002):
                        raise ExpectationFailed("%s: lost 10 gives %s debt, want %s (the 2026-09-11 slider-squared bug): %s"
                                                % (key, kv.get(key), want, text[:200]))
        with t.component("engine_off_gate_reads_duneEngineEnabled", toggle="duneEngineEnabled"):
            _gates(t, "duneEngineEnabled")
        with t.component("edge_loss_and_influx_over_days_state_read", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "edge loss and influx are day-scale accumulators (influxPerDay) needing real ticks on a dune "
                               "map; instrument missing: a tick-free influx probe reading TotalDepth across ProofRunInflux")

    @suite.chain("slow_loose_gear_buried_and_returns")
    def slow_burial(t):
        with t.component("burial_api_caches_the_thing_and_removes_it_from_the_map", beyond_toggle=True):
            kv, text = _proof(t, "ProofBury")
            if kv:
                if kv.get("api_cache") != "True" or kv.get("api_count") != "1" or kv.get("api_spawned") != "False":
                    raise ExpectationFailed("BuryThingsAt did not leave exactly one cached, despawned item: %s" % text)
        with t.component("only_wild_unforbidden_loot_is_a_burial_candidate", beyond_toggle=True):
            kv, text = _proof(t, "ProofBury")
            if kv:
                if kv.get("cand") != "True":
                    raise ExpectationFailed("a free item outside the home area is not a burial candidate: %s" % text)
                if kv.get("cand_forbidden") != "False":
                    raise ExpectationFailed("a forbidden item IS a burial candidate (the colony's stores are exempt): %s" % text)
        with t.component("burialEnabled_off_arm_buries_nothing", toggle="burialEnabled"):
            _gates(t, "burialEnabled")
            kv, text = _proof(t, "ProofBury")
            if kv:
                if kv.get("field") != "True":
                    _unmeasured(t, "the current map is not a dune field, so the real burial gate (TryBuryAt) cannot be reached")
                elif kv.get("arm_off_cache") != "False" or kv.get("arm_off_spawned") != "True":
                    raise ExpectationFailed("burialEnabled=false still buried the item: %s" % text)
                elif kv.get("arm_on_cache") != "True" or kv.get("arm_on_spawned") != "False":
                    raise ExpectationFailed("burialEnabled=true did not bury a candidate on a dune field: %s" % text)
        with t.component("burial_by_advancing_drift_and_wind_turn_return_state_read", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "an advancing dune depositing >= burialDepth then the wind turning over game days; "
                               "instrument missing: a tick-free deposit probe (burial half is proven by the arms above)")

    @suite.chain("slow_deep_drift_kills_plants")
    def slow_choke(t):
        with t.component("choke_sample_rate_scales_with_the_drift_slider", beyond_toggle=True):
            kv, text = _proof(t, "ProofMath")
            if kv:
                for key, f in (("choke1", 1.0), ("choke2", 2.0)):
                    want = expected_attempts(mat, f) * mat["plantChokeSampleFraction"]
                    if not _near(kv.get(key), want, 0.002):
                        raise ExpectationFailed("%s: %s samples, XML-derived formula says %s: %s" % (key, kv.get(key), want, text[:200]))
        with t.component("choke_damage_kills_a_buried_plant_in_plantChokeDays", beyond_toggle=True):
            kv, text = _proof(t, "ProofMath")
            if kv:
                if int(kv.get("dmg_a", "0")) != 17 or int(kv.get("dmg_b", "0")) != 1:
                    raise ExpectationFailed("damage per visit for 100hp/3d/2 visits is %s (want 17), floor-of-1 case %s (want 1): %s"
                                            % (kv.get("dmg_a"), kv.get("dmg_b"), text[:200]))
        with t.component("plant_choke_gate_reads_plantChokeEnabled", toggle="plantChokeEnabled"):
            _gates(t, "plantChokeEnabled")
        with t.component("plants_dying_over_game_days_state_read", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "plantChokeDays 3 on a plant under >= 0.5 depth: game days on a dune-field map; "
                               "instrument missing: a [Tool] that runs RunPlantChoke on a staged plant")

    @suite.chain("slow_wind_locked_to_the_sun_on_stillsand")
    def slow_windlock(t):
        with t.component("lock_applies_only_with_setting_and_a_locking_biome", toggle="windLockEnabled"):
            _gates(t, "windLockEnabled")
            kv, text = _proof(t, "ProofMath")
            if kv:
                want = {"lock_tt": "True", "lock_ft": "False", "lock_tf": "False", "lock_tn": "False"}
                bad = dict((k, kv.get(k)) for k, v in want.items() if kv.get(k) != v)
                if bad:
                    raise ExpectationFailed("wind-lock gate truth table wrong %s (want %s): %s" % (bad, want, text[:200]))
        with t.component("locked_wind_follows_the_sun_bearing", beyond_toggle=True):
            kv, text = _proof(t, "ProofMath")
            if kv:
                # from (0,0): substellar due north = bearing 0, due east = 90; the wind blows along the shadows (+180)
                want = {"bear_n": 0.0, "bear_e": 90.0}
                for k, v in want.items():
                    if not _near(kv.get(k), v, 0.001):
                        raise ExpectationFailed("%s = %s, want %s: %s" % (k, kv.get(k), v, text[:200]))
                for k, v in (("wind_away_n", "4"), ("wind_toward_n", "0"), ("wind_away_e", "6")):
                    if kv.get(k) != v:
                        raise ExpectationFailed("%s = %s, want %s (0 = north, clockwise, 8-way): %s" % (k, kv.get(k), v, text[:200]))
        with t.component("stillsand_map_wind_is_locked_state_read", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "needs an RM_Stillsand map (owned by the Stillsand/biomes mods) to read the live wind index")

    @suite.chain("slow_shovelled_drift_yields_sand")
    def slow_yield(t):
        with t.component("yield_scales_with_depth_removed_and_multiplier", toggle="clearYieldMultiplier"):
            _gates(t, "clearYieldMultiplier")
            kv, text = _proof(t, "ProofMath")
            if kv:
                if not _near(kv.get("yield_on"), 0.5 * 6.0, 0.002) or not _near(kv.get("yield_x2"), 0.5 * 6.0 * 2.0, 0.002):
                    raise ExpectationFailed("0.5 depth x 6/depth yields %s (want 3), x2 slider %s (want 6): %s"
                                            % (kv.get("yield_on"), kv.get("yield_x2"), text[:200]))
        with t.component("clearYieldEnabled_off_arm_yields_nothing", toggle="clearYieldEnabled"):
            _gates(t, "clearYieldEnabled")
            kv, text = _proof(t, "ProofMath")
            if kv and not _near(kv.get("yield_off"), 0.0, 0.0001):
                raise ExpectationFailed("clearYieldEnabled=false still yields %s: %s" % (kv.get("yield_off"), text[:200]))
        with t.component("colonist_shovel_job_pays_the_yield_state_read", beyond_toggle=True):
            if _live(t):
                _unmeasured(t, "needs a drift cell, a clear-sand designation and a colonist job on an RM_Stillsand map; "
                               "instrument missing: a [Tool] that runs Patch_ClearSand_Yield.Pay on a staged cell")

    return suite


suite = _build_suite() if Suite is not None else None

if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
