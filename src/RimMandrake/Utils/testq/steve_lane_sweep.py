#!/usr/bin/env python3
"""steve_lane_sweep.py: the SteveDesktop test lane, swept offline over simulated days (RIMMANDRAKE_BUILD_STEVE_LANE_SWEEP_
PAUSE_HELD_49_HOURS; rank 1 of design/specs/2026-11-26-simulation-census/one_page.md, about 64 hours lost).

Part A (the lane): the REAL testq.py tick and fill code (cmd_tick, reconcile, finish, admit, lane_stop.step and
on_finish, fill_once and fill_plan, cmd_pause and cmd_resume) runs every pass of a simulated day on a fake clock, in the
order of testq-tick.service (tick, fill each mod, tick), in a temp queue home. Stand-ins replace only what touches the
world: both games' workers and ssh (testq.remote), systemd (lane_stop's systemctl), git (fill_once's rev-parse), the
idle stop's ssh, the companion stager's probe (companion_unready/companion_hold: their own unit), the visit feed, site
stage and the Archmagi lane (switched off), and the filler's evidence ranking (fill_rank_declared: modcheck records).
cmd_submit is replaced by a submit that builds the job with the real schema.make_job (its refusals only refuse).
After every pass it checks that no pause, stop or job stays in a state that nothing ends:
  PAUSE_PAST_END  a pause stands past its own end (its until; since + DEFAULT_PAUSE_H when it names none; its unit's end
                  while systemd answers)
  STOP_PAST_END   a game's stop is in effect longer than lane_stop.RETRY_S after it was made
  REPEAT          a third (or later) equal refusal on one game came sooner than RETRY_S after the one before it
  JOB_STUCK       a running job whose attempt has ended stays running, or a ready job waits while a game is free
  SSH_MARK_PAST_END  testq still marks SteveDesktop down a probe interval (PROBE_S) after ssh came back
Part C (the account gate of SteveDesktop, 2026-11-26): account_plan_sweep's world with SteveDesktop on the live account
and one run there that only waits (it never ends and hears no save order: a run the store lists as running that is not
live), with the save-order and stop seams the real pass has. Its STUCK check reads the refusals of the machine's gate.

Deterministic: seeded, no network, no live game, no model call; writes only under a temp folder.
  steve_lane_sweep.py grid [--quick]      every regime, one line each, VIOLATES lines last
  steve_lane_sweep.py one '<regime json>'  one regime, its trace
  steve_lane_sweep.py gate [--plant]       Part C (JSON)
Design: design/specs/2026-11-27-steve-lane-sweep/boundary.md."""
import argparse
import contextlib
import io
import json
import os
import random
import subprocess as _subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
_SCRATCH = tempfile.mkdtemp(prefix="steve_lane_sweep_")
os.environ["TESTQ_QUEUE"] = os.path.join(_SCRATCH, "q0")    # before testq is imported: its QHOME is never the live one
sys.path.insert(0, HERE)
import testq as T  # noqa: E402
import lane_stop as LS  # noqa: E402
import idle_stop as IS  # noqa: E402

S = T.S
REAL_TIME = time.time
PROBE_S = T.PROBE_S         # read before any plant moves it
PASS_S = 60                 # testq-tick.timer OnUnitInactiveSec=60s (src/RimMandrake/Utils/systemd/testq-tick.timer)
T0 = S.parse_ts("2026-11-23T00:00:00Z")
END_LIMIT_S = 2 * PASS_S    # lane_stop.step runs at the start of each tick: an end is read within one pass; one more
                            # pass for the tick that saw it to run (a fact of cmd_tick's order)
STUCK_PASSES = 2            # reconcile and admit run on every tick that reaches the machine: one pass, plus one
BROKEN_NOTE = "Steve2 is running; it rewrites Prefs.xml on exit. Stop it first (pid 4242)"   # the 2026-11-23 refusal
BLIND = set(filter(None, os.environ.get("STEVE_LANE_SWEEP_BLIND", "").split(",")))   # checks switched off: the
                                    # selftest's proof that a sweep that cannot see a fault fails its test
OWN_PAUSE = ("CANARY", "GUARD_HELD", "BLOCKED_SELECTION", "SCHEMA")   # a cause with its own pause or retry, or a bad
                                                                      # request: not a game refusing every job


def stamp(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def within(win, h):
    return bool(win) and win[0] <= h < win[1]


class Game:
    """One game's worker on SteveDesktop: the verbs testq.py calls (status, start, result, ack, outbox, stop)."""

    def __init__(self, world, host, spec):
        self.w, self.host, self.spec = world, host, spec or {}
        self.att = {}       # aid -> {job, start, end, outcome, cause, note, acked, lost}
        self.n = {}

    def win(self, key, h=None):
        h = self.w.h() if h is None else h
        return any(within(x, h) for x in (self.spec.get(key) or []))

    def running(self):
        return [a for a, r in self.att.items() if not r["lost"] and r["end"] > self.w.t]

    def ending(self, h):
        for key, oc, cause, note, dur in (("broken", "REFUSED", "LOAD", BROKEN_NOTE, (1, 2)),
                                          ("sync", "REFUSED", "SYNC", "the runner clone would not sync", (1, 2)),
                                          ("guard", "REFUSED", "GUARD_HELD", "a driver holds the game guard", (1, 1)),
                                          ("canary", "INVALID", "CANARY", "canary row red", (5, 8)),
                                          ("crash", "INTERRUPTED", "CRASH", "the game crashed", (10, 30))):
            if self.win(key, h):
                return oc, cause, note, dur
        return "DONE", None, "", tuple(self.spec.get("dur_min") or (20, 60))

    def call(self, args, stdin):
        verb, t = args[0], self.w.t
        if verb == "status" and "--job" not in args:
            run = self.running()
            if self.win("busy"):
                return 0, {"busy": True, "current": "a driver's own run (not testq's)"}
            return 0, {"busy": bool(run), "current": run[0] if run else None}
        if verb == "status":
            jid = args[args.index("--job") + 1]
            mine = sorted((a for a in self.att if a.rsplit(".a", 1)[0] == jid), key=lambda a: int(a.rsplit(".a", 1)[1]))
            if not mine or self.att[mine[-1]]["lost"]:
                return 0, {"attempt": None, "state": "none"}
            a = mine[-1]
            return 0, {"attempt": a, "state": "running" if self.att[a]["end"] > t else "finished"}
        if verb == "start":
            job = json.loads(stdin)
            run = self.running()
            same = [a for a in run if a.rsplit(".a", 1)[0] == job["id"]]
            if same:
                return 0, {"attempt": same[0], "duplicate": True}
            if run or self.win("busy") or ("--retry" in args and self.win("guard")):
                return T.EX_BUSY, {"busy_with": run[0] if run else "the game guard"}
            k = self.n[job["id"]] = self.n.get(job["id"], 0) + 1
            aid = "%s.a%d" % (job["id"], k)
            oc, cause, note, (lo, hi) = self.ending(self.w.h())
            self.att[aid] = {"job": job, "start": t, "end": t + self.w.rng.uniform(lo, hi) * 60, "outcome": oc,
                             "cause": cause, "note": note, "acked": False, "lost": self.win("lose")}
            return 0, {"attempt": aid}
        if verb == "result":
            aid = args[args.index("--attempt") + 1]
            r = self.att.get(aid)
            if not r or self.win("unread"):
                return 1, {"error": "sweep: result of %s not readable now" % aid}
            chains = (r["job"].get("selector") or {}).get("chains") or ["c"]
            return 0, {"schema": S.RESULT_SCHEMA, "job": r["job"]["id"], "attempt": aid, "outcome": r["outcome"],
                       "cause": r["cause"], "note": r["note"], "counts": {"rows": len(chains)},
                       "rows": [{"chain": c, "row": "r1", "verdict": "PASS" if r["outcome"] == "DONE" else "UNMEASURED"}
                                for c in chains]}
        if verb == "ack":
            aid = args[args.index("--attempt") + 1]
            if aid in self.att:
                self.att[aid]["acked"] = True
            return 0, {"acked": aid}
        if verb == "outbox":
            return 0, {"outbox": sorted(a for a, r in self.att.items()
                                        if not r["lost"] and r["end"] <= t and not r["acked"])}
        if verb == "stop":
            aid = args[args.index("--attempt") + 1]
            if aid in self.att and self.att[aid]["end"] > t:
                self.att[aid].update(end=t, outcome="INTERRUPTED", cause="CRASH", note="stopped")
            return 0, {"stopped": aid}
        return 2, {"error": "sweep: unknown verb %s" % verb}


class World:
    def __init__(self, reg):
        self.reg = reg
        self.rng = random.Random(reg.get("seed", 0))
        self.t = T0
        self.games = {T.STEVE: Game(self, T.STEVE, reg.get("steve1")),
                      T.STEVE2: Game(self, T.STEVE2, reg.get("steve2"))}
        self.ids = 0
        self.unit_end = {}      # unit -> the time it went inactive (None while active)

    def h(self, t=None):
        return ((self.t if t is None else t) - T0) / 3600

    def ssh_up(self):
        return not any(within(x, self.h()) for x in self.reg.get("ssh_down") or [])

    def systemd_reads(self):
        return not any(within(x, self.h()) for x in self.reg.get("systemd_unread") or [])

    def unit_on(self, unit):
        return within((self.reg.get("units") or {}).get(unit), self.h())

    # ---- the stand-ins
    def remote(self, args, stdin=None, timeout=None, host=T.STEVE):     # T.remote's signature; a fake game never hangs
        if not self.ssh_up():
            raise T.SshDown("sweep: ssh to SteveDesktop timed out")
        return self.games[host].call(args, stdin)

    def systemctl(self, argv, **_kw):
        if argv[:3] != ["systemctl", "--user", "is-active"]:
            raise AssertionError("sweep: unexpected subprocess %s" % argv)
        if not self.systemd_reads():
            raise _subprocess.TimeoutExpired(argv, 20)
        on = self.unit_on(argv[3])
        return _subprocess.CompletedProcess(argv, 0 if on else 3, "active\n" if on else "inactive\n", "")

    def git(self, argv, **_kw):
        if argv[:1] != ["git"] or "rev-parse" not in argv:
            raise AssertionError("sweep: unexpected subprocess %s" % argv)
        return _subprocess.CompletedProcess(argv, 0, "abc1234\n", "")

    def new_job_id(self):
        self.ids += 1
        return "J%s-%06x" % (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(self.t)), self.ids)

    def submit(self, a):
        """cmd_submit's stand-in: the real schema.make_job, the real duplicate rule, one pending record."""
        job = S.make_job(a.mod, {"chains": [c for c in a.chains.split(",") if c]}, a.purpose, a.by, a.sha,
                         priority=a.priority, lane=a.lane, timeout_s=a.timeout)
        for other in T.records("pending") + [r["job"] for r in T.records("running")]:
            if T.same_request(job, other):
                return 0
        S.dump(job, T.q("pending", job["id"] + ".json"))
        return 0

    def pick(self, mod, n, now, today=None):
        self.ids += 0
        k = int((now - T0) // PASS_S)
        return {"verdict": "pick", "rank": "sweep", "purpose": "sweep", "pick": ["%s_c%d" % (mod, k % 7)],
                "row_items": {}, "dry": [], "blind": [], "gone": [], "text": "would queue (sweep)"}


def hand_events(w):
    """The regime's hand acts due this pass: pauses (real cmd_pause, or a legacy record of a build before 767bcaeb)
    and hand jobs."""
    out = []
    for e in w.reg.get("events") or []:
        if e.get("done") or w.h() < e["at_h"]:
            continue
        e["done"] = True
        kind = e["kind"]
        if kind == "pause":
            T.cmd_pause(argparse.Namespace(reason="sweep: hand pause", hours=e.get("hours"),
                                           until_unit=e.get("unit")))
        elif kind == "legacy_pause":       # what cmd_pause wrote before 767bcaeb: no until, no unit
            S.dump({"since": S.utcnow(), "job": None, "attempt": None, "outcome": None, "cause": None,
                    "reason": "sweep: hand pause (old build)", "note": "paused by hand"},
                   T.pause_path(e.get("host") or T.STEVE))
        elif kind == "jobs":
            for i in range(e["n"]):
                w.submit(argparse.Namespace(mod=e.get("mod", "SimHand"), chains="h%d_%d" % (int(e["at_h"] * 10), i),
                                            purpose="fix", by="BENCH", sha="abc1234", priority=50,
                                            lane="stevedesktop", timeout=S.DEFAULTS["timeout_s"]))
        out.append(kind)
    return out


class Checks:
    def __init__(self, w):
        self.w = w
        self.viol, self.seen = [], set()
        self.m = {"pause_late_s": [None, END_LIMIT_S, 0], "stop_late_s": [None, END_LIMIT_S, 0],
                  "repeat_gap_s": [None, LS.RETRY_S, 0], "running_stale_passes": [None, STUCK_PASSES, 0],
                  "pending_free_passes": [None, STUCK_PASSES, 0], "ssh_mark_late_s": [None, END_LIMIT_S, 0]}
        self.up_for = 0
        self.same_max = 0       # the longest row of equal refusals on one game
        self.ends = {h: [] for h in T.STEVE_HOSTS}      # (finished t, signature) of each counted ending, in order
        self.done_seen = set()
        self.stale = {}
        self.free_wait = {h: 0 for h in T.STEVE_HOSTS}
        self.unit_seen_on = {}

    def flag(self, check, key, detail):
        if check in BLIND or (check, key) in self.seen:
            return
        self.seen.add((check, key))
        self.viol.append({"check": check, "h": round(self.w.h(), 2), "detail": detail})

    def worst(self, name, val, bigger_is_worse=True):
        m = self.m[name]
        m[2] += 1
        if m[0] is None or (val > m[0] if bigger_is_worse else val < m[0]):
            m[0] = val

    def pause_end(self, pz, host):
        """-> the pause's end by its own record (None: not yet known), read here, not by lane_stop."""
        w = self.w
        if pz.get("until_unit"):
            u = pz["until_unit"]
            if w.unit_on(u):
                return None
            win = (w.reg.get("units") or {}).get(u)
            end = T0 + win[1] * 3600 if win and w.h() >= win[1] else S.parse_ts(pz["since"])
            for x in w.reg.get("systemd_unread") or []:      # systemd that cannot answer cannot end it (designed)
                a, b = T0 + x[0] * 3600, T0 + x[1] * 3600
                if a <= max(end, w.t - END_LIMIT_S) and b > end:
                    end = min(b, w.t) if b <= w.t else None
                    if end is None:
                        return None
            return end
        if pz.get("until"):
            return S.parse_ts(pz["until"])
        return S.parse_ts(pz["since"]) + LS.DEFAULT_PAUSE_H * 3600

    def after_pass(self):
        w = self.w
        for host in T.STEVE_HOSTS:
            pz = T.paused(host)
            if pz:
                end = self.pause_end(pz, host)
                if end is not None:
                    late = w.t - end
                    self.worst("pause_late_s", late)
                    if late > END_LIMIT_S:
                        self.flag("PAUSE_PAST_END", host + str(pz.get("since")),
                                  {"game": T.GAME_NAMES[host], "since": pz.get("since"), "end": stamp(end),
                                   "late_h": round(late / 3600, 2), "until": pz.get("until"),
                                   "unit": pz.get("until_unit"), "outcome": pz.get("outcome")})
            st = LS.stopped(T, host)       # the stop as admit reads it: in effect
            if st:
                late = w.t - (S.parse_ts(st["since"]) + LS.RETRY_S)   # each stop is for RETRY_S (lane_stop's bar)
                self.worst("stop_late_s", late)
                if late > END_LIMIT_S:
                    self.flag("STOP_PAST_END", host + st["since"], {"game": T.GAME_NAMES[host], "stop": st})
        for rec in T.records("done"):
            jid = rec["job"]["id"]
            if jid in self.done_seen:
                continue
            self.done_seen.add(jid)
            res, host = rec.get("result") or {}, rec.get("host") or T.STEVE
            if host not in self.ends or rec.get("cancelled") or res.get("outcome") == "INTERRUPTED":
                continue
            sig = None if res.get("outcome") == "DONE" or res.get("cause") in OWN_PAUSE else \
                "%s/%s: %s" % (res.get("outcome"), res.get("cause"), res.get("note"))
            ends = self.ends[host]
            t_fin = S.parse_ts(rec["finished"])
            run = 0
            for _t, s in reversed(ends):
                if s != sig or sig is None:
                    break
                run += 1
            if sig is not None and run >= 2:     # the third (or later) equal ending in a row on this game
                gap = t_fin - ends[-1][0]
                self.worst("repeat_gap_s", gap, bigger_is_worse=False)
                if gap < LS.RETRY_S:
                    self.flag("REPEAT", host + sig, {"game": T.GAME_NAMES[host], "signature": sig[:90],
                                                     "in_a_row": run + 1, "gap_min": round(gap / 60, 1)})
            ends.append((t_fin, sig))
            if sig is not None:
                self.same_max = max(self.same_max, run + 1)
        mark = (T.read_json(T.q("ssh_state.json")) or {}).get("down_since")
        self.up_for = self.up_for + PASS_S if w.ssh_up() else 0
        if mark:
            late = self.up_for - PROBE_S       # testq probes a machine marked down once each PROBE_S (designed)
            self.worst("ssh_mark_late_s", late)
            if late > END_LIMIT_S:
                self.flag("SSH_MARK_PAST_END", mark, {"down_since": mark, "up_for_min": self.up_for / 60})
        if not w.ssh_up() or mark:
            self.stale.clear()
            self.free_wait = {h: 0 for h in T.STEVE_HOSTS}
            return
        now_running = {}
        for rec in T.records("running"):
            host = T.host_of(rec)
            now_running.setdefault(host, []).append(rec)
            g = w.games[host]
            a = g.att.get(rec.get("attempt") or "")
            ended = a is None or a["lost"] or a["end"] <= w.t
            held = g.win("unread") or g.win("guard")      # a result it cannot read, a guard a driver holds: they end
            jid = rec["job"]["id"]
            key = (jid, rec.get("attempt"))     # a fresh attempt each pass (a worker that loses them) is not stuck
            self.stale[key] = self.stale.get(key, 0) + 1 if ended and not held else 0
            self.worst("running_stale_passes", self.stale[key])
            if self.stale[key] > STUCK_PASSES:
                self.flag("JOB_STUCK", jid, {"job": jid, "game": T.GAME_NAMES[host], "state": "running",
                                             "attempt": rec.get("attempt"), "passes": self.stale[key]})
        pend = [j for j in T.records("pending") if T.ready(j, w.t)]
        for host in T.STEVE_HOSTS:
            g = w.games[host]
            free = (pend and not now_running.get(host) and not g.win("busy") and not g.running()
                    and not T.paused() and not T.paused(host) and not LS.stopped(T, host)
                    and (host == T.STEVE or T.steve2_on()))
            self.free_wait[host] = self.free_wait[host] + 1 if free else 0
            self.worst("pending_free_passes", self.free_wait[host])
            if self.free_wait[host] > STUCK_PASSES:
                self.flag("JOB_STUCK", "free" + host, {"game": T.GAME_NAMES[host], "state": "pending",
                                                       "jobs": len(pend), "passes": self.free_wait[host]})


@contextlib.contextmanager
def seams(w, plant=None):
    """Point the real code at the world; every original is put back."""
    saved = []

    def put(obj, name, val):
        saved.append((obj, name, getattr(obj, name)))
        setattr(obj, name, val)
    qhome = tempfile.mkdtemp(prefix="q_", dir=_SCRATCH)
    put(T, "QHOME", qhome)
    T.ensure_dirs()
    if w.reg.get("steve2", {}).get("off") is not True:
        open(T.q("steve2.on"), "w").close()
    put(time, "time", lambda: w.t)
    put(S, "utcnow", lambda: stamp(w.t))
    put(S, "new_job_id", w.new_job_id)
    put(T, "remote", w.remote)
    put(T, "subprocess", types.SimpleNamespace(run=w.git, TimeoutExpired=_subprocess.TimeoutExpired,
                                               CompletedProcess=_subprocess.CompletedProcess))
    put(LS, "subprocess", types.SimpleNamespace(run=w.systemctl, SubprocessError=_subprocess.SubprocessError,
                                                TimeoutExpired=_subprocess.TimeoutExpired))
    put(IS, "ssh_run", lambda _T, cmd: (0, "sweep: game stopped for the memory"))
    for name in ("site_stage_step", "visit_feed_step"):
        put(T, name, lambda *a, **k: None)
    put(T, "archmagi_tick", lambda **k: None)
    put(T, "companion_unready", lambda job, read=None: None)
    put(T, "companion_hold", lambda rev="origin/main": None)
    put(T, "facts_hold", lambda mod, now: None)
    put(T, "held_fill", lambda mod: None)
    put(T, "switch_applies", lambda: False)
    put(T, "fill_rank_declared", w.pick)
    put(T, "cmd_submit", w.submit)
    for mod, name, val in PLANTS.get(plant) or []:
        put({"LS": LS, "T": T}[mod], name, val)
    try:
        yield qhome
    finally:
        for obj, name, val in reversed(saved):
            setattr(obj, name, val)


_REAL_ON_FINISH = LS.on_finish


def _stop_for_ever(rec, T_, host):
    """The stop_no_end mutant: the stop on_finish made, with an end ten days on."""
    if rec:
        rec["until"] = LS.stamp(time.time() + 10 * 86400)
        S.dump(rec, LS.stop_path(T_, host))
    return rec


# A plant puts back the code before a fix (the sweep must report the fault it fixed), or breaks one step of the lane
# (each check must see the fault it is for: mutate-your-checker). (module, attribute, stand-in).
PLANTS = {
    # before 767bcaeba9 (2026-11-23; RIMMANDRAKE_END_EVERY_LANE_PAUSE_ITSELF_FORTYNINE_HOURS): no tick ended a pause
    "pause_no_end": [("LS", "step", lambda T_, hosts, now=None, active=None: [])],
    # before 767bcaeba9: an ending stopped nothing ("two equal refusals stop that game")
    "repeat": [("LS", "on_finish", lambda T_, host, job, res, cancelled, now=None: None)],
    # the checks' own mutants
    "stop_no_end": [("LS", "on_finish", lambda T_, host, job, res, cancelled, now=None:
                     _stop_for_ever(_REAL_ON_FINISH(T_, host, job, res, cancelled, now), T_, host))],
    "no_reconcile": [("T", "reconcile", lambda rec: None)],
    "no_admit": [("T", "admit", lambda status, host=None: None)],
    "no_reprobe": [("T", "PROBE_S", 10 ** 9)],
}


def run_regime(reg, plant=None, trace=None):
    """-> {violations, measures, passes, seconds}."""
    t_start = REAL_TIME()
    reg = json.loads(json.dumps(reg))
    w = World(reg)
    ck = Checks(w)
    hours = reg.get("hours", 24)
    mods = reg.get("mods", ["SimA", "SimB"])
    passes = 0
    with seams(w, plant), contextlib.redirect_stdout(io.StringIO()):
        while w.t < T0 + hours * 3600:
            w.t += PASS_S
            hand_events(w)
            T.cmd_tick(None)
            for m in mods:
                T.fill_once(argparse.Namespace(mod=m, n=4, cap=T.FILL_CAP_DEFAULT))
            T.cmd_tick(None)
            ck.after_pass()
            passes += 1
            if trace is not None and passes % reg.get("trace_every", 30) == 0:
                trace.append("%6.2fh run=%s pend=%d done=%d pz1=%s pz2=%s stop2=%s" % (
                    w.h(), [T.GAME_NAMES[T.host_of(r)] for r in T.records("running")], len(T.records("pending")),
                    len(T.records("done")), bool(T.paused()), bool(T.paused(T.STEVE2)),
                    bool(T.read_json(LS.stop_path(T, T.STEVE2)))))
        done = T.records("done")
    meas = {k: {"worst": v[0], "limit": v[1], "cases": v[2]} for k, v in ck.m.items()}
    meas["jobs_done"] = len(done)
    meas["same_refusals_max"] = ck.same_max
    meas["done_ok"] = sum(1 for r in done if (r.get("result") or {}).get("outcome") == "DONE")
    return {"violations": ck.viol, "measures": meas, "passes": passes, "seconds": round(REAL_TIME() - t_start, 2)}


def base(**kw):
    r = {"seed": 1, "hours": 24, "mods": ["SimA", "SimB"], "steve1": {}, "steve2": {}}
    r.update(kw)
    return r


def regions(quick=False):
    """The regimes of the range written on the boundary page. -> [(name, regime, plant)]."""
    out = [
        ("calm: both games free all day", base(), None),
        ("ssh flaps: down 0.5 h three times, 6 h once", base(ssh_down=[[2, 2.5], [5, 5.5], [9, 15], [20, 20.5]]), None),
        ("Steve2 refuses every job the same way all day, a backlog of 60 hand jobs",
         base(steve2={"broken": [[0, 24]]}, events=[{"kind": "jobs", "at_h": 0.1, "n": 60}]), None),
        ("Steve1 refuses every job 3-11 h", base(steve1={"broken": [[3, 11]]}), None),
        ("canary reds on Steve1 4-8 h, on Steve2 10-12 h", base(steve1={"canary": [[4, 8]]},
                                                               steve2={"canary": [[10, 12]]}), None),
        ("sync refusals on Steve1 6-7 h (an auto pause on every game)", base(steve1={"sync": [[6, 7]]}), None),
        ("crashes, lost attempts, results unreadable for an hour, a driver's run and guard",
         base(steve1={"crash": [[2, 4]], "lose": [[5, 6]], "unread": [[7, 8]], "busy": [[9, 11]]},
              steve2={"guard": [[3, 4]], "lose": [[12, 13]], "crash": [[14, 15]]}), None),
        ("hand pauses: default, 5 h, a unit for 3 h, a legacy record on each game",
         base(units={"rm-sweep-maint.service": [0, 9]},
              events=[{"kind": "pause", "at_h": 1}, {"kind": "pause", "at_h": 4, "hours": 5},
                      {"kind": "pause", "at_h": 6, "unit": "rm-sweep-maint.service"},
                      {"kind": "legacy_pause", "at_h": 12}, {"kind": "legacy_pause", "at_h": 15,
                                                               "host": T.STEVE2}]), None),
        ("a unit pause while systemd cannot answer 7-10 h",
         base(units={"rm-sweep-maint.service": [0, 8]}, systemd_unread=[[7, 10]],
              events=[{"kind": "pause", "at_h": 6, "unit": "rm-sweep-maint.service"}]), None),
        ("Steve2 off, a hand pause during an ssh outage", base(steve2={"off": True}, ssh_down=[[3, 6]],
                                                              events=[{"kind": "pause", "at_h": 2.5}]), None),
    ]
    forced = os.environ.get("STEVE_LANE_SWEEP_PLANT") or None    # the selftest's proof that the clean sweep can be red
    if quick:
        return [(n, dict(r, hours=min(r["hours"], 16)), forced or p) for n, r, p in out]
    for seed in range(2, 6):            # seeded mixes: every window kind, at random hours
        rng = random.Random(seed)

        def wins(k):
            return [[a, a + rng.uniform(0.3, 4)] for a in sorted(rng.uniform(0, 22) for _ in range(k))]
        g = lambda: {k: wins(rng.randint(0, 2)) for k in ("broken", "canary", "crash", "lose", "unread", "busy",  # noqa
                                                           "guard", "sync")}
        out.append(("mixed seed %d" % seed, base(seed=seed, steve1=g(), steve2=g(), ssh_down=wins(rng.randint(0, 2)),
                                                 events=[{"kind": "pause", "at_h": rng.uniform(0, 20),
                                                          "hours": rng.choice([None, 1, 3])},
                                                         {"kind": "jobs", "at_h": rng.uniform(0, 12),
                                                          "n": rng.randint(1, 20)}]), None))
    return [(n, r, forced or p) for n, r, p in out]


# ---------------------------------------------------------------- part C: SteveDesktop's account gate

def gate_case(plant=False, hours=8):
    """The 2026-11-26 case: SteveDesktop's account at its end while one run there only waits. -> {violations,
    refused_max_min, limit_min, switches, gate_reads, plant}. Runs in its own process (account_plan_sweep sets its
    folders at import)."""
    sys.path.insert(0, UTILS)
    import account_plan_sweep as APS
    AP = APS.AP
    cur = []

    class GateWorld(APS.World):
        def __init__(self, reg):
            super().__init__(reg)
            cur.append(self)
            self.refused_run, self.refused_max, self.gate_reads = 0.0, 0.0, 0
            start = self.steve.start

            def first_waits(t, forever=False):      # its first run never ends and hears no save order
                start(t, forever=forever or self.steve.seq == 0)
            self.steve.start = first_waits

        def ms_order(self, alias, units, text):
            self.steve.order({r["name"] for r in self.steve.runs}, "at_easy_spot", self.t)
            return True, "sweep: the save order reached %d run(s)" % len(self.steve.runs)

        def ms_stop(self, alias, units, why):
            n = len(self.steve.runs)
            self.steve.runs = []
            self.events.append({"kind": "stop", "t": self.t, "machine": APS.STEVE, "runs": n})
            return True, "sweep: %d run(s) stopped (write-now)" % n

        def gate_steve(self):
            ok, why = super().gate_steve()
            self.gate_reads += 1
            return ok, why

        def advance(self, secs, plan):
            t0 = self.t
            super().advance(secs, plan)
            ok, _ = super().gate_steve()
            self.refused_run = 0.0 if ok else self.refused_run + (self.t - t0) / 60
            self.refused_max = max(self.refused_max, self.refused_run)

    real_tick, real_bound = AP.tick, AP.machine_bound_s

    def tick(dry=False, seams=None):
        m = (seams or {}).get("machines")
        if m is not None and cur:
            m.setdefault("order", cur[0].ms_order)
            m.setdefault("stop", cur[0].ms_stop)
        return real_tick(dry=dry, seams=seams)
    real_world = APS.World
    APS.World, AP.tick = GateWorld, tick
    if plant:   # before 44a3797f6e: no bound, so no write-now stop; the switch waits for the run for ever
        AP.machine_bound_s = lambda plan, d: (10 ** 9, "sweep plant: no bound")
    try:
        reg = APS.base(hours=hours, steve={"account": "same", "runs": {"mode": "always", "n": 2, "save_min": 20},
                                           "burn": {"kind": "const", "rate": 2}})
        out = APS.run_regime(reg)
    finally:
        APS.World, AP.tick, AP.machine_bound_s = real_world, real_tick, real_bound
    w = cur[0]      # the run's world (foresight_bound builds a second)
    return {"violations": [v for v in out["violations"] if v["check"] == "STUCK" and "STUCK" not in BLIND],
            "other_violations": [v["check"] for v in out["violations"] if v["check"] != "STUCK"],
            "refused_max_min": round(w.refused_max, 1), "limit_min": (APS.K_STUCK + 6) * APS.PASS_S / 60,
            "gate_reads": w.gate_reads, "switches": out["measures"].get("switch_list"), "plant": plant,
            "seconds": out["seconds"]}


# The measured faults, planted: (regime, plant, the check that must report it). Each regime is the evidence's own shape.
PLANTED = {
    # 2026-11-15..17: a pause with no end of its own (a record of the build before 767bcaeb) held the lane 49.3 h
    "pause_no_end": (base(hours=51.3, events=[{"kind": "legacy_pause", "at_h": 2.0}]), "pause_no_end", "PAUSE_PAST_END"),
    # 2026-11-23: Steve2 gave the same refusal 47 times in 11 h; a backlog of hand jobs (the filler's brake holds only
    # its own)
    "repeat": (base(hours=11, steve2={"broken": [[0, 11]]}, events=[{"kind": "jobs", "at_h": 0.1, "n": 60}]),
               "repeat", "REPEAT"),
}
# Each other check, red on a fault of its own kind.
MUTANTS = {
    "stop_no_end": (base(hours=3, steve2={"broken": [[0, 3]]}, events=[{"kind": "jobs", "at_h": 0.1, "n": 20}]),
                    "stop_no_end", "STOP_PAST_END"),
    "no_reconcile": (base(hours=3), "no_reconcile", "JOB_STUCK"),
    "no_admit": (base(hours=3, events=[{"kind": "jobs", "at_h": 0.1, "n": 4}]), "no_admit", "JOB_STUCK"),
    "no_reprobe": (base(hours=3, ssh_down=[[0.5, 1]]), "no_reprobe", "SSH_MARK_PAST_END"),
}


def _one(arg):
    name, reg, plant = arg
    if name.startswith("gate"):
        return name, gate_in_process(bool(plant))
    return name, run_regime(reg, plant)


def sweep_all(cases, workers=None):
    """Run [(name, regime, plant)] (a name starting "gate": part C, plant True/False) in parallel processes (each regime has its
    own queue home and clock). -> {name: out}, in the order given."""
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    with ProcessPoolExecutor(max_workers=workers or min(len(cases), os.cpu_count() or 2),
                             mp_context=multiprocessing.get_context("fork")) as ex:
        return dict(ex.map(_one, cases))


# budget: danger=a part C that never ends holds the selftest and the publish door; evidence=one measured run
# budget: 2026-11-27, 2.8 s alone (shipped and planted), under 40 s in the full pool; longest=40s (one measured run)
GATE_S = 400


def gate_in_process(plant=False):
    """Part C in its own process. -> its JSON, or {"error"}."""
    r = _subprocess.run([sys.executable, os.path.abspath(__file__), "gate"] + (["--plant"] if plant else []),
                        capture_output=True, text=True, timeout=GATE_S)
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"error": (r.stdout + r.stderr)[-1500:]}


def line(name, out):
    v = out["violations"]
    m = out["measures"]
    worst = "; ".join("%s worst %s limit %s cases %s" % (k, m[k]["worst"], m[k]["limit"], m[k]["cases"])
                      for k in ("pause_late_s", "stop_late_s", "repeat_gap_s", "running_stale_passes",
                                "pending_free_passes", "ssh_mark_late_s"))
    return "%-8s %s | %d passes %.1f s, %d done (%d DONE) | %s%s" % (
        "VIOLATES" if v else "ok", name, out["passes"], out["seconds"], m["jobs_done"], m["done_ok"], worst,
        "" if not v else " | " + "; ".join("%s at %sh %s" % (x["check"], x["h"], json.dumps(x["detail"])[:240])
                                            for x in v[:4]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("grid")
    g.add_argument("--quick", action="store_true")
    o = sub.add_parser("one")
    o.add_argument("regime")
    o.add_argument("--plant", choices=sorted(PLANTS))
    c = sub.add_parser("gate")
    c.add_argument("--plant", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "gate":
        with contextlib.redirect_stdout(io.StringIO()):
            out = gate_case(a.plant)
        print(json.dumps(out))
        return 1 if out["violations"] else 0
    if a.cmd == "one":
        tr = []
        out = run_regime(json.loads(a.regime), a.plant, tr)
        print("\n".join(tr))
        print(line("one", out))
        return 1 if out["violations"] else 0
    bad = 0
    lines = []
    cases = regions(a.quick)
    outs = sweep_all(cases + [("gate", None, False)])
    for name, _reg, _plant in cases:
        bad += bool(outs[name]["violations"])
        lines.append(line(name, outs[name]))
    gc = outs["gate"]
    lines.append("%-8s account gate: a run that only waits on SteveDesktop's account at its end | refused for %s min "
                 "at most, limit %s min, %s gate reads | %s" % (
                     "VIOLATES" if gc.get("violations") or gc.get("error") else "ok", gc.get("refused_max_min"),
                     gc.get("limit_min"), gc.get("gate_reads"), gc.get("error") or gc.get("switches")))
    bad += bool(gc.get("violations") or gc.get("error"))
    print("\n".join(sorted(lines, key=lambda s: s.startswith("VIOLATES"))))
    print("%d regime(s) VIOLATE" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
