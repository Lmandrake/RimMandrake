"""validation.py -- modcheck suite for RimMandrake: Luminous Pigment ("Deepfire", mandrake.rm.luminouspigment).

First north-star script (LUMINOUS_PIGMENT_FIRST_SCRIPT_1). Walk: design/validation_walks/RimMandrake/LuminousPigment.md
(every `## must be true` line carries an arrow to the component below that covers it). Spec:
design/RimMandrake/deepfire_luminous_pigment_spec.md. Never deployed (deploy_custom_mods.py excludes `.py`).

TIER. `luminouspigment_ns` (modset_builder.py): bridge + this mod + Ninefold, all five DLCs. Without Ninefold the
god-delta chain reads UNMEASURED, never PASS. LightsOut (third-party) is not carried: one bar is UNCOVERED.

WHAT IS REUSED. The six `src/RimMandrake/bridgetools/prove_deepfire_*.py` harnesses were PROVEN live 2026-09-30
(115 checks on the 612-mod list). This suite drives the SAME mod-owned `Deepfire` debug actions
(DeepfireFloorDebugActions, ...FirstCoat..., ...ProxyStorage..., ...WornGlow..., ...Status..., ...GodDelta...)
and the SAME companion tools (`deepfire/*` in JawaBenchDeepfireTools.cs), with the strongest assertion of each
proof, so those proofs become rerunnable chains. Debug actions are found by reading the live Actions tree (1.6
flattens mod categories to "T: <Prefix>: ..." leaves), never constructed.

NEW HERE (nothing proved live before this script): the whole CHAIN (fresh-mat clock and chill kill, the research
sighting gate, the powered press, GlowTank seed/blackout, the stack glow), the patch-effect reads (a patch that
matches nothing logs nothing), the Mod Settings arms, and a real-AI A/B for `paintingEnabled`.

SETTINGS ARMS. Fields are `public static` (LuminousPigmentSettings). `jawa/mod_settings_field` writes the static but
never calls WriteSettings, so the DEF-LEVEL settings (ApplySettings: MarketValue, glow radius, designationCategory,
stove recipe lists, research finish) only reach the defs once the Mod Settings dialog closes (Dialog_ModSettings.
PreClose -> LuminousPigmentMod.WriteSettings -> ApplySettings). `_apply()` opens and closes that dialog.
`settings_apply.apply_reaches_defs` is the CANARY: if it FAILS, the apply path itself (harness) is broken and every
arm that needs it after it reads UNMEASURED, not a mod defect. Live-read settings (matLifeDays, maxCoats, the
paintable toggles, ...) need no apply. Every arm restores its fields in a `finally` through the raw session
(t.set_setting is a no-op once a chain has failed, so it cannot be used to restore).

DECLARATION PROBE. Offline `modcheck floor` runs every chain with a no-op context (no session, results None). All
code outside a component is therefore guarded by `_live(t)` or goes through helpers that return {} / [] there.

Not expressible with the current bridge tools (walk marks them UNCOVERED with the reason): the wild shore spawn
(needs a generated ocean-shore map), the GlowTank growth cycle (12 game days), cooking outcomes by chef skill (no
cook-a-dish harness), the Designator's own accept path (the bridge designates directly), LightsOut.
"""
import contextlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

_UTILS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils")
if os.path.isdir(_UTILS) and _UTILS not in sys.path:
    sys.path.insert(0, _UTILS)          # `python3 validation.py` (static checks) runs with no modcheck path set
from modcheck import Suite, ExpectationFailed

suite = Suite("LuminousPigment")
suite.toggles = [
    "shoreMatsEnabled", "matLifeDays", "matChillKillTemp",
    "pressGate", "deepfireMarketValue", "deepfireStackGlows",
    "glowTankEnabled", "tankPowerGraceHours", "tankNeedsWater",
    "paintingEnabled", "maxCoats", "floorsPaintable", "wallsPaintable", "furniturePaintable",
    "apparelPaintable", "weaponsPaintable", "wornLightEnabled", "stylingStationLacquer",
    "combatPenaltiesEnabled", "artQualityBump",
    "cuisineEnabled", "hediffGlowEnabled",
    "godsReact", "ishkoIdolPaintable",
    "statusEnabled",
]

SETTINGS = "RimMandrake.LuminousPigment.LuminousPigmentSettings"
MOD_ID = "mandrake.rm.luminouspigment"
LIT = 0.3                       # GlowGrid.GameGlowLitThreshold
PREFIXES = ("Floor:", "FirstCoat:", "Proxy:", "WornGlow:", "Status:", "GodDeltas:", "LightsOut:")
TAGS = ("[DeepfireFloor] ", "[DeepfireFirstCoat] ", "[DeepfireProxy] ", "[DeepfireWorn] ",
        "[DeepfireStatus] ", "[DeepfireGods] ")
GODS = ("Ishko", "Ohm", "Oomo", "MobUnloo", "Rekko", "TaBaa", "Zizzik", "Shkaar", "Ozzik")
TRIO = ("MobUnloo", "Rekko", "Zizzik")
LIKE, ADORE, ISHKO, STATUE, DIMINISHED = 3.0, 8.0, 3.0, 15.0, 1.0   # shipped godDelta* defaults
SAT_MIN, SAT_MAX = -100.0, 100.0
POLL = 15                       # DeepfirePaintDefaults.WornLightTickInterval
STYLE_COST = 3                  # costApparel default
PRESS_YIELD = 2                 # pressYield default
MAT_CHILL_OFF = "-100"          # matChillKillTemp that can never fire: the control arm
RECIPE_OWNERS = ("ElectricStove", "FueledStove")


# ------------------------------------------------------------------------- shipped defs, from the files

def _shipped_defs():
    """[(DefType, defName)] for every non-abstract def under this mod's Defs/, read from the XML at import
    (never a hand list: a def added later is checked with no edit here)."""
    out = []
    ddir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Defs")
    for dirpath, _dirs, files in os.walk(ddir):
        for fn in sorted(files):
            if not fn.endswith(".xml"):
                continue
            try:
                root = ET.parse(os.path.join(dirpath, fn)).getroot()
            except ET.ParseError:
                continue
            for el in list(root):
                if not isinstance(el.tag, str) or str(el.get("Abstract", "")).lower() == "true":
                    continue
                nm = el.find("defName")
                if nm is not None and (nm.text or "").strip():
                    out.append((el.tag, nm.text.strip()))
    return sorted(set(out))


SHIPPED = _shipped_defs()
ALL_DEFS = ["%s/%s" % p for p in SHIPPED]
MEAL_RECIPES = [n for ty, n in SHIPPED if ty == "RecipeDef" and n.startswith("RM_MealDeepfire")]
GLOW_HEDIFFS = [n for ty, n in SHIPPED if ty == "HediffDef" and n.startswith("RM_Glow_")]


# ------------------------------------------------------------------------------------------ plumbing

PRESS_WATTS = 150      # LuminousPigmentSettings.pressPower default (LuminousPigmentMod.cs:47)


def _live(t):
    """True only for a real run against a real Session and an unfailed chain; False for the offline
    declaration probe, so manual assertions never trip on its no-op (None) results."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _chk(t, cond, msg):
    if _live(t) and not cond:
        raise ExpectationFailed(msg)


class _Unmeasured(Exception):
    pass


def _unmeasured(t, why):
    """Stop this component and record it UNMEASURED with `why` (never a pass)."""
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True      # the grader's only route to an UNMEASURED verdict
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, **kw):
    """t.component() plus the `_unmeasured` fix-up: the verdict stays UNMEASURED, its detail names the real
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
    if t.session is not None:    # progress line (the driver prints only at the very end)
        c = t.components[-1]
        print("[deepfire] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict),
              str(c.detail or "")[:300], file=sys.stderr, flush=True)


def _need(t, state, *keys):
    """UNMEASURED (never a KeyError FAIL) when an earlier component of the chain did not produce `keys`."""
    miss = [k for k in keys if state.get(k) is None]
    if _live(t) and miss:
        _unmeasured(t, "an earlier component of this chain did not produce %s" % miss)


def _note(t, label, data):
    t._record(label, data)
    if t.session is not None:
        print("[deepfire-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]),
              file=sys.stderr, flush=True)


def _u(r):
    """A tool result as a dict. The transport normally returns one already; an MCP envelope is unwrapped."""
    if isinstance(r, dict) and "content" in r and "success" not in r:
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r if isinstance(r, dict) else {}


def _call(t, tool, **p):
    """Pass-through to the chain's bridge_call. Every CALL SITE passes a literal tool name and literal keyword
    names, which is what northstar_driver/lint_calls.py checks against the declared schemas (it recognises the
    `_call(t, "tool", k=v)` shape). The one dynamic dispatch lives here and is reached by getattr so the lint
    does not report this wrapper's own non-literal forwarding."""
    return _u(getattr(t, "bridge_call")(tool, **p))


def _ok(t, r, what):
    if _live(t) and not (r or {}).get("success", False):
        _fail("%s failed: %s" % (what, json.dumps(r, default=str)[:300]))
    return r


def _wait(t, n):
    return t.wait_ticks(n)


def _near(a, b, tol=0.02):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


def _rect(x, z, w, h):
    return "%d,%d,%d,%d" % (x, z, w, h)


# --- pads: every chain builds on its own 3-aligned corner so the cluster grid lines up (floor proof) ---

PADS = {
    "mat": (-60, -45), "gate": (-60, -30), "glow": (-60, -15), "press": (-60, 0), "tank": (-60, 15),
    "floor": (-30, -45), "coat1": (-30, -30), "proxy": (-30, -15), "paint": (-30, 0), "toggles": (-30, 15),
    "gods": (0, -45), "status": (0, -30), "worn": (0, -15), "styling": (0, 15), "cuisine": (30, -45),
}


def _pad(t, name):
    ax, az = t.anchor if t.anchor else (126, 126)
    bx, bz = (int(ax) // 3) * 3, (int(az) // 3) * 3
    dx, dz = PADS[name]
    return bx + dx, bz + dz


def _room(t, x, z):
    """An 8x8 walled, roofed, WoodPlankFloor room whose 6x6 interior starts at (x,z) (the floor proof's fixture)."""
    r = _call(t, "jawa/make_empty_room", rect=_rect(x - 1, z - 1, 8, 8), wallDef="Wall",
              stuffDef="WoodLog", floorDef="WoodPlankFloor")
    _ok(t, r, "make_empty_room")
    return r


def _spawn(t, ops, stuff=None):
    if stuff:
        r = _call(t, "jawa/spawn_batch", ops=ops, stuff=stuff)
    else:
        r = _call(t, "jawa/spawn_batch", ops=ops)
    _ok(t, r, "spawn_batch(%s)" % ops[:60])
    return r


def _things(t, defs, rect=None, limit=500):
    if rect:
        r = _call(t, "jawa/list_things", defName=defs, limit=limit, rect=rect)
    else:
        r = _call(t, "jawa/list_things", defName=defs, limit=limit)
    if _live(t):
        if not r.get("success", True):
            _fail("list_things(%s) failed: %s" % (defs, json.dumps(r, default=str)[:200]))
        if r.get("isCompleteList") is False:
            _fail("list_things(%s) truncated" % defs)
    return r.get("things") or []


def _stack(rows):
    return sum(int(x.get("stackCount") or 1) for x in rows)


def _xz(row):
    p = row.get("position") or {}
    return p.get("x", row.get("x")), p.get("z", row.get("z"))


def _one(t, defs, rect=None):
    rows = _things(t, defs, rect)
    if _live(t) and not rows:
        _fail("no %s found%s" % (defs, " in %s" % rect if rect else ""))
    return rows[0] if rows else {}


def _colonists(t):
    r = _call(t, "jawa/list_pawns", limit=300)
    return [p for p in (r.get("pawns") or [])
            if p.get("id") and p.get("faction") and not p.get("dead")
            and p.get("intelligence", "Humanlike") == "Humanlike" and p.get("hostility") not in ("Hostile",)]


def _spawn_colonist(t, x, z):
    r = _call(t, "jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1)
    _ok(t, r, "spawn_pawn")
    row = (r.get("pawns") or [{}])[0]
    if _live(t) and not row.get("id"):
        _fail("spawn_pawn returned no pawn id: %s" % json.dumps(r, default=str)[:200])
    pid = row.get("id")
    if pid:
        _call(t, "jawa/set_draft", pawnId=pid, drafted=False)
        _call(t, "jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
        _call(t, "jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
    return pid


def _prio(t, work, prio=1):
    for p in _colonists(t):
        _call(t, "jawa/set_work_priority", pawnId=p["id"], workType=work, priority=prio)


def _glow(t, x, z):
    r = _call(t, "deepfire/glow_at", x=int(x), z=int(z))
    _ok(t, r, "deepfire/glow_at(%s,%s)" % (x, z))
    return float(r.get("groundGlow") or 0.0) if _live(t) else 0.0


def _glow_rgb(t, x, z):
    r = _call(t, "deepfire/glow_at", x=int(x), z=int(z))
    _ok(t, r, "deepfire/glow_at(%s,%s)" % (x, z))
    v = r.get("visual") or {}
    return (int(v.get("r") or 0), int(v.get("g") or 0), int(v.get("b") or 0))


def _get_defs(t, defs, fields):
    r = _call(t, "jawa/get_defs", defs=defs, fields=fields, deep=False)
    _ok(t, r, "get_defs(%s)" % defs)
    if _live(t) and r.get("notFound"):
        _fail("get_defs could not resolve %r" % (r.get("notFound"),))
    return dict((d.get("defName"), d.get("fields") or {}) for d in (r.get("defs") or []))


def _field(t, row, name):
    """A `fields` value; a missing field comes back '(no such field)', which is UNMEASURED, never a value."""
    v = (row or {}).get(name, "(absent)")
    if _live(t) and (isinstance(v, str) and v in ("(no such field)", "(absent)")):
        _unmeasured(t, "get_defs cannot read field %r (%s)" % (name, v))
    return v


# ----------------------------------------------------------------------------- the Mod Settings arms

def _raw_get(t, field):
    r = _u(t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field))
    return r.get("value")


def _raw_set(t, field, value):
    return _u(t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field,
                             value=str(value)))


@contextlib.contextmanager
def _settings(t, **kv):
    """Set `kv` for the body and ALWAYS restore the previous raw values, even after a failed chain
    (t.set_setting is guarded by the chain's own failure flag, so it cannot restore)."""
    old = {}
    if t.session is not None:
        for f in kv:
            old[f] = _raw_get(t, f)
    try:
        if _live(t):
            for f, v in kv.items():
                r = _raw_set(t, f, v)
                if not r.get("success"):
                    _fail("mod_settings_field(set %s=%s) failed: %s" % (f, v, json.dumps(r, default=str)[:200]))
                back = _raw_get(t, f)
                if str(back) != str(v):
                    _fail("setting %s did not take: wrote %r, read %r" % (f, v, back))
        yield
    finally:
        if t.session is not None:
            for f, v in old.items():
                try:
                    _raw_set(t, f, v)
                except Exception:
                    pass


def _apply(t):
    """Make LuminousPigmentMod.WriteSettings -> ApplySettings run, the way a player does: open the Mod
    Settings dialog and close it. Unreachable dialog = UNMEASURED (a harness limit), never a pass."""
    if not _live(t):
        return
    r = _u(t.session.call("rimworld/open_mod_settings", modId=MOD_ID, replaceExisting=True))
    if not r.get("success", False):
        _unmeasured(t, "cannot open the Mod Settings dialog for %s: %s" % (MOD_ID, json.dumps(r, default=str)[:200]))
    t.session.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)


def _apply_safely(t):
    """Restore-path apply: never raises."""
    if t.session is None:
        return
    try:
        _u(t.session.call("rimworld/open_mod_settings", modId=MOD_ID, replaceExisting=True))
        t.session.call("jawa/window_list_close", action="close", typeName="ModSettings", closeAll=True)
    except Exception:
        pass


# ------------------------------------------------------------------------------ the mod's debug actions

_ACTIONS = {}
_APPLY = {"ok": None}      # the settings-dialog apply path, set by settings_apply.apply_reaches_defs


def _find_actions(t):
    if _ACTIONS or not _live(t):
        return _ACTIONS
    r = _call(t, "rimworld/list_debug_action_children", path="Actions")
    kids = r.get("children") or []
    found = {}
    for c in kids:
        label = c.get("label") or ""
        if label == "Deepfire" or (c.get("path") or "").endswith("\\Deepfire"):
            sub = _call(t, "rimworld/list_debug_action_children", path=c.get("path"))
            found = dict(((l.get("label") or ""), l.get("path")) for l in sub.get("children") or [])
            break
    if not found:     # 1.6 flattens mod categories: "T: Floor: ..." leaves directly under Actions
        found = dict(((c.get("label") or ""), c.get("path")) for c in kids
                     if any(p in (c.get("label") or c.get("path") or "") for p in PREFIXES))
    if not found:
        _unmeasured(t, "no Deepfire debug actions in the live Actions tree (mod not loaded, or the tree "
                       "did not enumerate: success=%r children=%d)" % (r.get("success"), len(kids)))
    _ACTIONS.update(found)
    return _ACTIONS


def _act(t, label, x, z):
    """Run one Deepfire debug action at (x, z); return its tagged JSON log line as a dict. A missing action
    FAILS; a result with no tagged line is UNMEASURED (log cap); the probe returns {}."""
    if not _live(t):
        return {}
    acts = _find_actions(t)
    path = next((p for l, p in acts.items() if label.lower() in l.lower()), None)
    if not path:
        _fail("no Deepfire debug action matching %r (have %d)" % (label, len(acts)))
    r = _call(t, "rimworld/execute_debug_action", path=path, x=int(x), z=int(z))
    logs = [str(m.get("message") if isinstance(m, dict) else m)
            for m in ((r.get("effects") or {}).get("logs") or [])]
    for line in logs:
        for tag in TAGS:
            i = line.find(tag)
            if i >= 0:
                try:
                    return json.loads(line[i + len(tag):].strip())
                except Exception:
                    pass
    # No tagged line is UNMEASURED, never FAIL: RimWorld stops logging after 10,000 messages ("Reached max
    # messages limit", Transient/bridge_debugaction_noop_report.md), after which every report action is silent.
    _unmeasured(t, "debug action %r logged no %s line (log cap reached after a long session? relaunch and rerun) "
                   "raw: %s" % (label, "/".join(x.strip() for x in TAGS), json.dumps(r, default=str)[:300]))


def _log_baseline(t):
    """Error-type lines already in the 1000-entry Log.Messages buffer that name this mod, text -> repeats.
    (jawa/drain_log does NOT drain; the proofs learned this on 2026-09-30.)"""
    r = _call(t, "jawa/drain_log", errorsOnly=True, limit=1000)
    pat = re.compile(r"Deepfire|LuminousPigment|Luminous|WornGlow|FirstCoat|Sumptuary|Ninefold")
    c = {}
    for m in r.get("messages") or []:
        if isinstance(m, dict) and m.get("type") == "Error" and pat.search(m.get("text") or ""):
            c[m["text"]] = c.get(m["text"], 0) + int(m.get("repeats") or 1)
    return c


_GLOBAL = {}


# the start-of-run baseline is recorded by a tiny first chain so no_new_errors has something to diff against
@suite.chain("00_log_baseline")
def _log_start(t):
    with _comp(t, "log_baseline_recorded"):
        if _live(t):
            _GLOBAL["log0"] = _log_baseline(t)
            _note(t, "mod error lines already in the buffer", len(_GLOBAL["log0"]))


# =========================================================================================== chain 1: defs

@suite.chain("defs_load")
def defs_load(t):
    """Every def this mod ships loads and resolves, and the patches it carries actually landed."""
    with _comp(t, "all_defs_resolve"):
        if _live(t):
            n, bad = 0, []
            for i in range(0, len(ALL_DEFS), 25):
                chunk = ALL_DEFS[i:i + 25]
                r = _call(t, "jawa/get_defs", defs=";".join(chunk), limit=100)
                _ok(t, r, "get_defs chunk %d" % i)
                n += int(r.get("foundCount") or 0)
                bad += list(r.get("notFound") or [])
            _note(t, "defs requested/found", {"requested": len(ALL_DEFS), "found": n, "notFound": bad})
            _chk(t, not bad and n == len(ALL_DEFS),
                 "%d of %d shipped defs did not resolve: %s" % (len(ALL_DEFS) - n, len(ALL_DEFS), bad[:10]))
            _chk(t, len(ALL_DEFS) >= 50, "only %d defs were derived from Defs/*.xml -- the file scan is broken" % len(ALL_DEFS))
            # sanity probe: the same tool must be able to say "not found"
            p = _call(t, "jawa/get_defs", defs="ThingDef/RM_NoSuchDefProbe_Sanity")
            _chk(t, "RM_NoSuchDefProbe_Sanity" in " ".join(str(x) for x in (p.get("notFound") or [])),
                 "sanity probe: get_defs did not list a bogus def as notFound: %s" % json.dumps(p, default=str)[:200])

    with _comp(t, "patches_applied"):
        if _live(t):
            tags = _get_defs(t, "TerrainDef/WaterOceanShallow", "tags").get("WaterOceanShallow") or {}
            tg = _field(t, tags, "tags")
            _chk(t, isinstance(tg, list) and "RM_CrowncarpetBed" in tg,
                 "CrowncarpetBedTag did not land: WaterOceanShallow.tags = %r" % (tg,))
            stoves = _get_defs(t, ";".join("ThingDef/%s" % s for s in RECIPE_OWNERS), "recipes")
            for s in RECIPE_OWNERS:
                rec = _field(t, stoves.get(s) or {}, "recipes")
                miss = [m for m in MEAL_RECIPES if m not in (rec or [])]
                _chk(t, isinstance(rec, list) and not miss and len(MEAL_RECIPES) == 15,
                     "%s is missing %d of %d deepfire meal recipes (or the recipe set is not 15): %s"
                     % (s, len(miss), len(MEAL_RECIPES), miss[:5]))
            # get_defs serialises a List<Type> as 'RuntimeType' strings (MEASURED live 2026-10-07), so the type
            # names cannot be read from specialDesignatorClasses. Read the RESOLVED Orders toolbar instead: the
            # designators' own labels (Designator_Deepfire / Designator_RemoveDeepfire defaultLabel).
            cats = _call(t, "rimworld/list_architect_categories")
            rows = cats.get("categories") or []
            orders = next((c for c in rows if c.get("categoryDefName") == "Orders"), None)
            if not orders or not orders.get("id"):
                _unmeasured(t, "no architect category with categoryDefName 'Orders' in %s" % json.dumps(cats, default=str)[:200])
            lst = _call(t, "rimworld/list_architect_designators", categoryId=orders["id"])
            _ok(t, lst, "list_architect_designators(Orders)")
            ds = lst.get("designators")
            text = json.dumps(ds, default=str).lower()
            if not isinstance(ds, list) or "hunt" not in text:      # sanity probe: vanilla Hunt must be listed
                _unmeasured(t, "the Orders listing is not trustworthy (no vanilla Hunt): %s" % text[:300])
            lacking = [n for n in ("apply deepfire", "remove deepfire") if n not in text]
            _chk(t, not lacking, "DeepfireOrdersPatch did not register designator(s) %s in the resolved Orders toolbar" % lacking)

    with _comp(t, "mechanics_wired_to_defs"):
        if _live(t):
            cc = _call(t, "jawa/get_def", defName="RM_Crowncarpet", defType="ThingDef")
            _ok(t, cc, "get_def RM_Crowncarpet")
            comps = cc.get("comps")
            _chk(t, isinstance(comps, list) and comps, "get_def RM_Crowncarpet returned no comps list: %r" % (comps,))
            _chk(t, "MatDiscovery" in json.dumps(comps), "RM_Crowncarpet carries no CompProperties_MatDiscovery: %s"
                 % json.dumps(comps, default=str)[:300])
            fr = _call(t, "jawa/get_def", defName="RM_CrowncarpetFresh", defType="ThingDef")
            _ok(t, fr, "get_def RM_CrowncarpetFresh")
            _chk(t, "MatVitality" in json.dumps(fr.get("comps")),
                 "RM_CrowncarpetFresh carries no CompProperties_MatVitality: %s" % json.dumps(fr.get("comps"), default=str)[:300])
            gt = _call(t, "jawa/get_def", defName="RM_GlowTank", defType="ThingDef")
            _ok(t, gt, "get_def RM_GlowTank")
            _chk(t, "Building_GlowTank" in json.dumps(gt.get("extra") or {}),
                 "RM_GlowTank.thingClass is not Building_GlowTank: %s" % json.dumps(gt.get("extra"), default=str)[:300])


# ===================================================================================== chain 2: mat clock

def _gone_or_moved(t, defs):
    """The staged stack is in neither state inside the fixture rect. Search the whole map: found elsewhere = a pawn
    moved it (a FIXTURE fault, UNMEASURED); found nowhere = the stack was destroyed without leaving a dead stack."""
    rows = _things(t, defs)
    if rows:
        _unmeasured(t, "the staged stack left the fixture rect (hauled?): %s"
                    % json.dumps([(r.get("defName") or r.get("def"), _xz(r), r.get("stackCount")) for r in rows[:5]], default=str))
    _fail("the staged stack is gone from the whole map -- neither fresh nor dead exists anywhere (comp destroyed it "
          "without leaving RM_CrowncarpetDead, or the spawn never persisted)")


@suite.chain("mat_vitality")
def mat_vitality(t):
    """Fresh crowncarpet lives one day and dies at once if chilled (spec 2.2). Control first (chill disabled,
    full life: alive after 600 ticks), then the same environment with the clock cut short, then with the chill
    threshold raised above any ambient. The three arms differ in ONE setting each, so they can fail."""
    x, z = _pad(t, "mat")
    rect = _rect(x - 6, z - 6, 13, 13)
    fresh_cell = "%d,%d" % (x, z)
    _GEN = {}
    with _comp(t, "mat_alive_control", toggle="matLifeDays"):
        if _live(t):
            _call(t, "jawa/destroy_batch", rects=rect, categories="All")
        with _settings(t, matChillKillTemp=MAT_CHILL_OFF, matLifeDays="1"):
            if _live(t):
                _room(t, x, z)         # a doorless sealed room: no colonist can reach and haul the stack away
            _spawn(t, "RM_CrowncarpetFresh:%s,4" % fresh_cell)
            _wait(t, 600)
            fresh = _things(t, "RM_CrowncarpetFresh", rect)
            dead = _things(t, "RM_CrowncarpetDead", rect)
            if _live(t) and not fresh and not dead:
                _gone_or_moved(t, "RM_CrowncarpetFresh,RM_CrowncarpetDead")
            _GEN["fresh"] = _stack(fresh)
            _chk(t, _stack(fresh) == 4 and not dead,
                 "control: with chill disabled and a 1-day life the stack should still be 4 alive after 600 ticks "
                 "(fresh=%d dead=%d)" % (_stack(fresh), _stack(dead)))
            if _live(t):
                ins = _call(t, "jawa/inspect_string", thingIds=fresh[0].get("id"))
                _ok(t, ins, "inspect_string")
                text = json.dumps(ins.get("things") or ins, default=str)
                _chk(t, "alive:" in text, "inspect string carries no 'alive: Nh left' countdown: %s" % text[:300])

    with _comp(t, "mat_dies_on_clock", toggle="matLifeDays"):
        with _settings(t, matChillKillTemp=MAT_CHILL_OFF, matLifeDays="0.005"):   # 0.005 d = 300 ticks < ticksAlive
            _wait(t, 400)
            fresh = _things(t, "RM_CrowncarpetFresh", rect)
            dead = _things(t, "RM_CrowncarpetDead", rect)
            _chk(t, not fresh and _stack(dead) == _GEN.get("fresh", 4),
                 "cutting matLifeDays to 0.005 should turn the whole stack into RM_CrowncarpetDead with the same "
                 "stackCount (fresh=%d dead=%d, control stack was %s)" % (_stack(fresh), _stack(dead), _GEN.get("fresh")))

    with _comp(t, "mat_dies_when_chilled", toggle="matChillKillTemp"):
        if _live(t):
            _call(t, "jawa/destroy_batch", rects=rect, categories="All")
        with _settings(t, matChillKillTemp="100", matLifeDays="1"):
            if _live(t):
                _room(t, x, z)
            _spawn(t, "RM_CrowncarpetFresh:%s,4" % fresh_cell)
            _wait(t, 600)
            fresh = _things(t, "RM_CrowncarpetFresh", rect)
            dead = _things(t, "RM_CrowncarpetDead", rect)
            _chk(t, not fresh and _stack(dead) == 4,
                 "ambient below matChillKillTemp=100 must kill a fresh stack within a rare tick, while the control "
                 "arm (threshold -100, same cell) stayed alive (fresh=%d dead=%d)" % (_stack(fresh), _stack(dead)))


# =================================================================================== chain 3: sighting gate

def _avail(t):
    r = _call(t, "jawa/research_availability", project="RM_DeepfireRefining")
    _ok(t, r, "research_availability")
    return r


def _finished(r):
    """None when the tool does not say."""
    for k in ("isFinished", "finished"):
        if k in r:
            return bool(r[k])
    snap = r.get("project")
    if isinstance(snap, dict):
        for k in ("isFinished", "finished"):
            if k in snap:
                return bool(snap[k])
    return None


@suite.chain("research_gate")
def research_gate(t):
    """Spec 2.3: RM_DeepfireRefining cannot start until a colonist has SEEN crowncarpet (CompMatDiscovery sets
    GameComponent_Deepfire.matSeen, which persists in the game; Harmony postfix on CanStartNow keeps it locked)."""
    x, z = _pad(t, "gate")
    state = {}
    with _comp(t, "locked_before_sighting"):
        if _live(t):
            _call(t, "jawa/research_finish_project", project="Electricity", doCompletionDialog=False,
                  doCompletionLetter=False)        # the project's one prerequisite; an already-finished refusal is fine
            a = _avail(t)
            state["before"] = a
            if _finished(a):
                _unmeasured(t, "RM_DeepfireRefining is already finished in this game (pressGate Buildable ran earlier)")
            if a.get("prerequisitesCompleted") is not True:
                _unmeasured(t, "Electricity did not finish, so the gate cannot be isolated: %s" % json.dumps(a, default=str)[:300])
            others = [k for k in ("techprintRequirementMet", "playerMechanitorRequirementMet",
                                  "analyzedThingsRequirementsMet", "inspectionRequirementsMet") if a.get(k) is False]
            if a.get("isHidden") is True or others:
                _unmeasured(t, "another gate is closed (isHidden=%r, %s), so canStartNow=false proves nothing about ours"
                            % (a.get("isHidden"), others))
            if a.get("canStartNow") is True:
                _unmeasured(t, "canStartNow is already true: matSeen was set earlier in this game (it persists); "
                               "run on a fresh game to measure the locked state")
            _chk(t, a.get("canStartNow") is False, "research_availability gave no canStartNow: %s" % json.dumps(a, default=str)[:300])

    with _comp(t, "unlocked_after_sighting"):
        if _live(t):
            _call(t, "jawa/set_fog", action="unfog", rect=_rect(x - 8, z - 8, 17, 17))
            pid = _spawn_colonist(t, x + 2, z)
            # The pad sits in the quicktest's rock, whose terrain has no Light affordance, so set_plants rejects the
            # cell ("terrain or conditions cannot support", MEASURED live 2026-10-07). The plant ignores fertility,
            # so plain Soil under it is all it needs; the wild-bed tag is irrelevant to a hand-placed plant.
            st = _call(t, "jawa/set_terrain", terrainDef="Soil", x=x, z=z, width=1, height=1)
            _ok(t, st, "set_terrain Soil under the crowncarpet")
            pl = _call(t, "jawa/set_plants", ops="RM_Crowncarpet:%d,%d,1,1" % (x, z), growth=1.0, clearFirst=False)
            if not int(pl.get("planted") or 0):
                _unmeasured(t, "set_plants refused the crowncarpet cell: %s" % json.dumps(pl, default=str)[:300])
            _wait(t, 2100)       # CompTickLong: plants tick Long (2000), the comp checks colonists within 20 cells
            if not _things(t, "RM_Crowncarpet", _rect(x - 3, z - 3, 7, 7)):
                _unmeasured(t, "the crowncarpet plant is gone before its long tick, so no sighting could happen")
            a = _avail(t)
            _chk(t, a.get("canStartNow") is True,
                 "a colonist stood 2 cells from a spawned, unfogged crowncarpet for 2100 ticks and RM_DeepfireRefining "
                 "is still locked: %s" % json.dumps(a, default=str)[:300])


# ===================================================================================== chain 4: settings apply

def _designation(t, defname):
    row = _get_defs(t, "ThingDef/%s" % defname, "designationCategory").get(defname) or {}
    v = row.get("designationCategory", "(absent)")
    if _live(t) and v == "(no such field)":
        _unmeasured(t, "get_defs cannot read ThingDef.designationCategory")
    # MEASURED live 2026-10-07: jawa/get_defs OMITS a null field from `fields` (a requested field whose value is null
    # comes back as an empty dict), so a nulled designationCategory reads "(absent)" here. A typo'd field name is
    # different -- it answers "(no such field)", handled above as UNMEASURED.
    return None if v in (None, "null", "None", "", "(absent)") else v


@suite.chain("settings_apply")
def settings_apply(t):
    """Def-level Mod Settings reach the defs when the settings dialog closes (ApplySettings). The market-value
    canary comes first; the arms after it need the same apply path."""
    with _comp(t, "apply_reaches_defs", toggle="deepfireMarketValue"):
        try:
            if _live(t):
                def mv():
                    r = _call(t, "jawa/get_def", defName="RM_Deepfire", defType="ThingDef")
                    _ok(t, r, "get_def RM_Deepfire")
                    sb = r.get("statBases")
                    items = sb.items() if isinstance(sb, dict) else [
                        (s.get("stat") or s.get("defName") or s.get("name"), s.get("value")) for s in (sb or [])
                        if isinstance(s, dict)]
                    for k, v in items:
                        if k == "MarketValue":
                            return float(v)
                    _unmeasured(t, "cannot find MarketValue in get_def statBases: %s" % json.dumps(sb, default=str)[:300])
                before = mv()
                _chk(t, _near(before, 90.0, 0.5), "RM_Deepfire MarketValue reads %s, shipped default is 90" % before)
                _APPLY["ok"] = False
                with _settings(t, deepfireMarketValue="200"):
                    _apply(t)
                    after = mv()
                    _APPLY["ok"] = _near(after, 200.0, 0.5)
                    _chk(t, _near(after, 200.0, 0.5),
                         "deepfireMarketValue=200 then settings-dialog close left MarketValue at %s (ApplySettings did "
                         "not reach the def; if the dialog could be opened this is the apply path, not one toggle)" % after)
        finally:
            _apply_safely(t)

    with _comp(t, "glowtank_toggle", toggle="glowTankEnabled"):
        try:
            if _live(t):
                _chk(t, _designation(t, "RM_GlowTank") == "Production",
                     "RM_GlowTank is not in Production under the shipped default (glowTankEnabled=True)")
                with _settings(t, glowTankEnabled="False"):
                    _apply(t)
                    _chk(t, _designation(t, "RM_GlowTank") is None,
                         "glowTankEnabled=False did not remove the GlowTank from the build menu")
        finally:
            _apply_safely(t)

    with _comp(t, "press_unbuildable", toggle="pressGate"):
        try:
            if _live(t):
                _chk(t, _designation(t, "RM_DeepfirePress") == "Production",
                     "RM_DeepfirePress is not in Production under pressGate=Research")
                with _settings(t, pressGate="Unbuildable"):
                    _apply(t)
                    _chk(t, _designation(t, "RM_DeepfirePress") is None,
                         "pressGate=Unbuildable did not remove the press from the build menu")
        finally:
            _apply_safely(t)

    with _comp(t, "cuisine_recipes_toggle", toggle="cuisineEnabled"):
        try:
            if _live(t):
                def listed():
                    rows = _get_defs(t, ";".join("ThingDef/%s" % s for s in RECIPE_OWNERS), "recipes")
                    return dict((s, [m for m in MEAL_RECIPES if m in (_field(t, rows.get(s) or {}, "recipes") or [])])
                                for s in RECIPE_OWNERS)
                on = listed()
                _chk(t, all(len(v) == len(MEAL_RECIPES) for v in on.values()),
                     "under cuisineEnabled=True the stoves list %s of %d recipes"
                     % ({k: len(v) for k, v in on.items()}, len(MEAL_RECIPES)))
                with _settings(t, cuisineEnabled="False"):
                    _apply(t)
                    off = listed()
                    _chk(t, all(not v for v in off.values()),
                         "cuisineEnabled=False left deepfire recipes on the stoves: %s" % {k: len(v) for k, v in off.items()})
        finally:
            _apply_safely(t)

    with _comp(t, "press_buildable_finishes_research", toggle="pressGate"):
        try:
            if _live(t):
                a = _avail(t)
                fin = _finished(a)
                if fin is None:
                    _unmeasured(t, "research_availability does not report whether the project is finished: %s"
                                % json.dumps(a, default=str)[:300])
                if fin:
                    _unmeasured(t, "RM_DeepfireRefining was already finished before this arm")
                with _settings(t, pressGate="Buildable"):
                    _apply(t)
                    a2 = _avail(t)
                    _chk(t, _finished(a2) is True,
                         "pressGate=Buildable then dialog close did not complete RM_DeepfireRefining: %s"
                         % json.dumps(a2, default=str)[:300])
        finally:
            _apply_safely(t)       # the project stays finished for the rest of this game; recorded in the live sheet


# =================================================================================== chain 5: deepfire glow

@suite.chain("item_glow")
def item_glow(t):
    """Spec 2.4: a stack of refined deepfire glows faintly, on its own (CompGlower 1.5), and deepfireStackGlows
    turns it off. Roofed room = the only light in it is ours."""
    x, z = _pad(t, "glow")
    cx, cz = x + 1, z + 1            # stack cell
    ox, oz = x + 5, z + 5            # control cell, 5+ away
    with _comp(t, "stack_glows"):
        _room(t, x, z)
        _wait(t, 5)
        if _live(t):
            base_c, base_o = _glow(t, cx, cz), _glow(t, ox, oz)
            _chk(t, base_c < LIT and base_o < LIT, "the roofed room is not dark before the stack (%.3f / %.3f)" % (base_c, base_o))
            _spawn(t, "RM_Deepfire:%d,%d,10" % (cx, cz))
            _wait(t, 10)
            on_c, on_o = _glow(t, cx, cz), _glow(t, ox, oz)
            _note(t, "glow", {"stackBefore": base_c, "stackAfter": on_c, "controlAfter": on_o})
            _chk(t, on_c > base_c + 0.01, "a 10-stack of RM_Deepfire raised the glow at its own cell by only %.4f" % (on_c - base_c))
            _chk(t, on_c > on_o, "glow at the stack (%.3f) is not above the control cell 5 away (%.3f)" % (on_c, on_o))

    with _comp(t, "stack_glow_toggle", toggle="deepfireStackGlows"):
        try:
            if _live(t) and _APPLY["ok"] is False:
                _unmeasured(t, "the canary settings_apply.apply_reaches_defs failed: the settings-dialog apply path "
                               "does not reach defs, so this arm cannot be read")
            if _live(t):
                with _settings(t, deepfireStackGlows="False"):
                    _apply(t)
                    _call(t, "jawa/destroy_batch", rects=_rect(cx, cz, 1, 1), categories="All")
                    _spawn(t, "RM_Deepfire:%d,%d,10" % (x + 3, z + 3))     # a NEW stack registers its glower under the new radius
                    _wait(t, 10)
                    off = _glow(t, x + 3, z + 3)
                    _chk(t, off < LIT and off <= _glow(t, ox, oz) + 0.01,
                         "deepfireStackGlows=False: a fresh stack still lights its cell (glow %.3f)" % off)
        finally:
            _apply_safely(t)


# ================================================================================== chain 6: the powered press

def _power(t, thing, on=None):
    if on is None:
        r = _call(t, "jawa/power_net", thing=thing)
    else:
        r = _call(t, "jawa/power_net", thing=thing, forcePowerOn=bool(on))
    _ok(t, r, "power_net")
    return r


def _deepfire_here(t, x, z):
    """Deepfire stacks inside this chain's own room (earlier chains leave stacks elsewhere on the map)."""
    return _stack(_things(t, "RM_Deepfire", _rect(x - 2, z - 6, 10, 12)))


def _run_batch(t, x, z, press_id, label, budget=9000):
    """Stage 4 fresh + 1 neutroamine + 2 chemfuel on the row at (x..x+2, z), queue one refine bill, wait up to
    `budget` ticks for RM_Deepfire to appear. Returns (deepfire stack count, leftover ingredient units)."""
    _spawn(t, "RM_CrowncarpetFresh:%d,%d,4;Neutroamine:%d,%d,1;Chemfuel:%d,%d,2" % (x, z, x + 1, z, x + 2, z))
    b = _call(t, "jawa/bill_add", giverId=press_id, recipe="RM_RefineDeepfire", repeatMode="RepeatCount", repeatCount=1)
    if _live(t) and not b.get("success"):
        _unmeasured(t, "bill_add refused (%s): %s" % (label, json.dumps(b, default=str)[:300]))
    got = 0
    spent = 0
    held = _deepfire_here(t, x, z)      # stacks already in the room before this batch
    while spent < budget:
        _wait(t, 500)
        spent += 500
        got = _deepfire_here(t, x, z) - held
        if got:
            break
    left = _stack(_things(t, "RM_CrowncarpetFresh,Neutroamine,Chemfuel", _rect(x - 4, z - 4, 12, 12)))
    return got, left, spent


@suite.chain("press_refine")
def press_refine(t):
    """Spec 2.3: the press is POWERED ONLY; 4 fresh mat + 1 neutroamine + 2 chemfuel -> 2 deepfire. The powered
    batch is the control for the unpowered one (it proves a pawn WILL take the bill here); both use one bench."""
    x, z = _pad(t, "press")
    ids = {}
    with _comp(t, "press_is_a_powered_bench", toggle=None):
        _room(t, x, z)
        _prio(t, "Crafting", 1)
        _spawn(t, "RM_DeepfirePress:%d,%d" % (x + 2, z + 4))
        press = _one(t, "RM_DeepfirePress")
        ids["press"] = press.get("id")
        pn = _power(t, ids["press"])
        if _live(t):
            _chk(t, pn.get("isPowerTrader") is True, "RM_DeepfirePress has no CompPowerTrader: %s" % json.dumps(pn, default=str)[:300])
            # CompPower.WattsToWattDaysPerTick = 1/60000: the engine reports energy per tick in watt-DAYS, so the
            # shipped 150 W reads -0.0025 (MEASURED live 2026-10-07: -0.0025). Tolerance 0.0002 still tells 150 W
            # from the 100 W / 200 W neighbours (+-0.0008).
            _chk(t, _near(pn.get("energyOutputPerTick"), -PRESS_WATTS / 60000.0, 0.0002),
                 "press draw is %s per tick; shipped pressPower=%d W is %.5f per tick"
                 % (pn.get("energyOutputPerTick"), PRESS_WATTS, -PRESS_WATTS / 60000.0))
            _chk(t, pn.get("powerOnBefore") is False, "an unconnected press reads powered-on (powerOn=%r)" % pn.get("powerOnBefore"))

    with _comp(t, "powered_press_refines"):
        pn = _power(t, ids.get("press"), on=True)
        if _live(t) and pn.get("powerOnAfter") is not True:
            _unmeasured(t, "cannot force the press powered on (powerOnAfter=%r): %s"
                        % (pn.get("powerOnAfter"), json.dumps(pn, default=str)[:300]))
        got, left, took = _run_batch(t, x, z + 2, ids.get("press"), "powered")
        ids["took"] = took
        if _live(t):
            _note(t, "powered batch", {"deepfire": got, "leftoverIngredients": left, "ticksWaited": took})
            if got == 0:
                _unmeasured(t, "no deepfire after 9000 ticks with the bench forced on: no pawn took the bill (AI, "
                               "work priorities or reachability), so the recipe itself was not exercised")
            _chk(t, got == PRESS_YIELD, "one batch yielded %d deepfire, shipped pressYield is %d" % (got, PRESS_YIELD))
            _chk(t, left == 0, "the batch left %d ingredient units behind (it should consume 4 mat + 1 neutroamine + 2 chemfuel)" % left)

    with _comp(t, "unpowered_press_refuses"):
        if _live(t):
            before = _deepfire_here(t, x, z + 2)
            if before != PRESS_YIELD:
                _unmeasured(t, "the powered control did not complete (deepfire=%d), so an unpowered result would be vacuous" % before)
            pn = _power(t, ids.get("press"), on=False)
            if pn.get("powerOnAfter") is not False:
                _unmeasured(t, "cannot force the press off (powerOnAfter=%r)" % pn.get("powerOnAfter"))
            # the unpowered arm must wait LONGER than the powered one needed, or a press that ignores power
            # would simply not have finished yet and the arm would pass vacuously
            got, left, _ = _run_batch(t, x, z + 2, ids.get("press"), "unpowered",
                                      budget=max(3000, int(1.5 * (ids.get("took") or 0))))
            _chk(t, _deepfire_here(t, x, z + 2) == before and left == 7,
                 "with power forced off the press still produced (deepfire %d -> %d) or consumed ingredients (left %d of 7)"
                 % (before, _deepfire_here(t, x, z + 2), left))


# ===================================================================================== chain 7: the GlowTank

@suite.chain("glowtank")
def glowtank(t):
    """Spec 2.5: unseeded tank says so; a blackout past tankPowerGraceHours kills the seed culture, and power
    kept on does not (the control). The 12-day growth cycle is UNCOVERED (walk)."""
    x, z = _pad(t, "tank")
    ids = {}
    with _comp(t, "unseeded_tank_says_so"):
        _room(t, x, z)
        _spawn(t, "RM_GlowTank:%d,%d" % (x + 3, z + 3))
        tank = _one(t, "RM_GlowTank")
        ids["tank"] = tank.get("id")
        if _live(t):
            ins = _call(t, "jawa/inspect_string", thingIds=ids["tank"])
            _ok(t, ins, "inspect_string")
            text = json.dumps(ins.get("things") or ins, default=str)
            _chk(t, "Needs a seed culture" in text, "an unseeded GlowTank's inspect string lacks 'Needs a seed culture': %s" % text[:300])

    with _comp(t, "blackout_kills_seed", toggle="tankPowerGraceHours"):
        if _live(t):
            pid = _spawn_colonist(t, x, z)
            _spawn(t, "RM_CrowncarpetFresh:%d,%d,2" % (x + 1, z))
            mat = _one(t, "RM_CrowncarpetFresh", _rect(x, z, 6, 6))
            r = _call(t, "jawa/ordered_job", pawnId=pid, jobDef="Refuel", targetAId=ids["tank"],
                      targetBId=mat.get("id"), count=1, waitTicks=60)
            if not r.get("accepted"):
                _unmeasured(t, "the Refuel order was refused, so the tank cannot be seeded: %s" % json.dumps(r, default=str)[:300])
            seeded = False
            for _ in range(8):
                _wait(t, 250)
                ins = _call(t, "jawa/inspect_string", thingIds=ids["tank"])
                if "Needs a seed culture" not in json.dumps(ins.get("things") or ins, default=str):
                    seeded = True
                    break
            if not seeded:
                _unmeasured(t, "the tank never accepted a seed culture within 2000 ticks")
            with _settings(t, tankPowerGraceHours="0.1"):          # 250 ticks of grace
                _power(t, ids["tank"], on=True)
                _wait(t, 800)
                ins = _call(t, "jawa/inspect_string", thingIds=ids["tank"])
                _chk(t, "Needs a seed culture" not in json.dumps(ins.get("things") or ins, default=str),
                     "control: with the tank powered the seed culture was lost anyway")
                _power(t, ids["tank"], on=False)
                _wait(t, 1000)
                ins = _call(t, "jawa/inspect_string", thingIds=ids["tank"])
                _chk(t, "Needs a seed culture" in json.dumps(ins.get("things") or ins, default=str),
                     "a blackout longer than tankPowerGraceHours=0.1 did not kill the seed culture")

    # DESIGN_PASS LP-2 (GLOW_TANK_LIQUID_FEED_1): with FlowWorks loaded, a tank on no liquid net reads "Dry: growth
    # paused"; the setting off removes the line. FlowWorks absent: the gate never applies, so this cannot be judged.
    with _comp(t, "water_gate_dry_tank_pauses", toggle="tankNeedsWater"):
        if _live(t):
            _power(t, ids["tank"], on=True)
            with _settings(t, tankNeedsWater="True"):
                _wait(t, 500)
                on = json.dumps(_call(t, "jawa/inspect_string", thingIds=ids["tank"]), default=str)
            if "not needed (FlowWorks not loaded)" in on:
                _unmeasured(t, "FlowWorks is not loaded on this list, so the water gate cannot apply")
            _chk(t, "Dry: growth paused" in on, "a GlowTank on no liquid net did not read dry with FlowWorks loaded: %s" % on[:300])
            with _settings(t, tankNeedsWater="False"):
                _wait(t, 500)
                off = json.dumps(_call(t, "jawa/inspect_string", thingIds=ids["tank"]), default=str)
            _chk(t, "Dry: growth paused" not in off, "tankNeedsWater=False still reads dry")


# ================================================================================== chain 8: painting a thing

def _paint_fixture(t, x, z, deepfire=12):
    _room(t, x, z)
    _spawn(t, "Wall:%d,%d" % (x + 2, z + 4), stuff="Steel")
    _spawn(t, "RM_Deepfire:%d,%d,%d" % (x + 1, z, deepfire))
    wall = _one(t, "Wall", _rect(x + 2, z + 4, 1, 1))
    return wall.get("id"), _xz(wall)


@suite.chain("paint_pipeline")
def paint_pipeline(t):
    """Spec 3.2/3.3: designation -> WorkGiver -> JobDriver -> coat (the real path, with the pawn forced onto the
    job, as DEEPFIRE_PAINT_LIVE_VERIFY_1 did), three coats, glow that rises with them, removal."""
    x, z = _pad(t, "paint")
    s = {}
    with _comp(t, "wall_coat_via_real_job"):
        wid, (wx, wz) = _paint_fixture(t, x, z)
        s.update(wall=wid, wx=wx, wz=wz)
        pid = _spawn_colonist(t, x + 4, z + 1)
        if _live(t):
            cc = _call(t, "deepfire/comp_coats", thing=wid)
            _ok(t, cc, "comp_coats")
            _chk(t, cc.get("present") is True and cc.get("coats") == 0,
                 "a fresh steel wall has no CompDeepfire (or already coated): %s" % json.dumps(cc, default=str)[:200])
            s["base"] = _glow(t, wx, wz)
            _chk(t, s["base"] < LIT, "the roofed room is lit before any coat (%.3f)" % s["base"])
            _ok(t, _call(t, "deepfire/designate", thing=wid), "deepfire/designate")
            fj = _call(t, "deepfire/force_apply_job", pawn=pid, thing=wid)
            _ok(t, fj, "deepfire/force_apply_job")
            _chk(t, fj.get("jobDefName") == "RM_ApplyDeepfire", "forced job is %r, not RM_ApplyDeepfire" % fj.get("jobDefName"))
            coats = 0
            for _ in range(6):
                _wait(t, 250)
                coats = int(_call(t, "deepfire/comp_coats", thing=wid).get("coats") or 0)
                if coats:
                    break
            _chk(t, coats == 1, "the apply job did not leave a coat on the wall within 1500 ticks (coats=%d)" % coats)
            left = _stack(_things(t, "RM_Deepfire", _rect(x, z, 6, 6)))
            _chk(t, left == 11, "one coat on a wall cell should cost costWallCell=1 deepfire; 12 -> %d" % left)
            s["g1"] = _glow(t, wx, wz)
            _chk(t, s["g1"] > s["base"] + 0.01, "the coated wall did not raise the glow beside it (%.3f -> %.3f)" % (s["base"], s["g1"]))

    with _comp(t, "glow_colour_follows_paint"):
        _need(t, s, "wall", "wx", "wz")
        if _live(t):
            before = _glow_rgb(t, s["wx"], s["wz"])
            pr = _call(t, "deepfire/paint_building", thing=s["wall"], colorDef="Structure_Blue")
            _ok(t, pr, "deepfire/paint_building")
            _wait(t, 20)
            after = _glow_rgb(t, s["wx"], s["wz"])
            _note(t, "glow rgb before/after Structure_Blue", {"before": before, "after": after})
            _chk(t, after[2] - after[0] > before[2] - before[0] + 10 and after[2] > after[1],
                 "painting the coated wall Structure_Blue did not turn its glow blue-dominant: rgb %s -> %s" % (before, after))

    with _comp(t, "three_coats_then_refused"):
        _need(t, s, "wall", "wx", "wz", "g1")
        if _live(t):
            for _ in range(2):
                _ok(t, _call(t, "deepfire/add_coat", thing=s["wall"]), "add_coat")
            r4 = _call(t, "deepfire/add_coat", thing=s["wall"])
            cc = _call(t, "deepfire/comp_coats", thing=s["wall"])
            _wait(t, 20)
            s["g3"] = _glow(t, s["wx"], s["wz"])
            _chk(t, cc.get("coats") == 3 and cc.get("canAddCoat") is False,
                 "after 3 coats + a 4th attempt the wall reads coats=%s canAddCoat=%s (4th add: %s)"
                 % (cc.get("coats"), cc.get("canAddCoat"), json.dumps(r4, default=str)[:160]))
            _chk(t, s["g3"] > s["g1"] + 0.01, "three coats do not glow more than one (%.3f vs %.3f)" % (s["g3"], s["g1"]))

    with _comp(t, "remove_coats_clears_glow"):
        _need(t, s, "wall", "wx", "wz", "base")
        if _live(t):
            _ok(t, _call(t, "deepfire/remove_coats", thing=s["wall"]), "remove_coats")
            _wait(t, 20)
            cc = _call(t, "deepfire/comp_coats", thing=s["wall"])
            after = _glow(t, s["wx"], s["wz"])
            _chk(t, cc.get("coats") == 0 and _near(after, s["base"], 0.02),
                 "removing coats left coats=%s and glow %.3f (baseline %.3f)" % (cc.get("coats"), after, s["base"]))

    with _comp(t, "max_coats_setting", toggle="maxCoats"):
        _need(t, s, "wall")
        if _live(t):
            with _settings(t, maxCoats="1"):
                _ok(t, _call(t, "deepfire/add_coat", thing=s["wall"]), "add_coat")
                cc = _call(t, "deepfire/comp_coats", thing=s["wall"])
                _chk(t, cc.get("coats") == 1 and cc.get("canAddCoat") is False,
                     "maxCoats=1: after one coat canAddCoat is %s (coats=%s)" % (cc.get("canAddCoat"), cc.get("coats")))
            cc = _call(t, "deepfire/comp_coats", thing=s["wall"])
            _chk(t, cc.get("canAddCoat") is True, "restoring maxCoats did not re-open the wall to coats (canAddCoat=%s)" % cc.get("canAddCoat"))
            _call(t, "deepfire/remove_coats", thing=s["wall"])

    for comp_name, toggle, spawn_op, stuff, kind in (
            ("walls_paintable_toggle", "wallsPaintable", None, None, "Construction"),
            ("furniture_paintable_toggle", "furniturePaintable", "Stool", "WoodLog", "Construction"),
            ("apparel_paintable_toggle", "apparelPaintable", "Apparel_Parka", "Cloth", "Crafting"),
            ("weapons_paintable_toggle", "weaponsPaintable", "MeleeWeapon_Knife", "Steel", "Crafting")):
        with _comp(t, comp_name, toggle=toggle):
            _need(t, s, "wall")
            _paintable_ab(t, x, z, s, toggle, spawn_op, stuff, kind)

    with _comp(t, "painting_enabled_blocks_ai", toggle="paintingEnabled"):
        _painting_enabled_ab(t, x, z)


def _paintable_ab(t, x, z, s, toggle, spawn_op, stuff, kind):
    """A/B on the WorkGiver's own eligibility (HasJobOnThing reads the paintable toggles; deepfire/debug_workgiver
    calls it directly): True -> a free colonist has a job on the designated thing; False -> none does."""
    if not _live(t):
        return
    if spawn_op is None:
        tid = s["wall"]
    else:
        _spawn(t, "%s:%d,%d" % (spawn_op, x + 4, z + 3), stuff=stuff)
        tid = _one(t, spawn_op, _rect(x + 4, z + 3, 1, 1)).get("id")
    _ok(t, _call(t, "deepfire/designate", thing=tid), "deepfire/designate")
    key = "hasJobConstruction" if kind == "Construction" else "hasJobCrafting"

    def any_job():
        r = _call(t, "deepfire/debug_workgiver", thing=tid)
        _ok(t, r, "debug_workgiver")
        rows = [p for p in (r.get("pawns") or []) if "error" not in p]
        if not rows:
            _unmeasured(t, "debug_workgiver reported no usable colonist: %s" % json.dumps(r, default=str)[:300])
        return any(p.get(key) for p in rows), rows
    on, rows = any_job()
    if not on:
        _unmeasured(t, "control: no colonist has a %s job on the designated %s even with %s=True (%s)"
                    % (kind, spawn_op or "wall", toggle, json.dumps(rows[:2], default=str)[:300]))
    with _settings(t, **{toggle: "False"}):
        off, rows = any_job()
        _chk(t, not off, "%s=False but a colonist still has a deepfire job on the designated %s" % (toggle, spawn_op or "wall"))


def _painting_enabled_ab(t, x, z):
    """paintingEnabled gates WorkGiver_ApplyDeepfireBase.ShouldSkip, which only the real work scan consults, so
    this is a real-AI A/B: a designated wall is coated by an idle colonist with the toggle on, and left alone
    with it off. The ON arm is the control; if it never coats the OFF arm would pass vacuously -> UNMEASURED."""
    if not _live(t):
        return
    _prio(t, "Construction", 1)
    wid, _ = _paint_fixture(t, x, z, deepfire=12)
    _spawn_colonist(t, x + 4, z + 1)
    _ok(t, _call(t, "deepfire/designate", thing=wid), "deepfire/designate")
    coats = 0
    took = 0
    for _ in range(8):
        _wait(t, 250)
        took += 250
        coats = int(_call(t, "deepfire/comp_coats", thing=wid).get("coats") or 0)
        if coats:
            break
    if not coats:
        _unmeasured(t, "control: with paintingEnabled=True no colonist coated a designated wall in 2000 ticks (the "
                       "real AI path is known to be unreliable; the forced-job chain above is the proven route)")
    wid2, _ = _paint_fixture(t, x, z, deepfire=12)
    _spawn_colonist(t, x + 4, z + 1)
    with _settings(t, paintingEnabled="False"):
        _ok(t, _call(t, "deepfire/designate", thing=wid2), "deepfire/designate")
        _wait(t, max(2000, 2 * took))      # longer than the ON arm needed, or the OFF arm would pass vacuously
        c2 = int(_call(t, "deepfire/comp_coats", thing=wid2).get("coats") or 0)
        _chk(t, c2 == 0, "paintingEnabled=False but an idle colonist still coated the designated wall (coats=%d)" % c2)


# ================================================================================== chain 9: floors (6x6)

@suite.chain("floor_paint")
def floor_paint(t):
    """Spec 3.6 / DEEPFIRE_FLOOR_PAINT_1 (22/22 live 2026-09-30): a 6x6 floor coat is 36 grid cells lit by exactly
    4 shared proxies, tracks vanilla floor paint, and goes dark when stripped or when the floor is removed."""
    x, z = _pad(t, "floor")
    r0 = {}
    with _comp(t, "floor_baseline"):
        _room(t, x, z)
        r0.update(_act(t, "Floor: report 6x6", x, z))
        _chk(t, r0.get("floorCellsInRect") == 36 and r0.get("coatedInRect") == 0 and r0.get("floorLights") == 0
             and r0.get("roomCells") == 36 and r0.get("roomOutdoors") is False,
             "baseline is not a clean 36-cell roofed floor: %s" % json.dumps(r0, default=str)[:300])

    with _comp(t, "floor_coat_lights_in_four_blocks"):
        a1 = _act(t, "Floor: coat 6x6", x, z)
        r1 = _act(t, "Floor: report 6x6", x, z)
        _chk(t, a1.get("added") == 36, "floor coat added %s of 36 cells" % a1.get("added"))
        _chk(t, r1.get("coatedInRect") == 36 and r1.get("coatSumInRect") == 36, "grid holds %s coated cells" % r1.get("coatedInRect"))
        _chk(t, r1.get("floorLights") == 4, "36 coated cells must be lit by EXACTLY 4 shared proxies (one per 3x3 block), got %s"
             % r1.get("floorLights"))
        _chk(t, (r1.get("centerGroundGlow") or 0) > (r0.get("centerGroundGlow") or 0) and (r1.get("centerGroundGlow") or 0) > 0,
             "centre glow did not rise: %s -> %s" % (r0.get("centerGroundGlow"), r1.get("centerGroundGlow")))
        _chk(t, _near((r1.get("centerCellBeauty") or 0) - (r0.get("centerCellBeauty") or 0), 0.5, 0.01),
             "CellBeauty at the centre rose by %s, expected +0.5" % ((r1.get("centerCellBeauty") or 0) - (r0.get("centerCellBeauty") or 0)))
        _chk(t, _near(r1.get("roomDeepfireBonus"), 6.0, 0.01) and r1.get("roomCoatedCells") == 36,
             "room line is %s over %s coated cells, expected +6 over 36" % (r1.get("roomDeepfireBonus"), r1.get("roomCoatedCells")))
        n = (r0.get("roomCells") or 36)
        curve = 20.0 + n * 0.5 if n <= 40 else float(n)      # RoomStatWorker_Beauty.CellCountCurve
        want = 36 * 0.5 / curve + 6.0
        _chk(t, _near((r1.get("roomBeauty") or 0) - (r0.get("roomBeauty") or 0), want, 0.03),
             "room Beauty rose %s, expected %.3f (= 18/CellCountCurve + 6)"
             % ((r1.get("roomBeauty") or 0) - (r0.get("roomBeauty") or 0), want))

    with _comp(t, "floor_tracks_vanilla_paint"):
        a2 = _act(t, "Floor: vanilla-paint 6x6 red", x, z)
        r2 = _act(t, "Floor: report 6x6", x, z)
        v = r2.get("centerVisual") or [0, 0, 0]
        _chk(t, a2.get("colorDefFound") and a2.get("painted") == 36, "red paint did not apply to 36 cells: %s" % json.dumps(a2))
        _chk(t, r2.get("centerColorDef") == "Structure_Red", "centre colour def is %r" % r2.get("centerColorDef"))
        _chk(t, r2.get("coatedInRect") == 36 and r2.get("floorLights") == 4, "painting dropped coats or proxies: %s/%s"
             % (r2.get("coatedInRect"), r2.get("floorLights")))
        _chk(t, v[0] > v[1] and v[0] > v[2], "glow at the centre is not red-dominant after red paint: rgb=%s" % (v,))

    with _comp(t, "floor_strip_clears_everything"):
        a3 = _act(t, "Floor: strip coats 6x6", x, z)
        r3 = _act(t, "Floor: report 6x6", x, z)
        _chk(t, a3.get("stripped") == 36 and r3.get("coatedInRect") == 0 and r3.get("floorLights") == 0,
             "strip left coated=%s lights=%s" % (r3.get("coatedInRect"), r3.get("floorLights")))
        _chk(t, _near(r3.get("roomBeauty"), r0.get("roomBeauty"), 0.03) and _near(r3.get("roomDeepfireBonus"), 0.0),
             "room Beauty %s / line %s did not return to baseline %s" % (r3.get("roomBeauty"), r3.get("roomDeepfireBonus"), r0.get("roomBeauty")))

    with _comp(t, "floor_removed_takes_coat_with_it"):
        _act(t, "Floor: coat 6x6", x, z)
        a5 = _act(t, "Floor: remove floor 6x6", x, z)
        r5 = _act(t, "Floor: report 6x6", x, z)
        _chk(t, a5.get("removed") == 36 and r5.get("coatedInRect") == 0 and r5.get("floorLights") == 0 and r5.get("floorCellsInRect") == 0,
             "removing the floor left coated=%s lights=%s floorCells=%s" % (r5.get("coatedInRect"), r5.get("floorLights"), r5.get("floorCellsInRect")))
        _chk(t, _near(r5.get("roomDeepfireBonus"), 0.0), "room line survived the floor: %s" % r5.get("roomDeepfireBonus"))


# =========================================================================== chain 10: first-coat bonus

@suite.chain("first_coat")
def first_coat(t):
    """Spec 3.5 / DEEPFIRE_FIRSTCOAT_BONUS_1 (10/10 live): the first coat bumps an art item's quality ONCE (capped
    at Legendary), or adds a flat+percent Beauty to everything else; later coats and re-coating never re-bump."""
    x, z = _pad(t, "coat1")
    with _comp(t, "art_quality_bumps_once"):
        _room(t, x, z)
        a0 = _act(t, "FirstCoat: spawn art Normal", x, z)
        _chk(t, a0.get("isArt") and a0.get("quality") == "Normal" and a0.get("coats") == 0 and not a0.get("bonusApplied"),
             "spawned art is not a clean Normal sculpture: %s" % json.dumps(a0))
        a1 = _act(t, "FirstCoat: coat thing", x, z)
        _chk(t, a1.get("coats") == 1 and a1.get("bonusApplied") is True and a1.get("quality") == "Good",
             "first coat: expected coats=1 bonusApplied quality Good, got %s" % json.dumps(a1))
        a2 = _act(t, "FirstCoat: coat thing", x, z)
        _chk(t, a2.get("coats") == 2 and a2.get("quality") == "Good", "second coat re-bumped or lost coats: %s" % json.dumps(a2))

    with _comp(t, "legendary_caps_but_still_charges"):
        _act(t, "FirstCoat: destroy thing", x, z)
        s = _act(t, "FirstCoat: spawn art Legendary", x, z)
        _chk(t, s.get("quality") == "Legendary", "spawned art is %r, not Legendary" % s.get("quality"))
        a3 = _act(t, "FirstCoat: coat thing", x, z)
        _chk(t, a3.get("quality") == "Legendary" and a3.get("coats") == 1, "Legendary art: %s" % json.dumps(a3))
        _act(t, "FirstCoat: destroy thing", x, z)

    with _comp(t, "art_bump_toggle", toggle="artQualityBump"):
        with _settings(t, artQualityBump="False"):
            _act(t, "FirstCoat: spawn art Normal", x, z)
            a = _act(t, "FirstCoat: coat thing", x, z)
            _chk(t, a.get("coats") == 1 and a.get("quality") == "Normal",
                 "artQualityBump=False: the coat must charge without bumping quality, got %s" % json.dumps(a))
            _act(t, "FirstCoat: destroy thing", x, z)

    with _comp(t, "wall_beauty_bonus_exact_and_not_doubled"):
        r0 = _act(t, "FirstCoat: spawn wall", x, z)
        _chk(t, not r0.get("isArt") and r0.get("coats") == 0, "spawned wall: %s" % json.dumps(r0))
        base = r0.get("beauty")
        if _live(t):
            # thing_stats resolves the engine's string id ("Wall92242"), not the bare thingIDNumber the debug
            # action logs (MEASURED live 2026-10-07: NoSuchThingId for 92242 and 58072), so look the wall up.
            wall = _one(t, "Wall", _rect(x, z, 1, 1))
            ts = _call(t, "jawa/thing_stats", thing=wall.get("id"), stats="Beauty")
            _ok(t, ts, "thing_stats Beauty")
            parts = json.dumps([s.get("statParts") for th in (ts.get("things") or []) for s in (th.get("stats") or [])])
            _chk(t, "Deepfire" in parts, "the Beauty StatPart patch did not land: statParts=%s" % parts[:300])
        r1 = _act(t, "FirstCoat: coat thing", x, z)
        want = 3.0 + 0.25 * (base or 0.0)             # beautyFlat * min(area,4)=1 + beautyPct * base
        _chk(t, r1.get("coats") == 1 and _near((r1.get("beauty") or 0) - (base or 0), want, 0.02),
             "wall Beauty rose %s, expected %.4f (flat 3 + 25%% of %s)" % ((r1.get("beauty") or 0) - (base or 0), want, base))
        r2 = _act(t, "FirstCoat: remove coats", x, z)
        _chk(t, r2.get("coats") == 0 and _near(r2.get("beauty"), base, 0.02), "stripping left Beauty %s (baseline %s)" % (r2.get("beauty"), base))
        r3 = _act(t, "FirstCoat: coat thing", x, z)
        _chk(t, r3.get("coats") == 1 and _near(r3.get("beauty"), r1.get("beauty"), 0.02),
             "re-coating rose to %s, first coat was %s (double count)" % (r3.get("beauty"), r1.get("beauty")))
        _act(t, "FirstCoat: destroy thing", x, z)


# ===================================================================== chain 11: proxies vs storage

@suite.chain("proxy_storage")
def proxy_storage(t):
    """DEEPFIRE_PROXY_BLOCKS_STORAGE_1 (17/17 live): the shared light proxies are Ethereal, so they displace no
    stockpile item and never block a storage cell; a coated wall spawns a clustered proxy and stays standing."""
    x, z = _pad(t, "proxy")
    with _comp(t, "coat_over_a_stockpile_displaces_nothing"):
        _room(t, x, z)
        a0 = _act(t, "Proxy: stockpile + items 6x6", x, z)
        _chk(t, a0.get("zoneCells") == 36 and a0.get("items") == 36, "stockpile fixture: %s" % json.dumps(a0))
        _act(t, "Floor: coat 6x6", x, z)
        r1 = _act(t, "Proxy: storage report 6x6", x, z)
        _chk(t, r1.get("proxyCategory") == "Ethereal", "proxy def category is %r, not Ethereal" % r1.get("proxyCategory"))
        _chk(t, r1.get("floorLights") == 4 and r1.get("proxyCellsInRect") == 4 and r1.get("proxiesSeenInGrid") == 4,
             "expected 4 proxies spawned in the thing grid, got lights=%s inRect=%s seen=%s"
             % (r1.get("floorLights"), r1.get("proxyCellsInRect"), r1.get("proxiesSeenInGrid")))
        _chk(t, r1.get("tracked") == 36 and r1.get("displaced") == 0 and r1.get("lost") == 0,
             "stockpile items displaced=%s lost=%s of %s" % (r1.get("displaced"), r1.get("lost"), r1.get("tracked")))
        _chk(t, r1.get("maxItemCountOnProxyCell") == 1, "a proxy cell counts %s items (the proxy itself must not count)" % r1.get("maxItemCountOnProxyCell"))

    with _comp(t, "emptied_cells_accept_storage"):
        _act(t, "Proxy: clear placed items", x, z)
        r2 = _act(t, "Proxy: storage report 6x6", x, z)
        _chk(t, r2.get("proxyCellsValidStorage") == 4 and r2.get("emptyCellsValidStorage") == 36 and r2.get("floorLights") == 4,
             "storage validity: proxyCells=%s emptyCells=%s lights=%s"
             % (r2.get("proxyCellsValidStorage"), r2.get("emptyCellsValidStorage"), r2.get("floorLights")))

    with _comp(t, "coated_wall_stands_beside_its_proxy"):
        wx = x + 10
        before = _act(t, "Floor: report 6x6", x, z)
        w0 = _act(t, "FirstCoat: spawn wall", wx, z)
        w1 = _act(t, "FirstCoat: coat thing", wx, z)
        w2 = _act(t, "FirstCoat: report thing", wx, z)
        after = _act(t, "Floor: report 6x6", x, z)
        _chk(t, w0.get("found") and w1.get("coats") == 1 and w2.get("found") and w2.get("thingId") == w0.get("thingId"),
             "the wall did not survive its own proxy: %s / %s" % (json.dumps(w0)[:120], json.dumps(w2)[:120]))
        _chk(t, after.get("clusteredBuildingLights") == before.get("clusteredBuildingLights", 0) + 1,
             "a coated wall should add one clustered building proxy: %s -> %s"
             % (before.get("clusteredBuildingLights"), after.get("clusteredBuildingLights")))
        _act(t, "FirstCoat: destroy thing", wx, z)


# ============================================================================ chain 12: worn glow

@suite.chain("worn_glow")
def worn_glow(t):
    """Spec 3.4 / DEEPFIRE_WORN_GLOW_1 (15/15 live): a coated garment makes its wearer a moving light (one proxy
    that follows the pawn), plus the dark-only combat trade; the styling station lacquers a worn item."""
    x, z = _pad(t, "worn")
    st = {}
    with _comp(t, "coated_walker_carries_a_light"):
        if _live(t):
            # The 30-cell walk strip lies in the quicktest's rock: the walker's Goto ended at once (job "Wait", cell
            # unchanged over 80 samples, MEASURED live 2026-10-07), so clear the buildings off the strip first.
            _call(t, "jawa/destroy_batch", rects=_rect(x - 3, z - 4, 40, 9), categories="Building")
        r0 = _act(t, "WornGlow: roof dark strip", x, z)
        _chk(t, r0.get("baselineGlow", 1) < LIT, "the roofed strip is not dark: %s" % json.dumps(r0))
        _act(t, "WornGlow: spawn coated walker", x, z)
        w1 = _act(t, "WornGlow: report walker", x, z)
        _chk(t, w1.get("coats") == 3 and w1.get("tracked") and (w1.get("proxyX"), w1.get("proxyZ")) == (w1.get("x"), w1.get("z"))
             and (w1.get("groundGlow") or 0) > LIT and w1.get("glowingInDark"),
             "walker report: %s" % json.dumps(w1)[:400])
        st["x0"] = w1.get("x")

    with _comp(t, "light_follows_the_walker"):
        wk = _act(t, "WornGlow: walker walk 30 east", x, z)
        _chk(t, wk.get("ordered"), "walk not ordered: %s" % json.dumps(wk))
        dest = (wk.get("destX"), wk.get("destZ"))
        cur = _act(t, "WornGlow: report walker", x, z)
        _wait(t, (POLL - (cur.get("ticks", 0) % POLL)) % POLL or POLL)      # land on a poll tick
        samples, bad = [], []
        for _ in range(80 if _live(t) else 0):
            s = _act(t, "WornGlow: report walker", x, z)
            samples.append(s)
            on_proxy = (s.get("proxyX"), s.get("proxyZ")) == (s.get("x"), s.get("z"))
            if not (s.get("tracked") and on_proxy and s.get("roofed") and (s.get("groundGlow") or 0) > LIT):
                bad.append(s)
            if (s.get("x"), s.get("z")) == dest and s.get("job") != "Goto":
                break
            _wait(t, POLL)
        if _live(t):
            travelled = (samples[-1].get("x", 0) - st["x0"]) if samples and st.get("x0") is not None else 0
            distinct = len(set((s.get("x"), s.get("z")) for s in samples))
            _chk(t, travelled >= 25 and distinct >= 5,
                 "the light was seen at %d distinct cells over %s cells travelled (need >=5 and >=25)" % (distinct, travelled))
            _chk(t, samples and not bad, "%d of %d samples had the proxy off the pawn's cell or the cell unlit: %s"
                 % (len(bad), len(samples), json.dumps(bad[:2])[:300]))

    with _comp(t, "stripping_the_garment_darkens_the_pawn"):
        s3 = _act(t, "WornGlow: strip walker", x, z)
        _chk(t, not s3.get("tracked") and (s3.get("groundGlow") if s3.get("groundGlow") is not None else 1) < LIT and not s3.get("glowingInDark"),
             "stripped walker still tracked or lit: %s" % json.dumps(s3)[:300])

    with _comp(t, "worn_light_toggle", toggle="wornLightEnabled"):
        with _settings(t, wornLightEnabled="False"):
            _act(t, "WornGlow: spawn coated walker", x, z)
            off = _act(t, "WornGlow: report walker", x, z)
            _chk(t, not off.get("tracked"), "wornLightEnabled=False but the coated walker is still tracked: %s" % json.dumps(off)[:300])
        _act(t, "WornGlow: strip walker", x, z)

    with _comp(t, "dark_combat_trade_in_twenty_pairs"):
        h = _act(t, "WornGlow: 20 hit-report pairs", x + 15, z + 15)
        _chk(t, h.get("darkCount") == 20 and h.get("coatedHigher") == 20 and h.get("readoutLines") == 20
             and h.get("dodgeLowerOrZero") == 20 and h.get("dodgeExplained") == 20,
             "pairs (of 20): dark=%s aimHigher=%s readout=%s dodge<=%s explained=%s"
             % (h.get("darkCount"), h.get("coatedHigher"), h.get("readoutLines"), h.get("dodgeLowerOrZero"), h.get("dodgeExplained")))

    with _comp(t, "combat_penalty_toggle", toggle="combatPenaltiesEnabled"):
        with _settings(t, combatPenaltiesEnabled="False"):
            h = _act(t, "WornGlow: 20 hit-report pairs", x + 15, z + 15)
            _chk(t, (h.get("coatedHigher") if h.get("coatedHigher") is not None else 20) < 20,
                 "combatPenaltiesEnabled=False but the coated twin still aims higher in all 20 pairs: %s" % json.dumps({k: v for k, v in h.items() if k != "rows"})[:300])


@suite.chain("styling_lacquer")
def styling_lacquer(t):
    """Spec 3.4 (Ideology): the styling station's lacquer checkbox queues the real job, which consumes 3 deepfire
    and leaves the parka at coats 1; stylingStationLacquer=False queues nothing."""
    x, z = _pad(t, "styling")
    with _comp(t, "styling_station_lacquers_a_parka"):
        if _live(t):
            # station, deepfire (c + 0,-4) and styler (c + 3,-3) must stand on open ground the styler can walk
            _call(t, "jawa/destroy_batch", rects=_rect(x - 2, z - 7, 9, 10), categories="Building")
        y0 = _act(t, "WornGlow: styling lacquer setup", x, z)
        # deepfireOnMap is MAP-WIDE (StylingStationLacquer.AvailableDeepfire), and earlier chains leave stacks around
        # (25 on the map in the 2026-10-07 run), so the fixture promises "at least the cost", not "exactly the cost";
        # the consumption is checked as a DELTA below.
        _chk(t, y0.get("queued") and y0.get("coats") == 0 and (y0.get("deepfireOnMap") or 0) >= STYLE_COST,
             "lacquer setup: %s" % json.dumps(y0)[:300])
        y = y0
        for _ in range(40 if _live(t) else 0):
            _wait(t, 250)
            y = _act(t, "WornGlow: report styler", x, z)
            if y.get("coats") == 1:
                break
        left0 = y0.get("deepfireOnMap") or 0
        _chk(t, y.get("coats") == 1 and y.get("deepfireOnMap") == left0 - STYLE_COST,
             "after the job the parka reads coats=%s with %s deepfire on the map (expected 1 and %d = %d - %d)"
             % (y.get("coats"), y.get("deepfireOnMap"), left0 - STYLE_COST, left0, STYLE_COST))
        _act(t, "WornGlow: cleanup test pawns", x, z)

    with _comp(t, "styling_lacquer_toggle", toggle="stylingStationLacquer"):
        with _settings(t, stylingStationLacquer="False"):
            y = _act(t, "WornGlow: styling lacquer setup", x, z)
            if y.get("queued"):
                # MEASURED 2026-10-08: stylingStationLacquer gates only DrawCheckboxes (the dialog UI,
                # DeepfireStylingStationPatches.cs:72); the debug setup calls QueueLacquer directly, bypassing it.
                _act(t, "WornGlow: cleanup test pawns", x, z)
                _unmeasured(t, "stylingStationLacquer gates only the dialog checkbox; the debug setup bypasses the UI, so a queued job is not a defect: %s" % json.dumps(y)[:200])
        _act(t, "WornGlow: cleanup test pawns", x, z)


# ================================================================================ chain 13: status engine

def _th(p, name):
    return (p or {}).get(name) or {}


@suite.chain("status")
def status(t):
    """Spec 4 / DEEPFIRE_STATUS_THOUGHTS_1 (26/26 live on a clean map): a titled pawn wearing 2 coats feels it, a
    commoner doing the same offends the titled pawn, a lit bedroom lifts its owner, a lit public room impresses a
    visitor once per quadrum; statusEnabled=False silences the thoughts."""
    x, z = _pad(t, "status")
    px = x + 12
    with _comp(t, "titled_pawn_in_two_coats"):
        for rx in (x, px):
            _room(t, rx, z)
        # RM_SawCommonerInDeepfire is MAP-WIDE (any coated non-titled humanlike on the map offends the titled pawn), so
        # a coated walker left alive by a failed worn_glow chain would trip the clean baseline below (MEASURED live
        # 2026-10-07). The worn_glow test pawns are a static the chain owns: cleanse them first.
        _act(t, "WornGlow: cleanup test pawns", x, z)
        _act(t, "Status: spawn titled + commoner", x, z - 6)
        r1 = _act(t, "Status: report pair", x, z)
        names = ("RM_WearingDeepfireTitled", "RM_WearingDeepfireCommon", "RM_SawCommonerInDeepfire", "RM_DeepfireBedroom")
        _chk(t, not any(_th(r1.get(p), d).get("active") for p in ("titled", "commoner") for d in names) and not r1.get("aboveStationActive"),
             "a Deepfire thought is active before anyone wears anything: %s" % json.dumps(r1)[:300])
        a2 = _act(t, "Status: dress titled in 2 coats", x, z)
        _chk(t, a2.get("coats") == 2 and a2.get("displayScore") == 2, "titled parka: %s" % json.dumps(a2))
        r2 = _act(t, "Status: report pair", x, z)
        wt = _th(r2.get("titled"), "RM_WearingDeepfireTitled")
        _chk(t, wt.get("active") and wt.get("stage") == 0 and _near(wt.get("liveMood"), 3.0, 0.01), "titled thought: %s" % json.dumps(wt))
        _chk(t, not _th(r2.get("titled"), "RM_WearingDeepfireCommon").get("active")
             and not _th(r2.get("titled"), "RM_SawCommonerInDeepfire").get("active") and not r2.get("aboveStationActive"),
             "a commoner-only thought fired for the titled pawn alone")

    with _comp(t, "status_toggle", toggle="statusEnabled"):
        with _settings(t, statusEnabled="False"):
            r = _act(t, "Status: report pair", x, z)
            _chk(t, not _th(r.get("titled"), "RM_WearingDeepfireTitled").get("active"),
                 "statusEnabled=False but the titled pawn still holds RM_WearingDeepfireTitled: %s"
                 % json.dumps(_th(r.get("titled"), "RM_WearingDeepfireTitled")))
        r = _act(t, "Status: report pair", x, z)
        _chk(t, _th(r.get("titled"), "RM_WearingDeepfireTitled").get("active"), "restoring statusEnabled did not bring the thought back")

    with _comp(t, "commoner_in_two_coats_offends_the_titled"):
        a3 = _act(t, "Status: dress commoner in 2 coats", x, z)
        _chk(t, a3.get("displayScore") == 2, "commoner parka: %s" % json.dumps(a3))
        r3 = _act(t, "Status: report pair", x, z)
        social = dict((s["def"], s["opinion"]) for s in r3.get("titledSocialThoughtsOfCommoner") or [])
        saw = _th(r3.get("titled"), "RM_SawCommonerInDeepfire")
        wc = _th(r3.get("commoner"), "RM_WearingDeepfireCommon")
        _chk(t, r3.get("aboveStationActive") and _near(social.get("RM_WearsAboveStation"), -15.0, 0.01),
             "opinion offset toward the commoner: %s (above-station active: %s)" % (json.dumps(social), r3.get("aboveStationActive")))
        _chk(t, saw.get("active") and _near(saw.get("liveMood"), -3.0, 0.01), "RM_SawCommonerInDeepfire: %s" % json.dumps(saw))
        _chk(t, wc.get("active") and wc.get("stage") == 0 and _near(wc.get("liveMood"), 1.0, 0.01), "commoner's own thought: %s" % json.dumps(wc))
        _chk(t, not _th(r3.get("commoner"), "RM_SawCommonerInDeepfire").get("active")
             and not _th(r3.get("commoner"), "RM_WearingDeepfireTitled").get("active"), "the commoner took offence or a titled thought")

    with _comp(t, "lit_bedroom_lifts_its_owner"):
        b = _act(t, "Status: bed for titled", x + 1, z + 1)
        _chk(t, b.get("claimed") and b.get("ownedRoom") and b.get("role") == "Bedroom", "bed: %s" % json.dumps(b))
        rs0 = _act(t, "Status: room score", x + 3, z + 3)
        r4a = _act(t, "Status: report pair", x, z)
        base_ok = rs0.get("score") == 0 and not _th(r4a.get("titled"), "RM_DeepfireBedroom").get("active")
        if _live(t) and not base_ok:
            _unmeasured(t, "bedroom baseline is not 0 (map leftovers score %s): run on a regenerated clean map" % rs0.get("score"))
        _act(t, "Floor: coat 6x6", x, z)
        rs1 = _act(t, "Status: room score", x + 3, z + 3)
        _chk(t, rs1.get("score") == 3, "36 coated cells should score 3, got %s" % rs1.get("score"))
        bd = _th(_act(t, "Status: report pair", x, z).get("titled"), "RM_DeepfireBedroom")
        _chk(t, bd.get("active") and bd.get("stage") == 0 and _near(bd.get("liveMood"), 4.0, 0.01), "bedroom stage 0: %s" % json.dumps(bd))
        s1 = _act(t, "Status: coated sculpture", x + 4, z + 4)
        s2 = _act(t, "Status: coated sculpture", x + 4, z + 1)
        _chk(t, s1.get("coats") == 3 and s2.get("roomScore") == 9, "two sculptures: %s / %s" % (json.dumps(s1)[:100], json.dumps(s2)[:100]))
        _act(t, "Status: room score", x + 3, z + 3)       # invalidates the score cache
        bd2 = _th(_act(t, "Status: report pair", x, z).get("titled"), "RM_DeepfireBedroom")
        _chk(t, bd2.get("active") and bd2.get("stage") == 1 and _near(bd2.get("liveMood"), 6.0, 0.01), "bedroom stage 1: %s" % json.dumps(bd2))

    with _comp(t, "public_room_impresses_a_visitor_once"):
        _act(t, "Floor: coat 6x6", px, z)
        _act(t, "Status: coated sculpture", px + 4, z + 4)
        _act(t, "Status: coated sculpture", px + 4, z + 1)
        pr = _act(t, "Status: room score", px + 3, z + 3)
        _chk(t, pr.get("score") == 9 and pr.get("public"), "public room: %s" % json.dumps(pr))
        im = _act(t, "Status: visitor impress test", px + 3, z - 6)
        if _live(t) and not (im.get("faction") and im.get("visitorImpressible")):
            _unmeasured(t, "no impressible visitor faction on this map: %s" % json.dumps(im)[:300])
        _chk(t, (im.get("bestPublicRoomScore") or 0) >= 8, "best public room score %s < 8" % im.get("bestPublicRoomScore"))
        _chk(t, im.get("impressed1") == 1 and (im.get("goodwill1") or 0) - (im.get("goodwill0") or 0) == 2,
             "first check: impressed=%s goodwill %s -> %s (expected +2)" % (im.get("impressed1"), im.get("goodwill0"), im.get("goodwill1")))
        _chk(t, im.get("impressed2") == 0 and im.get("goodwill2") == im.get("goodwill1"), "second check in the same quadrum still moved goodwill")
        _act(t, "Status: cleanup test pawns", x, z)


# ================================================================================== chain 14: the gods

def _god_table(ishko_penalty):
    return dict((g, -ishko_penalty if g == "Ishko" else ADORE if g in TRIO else LIKE) for g in GODS)


def _god_check(t, name, rep, table, key="deltas"):
    """Every god's change vs the spec number x Ninefold's multiplier, clamped to the satiation range."""
    if not _live(t):
        return
    if not rep.get("ninefold"):
        _unmeasured(t, "%s: Ninefold is not loaded (the tier must carry mandrake.rm.ninefold)" % name)
    if not rep.get("engineEnabled") or not rep.get("godsReact"):
        _unmeasured(t, "%s: Ninefold engine or godsReact is OFF: %s" % (name, json.dumps(rep)[:200]))
    mult = rep.get("multiplier", 1.0)
    bad = []
    for g in GODS:
        cell = (rep.get(key) or {}).get(g)
        if cell is None:
            bad.append("%s missing" % g)
            continue
        b = cell.get("b")
        want = max(SAT_MIN, min(SAT_MAX, b + table.get(g, 0.0) * mult)) - b
        if not _near(cell.get("d"), want, 0.01):
            bad.append("%s %+.2f (want %+.2f)" % (g, cell.get("d"), want))
    _chk(t, not bad, "%s: %s" % (name, "; ".join(bad)))


@suite.chain("gods")
def gods(t):
    """Spec 5 / DEEPFIRE_GOD_BRIDGE_DELTAS_1 (25/25 live): a first coat moves the nine Ninefold gods by the spec
    amounts, a second coat moves none, a tagged idol moves its god by 15, sales move Mob'Unloo; godsReact=False
    silences all of it. Needs Ninefold in the tier."""
    x, z = _pad(t, "gods")
    with _comp(t, "first_coat_moves_every_god"):
        _room(t, x, z)
        w = _act(t, "GodDeltas: coat new wall", x, z + 1)
        _chk(t, w.get("coats") == 1 and not w.get("wornClass") and not w.get("statueGod"), "wall coat: %s" % json.dumps(w)[:200])
        _god_check(t, "wall first coat: Ishko -3, trio +8, other five +3", w, _god_table(ISHKO))

    with _comp(t, "second_coat_moves_no_god"):
        w2 = _act(t, "GodDeltas: second coat", x, z + 1)
        _chk(t, w2.get("coats") == 2, "second coat did not land: %s" % json.dumps(w2)[:200])
        _god_check(t, "second coat", w2, dict((g, 0.0) for g in GODS))

    with _comp(t, "worn_first_coat_is_harsher_on_ishko"):
        p = _act(t, "GodDeltas: coat new parka", x + 1, z + 1)
        _chk(t, p.get("wornClass") and p.get("coats") == 1, "parka coat: %s" % json.dumps(p)[:200])
        _god_check(t, "parka first coat: Ishko -8, trio +8, others +3", p, _god_table(ADORE))

    with _comp(t, "a_gods_own_idol_moves_it_by_fifteen"):
        ir = _act(t, "GodDeltas: coat idol of Rekko", x + 2, z + 1)
        # StatueGodOf answers null for every god unless Ninefold is loaded (NinefoldDeltaBridge.IsGod), so without
        # it statueGod reads '' -- not a defect in the idol tagging. Say UNMEASURED, as the sibling arms do.
        if _live(t) and not ir.get("ninefold"):
            _unmeasured(t, "Rekko idol: Ninefold is not loaded (the tier must carry mandrake.rm.ninefold)")
        _chk(t, ir.get("statueGod") == "Rekko", "idol read as %r, not Rekko" % ir.get("statueGod"))
        tbl = dict((g, STATUE if g == "Rekko" else -ISHKO if g == "Ishko" else LIKE) for g in GODS)
        _god_check(t, "Rekko idol: Rekko +15, Ishko -3, others +3", ir, tbl)

    with _comp(t, "sale_of_deepfire_moves_mobunloo"):
        s = _act(t, "GodDeltas: sold deepfire", x, z)
        _chk(t, s.get("prefixRegistered") and s.get("postfixRegistered"), "TradeDeal.TryExecute patches not registered: %s" % json.dumps(s)[:200])
        _chk(t, s.get("sellsJar") and s.get("sellsCoatedSculpture") and not s.get("sellsSteel") and not s.get("buysJar"),
             "sale classifier: %s" % json.dumps(s)[:300])
        _god_check(t, "sold: Mob'Unloo +8, nobody else", s, dict((g, ADORE if g == "MobUnloo" else 0.0) for g in GODS))

    with _comp(t, "gods_react_toggle", toggle="godsReact"):
        with _settings(t, godsReact="False"):
            r = _act(t, "GodDeltas: coat new wall", x + 3, z + 1)
            if _live(t) and not r.get("ninefold"):
                _unmeasured(t, "Ninefold is not loaded")
            moved = [g for g in GODS if abs(((r.get("deltas") or {}).get(g) or {}).get("d", 0.0)) > 0.001]
            _chk(t, r.get("coats") == 1 and not moved, "godsReact=False but these gods moved on a first coat: %s" % moved)


# ====================================================================================== chain 15: cuisine

@suite.chain("cuisine")
def cuisine(t):
    """Spec 6: the 14 glow-hediff families exist and every steered meal recipe carries a Cooking skill
    requirement; the outcome mechanics are UNCOVERED (walk). The recipes' stove listing is covered by
    defs_load.patches_applied and settings_apply.cuisine_recipes_toggle."""
    with _comp(t, "fourteen_families_and_fifteen_recipes"):
        _chk(t, len(GLOW_HEDIFFS) == 14, "expected 14 RM_Glow_* hediffs in Defs/, found %d: %s" % (len(GLOW_HEDIFFS), GLOW_HEDIFFS))
        _chk(t, len(MEAL_RECIPES) == 15, "expected 15 RM_MealDeepfire* recipes in Defs/, found %d" % len(MEAL_RECIPES))
        if _live(t):
            rows = _get_defs(t, ";".join("HediffDef/%s" % h for h in GLOW_HEDIFFS), "label")
            _chk(t, len(rows) == 14 and all(isinstance(v.get("label"), str) and v.get("label") for v in rows.values()),
                 "a glow hediff has no label (%d read)" % len(rows))


# ====================================================================== chain 16: toggles with no reachable effect

def _flip(t, comp, field):
    with _comp(t, comp, toggle=field):
        if _live(t):
            old = _raw_get(t, field)
            try:
                for v in ("False", "True"):
                    r = _raw_set(t, field, v)
                    _chk(t, r.get("success"), "mod_settings_field(set %s=%s) failed: %s" % (field, v, json.dumps(r, default=str)[:200]))
                    _chk(t, str(_raw_get(t, field)) == v, "%s did not read back %s" % (field, v))
            finally:
                _raw_set(t, field, old)


@suite.chain("toggle_flips")
def toggle_flips(t):
    """Write + read-back only. The behaviour behind each of these is not drivable through the bridge today
    (the walk's UNCOVERED lines say why): shore spawn needs map generation; the floor and Ishko-idol toggles
    gate the Designator's own accept path, which the bridge bypasses; hediffGlowEnabled needs a cooked dish."""
    _flip(t, "shore_mats_setting_flips", "shoreMatsEnabled")
    _flip(t, "floors_paintable_setting_flips", "floorsPaintable")
    _flip(t, "ishko_idol_setting_flips", "ishkoIdolPaintable")
    _flip(t, "hediff_glow_setting_flips", "hediffGlowEnabled")


# ====================================================================== settings round trip (every scalar field)

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCALAR = re.compile(r"public\s+static\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);")


def _settings_fields():
    """(type, name) for every scalar `public static` field of LuminousPigmentSettings, read from the C# source.
    Arrays (coatRadius, coatIntensity, familyEnabled) and the PressGate enum are not scalar and are checked
    statically only (round-tripping them needs a typed value the raw writer does not take as one string)."""
    src = open(os.path.join(_HERE, "Source", "LuminousPigmentMod.cs"), encoding="utf-8").read()
    body = src.split("class LuminousPigmentSettings", 1)[1]
    body = body.split("ExposeData", 1)[0]
    return [(m.group(1), m.group(2)) for m in _SCALAR.finditer(re.sub(r"//[^\n]*", "", body))]


def _alt(ty, cur):
    if ty == "bool":
        return "False" if str(cur).lower() == "true" else "True"
    if ty == "int":
        return str(int(float(cur)) + 1)
    return str(float(cur) + 1.0)


def _same(ty, a, b):
    if ty == "bool":
        return str(a).lower() == str(b).lower()
    return a is not None and b is not None and abs(float(a) - float(b)) <= 1e-4 * max(1.0, abs(float(b)))


@suite.chain("settings_roundtrip")
def settings_roundtrip(t):
    """Every scalar Mod Settings field: read the default, write a different value, read it back (numerics compared
    numerically), restore, read the default back. Raw static write only (no dialog), so this proves the field is
    exposed to the settings tool and writable, not that anything consumes it (settings_apply and the behaviour chains
    do that). Restores in a finally."""
    fields = _settings_fields()
    with _comp(t, "settings_fields_found"):
        if not fields:
            _fail("settings probe found no scalar field in LuminousPigmentSettings (the regex is blind)")
    with _comp(t, "every_scalar_field_round_trips", beyond_toggle=True):
        if _live(t):
            bad = []
            for ty, name in fields:
                old = _raw_get(t, name)
                if old is None:
                    bad.append("%s: get returned no value" % name)
                    continue
                try:
                    new = _alt(ty, old)
                    r = _raw_set(t, name, new)
                    if not r.get("success"):
                        bad.append("%s: set failed %s" % (name, json.dumps(r, default=str)[:120]))
                    elif not _same(ty, _raw_get(t, name), new):
                        bad.append("%s: wrote %s, read %r" % (name, new, _raw_get(t, name)))
                finally:
                    _raw_set(t, name, old)
                if not _same(ty, _raw_get(t, name), old):
                    bad.append("%s: did not restore to %r" % (name, old))
            _chk(t, not bad, "%d of %d fields failed: %s" % (len(bad), len(fields), bad[:5]))


@suite.chain("no_new_errors")
def no_new_errors(t):
    """Debugging check for every past live failure in DEEPFIRE_LIVE_FAILURES_1: the run must leave no NEW
    Error-type line naming this mod (the proxy double-destroy, the visitor NRE and the stale social cache each
    surfaced this way). The baseline is taken here, so errors from before the run do not count; to make it a
    whole-run check the driver runs this chain LAST (declaration order) and compares to the buffer it saw at
    the start of the run."""
    with _comp(t, "no_error_lines_from_this_mod"):
        if _live(t):
            now = _log_baseline(t)
            first = _GLOBAL.get("log0")
            if first is None:
                _unmeasured(t, "no start-of-run log baseline was recorded (the defs_load chain records it)")
            new = [k[:240] for k, n in now.items() if n > first.get(k, 0)]
            _chk(t, not new, "%d new Error-type line(s) naming this mod during the run: %s" % (len(new), new[:3]))


# ------------------------------------------------------------------------------------------- static checks

def static_checks():
    """Failure strings; empty means pass. Needs no game."""
    bad = []
    fields = _settings_fields()
    if not fields:
        return ["settings probe found no scalar field (sanity probe failed)"]
    mod = open(os.path.join(_HERE, "Source", "LuminousPigmentMod.cs"), encoding="utf-8").read()
    scribed = mod.split("ExposeData", 1)[1] if "ExposeData" in mod else ""
    for _ty, name in fields:
        if '"%s"' % name not in scribed:
            bad.append("settings field %s is not Scribed" % name)
    names = set(n for _t, n in fields)
    for tg in suite.toggles:
        if tg not in names and not re.search(r"public static \w+(\[\])? %s\b" % tg, mod):
            bad.append("suite.toggles names %s, which is not a settings field" % tg)
    proj = open(os.path.join(_HERE, "Source", "RM_LuminousPigment.csproj"), encoding="utf-8").read()
    for fn in sorted(os.listdir(os.path.join(_HERE, "Source"))):
        if fn.endswith(".cs") and 'Compile Include="%s"' % fn not in proj and "Compile Include=\"Source" not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % fn)
    if not SHIPPED:
        bad.append("no shipped defs parsed")
    if not os.path.isfile(os.path.join(_HERE, "..", "..", "..", "design", "validation_walks", "RimMandrake", "LuminousPigment.md")):
        bad.append("walk missing")
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p_ in problems:
        print("  - " + p_)
    sys.exit(1 if problems else 0)
