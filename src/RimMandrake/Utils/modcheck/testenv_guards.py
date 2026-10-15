"""modcheck.testenv_guards -- test-environment guards from live rounds 5 and 6 (2026-10-15), shared by every harness.

1. FOG TRIGGERS (TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL). Vanilla arms ancient-danger rooms with ethereal trigger
   things: TriggerUnfogged sends its signal the first tick its cell is unfogged after having been fogged
   (Verse/TriggerUnfogged.cs), RectTrigger/RadialTrigger when a colonist comes near, and the SignalAction_* things answer
   that signal (Ambush spawns attackers, DormancyWakeUp wakes sleeping mechs, Infestation, OpenCasket...). A test that
   reveals fog over its site (validation_core.reveal: a colonist's sight) fires them, and the wave lands mid-row.
   Separately, FloodFillerFog.FloodUnfog sets mindState.Active=true on every pawn it uncovers and sends the ThreatBig
   "Area revealed" letter when one is a mechanoid -- so sleeping hostile PAWNS must be gone before any reveal too
   (helpers.kill_hostiles / destroy_bulk nonColonists do that; this module removes the triggers).
   disarm_fog_triggers() lists every trigger/signal-action thing and vanishes it (DestroyMode.Vanish never Activates it),
   then READS BACK. A row about ancient dangers must not use it.

2. HEAT (TESTENV_SITE_HEAT_HARDEN_COOKS_BY_ROW3). On a 56-58 C Pyrelands site vanilla HediffGiver_Heat builds Heatstroke
   on colonists until they drop (0.65, downed, 2026-10-15) inside a row that measures fruit rot. The site is the subject
   and is never cooled; the guard only takes the vanilla Heatstroke hediff off SUPPORT colonists at bounded intervals, in
   rows whose topic is not health/needs/damage/death/heat (owner 2026-10-13 by card: support colonists may be protected
   only there). heat_steps() splits a long wait so no colonist carries more than HEAT_CHUNK_TICKS of exposure, and
   heatstroke_gain() is the vanilla formula so the chunk is checked offline against the hottest site measured.

3. FOG BLOCKERS (TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL residual, r6 map 3). With the triggers gone and every spawned
   hostile vanished, a ThreatBig "Area revealed" letter still came 32 ticks after the noon pin, inside the matrix block.
   In 1.6 only FogGrid.FloodUnfogAdjacent(sendLetters) sends that letter, and mid-run its one caller is
   Building.DeSpawn -> FogGrid.Notify_FogBlockerRemoved: a fog-making edifice (rock, wall) removed next to unfogged ground
   floods into the fogged pocket behind it, wakes every pawn there and letters on a mechanoid. A site clear
   (destroy_batch All) removes exactly such edifices. A colonist's sight and a door send no letter. clear_map_fog() unfogs
   the WHOLE map once the hostile sweep has read back empty, so no later fog-blocker removal has a fogged pocket to flood.

4. STORM TAIL (TESTENV_STORM_FIRES_HARDEN_DECOY_BURN). Unlocking a DryThunderstorm leaves it the CURRENT weather, and even a
   transition to Clear keeps WeatherManager.lastWeather ticking (lightning included) for TransitionTicks 4000 at a falling
   weight (RimWorld/WeatherManager.WeatherManagerTick). calm_sky() locks Clear and transitions to Clear a second time
   (lastWeather becomes Clear: no storm tail), puts out every fire and reads back that no stray Fire is left.

5. EXPECTED DISTURBANCE (TESTENV_SWEPT_BRUISE_HARDEN_OWN_HAZARD). expected_hurt() builds a vitals-trigger predicate for
   clockgate.expected_disturbance(): a 'hurt' trigger on one of the row's own staged subjects whose newest hediff is the
   one the mod under test is designed to inflict. Everything else still stops the clock.

`session` is anything with call(tool, **params) -> dict (rimdrive Session, validation_core bridge, a fake).
"""
import re

# ------------------------------------------------------------------ 1. fog triggers
# Core ThingDefs (Defs/Core/ThingDefs_Misc/Ethereal_Various.xml, Ethereal_SignalActions.xml; rimsage 1.6 index 2026-10-15).
TRIGGER_DEFS = ("TriggerUnfogged", "RectTrigger", "RadialTrigger", "TriggerContainerEmptied")
SIGNAL_ACTION_DEFS = ("SignalAction_Ambush", "SignalAction_DormancyWakeUp", "SignalAction_Infestation",
                      "SignalAction_Incident", "SignalAction_OpenCasket", "SignalAction_StartWick",
                      "SignalAction_OpenDoor", "SignalAction_Letter", "SignalAction_Message",
                      "SignalAction_SoundOneShot", "SignalAction_Delay")
FOG_TRIGGER_DEFS = TRIGGER_DEFS + SIGNAL_ACTION_DEFS
LIST_LIMIT = 2000


def _ok(r):
    return isinstance(r, dict) and r.get("success") is not False


def _list_triggers(session):
    """-> (rows, error). rows: [{"id", "def", "x", "z"}] for spawned trigger things; error is None or the reason the
    listing cannot be trusted (failed, or truncated: a partial list must never read as 'all gone')."""
    r = session.call("jawa/list_things", defName=",".join(FOG_TRIGGER_DEFS), limit=LIST_LIMIT)
    if not _ok(r) or not isinstance(r.get("things"), list):
        return [], "list_things failed: %s" % (str(r)[:200],)
    if r.get("isCompleteList") is False or (r.get("countMatched") or 0) > len(r["things"]):
        return [], "list_things truncated (%s matched, %d returned)" % (r.get("countMatched"), len(r["things"]))
    rows = [{"id": t.get("id"), "def": t.get("def"), "x": t.get("x"), "z": t.get("z")}
            for t in r["things"] if t.get("x") is not None and t.get("z") is not None]
    return rows, None


def disarm_fog_triggers(session):
    """Vanish every fog/proximity trigger and signal-action thing on the current map, then read back.
    -> {"found": n, "byDef": {def: n}, "destroyed": n, "left": n|None, "verified": bool, "error": str|None}.
    verified=False means the map is not SHOWN disarmed: a gate that needs it (proof_all P3) refuses; `left` > 0 means a
    trigger read back armed (validation_core.prepare_site then records its site UNMEASURED/SITE)."""
    out = {"found": 0, "byDef": {}, "destroyed": 0, "left": None, "verified": False, "error": None}
    rows, err = _list_triggers(session)
    if err:
        out["error"] = err
        return out
    out["found"] = len(rows)
    for t in rows:
        out["byDef"][t["def"]] = out["byDef"].get(t["def"], 0) + 1
    if rows:
        cells = sorted({(int(t["x"]), int(t["z"])) for t in rows})
        # Ethereal is the triggers' ThingCategory; destroy_batch skips pawns and only touches that category in these cells
        # (any other ethereal thing sharing a trigger's cell goes too -- acceptable on a test map, and never a pawn)
        r = session.call("jawa/destroy_batch", rects=";".join("%d,%d,1,1" % c for c in cells), categories="Ethereal")
        if not _ok(r):
            out["error"] = "destroy_batch failed: %s" % (str(r)[:200],)
        out["destroyed"] = int((r or {}).get("destroyed") or 0) if isinstance(r, dict) else 0
    left, err2 = _list_triggers(session)
    if err2:
        out["error"] = out["error"] or ("read-back " + err2)
        return out
    out["left"] = len(left)
    out["verified"] = not left and out["error"] is None
    if left:
        out["leftDefs"] = sorted({t["def"] for t in left})
    return out


# ------------------------------------------------------------------ 2. heat
# Verse/HediffGiver_Heat.OnIntervalPassed (rimsage 1.6, read 2026-10-15): above SafeTemperatureRange.max the severity
# rises by max(curve(overage) * 6.45e-5, 0.000375) per interval; HediffGivers run every 60 ticks.
HEAT_CURVE = ((0.0, 0.0), (25.0, 25.0), (50.0, 40.0), (100.0, 60.0), (200.0, 80.0), (400.0, 100.0), (4000.0, 1000.0))
HEAT_RATE = 6.45e-05
HEAT_MIN_STEP = 0.000375
HEAT_INTERVAL_TICKS = 60
# Worst case: a naked baseliner (ComfyTemperatureMax 26 + the 10 C safe margin); clothing only raises it.
SAFE_MAX_WORST_C = 36.0
HEATSTROKE_MODERATE = 0.20          # Heatstroke stage that still leaves a pawn on its feet with margin (extreme 0.62 downs)
HOTTEST_SITE_C = 65.0               # r5 measured 56.7 (r6) and 58.3 (r7); 65 leaves margin for a hotter fresh tile
HEAT_CHUNK_TICKS = 6000             # exposure carried between two guard passes (selftest: gain at HOTTEST_SITE_C < moderate)
HEATSTROKE_DEF = "Heatstroke"
# Rows whose topic forbids the guard (owner 2026-10-13 by card) -- heat is added because Heatstroke IS that topic.
HEAT_GUARD_REFUSED_TOPICS = frozenset(["health", "needs", "damage", "death", "heat"])


def _curve(x):
    pts = HEAT_CURVE
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def heatstroke_gain(ticks, ambient_c, safe_max_c=SAFE_MAX_WORST_C):
    """Pure: Heatstroke severity vanilla adds over `ticks` at a steady `ambient_c` (0 at or below the safe max)."""
    if ambient_c <= safe_max_c:
        return 0.0
    per = max(_curve(ambient_c - safe_max_c) * HEAT_RATE, HEAT_MIN_STEP)
    return per * (int(ticks) // HEAT_INTERVAL_TICKS)


def heat_steps(n, carried=0, chunk=HEAT_CHUNK_TICKS):
    """Pure: split an n-tick wait so exposure since the last guard pass never exceeds `chunk`.
    -> [(ticks, guard_after), ...]; sum(ticks) == n. `carried` = ticks already waited since the last pass."""
    if chunk <= 0:
        raise ValueError("chunk must be positive")
    steps, left, have = [], int(n), max(0, int(carried))
    if have >= chunk and left > 0:
        steps.append((0, True))
        have = 0
    while left > 0:
        step = min(left, chunk - have)
        left -= step
        have += step
        full = have >= chunk
        steps.append((step, full))
        if full:
            have = 0
    return steps


def clear_heatstroke(session, keep_ids=()):
    """Remove vanilla Heatstroke from every living humanlike PLAYER pawn not in keep_ids, recording the severity each had
    BEFORE the repair. -> {"cleared": [(id, severity)], "failed": [(id, msg)], "read": bool}. Never raises."""
    out = {"cleared": [], "failed": [], "read": False}
    try:
        r = session.call("jawa/list_pawns", faction="player", includeHealth=True, limit=100)
    except Exception as e:  # noqa: BLE001 - a guard pass is never a crash
        out["failed"].append((None, "list_pawns raised %s" % type(e).__name__))
        return out
    if not _ok(r) or not isinstance(r.get("pawns"), list):
        out["failed"].append((None, "list_pawns failed: %s" % (str(r)[:160],)))
        return out
    out["read"] = True
    keep = set(keep_ids or ())
    for p in r["pawns"]:
        pid = p.get("id")
        if not pid or pid in keep or p.get("dead") or p.get("intelligence") not in (None, "Humanlike"):
            continue
        hs = [h for h in ((p.get("health") or {}).get("hediffs") or []) if isinstance(h, dict) and h.get("def") == HEATSTROKE_DEF]
        if not hs:
            continue
        sev = max(float(h.get("severity") or 0.0) for h in hs)
        try:
            rr = session.call("jawa/pawn_health", pawn=pid, action="remove", hediff=HEATSTROKE_DEF)
        except Exception as e:  # noqa: BLE001
            rr = {"success": False, "message": "raised %s" % type(e).__name__}
        if _ok(rr):
            out["cleared"].append((pid, round(sev, 4)))
        else:
            out["failed"].append((pid, str((rr or {}).get("message") or rr)[:160]))
    return out


# ------------------------------------------------------------------ 3. fog blockers
def _hostile_pawns(session):
    """-> (ids, error). Living hostile pawns on the current map, or the reason the listing cannot be trusted."""
    r = session.call("jawa/list_pawns", faction="hostile", limit=200)
    if not _ok(r) or not isinstance(r.get("pawns"), list):
        return None, "list_pawns hostile failed: %s" % (str(r)[:200],)
    return [p.get("id") for p in r["pawns"] if not p.get("dead")], None


def clear_map_fog(session):
    """Unfog the WHOLE current map, but only on a map already swept of hostiles (an unfog wakes every pawn it uncovers:
    Pawn.Notify_Unfogged). -> {"hostilesBefore": [...]|None, "foggedBefore": n|None, "foggedNow": n|None,
    "verified": bool, "error": str|None}. verified=True means no fogged cell is left, so no later fog-blocker removal
    can flood a pocket (no "Area revealed" letter, no woken sleeper). A refused or unread map is never verified."""
    out = {"hostilesBefore": None, "foggedBefore": None, "foggedNow": None, "verified": False, "error": None}
    ids, err = _hostile_pawns(session)
    out["hostilesBefore"] = ids
    if err:
        out["error"] = err
        return out
    if ids:
        out["error"] = "refused: %d hostile pawn(s) still on the map would be woken by the unfog: %s" % (len(ids), ids[:6])
        return out
    r = session.call("jawa/set_fog", action="unfogAll")
    if not _ok(r) or not isinstance(r.get("foggedCellsNow"), int):
        out["error"] = "set_fog unfogAll failed or gave no read-back: %s" % (str(r)[:200],)
        return out
    out["foggedBefore"], out["foggedNow"] = r.get("foggedCellsBefore"), r["foggedCellsNow"]
    out["verified"] = r["foggedCellsNow"] == 0
    if not out["verified"]:
        out["error"] = "%d cell(s) still fogged after unfogAll" % r["foggedCellsNow"]
    return out


# ------------------------------------------------------------------ 4. storm tail
CALM_WEATHER = "Clear"


def calm_sky(session, map_size, settle=None):
    """Lock Clear, transition to Clear AGAIN (so lastWeather is Clear and no storm tail ticks), extinguish the whole map,
    run `settle()` (a short governed wait, or None), then count Fire. -> {"weather": [...], "extinguished": n|None,
    "strayFires": n|None, "verified": bool, "error": str|None}. verified=False when any call failed or a fire is left."""
    w, h = map_size
    out = {"weather": [], "extinguished": None, "strayFires": None, "verified": False, "error": None}
    for kw in ({"weather": CALM_WEATHER, "lockWeather": True}, {"weather": CALM_WEATHER}):
        r = session.call("jawa/weather_set", **kw)
        out["weather"].append({"after": (r or {}).get("after") if isinstance(r, dict) else None, "ok": _ok(r) and r.get("success") is True})
        if not (_ok(r) and r.get("success") is True):
            out["error"] = "weather_set %s refused: %s" % (kw, str(r)[:160])
            return out
    r = session.call("jawa/map_fire", action="extinguish", rect="0,0,%d,%d" % (int(w), int(h)))
    if not _ok(r):
        out["error"] = "map_fire extinguish refused: %s" % (str(r)[:160],)
        return out
    out["extinguished"] = (r or {}).get("firesExtinguished")
    if settle is not None:
        settle()
    lt = session.call("jawa/list_things", defName="Fire", limit=LIST_LIMIT)
    if not _ok(lt) or not isinstance(lt.get("things"), list):
        out["error"] = "list_things Fire failed: %s" % (str(lt)[:160],)
        return out
    n = max(len(lt["things"]), int(lt.get("countMatched") or 0))
    out["strayFires"] = n
    out["verified"] = n == 0
    if n:
        out["error"] = "%d stray Fire still burning after the calm" % n
    return out


# ------------------------------------------------------------------ 5. expected disturbance
def _num_id(x):
    m = re.search(r"(\d+)$", str(x if x is not None else ""))
    return int(m.group(1)) if m else None


def expected_hurt(subject_ids, hediff):
    """Predicate over one jawa/vitals trigger: True only for kind 'hurt' on one of `subject_ids` (ThingIDs like
    'Human460415' or bare numbers) whose newest hediff is `hediff` (the vitals detail reads 'newest hediff <Def>/<Part>').
    Pure. A downed or dead subject is another kind, so it never matches. The id is the trailing digits of a ThingID, so a
    race defName that itself ends in a digit parses to a different number and simply never matches (no resume)."""
    ids = set(n for n in (_num_id(s) for s in subject_ids or ()) if n is not None)
    pat = re.compile(r"newest hediff %s(/|\s|$)" % re.escape(hediff))

    def pred(t):
        return (isinstance(t, dict) and t.get("kind") == "hurt" and _num_id(t.get("subjectId")) in ids
                and bool(pat.search(str(t.get("detail") or ""))))
    return pred
