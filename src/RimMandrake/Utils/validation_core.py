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
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = HERE
# One path seam (game_paths resolves the Windows path or its /mnt/c twin). The old USERPROFILE join collapsed to a RELATIVE
# path when USERPROFILE was unset (WSL), so every save/log read looked at the wrong place and read as "no save".
from game_paths import SAVES, PLAYER_LOG  # noqa: E402
if not os.path.isabs(SAVES) and not re.match(r"^[A-Za-z]:[\\/]", SAVES):
    raise RuntimeError("validation_core: game_paths.SAVES is not an absolute path (%r); refusing to use a relative save "
                       "folder" % (SAVES,))

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
FIELDS_BATCH = "jawa/mod_settings_fields"   # many settings fields in one call (probe_of); old companions lack it
SITE_NOTES = []


class Row(dict):
    pass


class YieldAtRowBoundary(BaseException):
    """The testq Archmagi backfill was asked to hand the game back (a bridge take, work_allocation_framework section 2):
    raised right after a row is recorded, so no row is cut in half. A BaseException, so a driver's `except Exception`
    does not swallow it."""


def row(rows, rid, status, cls, detail):
    status, cls, detail = PRE.judge(status, cls, detail)
    rows.append({"id": rid, "status": status, "class": cls, "detail": detail})
    print("%-28s %-9s %s" % (rid, status, str(detail)), flush=True)
    yield_check(rows)


def yield_check(rows, path=None):
    """Row boundary: when TESTQ_YIELD_FILE exists (testq wrote it on a bridge take), leave the rows measured so far
    beside it (<file>.rows.json, so the job does not redo them) and stop the proof. Unset or absent: nothing happens."""
    path = path or os.environ.get("TESTQ_YIELD_FILE")
    if not path or not os.path.exists(path):
        return
    try:
        with open(path + ".rows.json", "w", encoding="utf-8") as f:
            json.dump({"rows": rows}, f, default=str)
    except OSError as e:
        print("yield: could not keep the rows beside %s: %s" % (path, e), flush=True)
    print("TESTQ_YIELD at the row boundary after %s (%d rows kept)" % (rows[-1]["id"] if rows else None, len(rows)),
          flush=True)
    raise YieldAtRowBoundary(path)


def rows_exit(rows):
    """Process exit for a proof driver from its rows: 1 if any FAIL, 2 if any UNMEASURED or no rows at all, else 0.
    A driver that returns 0 after writing FAIL rows tells every command-based caller the proof passed."""
    st = [r.get("status") for r in rows or []]
    if "FAIL" in st:
        return 1
    if not st or "UNMEASURED" in st:
        return 2
    return 0


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
    # safe_advance stopOn for ticks(): "default" is the vitals latch's full list. A caller whose scene hurts or kills on
    # purpose (scenes/scenelib.run, SCENERUN_MIGRATE_OFF_UNPAUSED_PLAY) narrows it so the latch neither stops nor "heals" it.
    stop_on = "default"

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
        """Post `cmd` to probe_type's static request field and wait for the frame that services it (serial moves), then
        return its parsed result. Two calls through jawa/mod_settings_fields (reads serial and posts the request in one
        main-thread pass, then polls serial+result together); the old four single-field calls when the companion lacks
        it (speed_20261112 step 2b: GSS proof_all's 1,600 single-field reads were this loop)."""
        if self.__dict__.get("_fields_batch_ok") is not False:
            got = self._probe_batched(probe_type, cmd, wait_s, poll_s)
            if got is not None:
                return got
        before = self.call("jawa/mod_settings_field", typeName=probe_type, action="get", field="serial").get("value")
        if before is None:
            # an unreadable serial would let ANY later serial look "changed" and return the PREVIOUS probe's result as this answer
            return {"success": False, "error": "probe set failed: serial unreadable before the request", "raw": None}
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

    def _probe_batched(self, probe_type, cmd, wait_s, poll_s):
        """probe_of over jawa/mod_settings_fields. None when the companion has no such tool (the caller falls back);
        the real tool's reply always carries `values` (and `ticksGame`), an absent tool's error reply does not."""
        try:
            s = self.call(FIELDS_BATCH, typeName=probe_type, fields="serial", setField="request", setValue=cmd)
        except Exception:  # noqa: BLE001 - a transport that raises on an unknown tool: the four-call probe still works
            if self.__dict__.get("_fields_batch_ok"):
                raise           # the tool exists here: this request may have been posted, so never post it twice
            s = {}
        if not isinstance(s.get("values"), dict):
            self.__dict__["_fields_batch_ok"] = False
            return None
        self.__dict__["_fields_batch_ok"] = True
        before = s["values"].get("serial")
        if before is None:
            # the tool refuses to post when a read fails, so nothing was requested
            return {"success": False, "error": "probe set failed: serial unreadable before the request", "raw": s}
        if not s.get("success") or not s.get("set"):
            return {"success": False, "error": "probe set failed", "raw": s}
        t0 = time.time()
        while time.time() - t0 < wait_s:
            r = self.call(FIELDS_BATCH, typeName=probe_type, fields="serial,result")
            vals = r.get("values") if isinstance(r.get("values"), dict) else {}
            if vals.get("serial") is not None and vals.get("serial") != before:
                try:
                    return json.loads(vals.get("result"))
                except Exception:  # noqa: BLE001
                    return {"success": False, "raw": vals.get("result")}
            time.sleep(poll_s)
        return {"success": False, "error": "probe timed out (no frame serviced it)"}

    def probe(self, cmd, wait_s=20.0):
        if not self.probe_type:
            return {"success": False, "error": "no probe_type on this bridge class"}
        return self.probe_of(self.probe_type, cmd, wait_s)

    # -- bridge conditions (CONDSDSL_WIRE_PYTHON_BUILDERS, build_spec §1.9); the engine is conds_dsl.py
    def _watches(self):
        w = self.__dict__.get("_cond_watches")
        if w is None:
            w = self.__dict__["_cond_watches"] = []
        return w

    def _note_mutation(self, mut):
        """A mutation the wrapper made while game time ran (site_recover): every armed watch records it and restarts
        its stateful baselines (conds_dsl.WatchHandle.on_mutation)."""
        for w in list(self._watches()):
            w.on_mutation(mut)

    def _cond_recover(self, r):
        """conds_dsl.run_until's recover hook: site_recover, as ticks() uses it -> a mutation dict or None."""
        n = len(SITE_NOTES)
        with PRE.quiet():
            took = site_recover(self, r)
        if took is None:
            return None
        notes = SITE_NOTES[n:]
        return {"kind": "site_recover", "stopBy": r.get("stopBy"), "executed": took,
                "notes": [x.get("detail") for x in notes]}

    def until(self, cond, max_ticks, **kw):
        """Advance until `cond` holds or max_ticks pass (jawa/safe_advance + until) -> conds.CondResult. Re-attaches
        by runKey under the 540 s limit; a resumable or site_recover-able stop resumes (mutations[], gaps[]); any
        other stop raises clockgate.GovernorStop. kw: every, on_unknown, map_id, watch, sample, snapshot_on_hit,
        run_key, timeout_ms, progress."""
        import conds_dsl
        if self.stop_on != "default":
            kw.setdefault("stop_on", self.stop_on)
        return conds_dsl.run_until(self.call, cond, max_ticks, recover=self._cond_recover,
                                   on_mutation=self._note_mutation, **kw)

    def watch(self, name_or_map, cond=None, owner="py", ttl_min=30):
        """Persistent watcher(s) as a context manager: watch("dry", edge(...), owner=RUN), or watch({name: cond}).
        -> conds_dsl.WatchHandle (events(), gaps, mutations)."""
        import conds_dsl
        items = name_or_map if cond is None else {name_or_map: cond}
        return conds_dsl.WatchHandle(self.call, owner, items, ttl_min=ttl_min, registry=self._watches())

    def cond_eval(self, cond, map_id=None):
        """Evaluate a condition now, no tick (jawa/cond_eval); a dry run that returns refusals instead of raising."""
        import conds_dsl
        return conds_dsl.cond_eval(self.call, cond, map_id=map_id)

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
                ex = (cg.advance_chunk(self, req) if self.stop_on == "default"
                      else cg.advance_chunk(self, req, stop_on=self.stop_on))
            except cg.GovernorStop as g:
                with PRE.quiet():
                    took = site_recover(self, g.result)
                if took is None:
                    raise
                if self._watches():
                    self._note_mutation({"kind": "site_recover", "stopBy": g.result.get("stopBy"), "executed": took,
                                         "atTick": (g.result.get("stopBy") or {}).get("tick")})
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
        PRE.reply(tool, kw, r, answer=_answer)
        return r if isinstance(r, dict) else {"success": False, "raw": r}

    def _probed(self, cmd, r, answer):
        if _channel_dead(r):
            PRE.fault("probe %s" % str(cmd)[:60], str((r or {}).get("error") or "dead probe channel") if isinstance(r, dict) else r)
        elif not answer and r.get("success") is False:
            PRE.fault("probe %s" % str(cmd)[:60], str(r.get("error") or r.get("message") or r))
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


class WatchdogAbort(Exception):
    """A proof's own watchdog gave up: its wall-clock budget is spent, or the probe channel stopped answering. The caller
    writes every unwritten row UNMEASURED/HARNESS and exits; it never waits on."""


def bounded(fn, timeout_s, *a, **kw):
    """fn(*a, **kw) on a daemon thread, waited on for at most timeout_s -> (True, result), or (False, None) when it has not
    returned by then (the thread is abandoned: a frozen game never answers it, and a daemon thread does not hold the process
    open). An exception fn raises re-raises here. LEVEL_PERF_PROOF_SHRINK_TO_FIT_BUDGET (2026-11-02): a probe call into a
    frozen main thread never returned, so a between-calls deadline outlived its budget by 35 s."""
    box = {}

    def run():
        try:
            box["r"] = fn(*a, **kw)
        except BaseException as ex:  # noqa: BLE001  (handed back to the caller)
            box["ex"] = ex

    t = threading.Thread(target=run, name="bounded-call", daemon=True)
    t.start()
    t.join(max(0.0, float(timeout_s)))
    if t.is_alive():
        return False, None
    if "ex" in box:
        raise box["ex"]
    return True, box.get("r")


class Watchdog(object):
    """Wraps a bridge (normally a Guarded one) so a proof cannot hang silently (LEVEL_REHEARSAL_UNSTICK_WAITS_FOR_GODOT,
    2026-10-23: pipe_levelling --rehearsal sat 9 min after a mech raid landed, every probe timing out at 20 s while 400 hose
    lays queued behind it). Every call first checks the budget; every hp/probe/probe_of reply whose channel is dead
    (_channel_dead) counts, `dead_max` in a row raises WatchdogAbort; any live reply resets the count. Everything else passes
    through to the wrapped bridge.
    call_cap_s (LEVEL_PERF_PROOF_SHRINK_TO_FIT_BUDGET): when set, each watched call also runs under a deadline of
    min(call_cap_s, budget left) through bounded(), so a call that never returns raises WatchdogAbort at the budget instead of
    after it. None (the default) keeps the old between-calls check only."""

    def __init__(self, B, budget_s, dead_max=3, clock=time.time, call_cap_s=None):
        self.__dict__.update(_B=B, _clock=clock, _deadline=clock() + float(budget_s), _dead=0, _dead_max=int(dead_max),
                             budget_s=float(budget_s), call_cap_s=None if call_cap_s is None else float(call_cap_s))

    def __getattr__(self, k):
        return getattr(self._B, k)

    def __setattr__(self, k, v):
        setattr(self._B, k, v)

    def remaining(self):
        return self._deadline - self._clock()

    def _check(self, what):
        if self._clock() > self._deadline:
            raise WatchdogAbort("wall-clock budget of %.0f s spent (at %s)" % (self.budget_s, str(what)[:80]))

    def _run(self, what, fn, *a, **kw):
        self._check(what)
        if self.call_cap_s is None:
            return fn(*a, **kw)
        wait = max(0.0, min(self.call_cap_s, self.remaining()))
        done, r = bounded(fn, wait, *a, **kw)
        if not done:
            raise WatchdogAbort("call never returned within %.1f s (main thread frozen?) (at %s)" % (wait, str(what)[:80]))
        return r

    def _count(self, what, r):
        if _channel_dead(r):
            self.__dict__["_dead"] += 1
            if self._dead >= self._dead_max:
                raise WatchdogAbort("probe channel dead: %d replies in a row never came back (last: %s -> %s)"
                                    % (self._dead, str(what)[:60], str((r or {}).get("error") if isinstance(r, dict) else r)[:80]))
        else:
            self.__dict__["_dead"] = 0
        return r

    def call(self, tool, *a, **kw):
        return self._run(tool, self._B.call, tool, *a, **kw)

    def hp(self, cmd, *a, **kw):
        return self._count(cmd, self._run(cmd, self._B.hp, cmd, *a, **kw))

    def probe(self, cmd, *a, **kw):
        return self._count(cmd, self._run(cmd, self._B.probe, cmd, *a, **kw))

    def probe_of(self, probe_type, cmd, *a, **kw):
        return self._count(cmd, self._run(cmd, self._B.probe_of, probe_type, cmd, *a, **kw))

    def ticks(self, n):
        return self._run("ticks %s" % n, self._B.ticks, n)


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


# PROOF_HOSE_SWEEP_FIX_ATE_THE_ZOO (2026-10-22): proof_hose --no-fresh-map ran `destroy_bulk nonColonists` on walkthrough
# save c and wiped every staged animal and prisoner (map C lost 9, map R lost R1's muffalo, twice). A proof that runs on a
# map it did not make snapshots that map's non-colonists first (keep_pawns_on_map); every later sweep (sweep_non_colonists,
# remove_intruders) leaves those ids alone and removes only what arrived after the snapshot. KEEP_UNREAD: the snapshot could
# not be read, so nothing is known to be safe and sweep_non_colonists refuses to remove anything.
KEEP_PAWNS = set()
KEEP_UNREAD = [False]
KEEP_TAKEN = [False]     # a snapshot of THIS map was taken (sweep_at_start does not re-take it: strays would be kept)


def _sweepable(H, x):
    return not x.get("dead") and x.get("spawned", True) and not H.is_colonist(x)


def keep_pawns_on_map(B):
    """Snapshot every live non-colonist pawn on the current map into KEEP_PAWNS (a loaded review save's staged animals,
    prisoners, visitors). -> {"kept": [ids]} or {"error": ...} (then KEEP_UNREAD is set and sweeps refuse)."""
    try:
        H = _helpers()
        ids = set(x["id"] for x in H.read_pawns(B, health=False) if _sweepable(H, x))
    except Exception as ex:  # noqa: BLE001
        KEEP_UNREAD[0] = True
        KEEP_TAKEN[0] = True
        return {"error": repr(ex)}
    KEEP_TAKEN[0] = True
    KEEP_PAWNS.update(ids)
    H.KEEP_PAWNS.update(ids)   # the modcheck helpers' bulk removers (quiet_site hostiles_removed) spare them too
    return {"kept": sorted(ids)}


def keep_pawns_reset():
    KEEP_PAWNS.clear()
    try:
        _helpers().KEEP_PAWNS.clear()
    except Exception:  # noqa: BLE001
        pass
    KEEP_UNREAD[0] = False
    KEEP_TAKEN[0] = False


def sweep_non_colonists(B):
    """Remove the map's non-colonist pawns EXCEPT the kept ones. Nothing kept: jawa/destroy_bulk nonColonists (the old
    route, a fresh map). Something kept: vanish per exact id only the pawns not in KEEP_PAWNS (no death, no corpse), read
    back. Snapshot unreadable: remove nothing. -> {"route", "removed", "left", "kept"}."""
    if KEEP_UNREAD[0]:
        return {"route": "refused: the keep snapshot was unreadable", "removed": [], "left": [], "kept": None}
    if not KEEP_PAWNS:
        r = B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False) or {}
        return {"route": "destroy_bulk", "removed": r.get("matchedCount"), "left": [], "kept": 0}
    H = _helpers()

    def pick(x):
        return _sweepable(H, x) and x.get("id") not in KEEP_PAWNS
    ids = set(x["id"] for x in H.read_pawns(B, health=False) if pick(x))
    if not ids:
        return {"route": "none-needed", "removed": [], "left": [], "kept": len(KEEP_PAWNS)}
    res = H._kill_ids(B, ids, "sweep_non_colonists", pick, action="vanish")
    return {"route": "vanish-per-id", "removed": sorted(res.evidence.get("targeted") or []), "left": list(res.residue),
            "kept": len(KEEP_PAWNS)}


def evict_from_plots(B, ids):
    """LIVE_SESSION_FIX_B1_NEEDS_PRISTINE_MAP (driver 7, ls_c1: a kept RM_Shambles stood in a validation_v2 plot and the run
    ABORTed): vanish these exact non-colonist ids EVEN IF KEPT -- the caller has read them standing on ground it is about
    to clear and dig, so keeping them would only spoil the run. Colonists are never touched (pick re-checks). The ids
    leave the keep set. -> {"removed": [ids acted on], "left": [ids still standing]}."""
    H = _helpers()
    ids = set(ids)
    res = H._kill_ids(B, ids, "evict_from_plots", lambda x: _sweepable(H, x), action="vanish")
    KEEP_PAWNS.difference_update(ids)
    H.KEEP_PAWNS.difference_update(ids)
    return {"removed": sorted(res.evidence.get("targeted") or []), "left": list(res.residue)}


def sweep_at_start(B, made_map):
    """PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN: the opening sweep every proof shares. made_map = this run generated the map
    (a fresh quicktest map, or a clean site save it loaded): the old bulk route, nothing to keep. Otherwise (the current
    map, a review save) the map's own non-colonists are snapshotted first (keep_pawns_on_map) and this and every later
    sweep_non_colonists / remove_intruders removes only what arrived after; an unreadable snapshot removes nothing.
    A made map resets the keep set; on a kept map a second call (the next scene of the same run) keeps the first
    snapshot rather than re-taking it with the strays that arrived since. -> sweep_non_colonists' dict + "snapshot"."""
    snap = None
    if made_map:
        keep_pawns_reset()
    elif not KEEP_TAKEN[0]:
        snap = keep_pawns_on_map(B)
    sw = sweep_non_colonists(B)
    sw["snapshot"] = snap
    return sw


def remove_intruders(B, rect=None, margin=SITE_SWEEP_MARGIN):
    """Vanish (no death action: a killed Toughspike/Fingerspike runs DeathActionWorker_Divide) every hostile pawn and every
    factionless stranger / wild animal -- on the whole map, or inside rect +- margin. Colonists and the colony's own are never
    matched. Read back; -> {"removed": [...], "left": [...]}."""
    H = _helpers()

    def pick(x):
        if x.get("dead") or not x.get("spawned", True) or H.is_colonist(x) or x.get("id") in KEEP_PAWNS:
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
CALM_FOOD_FLOOR = 0.9      # site_calm tops up Food below this (HARNESS_REPAIR_CAUSE_8135787B; see site_calm)


def clear_threat_structures(B):
    """Vanish hostile threat structures (insect hives, dormant spawners) via jawa/quiet_site and read back threatsAfter (must be 0).
    -> {"removed": [(def, id)], "threatsAfter": n, "error": None|str}. error is set when the call did not succeed."""
    qs = B.call("jawa/quiet_site", action="apply", clearThreats=True)
    qs = qs if isinstance(qs, dict) else {}
    return {"removed": [(x.get("def"), x.get("id")) for x in qs.get("removed") or []],
            "threatsAfter": qs.get("threatsAfter"), "error": None if qs.get("success") else str(qs)}


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
        ts = clear_threat_structures(B)
        out["threatStructures"] = ts
        if ts["error"] or ts["threatsAfter"]:
            out["ok"] = False
    except Exception as ex:  # noqa: BLE001
        out["ok"], out["error"] = False, repr(ex)
    # pass 3 (HARNESS_REPAIR_CAUSE_8135787B): a sweep runs sprinkler_live on the run's own map after thirst_live has
    # spent ~15 min of game time there; a colonist reached Food 0 and the governor stopped the driver's first advance
    # ("starving: food category Starving"), so no result and thirst T21/T22 went driver_undelivered. Top up FOOD of a
    # colonist below CALM_FOOD_FLOOR; thirst is left alone, since the thirst and sprinkler drivers measure it. Not the
    # suite's per-chunk 0.25 (bland_world.feed_colonists' default): site_calm runs ONCE before a driver's whole run, and
    # Food falls 2.67e-5/tick (Need_Food.BaseHungerRate), so 0.25 lasts ~9,400 ticks (~6,250 at a x1.5 trait) -- less
    # than a full sprinkler_live run. 0.9 leaves >= ~22,000 ticks. Its own try: a calm piece that broke above must not
    # leave a starving colonist to stop the driver's first advance as well.
    try:
        _helpers()
        import bland_world  # noqa: E402 - beside helpers, on sys.path after _helpers()
        out["fed"] = bland_world.feed_colonists(B, floor=CALM_FOOD_FLOOR, thirst_floor=None)
    except Exception as ex:  # noqa: BLE001
        out["ok"], out["fedError"] = False, repr(ex)
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


# FlowWorks' hose reel turns (4 facings) since a98046cbe9 and a bare build op builds it NORTH. The proofs were laid out
# with the old always-WEST outlet and the reel's 2x2 on [c, c+(1,1)]; a 2x2 built West is placed one square EAST of that
# footprint (GenAdj.AdjustForRotation), so its Position -- and HoseProbe census "reel" -- is c + (1, 0). Stage reels with
# reel_west / reel_west_ops and find them with reel_at; probes that take "any square of the reel" need nothing.
def reel_west(c):
    return "RM_HoseReel:%d,%d,3" % (c[0] + 1, c[1])


def reel_west_ops(cells):
    return ";".join(reel_west(c) for c in cells)


# SCENARIO_REELS_FIX_STILL_FACING_WEST (2026-10-22 audit D10): a reel staged West whose free end lies behind it leaves the
# west nozzle and U-turns 180 degrees past itself (the straight lead-out rule). Stage a reel facing its target instead:
# reel_facing picks the facing from the footprint centre toward the target (the larger axis; ties go east/west) and the
# Position that keeps the 2x2 on [c, c+(1,1)] for that facing (GenAdj.AdjustForRotation: N +0, E z+1, S x+1 z+1, W x+1).
REEL_POS_SHIFT = {0: (0, 0), 1: (0, 1), 2: (1, 1), 3: (1, 0)}


def reel_facing(c, target):
    """Rot4 int (0 N, 1 E, 2 S, 3 W) for a 2x2 reel on footprint corner c whose hose goes to `target` (a cell); West when
    target is None (the proofs' old layout)."""
    if target is None:
        return 3
    dx, dz = target[0] + 0.5 - (c[0] + 1), target[1] + 0.5 - (c[1] + 1)
    if abs(dx) >= abs(dz):
        return 1 if dx > 0 else 3
    return 0 if dz > 0 else 2


# PROOF_REELS_FIX_STILL_STAGED_WEST (live batch 2026-10-23): a reel facing its target with the target closer than the straight
# lead-out (OutletStraight + half the bend radius, ~4.5 cells) is refused "no room for the straight lead-out from the nozzle",
# and a reel facing a pipe/pump built against its nozzle side can never lay. A stager that knows its geometry passes
# min_run (cells of straight run the facing needs from the reel edge to the target) and/or blocked (facings that touch
# something); the reel then falls back to West, the old layout whose lead-out U-turns on open ground and always laid.
REEL_LEAD_ROOM = 6


def reel_facing_roomy(c, target, min_run=REEL_LEAD_ROOM, blocked=()):
    """reel_facing, but West when the facing toward target has less than min_run cells of straight run (edge to target) or is in
    `blocked`; then the first unblocked of W, E, N, S."""
    rot = reel_facing(c, target)
    if target is None:
        return rot if rot not in blocked else next((r for r in (3, 1, 0, 2) if r not in blocked), 3)
    run = {1: target[0] - (c[0] + 2), 3: c[0] - (target[0] + 1), 0: target[1] - (c[1] + 2), 2: c[1] - (target[1] + 1)}[rot]
    if rot in blocked or run < min_run:
        return next((r for r in (3, 1, 0, 2) if r not in blocked), 3)
    return rot


def reel_pos(c, rot):
    """The build Position of a 2x2 reel on footprint corner c built facing rot."""
    sx, sz = REEL_POS_SHIFT[rot % 4]
    return (c[0] + sx, c[1] + sz)


def reel_toward(c, target, roomy=False, blocked=(), min_run=REEL_LEAD_ROOM):
    """Build op for a reel on footprint corner c facing its hose's target (reel_west when target is None). roomy=True (or any
    `blocked` facings): see reel_facing_roomy -- West where the facing toward the target has no lead-out room."""
    rot = reel_facing_roomy(c, target, min_run, blocked) if (roomy or blocked) else reel_facing(c, target)
    return "RM_HoseReel:%d,%d,%d" % (reel_pos(c, rot) + (rot,))


def reel_at(pos, c):
    """True when a reel whose Position is `pos` is the one staged at footprint corner `c` (any facing)."""
    return tuple(pos or ()) in tuple(reel_pos(c, r) for r in range(4))


# HOSE_PROOFS_FIX_STALE_LAYOK_AFTER_PEEK: since fa833277f8 (HOSE_CENSUS_FIX_RELAYS_IN_PROBE) the hose census reads the cached
# lay (r.lay) and never lays; a changed hose is re-laid off the frame (HoseLayQueue) by the draw and the 250-tick check. A row
# that acts and then reads layOk / pathLen / bbox at once read a stale or null lay. It waits here until the hose shows
# layKeyed true (re-laid under its current key) and layRunning false (no lay of it on the queue). Only a LAID hose is waited
# on: an unlaid one (stored, carried, dropped) is never laid by the tick, so it is settled as it reads. A census without the
# fields (a DLL before them, or an offline fake) is settled. The wait is wall-clock, never ticks: frames lay while paused,
# and a stepped tick would move the very state a row measures. The `lay` verb still lays synchronously.
LAY_SETTLE_S = 8.0


def lay_settled(h):
    """True when this census hose's lay is current: not laid, a census without layKeyed/layRunning, or keyed and not running."""
    if not h or not h.get("laid") or "layKeyed" not in h or "layRunning" not in h:
        return True
    return h.get("layKeyed") is True and h.get("layRunning") is not True


def settle_hose(read, wait_s=LAY_SETTLE_S, poll_s=0.25, sleep=None, clock=None):
    """Re-read until lay_settled. `read()` returns (hose, census) or a bare hose dict; returns what the last read returned.
    A hose still unsettled after `wait_s` comes back marked layUnsettled True (copied, so a row's detail shows why)."""
    sleep = sleep or time.sleep
    clock = clock or time.time
    t0 = clock()
    while True:
        got = read()
        h = got[0] if isinstance(got, tuple) else got
        if lay_settled(h):
            return got
        if clock() - t0 >= wait_s:
            h = dict(h, layUnsettled=True)
            return (h,) + tuple(got[1:]) if isinstance(got, tuple) else h
        sleep(poll_s)


def settle_census(read, match, wait_s=LAY_SETTLE_S, poll_s=0.25, sleep=None, clock=None):
    """settle_hose for a whole-census reader: `read()` returns the census, `match(h)` picks the hose(s) a row reads; it waits
    until every matched hose is settled. Returns the last census (an unsettled matched hose marked layUnsettled)."""
    sleep = sleep or time.sleep
    clock = clock or time.time
    t0 = clock()
    while True:
        c = read()
        hs = [h for h in (c or {}).get("hoses") or [] if match(h)] if isinstance(c, dict) else []
        if all(lay_settled(h) for h in hs):
            return c
        if clock() - t0 >= wait_s:
            for h in hs:
                if not lay_settled(h):
                    h["layUnsettled"] = True
            return c
        sleep(poll_s)


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
    """After rimworld/save_game: wait until <name>.rws was WRITTEN by this save (mtime >= call start minus 5 s of clock/drvfs
    slack, so a same-name save left by an earlier run cannot satisfy it) and its size holds across two reads 1 s apart."""
    path = os.path.join(SAVES, name + ".rws")
    t0, last = time.time(), -1
    while time.time() - t0 < budget_s:
        time.sleep(1.0)
        size = os.path.getsize(path) if os.path.exists(path) else -1
        fresh = size > 0 and os.path.getmtime(path) >= t0 - 5
        if fresh and size == last:
            return True
        last = size
    return False


def _wait_playing(B, budget_s=240, leave_s=30):
    """After rimworld/load_game: wait for the load to START, then for Playing (load_game answers "queued" and the old map
    stays Playing for ~3-8 s first, measured 2026-10-10 on the 550-mod list)."""
    from await_lifecycle import await_lifecycle, await_leaving  # noqa: E402  (READYWAITS_MIGRATE_REMAINING_52_COPIES)
    # every poll is an answer, not a fault: "No current map" while the load finishes is expected (live 2026-10-21 drawbridge
    # SAVE_MIDRAISE went UNMEASURED/HARNESS on exactly this refusal while every read after the load succeeded)
    call = lambda tool, **kw: B.call(tool, _answer=True, **kw)  # noqa: E731
    t0 = time.time()
    nap = lambda s: time.sleep(s)  # noqa: E731  late-bound, so a selftest's patched V.time.sleep is honoured
    await_leaving(call, "playing", leave_s, poll_s=0.5, sleep=nap)  # a load that never visibly starts: the map wait judges
    lc = await_lifecycle(call, "map_ready", max(0.0, budget_s - (time.time() - t0)), poll_s=2.0, sleep=nap)
    if lc.ok:
        return True, int(time.time() - t0)
    print("_wait_playing: %s" % lc.reason)
    return False, lc.last.get("programState")


# ---- saveload_triplet (PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET) ------------------------------------------------------------
TRIPLET_IDENTICAL = "IDENTICAL"
TRIPLET_SAVE_DROPS = "SAVE_DROPS_STATE"
TRIPLET_LOAD_NONDET = "LOAD_NONDETERMINISTIC"
TRIPLET_UNMEASURED = "UNMEASURED"
TRIPLET_LOAD_SLACK = 3      # a real load lands at the saved tick + at most this many (Prefs.PauseOnLoad runs ONE DoSingleTick)
TRIPLET_MIN_TICKS = 10      # > TRIPLET_LOAD_SLACK: a no-op load (still at arm A's target) can never pass for a fresh one


def ticks_game(B):
    """Find.TickManager.TicksGame through jawa/time_clock, or None when unreadable (never a guessed 0)."""
    r = B.call("jawa/time_clock", _answer=True) or {}
    v = r.get("ticksGame")
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _flatten(x, pre=""):
    """A read_state result -> {dotted.key: leaf}. Lists keep their order (index keys); a set-like reading should be sorted
    by its reader. An empty dict or list is a leaf of its own ({} / []), so {"y": {}} never equals a reading without y.
    Two paths that spell the same key ({"a.b": 1} beside {"a": {"b": 2}}) raise ValueError: the reading is ambiguous."""
    out = {}

    def put(k, v):
        if k in out:
            raise ValueError("saveload_triplet: two paths flatten to the key %r" % k)
        out[k] = v

    if isinstance(x, dict):
        if not x:
            put(pre, {})
        for k in sorted(x, key=str):
            part = _key_part(k)
            for kk, vv in _flatten(x[k], "%s.%s" % (pre, part) if pre else part).items():
                put(kk, vv)
    elif isinstance(x, (list, tuple)):
        if not x:
            put(pre, [])
        for i, v in enumerate(x):
            for kk, vv in _flatten(v, "%s[%d]" % (pre, i)).items():
                put(kk, vv)
    else:
        put(pre, x)
    return out


def _key_part(k):
    """A dict key as one path component: a plain str as itself; a str holding . [ ] " , starting with <, or empty, JSON-quoted;
    any other type
    tagged with its type -- so {"a.b": 1} vs {"a": {"b": 1}}, {"x[0]": 1} vs {"x": [1]} and {1: v} vs {"1": v} never alias."""
    if isinstance(k, str):
        return json.dumps(k) if (not k or k[0] == "<" or any(c in k for c in '.[]"')) else k
    return "<%s:%r>" % (type(k).__name__, k)


def _check_tolerance(tolerance):
    import math
    for k, t in (tolerance or {}).items():
        if isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or t < 0:
            raise ValueError("saveload_triplet: tolerance[%r] = %r -- a tolerance is a finite number >= 0" % (k, t))


def _nonfinite(flat):
    import math
    return sorted(k for k, v in flat.items() if isinstance(v, float) and not math.isfinite(v))


def _tol_for(key, tolerance):
    import fnmatch
    if key in tolerance:
        return tolerance[key]
    for pat, tol in tolerance.items():
        if fnmatch.fnmatchcase(key, pat):
            return tol
    return None


_MISSING = object()


def triplet_diff(a, b, tolerance=None):
    """Field-level diff of two flattened readings: {key: [a, b]} for every key that differs. A number differs only beyond
    its tolerance (exact key or fnmatch pattern in `tolerance`, absolute); a key on one side only differs (missing reads
    as None in the pair, with the key listed)."""
    tolerance = tolerance or {}
    out = {}
    for k in sorted(set(a) | set(b)):
        va, vb = a.get(k, _MISSING), b.get(k, _MISSING)
        if va is _MISSING or vb is _MISSING:
            out[k] = [None if va is _MISSING else va, None if vb is _MISSING else vb]
            continue
        num = (isinstance(va, (int, float)) and isinstance(vb, (int, float))
               and not isinstance(va, bool) and not isinstance(vb, bool))
        tol = _tol_for(k, tolerance) if num else None
        if num and tol is not None:
            from fractions import Fraction      # exact: 2**53+1 vs float(2**53) must not subtract to 0.0
            if abs(Fraction(va) - Fraction(vb)) > Fraction(tol):
                out[k] = [va, vb]
        elif va != vb or (not num and type(va) is not type(vb)):    # True vs 1, 1 vs "1": a different leaf
            out[k] = [va, vb]
    return out


def saveload_triplet(B, read_state, ticks=60, tolerance=None, save_name=None, saves_stat=None, wait_saved=None,
                     wait_playing=None):
    """Separate "the save drops state" from "the load is nondeterministic" with three arms from ONE save.

    Two lessons of 2026-11-01 (FOUNDRY) misread a one-save-one-load proof: (1) Game.LoadGame with Prefs.PauseOnLoad runs one
    DoSingleTick after load, so a loaded arm read "right after the load" is a tick ahead of the live one; (2) a save
    quantises some state (SurfaceLayer writes a tile's base temperature as ushort RoundToInt((t+300)*10)), so a never-saved
    world differs from its own reload by ~0.03 C. And one load alone cannot say WHICH of the two is wrong.

        save at T0 -> arm A: live, advance to T = T0 + ticks, read
                   -> arm B: load, MEASURE TicksGame, advance to T, read
                   -> arm C: load again, the same
        B != C              LOAD_NONDETERMINISTIC (two loads of one file disagree: the save is not the only cause)
        B == C, A != B, A != C  SAVE_DROPS_STATE  (both loads agree with each other, not with the live game: the save/load
                                                   ROUND TRIP loses it -- the writer, or a deterministic loader; the .rws
                                                   itself says which)
        A == B == C         IDENTICAL
        anything unread     UNMEASURED            (save not landed, load not Playing, arm not at T, read failed/empty)

    read_state(B) -> a dict/list reading (flattened to dotted keys and compared field by field), or None when unreadable.
    It must read only what a save should carry (no wall clock, no frame counter, no random per-load ids), be deterministic
    over `ticks` on a live game, and NOT advance game time (the clock is checked after each read). tolerance = {key or fnmatch pattern: absolute tolerance} for KNOWN save
    quantisation, e.g. {"*.temperature": 0.05} (finite, >= 0, else ValueError). Arms are aligned on the measured TicksGame, never on an assumed delta: the
    loaded arms advance (T - their measured tick), so the PauseOnLoad tick is absorbed; ticks must be >= TRIPLET_MIN_TICKS.
    A load counts only when the clock reads back at the saved tick (+ <= TRIPLET_LOAD_SLACK) after it; every arm must end
    its read at the same tick; NaN/inf, an empty reading or two paths flattening to one key are UNMEASURED; IDENTICAL needs
    AB, BC and AC all equal (a tolerance is not transitive), and a mixed AB/AC is UNMEASURED, never a verdict.

    The save is a NEW file (a same-name file refuses); on return the game is in arm C (a load of that save). Keeper maps:
    wrap the call in save_guard (rimworld/save_game has written the current slot). The seams saves_stat / wait_saved /
    wait_playing default to this module's own (_saves_stat / _wait_saved / _wait_playing); the offline selftest passes fakes.

    Returns {"verdict", "why", "save", "target", "arms": {"A"|"B"|"C": {"tick", "loadedAt", "readTick", "state"}}, "AB",
    "BC", "AC"}
    where AB/BC/AC are triplet_diff results."""
    _check_tolerance(tolerance)
    saves_stat = saves_stat or _saves_stat
    wait_saved = wait_saved or _wait_saved
    wait_playing = wait_playing or _wait_playing
    if int(ticks) < TRIPLET_MIN_TICKS:
        raise ValueError("saveload_triplet: ticks=%r < %d -- a real load lands up to TRIPLET_LOAD_SLACK ticks past the save, so "
                         "it could not be told from a load that never ran (the clock left at arm A's target)" % (ticks, TRIPLET_MIN_TICKS))
    name = save_name or "RM_triplet_%s" % time.strftime("%Y%m%d%H%M%S")
    res = {"verdict": TRIPLET_UNMEASURED, "why": None, "save": name + ".rws", "target": None, "arms": {},
           "AB": None, "BC": None, "AC": None, "tolerance": dict(tolerance or {})}

    def unmeasured(why):
        res["why"] = why
        return res

    def advance_to(target):
        """Advance to `target` on the measured clock; -> the measured tick, or an error string."""
        now = ticks_game(B)
        if now is None:
            return "TicksGame unreadable"
        if now > target:
            return "arm at tick %d is already past the target %d" % (now, target)
        if target > now:
            B.ticks(target - now)
        end = ticks_game(B)
        if end != target:
            return "arm ended at tick %r, not the target %d (asked for %d ticks)" % (end, target, target - now)
        return end

    def read(arm):
        try:
            st = read_state(B)
        except Exception as ex:  # noqa: BLE001 - a reader crash is an unread arm, never a verdict
            return "arm %s: read_state raised %r" % (arm, ex)
        if st is None:
            return "arm %s: read_state returned None (unreadable)" % arm
        if not st:
            return "arm %s: read_state returned an empty reading (the instrument sees nothing)" % arm
        try:
            flat = _flatten(st)
        except ValueError as ex:
            return "arm %s: %s" % (arm, ex)
        bad = _nonfinite(flat)
        if bad:
            return "arm %s: non-finite reading(s) %s (NaN/inf compare as equal under a tolerance)" % (arm, bad[:5])
        res["arms"][arm]["state"] = flat
        return None

    before = saves_stat()
    if name + ".rws" in before:
        return unmeasured("%s.rws already exists: the triplet saves a NEW file only" % name)
    t0 = ticks_game(B)
    if t0 is None:
        return unmeasured("TicksGame unreadable before the save")
    target = t0 + int(ticks)
    res["target"] = target
    sv = B.call("rimworld/save_game", saveName=name) or {}
    if sv.get("success") is False:
        return unmeasured("rimworld/save_game refused: %s" % str(sv))
    if not wait_saved(name):
        return unmeasured("%s.rws was not written (or not stable) after rimworld/save_game" % name)
    after = saves_stat()
    changed = sorted(n for n in before if n in after and after[n] != before[n])
    if name + ".rws" not in after or changed:
        return unmeasured("the save did not land as a new file only: new=%s changed=%s"
                          % (sorted(set(after) - set(before)), changed))
    t_saved = ticks_game(B)
    if t_saved != t0:
        return unmeasured("the clock moved during the save (%r -> %r): arm A would not start at the saved tick" % (t0, t_saved))

    for arm in ("A", "B", "C"):
        res["arms"][arm] = {"tick": None, "loadedAt": None, "readTick": None, "state": None}
        if arm != "A":
            ld = B.call("rimworld/load_game", saveName=name) or {}
            if ld.get("success") is not True:
                return unmeasured("arm %s: rimworld/load_game did not answer success: %s" % (arm, str(ld)))
            ok, waited = wait_playing(B)
            if not ok:
                return unmeasured("arm %s: the load never reached Playing with a map (%r)" % (arm, waited))
            at = ticks_game(B)
            res["arms"][arm]["loadedAt"] = at
            # the evidence that THIS load happened: the clock is back at the save (+ PauseOnLoad's tick), not where arm A
            # (or the previous arm) left it. A queued load that never ran keeps the old map Playing at the target tick.
            if at is None or not (t0 <= at <= t0 + TRIPLET_LOAD_SLACK):
                return unmeasured("arm %s: after the load the clock reads %r, not the saved tick %d (+<= %d): the load did "
                                  "not take" % (arm, at, t0, TRIPLET_LOAD_SLACK))
        got = advance_to(target)
        if isinstance(got, str):
            return unmeasured("arm %s: %s" % (arm, got))
        res["arms"][arm]["tick"] = got
        err = read(arm)
        if err:
            return unmeasured(err)
        # the reading must be taken AT the target: a reader that advances the clock hides when it sampled (equal end ticks do
        # not prove equal capture ticks), so any tick inside read_state is UNMEASURED
        res["arms"][arm]["readTick"] = ticks_game(B)
        if res["arms"][arm]["readTick"] != target:
            return unmeasured("arm %s: the clock read %r after read_state, not the target %d -- read_state must not advance "
                              "game time" % (arm, res["arms"][arm]["readTick"], target))

    A, Bs, C = (res["arms"][k]["state"] for k in ("A", "B", "C"))
    res["AB"] = triplet_diff(A, Bs, tolerance)
    res["BC"] = triplet_diff(Bs, C, tolerance)
    res["AC"] = triplet_diff(A, C, tolerance)
    if res["BC"]:
        res["verdict"] = TRIPLET_LOAD_NONDET
        res["why"] = "two loads of one save disagree on %d field(s)" % len(res["BC"])
    elif res["AB"] and res["AC"]:
        res["verdict"] = TRIPLET_SAVE_DROPS
        res["why"] = ("both loads agree with each other and differ from the live arm on %d field(s): the round trip loses it "
                      "(the writer or a deterministic loader -- read the .rws to tell which)" % len(res["AB"]))
    elif not res["AB"] and not res["AC"]:
        res["verdict"] = TRIPLET_IDENTICAL
        res["why"] = "live, load and reload agree at tick %d" % target
    else:
        # a tolerance is not transitive: B~C and one of A~B / A~C but not the other. No side can be blamed.
        res["why"] = ("ambiguous under the tolerance: BC equal, AB %s, AC %s -- tighten or widen the tolerance"
                      % ("equal" if not res["AB"] else "differs", "equal" if not res["AC"] else "differs"))
    return res


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
    # PROOF_SITE_HARDEN_HUGE_TRUNKS_SURVIVE_CLEAR (run6 2026-10-25, 3905 RM_HugeTrunkBlocker on a quicktest map): Huge Things
    # re-plans a trunk blocker while its giant stands, so _prepare_site's destroy alone left "TrunkBlocker still standing" and
    # the Soil paint did not read back. The giants go first, for every caller; the read-back below still gates the site.
    try:
        huge = clear_huge_plants(B)
        if huge.get("blockers"):
            SITE_NOTES.append({"id": "%s_huge_plants" % rid, "detail": huge})
    except Exception as ex:  # noqa: BLE001 - a courtesy like the sweep; a blocker left in the rect still fails the read-back
        SITE_NOTES.append({"id": "%s_huge_plants_failed" % rid, "detail": repr(ex)})
    return _prepare_site(B, rect, rows, rid)


def _prepare_site(B, rect, rows, rid):
    """Make a site's cells independent of the quicktest map's random terrain (roofed ruins, rock, plants, non-soil floor).
    Clear everything, Soil, unfog, remove roof, then READ BACK: any roof or any thing still standing in the rect is an
    environmental block and is recorded UNMEASURED (never a mod FAIL). Returns True when the site is ready."""
    import re
    r = "%d,%d,%d,%d" % tuple(rect)
    why = []
    for tool, kw in (("jawa/destroy_batch", {"rects": r, "categories": "All"}),
                     # clearOverlays: floodwater/thin ice (tempGrid) and Substructure (foundation) read before the top
                     # grid, so a bare Soil paint left them showing (HOSE_SITE_FIX_TERRAIN_WONT_READ_BACK, run4 2026-10-25:
                     # R_site_ready 4 and RF_site0_ready 231 cells "did not read back")
                     ("jawa/set_terrain_batch", {"ops": "Soil:" + r, "clearOverlays": True}),
                     ("jawa/set_fog", {"action": "unfog", "rect": r}),
                     ("jawa/set_roof_batch", {"ops": "None:" + r})):
        res = B.call(tool, **kw)
        if isinstance(res, dict) and res.get("success") is False:
            # the message first and long enough to read: live 20261023T044826 cut "...337 cell(s) changed, 104 a" at 160
            # chars, before the clause that said WHY set_terrain_batch refused
            why.append("%s refused: %s" % (tool, str(res.get("message") or res)))
    # a trigger READ BACK as still armed blocks the site; an unreadable listing is only recorded in reveal's result (the
    # proof drivers gate the map-wide read-back once, in preflight: proof_all P3)
    ft = reveal(B, rect).get("fogTriggers") or {}
    if ft.get("left"):
        why.append("fog triggers still armed after the disarm (an ancient-danger wave can land mid-row): %s"
                   % str({k: ft.get(k) for k in ("error", "found", "left", "leftDefs")}))
    B.ticks(2)
    # 2026-10-22 (BENCH belt, lines_proof 21x95-cell site, fw_gss_sitting): ONE Plant_Grass read back after the ~60 reveal
    # ticks -- vanilla's WildPlantSpawner seeds new plants on a large fertile rect while the colonist stands there. The first
    # destroy ran before reveal, so plants are swept again after it (HARNESS/SITE class fix; a plant re-seeded later inside a
    # row is the row's own site read, not this gate's).
    # 2026-11-03 (DRAWBRIDGE_WINCH_DIAGNOSE_UNLINKED_REBUILT, test pilot): the first sweep destroys rock under a mountain roof
    # and the roof collapse that follows drops CollapsedRocks (213 read back, no roof left) AFTER it -> SITE UNMEASURED. A
    # second All sweep cleared every one live and none returned in 120 ticks; destroy_batch skips pawns, so All is safe.
    B.call("jawa/destroy_batch", rects=r, categories="All")
    roof = B.call("jawa/get_roof_batch", rects=r) or {}
    roofs = [x for x in (roof.get("roofs") or []) if x not in (None, "None")]
    if roofs:
        why.append("roof still present over the site: %s" % roofs)
    elif roof.get("success") is False:
        why.append("get_roof_batch unreadable: %s" % str(roof))
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
