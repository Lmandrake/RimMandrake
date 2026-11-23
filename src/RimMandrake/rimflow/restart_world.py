#!/usr/bin/env python3
"""restart_world.py - the rig of selftest_handoff_restart.py (it was selftest_idle_bringback.py's World; that machine was
removed 2026-11-23). Every window here is a REAL child process with a real sessions/<pid>.json, a transcript on disk and
a real armed doorbell, in a temp CLAUDE_CONFIG_DIR and a temp dispatcher state. dispatcher.tick() runs with obs=None, so
default_obs, decide, execute, the ring files and kill_pid are the production code on the production thresholds. The clock
is simulated; the tile is the harness, which claims the killed record exactly as `seat_restart.py intile` does. Stubbed:
only `claude agents` (listing the stubs), `rimflow next --peek`, the bridge and PAUSE readings, and the launch of a
fallback tile.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="restart_world_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(TMP, "claude")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")
os.environ["RM_SEAT_LOG_DIR"] = os.path.join(TMP, "seat_log")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "testq")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import dispatcher as D  # noqa: E402
import doorbell  # noqa: E402
import seat_restart as SR  # noqa: E402

SEAT = "FOUNDRY"
FAILS = []
SHIPPED = D.load_schedule()
REAL = json.loads(json.dumps(SHIPPED))
# the owner tunes these; the cases run on pinned numbers
REAL.update(tick_s=120, handoff_s=600)
# a worker seat of the old FOUNDRY shape: the live schedule has none since it retired (owner by card 2026-11-02)
REAL["seats"].setdefault(SEAT, {"enabled": True, "wake": True, "recover_dead": False, "session_name": "AGENT FOUNDRY", "clone": "/home/mandrake/rm/foundry", "model": "sonnet"})
REAL["seat_restart"]["seats"].setdefault(SEAT, {"backstop": True, "backstop_ctx_tokens": 110000, "backstop_busy": True, "backstop_hard_tokens": 200000, "backstop_hard_alarm_s": 3600, "backstop_idle_s": 1800, "grace_s": 20, "quiet_s": 20, "helper_stale_s": 1800})
TICK = REAL["tick_s"]
LIMIT = 1800


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git_clone(clone):
    """A real git clone with the seat's shard published: a bring-back holds until the shard is on origin, and a clone git
    cannot read holds it for good (unpublished_shard, UNMEASURED), so the shard check runs here as production code."""
    rel = os.path.join("infrastructure", "state", "ledger", "events", SEAT + ".jsonl")
    open(os.path.join(clone, rel), "w").close()
    for argv in (["init", "-q", "-b", "main"], ["add", rel],
                 ["-c", "user.name=selftest", "-c", "user.email=selftest@invalid", "commit", "-q", "--no-verify", "-m", "shard"],
                 ["update-ref", "refs/remotes/origin/main", "HEAD"]):
        subprocess.run(["git"] + argv, cwd=clone, check=True, capture_output=True, timeout=60)


class World:
    def __init__(self, name, ignores=True, fallbacks=None):
        self.dir = os.path.join(TMP, name)
        os.environ["RM_DISPATCHER_STATE"] = self.state = os.path.join(self.dir, "state")
        os.environ["CLAUDE_CONFIG_DIR"] = self.claude = os.path.join(self.dir, "claude")
        os.environ["RM_OPS_WATCH_DIR"] = self.ops = os.path.join(self.dir, "ops")
        self.clone = os.path.join(self.dir, "foundry")
        for d in (self.state, os.path.join(self.claude, "sessions"), self.ops,
                  os.path.join(self.clone, "infrastructure", "state", "ledger", "events")):
            os.makedirs(d)
        git_clone(self.clone)
        self.t0 = time.time() - 8 * 3600     # all of it in the past: the quiet checks read the wall clock
        self.now = self.t0
        self.windows = []
        self.gone = []
        self.n = 0
        self.ignores = ignores
        self.queue = {"id": "READY_TICKET_WAITING"}
        self.kills = []
        self.claimed = set()
        self.tile_delay = 0
        self.owed = None
        self.first_prompt = None
        self.takes_on_ring = False
        self.acts = []
        self.sch = self.schedule()

    def schedule(self):
        s = json.loads(json.dumps(REAL))
        s["seats"] = {SEAT: dict(s["seats"][SEAT], clone=self.clone)}
        s["seat_restart"]["seats"] = {SEAT: s["seat_restart"]["seats"][SEAT]}
        s["no_handoff"]["conductor_log"] = os.path.join(self.dir, "conductor_log.md")
        for k in ("roles", "measure", "login_watch", "signal_watch", "long_helper", "golive", "helper_budget"):
            s.pop(k, None)
        s.update(publish=False, ledger_notes=False, alarm_item=None)
        p = os.path.join(self.dir, "sched.json")
        with open(p, "w") as f:
            json.dump(s, f)
        return D.load_schedule(p)

    def iso(self, t):
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + "Z"

    def tx(self, w):
        return SR.transcript_path(self.clone, w["sid"])

    def write(self, w, rec):
        with open(self.tx(w), "a") as f:
            f.write(json.dumps(dict(rec, timestamp=self.iso(self.now), sessionId=w["sid"])) + "\n")

    def end_turn(self, w):
        self.write(w, {"type": "assistant", "message": {"stop_reason": "end_turn", "content": [{"type": "text", "text": "ok"}],
                                                        "usage": {"input_tokens": 1000}}})

    def spawn(self, status="idle", arm=True):
        self.n += 1
        p = subprocess.Popen(["sleep", "86400"])
        threading.Thread(target=p.wait, daemon=True).start()      # reap it, or a killed stub stays a zombie
        w = {"sid": "sid-%d" % self.n, "pid": p.pid, "proc": p, "status": status}
        with open(os.path.join(self.claude, "sessions", "%d.json" % p.pid), "w") as f:
            json.dump({"pid": p.pid, "sessionId": w["sid"], "cwd": self.clone, "name": "AGENT " + SEAT, "status": status,
                       "procStart": SR.proc_start(p.pid)}, f)
        os.makedirs(os.path.dirname(self.tx(w)), exist_ok=True)
        if self.first_prompt:
            self.write(w, relaunch_record(self.first_prompt))
        self.end_turn(w)
        if arm:
            doorbell.arm(SEAT, w["sid"], pid=p.pid)
        self.windows.append(w)
        return w

    def agents(self):
        return {"state": "MEASURED", "sessions": [
            {"name": "AGENT " + SEAT, "status": w["status"], "sessionId": w["sid"], "pid": w["pid"], "kind": "interactive",
             "cwd": self.clone} for w in self.windows]}

    def human(self, w):
        self.write(w, {"type": "user", "origin": {"kind": "human"}, "message": {"role": "user", "content": "looking at this"}})
        self.end_turn(w)

    def take(self, what="claim"):
        p = os.path.join(self.clone, "infrastructure", "state", "ledger", "events", SEAT + ".jsonl")
        with open(p, "a") as f:
            f.write(json.dumps({"event": what, "id": self.queue["id"] if self.queue else "X", "seat": SEAT,
                                "ts": self.iso(self.now)}) + "\n")

    def tile(self):
        """The WT profile's seat_loop: the killed record, claimed once, becomes a new window."""
        rec = SR.killed_reading(SEAT)
        if not rec or rec.get("killed_at") in self.claimed or rec.get("aborted"):
            return
        if SR.intile_claim(SEAT, rec["killed_at"] + 5):    # the tile claims seconds after its window died
            self.claimed.add(rec["killed_at"])
            self.owed = self.now + self.tile_delay
            self.first_prompt = rec["argv"][-1]              # what the real tile hands the new window

    def step(self):
        self.now += TICK
        for w in list(self.windows):
            if w["proc"].poll() is not None:     # SIGTERM really landed
                self.windows.remove(w)
                self.gone.append(w)
                self.kills.append(self.now)
        if self.owed is not None and self.now >= self.owed:
            self.owed = None
            self.spawn()
        for w in self.windows:
            ring = doorbell.take_ring(SEAT, session_id=w["sid"])
            if ring:
                self.write(w, {"type": "user", "origin": {"kind": "task-notification"},
                               "message": {"role": "user", "content": "[RimFlow Dispatcher] ring"}})
                if self.takes_on_ring:
                    self.take()
                self.end_turn(w)
                doorbell.arm(SEAT, w["sid"], pid=w["pid"])
        acts = D.tick(self.sch, True, now=self.now, fx={"seat_restart": {"fallback": self.fallback}})
        self.acts += acts
        self.tile()
        return acts

    def fallback(self, argv):
        self.acts.append({"do": "fallback_ran"})
        return "ran"

    def run(self, seconds):
        end = self.now + seconds
        while self.now < end:
            self.step()

    def until(self, cond):
        """Ticks until cond, at most 12 past the limit: a machine that never fires fails its checks, it does not hang."""
        while not cond() and self.now - self.t0 < LIMIT + 12 * TICK:
            self.step()

    def count(self, do, kind=None):
        return sum(1 for a in self.acts if a.get("do") == do and (kind is None or a.get("kind") == kind))

    def close(self):
        for w in self.windows:
            w["proc"].kill()


def relaunch_record(prompt):
    """What a relaunch's first prompt becomes in a real transcript: every structural field says a person typed it."""
    return {"type": "user", "promptSource": "typed", "turnOrigin": "human", "origin": {"kind": "human"},
            "message": {"role": "user", "content": prompt}}


def patch(world):
    D.observe_agents = world.agents
    D.peek_ticket = lambda clone, seat: world.queue
    D.paused_now = lambda: None
    SR.paused_now = lambda: None
    SR.bridge_reading = lambda seat: {"state": "MEASURED", "holders": []}


def start(name, **kw):
    w = World(name, **kw)
    patch(w)
    w.spawn()
    return w
