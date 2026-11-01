#!/usr/bin/env python3
"""selftest_idle_bringback.py — DI1 + CK4: the planted fault on the real path.

IDLE_SEAT_RESTART_BUILD_BRINGS_QUIET_BACK. Every window here is a REAL child process with a real sessions/<pid>.json,
a transcript on disk and a real armed doorbell, in a temp CLAUDE_CONFIG_DIR and a temp dispatcher state. dispatcher.tick()
runs with obs=None, so default_obs, decide, execute, the ring files and kill_pid are the production code on the production
thresholds (read from dispatcher_schedule.json). The clock is simulated; the tile is the harness, which claims the killed
record exactly as `seat_restart.py intile` does. Stubbed: only `claude agents` (listing the stubs), `rimflow next --peek`,
the bridge and PAUSE readings, and the launch of a fallback tile.
  ignores      a window that ignores rings is SIGTERMed once at the limit, not before; its replacement, which ignores
               them too, raises one incident (one told row, one Conductor line) after fresh_take_s; two more hours of
               ticks bring no second kill
  takes        a replacement that takes work ends the machine: no incident
  human        a human input in the window leaves it alone at the limit
  overlap      a replacement slow to arrive, and two windows at once, never get a second restart
  work         work taken without a ring, an empty queue: no restart
  no doorbell  a window no ring can reach is brought back too
  off          the key unset: the machine does not exist
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
TMP = tempfile.mkdtemp(prefix="selftest_idle_bringback_")
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
REAL = D.load_schedule()
TICK = REAL["tick_s"]
LIMIT = REAL["idle_bringback_after_min"] * 60
FRESH = REAL["fresh_take_s"]


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


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
        self.takes_on_ring = False
        self.acts = []
        self.sch = self.schedule()

    def schedule(self):
        s = json.loads(json.dumps(REAL))
        s["seats"] = {SEAT: dict(s["seats"][SEAT], clone=self.clone)}
        s["seat_restart"]["seats"] = {SEAT: s["seat_restart"]["seats"][SEAT]}
        s["no_handoff"]["conductor_log"] = os.path.join(self.dir, "conductor_log.md")
        for k in ("roles", "measure", "login_watch", "signal_watch", "long_helper", "golive"):
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

    def incidents(self):
        return [a for a in self.acts if a.get("kind") == "idle_bringback:" + SEAT and a.get("result") != "repeat alarm (rate-limited)"]

    def told(self):
        try:
            with open(os.path.join(self.ops, "told.jsonl")) as f:
                return [r for r in map(json.loads, f) if str(r.get("kind")).startswith("idle_bringback:")]
        except FileNotFoundError:
            return []

    def close(self):
        for w in self.windows:
            w["proc"].kill()


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


def test_ignores():
    w = start("ignores")
    first = w.windows[0]
    w.run(LIMIT - 2 * TICK)
    check(w.kills == [] and first["proc"].poll() is None, "not restarted before the limit (%d rings so far)" % w.count("ring"))
    check(w.count("ring") >= 2, "it was rung first: %d rings" % w.count("ring"))
    w.until(lambda: w.count("restart_verified"))
    check(len(w.kills) == 1 and first["proc"].poll() is not None, "restarted at the limit: %s s after the start" % (
        [int(k - w.t0) for k in w.kills]))
    check(w.kills and LIMIT <= w.kills[0] - w.t0 <= LIMIT + 5 * TICK, "the kill landed within a few ticks of %d s" % LIMIT)
    check(len(w.windows) == 1 and w.windows[0]["sid"] == "sid-2", "one fresh window")
    check(w.count("restart_verified") == 1, "the fresh window was verified")
    check(not w.incidents(), "no incident yet")
    w.run(FRESH + 4 * TICK)
    check(w.count("ring") >= 4, "the fresh window was rung too: %d rings" % w.count("ring"))
    check(len(w.incidents()) == 1, "a fresh window that takes nothing raises the incident (%d)" % len(w.incidents()))
    rows = w.told()
    check(len(rows) == 1 and rows[0]["kind"] == "idle_bringback:" + SEAT, "one signal in the told ledger: %s" % str(rows)[:200])
    with open(w.sch["no_handoff"]["conductor_log"]) as f:
        log = f.read()
    check(log.count("still takes no work") == 1, "one RAISE FIRST line in the Conductor's log")
    w.run(2 * 3600)
    check(len(w.kills) == 1 and w.windows and w.windows[0]["proc"].poll() is None,
          "two more hours: no second restart (kills %d)" % len(w.kills))
    check(len(w.told()) == 1, "one outage stays one incident (%d rows)" % len(w.told()))
    check(w.count("restart_request") == 1, "one restart request in the whole run (%d)" % w.count("restart_request"))
    w.take()
    w.run(2 * TICK)
    check(w.count("bringback_end") == 1, "a real take ends the incident's watch")
    check(sum(1 for a in w.acts if a.get("kind") == "idle_bringback:" + SEAT) <= 3, "the incident is not one journal line per tick")
    w.close()


def test_takes():
    w = start("takes")
    w.until(lambda: w.kills)
    check(len(w.kills) == 1, "restarted once")
    w.takes_on_ring = True
    w.run(FRESH + 4 * TICK)
    check(not w.incidents() and not w.told(), "a fresh window that takes the ring raises nothing")
    check(len(w.kills) == 1, "and is not restarted")
    w.close()


def test_human():
    w = start("human")
    w.run(LIMIT - 3 * TICK)
    w.human(w.windows[0])
    w.run(10 * TICK)
    check(w.kills == [] and w.count("restart_request") == 0, "a human in the window at the limit: left alone")
    check(w.count("bringback_end") >= 1, "the watch ended, with the reason journalled")
    w.close()
    w = start("human_pending")               # he types inside the grace: the pending restart cancels, and no kill follows
    w.run(LIMIT)
    w.until(lambda: w.count("restart_request"))
    w.human(w.windows[0])
    w.run(6 * TICK)
    check(w.kills == [], "a human arriving during the restart's grace cancels it (kills %d)" % len(w.kills))
    w.close()


def test_overlap():
    w = start("overlap")
    w.tile_delay = 9 * TICK                  # the first replacement is slow, past the restart's own deadline
    w.until(lambda: w.kills)
    w.run(2 * TICK)
    check(len(w.kills) == 1 and not w.windows, "killed, replacement not yet up")
    w.run(9 * TICK)
    check(len(w.windows) == 1 and len(w.kills) == 1 and w.count("restart_request") == 1,
          "a slow replacement gets no second restart beside it, and it does arrive")
    check(len(w.incidents()) == 1 and "no replacement" in w.incidents()[0]["why"], "the failed relaunch is the incident")
    w.run(FRESH + 2 * 3600)
    check(len(w.kills) == 1 and w.count("restart_request") == 1, "never a second one afterwards either")
    w.close()
    w = start("two_windows")
    w.spawn(arm=False)                       # the fallback and the tile both landed
    w.run(LIMIT + 6 * TICK)
    check(w.kills == [] and w.count("restart_request") == 0, "two windows on the seat: neither is chosen for a kill")
    w.close()


def test_work():
    w = start("work")
    w.run(LIMIT - 4 * TICK)
    w.take()                                 # a take no ring saw: the seat went straight to its queue
    w.run(6 * TICK)
    check(w.kills == [] and w.count("bringback_end") >= 1, "work taken without a ring: no restart")
    w.close()
    w = start("empty")
    w.run(LIMIT - 4 * TICK)
    w.queue = {}
    w.run(10 * TICK)
    check(w.kills == [] and w.count("restart_request") == 0, "the queue ran dry: an idle window is correct")
    w.close()


def test_no_doorbell():
    w = start("no_doorbell")
    os.remove(doorbell.armed_path(SEAT))
    w.run(LIMIT + 8 * TICK)
    check(len(w.kills) == 1, "a window with no doorbell, which no ring can reach, is brought back (kills %d)" % len(w.kills))
    w.close()


def test_off():
    w = start("off")
    w.sch.pop("idle_bringback_after_min")
    w.run(LIMIT + 6 * TICK)
    check(w.kills == [] and w.count("restart_request") == 0, "the key unset: no bring-back")
    w.close()


def test_schedule():
    check(REAL.get("idle_bringback_after_min") == 30, "dispatcher_schedule.json: idle_bringback_after_min 30")
    check(REAL.get("fresh_take_s") == 900, "dispatcher_schedule.json: fresh_take_s 900")
    check(SR.bb_rule(REAL) == (1800, 900), "the rule reads it")
    try:
        SR.bb_rule({"idle_bringback_after_min": "30"})
        check(False, "a malformed limit is refused")
    except ValueError:
        check(True, "a malformed limit is refused")


if __name__ == "__main__":
    try:
        for t in (test_schedule, test_ignores, test_takes, test_human, test_overlap, test_work, test_no_doorbell, test_off):
            t()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("FAILED %d: %s" % (len(FAILS), FAILS) if FAILS else "PASS")
    sys.exit(1 if FAILS else 0)
