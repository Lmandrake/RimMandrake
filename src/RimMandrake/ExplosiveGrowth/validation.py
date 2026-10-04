"""validation.py -- modcheck suite for RimMandrake: Explosive Plant Growth
(mandrake.rm.explosivegrowth). Walk: design/validation_walks/RimMandrake/ExplosiveGrowth.md
(`## must be true`, every line ends in `-> chain.component` or `-> UNCOVERED: why`).

Never deployed (deploy_custom_mods.py excludes `.py`). Drive it on the `explosivegrowth_solo`
tier (engine alone + the bridge, all five DLCs):

    python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod ExplosiveGrowth \\
        --plan src/RimMandrake/ExplosiveGrowth/northstar_plan.py

Grounded in the mod's own source (`Source/`): `ExplosiveGrowthMod.cs` (25 settings fields, all
`public static` on `RimMandrake.ExplosiveGrowth.ExplosiveGrowthSettings`), the Harmony patches
in `RM_ExplosiveGrowthPatches.cs`, the registry (`RM_ExplosiveGrowthRegistry.cs`), the per-map
component (`RM_MapComponent_ExplosiveGrowth.cs`: soak grid, suppression grid, the charge clock,
the pass every 250 ticks) and `RM_TopResolver.cs` (the six tops).

THE OBSERVATION CHANNEL. The engine has no bridge `[Tool]`. Its only live read-out is the debug
menu (`Source/Debug/RM_ExplosiveGrowthDebugActions.cs`), driven through
`rimworld/execute_debug_action` with the paths MEASURED in `Transient/livesession_20261001/actions.json`:
`Actions\\T: Soak 5x5 here`, `Actions\\T: Suppress r2 here`, `Actions\\T: Fire top of plant here`
(all three read `UI.MouseCell()`; the call's x/z only place the virtual mouse), and
`Actions\\Charge all charging plants to 0.9`, `Actions\\Report state (current map)` (Direct).
Each prints one `[RMExplosiveGrowthDebug]` line. The line is read from THAT CALL'S OWN
`effects.logs` (skills/rimbridge/references/map-authoring.md: `jawa/drain_log contains=` returns a
STALE first message), never from `drain_log`. 🔴 RimWorld stops ALL logging after 10,000
messages (`Reached max messages limit`; Transient/bridge_debugaction_noop_report.md): an action
that ran but logged nothing is UNMEASURED here, never a pass and never a mod failure.

UNPROVEN SHAPES (first live run settles them; each degrades to UNMEASURED, never PASS):
the `effects.logs` row shape (str or {text|message}); the plant inspect line `Growth rate: N%`;
`jawa/pawn_get` carrying `hediffs`; `jawa/harmony_patches` `methods[].postfixes[].owner`.

SITE VS MOD. A plant that cannot grow right now (night, cold, no fertility) is wet but dormant and
correctly never charges (`StepCharge`, fixed 2026-09-26). Every chain that needs growth first reads
the control plant's own GrowthRate and records UNMEASURED (a SITE fault) when it is 0.

THE TOPS. Burst / Tinder / Slime / Rupture / Flush plants are roster rows naming Alpha Biomes (`AB_`),
`RG_` and Pyrelands (`RM_FE_`) plants that the solo tier does not load: those chains probe for the
donor def and record UNMEASURED ("donor not loaded") on it. They run for real on a list that carries
the donors (the owner's full list). Churn, the default top, is proven on the solo tier with vanilla Rice.

A FAIL turns the rest of a chain UNMEASURED, so every independent proof has its OWN chain, and
every settings arm restores the shipped default in a `finally` that bypasses the guard.
"""
import contextlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))    # so `python3 validation.py` finds modcheck

from modcheck import Suite, ExpectationFailed

suite = Suite("ExplosiveGrowth")

SETTINGS = "RimMandrake.ExplosiveGrowth.ExplosiveGrowthSettings"
TAG = "[RMExplosiveGrowthDebug]"
HARMONY_ID = "mandrake.rm.explosivegrowth"

# field -> shipped default (ExplosiveGrowthMod.cs). The suite restores exactly these.
DEFAULTS = [
    ("enabled", True), ("soakMultiplier", 10.0), ("defaultSoakHours", 24.0),
    ("minGrowDaysToSoak", 1.0), ("cavePlantsNeverSoak", True),
    ("irrigationSoakEnabled", True), ("gradientSurgeSoakEnabled", True), ("weatherSoakEnabled", True),
    ("chargeHours", 6.0), ("maxOvergrowthScale", 2.0), ("reprintIntervalTicks", 250),
    ("hueShiftEnabled", True), ("tellSoundsEnabled", True), ("groundTellEnabled", True),
    ("churnEnabled", True), ("burstEnabled", True), ("burstHurtsPawns", True), ("tinderEnabled", True),
    ("slimeEnabled", True), ("ruptureEnabled", True), ("ruptureMutationChance", 0.08),
    ("flushEnabled", True), ("harvestJackpotEnabled", True), ("lastSwingGambleEnabled", True),
    ("suppressionEnabled", True),
]
DEFAULT_OF = dict(DEFAULTS)
suite.toggles = [f for f, _ in DEFAULTS]

P_SOAK = "Actions\\T: Soak 5x5 here"
P_SUPPRESS = "Actions\\T: Suppress r2 here"
P_CHARGE = "Actions\\Charge all charging plants to 0.9"
P_REPORT = "Actions\\Report state (current map)"
P_FIRE = "Actions\\T: Fire top of plant here"

CHURN_PLANT = "Plant_Rice"        # vanilla, growDays 3, harvestedThingDef RawRice x6, Churn by default
CHURN_PRODUCE = "RawRice"
SOAKER = "Plant_Bush"             # vanilla, growDays 3: the soak-ratio subject
SOAK_DISK_MIN, SOAK_DISK_MAX = 25, 37    # RadialCellsAround(c, 2.9, true) is 29 cells; wide band on purpose
EXEMPT_PLANTS = ["Plant_TreeAnima", "Plant_Ambrosia", "Plant_MagmaCactus"]   # builtin exempt x2 + roster NONE row
CAVE_PLANT = "Agarilux"           # Core CavePlantBase fungus: cavePlantsNeverSoak
SOUND_DEFS = ["RM_EG_Creak", "RM_EG_Split", "RM_EG_Pop", "RM_EG_Rupture"]
PATCHED = [  # (method, kinds of patch that must carry our owner id)
    ("get_GrowthRate", ("postfixes",)), ("Print", ("prefixes", "finalizers")),
    ("get_Graphic", ("postfixes",)), ("YieldNow", ("postfixes",)), ("PlantCollected", ("prefixes",)),
]


# --------------------------------------------------------------------------- helpers

def _live(t):
    """True only against a real Session and an unfailed chain; False for the offline probe."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


class _Unmeasured(Exception):
    pass


def _unmeasured(t, why):
    """Stop this component and record it UNMEASURED with `why` (never a pass)."""
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True        # the grader's only route to an UNMEASURED verdict
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, **kw):
    """t.component() plus the `_unmeasured` fix-up: verdict stays UNMEASURED, detail names the
    reason, and the chain is not poisoned for an independent next component."""
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
        print("[eg] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _note(t, label, data):
    t._record(label, data)
    if t.session is not None:
        print("[eg-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]),
              file=sys.stderr, flush=True)


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


# ---- settings: arms restore the shipped default with the guard BYPASSED (a FAIL sets upstream_failed)

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
    """Set settings for the body; ALWAYS restore each to its shipped default."""
    try:
        for f, v in values.items():
            _put(t, f, v)
        yield
    finally:
        for f in values:
            try:
                _put(t, f, DEFAULT_OF[f])
            except Exception as e:      # never mask the body's own exception
                print("[eg] RESTORE FAILED %s: %s" % (f, e), file=sys.stderr, flush=True)


# ---- site

def _prep(t, size=40):
    """Everything true before the first assertion: cleared, open fertile soil, clear weather, noon."""
    t.clear_area(size=size)
    x, z = t.anchor
    h = size // 2
    rect = "%d,%d,%d,%d" % (x - h, z - h, size, size)
    t.bridge_call("jawa/set_terrain_batch", ops="Soil:%s" % rect)
    t.bridge_call("jawa/set_roof_batch", ops=rect, roofDef="None")
    t.bridge_call("jawa/set_fog", action="unfog", rect=rect)
    t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
    t.bridge_call("jawa/log_autoopen_suppress")
    _noon(t)


def _noon(t):
    """Time only moves forward: jump to the next midday so the light factor is not zero."""
    clk = t.bridge_call("jawa/time_clock")
    if not _live(t):
        return
    _ok(clk, "time_clock")
    hour = clk.get("hour")
    if hour is None or clk.get("ticksGame") is None:
        _unmeasured(t, "time_clock has no hour/ticksGame: %s" % str(clk)[:120])
    if not (9 <= hour < 14):
        t.bridge_call("jawa/time_set_ticks", ticks=int(clk["ticksGame"]) + int(((12 - hour) % 24) * 2500))


def _env_grows(t):
    """SITE precondition for every growth chain: the anchor must be in plant temperature."""
    x, z = t.anchor
    r = t.bridge_call("jawa/cell_temperature", cell="%d,%d" % (x, z))
    if not _live(t):
        return
    _ok(r, "cell_temperature")
    temp = r.get("temperature")
    if temp is None or not r.get("ok", True):
        _unmeasured(t, "cell_temperature unreadable at the anchor: %s" % str(r)[:140])
    if not (8.0 <= float(temp) <= 38.0):
        _unmeasured(t, "SITE: anchor is %.1f C -- plants are dormant outside ~8-38 C, so nothing can "
                       "charge here (a cold map is the 2026-09-26 false RED); use a temperate map" % float(temp))


# ---- debug-action channel

def _log_texts(r):
    eff = (r or {}).get("effects") or {}
    out = []
    for row in (eff.get("logs") or []):
        if isinstance(row, str):
            out.append(row)
        elif isinstance(row, dict):
            out.append(str(row.get("text") or row.get("message") or row.get("msg") or ""))
    return out


def _act(t, path, x=None, z=None):
    """Run a debug action and return its own `[RMExplosiveGrowthDebug]` log lines.
    success!=true is a FAIL; an action that logged nothing is UNMEASURED (the 10,000-message cap)."""
    if x is None:
        r = t.bridge_call("rimworld/execute_debug_action", path=path)
    else:
        r = t.bridge_call("rimworld/execute_debug_action", path=path, x=int(x), z=int(z))
    if not _live(t):
        return []
    if not isinstance(r, dict) or r.get("success") is not True:
        _fail("execute_debug_action %s did not succeed: %r" % (path, r))
    lines = [l for l in _log_texts(r) if TAG in l]
    if not lines:
        eff = r.get("effects") or {}
        _unmeasured(t, "debug action %s answered success but logged no %s line (effects.logCount=%s) -- "
                       "check Player.log for 'Reached max messages limit' before blaming the mod"
                       % (path, TAG, eff.get("logCount")))
    return lines


def _soak(t, x, z):
    """Soak around (x,z); returns the number of cells the engine says it soaked."""
    lines = _act(t, P_SOAK, x, z)
    if not _live(t):
        return 0
    m = re.search(r"soaked (\d+) cells around", lines[-1])
    if not m:
        _unmeasured(t, "soak log line unparseable: %r" % lines[-1][:200])
    return int(m.group(1))


def _report(t):
    """Parse the engine's Report line into {'head': {...}, 'tail': {...}}."""
    lines = _act(t, P_REPORT)
    if not _live(t):
        return {"head": {}, "tail": {}}
    line = [l for l in lines if "soaked=" in l]
    if not line:
        _unmeasured(t, "report line has no soaked= field: %r" % lines[-1][:200])
    head, _, tail = line[-1].partition("| soaked plants:")
    kv = re.compile(r"([A-Za-z/]+)(?:\([^)]*\))?=(\S+)")
    h, tl = dict(kv.findall(head)), dict(kv.findall(tail))
    need = ("soaked", "charging", "suppressed", "ruptures", "soaking", "none", "resolved")
    if any(k not in h for k in need) or any(k not in tl for k in ("immature", "charging", "topNone/exempt")):
        _unmeasured(t, "report line shape not understood: %r" % line[-1][:300])

    def num(v):
        try:
            return int(v)
        except ValueError:
            return v
    rep = {"head": dict((k, num(v)) for k, v in h.items()), "tail": dict((k, num(v)) for k, v in tl.items())}
    t._record("report", rep)
    return rep


# ---- reads

def _count(t, defName, rect=None):
    """Count of one def (comma list ok) over rect; a failed/truncated read raises, never reads as 0."""
    if rect:
        r = t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=1)
    else:
        r = t.bridge_call("jawa/list_things", defName=defName, limit=1)
    if not _live(t):
        return 0
    _ok(r, "list_things(%s)" % defName)
    if "countMatched" not in r or not r.get("scanned"):
        _fail("list_things(%s) unreadable (no countMatched / scanned 0): %r" % (defName, r))
    return r["countMatched"]


def _ids(t, defName, rect):
    r = t.bridge_call("jawa/list_things", defName=defName, rect=rect, limit=50)
    if not _live(t):
        return []
    _ok(r, "list_things(%s)" % defName)
    return [x.get("id") for x in (r.get("things") or []) if x.get("id")]


def _place(t, defName, x, z, growth=1.0):
    """Place ONE plant, read back, return its thing id. Unplaceable = SITE/donor, UNMEASURED."""
    r = t.bridge_call("jawa/set_plants", ops="%s:%d,%d,1,1" % (defName, x, z), growth=growth)
    if not _live(t):
        return None
    if not isinstance(r, dict) or r.get("success") is False:
        _unmeasured(t, "set_plants %s failed: %s" % (defName, str(r)[:160]))
    ids = _ids(t, defName, "%d,%d,1,1" % (x, z))
    if len(ids) != 1:
        _unmeasured(t, "%s did not place at %d,%d (set_plants said %s) -- terrain/fertility refuses it"
                       % (defName, x, z, str(r)[:160]))
    return ids[0]


def _donor(t, defName):
    """The donor plant must be loaded (get_defs success + found), else this chain cannot run here."""
    r = t.bridge_call("jawa/get_defs", defs="ThingDef/%s" % defName)
    if not _live(t):
        return
    if not isinstance(r, dict) or r.get("success") is not True:
        _unmeasured(t, "get_defs ThingDef/%s could not be asked: %s" % (defName, str(r)[:140]))
    if r.get("notFound"):
        _unmeasured(t, "donor plant %s is not loaded on this tier -- run on a list that carries it "
                       "(Alpha Biomes / RG_ / Pyrelands); this is NOT a mod fault" % defName)


def _rate(t, tid):
    """The plant's `Growth rate: N%` inspect line as a float percent."""
    r = t.bridge_call("jawa/inspect_string", thingIds=str(tid), limit=1)
    if not _live(t):
        return 0.0
    _ok(r, "inspect_string")
    rows = r.get("things") or r.get("rows") or []
    lines = []
    for row in rows:
        ins = row.get("inspect")
        lines.extend(ins if isinstance(ins, list) else [str(ins or "")])
    for ln in lines:
        m = re.search(r"growth rate\D{0,6}?(-?[\d.]+)\s*%", ln, re.I)
        if m:
            return float(m.group(1))
    _unmeasured(t, "no `Growth rate: N%` line in the plant's inspect string: %r" % (lines[:6],))


def _wait(t, n):
    """Advance n real ticks; long waits run Ultrafast and poll the real clock (53 ticks/s paused-step)."""
    if t.session is None or t.upstream_failed or n <= 3000:
        return t.wait_ticks(n)
    s = t.session
    start = s._ticks()
    target = start + n
    s.call("rimworld/set_time_speed", speed="Ultrafast")
    last, stall = start, time.time()
    try:
        while True:
            time.sleep(1.0)
            now = s._ticks()
            if now is None:
                raise ExpectationFailed("clock unreadable during a %d-tick wait" % n)
            if now >= target - 400:
                break
            if now > last:
                last, stall = now, time.time()
            elif time.time() - stall > 60:
                raise ExpectationFailed("clock stalled at %d during a %d-tick wait (a modal dialog?)" % (now, n))
    finally:
        s.call("rimworld/set_time_speed", speed="Paused")
    now = s._ticks()
    if now < target:
        t.wait_ticks(target - now)
    t._record("_wait(%d) Ultrafast" % n, (s._ticks() or 0) - start)


def _arm_charge(t, plant_def, x, z, growth=1.0):
    """Plant mature, soak it, wait two passes; returns (thing id, report). Dormancy is a SITE fault."""
    _env_grows(t)
    tid = _place(t, plant_def, x, z, growth)
    _soak(t, x, z)
    _wait(t, 700)
    rep = _report(t)
    if _live(t):
        if rep["tail"]["matureDormant"] and not rep["tail"]["charging"]:
            _unmeasured(t, "SITE: the soaked mature %s is dormant (GrowthRate 0: cold, dark, or no fertility) "
                           "-- correctly holds, cannot charge here" % plant_def)
    return tid, rep


# --------------------------------------------------------------------------- boot / static

@suite.chain("boot_defs")
def boot_defs(t):
    """Def-level facts that need no map: the engine started clean and every patch is attached."""
    with _comp(t, "startup_log_clean"):
        r = t.bridge_call("jawa/drain_log", contains="[RM ExplosiveGrowth]", limit=200)
        e = t.bridge_call("jawa/drain_log", contains="[RM ExplosiveGrowth]", limit=50, errorsOnly=True)
        if _live(t):
            _ok(r, "drain_log")
            msgs = [m.get("text", "") for m in (r.get("messages") or [])]
            if not msgs:
                _unmeasured(t, "no [RM ExplosiveGrowth] startup line in the log buffer (scrolled away or "
                               "the 10,000-message cap): cannot tell clean from absent")
            bad = [m for m in ((e or {}).get("messages") or [])]
            if bad:
                _fail("[RM ExplosiveGrowth] logged an error: %s" % str(bad[0])[:300])
            text = "\n".join(msgs)
            m = re.search(r"(\d+) plant defs soak", text)
            if not m or int(m.group(1)) <= 0:
                _fail("no `N plant defs soak` startup line, or N=0 (registry empty): %r" % text[:300])
            if "failed to build the plant table" in text:
                _fail("registry build failed at startup: %r" % text[:300])
            if "charge clock self-test PASS" not in text:
                _fail("the startup line `charge clock self-test PASS` is missing (FAIL line, or the deployed "
                      "DLL predates RM_ChargeSelfTest -- the 2026-09-27 deploy gap): %r" % text[:400])

    with _comp(t, "harmony_patches_attached"):
        for method, kinds in PATCHED:
            r = t.bridge_call("jawa/harmony_patches", typeName="Plant", methodName=method)
            if not _live(t):
                continue
            if not isinstance(r, dict) or r.get("success") is not True or r.get("harmonyError"):
                _unmeasured(t, "harmony_patches(Plant.%s) could not be asked: %s" % (method, str(r)[:160]))
            owners = []
            for m in (r.get("methods") or []):
                for k in kinds:
                    owners.extend(p.get("owner") for p in (m.get(k) or []))
            if HARMONY_ID not in owners:
                _fail("Plant.%s carries no %s of Harmony owner %s (owners seen: %s)"
                      % (method, "/".join(kinds), HARMONY_ID, sorted(set(o for o in owners if o))[:8]))

    with _comp(t, "sound_defs_resolve"):
        r = t.bridge_call("jawa/get_defs", defs=";".join("SoundDef/%s" % d for d in SOUND_DEFS))
        if _live(t):
            if not isinstance(r, dict) or r.get("success") is not True:
                _unmeasured(t, "get_defs SoundDef could not be asked: %s" % str(r)[:140])
            if r.get("notFound"):
                _fail("SoundDef(s) did not resolve: %r" % r.get("notFound"))
            if r.get("foundCount") != len(SOUND_DEFS):
                _fail("foundCount %r != %d" % (r.get("foundCount"), len(SOUND_DEFS)))


@suite.chain("registry_report")
def registry_report(t):
    """The registry classified plants and the roster resolved. Floors are CALIBRATING (vanilla+DLC
    ship dozens of plants); the point is that an empty/unready registry reads zero."""
    with _comp(t, "report_reads_registry"):
        _prep(t, 24)
        rep = _report(t)
        if _live(t):
            h = rep["head"]
            if h["soaking"] < 20:
                _fail("registry classifies only %d plant defs as soaking (expected dozens): %r" % (h["soaking"], h))
            if h["none"] < 3:
                _fail("registry has %d never-soak defs; the three builtin exempt plants alone make 3: %r" % (h["none"], h))
            if h["resolved"] < 1:
                _fail("no roster row resolved (the vanilla/DLC rows Plant_Reeds, Plant_MagmaCactus must): %r" % h)
            if h["biomeRefusesSoak"] != "False":
                _fail("the test map's biome refuses soak (carve-out): %r -- pick another biome" % h)


# --------------------------------------------------------------------------- the soak

@suite.chain("soak_footprint")
def soak_footprint(t):
    x, z = t.anchor
    with _comp(t, "soak_cells_registered"):
        _prep(t, 40)
        n = _soak(t, x, z)
        rep = _report(t)
        if _live(t):
            if not (SOAK_DISK_MIN <= n <= SOAK_DISK_MAX):
                _fail("soak action reports %d cells, expected ~29 (radius 2.9)" % n)
            if rep["head"]["soaked"] != n:
                _fail("Report says soaked=%r but the action soaked %d" % (rep["head"]["soaked"], n))


def _soak_ratio_chain(t, comp_name, setting, expect, prefix, **arm):
    """Growth-rate ratio on one soaked plant vs an unsoaked control, both read from the inspect pane."""
    x, z = t.anchor
    with _comp(t, comp_name, toggle=setting):
        _prep(t, 40)
        _env_grows(t)
        a = _place(t, SOAKER, x - 8, z, 0.5)
        b = _place(t, SOAKER, x + 8, z, 0.5)
        ra0, rb0 = _rate(t, a), _rate(t, b)
        if _live(t) and rb0 <= 0:
            _unmeasured(t, "SITE: the control bush's GrowthRate is 0 (night/cold/no fertility): %s" % rb0)
        with _arm(t, **arm):
            n = _soak(t, x - 8, z)
            ra1, rb1 = _rate(t, a), _rate(t, b)
        _note(t, prefix, {"rateA_before": ra0, "rateA_after": ra1, "ctrl_before": rb0, "ctrl_after": rb1, "cells": n})
        if _live(t):
            if abs(rb1 - rb0) > max(1.0, 0.02 * rb0):
                _fail("the UNSOAKED control's rate moved %s -> %s: the soak leaked or the site drifted" % (rb0, rb1))
            ratio = ra1 / ra0 if ra0 > 0 else 0.0
            if expect is None:
                if abs(ratio - 1.0) > 0.05:
                    _fail("soak was meant to be REFUSED (ratio 1.0) but the plant's rate went %s -> %s (x%.2f); "
                          "soaked %d cells" % (ra0, ra1, ratio, n))
            elif abs(ratio - expect) > 0.2 * expect:
                _fail("soaked growth rate x%.2f, expected x%s (rate %s -> %s)" % (ratio, expect, ra0, ra1))


@suite.chain("soak_x10_default")
def soak_x10_default(t):
    _soak_ratio_chain(t, "soak_multiplies_growth_x10", "soakMultiplier", 10.0, "soak_x10")


@suite.chain("soak_multiplier_tuned")
def soak_multiplier_tuned(t):
    _soak_ratio_chain(t, "soak_multiplier_follows_setting", "soakMultiplier", 3.0, "soak_x3", soakMultiplier=3.0)


@suite.chain("master_switch_off")
def master_switch_off(t):
    """enabled=false: the soak is refused (TrySoak) and the GrowthRate postfix is a no-op."""
    _soak_ratio_chain(t, "master_off_refuses_soak", "enabled", None, "master_off", enabled=False)


@suite.chain("soak_length")
def soak_length(t):
    """defaultSoakHours=2 -> 5000 ticks. Still soaked at ~2500, gone after 5000 (the pass prunes)."""
    x, z = t.anchor
    with _comp(t, "soak_expires_after_default_hours", toggle="defaultSoakHours"):
        _prep(t, 40)
        with _arm(t, defaultSoakHours=2.0):
            n = _soak(t, x, z)
            _wait(t, 2500)
            mid = _report(t)
            _wait(t, 2900)
            end = _report(t)
        if _live(t):
            if mid["head"]["soaked"] != n:
                _fail("soak expired early: %d cells at t=0, %r at ~2500 ticks of a 5000-tick soak" % (n, mid["head"]["soaked"]))
            if end["head"]["soaked"] != 0:
                _fail("soak did not expire: %r cells still soaked ~5400 ticks into a 5000-tick soak" % end["head"]["soaked"])


@suite.chain("soak_exempt_plants")
def soak_exempt_plants(t):
    """A soaked disk holding one soaker and the never-soak plants: the Report's `topNone/exempt`
    counts exactly the exempt ones that placed, and the control bush counts as `immature`."""
    x, z = t.anchor
    with _comp(t, "exempt_and_cave_plants_never_soak", toggle="cavePlantsNeverSoak"):
        _prep(t, 40)
        _env_grows(t)
        _place(t, SOAKER, x, z, 0.5)
        placed = 0
        for i, d in enumerate(EXEMPT_PLANTS + [CAVE_PLANT]):
            try:
                _place(t, d, x - 2 + (i % 4), z + 1 + (i // 4), 0.5)
                placed += 1
            except _Unmeasured:
                t.upstream_failed = False       # one plant refusing terrain must not hide the others
                t._why = None
        if _live(t) and placed < 2:
            _unmeasured(t, "only %d of %d never-soak plants could be placed" % (placed, len(EXEMPT_PLANTS) + 1))
        _soak(t, x, z)
        rep = _report(t)
        if _live(t):
            tl = rep["tail"]
            if tl["immature"] != 1:
                _fail("the control bush should read immature=1 (a soaked growing plant); got %r -- the Report "
                      "cannot see soaked plants, so the exempt count below means nothing" % tl)
            if tl["topNone/exempt"] != placed:
                _fail("topNone/exempt=%r but %d never-soak plants are in the soaked disk" % (tl["topNone/exempt"], placed))


# --------------------------------------------------------------------------- the charge and the churn top

def _churn_cycle(t, comp, produce_expected, **arm):
    """Soak a mature rice plant, arm, force 0.9, wait for the top. Returns observations."""
    x, z = t.anchor
    rect = "%d,%d,10,10" % (x - 5, z - 5)
    cell = "%d,%d,1,1" % (x, z)
    _prep(t, 40)
    with _arm(t, **arm):
        tid, rep = _arm_charge(t, CHURN_PLANT, x, z)
        if _live(t) and rep["tail"]["charging"] != 1:
            _fail("a mature soaked %s should be charging=1 after two passes; Report: %r" % (CHURN_PLANT, rep))
        sprouts_armed = _count(t, CHURN_PLANT, rect)
        _act(t, P_CHARGE)
        _wait(t, 2500)
        rep2 = _report(t)
        gone = _count(t, CHURN_PLANT, cell) == 0
        produce = _count(t, CHURN_PRODUCE, rect)
        sprouts = _count(t, CHURN_PLANT, rect)
    _note(t, comp, {"sprouts_when_armed": sprouts_armed, "original_gone": gone, "produce_things": produce,
                    "plants_after_top": sprouts, "report_after": rep2})
    return {"gone": gone, "produce": produce, "sprouts": sprouts, "sprouts_armed": sprouts_armed,
            "report": rep2, "armed": rep}


@suite.chain("churn_cycle")
def churn_cycle(t):
    """The whole default cycle at shipped settings: arm -> charge -> top. Churn: the plant splits,
    dies, drops its produce and sows a ring of sprouts."""
    with _comp(t, "mature_soaked_plant_charges_then_churns", toggle="churnEnabled"):
        o = _churn_cycle(t, "churn_cycle", True)
        if _live(t):
            if o["report"]["head"]["charging"] != 0:
                _fail("charge did not complete in 2500 ticks from 0.9 (0.1 of a 15000-tick clock is ~1500): %r" % o["report"])
            if not o["gone"]:
                _fail("the soaked, fully charged plant was not destroyed by its top (Churn)")
            if o["produce"] < 1:
                _fail("Churn dropped no %s (harvestedThingDef x6 x produceFactor 1)" % CHURN_PRODUCE)
            if o["sprouts"] < 2:
                _fail("Churn sowed %d plants near the stump; the ring is 2-4 sprouts" % o["sprouts"])


@suite.chain("ground_tell_on")
def ground_tell_on(t):
    """The ground tell fires when a charge ARMS: one sprout appears beside the plant (Churn)."""
    x, z = t.anchor
    rect = "%d,%d,10,10" % (x - 5, z - 5)
    with _comp(t, "ground_tell_sprouts_beside_arming_plant", toggle="groundTellEnabled"):
        _prep(t, 40)
        _arm_charge(t, CHURN_PLANT, x, z)
        n = _count(t, CHURN_PLANT, rect)
        if _live(t) and n < 2:
            _fail("no sprout appeared beside the charging plant (plants in rect: %d); the ground tell "
                  "sows one at arming" % n)


@suite.chain("ground_tell_off")
def ground_tell_off(t):
    x, z = t.anchor
    rect = "%d,%d,10,10" % (x - 5, z - 5)
    with _comp(t, "ground_tell_off_sows_nothing", toggle="groundTellEnabled"):
        _prep(t, 40)
        with _arm(t, groundTellEnabled=False):
            _, rep = _arm_charge(t, CHURN_PLANT, x, z)
            n = _count(t, CHURN_PLANT, rect)
        if _live(t):
            if rep["tail"]["charging"] != 1:
                _fail("with the tell off the plant must STILL charge (charging=1): %r" % rep)
            if n != 1:
                _fail("groundTellEnabled=false but %d plants stand near the charger (expected only itself)" % n)


@suite.chain("churn_off")
def churn_off(t):
    """churnEnabled=false: a fully charged plant just relaxes -- no top, no produce, it lives."""
    with _comp(t, "churn_off_plant_relaxes", toggle="churnEnabled"):
        o = _churn_cycle(t, "churn_off", False, churnEnabled=False)
        if _live(t):
            if o["gone"]:
                _fail("churnEnabled=false but the charged plant was destroyed")
            if o["produce"] != 0:
                _fail("churnEnabled=false but %d %s dropped" % (o["produce"], CHURN_PRODUCE))
            if o["report"]["head"]["charging"] != 0:
                _fail("the charge record should be dropped once the top resolves to nothing: %r" % o["report"])


@suite.chain("charge_hours")
def charge_hours(t):
    """chargeHours=1 -> a 2500-tick clock: the top fires on its own within ~3500 ticks of arming
    (the default 6 h clock needs ~15000). No ChargeAll shortcut."""
    x, z = t.anchor
    cell = "%d,%d,1,1" % (x, z)
    with _comp(t, "charge_hours_sets_the_clock", toggle="chargeHours"):
        _prep(t, 40)
        with _arm(t, chargeHours=1.0):
            _arm_charge(t, CHURN_PLANT, x, z)
            _wait(t, 3600)
            gone = _count(t, CHURN_PLANT, cell) == 0
        if _live(t) and not gone:
            _fail("chargeHours=1 but the plant is still standing ~4300 ticks after arming (clock ~2500)")


# --------------------------------------------------------------------------- suppression (the SURVIVE verb)

@suite.chain("suppression_on")
def suppression_on(t):
    """Suppress at the plant: the grid dries the cells, refuses new soak there, and a charging plant
    relaxes to zero -- alive, no top."""
    x, z = t.anchor
    rect = "%d,%d,10,10" % (x - 5, z - 5)
    with _comp(t, "suppression_dries_and_defuses", toggle="suppressionEnabled"):
        _prep(t, 40)
        _, rep0 = _arm_charge(t, CHURN_PLANT, x, z)
        if _live(t) and rep0["tail"]["charging"] != 1:
            _fail("precondition: the plant should be charging=1: %r" % rep0)
        _act(t, P_SUPPRESS, x, z)
        rep1 = _report(t)
        n_again = _soak(t, x, z)
        _wait(t, 1800)
        rep2 = _report(t)
        alive = _count(t, CHURN_PLANT, "%d,%d,1,1" % (x, z)) == 1
        produce = _count(t, CHURN_PRODUCE, rect)
        _note(t, "suppression", {"after_suppress": rep1, "resoak_cells": n_again, "after_relax": rep2})
        if _live(t):
            if rep1["head"]["suppressed"] < 13:
                _fail("Suppress r2 marked %r cells (disk r2.5 is 21)" % rep1["head"]["suppressed"])
            if rep1["head"]["soaked"] >= rep0["head"]["soaked"]:
                _fail("suppression did not dry any soaked cell (%r -> %r)" % (rep0["head"]["soaked"], rep1["head"]["soaked"]))
            if n_again >= 29 - rep1["head"]["suppressed"] + 1:
                _fail("a re-soak over suppressed ground still took %d cells; suppressed cells must refuse" % n_again)
            if rep2["head"]["charging"] != 0:
                _fail("the charge did not relax to zero within ~1800 ticks of drying: %r" % rep2)
            if not alive or produce:
                _fail("a relaxed plant must live and fire no top (alive=%s, produce=%d)" % (alive, produce))


@suite.chain("suppression_off")
def suppression_off(t):
    x, z = t.anchor
    with _comp(t, "suppression_off_is_inert", toggle="suppressionEnabled"):
        _prep(t, 40)
        with _arm(t, suppressionEnabled=False):
            n = _soak(t, x, z)
            _act(t, P_SUPPRESS, x, z)
            rep = _report(t)
        if _live(t):
            if rep["head"]["suppressed"] != 0:
                _fail("suppressionEnabled=false but %r cells were suppressed" % rep["head"]["suppressed"])
            if rep["head"]["soaked"] != n:
                _fail("suppressionEnabled=false but the soak changed (%d -> %r)" % (n, rep["head"]["soaked"]))


# --------------------------------------------------------------------------- the other tops (donor plants)

def _top_chain(t, comp_on, comp_off, donor, setting, observe, expect_on, expect_off, why):
    """Fire the donor plant's top directly (no charge needed). `observe(t, x, z)` returns a dict;
    `expect_on`/`expect_off` map a key to a predicate (True = must hold)."""
    x, z = t.anchor
    for name, arm, expect, tog in ((comp_on, {}, expect_on, None), (comp_off, {setting: False}, expect_off, setting)):
        with _comp(t, name, toggle=tog):
            _prep(t, 40)
            _donor(t, donor)
            _place(t, donor, x, z, 1.0)
            with _arm(t, **arm):
                _act(t, P_FIRE, x, z)
                obs = observe(t, x, z)
            _note(t, name, obs)
            if _live(t):
                for k, (pred, msg) in expect.items():
                    if not pred(obs[k]):
                        _fail("%s: %s -- observed %s=%r (%s)" % (name, msg, k, obs[k], why))


def _obs_common(t, x, z, defs):
    rect = "%d,%d,10,10" % (x - 5, z - 5)
    out = {"plant_at_cell": None}
    for d in defs:
        out[d] = _count(t, d, rect)
    return out


@suite.chain("top_burst")
def top_burst(t):
    def obs(t, x, z):
        o = _obs_common(t, x, z, ["Hay"])
        o["plant_at_cell"] = _count(t, "RG_Plant_AridGrass", "%d,%d,1,1" % (x, z))
        return o
    _top_chain(t, "burst_pops_leaves_chaff", "burst_off_falls_back_to_churn", "RG_Plant_AridGrass", "burstEnabled", obs,
               {"plant_at_cell": ((lambda v: v == 0), "the burst plant must be gone"),
                "Hay": ((lambda v: v >= 1), "a Burst leaves hay chaff")},
               {"Hay": ((lambda v: v == 0), "burstEnabled=false falls back to Churn: no hay")},
               "RM_TopResolver.Burst (3-6 hay) vs Fallback()")


@suite.chain("top_tinder")
def top_tinder(t):
    def obs(t, x, z):
        o = _obs_common(t, x, z, ["Hay"])
        o["plant_at_cell"] = _count(t, "RM_FE_Plant_Quickgrass", "%d,%d,1,1" % (x, z))
        return o
    _top_chain(t, "tinder_leaves_fuel", "tinder_off_falls_back_to_churn", "RM_FE_Plant_Quickgrass", "tinderEnabled", obs,
               {"plant_at_cell": ((lambda v: v == 0), "the tinder plant must be gone"),
                "Hay": ((lambda v: v >= 1), "a Tinder burst leaves hay (8-14)")},
               {"Hay": ((lambda v: v == 0), "tinderEnabled=false falls back to Churn: no hay")},
               "RM_TopResolver.Burst(tinder: true)")


@suite.chain("top_slime")
def top_slime(t):
    def obs(t, x, z):
        rect = "%d,%d,8,8" % (x - 4, z - 4)
        o = _obs_common(t, x, z, ["Filth_Slime"])
        tr = t.bridge_call("jawa/get_terrain_batch", rects=rect)
        o["slime_terrain_cells"] = (tr or {}).get("ops", "").count("RM_Slime_Rich") if _live(t) else 0
        o["plant_at_cell"] = _count(t, "AB_SlimyFern", "%d,%d,1,1" % (x, z))
        o["slime_anywhere"] = o["Filth_Slime"] + o["slime_terrain_cells"]
        return o
    _top_chain(t, "slime_turns_the_ground", "slime_off_falls_back_to_churn", "AB_SlimyFern", "slimeEnabled", obs,
               {"plant_at_cell": ((lambda v: v == 0), "the slime plant must be gone"),
                "slime_anywhere": ((lambda v: v >= 1), "a Slime top leaves RM_Slime_Rich ground (or Filth_Slime if the terrain is absent)")},
               {"slime_anywhere": ((lambda v: v == 0), "slimeEnabled=false falls back to Churn: no slime ground or filth")},
               "RM_TopResolver.Slime: RM_Slime_Rich ring, or Filth_Slime when the terrain is absent")


@suite.chain("top_rupture")
def top_rupture(t):
    def obs(t, x, z):
        o = _obs_common(t, x, z, ["Filth_Blood"])
        o["plant_at_cell"] = _count(t, "AB_AlienGrass", "%d,%d,1,1" % (x, z))
        o["ruptures"] = _report(t)["head"].get("ruptures")
        t.bridge_call("jawa/destroy_batch", rects="%d,%d,14,14" % (x - 7, z - 7), categories="Pawn")
        return o
    _top_chain(t, "rupture_opens_a_cloud_zone", "rupture_off_falls_back_to_churn", "AB_AlienGrass", "ruptureEnabled", obs,
               {"plant_at_cell": ((lambda v: v == 0), "the ruptured plant must be gone"),
                "Filth_Blood": ((lambda v: v >= 1), "a Rupture splashes blood filth (40% of 21 cells)"),
                "ruptures": ((lambda v: v == 1), "a Rupture registers one cloud zone")},
               {"ruptures": ((lambda v: v == 0), "ruptureEnabled=false falls back to Churn: no cloud zone"),
                "Filth_Blood": ((lambda v: v == 0), "ruptureEnabled=false falls back to Churn: no blood")},
               "RM_TopResolver.Rupture / AddRupture")


@suite.chain("top_flush")
def top_flush(t):
    def obs(t, x, z):
        return {"plant_at_cell": _count(t, "AB_KeeningCordax", "%d,%d,1,1" % (x, z))}
    _top_chain(t, "flush_plant_survives", "flush_off_falls_back_to_churn", "AB_KeeningCordax", "flushEnabled", obs,
               {"plant_at_cell": ((lambda v: v == 1), "a Flush top leaves the giant standing")},
               {"plant_at_cell": ((lambda v: v == 0), "flushEnabled=false falls back to Churn: the plant dies")},
               "RM_TopResolver.Flush")


@suite.chain("burst_hurts_pawns")
def burst_hurts_pawns(t):
    """A burst injures a pawn within 2.9 cells (a light blunt hit + a stun, never lethal); the setting off does not."""
    x, z = t.anchor
    for name, arm, hurt, tog in (("burst_bruises_nearby_pawn", {}, True, None),
                                 ("burst_hurt_off_spares_pawn", {"burstHurtsPawns": False}, False, "burstHurtsPawns")):
        with _comp(t, name, toggle=tog):
            _prep(t, 40)
            _donor(t, "RG_Plant_AridGrass")
            _place(t, "RG_Plant_AridGrass", x, z, 1.0)
            pid = t.spawn_pawn("Colonist", hostile=False)
            if _live(t) and not pid:
                _unmeasured(t, "could not spawn the colonist")
            t.bridge_call("jawa/set_draft", pawnId=pid, drafted=True)
            with _arm(t, **arm):
                _act(t, P_FIRE, x, z)
                r = t.bridge_call("jawa/pawn_get", pawn=pid)
            if _live(t):
                snap = (r or {}).get("pawn") or r or {}
                if not isinstance(snap, dict) or "hediffs" not in snap:
                    _unmeasured(t, "jawa/pawn_get has no hediffs list: %s" % str(r)[:160])
                n = len(snap["hediffs"])
                if hurt and n < 1:
                    _fail("a pawn on the burst plant's cell took no injury (hediffs=%d)" % n)
                if not hurt and n != 0:
                    _fail("burstHurtsPawns=false but the pawn carries %d hediff(s): %s" % (n, str(snap["hediffs"])[:200]))


# --------------------------------------------------------------------------- settings round trip

# Settings with no reachable live effect in this suite; each gets a write + read-back so a mistyped
# field name or a broken static still FAILS. (default, alternate) -- the alternate differs from the default.
FLIPS = [
    ("minGrowDaysToSoak", 1.0, 2.0),        # registry rebuild only on WriteSettings/startup: not live
    ("irrigationSoakEnabled", True, False),  # needs FlowWorks
    ("gradientSurgeSoakEnabled", True, False),  # needs EnvironmentalHazards' gradient axis
    ("weatherSoakEnabled", True, False),     # no soak weather is named at the RM tier
    ("maxOvergrowthScale", 2.0, 1.5),        # visual (Plant.Print scale)
    ("reprintIntervalTicks", 250, 500),      # visual cadence / perf
    ("hueShiftEnabled", True, False),        # visual (Plant.Graphic tint)
    ("tellSoundsEnabled", True, False),      # audio
    ("ruptureMutationChance", 0.08, 0.2),    # statistical, needs Contagion hediffs + a pawn in the cloud
    ("harvestJackpotEnabled", True, False),  # needs a harvesting pawn (YieldNow)
    ("lastSwingGambleEnabled", True, False),  # needs a cutting pawn, random (PlantCollected)
]


def _make_flip(field, default, alt):
    def chain(t):
        with _comp(t, "%s_setting_round_trips" % field, toggle=field):
            try:
                _put(t, field, alt)
                _put(t, field, default)
            finally:
                if t.session is not None:
                    try:
                        _put(t, field, default)
                    except Exception as e:
                        print("[eg] RESTORE FAILED %s: %s" % (field, e), file=sys.stderr, flush=True)
    chain.__doc__ = "Write + read-back of %s (no live effect reachable here; see FLIPS)." % field
    return chain


for _f, _d, _a in FLIPS:
    suite.chain("flip_%s" % _f)(_make_flip(_f, _d, _a))


# --------------------------------------------------------------------------- probes (EXPLOSIVE_GROWTH_PROBE_TOOL_1)
# State reads through RM_ExplosiveGrowthProof (jawa/static_call, this mod's own assembly): each stages its own plant or
# pawn near the map centre. An "ERROR" answer (no plantable cell, no Muffalo) is a SITE fault: UNMEASURED.

def _probe(t, method):
    r = t.bridge_call("jawa/static_call", type="RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthProof", method=method,
                      args="current")
    text = str((r or {}).get("result", "")) if isinstance(r, dict) else ""
    _note(t, method, text)
    if _live(t) and (not text or text.startswith("ERROR")):
        _unmeasured(t, "%s could not stage: %s" % (method, text[:160] or r))
    return dict(re.findall(r"(\w+(?:\.\d+)?)=([\w.\-/]+)", text)), text


@suite.chain("probe_jackpot_on")
def probe_jackpot_on(t):
    """Harvesting a swollen plant pays up to double at full charge: mean YieldNow at charge 1 vs uncharged."""
    with _comp(t, "harvest_jackpot_doubles_at_full_charge", toggle="harvestJackpotEnabled"):
        v, raw = _probe(t, "ProofJackpot")
        if _live(t):
            ratio = float(v.get("ratio", 0))
            if float(v.get("base", 0)) <= 0 or not 1.7 <= ratio <= 2.3:
                _fail("jackpot ratio %.2f, expected about 2 at full charge: %s" % (ratio, raw))


@suite.chain("probe_jackpot_off")
def probe_jackpot_off(t):
    with _comp(t, "jackpot_off_pays_plain", toggle="harvestJackpotEnabled"):
        with _arm(t, harvestJackpotEnabled=False):
            v, raw = _probe(t, "ProofJackpot")
        if _live(t) and not 0.85 <= float(v.get("ratio", 0)) <= 1.15:
            _fail("harvestJackpotEnabled=false but a charged plant still pays extra: %s" % raw)


@suite.chain("probe_gamble_on")
def probe_gamble_on(t):
    """Cutting a charging plant below the tremble defuses it; past the tremble the last swing is a 15-60% gamble."""
    with _comp(t, "cut_defuses_and_last_swing_is_a_gamble", toggle="lastSwingGambleEnabled"):
        v, raw = _probe(t, "ProofGamble")
        if _live(t):
            if v.get("cutBelowTrembleDefused") != "True" or v.get("plantCollected") != "True":
                _fail("a cut below the tremble did not defuse and collect: %s" % raw)
            c5, c7, c1 = (float(v.get(k, -1)) for k in ("chanceAt0.5", "chanceAt0.7", "chanceAt1"))
            if c5 != 0 or abs(c7 - 0.15) > 0.02 or abs(c1 - 0.6) > 0.02:
                _fail("gamble curve wrong (want 0 / 0.15 / 0.60): %s" % raw)


@suite.chain("probe_gamble_off")
def probe_gamble_off(t):
    with _comp(t, "gamble_off_never_fires", toggle="lastSwingGambleEnabled"):
        with _arm(t, lastSwingGambleEnabled=False):
            v, raw = _probe(t, "ProofGamble")
        if _live(t) and float(v.get("chanceAt1", -1)) != 0:
            _fail("lastSwingGambleEnabled=false but the top swing can still fire: %s" % raw)


@suite.chain("probe_rupture_on")
def probe_rupture_on(t):
    """Anyone in a rupture cloud without a vacuum seal can mutate: 200 pulses on a muffalo in the cloud."""
    with _comp(t, "rupture_cloud_mutates_the_unsealed"):
        v, raw = _probe(t, "ProofRupture")
        if _live(t):
            if int(v.get("pool", 0)) == 0:
                _unmeasured(t, "no rupture mutation hediff resolved on this list (the Contagion pool is empty): %s" % raw)
            if v.get("inZone") != "True" or int(v.get("mutations", 0)) < 1:
                _fail("a pawn in the cloud took no mutation in 200 pulses: %s" % raw)


@suite.chain("probe_rupture_off")
def probe_rupture_off(t):
    with _comp(t, "rupture_chance_zero_mutates_nobody"):
        with _arm(t, ruptureMutationChance=0.0):
            v, raw = _probe(t, "ProofRupture")
        if _live(t) and int(v.get("mutations", -1)) != 0:
            _fail("ruptureMutationChance=0 but the cloud still mutated: %s" % raw)


@suite.chain("probe_tell_ladder")
def probe_tell_ladder(t):
    """The tell ladder in order (Ground, Swell, Hue, Tremble, Creak, Silence), the swell growing toward
    maxOvergrowthScale and the hue going fully wrong at the top."""
    with _comp(t, "tell_ladder_stages_swell_and_hue"):
        v, raw = _probe(t, "ProofTell")
        if _live(t):
            want = ["Ground", "Swell", "Hue", "Tremble", "Creak", "Silence"]
            got = [v.get(k, "?/?/?").split("/")[0] for k in ("c0.10", "c0.20", "c0.50", "c0.75", "c0.90", "c0.97")]
            if got != want:
                _fail("tell stages %s, expected %s: %s" % (got, want, raw))
            top = v.get("c0.97", "?/0/0").split("/")
            if not (1.9 <= float(top[1]) <= 2.0 and float(top[2]) == 1.0):
                _fail("at charge 0.97 the plant should be ~1.96x and fully hued: %s" % raw)


@suite.chain("probe_tell_scale_off")
def probe_tell_scale_off(t):
    with _comp(t, "max_scale_one_never_swells"):
        with _arm(t, maxOvergrowthScale=1.0):
            v, raw = _probe(t, "ProofTell")
        if _live(t) and abs(float(v.get("c0.97", "?/0/0").split("/")[1]) - 1.0) > 0.001:
            _fail("maxOvergrowthScale=1 but the silent plant is still drawn swollen: %s" % raw)


@suite.chain("settings_restored")
def settings_restored(t):
    """LAST: every field is back at its shipped default (a leaked arm would corrupt the next run)."""
    with _comp(t, "all_settings_at_shipped_defaults"):
        if _live(t):
            bad = []
            for f, d in DEFAULTS:
                if not _same(_get(t, f), _sv(d)):
                    bad.append((f, _get(t, f), _sv(d)))
            if bad:
                _fail("settings left off their shipped default by an earlier arm: %s" % bad)


# --------------------------------------------------------------------------- defs_resolve (first-script contract chain 1)

def shipped_defs():
    """(defType, defName) for every top-level def the mod's own Defs/ XML ships (parsed, never listed by hand)."""
    out = []
    for dp, _, files in os.walk(os.path.join(HERE, "Defs")):
        for f in sorted(files):
            if f.endswith(".xml"):
                for e in ET.parse(os.path.join(dp, f)).getroot():
                    n = e.findtext("defName")
                    if n and not e.get("Abstract"):
                        out.append((e.tag.split(".")[-1], n))
    return out


@suite.chain("defs_resolve")
def defs_resolve(t):
    """Every def the mod ships resolves in the running game; a control proves the probe can say absent.
    The roster def's DefType name is UNPROVEN against get_defs: a failed ask is UNMEASURED, not FAIL."""
    with _comp(t, "shipped_defs_resolve"):
        want = shipped_defs()
        sounds = ["%s/%s" % x for x in want if x[0] == "SoundDef"]
        others = ["%s/%s" % x for x in want if x[0] != "SoundDef"]
        r = t.bridge_call("jawa/get_defs", defs=";".join(sounds))
        if _live(t):
            if not isinstance(r, dict) or r.get("success") is not True:
                _unmeasured(t, "get_defs could not be asked: %s" % str(r)[:140])
            if r.get("notFound") or r.get("foundCount") != len(sounds):
                _fail("shipped SoundDefs did not resolve: notFound=%r foundCount=%r of %d" % (r.get("notFound"), r.get("foundCount"), len(sounds)))
        for d in others:
            r = t.bridge_call("jawa/get_defs", defs=d)
            if _live(t):
                if not isinstance(r, dict) or r.get("success") is not True:
                    _unmeasured(t, "get_defs %s could not be asked (DefType name unproven?): %s" % (d, str(r)[:140]))
                if r.get("notFound") or r.get("foundCount") != 1:
                    _fail("roster def did not load (a def with an unresolvable field is discarded silently): %s -> %r" % (d, r))
    with _comp(t, "control_absent_def_reads_absent"):
        r = t.bridge_call("jawa/get_defs", defs="SoundDef/RM_EG_NoSuchSoundForTheControl")
        if _live(t):
            if not isinstance(r, dict) or r.get("success") is not True:
                _unmeasured(t, "control ask failed: %s" % str(r)[:140])
            if r.get("foundCount") != 0 or not r.get("notFound"):
                _fail("the probe cannot say absent: control returned %r" % r)


# --------------------------------------------------------------------------- static (offline)

def static_checks():
    """Offline, no game. Returns failure strings; empty = pass."""
    bad = []
    src = open(os.path.join(HERE, "Source", "ExplosiveGrowthMod.cs"), encoding="utf-8").read()
    fields = re.findall(r"public static (?:bool|float|int) (\w+)\s*=", src.split("class ExplosiveGrowthSettings")[1].split("ExposeData")[0]) \
        if "class ExplosiveGrowthSettings" in src else []
    if len(fields) < 1:
        bad.append("sanity probe: found no settings fields in ExplosiveGrowthMod.cs (regex broke)")
    for f in fields:
        if f not in DEFAULT_OF:
            bad.append("settings field %s is not in DEFAULTS (round-trip would skip it)" % f)
    for f in DEFAULT_OF:
        if f not in fields:
            bad.append("DEFAULTS names %s but the settings class has no such field" % f)
        if '"%s"' % f not in src:
            bad.append("settings field %s is not Scribed" % f)
    proj = open(os.path.join(HERE, "Source", "RM_ExplosiveGrowth.csproj"), encoding="utf-8").read() \
        if os.path.isfile(os.path.join(HERE, "Source", "RM_ExplosiveGrowth.csproj")) else ""
    if proj:
        for cs in re.findall(r'Compile Include="([^"]+)"', proj):
            if not os.path.isfile(os.path.join(HERE, "Source", cs.replace("\\", "/"))):
                bad.append("csproj lists missing file " + cs)
    defs = shipped_defs()
    snd = {n for k, n in defs if k == "SoundDef"}
    for s_ in SOUND_DEFS:
        if s_ not in snd:
            bad.append("SOUND_DEFS names %s but no shipped SoundDef" % s_)
    if not any(k.endswith("RosterDef") for k, _ in defs):
        bad.append("no roster def shipped")
    if not os.path.isfile(os.path.join(HERE, "Assemblies", "RimMandrake.ExplosiveGrowth.dll")) and not any(
            f.endswith(".dll") for f in os.listdir(os.path.join(HERE, "Assemblies"))):
        bad.append("no DLL in Assemblies")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p_ in problems:
        print("  - " + p_)
    sys.exit(1 if problems else 0)
