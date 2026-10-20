"""validation_core.py -- the mod-neutral half of a live bridge validation script (hose port step 2, design FINAL §3.10, G5.1).

Extracted from GimmeSomeSlack/validation.py so a script of another mod (FlowWorks/validation_hose.py) can drive the bridge
without importing Gimme Some Slack's harness. Nothing here names a mod: the probe a Bridge talks to is the `probe_type`
attribute of its subclass, and the mod/package/tier constants live in each script.

    import validation_core as V
    class B(V.Bridge): probe_type = "RimMandrake.FlowWorks.Hose.HoseProbe"

Contents: REPO / UTILS / SAVES / PLAYER_LOG paths; row/hrow (with the SHARED one-session switch a proof driver sets);
_BridgeBase / Bridge (own socket) / SuiteBridge (a modcheck Session); ops/perimeter cell helpers; save helpers
_saves_stat / _wait_saved / _wait_playing.
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = HERE
SAVES = os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "LocalLow", "Ludeon Studios",
                     "RimWorld by Ludeon Studios", "Saves")
PLAYER_LOG = os.path.join(os.path.dirname(SAVES), "Player.log")

if os.path.join(UTILS, "modcheck") not in sys.path:
    sys.path.insert(0, os.path.join(UTILS, "modcheck"))
import preconditions as _PC  # noqa: E402

# PRECONDITIONS (PROOF_VERDICTS_REPAIR_SAME_BUG_EVERY_ROUND): inside `with scope(name):` every refused / non-taking bridge
# reply, every dead probe read and every failed require() withholds the PASS/FAIL of each row emitted later in that scope
# (row() reads UNMEASURED, the faults attached). A call whose reply IS the measured answer passes `_answer=True`. No scope
# open: nothing changes (validation_hose, proof_all and the other users that never open one). See modcheck/preconditions.py.
PRE = _PC.Preconditions()
scope = PRE.scope
require = PRE.require
adopt = PRE.adopt
quiet = PRE.quiet

# SHARED (set by a proof driver): one session, one map. A harness/site row is then written only when it is NOT PASS (a
# fault still surfaces under its own id; a green one becomes a site note).
SHARED = False
SITE_NOTES = []


class Row(dict):
    pass


def row(rows, rid, status, cls, detail):
    status, cls, detail = PRE.judge(status, cls, detail)
    rows.append({"id": rid, "status": status, "class": cls, "detail": detail})
    print("%-28s %-9s %s" % (rid, status, str(detail)[:150]), flush=True)


def hrow(rows, rid, status, cls, detail):
    """A harness/site row: a row of its own standalone; in SHARED mode only when it is not PASS."""
    if SHARED and status == "PASS":
        SITE_NOTES.append({"id": rid, "detail": detail})
        return
    row(rows, rid, status, cls, detail)


class _BridgeBase(object):
    """call / probe / ticks over a raw transport (`_raw`): the standalone socket or the suite's Session. `probe` talks to
    the static request/result/serial fields of the type named by the subclass's `probe_type`."""
    probe_type = None

    def _raw(self, tool, kw):
        raise NotImplementedError

    def call(self, tool, _answer=False, **kw):
        """One bridge call. `_answer` is the Guarded proxy's flag (see guard()); it is dropped here, never sent to the game."""
        r = self._raw(tool, kw) or {}
        tap_after(tool)
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:  # noqa: BLE001
                pass
        return r if isinstance(r, dict) else {"success": False, "raw": r}

    def probe_of(self, probe_type, cmd, wait_s=20.0, poll_s=0.3):
        before = self.call("jawa/mod_settings_field", typeName=probe_type, action="get", field="serial").get("value")
        s = self.call("jawa/mod_settings_field", typeName=probe_type, action="set", field="request", value=cmd)
        if not s.get("success"):
            return {"success": False, "error": "probe set failed", "raw": s}
        t0 = time.time()
        while time.time() - t0 < wait_s:
            now = self.call("jawa/mod_settings_field", typeName=probe_type, action="get", field="serial").get("value")
            if now != before:
                res = self.call("jawa/mod_settings_field", typeName=probe_type, action="get", field="result").get("value")
                try:
                    return json.loads(res)
                except Exception:  # noqa: BLE001
                    return {"success": False, "raw": res}
            time.sleep(poll_s)
        return {"success": False, "error": "probe timed out (no frame serviced it)"}

    def probe(self, cmd, wait_s=20.0):
        if not self.probe_type:
            return {"success": False, "error": "no probe_type on this bridge class"}
        return self.probe_of(self.probe_type, cmd, wait_s)

    def ticks(self, n):
        """Game time in governed chunks (WATCH_WAIT_WIRE_SMALL_STEPS): jawa/safe_advance when present, stopped by the
        vitals latch (raises clockgate.GovernorStop); the legacy rimworld/step_game_ticks otherwise.

        TESTENV_GOVERNOR_STOP_SITE_NOT_MOD (2026-10-19): a stop whose cause is a NON-MOD disturbance (a wild/entity hostile
        arriving, a colonist bruised by a pawn in a fight) is a SITE event: it is recorded in SITE_NOTES, the intruder is
        removed / the fight ended / the wound healed (site_recover), and the remaining ticks run. Anything else (a death, a
        downed colonist, a modal, a hurt with no pawn source -- the mod's own damage) still raises, as does a stop whose
        recovery could not be read back, or the SITE_RECOVER_MAX-th recovery of the session."""
        cg = _clockgate()
        left, done = int(n), 0
        while left > 0:
            req = min(left, cg.SAFE_CHUNK_MAX)
            try:
                ex = cg.advance_chunk(self, req)
            except cg.GovernorStop as g:
                with PRE.quiet():
                    took = site_recover(self, g.result)
                if took is None:
                    raise
                ex = min(req, took)
                left -= ex
                done += ex
                continue
            done += req if ex is None else int(ex)
            left -= req
        return {"success": True, "advanced": done}


def _clockgate():
    d = os.path.join(UTILS, "modcheck")
    if d not in sys.path:
        sys.path.insert(0, d)
    import clockgate  # noqa: E402
    return clockgate


class Bridge(_BridgeBase):
    """Standalone: its own socket to the bridge."""

    def __init__(self):
        if UTILS not in sys.path:
            sys.path.insert(0, UTILS)
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        self.S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.S.connect()

    def _raw(self, tool, kw):
        return self.S.call(tool, kw, check=False)


class SuiteBridge(_BridgeBase):
    """Suite: calls ride the runner's Session; game time goes through t.wait_ticks (clock-verified)."""

    def __init__(self, t):
        self.t = t

    def _raw(self, tool, kw):
        return self.t.session.call(tool, **kw)

    def ticks(self, n):
        self.t.wait_ticks(n)
        return {"success": True}


def _channel_dead(r):
    """A probe reply that never came from the probe: the request was not taken, no frame serviced it, the result would not parse."""
    if not isinstance(r, dict):
        return True
    err = str(r.get("error") or "")
    return r.get("success") is False and ("timed out" in err or "set failed" in err or "no probe_type" in err
                                          or ("raw" in r and "error" not in r))


class Guarded(object):
    """The one place a scoped proof's bridge replies reach PRE. Wraps ANY bridge object (Bridge, SuiteBridge, a proof's own
    subclass, a selftest's fake): call / hp / probe / probe_of replies are reported, everything else passes through.

    `_answer=True` on a call (or `answer=True` on a probe) marks a reply that IS the measurement -- the mod's own refusal
    under test, an existence check, best-effort cleanup: the caller judges it, it is never a fault. A dead probe channel is
    a fault even then (nothing was asked)."""

    def __init__(self, B):
        self.__dict__["_B"] = B

    def __getattr__(self, k):
        return getattr(self._B, k)

    def __setattr__(self, k, v):
        setattr(self._B, k, v)

    def call(self, tool, _answer=False, **kw):
        try:
            r = self._B.call(tool, **kw)
        except Exception as ex:
            PRE.fault(tool, "raised %r" % ex)
            raise
        return PRE.reply(tool, kw, r, answer=_answer)

    def _probed(self, cmd, r, answer):
        if _channel_dead(r):
            PRE.fault("probe %s" % str(cmd)[:60], str((r or {}).get("error") or "dead probe channel") if isinstance(r, dict) else r)
        elif not answer and r.get("success") is False:
            PRE.fault("probe %s" % str(cmd)[:60], str(r.get("error") or r.get("message") or r)[:200])
        return r if isinstance(r, dict) else {"success": False, "raw": r}

    def hp(self, cmd, wait_s=20.0, answer=False):
        return self._probed(cmd, self._B.hp(cmd, wait_s), answer)

    def probe(self, cmd, wait_s=20.0, answer=False):
        return self._probed(cmd, self._B.probe(cmd, wait_s), answer)

    def probe_of(self, probe_type, cmd, wait_s=20.0, poll_s=0.3, answer=False):
        return self._probed(cmd, self._B.probe_of(probe_type, cmd, wait_s, poll_s), answer)


def guard(B):
    """B wrapped once (idempotent). Every proof that opens a scope() drives the bridge through this."""
    return B if isinstance(B, Guarded) else Guarded(B)


# ------------------------------------------------------------------ site disturbances (not the mod's doing)
SITE_PHASE = ["measure"]          # "prepare" inside prepare_site; recorded on every event so a reader can weigh it
SITE_RECOVER_MAX = 12             # recoveries per session: a site that keeps raising them is a site problem, so it stops
SITE_RECOVERED = [0]
SITE_SWEEP_MARGIN = 30            # cells around a plot swept of non-colonists before the plot is prepared
_HURT_BY_PAWN = re.compile(r"newest hediff (\w+)/([\w ]+?) age \d+ from ([A-Za-z_]\w*)\s*$")
_RIDE_ALONG = ("departed", "hurt", "downed")


def classify_site_stop(r):
    """-> None (a REAL stop: the clock stays stopped) or {"kind": "intruder"|"fight", "hurt": [(pawnId, hediff, part)]}
    for a safe_advance stop whose every trigger is a non-mod disturbance. Pure.
    Recoverable: stopBy is a hostile_arrival (a wild animal / entity), or a `hurt` of damage severity whose newest hediff names
    a pawn source ("... Bruise/Leg age 0 from Human": a colonist fight -- the mod's own damage, e.g. a current's bruise, names
    none). Every other trigger must be one of those or an info-severity departed/hurt/downed of nobody critical or declared.
    A death, a downed colonist, a critical or declared actor, a modal, a clock jump are never recoverable."""
    if not isinstance(r, dict) or r.get("state") != "stopped" or not r.get("stopBy"):
        return None
    sb = r["stopBy"]
    trig = list(r.get("triggers") or []) or [sb]
    out = {"kind": None, "hurt": []}

    def pawn_hurt(t):
        m = _HURT_BY_PAWN.search(str(t.get("detail") or ""))
        return m if (t.get("kind") == "hurt" and t.get("severity") == "damage" and m) else None

    for t in [sb] + trig:
        if t.get("critical") or t.get("declared"):
            return None
    m = pawn_hurt(sb)
    if sb.get("kind") == "hostile_arrival":
        out["kind"] = "intruder"
    elif m:
        out["kind"] = "fight"
    else:
        return None
    for t in trig:
        if t.get("kind") == "hostile_arrival":
            continue
        mt = pawn_hurt(t)
        if mt:
            out["hurt"].append((t.get("subjectId"), mt.group(1), mt.group(2).strip()))
            continue
        if t.get("severity") == "info" and t.get("kind") in _RIDE_ALONG:
            continue
        return None
    return out


def _helpers():
    d = os.path.join(UTILS, "modcheck")
    if d not in sys.path:
        sys.path.insert(0, d)
    import helpers  # noqa: E402
    return helpers


def remove_intruders(B, rect=None, margin=SITE_SWEEP_MARGIN):
    """Vanish (no death action: a killed Toughspike/Fingerspike runs DeathActionWorker_Divide) every hostile pawn and every
    factionless stranger / wild animal -- on the whole map, or inside rect +- margin. Colonists and the colony's own are never
    matched. Read back; -> {"removed": [...], "left": [...]}."""
    H = _helpers()

    def pick(x):
        if x.get("dead") or not x.get("spawned", True) or H.is_colonist(x):
            return False
        if not (H.is_hostile(x) or H.is_stranger(x) or H.is_wildlife(x)):
            return False
        if rect is None or x.get("x") is None:
            return True
        rx, rz, rw, rh = rect
        return rx - margin <= x["x"] <= rx + rw + margin and rz - margin <= x["z"] <= rz + rh + margin

    ids = [x["id"] for x in H.read_pawns(B, health=False) if pick(x)]
    if not ids:
        return {"removed": [], "left": []}
    res = H._kill_ids(B, set(ids), "remove_intruders", pick, action="vanish")
    return {"removed": sorted(res.evidence.get("targeted") or []), "left": list(res.residue)}


def site_recover(B, r):
    """A safe_advance stop `r` that classify_site_stop calls a non-mod disturbance: record it (SITE_NOTES, with the phase),
    remove the intruder / end the fight and heal what the fight did, READ BACK. -> ticks the stopped chunk had executed
    (the caller carries on), or None when the stop is real, the recovery did not read back clean, or the session has used
    SITE_RECOVER_MAX recoveries. Never raises."""
    try:
        c = classify_site_stop(r)
        if c is None or SITE_RECOVERED[0] >= SITE_RECOVER_MAX:
            return None
        H = _helpers()
        ev = {"kind": c["kind"], "phase": SITE_PHASE[0], "stopBy": r.get("stopBy"), "tick": (r.get("stopBy") or {}).get("tick"),
              "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        gone = remove_intruders(B)
        ev["removed"] = gone["removed"]
        clean = not gone["left"]
        if c["kind"] == "fight":
            cols = [p["id"] for p in H.read_pawns(B, health=False) if H.is_colonist(p) and not p["dead"]]
            calm = H.calm_colonists(B, cols)
            healed = []
            for pid, hd, part in c["hurt"]:
                if pid is None:
                    continue
                res = B.call("jawa/pawn_health", pawn=pid, action="remove", hediff=hd, bodyPart=part) or {}
                if not res.get("success") and "no hediff" in str(res.get("message", "")).lower():
                    res = B.call("jawa/pawn_health", pawn=pid, action="remove", hediff=hd) or {}
                healed.append((pid, hd, part, bool(res.get("success"))))
            ev["calmed"], ev["calmResidue"], ev["healed"] = calm.acted, calm.residue, healed
            clean = clean and calm.verified and all(h[3] for h in healed)
        ev["recovered"] = clean
        SITE_NOTES.append({"id": "SITE_DISTURBANCE_%s" % c["kind"].upper(), "detail": ev})
        if not clean:
            return None
        SITE_RECOVERED[0] += 1
        return int(r.get("executed") or 0)
    except Exception as ex:  # noqa: BLE001 - a recovery that breaks is a real stop, never a silent resume
        SITE_NOTES.append({"id": "SITE_DISTURBANCE_RECOVERY_FAILED", "detail": repr(ex)})
        return None


_CALM = {}


def site_calm(B):
    """Static boring test world for the whole run: storyteller off, threat scale 0, queue cleared, random mental breaks and
    diseases off, wild-animal replenishment blocked, and every non-colonist already on the map removed. DebugSettings are statics
    a load turns back on, so a driver re-applies this at each block. Idempotent; every piece is read back by helpers; a piece the
    companion lacks is named in the result, never assumed. Restore with site_calm_restore(). Social fights are not a
    random mental break, so they are NOT prevented here: site_recover ends one and heals its wound instead.
    -> {"ok": bool, "storyteller": ..., "wildSpawner": ..., "removed": ...}"""
    out = {"ok": True}
    try:
        H = _helpers()
        if "tx" not in _CALM:
            _CALM["tx"] = H.SettingsTransaction(B).__enter__()
        q = H.quiet_world(B, _CALM["tx"], wild_spawner=("wild" not in _CALM))
        _CALM["wild"] = True
        H.random_events_off(B, _CALM["tx"])
        out["storyteller"] = q.evidence.get("readBack")
        out["wildSpawner"] = q.evidence.get("wildSpawner")
        out["ok"] = bool(q.verified)
        out["removed"] = remove_intruders(B)
        # pass 2 (2026-10-19, SITE): a fresh quicktest map rolled 3 insect Hives; remove_intruders sweeps PAWNS only, so the
        # governor stopped proof_hose realflow at its first advance ("threat_structure: present at arm"). Vanish hostile
        # threat structures too (jawa/quiet_site, the vitals classifier; read back: threatsAfter must be 0).
        qs = B.call("jawa/quiet_site", action="apply", clearThreats=True)
        qs = qs if isinstance(qs, dict) else {}
        out["threatStructures"] = {"removed": [(x.get("def"), x.get("id")) for x in qs.get("removed") or []],
                                   "threatsAfter": qs.get("threatsAfter"), "error": None if qs.get("success") else str(qs)[:200]}
        if qs.get("success") is not True or qs.get("threatsAfter"):
            out["ok"] = False
    except Exception as ex:  # noqa: BLE001
        out["ok"], out["error"] = False, repr(ex)
    return out


def site_calm_restore(B):
    tx = _CALM.pop("tx", None)
    _CALM.pop("wild", None)
    if tx is None:
        return None
    try:
        return tx.__exit__(None, None, None)
    except Exception as ex:  # noqa: BLE001
        return repr(ex)


def perimeter(x0, z0, x1, z1):
    out = []
    for x in range(x0, x1 + 1):
        out += [(x, z0), (x, z1)]
    for z in range(z0 + 1, z1):
        out += [(x0, z), (x1, z)]
    return out


def ops(defn, cells, rot=None):
    return ";".join("%s:%d,%d%s" % (defn, c[0], c[1], "" if rot is None else ",%d" % rot) for c in cells)


# Verse.Log stops ALL managed logging after 10,000 messages ("Reached max messages limit"; skills/rimbridge traps.md), and on
# the owner's full list a chatty conversation mod reaches that inside one session: every later Log.Warning/Error is dropped,
# so RimBridge's journal goes silent and a log-budget row reads "0 errors" while seeing nothing (2026-10-11: proof_hose Z
# read otherErrors 0 and v2's E9 sanity warning vanished, both after the cap). The only reset is Log.Clear (the debug log
# window's Clear button), reachable through jawa/static_call (test profile).
LOG_SENTINEL = "[proof log sentinel]"


def log_alive(B, tag="check"):
    """Emit one fresh warning and read it back: {"alive": bool, "sentinel": text}. A log budget is evidence only when alive."""
    s = "%s %s %d" % (LOG_SENTINEL, tag, int(time.time() * 1000))
    w = B.call("jawa/static_call", type="Verse.Log", method="Warning", args=s)
    lg = B.call("rimbridge/list_logs", limit=50, minimumLevel="warning") or {}
    seen = any(s in str(e.get("Message", "")) for e in lg.get("logs") or [])
    return {"alive": seen, "sentinel": s, "emitted": bool(w.get("success")), "why": None if seen else (w.get("error") or w.get("message"))}


class LogTap(object):
    """Keeps every warn+/error journal entry of a run, and says whether any were lost.

    RimBridge's journal is a RING of the last 1,000 entries of ALL levels. On the owner's full list an intimacy mod logs
    ~0.3 info lines per tick (MEASURED 2026-10-11: 176 per 600 ticks, "X cannot currently do lovin'"), so a warning
    is evicted ~3,400 ticks after it is written: a log budget read once at the end of a 10-minute proof saw only its last
    blocks (v2's E9 found "0 warn+ lines since base" though E7b's warning had fired). The tap is polled after every
    step_game_ticks a bridge makes (tap_after) and at block boundaries; `lost` counts journal entries that scrolled out
    between two polls -- a budget with lost > 0 is not evidence."""

    def __init__(self, B):
        self.B = B
        self.entries = {}
        self.lost = 0
        self.polls = 0
        self.gaps = []     # (first lost seq, last lost seq, poll #, the call that preceded the poll)
        self.trigger = None
        lg = B.call("rimbridge/list_logs", limit=1, minimumLevel="trace") or {}
        self.last = max([x.get("Sequence", 0) for x in lg.get("logs") or []] or [0])
        self.base = self.last

    def poll(self):
        self.polls += 1
        lg = self.B.call("rimbridge/list_logs", afterSequence=self.last, limit=1000, minimumLevel="trace") or {}
        logs = lg.get("logs") or []
        if not logs:
            return
        # an entry repeated N times is ONE journal row carrying the sequence of its LATEST occurrence and RepeatCount N: it
        # covers seq-N+1..seq (measured 2026-10-11: rows 22138 x4, 22142 x4, ... with nothing between), so coverage starts there
        lo = min(int(x.get("Sequence", 0)) - max(1, int(x.get("RepeatCount") or 1)) + 1 for x in logs)
        hi = max(int(x.get("Sequence", 0)) for x in logs)
        if lo > self.last + 1:
            self.lost += lo - self.last - 1
            if len(self.gaps) < 20:
                self.gaps.append((self.last + 1, lo - 1, self.polls, self.trigger))
        for x in logs:
            if str(x.get("Level", "")).lower() in ("warning", "error", "exception"):
                self.entries[x.get("Sequence", 0)] = x
        self.last = max(self.last, hi)

    def since(self, seq=None):
        self.poll()
        b = self.base if seq is None else seq
        return [self.entries[k] for k in sorted(self.entries) if k > b]


TAP = []


def tap_start(B):
    """Start the run's journal tap (replacing any earlier one); bridges poll it after each tick step."""
    del TAP[:]
    TAP.append(LogTap(B))
    return TAP[0]


# the calls after which the journal can have moved by a lot: a tick step, and a load/save/new game and the state polls a
# caller makes while one runs (a full-list save load writes ~1,000 lines; polled every couple of seconds it is kept whole)
TAP_TOOLS = ("rimworld/step_game_ticks", "jawa/safe_advance", "rimworld/load_game", "rimworld/save_game", "rimworld/get_ui_state", "jawa/map_info",
             "rimworld/start_debug_game_ready", "rimworld/go_to_main_menu", "jawa/order_pawn")


def tap_after(tool):
    """Bridge hook: poll the tap after a call that lets the journal scroll (TAP_TOOLS)."""
    if TAP and tool in TAP_TOOLS:
        try:
            TAP[0].trigger = tool
            TAP[0].poll()
        except Exception:  # noqa: BLE001 - the tap must never break the call it rides on
            pass


def log_revive(B):
    """Reset Verse.Log's message cap (Log.Clear) before a run, then prove logging is live."""
    c = B.call("jawa/static_call", type="Verse.Log", method="Clear")
    return dict(log_alive(B, "revive"), cleared=bool(c.get("success")))


def _saves_stat():
    return {n: (os.path.getsize(os.path.join(SAVES, n)), int(os.path.getmtime(os.path.join(SAVES, n))))
            for n in os.listdir(SAVES) if os.path.isfile(os.path.join(SAVES, n))}


def _wait_saved(name, budget_s=60):
    """After rimworld/save_game: wait until <name>.rws exists and its size holds across two reads 1 s apart."""
    path = os.path.join(SAVES, name + ".rws")
    t0, last = time.time(), -1
    while time.time() - t0 < budget_s:
        time.sleep(1.0)
        size = os.path.getsize(path) if os.path.exists(path) else -1
        if size > 0 and size == last:
            return True
        last = size
    return False


def _wait_playing(B, budget_s=240, leave_s=30):
    """After rimworld/load_game: wait for the load to START, then for Playing (load_game answers "queued" and the old map
    stays Playing for ~3-8 s first, measured 2026-10-10 on the 550-mod list)."""
    st = None
    t0 = time.time()
    while time.time() - t0 < leave_s:
        if B.call("rimworld/get_ui_state").get("programState") != "Playing":
            break
        time.sleep(0.5)
    while time.time() - t0 < budget_s:
        st = B.call("rimworld/get_ui_state").get("programState")
        if st == "Playing" and B.call("jawa/map_info").get("success"):
            return True, int(time.time() - t0)
        time.sleep(2)
    return False, st


def reveal(B, rect, ticks=30):
    """Make a site DISCOVERED for every fog on the list, not only vanilla's: a colonist stands at its centre for `ticks`
    and goes back. 2026-10-10 (550-mod list): jawa/set_fog unfog did not stop "CanDesignateCell refused ...: Can't place in
    undiscovered area" for designator-placed runs; a colonist's sight did. Uses B's own probe ("colonists" and
    "pawn:<id>=draft|undraft|tp:x,z", answered by GimmeSomeSlackProbe and FlowWorks' HoseProbe alike).

    TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL (r5 2026-10-15): revealing fog fires vanilla's ancient-danger triggers
    (TriggerUnfogged -> SignalAction_Ambush / DormancyWakeUp), and the wave downed a colonist mid-row. Every fog/proximity
    trigger on the map is vanished first (modcheck/testenv_guards.py); the result carries the read-back as `fogTriggers`."""
    mc = os.path.join(UTILS, "modcheck")
    if mc not in sys.path:
        sys.path.append(mc)
    import testenv_guards
    disarm = testenv_guards.disarm_fog_triggers(B)
    col = B.probe("colonists")
    pawns = [p for p in col.get("pawns") or [] if not p.get("downed") and p.get("pos")]
    if not pawns:
        return {"revealed": False, "why": "no free colonist", "fogTriggers": disarm}
    p = pawns[0]
    x, z, w, h = rect
    B.probe("pawn:%d=draft" % p["id"])            # drafted, so he takes no job while he stands there (audit 2026-10-10)
    spots = [(x + w // 4, z + h // 2), (x + 3 * w // 4, z + h // 2)] if w > 30 else [(x + w // 2, z + h // 2)]
    for sx, sz in spots:
        B.probe("pawn:%d=tp:%d,%d" % (p["id"], sx, sz))
        B.ticks(ticks)
    B.probe("pawn:%d=tp:%d,%d" % ((p["id"],) + tuple(p["pos"])))
    if not p.get("drafted"):
        B.probe("pawn:%d=undraft" % p["id"])
    return {"revealed": True, "pawn": p["id"], "fogTriggers": disarm}


def clear_huge_plants(B, margin=6, tile=16):
    """Remove every huge plant whose footprint is on the map, so no test site inherits its trunk blockers.

    2026-10-11 (full list, RM_TheRot quicktest map): Huge Things' MapComponent_HugeFootprints keeps a giant plant's footprint
    as RM_HugeTrunkBlocker buildings and RE-PLANS any blocker that vanishes while its plant stands -- so a site prep that
    destroyed the blockers inside its rect got them back from a giant standing OUTSIDE it, and a reel build there read
    "CanDesignateCell refused: Space already occupied" (style_hose R1-R6 FAIL, a site fault). The plant is found through its
    blockers: every plant within `margin` of a blocker cell goes (it is cheap: test maps only). Returns counts."""
    lt = B.call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=5000) or {}
    cells = [(t.get("x"), t.get("z")) for t in lt.get("things") or [] if t.get("x") is not None]
    tiles = sorted({(x // tile, z // tile) for x, z in cells})
    for tx, tz in tiles:
        B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (tx * tile - margin, tz * tile - margin, tile + 2 * margin,
                                                             tile + 2 * margin), categories="Plant")
    if tiles:
        B.ticks(2)
    left = (B.call("jawa/list_things", defName="RM_HugeTrunkBlocker", limit=5000) or {}).get("things") or []
    return {"blockers": len(cells), "tiles": len(tiles), "blockersLeft": len(left)}


def prepare_site(B, rect, rows, rid):
    """The site prep proper (_prepare_site), run on a map first swept of intruders. Wild animals, entities and strangers near
    the plot are removed BEFORE the colonist walks in (reveal() teleports him across the plot and ticks the clock there), a
    disturbance that still lands inside the prep is recovered by _BridgeBase.ticks (site_recover) and recorded as a SITE note
    with phase "prepare" -- it no longer stops the block (2026-10-19: two reruns of proof_hose realflow ended UNMEASURED on a
    Fingerspike arriving and on a colonist-fight bruise, both inside reveal)."""
    SITE_PHASE[0] = "prepare"
    try:
        # its own read-back gates the site (an UNMEASURED/SITE row and False); the courtesy calls inside are not the rows'
        # preconditions, so they are not recorded in PRE
        with PRE.quiet():
            ok = _prepare_site_swept(B, rect, rows, rid)
    finally:
        SITE_PHASE[0] = "measure"
    # a caller that carries on over an unprepared site still cannot score a row on it
    return require(ok, "%s site prepared" % rid, list(rect))


def _prepare_site_swept(B, rect, rows, rid):
    try:
        swept = remove_intruders(B, rect)
        if swept["removed"] or swept["left"]:
            SITE_NOTES.append({"id": "%s_site_sweep" % rid, "detail": swept})
    except Exception as ex:  # noqa: BLE001 - the sweep is a courtesy; the read-back below still gates the site
        SITE_NOTES.append({"id": "%s_site_sweep_failed" % rid, "detail": repr(ex)})
    return _prepare_site(B, rect, rows, rid)


def _prepare_site(B, rect, rows, rid):
    """Make a site's cells independent of the quicktest map's random terrain (roofed ruins, rock, plants, non-soil floor).
    Clear everything, Soil, unfog, remove roof, then READ BACK: any roof or any thing still standing in the rect is an
    environmental block and is recorded UNMEASURED (never a mod FAIL). Returns True when the site is ready."""
    import re
    r = "%d,%d,%d,%d" % tuple(rect)
    why = []
    for tool, kw in (("jawa/destroy_batch", {"rects": r, "categories": "All"}),
                     ("jawa/set_terrain_batch", {"ops": "Soil:" + r}),
                     ("jawa/set_fog", {"action": "unfog", "rect": r}),
                     ("jawa/set_roof_batch", {"ops": "None:" + r})):
        res = B.call(tool, **kw)
        if isinstance(res, dict) and res.get("success") is False:
            why.append("%s refused: %s" % (tool, str(res)[:160]))
    # a trigger READ BACK as still armed blocks the site; an unreadable listing is only recorded in reveal's result (the
    # proof drivers gate the map-wide read-back once, in preflight: proof_all P3)
    ft = reveal(B, rect).get("fogTriggers") or {}
    if ft.get("left"):
        why.append("fog triggers still armed after the disarm (an ancient-danger wave can land mid-row): %s"
                   % str({k: ft.get(k) for k in ("error", "found", "left", "leftDefs")})[:200])
    B.ticks(2)
    roof = B.call("jawa/get_roof_batch", rects=r) or {}
    roofs = [x for x in (roof.get("roofs") or []) if x not in (None, "None")]
    if roofs:
        why.append("roof still present over the site: %s" % roofs)
    elif roof.get("success") is False:
        why.append("get_roof_batch unreadable: %s" % str(roof)[:160])
    lt = B.call("jawa/list_things", rect=r, limit=20) or {}
    left = [d for d in ((t.get("defName") or t.get("def") or t.get("label") or "") for t in (lt.get("things") or []))
            if re.search(r"Granite|Sandstone|Limestone|Marble|Slate|Rock|Chunk|Plant_|Tree|Bush|Grass|Ruin|TrunkBlocker", str(d))]
    if left:
        why.append("rock/plants/ruins still standing in the site: %s" % left[:8])
    if why:
        row(rows, rid, "UNMEASURED", "SITE", {"rect": list(rect), "blocked": why,
            "meaning": "the quicktest terrain still blocks the site after clearing; this is environmental, not a mod result"})
        return False
    return True
