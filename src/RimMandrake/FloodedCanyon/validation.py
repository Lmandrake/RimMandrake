"""validation.py -- modcheck suite for RimMandrake: Flooded Canyon (mandrake.rm.floodedcanyon).

First script (debug_process.md section 2), item FLOODED_CANYON_FIRST_SCRIPT_1. Walk:
design/validation_walks/RimMandrake/FloodedCanyon.md (`## must be true`, each line ends in
`-> chain.component` or `-> UNCOVERED: why`). NEVER RUN LIVE YET; every live shape below that is
unproven degrades to UNMEASURED, never PASS.

Run offline: `python3 src/RimMandrake/FloodedCanyon/validation.py` -> `STATIC: PASS (0 findings)`.
Live: modcheck/northstar_driver on a tier carrying `mandrake.rm.floodedcanyon` + FlowWorks (its hard
dependency) + Explosive Growth (the soak chain; absent = that chain is UNMEASURED).

OBSERVATION CHANNEL. The mod has no bridge [Tool]; its state surface is its debug menu
(`Source/Debug/RM_FloodedCanyonDebugActions.cs`, category RMFloodedCanyon), driven through
`rimworld/execute_debug_action` with path `Actions\\<label>` (the Inhabited/ExplosiveGrowth pattern) and
read from THAT CALL'S OWN `effects.logs` (never `drain_log`: it returns a stale first message). Every
action prints `[RMFloodedCanyonDebug] ...`; the flood report is one line of `key=value` pairs
(`phase= nextFloodTick= activeFloodCells= raisedFillCells= active= explosiveGrowth= tarruqSilenced= ...`).
An action that succeeded but logged nothing is UNMEASURED (RimWorld stops logging at 10,000 messages).

SITE. The flood component only runs on an RM_FloodedCanyon map OR with `featureInOtherBiomes` on (its
own cross-biome toggle), so every behaviour chain arms `featureInOtherBiomes` on the bland site and
restores it in a `finally`. `DebugArmFloodSoon` sets nextFloodTick = now+1, so the whole warning
(Herald, Warned, Flooding) plays in ~3 ticks: the sequence chain polls the report one tick at a time.
The footprint is a BFS over the whole map's eligible cells (open, unroofed, unfogged, dry), so a bland
open site always has one.
"""
import contextlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))      # `python3 validation.py` finds modcheck

SETTINGS = "RimMandrake.FloodedCanyon.RM_FloodedCanyonSettings"
TAG = "[RMFloodedCanyonDebug]"
EG_TAG = "[RMExplosiveGrowthDebug]"
P_ARM = "Actions\\Arm chime + flood soon (current map)"
P_START = "Actions\\Start flood NOW (current map)"
P_REPORT = "Actions\\Report flood state (current map)"
P_RECEDE = "Actions\\Recede flood NOW (current map)"
P_AFTER = "Actions\\Report recede aftermath (current map)"
P_SEAMS = "Actions\\Report fossil seams (current map)"
P_EG_REPORT = "Actions\\Report state (current map)"


# --------------------------------------------------------------------------- parsed facts (never hand-listed)

def settings_defaults():
    """{field: (type, default)} parsed from the settings class's own `public static` initialisers."""
    src = open(os.path.join(HERE, "Source", "RM_FloodedCanyonMod.cs"), encoding="utf-8").read()
    body = src.split("class RM_FloodedCanyonSettings")[1].split("ExposeData")[0]
    out = {}
    for typ, name, val in re.findall(r"public static (bool|float|int) (\w+)\s*=\s*([^;]+);", body):
        v = val.strip()
        out[name] = (typ, (v == "true") if typ == "bool" else (float(v.rstrip("f")) if typ == "float" else int(v)))
    return out


def shipped_defs():
    """(defType, defName) for every concrete top-level def in the mod's own Defs/ XML."""
    out = []
    for dp, _, files in os.walk(os.path.join(HERE, "Defs")):
        for f in sorted(files):
            if f.endswith(".xml"):
                for e in ET.parse(os.path.join(dp, f)).getroot():
                    n = e.findtext("defName")
                    if n and e.get("Abstract") != "True":
                        out.append((e.tag.split(".")[-1], n))
    return out


try:
    from modcheck import Suite, ExpectationFailed
except ImportError:                       # offline static run outside the modcheck path
    Suite = None

if Suite is not None:
    suite = Suite("FloodedCanyon")
    SD = settings_defaults()
    suite.toggles = [f for f, (ty, _) in SD.items() if ty == "bool"]

    # ----------------------------------------------------------------------- helpers

    def _live(t):
        return t.session is not None and not t.upstream_failed

    def _fail(msg):
        raise ExpectationFailed(msg)

    class _Unmeasured(Exception):
        pass

    def _unmeasured(t, why):
        t._why = why
        t._record("UNMEASURED", why)
        t.upstream_failed = True
        raise _Unmeasured(why)

    @contextlib.contextmanager
    def _comp(t, name, **kw):
        """t.component() with the UNMEASURED fix-up: verdict stays UNMEASURED, detail names the reason, and
        the chain is not poisoned for an independent next component."""
        before = t.upstream_failed
        t._why = None
        with t.component(name, **kw) as tt:
            yield tt
        why = getattr(t, "_why", None)
        if why and not before:
            t.components[-1].detail = "UNMEASURED: %s" % why
            t.upstream_failed = False
        t._why = None
        if t.session is not None:
            c = t.components[-1]
            print("[fc] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
                  file=sys.stderr, flush=True)

    def _sv(v):
        if isinstance(v, bool):
            return "True" if v else "False"
        if isinstance(v, float):
            return "%g" % v
        return str(v)

    def _same(got, want):
        if str(got).strip().lower() == str(want).strip().lower():
            return True
        try:
            return abs(float(got) - float(want)) < 1e-6
        except (TypeError, ValueError):
            return False

    def _put(t, field, value):
        s = t.session
        if s is None:
            return
        sv = _sv(value)
        r = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=sv)
        if not (r or {}).get("success"):
            raise ExpectationFailed("mod_settings_field set %s=%s failed: %r" % (field, sv, r))
        g = s.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not (g or {}).get("success") or not _same((g or {}).get("value"), sv):
            raise ExpectationFailed("mod_settings_field %s did not take: wrote %s, read back %r"
                                    % (field, sv, (g or {}).get("value")))

    def _get(t, field):
        g = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field)
        if not (g or {}).get("success"):
            raise ExpectationFailed("mod_settings_field get %s failed: %r" % (field, g))
        return g.get("value")

    @contextlib.contextmanager
    def _arm(t, **values):
        """Set settings for the body; ALWAYS restore each to its shipped (parsed) default."""
        try:
            for f, v in values.items():
                _put(t, f, v)
            yield
        finally:
            for f in values:
                try:
                    _put(t, f, SD[f][1])
                except Exception as e:
                    print("[fc] RESTORE FAILED %s: %s" % (f, e), file=sys.stderr, flush=True)

    def _log_texts(r):
        out = []
        for row in ((r or {}).get("effects") or {}).get("logs") or []:
            out.append(row if isinstance(row, str) else str(row.get("text") or row.get("message") or row.get("msg") or ""))
        return out

    def _act(t, path, tag=TAG):
        """Run a debug action; return its own tagged log lines. Not success = FAIL; no line = UNMEASURED."""
        r = t.bridge_call("rimworld/execute_debug_action", path=path)
        if not _live(t):
            return []
        if not isinstance(r, dict) or r.get("success") is not True:
            _fail("execute_debug_action %s did not succeed: %r" % (path, r))
        lines = [l for l in _log_texts(r) if tag in l]
        if not lines:
            _unmeasured(t, "debug action %s answered success but logged no %s line (logCount=%s): check Player.log "
                           "for 'Reached max messages limit', or the action path is wrong, before blaming the mod"
                           % (path, tag, ((r.get("effects") or {}).get("logCount"))))
        return lines

    def _state(t):
        """Parse the flood report line into {key: value-string}."""
        lines = _act(t, P_REPORT)
        if not _live(t):
            return {}
        line = [l for l in lines if "phase=" in l]
        if not line:
            _unmeasured(t, "flood report has no phase= field: %r" % lines[-1][:200])
        st = dict(re.findall(r"(\w+)=(\S+)", line[-1]))
        need = ("phase", "activeFloodCells", "raisedFillCells", "active", "explosiveGrowth", "lastRecedeTick", "nextFloodTick", "nowTick")
        if any(k not in st for k in need):
            _unmeasured(t, "flood report shape not understood: %r" % line[-1][:300])
        t._record("flood_state", st)
        return st

    def _n(st, k):
        try:
            return int(st[k])
        except (KeyError, ValueError):
            return -999999

    def _settle(t):
        """Bring the map to phase Dry with no standing flood, whatever an earlier chain left."""
        t.clear_area(size=24)
        st = _state(t)
        if _live(t) and st.get("phase") == "Flooding":
            _act(t, P_RECEDE)
            t.wait_ticks(30)
            st = _state(t)
            if st.get("phase") != "Dry":
                _fail("could not settle the site: phase still %r after Recede NOW" % st.get("phase"))
        return st

    def _eg_soaked(t):
        """Explosive Growth's own soaked-cell count from its report (head `soaked=N`)."""
        lines = _act(t, P_EG_REPORT, EG_TAG)
        if not _live(t):
            return 0
        m = re.search(r"soaked=(\d+)", " ".join(lines))
        if not m:
            _unmeasured(t, "Explosive Growth report has no soaked= field: %r" % lines[-1][:200])
        return int(m.group(1))

    def _seams(t):
        lines = _act(t, P_SEAMS)
        if not _live(t):
            return 0
        m = re.search(r"impression=(\d+) skeleton=(\d+) unique=(\d+)", " ".join(lines))
        if not m:
            _unmeasured(t, "seam report unparseable: %r" % lines[-1][:200])
        return sum(int(g) for g in m.groups())

    def _after(t):
        lines = _act(t, P_AFTER)
        if not _live(t):
            return {}
        line = " ".join(lines)
        d = dict(re.findall(r"(\w+)=(-?\d+)", line))
        if not all(k in d for k in ("cohort", "migrants", "salvage")):
            _unmeasured(t, "aftermath report unparseable: %r" % line[:200])
        return {k: int(v) for k, v in d.items()}

    def _flood_once(t):
        """ArmSoon, let the 3-tick warning play, return the standing-flood state."""
        _act(t, P_ARM)
        t.wait_ticks(30)
        return _state(t)

    # ----------------------------------------------------------------------- 1. defs_resolve

    @suite.chain("defs_resolve")
    def defs_resolve(t):
        """Every def the mod ships (parsed from its own Defs/ XML) resolves live; a control reads absent."""
        with _comp(t, "shipped_defs_resolve", beyond_toggle=True):
            for typ, name in shipped_defs():
                r = t.bridge_call("jawa/get_defs", defs="%s/%s" % (typ, name))
                if _live(t):
                    if not isinstance(r, dict) or r.get("success") is not True:
                        _unmeasured(t, "get_defs %s/%s could not be asked: %s" % (typ, name, str(r)[:140]))
                    if r.get("notFound") or r.get("foundCount") != 1:
                        _fail("shipped def did not load (a def with an unresolvable field is discarded silently): "
                              "%s/%s -> %r" % (typ, name, r))
        with _comp(t, "control_absent_def_reads_absent", beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="BiomeDef/RM_FloodedCanyon_NoSuchControl")
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True:
                    _unmeasured(t, "control ask failed: %s" % str(r)[:140])
                if r.get("foundCount") != 0 or not r.get("notFound"):
                    _fail("the probe cannot say absent: control returned %r" % r)

    # ----------------------------------------------------------------------- 2. settings round trips

    def _alt(typ, d):
        return (not d) if typ == "bool" else (d + 1 if typ == "int" else d * 2 + 1)

    def _make_flip(field, typ, default):
        def chain(t):
            with _comp(t, "%s_round_trips" % field, toggle=field if typ == "bool" else None, beyond_toggle=typ != "bool"):
                try:
                    _put(t, field, _alt(typ, default))
                    _put(t, field, default)
                finally:
                    if t.session is not None:
                        try:
                            _put(t, field, default)
                        except Exception as e:
                            print("[fc] RESTORE FAILED %s: %s" % (field, e), file=sys.stderr, flush=True)
        chain.__doc__ = "Write alt, read back, write default, read back (numeric compare) for %s." % field
        return chain

    for _f, (_ty, _d) in SD.items():
        suite.chain("flip_%s" % _f)(_make_flip(_f, _ty, _d))

    # ----------------------------------------------------------------------- 3. behaviour chains

    @suite.chain("feature_gate_off")
    def feature_gate_off(t):
        """CONTROL: off a canyon biome and with featureInOtherBiomes off, the cycle is inert."""
        with _comp(t, "cycle_inert_on_plain_map", toggle="featureInOtherBiomes"):
            with _arm(t, featureInOtherBiomes=False, floodCycleEnabled=True):
                st = _settle(t)
                if _live(t) and st.get("active") != "False":
                    _unmeasured(t, "SITE: this map reads active=%s with the feature off, so it is a canyon-biome map; "
                                   "the control needs a plain biome" % st.get("active"))
                st = _flood_once(t)
                if _live(t) and (st.get("phase") == "Flooding" or _n(st, "activeFloodCells") != 0):
                    _fail("the cycle ran on a non-canyon map with featureInOtherBiomes off: %r" % st)

    @suite.chain("flood_cycle")
    def flood_cycle(t):
        """Arm -> the warning plays -> the wall stands on a footprint -> recede clears it and reschedules."""
        with _comp(t, "arm_reaches_standing_flood", toggle="floodCycleEnabled"):
            with _arm(t, featureInOtherBiomes=True, floodCycleEnabled=True):
                _settle(t)
                st = _flood_once(t)
                if _live(t):
                    if st.get("active") != "True":
                        _fail("component not active with featureInOtherBiomes on: %r" % st)
                    if st.get("phase") != "Flooding":
                        _fail("30 ticks after Arm the phase is %r, not Flooding" % st.get("phase"))
                    if _n(st, "activeFloodCells") + _n(st, "raisedFillCells") <= 0:
                        _unmeasured(t, "SITE: Flooding with an empty footprint: no eligible open cell on this map")
        with _comp(t, "recede_clears_footprint_and_reschedules", beyond_toggle=True):
            with _arm(t, featureInOtherBiomes=True):
                if _live(t):
                    now = _state(t)
                    if now.get("phase") != "Flooding":
                        _unmeasured(t, "no standing flood to recede (previous component did not leave one)")
                _act(t, P_RECEDE)
                t.wait_ticks(30)
                st = _state(t)
                if _live(t):
                    if st.get("phase") != "Dry":
                        _fail("after Recede NOW the phase is %r, not Dry" % st.get("phase"))
                    if _n(st, "activeFloodCells") != 0 or _n(st, "raisedFillCells") != 0:
                        _fail("footprint not cleared after recede: %r" % st)
                    if _n(st, "lastRecedeTick") < 0:
                        _fail("lastRecedeTick not stamped on recede: %r" % st)
                    if _n(st, "nextFloodTick") <= _n(st, "nowTick"):
                        _fail("next flood not rescheduled into the future: %r" % st)

    @suite.chain("master_switch_off")
    def master_switch_off(t):
        """floodCycleEnabled off: Arm does nothing (the component reads active=False)."""
        with _comp(t, "master_off_refuses_flood", toggle="floodCycleEnabled"):
            with _arm(t, featureInOtherBiomes=True, floodCycleEnabled=False):
                _settle(t)
                st = _flood_once(t)
                if _live(t):
                    if st.get("active") != "False":
                        _fail("active=%s with floodCycleEnabled off" % st.get("active"))
                    if st.get("phase") == "Flooding" or _n(st, "activeFloodCells") != 0:
                        _fail("a flood ran with the master switch off: %r" % st)

    def _phase_walk(t, ticks=10):
        """Arm, then read the phase once per tick; returns the ordered distinct phases seen."""
        _act(t, P_ARM)
        seen = []
        for _ in range(ticks):
            t.wait_ticks(1)
            ph = _state(t).get("phase") if _live(t) else None
            if ph and (not seen or seen[-1] != ph):
                seen.append(ph)
            if ph == "Flooding":
                break
        return seen

    @suite.chain("warning_sequence_five_beats")
    def warning_sequence_five_beats(t):
        """fiveBeatsEnabled on: Dry -> Herald -> Warned -> Flooding, in that order, and the tarruq go silent."""
        with _comp(t, "herald_then_chime_then_wall", toggle="fiveBeatsEnabled"):
            with _arm(t, featureInOtherBiomes=True, fiveBeatsEnabled=True, floodCycleEnabled=True):
                _settle(t)
                seen = _phase_walk(t)
                if _live(t):
                    want = ["Herald", "Warned", "Flooding"]
                    idx = [seen.index(p) if p in seen else -1 for p in want]
                    if -1 in idx or idx != sorted(idx):
                        # Tick granularity can hide a one-tick phase: a missing phase is UNMEASURED only if the
                        # wall itself was reached; an unreached wall is a FAIL.
                        if "Flooding" not in seen:
                            _fail("the warning never reached Flooding: saw %r" % seen)
                        _unmeasured(t, "phase poll saw %r: a one-tick phase may have fallen between polls" % seen)
                    st = _state(t)
                    if st.get("tarruqSilenced") != "True":
                        _fail("tarruq not silenced while Flooding with fiveBeats on: %r" % st.get("tarruqSilenced"))
        with _comp(t, "five_beats_off_skips_herald", toggle="fiveBeatsEnabled"):
            with _arm(t, featureInOtherBiomes=True, fiveBeatsEnabled=False, floodCycleEnabled=True):
                _settle(t)
                seen = _phase_walk(t)
                if _live(t):
                    if "Flooding" not in seen:
                        _fail("with fiveBeats off the warning never reached Flooding: saw %r" % seen)
                    if "Herald" in seen:
                        _fail("Herald phase entered with fiveBeatsEnabled off: %r" % seen)
                    st = _state(t)
                    if st.get("tarruqSilenced") == "True":
                        _fail("tarruq silenced with fiveBeatsEnabled off (the hush is a five-beats beat)")

    @suite.chain("soak_coupling")
    def soak_coupling(t):
        """The flood hands its cells to Explosive Growth as soaked; growthCouplingEnabled off hands none."""
        with _comp(t, "flood_soaks_cells_via_explosive_growth", toggle="growthCouplingEnabled"):
            with _arm(t, featureInOtherBiomes=True, floodCycleEnabled=True):
                st = _settle(t)
                if _live(t) and st.get("explosiveGrowth", "").startswith("ABSENT"):
                    _unmeasured(t, "Explosive Growth is not loaded on this tier (report says ABSENT): the soak is a "
                                   "no-op by design, which the flood_cycle chain covers; run on a list carrying it")
                base = _eg_soaked(t)
                with _arm(t, growthCouplingEnabled=False):
                    st = _flood_once(t)
                    if _live(t) and _n(st, "activeFloodCells") + _n(st, "raisedFillCells") <= 0:
                        _unmeasured(t, "SITE: empty footprint, nothing to soak")
                    off = _eg_soaked(t)
                    _act(t, P_RECEDE)
                    t.wait_ticks(30)
                if _live(t) and off != base:
                    _fail("growthCouplingEnabled off yet Explosive Growth's soaked count moved %d -> %d" % (base, off))
                _flood_once(t)
                on = _eg_soaked(t)
                if _live(t) and not on > off:
                    _fail("flood with coupling on soaked nothing in Explosive Growth (soaked %d -> %d)" % (off, on))
                _act(t, P_RECEDE)
                t.wait_ticks(30)

    @suite.chain("recede_salvage")
    def recede_salvage(t):
        """Floodline salvage: a recede scatters salvage; floodlineSalvageEnabled off scatters none."""
        with _comp(t, "salvage_scattered_only_when_enabled", toggle="floodlineSalvageEnabled"):
            with _arm(t, featureInOtherBiomes=True, floodCycleEnabled=True, recedeFeastEnabled=False):
                _settle(t)
                b0 = _after(t)
                with _arm(t, floodlineSalvageEnabled=False):
                    _flood_once(t)
                    _act(t, P_RECEDE)
                    t.wait_ticks(30)
                    a0 = _after(t)
                if _live(t) and a0.get("salvage", 0) != b0.get("salvage", 0):
                    _fail("salvage scattered with floodlineSalvageEnabled off: %r -> %r" % (b0, a0))
                _flood_once(t)
                _act(t, P_RECEDE)
                t.wait_ticks(30)
                a1 = _after(t)
                if _live(t) and not a1.get("salvage", 0) > a0.get("salvage", 0):
                    _unmeasured(t, "recede with salvage on scattered nothing (%r -> %r): no standable dry cell in "
                                   "the footprint on this site, or a real fault; re-run on an open map" % (a0, a1))

    @suite.chain("recede_feast")
    def recede_feast(t):
        """The irqit carpet hatches on a recede; recedeFeastEnabled off hatches none."""
        with _comp(t, "irqit_cohort_only_when_enabled", toggle="recedeFeastEnabled"):
            with _arm(t, featureInOtherBiomes=True, floodCycleEnabled=True, floodlineSalvageEnabled=False):
                _settle(t)
                b0 = _after(t)
                with _arm(t, recedeFeastEnabled=False):
                    _flood_once(t)
                    _act(t, P_RECEDE)
                    t.wait_ticks(30)
                    a0 = _after(t)
                if _live(t) and a0.get("cohort", 0) != b0.get("cohort", 0):
                    _fail("irqit cohort grew with recedeFeastEnabled off: %r -> %r" % (b0, a0))
                _flood_once(t)
                _act(t, P_RECEDE)
                t.wait_ticks(30)
                a1 = _after(t)
                if _live(t) and not a1.get("cohort", 0) > a0.get("cohort", 0):
                    _fail("recede with the feast on hatched no irqit cohort (%r -> %r); RM_Irqit resolved "
                          "in defs_resolve, so this is the spawn path" % (a0, a1))

    @suite.chain("recede_seams")
    def recede_seams(t):
        """The flood re-cuts the ledger: fresh fossil seams along the wetted wall; off cuts none."""
        with _comp(t, "recede_recuts_seams_only_when_enabled", toggle="floodRecutSeamsEnabled"):
            with _arm(t, featureInOtherBiomes=True, floodCycleEnabled=True):
                _settle(t)
                s0 = _seams(t)
                with _arm(t, floodRecutSeamsEnabled=False):
                    _flood_once(t)
                    _act(t, P_RECEDE)
                    t.wait_ticks(30)
                    s1 = _seams(t)
                if _live(t) and s1 != s0:
                    _fail("seam count moved %d -> %d with floodRecutSeamsEnabled off" % (s0, s1))
                _flood_once(t)
                _act(t, P_RECEDE)
                t.wait_ticks(30)
                s2 = _seams(t)
                if _live(t) and not s2 > s1:
                    _unmeasured(t, "no new seam after a recede (%d -> %d): the footprint touched no natural, non-resource "
                                   "rock face on this site, or a real fault; the control above proves the off arm only" % (s1, s2))

    # ----------------------------------------------------------------------- 4. honest UNMEASURED

    def _um(chain, comp, why, toggle=None):
        def fn(t):
            with _comp(t, comp, toggle=toggle, beyond_toggle=toggle is None):
                _unmeasured(t, why)
        fn.__doc__ = "UNMEASURED: " + why
        suite.chain(chain)(fn)

    _um("flood_damage_light_and_nonfatal", "pawn_in_footprint_takes_light_blunt",
        "the footprint is a map-wide BFS from a random seed (not placeable), so a pawn cannot be put under the wall on demand; "
        "needs a debug seed or a bridge tool placing the seed", "floodDamageEnabled")
    _um("excavated_cells_survive", "dug_channel_filled_not_erased",
        "needs a FlowWorks-dug channel inside the footprint and an F-level read through a FlowWorks tool; no combined tier "
        "or seed control exists yet (CANYON_FLOOD_ERASES_CANALS_1 is the engine side)")
    _um("peakstorm_pulls_flood_forward", "peakstorm_light_pulls_next_flood",
        "a single 0.6 chance roll per cycle (PeakstormPullChance): statistical, needs a seeded RNG or a read of the roll",
        "peakstormBiasEnabled")
    _um("muttavaq_wakes_and_digs_in", "muttavaq_wakes_on_water_and_seals_dry",
        "needs a pan-sleeping muttavaq spawned on a flooded cell and the dry-down watched; no seed control to put water on its pan",
        "muttavaqWaterWakeEnabled")
    _um("recede_migrants", "flier_group_arrives_on_recede",
        "needs a biome roster with a flight-capable animal (map.Biome.AllWildAnimals); a plain biome has none: run on an "
        "RM_FloodedCanyon map", "recedeMigrantsEnabled")

    @suite.chain("settings_restored")
    def settings_restored(t):
        """LAST: every field is back at its shipped (parsed) default; a leaked arm would corrupt the next run."""
        with _comp(t, "all_settings_at_shipped_defaults", beyond_toggle=True):
            if _live(t):
                bad = [(f, _get(t, f), _sv(d)) for f, (ty, d) in SD.items() if not _same(_get(t, f), _sv(d))]
                if bad:
                    _fail("settings left off their shipped default by an earlier arm: %s" % bad)
else:
    suite = None


# --------------------------------------------------------------------------- static (offline)

def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    sd = settings_defaults()
    if len(sd) < 1:
        bad.append("sanity probe: no settings fields parsed from RM_FloodedCanyonMod.cs (regex broke)")
    mod = open(os.path.join(HERE, "Source", "RM_FloodedCanyonMod.cs"), encoding="utf-8").read()
    for f in sd:
        if '"%s"' % f not in mod:
            bad.append("settings field %s is not Scribed in ExposeData" % f)
        if len(re.findall(r"\b%s\b" % f, mod.split("DoWindowContents")[1])) < 1:
            bad.append("settings field %s has no control in DoWindowContents" % f)
    proj = open(os.path.join(HERE, "Source", "RM_FloodedCanyon.csproj"), encoding="utf-8").read()
    for cs in re.findall(r'Compile Include="([^"]+)"', proj):
        if not os.path.isfile(os.path.join(HERE, "Source", cs.replace("\\", "/"))):
            bad.append("csproj lists missing file " + cs)
    listed = {c.replace("\\", "/") for c in re.findall(r'Compile Include="([^"]+)"', proj)}
    for dp, _, files in os.walk(os.path.join(HERE, "Source")):
        for f in files:
            rel = os.path.relpath(os.path.join(dp, f), os.path.join(HERE, "Source")).replace("\\", "/")
            if f.endswith(".cs") and "/obj/" not in "/" + rel and rel not in listed:
                bad.append("%s is not in the csproj (EnableDefaultCompileItems false: compiles into nothing)" % rel)
    defs = shipped_defs()
    if len(defs) < 1:
        bad.append("no shipped defs parsed")
    names = {n for _, n in defs}
    defof = open(os.path.join(HERE, "Source", "RM_FloodedCanyonDefOf.cs"), encoding="utf-8").read()
    for n in re.findall(r"public static \w+ (RM_\w+);", defof):
        if n not in names:
            bad.append("DefOf field %s names no shipped def" % n)
    dbg = open(os.path.join(HERE, "Source", "Debug", "RM_FloodedCanyonDebugActions.cs"), encoding="utf-8").read()
    for p in (P_ARM, P_START, P_REPORT, P_RECEDE, P_AFTER, P_SEAMS):
        if p.split("\\")[1] not in dbg:
            bad.append("debug action label for path %r not in RM_FloodedCanyonDebugActions.cs" % p)
    if not any(f.endswith(".dll") for f in os.listdir(os.path.join(HERE, "Assemblies"))):
        bad.append("no DLL in Assemblies")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
