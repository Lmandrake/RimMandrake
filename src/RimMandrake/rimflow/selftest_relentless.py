#!/usr/bin/env python3
"""relentless.py with planted faults: worker dies, same failure repeats, stale worker publishes, spend limit, restart
returns to the top, share 0 and 1, plus crash recovery, a two-way lease race and live_line. No units, no ledger, no
network: Effects is replaced by FakeWorld."""
import glob
import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_line  # noqa: E402
import relentless as R  # noqa: E402

RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, share=0.5, max_workers=2,
             enrol_per_tick=50, max_queued=50, run_reserve=1000, item_spend_limit=10**7, day_spend_limit=10**9,
             staffing=None, circling=None)
STAFF = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json"))["staffing"], hold_s=600)
FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class FakeWorld:
    def __init__(self, n=4):
        self.items = {"I%d" % i: "proposed" for i in range(n)}
        self.up = {}            # unit -> alive
        self.launches = []
        self.closes = []
        self.notes = []
        self.needs = []
        self.tok = 0
        self.lfail = None
        self.close_fail = None
        self.unkillable = set()
        self.stops = []
        self.mem = 30.0
        self.is_pub = True
        self.live_broken = None
        self.touched = ["src/x.py"]
        self.pause = False
        self.bounce = set()
        self.owners = {}
        self.budget_v = 8
        self.helpers = 0
        self.burn_v = 1.0
        self.oom = 0
        self.words = set()
        self.heard = False
        self.fits = True
        self.takes = []
        self.take_fail = None
        self.on_settle = None
        self.alarms = []
        self.alarm_fail = None

    def budget(self): return self.budget_v
    def head_helpers(self): return self.helpers
    def burn(self): return self.burn_v
    def oom_kills(self): return self.oom
    def seat_words(self): return self.words
    def seat_heard(self, item, since): return self.heard
    def foreign_fits(self, item): return self.fits
    def settle_wait(self, s):
        if self.on_settle:
            self.on_settle()
    def ledger_take(self, item):
        if self.take_fail:
            return self.take_fail
        self.takes.append(item)
        self.owners[item] = "BENCH"
    def staffing_alarm(self, item, text):
        if self.alarm_fail:
            return self.alarm_fail
        self.alarms.append(text)

    def sync(self): pass
    def flush(self): return None

    def pool_order(self, r):
        return [i for i in sorted(self.items) if self.items[i] in ("proposed", "ready")
                and i not in getattr(self, "taken", ())], None

    def item_state(self, item):
        st = self.items.get(item)
        return None if st is None else {"state": st, "lease": None, "needs": "offline",
                                        "owner": self.owners.get(item, "BENCH")}

    def item_text(self, item): return "text of " + item
    def ledger_start(self, item):
        self.items[item] = "doing"
    def ledger_close(self, item, sha, reason, live=None):
        if self.close_fail:
            why, self.close_fail = self.close_fail, None
            return why
        self.closes.append((item, sha))
        self.items[item] = "done"
    reclaim_fail = None
    def ledger_reclaim(self, item):
        if self.reclaim_fail:
            why, self.reclaim_fail = self.reclaim_fail, None
            return why
        self.items[item] = "ready"
    def ledger_note(self, item, text): self.notes.append(text)
    def ledger_needs_owner(self, item, why): self.needs.append(item)
    def ledger_needs(self, item, to, why): self.needs.append((item, to))
    def clone_path(self, item, q=0): return "/c/%s.%d" % (item, q)
    def prepare(self, st):
        return "clone failed: POOL REFUSED: pool full" if self.refuse else None
    # the clone pool: path -> {busy, kept, real}. Empty unless a test plants one
    pool = {}
    pool_max = 10
    refuse = False
    jams = ()
    jam_fail = None
    def pool_clones(self): return sorted(self.pool)
    def pool_load(self): return len(self.pool), 0, self.pool_max, 10**12
    def clone_present(self, c): return c in self.pool
    def clone_busy(self, c): return self.pool[c].get("busy", False)
    def clone_idle_s(self, c): return 7200
    def clone_wip(self, c): return {"kept": self.pool[c].get("kept", False), "real": self.pool[c].get("real", [])}
    def remove_clone(self, st, before=None):
        if st.get("clone") not in self.pool:
            return None
        out = "/bundle/" + st["clone"]
        if before:
            before(out)
        del self.pool[st["clone"]]
        return out
    def conductor_alarm(self, text):
        if self.jam_fail:
            return self.jam_fail
        self.jams = list(self.jams) + [text]
    def clean_checkout(self, st, sha):
        self.mem_once = getattr(self, "mem_after", None)
        if self.refuse or (self.pool and len(self.pool) >= self.pool_max):
            return None, "checker clone failed: scratch_clone: FAILED: POOL REFUSED: pool full: 10 clones, cap 10\n"
        if self.pool:
            self.pool["/c/check-" + st["item"]] = {"busy": True}
        return "/c/check", None
    def published(self, sha): return self.is_pub
    def changed(self, base, sha, item): return self.touched
    def head(self): return "base"
    def commit_time(self, sha): return 0

    def launch(self, st, run, prompt, agent, clone, max_s, env):
        if self.lfail:
            return self.lfail
        self.launches.append((st["item"], run["unit"], prompt, agent, clone))
        self.up[run["unit"]] = True
        return None

    def alive(self, run): return bool(run) and self.up.get(run["unit"], False)
    def stop(self, run, force):
        self.stops.append((run["unit"], force))
        if run["unit"] not in self.unkillable:
            self.up[run["unit"]] = False
    def tokens(self, run): return self.tok
    def activity(self, st): return 0
    def mem_gb(self):
        v, self.mem_once = getattr(self, "mem_once", None), None
        return self.mem if v is None else v
    def paused(self): return self.pause
    def live_check(self, line, nb): return self.live_broken


class Rig:
    def __init__(self, n=4, **rules):
        self.d = tempfile.mkdtemp(prefix="rl-")
        self.s = R.Store(self.d)
        self.w = FakeWorld(n)
        self.r = dict(RULES, **rules)
        self.now = 1000000.0

    def tick(self, dt=120):
        self.now += dt
        return R.tick(self.s, self.w, self.r, self.now)

    def st(self, i):
        return self.s.load(i)

    def done(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def run_one(self, i):
        """Tick until `i` is running."""
        for _ in range(12):
            if self.st(i) and self.st(i)["status"] == "running":
                return
            self.tick()
        raise AssertionError("%s never ran: %s" % (i, self.st(i)))


def t_worker_dies():
    x = Rig(n=2, share=1.0, max_workers=1)
    x.run_one("I0")
    st = x.st("I0")
    g, u, clone = st["gen"], st["run"]["unit"], st["clone"]
    R.learn(x.s, "I0", g, "found the seam")
    R.contract(x.s, "I0", g, "run the test")
    x.now += 400                # past launch grace
    x.w.tok = 500
    x.w.up[u] = False
    x.tick()
    st = x.st("I0")
    ok(st["gen"] > g, "worker dies: fenced at once")
    x.run_one("I0")
    st = x.st("I0")
    ok(st["clone"] == clone, "worker dies: replacement keeps the clone")
    ok(x.w.launches[-1][1] != u and "found the seam" in x.w.launches[-1][2], "worker dies: replacement reads the record")
    ok(st["contract"]["proof"] == "run the test", "worker dies: contract survives")
    ok(st["spent"] == 500, "worker dies: the dead run is charged, once")
    x.done()


def t_same_failure():
    x = Rig(n=1, share=1.0)
    x.tick()
    for n in range(3):
        x.run_one("I0")
        st = x.st("I0")
        R.snag(x.s, "I0", st["gen"], "tests_red", "red again", x.r, now=x.now)
        x.w.up[st["run"]["unit"]] = False
    st = x.st("I0")
    ok(st["approach"] == "redesign" and st["approach_changes"] == 1, "3 same failures: approach changes")
    ok(st["status"] != "held", "3 same failures: never stops")
    x.run_one("I0")
    ok("REDESIGN" in x.w.launches[-1][2], "redesign brief reaches the next worker")
    for n in range(3):
        x.run_one("I0")
        st = x.st("I0")
        R.snag(x.s, "I0", st["gen"], "tests_red", "red again", x.r, now=x.now)
        x.w.up[st["run"]["unit"]] = False
    ok(x.st("I0")["approach"] == "pilot", "second round flips to pilot")
    x.run_one("I0")
    ok(x.w.launches[-1][3] == x.r["pilot_agent"], "pilot approach launches the test pilot agent")
    # rotating slugs
    y = Rig(n=1, share=1.0, unchanged_returns_limit=4)
    y.tick()
    for n in range(4):
        y.run_one("I0")
        st = y.st("I0")
        R.snag(y.s, "I0", st["gen"], "slug%d" % n, "x", y.r, now=y.now)
        y.w.up[st["run"]["unit"]] = False
    ok(y.st("I0")["approach"] == "redesign", "rotating failure slugs still change the approach")
    x.done(), y.done()


def expect_fence(fn, what):
    try:
        fn()
    except R.Fenced:
        ok(True, what)
        return
    ok(False, what)


def t_stale_worker():
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    g = st["gen"]
    R.contract(x.s, "I0", g, "p")
    R.snag(x.s, "I0", g, "wedged", "x", x.r, now=x.now)     # the fence moved; the old process lives on
    expect_fence(lambda: R.beat(x.s, "I0", g), "stale: beat refused")
    expect_fence(lambda: R.learn(x.s, "I0", g, "late"), "stale: learn refused")
    expect_fence(lambda: R.finish(x.s, "I0", g, "abc", "e"), "stale: finish refused")
    expect_fence(lambda: R.snag(x.s, "I0", g, "x", "y", x.r), "stale: snag refused")
    ok(x.s.read_receipt("I0", g) is None, "stale: no receipt written")
    ok(R.fence_check(x.s, "I0", g) is not None, "stale: push refused")
    with open(os.path.join(x.d, "relentless.json"), "w") as f:
        json.dump({}, f)
    gitd = os.path.join(x.d, "cl", ".git")
    os.makedirs(gitd)
    with open(os.path.join(gitd, "relentless.json"), "w") as f:
        json.dump({"item": "I0", "gen": g}, f)
    ok(R.hook_fence(os.path.join(x.d, "cl"), x.s), "stale: pre-push hook refuses from the marker")
    ok(R.hook_fence(x.d, x.s) is None, "no marker: the hook says nothing")
    ok(R.guard("close", "I0", [], env={}, store=x.s), "stale: rimflow close refused")
    ok(R.guard("close", "I0", ["--owner-said", "x"], env={}, store=x.s) is None, "his word passes the guard")
    ok(R.guard("close", "I0", [], env={"RELENTLESS_SUPERVISOR": "1"}, store=x.s) is None, "supervisor passes the guard")
    ok(R.guard("note", "I0", [], env={}, store=x.s) is None, "a note is not guarded")
    x.done()


def t_stop_order():
    x = Rig(n=1, share=1.0, stale_s=100, launch_grace_s=10)
    x.run_one("I0")
    st = x.st("I0")
    u = st["run"]["unit"]
    x.w.unkillable.add(u)
    g = st["gen"]
    x.tick(200)
    ok(x.st("I0")["gen"] > g and x.st("I0")["status"] == "stopping", "stale unit: fenced before it is gone")
    n = len(x.w.launches)
    x.tick(10)
    ok(len(x.w.launches) == n, "no replacement while the old unit is up")
    x.tick(x.r["stop_force_s"])
    ok(any(f for _, f in x.w.stops), "force after stop_force_s")
    x.tick(x.r["stop_quarantine_s"])
    st = x.st("I0")
    ok(st["status"] in ("queued", "running") and st["quarantined"], "unkillable unit is quarantined, not parked")
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "running" and st["clone"].endswith(".1"), "replacement after quarantine gets a new clone")
    x.done()


def t_spend():
    x = Rig(n=2, share=1.0, max_workers=1, item_spend_limit=1000)
    x.run_one("I0")
    st = x.st("I0")
    x.now += 400
    x.w.tok = 2000
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    x.tick()
    ok(x.st("I0")["status"] == "held", "spend limit: held")
    ok("I0" in x.w.needs, "spend limit: delivered to the owner route")
    x.tick()
    ok(x.w.needs.count("I0") == 1, "spend limit: delivered once")
    ok(x.st("I1")["status"] == "running", "spend limit: holds nothing else")
    R.unhold(x.s, "I0", "go on", now=x.now)
    ok(x.st("I0")["status"] == "queued" and x.st("I0")["returned_at"], "his word lifts the hold, to the top")
    x.tick()
    ok(("I0", "offline") in x.w.needs, "his word restores the ledger needs")
    # unmeasured run charged at the reserve
    y = Rig(n=1, share=1.0)
    y.run_one("I0")
    st = y.st("I0")
    y.now += 400
    y.w.tok = 0
    y.w.up[st["run"]["unit"]] = False
    y.tick()
    ok(y.st("I0")["spent"] == y.r["run_reserve"], "unmeasured run costs the reserve")
    # day limit holds launches, keeps places
    z = Rig(n=1, share=1.0, day_spend_limit=500)
    z.tick()
    ok(z.st("I0")["status"] == "queued" and not z.w.launches, "day limit: no launch, item keeps its place")
    x.done(), y.done(), z.done()


def t_top_of_queue():
    x = Rig(n=4, share=1.0, max_workers=1)
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "stuck", "x", x.r, now=x.now)
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    ok(x.st("I0")["status"] == "running", "restart: back ahead of every fresh item")
    order = R.queue_order([dict(R.new_state("F", 1, ""), status="queued"),
                           dict(R.new_state("B", 9, ""), status="queued", returned_at=50),
                           dict(R.new_state("A", 9, ""), status="queued", returned_at=40)])
    ok([s["item"] for s in order] == ["A", "B", "F"], "queue: oldest return first, then fresh")
    x.done()


def t_share():
    x = Rig(n=4, share=0)
    x.tick()
    ok(x.s.items() == [], "share 0 enrols nothing")
    x.done()
    x = Rig(n=4, share=1.0)
    x.tick()
    ok(len(x.s.items()) == 4, "share 1 enrols the whole pool")
    x.done()
    x = Rig(n=4, share=0.5)
    x.tick()
    x.tick()
    ok(len(x.s.items()) == 2, "share 0.5 of 4 enrols 2, and stays there")
    ok(x.st("I0")["item"] == "I0", "the top of the pool order is chosen first")
    x.done()


def full_pass(x, i, verdict="PASS"):
    x.run_one(i)
    st = x.st(i)
    if not st["contract"]:
        R.contract(x.s, i, st["gen"], "proof", live="once: test")
    R.learn(x.s, i, st["gen"], "SENTINEL_OF_THE_ATTEMPTS")
    R.finish(x.s, i, st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st(i)
    ok(st["status"] == "checking", "finish reaches the checker")
    prompt = x.w.launches[-1][2]
    ok("SENTINEL_OF_THE_ATTEMPTS" not in prompt and "text of" in prompt, "the checker's brief holds no record of the attempts")
    R.verdict(x.s, i, st["check"]["nonce"], verdict, "ran it")
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    x.tick()


def t_done_path():
    x = Rig(n=1, share=1.0)
    x.close_fail = None
    x.w.close_fail = "git hiccup"
    full_pass(x, "I0")
    x.tick()
    ok(x.st("I0")["status"] == "done" and x.w.closes == [("I0", "sha1")], "PASS closes, a failed close retries")
    x.done()
    x = Rig(n=1, share=1.0)
    full_pass(x, "I0", "FAIL")
    st = x.st("I0")
    ok(st["failures"].get("blind_fail") == 1 and st["last_fail"]["detail"] == "ran it", "FAIL returns with its reasons")
    x.run_one("I0")
    ok("ran it" in x.w.launches[-1][2], "the reasons reach the next worker")
    x.done()
    x = Rig(n=1, share=1.0)
    x.w.live_broken = "unit down"
    full_pass(x, "I0")
    ok(x.st("I0")["failures"].get("live_broken") == 1, "a broken live line returns the item, it does not close")
    x.done()
    # an unpublished sha never reaches a checker
    x = Rig(n=1, share=1.0)
    x.w.is_pub = False
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    R.finish(x.s, "I0", st["gen"], "local", "e")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    ok(x.st("I0")["failures"].get("bad_candidate") == 1, "an unpublished sha is refused")
    x.done()
    # a hook change must carry a live line
    x = Rig(n=1, share=1.0)
    x.w.touched = [".claude/hooks/block_x.py"]
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    R.finish(x.s, "I0", st["gen"], "s", "e")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    ok("live line" in x.st("I0")["last_fail"]["detail"], "a hook change with no live line is refused")
    x.done()
    # an old nonce is refused
    x = Rig(n=1, share=1.0)
    expect_fence(lambda: R.verdict(x.s, "I0", "x", "PASS", "y"), "a verdict with no check is refused")
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    R.finish(x.s, "I0", st["gen"], "s", "e")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    if x.st("I0")["status"] != "checking":
        x.tick()
    ok(x.st("I0")["status"] == "checking", "old nonce: planted, a check is running")
    expect_fence(lambda: R.verdict(x.s, "I0", "not-" + x.st("I0")["check"]["nonce"], "PASS", "y"),
                 "a wrong nonce on a running check is refused")
    x.done()


def t_crash_recovery():
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    # the receipt landed, the status write did not
    x.s._write(x.s.receipt_path("I0", st["gen"]), json.dumps({"item": "I0", "gen": st["gen"], "sha": "s", "evidence": "e"}))
    x.tick()
    ok(x.st("I0")["status"] == "candidate", "crash: the receipt is recovered by the tick")
    x.done()


def t_crash_windows():
    # a receipt that lands while the tick is looking at a dead unit is adopted, not called lost
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    u = st["run"]["unit"]
    x.w.up[u] = False
    tokens = x.w.tokens

    def late(run):
        R.finish(x.s, "I0", st["gen"], "s", "e", now=x.now)
        x.w.tokens = tokens
        return tokens(run)
    x.w.tokens = late
    x.tick(400)
    ok(x.st("I0")["status"] in ("candidate", "checking"), "crash: a receipt landing as the unit dies is adopted")
    ok(x.st("I0")["returns"] == 0, "crash: it costs no return")
    x.done()
    # the checker's identity is on disk before the unit exists, and a live checker is never launched twice
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    R.finish(x.s, "I0", st["gen"], "s", "e", now=x.now)
    x.w.up[st["run"]["unit"]] = False
    launch, seen = x.w.launch, []

    def sees(*a, **k):
        seen.append(x.st("I0")["check"])      # what a crash at this instant would leave on disk
        return launch(*a, **k)
    x.w.launch = sees
    x.tick()
    if x.st("I0")["status"] != "checking":
        x.tick()
    x.w.launch = launch
    ok(seen and seen[0] and seen[0]["run"]["scope"].endswith(".scope") and seen[0]["run"]["out"],
       "the checker's whole identity is on disk before the unit exists")
    n = len(x.w.launches)
    x.tick()
    ok(len(x.w.launches) == n, "a live checker is never launched twice")
    x.done()
    # the day charge is keyed by run
    x = Rig(n=1)
    st = R.new_state("I0", 1, "")
    with x.s.lock():
        R.charge(x.s, st, 100, x.now, x.r, "u1")
        R.charge(x.s, st, 100, x.now, x.r, "u1")
    ok(R.spent_today(x.s, x.now) == 100, "a replayed charge counts once in the day")
    x.done()
    # a finished worker that will not die cannot park the candidate
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    R.finish(x.s, "I0", st["gen"], "s", "e", now=x.now)
    x.w.unkillable.add(st["run"]["unit"])
    x.tick()
    x.tick(x.r["stop_quarantine_s"] + 10)
    st = x.st("I0")
    ok(st["status"] == "checking" and st["quarantined"], "an unkillable finished worker is quarantined, the check goes on")
    x.w.unkillable.clear()
    x.w.up[st["quarantined"][0]["run"]["unit"]] = False
    x.tick()
    ok(x.st("I0")["quarantined"][0]["reaped"], "the quarantined run is reaped and charged when it dies")
    x.done()
    x = Rig(n=1)
    R.enrol_one(x.s, "PICKED", "test", x.now)
    R.enrol_one(x.s, "PICKED", "again", x.now)
    ok(x.st("PICKED")["status"] == "queued" and x.st("PICKED")["why"] == "test", "enrol by name is idempotent")
    x.done()
    # a worker that reported and then died unmeasured is a lost worker, not a failed launch
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.beat(x.s, "I0", st["gen"], now=x.now)
    x.w.tok = None
    x.w.up[st["run"]["unit"]] = False
    x.tick(30)
    ok(x.st("I0")["failures"].get("worker_lost") == 1 and x.st("I0")["returns"] == 1,
       "a worker that beat and died inside the grace is worker_lost")
    x.done()
    x = Rig(n=2, share=1.0, max_workers=0)
    x.tick()
    q = [s for s in x.s.states() if s["status"] == "queued"]
    ok(q, "exclusion: planted, an item waits in the queue")
    x.r["pool_ids_exclude"] = [q[0]["item"]]
    x.tick()
    ok(x.st(q[0]["item"])["status"] == "retired", "an item excluded in the rules leaves the queue")
    x.done()
    # started, it hit a gate its own text sets: exclusion must still take it out, and hand the ledger back
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "gate_not_met", "waits on others", x.r, now=x.now)
    x.w.up[st["run"]["unit"]] = False
    x.r["pool_ids_exclude"] = ["I0"]
    x.w.reclaim_fail = "rimflow refused"
    launched = len(x.w.launches)
    x.tick(600)
    x.tick(600)
    ok(len(x.w.launches) == launched, "an excluded item is not relaunched on its way out")
    ok(x.st("I0")["status"] == "queued" and x.w.items["I0"] == "doing", "a refused hand-back does not retire it")
    x.tick(600)
    ok(x.w.reclaim_fail is None and x.w.items["I0"] == "ready", "a refused hand-back comes round again: %s" % x.w.items["I0"])
    ok(x.st("I0")["status"] == "retired", "a started item excluded in the rules leaves the line")
    ok(x.w.items["I0"] == "ready", "and the ledger gets it back, not left doing with nobody on it")
    x.done()
    # reassigned on the way out: nothing of ours to hand back, and a hand-back would be refused for good
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "gate_not_met", "waits on others", x.r, now=x.now)
    x.w.up[st["run"]["unit"]] = False
    x.r["pool_ids_exclude"] = ["I0"]
    x.w.owners["I0"] = "FOUNDRY"
    x.w.reclaim_fail = "not yours"
    x.tick(600)
    x.tick(600)
    ok(x.w.reclaim_fail == "not yours", "a reassigned item is not reclaimed")
    ok(x.st("I0")["status"] == "retired", "and leaves the line")
    x.done()
    # a checker past its deadline cannot pass
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    R.finish(x.s, "I0", st["gen"], "s", "e", now=x.now)
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    if x.st("I0")["status"] != "checking":
        x.tick()
    chk = x.st("I0")["check"]
    x.w.unkillable.add(chk["run"]["unit"])
    x.tick(x.r["check_max_s"] + x.r["launch_grace_s"] + 5)
    try:
        R.verdict(x.s, "I0", chk["nonce"], "PASS", "late")
        ok(False, "an expired checker is fenced")
    except R.Fenced:
        ok(True, "an expired checker is fenced")
    x.done()
    # a dead session's own generation beats the clone's newer marker
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    t = tempfile.mkdtemp(prefix="rlh-")
    os.makedirs(os.path.join(t, ".git"))
    with open(os.path.join(t, ".git", "relentless.json"), "w") as f:
        json.dump({"item": "I0", "gen": st["gen"]}, f)
    os.environ["RELENTLESS_GEN"] = str(st["gen"] - 1)
    ok(R.hook_fence(t, x.s), "the session's generation, not the marker's, is fenced")
    del os.environ["RELENTLESS_GEN"]
    ok(R.hook_fence(t, x.s) is None, "the marker still answers without one")
    shutil.rmtree(t, ignore_errors=True)
    x.done()
    # rimflow's close refuses an alarm item without a live line: the candidate gate catches it first
    x = Rig(n=1, share=1.0)
    x.w.items["OPS_X"] = x.w.items["I0"]
    R.enrol_one(x.s, "OPS_X", "t", x.now - 100)
    x.run_one("OPS_X")
    st = x.st("OPS_X")
    R.contract(x.s, "OPS_X", st["gen"], "p")
    R.finish(x.s, "OPS_X", st["gen"], "s", "e", now=x.now)
    x.tick()
    ok(x.st("OPS_X")["failures"].get("bad_candidate") == 1, "an alarm item with no live line is a bad candidate")
    x.done()
    # overdue reads the beat
    st = dict(R.new_state("I0", 1, ""), started_at=0, last_beat=1000)
    rr = dict(RULES, run_max_s=10 ** 6)
    ok(R.overdue(st, 0, 1500, rr) is None and R.overdue(dict(st, last_beat=0), 0, 5000, rr),
       "overdue reads the fresh beat")


def t_third_review():
    # a crash after the ledger heard `start`, before the lease is on disk: ours, not a seat's take
    x = Rig(n=1, share=1.0)
    start = x.w.ledger_start

    def dies(item):
        start(item)
        x.w.ledger_start = start
        raise OSError("planted crash")
    x.w.ledger_start = dies
    try:
        x.tick()
    except OSError:
        pass
    ok(x.w.items["I0"] == "doing" and not x.st("I0")["ledger_started"], "crash window: planted after start")
    x.tick()
    ok(x.st("I0")["status"] == "running", "a crash after start leaves the item ours, and it is leased")
    # a quarantined run's cost counts against the item before it is reaped
    x = Rig(n=1, share=1.0)
    x.tick()
    with x.s.lock():
        st = x.s.load("I0")
        st["status"] = "queued"
        st["spent"] = RULES["item_spend_limit"] - RULES["run_reserve"]
        st["quarantined"].append({"run": {"unit": "gone"}, "clone": None, "reaped": False})
        x.s.save(st)
    R.spend_holds(x.s, x.w, RULES, x.now, [])
    ok(x.st("I0")["status"] == "held", "an unreaped quarantined run counts toward the item's spend limit")
    # a retiring item's run still holds its place
    x = Rig(n=2, share=1.0, max_workers=1)
    x.run_one("I0")
    x.w.items["I0"] = "dropped"
    x.w.alive_always = True
    stop = x.w.stop
    x.w.stop = lambda run, force: None         # the unit does not die yet
    x.tick()
    ok(x.st("I0")["status"] == "retiring", "retiring: planted")
    ok(x.st("I1")["status"] == "queued", "a retiring run holds its place: nothing launches beside it")
    x.w.stop = stop
    # a new check never reuses a path a quarantined checker may be in, and the reaper frees it
    d = tempfile.mkdtemp(prefix="rlck-")
    fx = R.Effects.__new__(R.Effects)
    fx.base = d
    a, b = (os.path.join(d, "clones", "check-X-c%d" % n) for n in (1, 2))
    os.makedirs(a), os.makedirs(b)
    st = {"item": "X", "check_count": 2, "quarantined": [{"clone": a, "reaped": False}]}
    ok(fx.check_path(st).endswith("check-X-c3"), "each check has its own path")
    ok(fx.old_checks(st) == [b], "a quarantined checker's clone is kept, the older clean one goes")
    st["quarantined"][0]["reaped"] = True
    ok(sorted(fx.old_checks(st)) == [a, b], "once reaped it may go")
    shutil.rmtree(d, ignore_errors=True)


def t_real_effects():
    """The fakes cannot see an import that fails: walk the real read paths once against this tree's ledger."""
    d = tempfile.mkdtemp(prefix="rlfx-")
    store = R.Store(d)
    fx = R.Effects(dict(RULES, pool_seats=["BENCH"], pool_needs=["offline"], pool_targets=["v1"],
                        pool_kinds_exclude=[], pool_ids_exclude=[]), store)
    order, w = fx.pool_order(fx.r)
    ok(isinstance(order, list) and len(w.items) > 100, "real: pool_order reads the real ledger")
    want = {i.id for i in w.items.values() if R.eligible(i, fx.r) and i.target in (None, "v1")}
    ok(want and set(order) == want, "real: the pool is every eligible item, the proposed backlog included")
    ok(fx.item_state("NO_SUCH_ITEM_X") is None, "real: item_state")
    ok(fx.paused() in (True, False, None) or isinstance(fx.paused(), str), "real: paused answers")
    ok(fx.mem_gb() > 0, "real: memory reading")
    shutil.rmtree(d, ignore_errors=True)


def t_launch_fail():
    x = Rig(n=1, share=1.0, launch_breaker=2, breaker_cool_s=500)
    x.w.lfail = "auth dead"
    x.tick()
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "queued" and st["total_failures"] == 0, "launch failure is not the item's fault")
    ok(R.load_breaker(x.s).get("until", 0) > x.now, "the breaker opens")
    x.w.lfail = None
    x.tick(10)
    ok(not x.w.launches, "breaker holds launches while cooling")
    x.tick(600)
    ok(x.w.launches, "breaker cools and launches resume")
    x.done()


def breaker_rig(world_cls=None, **rules):
    """One tick per try, the clock well past each cool. The real Effects where the path is the fault's: launch, told,
    conductor log, the alarm item (its rimflow call stubbed: no selftest writes the real ledger)."""
    d = tempfile.mkdtemp(prefix="rlbrk-")
    log, seen = os.path.join(d, "conductor.md"), []
    r = dict(RULES, **dict(dict(share=1.0, launch_breaker=2, breaker_cool_s=900, staffing=dict(STAFF, conductor_log=log)), **rules))
    x = Rig(n=1, share=1.0)
    x.r = r
    real = R.Effects(r, x.s)
    real.RL = types.SimpleNamespace(launch_argv=lambda role, unit, msg, out, err, claude: [
        "/bin/sh", "-c", "echo Failed to connect to bus: No medium found >&2; exit 1", "--", "--output-format"])
    real.rimflow = lambda *a, **k: (seen.append(a), types.SimpleNamespace(returncode=0, stdout="", stderr=""))[1]
    real.item_state = lambda item: None
    x.w.launch = real.launch
    x.w.told = real.told
    x.w.conductor_alarm = real.conductor_alarm
    x.w.staffing_alarm = real.staffing_alarm
    x.w.budget = lambda: 3
    return x, d, log, seen


def emergencies(seen):
    return sum(1 for a in seen if any("EMERGENCY" in str(v) for v in a))


def told_rows(d):
    p = os.path.join(d, "told.jsonl")
    return [json.loads(ln) for ln in open(p, encoding="utf-8")] if os.path.exists(p) else []


def t_breaker_di2():
    """DI2, the planted faults: a refusal never charges; a failing launcher opens, reopens, and is told as an emergency."""
    old = os.environ.get("RM_OPS_WATCH_DIR")
    x, d, log, seen = breaker_rig()
    os.environ["RM_OPS_WATCH_DIR"] = d
    live = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    ok(live["breaker_cool_max_s"] == 1800, "the shipped cap is 1800")
    x.r["breaker_cool_max_s"] = live["breaker_cool_max_s"]

    # the real launcher, failing the real way, on the live rules
    longest, opens = 0, []
    for i in range(14):
        x.tick(10)
        br = R.load_breaker(x.s)
        cool = br.get("until", 0) - x.now
        longest = max(longest, cool)
        if br.get("until", 0) > x.now and (not opens or opens[-1] < x.now - 300):
            opens.append(x.now)
        if br.get("until", 0) > x.now:
            x.now = br["until"]         # the cool passes; the next tick is the half-open try
    ok(len(opens) >= 2, "a failing launcher opens the breaker and reopens it, got %d" % len(opens))
    ok(0 < longest <= 1800, "no cool past the cap, longest %s" % longest)
    rows = told_rows(d)
    ok(len(rows) == 1, "one incident, one row, however often it reopens: %s" % len(rows))
    row = rows[0] if rows else {}
    ok(row.get("class") == "emergency" and row.get("reader") == "Operations" and row.get("told_at")
       and row.get("ack_due") and "recover_by" in row and row.get("cause", "").startswith("relentless.breaker:"),
       "the told row is OP3's: %s" % row)
    ok("No medium found" in row.get("why", ""), "the row names the cause")
    with open(log, encoding="utf-8") as f:
        said = f.read()
    ok(said.count("EMERGENCY") == 1 and "No medium found" in said, "one line in the Conductor's log")
    ok(emergencies(seen) == 1, "the alarm item hears it once: %s" % seen)
    x.done()

    # a road that fails is retried and the others are not repeated
    x, d, log, seen = breaker_rig()
    os.environ["RM_OPS_WATCH_DIR"] = os.path.join(d, "no", "such")
    for i in range(10):
        x.tick(10)
        x.now = max(x.now, R.load_breaker(x.s).get("until", 0))
    ok(emergencies(seen) == 1 and open(log, encoding="utf-8").read().count("EMERGENCY") == 1,
       "the roads that landed are not repeated while told retries")
    os.environ["RM_OPS_WATCH_DIR"] = d
    x.tick(10)
    ok(len(told_rows(d)) == 1, "told lands once it can")
    x.done()

    # one open, then a launch that works: still counted; a second open by the same cause is the emergency
    x, d, log, seen = breaker_rig()
    os.environ["RM_OPS_WATCH_DIR"] = d
    br = {}
    for why in ("rm-relentless-work-A_ONE-g3 died at once with no usage",
                "rm-relentless-work-B_TWO-g17 died at once with no usage"):
        x.now += 5000
        R.launch_failed(x.s, x.r, x.now, why)
        R.launch_failed(x.s, x.r, x.now, why)
        R.launch_ok(x.s)
    br = R.load_breaker(x.s)
    ok(not br.get("until") and not br.get("fails"), "launch_ok closes it")
    ok(len(br.get("opens", {})) == 1 and list(br["opens"].values())[0]["n"] == 2, "two runs, one cause: %s" % br)
    x.tick(10)
    ok(len(told_rows(d)) == 1, "a flap between two opens does not hide the same cause")
    x.done()

    # two causes, one open each: not an emergency. Two failures of one tick: one open
    x, d, log, seen = breaker_rig()
    os.environ["RM_OPS_WATCH_DIR"] = d
    for why in ("auth dead", "quota gone"):
        x.now += 5000
        for _ in range(3):
            R.launch_failed(x.s, x.r, x.now, why)
        R.launch_ok(x.s)
    x.tick(10)
    ok(not told_rows(d) and len(R.load_breaker(x.s)["opens"]) == 2, "two causes, once each, is no emergency")
    # past the window a cause is forgotten
    x.now += x.r["breaker_same_cause_window_s"] + 1
    x.w.launch = lambda *a: None
    x.tick(10)
    ok(not R.load_breaker(x.s).get("opens"), "the window ends a cause's count")
    x.done()

    # a cool written under the old cap is cut down on the next look
    x, d, log, seen = breaker_rig()
    x.r["breaker_cool_max_s"] = 1800
    x.s._write(x.s.p("breaker.json"), json.dumps({"fails": 9, "until": x.now + 14000, "why": "old"}))
    x.tick(10)
    ok(R.load_breaker(x.s)["until"] - x.now <= 1800, "an old long cool obeys the new cap")
    x.done()

    # the pool's real refusal, from scratch_clone itself; and memory after a clone
    x, d, log, seen = breaker_rig(launch_breaker=1)
    real = R.Effects(x.r, x.s)
    real.books = os.path.dirname(os.path.dirname(os.path.dirname(R.HERE)))
    x.w.prepare = real.prepare
    x.w.clone_path = lambda item, q=0: os.path.join(d, "clones", item)
    x.w.clone_present = lambda c: False
    pool = {"RM_POOL_MAX_CLONES": "0", "RM_POOL_ROOT": os.path.join(d, "clones"),
            "RM_POOL_STATE_GLOB": os.path.join(d, "none*")}
    env = {k: os.environ.get(k) for k in pool}
    os.environ.update(pool)
    try:
        acts = x.tick()
    finally:
        for k, v in env.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    ok(any(R.POOL_REFUSED in str(a.get("why")) for a in acts), "planted: the pool really refused: %s" % acts)
    ok(not R.load_breaker(x.s), "a real pool refusal does not charge the breaker")
    ok(not told_rows(d), "and tells nobody")
    x.done()
    x = Rig(n=1, share=1.0, launch_breaker=1)
    x.w.lfail = "memory 3.1 GB after the clone"
    x.tick()
    ok(not R.load_breaker(x.s), "memory after a clone does not charge the breaker")
    x.done()
    # a start the ledger refuses waits on its own and the belt does not stop
    x = foreign_rig(launch_breaker=1)
    calls = []
    x.w.ledger_start = lambda item: calls.append(item) or "refused by a gate"
    x.tick()
    n = len(calls)
    x.tick()
    ok(n and not R.load_breaker(x.s), "a refused start does not charge the breaker")
    ok(len(calls) == n, "and is paced by itself: %s" % calls)
    x.done()
    if old is None:
        os.environ.pop("RM_OPS_WATCH_DIR", None)
    else:
        os.environ["RM_OPS_WATCH_DIR"] = old


def t_retire():
    x = Rig(n=2, share=1.0, max_workers=1)
    x.run_one("I0")
    u = x.st("I0")["run"]["unit"]
    x.w.items["I0"] = "dropped"
    x.tick()
    if x.st("I0")["status"] != "retired":
        x.tick()
    ok(x.st("I0")["status"] == "retired" and x.st("I0")["run"]["charged"] and not x.w.up[u],
       "his drop fences, stops and charges the run, then retires")
    x.w.items["I1"] = "doing"
    x.done()
    x = Rig(n=2, share=1.0, max_workers=0)
    x.tick()
    x.w.items["I1"] = "doing"
    x.tick()
    ok(x.st("I1")["status"] == "retired", "a seat took it first: let go")
    x.done()


def _race(a):
    d, q = a
    s = R.Store(d)
    for _ in range(40):
        try:
            R.beat(s, "I0", 1)
        except R.Fenced:
            pass
    q.put(1)


def t_concurrency():
    d = tempfile.mkdtemp(prefix="rl-")
    s = R.Store(d)
    st = dict(R.new_state("I0", 1, ""), status="running", gen=1)
    s.save(st)
    m = multiprocessing.Manager()
    q = m.Queue()
    ps = [multiprocessing.Process(target=_race, args=((d, q),)) for _ in range(4)]
    [p.start() for p in ps]
    [p.join() for p in ps]
    ok(all(p.exitcode == 0 for p in ps) and s.load("I0")["gen"] == 1, "four beating processes do not tear the state")
    # two ticks: the second is refused by tick.lock
    import fcntl
    with open(s.p("tick.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        ok(R.tick(s, FakeWorld(0), dict(RULES), 1.0)[0]["do"] == "skip", "a second tick skips")
    # many items, one lease each
    x = Rig(n=6, share=1.0, max_workers=3)
    x.tick()
    x.tick()
    states = x.s.states()
    run = [s2 for s2 in states if s2["status"] == "running"]
    ok(len(run) == 3 and len({s2["clone"] for s2 in run}) == 3, "max_workers holds, one clone each")
    x.done()
    # memory under step_back_mem_gb (8) but over the launch floor: one worker only
    x = Rig(n=6, share=1.0, max_workers=3, step_back_mem_gb=8)
    x.w.mem = 7
    x.tick()
    x.tick()
    ok(len([s2 for s2 in x.s.states() if s2["status"] == "running"]) == 1, "available memory under 8 GB steps back to 1 worker")
    x.w.mem = 20
    x.tick()
    x.tick()
    ok(len([s2 for s2 in x.s.states() if s2["status"] == "running"]) == 3, "memory back over 8 GB: 3 workers again")
    ok(R.worker_cap(FakeWorld(0), dict(RULES, max_workers=3, step_back_mem_gb=8), 1) == 4, "a check keeps its place on top of the cap")
    x.done()
    shutil.rmtree(d, ignore_errors=True)


def t_live_line():
    ok(live_line.parse("hook=block_foo.py")["kind"] == "hook", "live: hook")
    ok(live_line.parse("once: repair")["kind"] == "once", "live: once")
    p = live_line.parse("unit=rm-foo.timer reading=/x max_age=6h")
    ok(p["max_age_s"] == 21600, "live: unit")
    for bad in ("", "once:", "unit=x", "hook=", "hook=a b", "unit=a reading=b max_age=6"):
        try:
            live_line.parse(bad)
            ok(False, "live: refuses %r" % bad)
        except ValueError:
            ok(True, "live: refuses %r" % bad)
    d = tempfile.mkdtemp(prefix="rl-")
    f = os.path.join(d, "r")
    open(f, "w").close()
    os.utime(f, (1000, 1000))

    def runner(a, **k):
        return types.SimpleNamespace(stdout="enabled" if a[2] == "is-enabled" else "active")
    line = "unit=rm-x.timer reading=%s max_age=1h" % f
    ok(live_line.check(line, now=2000, runner=runner) is None, "live: holds")
    ok("old" in live_line.check(line, now=9000, runner=runner), "live: stale reading")
    ok("predates" in live_line.check(line, now=2000, not_before=1500, runner=runner), "live: reading older than the commit")

    def down(a, **k):
        return types.SimpleNamespace(stdout="inactive")
    ok("is-enabled" in live_line.check(line, now=2000, runner=down), "live: unit down")
    ok(live_line.needs_line(["a/.claude/hooks/x.py", "src/y.py", "Utils/systemd/rm-a.timer"]) ==
       ["a/.claude/hooks/x.py", "Utils/systemd/rm-a.timer"], "live: which paths oblige a line")
    shutil.rmtree(d, ignore_errors=True)


def staffed(n=12, **cfg):
    return Rig(n=n, share=0.5, max_workers=10, staffing=dict(STAFF, **cfg))


def running(x):
    return sum(1 for st in x.s.states() if st["status"] in R.HOLDS_A_PLACE)


def reading(x):
    with open(x.s.p("staffing.json"), encoding="utf-8") as f:
        return json.load(f)


def verdicts(x, good, bad):
    for i in range(good + bad):
        x.s.attempt("I0", {"at": R.iso(x.now), "end": "done" if i < good else "blind_fail", "sha": "s%d.%d" % (x.now, i)})


def t_staffing_places():
    x = staffed()
    x.tick()
    ok(running(x) == 2, "launches are limited per tick")
    x.tick(), x.tick()
    r = reading(x)
    ok(running(x) == 3 and r["target"] == 3 and r["running"] == 3 and not r["under"] and r["ready"] > 0,
       "the filler fills the first stage, and no further")
    x.done()
    x = staffed()
    x.w.budget_v = None
    for _ in range(4):
        x.tick()
    r = reading(x)
    ok(running(x) == 3 and r["budget_measured"] is False, "budget unreadable: the lowest stage, and marked")
    x.done()
    x = staffed(stages=["budget"])
    x.w.budget_v = None
    for _ in range(4):
        x.tick()
    ok(running(x) == 1, "budget unreadable at a budget stage does not run away")
    x.done()
    x = staffed()
    x.w.budget_v = 2
    for _ in range(4):
        x.tick()
    ok(running(x) == 2, "a budget below the stage rules")
    x.done()
    x = staffed()
    x.w.helpers = 7
    for _ in range(4):
        x.tick()
    r = reading(x)
    ok(running(x) == 1 and r["head_helpers"] == 7 and not r["under"], "a head's own helpers count against the budget")
    x.done()
    x = staffed()
    x.w.budget_v = 0
    for _ in range(25):
        x.tick()
    r = reading(x)
    ok(running(x) == 0 and r["why"] == "budget 0" and not x.w.alarms, "budget 0: nothing runs, and no alarm")
    x.done()
    x = staffed()
    x.w.mem = 7.0
    for _ in range(4):
        x.tick()
    ok(running(x) == 1 and reading(x)["target"] == 1, "memory under 8 GB steps back to 1")
    x.done()
    x = staffed()
    x.r["share"] = 0
    for _ in range(4):
        x.tick()
    ok(running(x) == 0 and reading(x)["why"] == "share 0", "share 0 is still his off switch")
    x.done()
    x = staffed(n=2)
    for _ in range(5):
        x.tick()
    ok(running(x) == 2 and not reading(x)["under"] and reading(x)["ready"] == 0, "no ready work is not under-staffed")
    x.done()
    # the filler's need, not the share of the backlog: the old rule enrols nothing past ceil(.5 x 2 items)
    x = Rig(n=12, share=0.01, max_workers=10, staffing=dict(STAFF))
    for _ in range(4):
        x.tick()
    ok(running(x) == 3, "a free place enrols whatever the share says")
    x.done()


def t_staffing_backlog():
    x = staffed()
    for _ in range(3):
        x.tick()
    # three candidates waiting: over check_backlog_max 2, so no builder starts
    with x.s.lock():
        for st in x.s.states():
            if st["status"] == "running":
                x.w.up[st["run"]["unit"]] = False
                st["status"] = "candidate"
                st["candidate"] = {"sha": "s", "gen": st["gen"], "evidence": "e", "at": x.now - 300}
                st["run"] = None
                x.s.save(st)
    n = len(x.w.launches)
    r = R.staffing
    fx, acts = x.w, []
    R.lease(x.s, fx, dict(x.r, max_workers=10, staffing=dict(STAFF, stages=[9])), x.now, acts)
    ok(len(x.w.launches) == n and any(a.get("why") == "check_backlog" for a in acts), "no new builders past the check backlog")
    rec = r(x.s, fx, x.r, x.now + 60, [])
    ok(rec["checks"]["waiting"] == 3 and rec["checks"]["oldest_wait_s"] >= 300, "the reading shows the check queue")
    x.done()


def stage_rig(**cfg):
    x = staffed(**cfg)
    for _ in range(3):
        x.tick()
    return x


def hold(x, n=6):
    for _ in range(n):
        x.tick()
    return reading(x)


def t_staffing_rise():
    x = stage_rig()
    ok(hold(x)["rise_lacks"].endswith("verdicts") and reading(x)["stage"] == 3, "no verdicts, no rise")
    verdicts(x, 3, 0)
    r = hold(x, 2)
    ok(r["stage"] == 5, "a clean reading rises one stage (%s)" % r["rise_lacks"])
    hold(x, 2)
    ok(running(x) == 5, "the filler refills to the new stage")
    x.done()
    x = stage_rig()
    verdicts(x, 2, 2)
    r = hold(x, 7)
    ok(r["stage"] == 3 and "rejected" in r["rise_lacks"], "rejected work holds the stage")
    x.done()
    x = stage_rig()
    verdicts(x, 3, 0)
    x.w.mem = 7.0
    x.tick()
    x.w.mem = 30.0
    r = hold(x, 7)
    ok(r["stage"] == 3 and "verdicts" in r["rise_lacks"], "one memory dip restarts the window: old verdicts do not count")
    verdicts(x, 3, 0)
    r = hold(x, 2)
    ok(r["stage"] == 5, "and a clean window after it still rises (%s)" % r["rise_lacks"])
    x.done()
    x = stage_rig()
    verdicts(x, 3, 0)
    x.w.burn_v = None
    r = hold(x, 7)
    ok(r["stage"] == 3 and r["rise_lacks"] == "burn unmeasured", "an unmeasured burn holds the stage")
    x.done()
    x = stage_rig()
    verdicts(x, 3, 0)
    x.w.burn_v = 3.5
    r = hold(x, 7)
    ok(r["stage"] == 3 and "burn" in r["rise_lacks"], "burn over the stop line holds the stage")
    x.done()
    x = stage_rig()
    verdicts(x, 3, 0)
    x.w.oom = None
    r = hold(x, 7)
    ok(r["stage"] == 3 and "OOM" in r["rise_lacks"], "an unreadable OOM count holds the stage")
    x.done()
    x = stage_rig()
    verdicts(x, 3, 0)
    hold(x, 8)
    ok(reading(x)["stage"] == 5, "setup: at the second stage")
    x.w.oom = 1
    x.tick()
    ok(reading(x)["stage"] == 3, "an OOM kill steps one down")
    x.tick()
    ok(reading(x)["stage"] == 3, "and the same kill counts once")
    x.done()
    x = stage_rig()
    verdicts(x, 3, 0)
    x.w.budget_v = 7
    hold(x, 8)
    verdicts(x, 3, 0)
    hold(x, 8)
    ok(reading(x)["stage"] == "budget", "the last stage is the budget (%s)" % reading(x)["rise_lacks"])
    ok(running(x) == 7, "and the filler stands at it")
    x.done()


def foreign_rig(**cfg):
    x = staffed(n=1, stages=[3], **cfg)
    x.w.owners["I0"] = "FOUNDRY"
    return x


def t_foreign_take():
    x = foreign_rig()
    seen = []
    x.w.on_settle = lambda: seen.append((x.st("I0")["status"], list(x.w.takes)))
    x.tick()
    ok(seen == [("running", [])], "the guard's word is on the store before the wait, the ledger unmoved")
    ok(x.w.takes == ["I0"] and len(x.w.launches) == 1 and x.st("I0")["foreign"], "a clear item is taken and runs")
    ok(not x.st("I0").get("reserving"), "the reservation ends at launch")
    x.done()
    x = foreign_rig()

    def said():
        x.w.words = {"I0"}
    x.w.on_settle = said
    x.tick()
    ok(x.st("I0")["status"] == "retired" and not x.w.takes and not x.w.launches, "a claim that won the race keeps it")
    x.tick()
    ok(not x.w.launches, "and it is not taken later")
    x.done()
    x = foreign_rig()

    def blind():
        x.w.words = None
    x.w.on_settle = blind
    x.tick()
    ok(x.st("I0")["status"] == "queued" and not x.w.takes, "its tree gone unreadable mid-wait: not taken, waits")
    x.done()
    x = foreign_rig()
    x.w.take_fail = "refused"
    x.tick()
    ok(x.st("I0")["status"] == "queued" and not x.w.launches, "a refused hand-over launches nothing")
    x.done()
    x = foreign_rig()
    orig = x.w.ledger_start

    def refuse(item):
        return "no"
    x.w.ledger_start = refuse
    x.tick()
    ok(x.st("I0")["status"] == "queued" and not x.w.launches, "a refused start launches nothing")
    x.w.ledger_start = orig
    x.done()
    # a crash inside the reservation
    x = foreign_rig()
    x.w.pause = True
    x.tick()
    x.w.pause = False
    with x.s.lock():
        st = x.st("I0")
        st.update(status="running", reserving=x.now, run=None, foreign=True, started_at=x.now)
        x.s.save(st)
    acts = []
    R.step(x.s, x.w, x.r, "I0", x.now, acts)
    ok(x.st("I0")["status"] == "queued" and not x.st("I0").get("reserving"), "a crashed reservation returns to the line")
    x.done()
    # back in line after a failed launch, its seat reached it
    x = foreign_rig()
    x.w.lfail = "no unit"
    x.tick()
    ok(x.st("I0")["status"] == "queued" and x.st("I0")["ledger_started"], "setup: a launch failed")
    x.w.lfail = None
    x.w.words = {"I0"}
    x.r["breaker_cool_s"] = 0
    x.s._write(x.s.p("breaker.json"), "{}")
    x.tick()
    ok(x.st("I0")["status"] == "queued" and len(x.w.launches) == 0, "a word from its seat while queued holds the launch")
    x.done()


def t_foreign_tomb():
    x = foreign_rig()
    x.tick(1)
    full_pass(x, "I0")
    x.tick()
    st = x.st("I0")
    ok(x.w.closes == [("I0", "sha1")] and st["status"] == "closing" and st.get("tomb_since"),
       "closed on the ledger, the guard's word stays")
    x.tick()
    ok(len(x.w.closes) == 1 and x.st("I0")["status"] == "closing", "not closed twice, and held while its tree is stale")
    ok(running(x) == 0, "a tombstone holds no place")
    x.w.heard = True
    x.tick()
    ok(x.st("I0")["status"] == "done", "its tree has heard: done")
    x.done()
    x = foreign_rig(tomb_max_s=100)
    x.tick(1)
    full_pass(x, "I0")
    x.tick()
    x.tick(200)
    ok(x.st("I0")["status"] == "done", "a tree that never hears ends at tomb_max_s")
    x.done()


def t_foreign_eligible():
    r = dict(RULES, pool_seats=["BENCH", "FOUNDRY"], staffing=dict(STAFF))

    def it(id="X_FIX_Y", owner="FOUNDRY", state="proposed", kind="task", title="a title"):
        return types.SimpleNamespace(id=id, owner=owner, state=state, kind=kind, title=title, blocked=False,
                                     needs="offline", lease=None, target="v1")
    ok(R.eligible(it(), r), "a proposed FOUNDRY task is eligible")
    ok(not R.eligible(it(state="ready"), r), "ready is what its `next` offers: refused")
    ok(R.eligible(it(owner="BENCH", state="ready"), r), "BENCH's ready stays eligible")
    ok(not R.eligible(it(kind="art"), r) and not R.eligible(it(kind="design"), r), "excluded kinds")
    ok(not R.eligible(it("HOSE_X_FIX"), r) and not R.eligible(it("MY_ARENA_FIX"), r), "excluded prefix anywhere")
    ok(R.eligible(it("PARTY_ARTIST_FIX"), r), "a word inside a word is no match")
    ok(not R.eligible(it(title="needs the bridge up"), r), "excluded by title")
    ok(R.eligible(it("HOSE_X_FIX", owner="BENCH"), r), "the exclusions are FOUNDRY's alone")


def t_foreign_tree():
    d = tempfile.mkdtemp(prefix="rlt-")
    tree, books = os.path.join(d, "foundry"), os.path.join(d, "books")
    for t in (tree, books):
        os.makedirs(os.path.dirname(os.path.join(t, R.SHARD % "X")))
    cfg = dict(STAFF, foreign_tree=tree)
    store = R.Store(d)
    fx = R.Effects(dict(RULES, staffing=cfg), store)
    fx.books = books
    ok(fx.seat_words() is None, "no tree files: refuse every item of that seat")

    def write(root, seat, *events):
        with open(os.path.join(root, R.SHARD % seat), "a", encoding="utf-8") as f:
            for e in events:
                f.write(json.dumps(e) + "\n")
    old = {"seat": "FOUNDRY", "event": "claim", "id": "OLD"}
    write(tree, "FOUNDRY", old)
    write(tree, "OWNER", {"seat": "OWNER", "event": "note", "id": "HIS"})
    write(books, "FOUNDRY", old)
    write(tree, "FOUNDRY", {"seat": "FOUNDRY", "event": "claim", "id": "NEW"}, {"seat": "FOUNDRY", "event": "seat"})
    ok(fx.seat_words() == {"NEW", "HIS"}, "only what the books have not heard; an event with no id is no subject")
    with open(os.path.join(tree, R.SHARD % "FOUNDRY"), "a", encoding="utf-8") as f:
        f.write('{"torn\n')
    ok(fx.seat_words() is None, "a torn line: refuse")
    since = "2026-10-31T10:00:00Z"
    ok(not fx.seat_heard("NEW", since), "no BENCH shard there: not heard")
    write(tree, "BENCH", {"seat": "BENCH", "event": "close", "id": "NEW_OTHER", "ts": "2026-10-31T11:00:00Z"},
          {"seat": "BENCH", "event": "reassign", "id": "NEW", "to": "BENCH", "ts": "2026-10-31T11:00:00Z"},
          {"seat": "BENCH", "event": "close", "id": "NEW", "ts": "2026-10-30T11:00:00Z"})
    with open(os.path.join(tree, R.SHARD % "BENCH"), "a", encoding="utf-8") as f:
        f.write('{"event":"close","id":"NEW\n')
    ok(not fx.seat_heard("NEW", since), "another id, a hand-over, an older close, a torn line: not heard")
    write(tree, "BENCH", {"seat": "BENCH", "event": "close", "id": "NEW", "ts": "2026-10-31T11:00:00Z"})
    ok(fx.seat_heard("NEW", since) and not fx.seat_heard("OTHER", since), "the close in its tree is heard")
    shutil.rmtree(d, ignore_errors=True)


def t_staffing_alarm():
    x = staffed(alarm_after_min=10)
    x.w.mem = 5.0       # nothing launches, ready work waits
    for _ in range(4):
        x.tick()
    ok(not x.w.alarms and reading(x)["under"] and reading(x)["why"] == "memory", "under, named, not yet alarmed")
    for _ in range(4):
        x.tick()
    r = reading(x)
    ok(len(x.w.alarms) == 1 and r["alarmed"] and r["minutes_under"] >= 10, "the alarm goes after its minutes")
    for _ in range(6):
        x.tick()
    ok(len(x.w.alarms) == 1, "once per episode")
    x.w.mem = 30.0
    for _ in range(3):
        x.tick()
    ok(not reading(x)["under"] and not reading(x)["alarmed"], "a filled stage ends the episode")
    x.w.mem = 5.0
    for st in x.s.states():
        if st["status"] == "running":
            x.w.up[st["run"]["unit"]] = False
    for _ in range(12):
        x.tick()
    ok(len(x.w.alarms) == 2, "a new episode alarms again")
    x.done()
    x = staffed(alarm_after_min=2)
    x.w.pause = True
    for _ in range(5):
        x.tick()
    ok(not x.w.alarms and reading(x)["why"] == "paused", "paused is no alarm")
    x.done()
    x = staffed(alarm_after_min=2)
    x.w.mem, x.w.alarm_fail = 5.0, "ledger down"
    for _ in range(5):
        x.tick()
    ok(not reading(x)["alarmed"], "an alarm that did not land is not marked")
    x.w.alarm_fail = None
    x.tick()
    ok(len(x.w.alarms) == 1, "and goes on the next tick")
    x.done()

    class Boom(FakeWorld):
        def oom_kills(self):
            raise RuntimeError("planted")
    x = staffed()
    x.w.__class__ = Boom
    res = x.tick()
    ok(running(x) == 2, "a dead reading stops no worker")
    ok(any("staffing" in str(a.get("why")) for a in res["acts"]) if isinstance(res, dict) else True, "and says so")
    x.done()


def t_foreign_back_in_line():
    # handed over, then a crash before `start`: the books say BENCH, the reservation still applies
    x = foreign_rig()
    x.w.pause = True
    x.tick()
    x.w.pause = False
    x.w.owners["I0"] = "BENCH"
    with x.s.lock():
        st = x.st("I0")
        st["foreign"] = True
        x.s.save(st)
    seen = []
    x.w.on_settle = lambda: seen.append(x.st("I0")["status"])
    x.tick()
    ok(seen == ["running"] and not x.w.takes and len(x.w.launches) == 1, "a half-done take resumes through the wait")
    x.done()
    x = foreign_rig()
    x.w.lfail = "no unit"
    x.tick()
    x.w.lfail = None
    x.s._write(x.s.p("breaker.json"), "{}")
    seen = []
    x.w.on_settle = lambda: seen.append(x.st("I0")["status"])
    x.tick()
    ok(seen == ["running"] and len(x.w.launches) == 1, "a failed launch comes back through the reservation")
    x.done()
    # a take that fails once is no reason to lose the item for good
    x = foreign_rig()
    orig = x.w.ledger_take
    x.w.ledger_take = lambda item: "no"
    x.tick()
    ok(x.st("I0")["status"] == "queued", "one failed take stays in line")
    x.tick(), x.tick()
    ok(x.st("I0")["status"] == "retired", "three end it")
    x.done()
    x = foreign_rig()
    orig = x.w.ledger_take
    x.w.ledger_take = lambda item: "no"
    x.tick()
    x.w.ledger_take = orig
    x.tick()
    ok(len(x.w.launches) == 1, "and a recovered take runs")
    x.done()
    # after the hand-over the ledger says ours: backing out must not strand it
    x = foreign_rig()
    orig = x.w.ledger_start
    x.w.ledger_start = lambda item: "no"
    x.tick()
    x.w.ledger_start = orig
    ok(x.st("I0")["status"] == "queued", "a refused start after the hand-over stays in line")
    x.tick(x.r["breaker_cool_s"] + 1)
    ok(len(x.w.launches) == 1 and x.w.takes == ["I0"], "and runs once its wait is over, not taken twice")
    x.done()
    x = foreign_rig()
    x.w.lfail = "no unit"
    x.tick()
    x.w.lfail = None
    x.s._write(x.s.p("breaker.json"), "{}")
    x.w.words = None
    x.tick()
    ok(x.st("I0")["status"] == "queued" and not x.w.launches, "a blind tree after the hand-over waits, never retires")
    x.done()
    x = foreign_rig()
    x.w.lfail = "no unit"
    x.tick()
    x.w.lfail = None
    x.s._write(x.s.p("breaker.json"), "{}")
    x.w.words = {"I0"}
    x.tick()
    ok(x.st("I0")["status"] == "queued" and not x.w.launches, "a word after the hand-over waits in line, no launch")
    x.w.words = set()
    x.tick()
    ok(len(x.w.launches) == 1, "and goes once the word is published and read")
    x.done()
    # a hung rimflow in the take: the tick still flushes and reads
    x = foreign_rig()

    def hang(item):
        raise TimeoutError("planted")
    x.w.ledger_take = hang
    res = x.tick()
    ok(any("lease" in str(a.get("why")) for a in res) and x.st("I0")["status"] == "running", "a raising lease loses no tick")
    x.tick()
    ok(x.st("I0")["status"] != "running" or x.st("I0").get("reserving"), "and the reservation is taken back or redone")
    x.done()
    x = foreign_rig()
    x.w.pause = True
    x.tick()
    x.w.pause = False
    x.w.fits = False
    x.tick()
    ok(x.st("I0")["status"] == "retired" and not x.w.takes and not x.w.launches, "unfit at launch: given back")
    x.done()


def t_staffing_edges():
    # a budget or memory cut must not leave candidates waiting on each other
    x = staffed(n=2, check_backlog_max=9)
    x.tick(), x.tick()
    finish_all(x)
    x.w.budget_v = 0
    x.tick(), x.tick(), x.tick()
    ok(any(st["status"] == "checking" for st in x.s.states()), "budget 0: a candidate still reaches its check")
    x.done()
    # unmeasured is not free
    x = staffed(stages=[3, 5, "budget"])
    x.s._write(x.s.p("staffing_state.json"), json.dumps({"stage": 1, "stage_since": x.now, "full_s": 0, "mem_min": 30, "oom": 0}))
    x.w.helpers = None
    x.w.budget_v = 5
    hold(x, 3)
    r = reading(x)
    ok(running(x) == 3 and r["head_helpers"] is None and r["target"] == 3, "helpers unmeasured: the lowest stage, shown")
    x.w.helpers, x.w.budget_v = 0, None
    hold(x, 3)
    ok(reading(x)["target"] == 3, "budget unreadable at a numeric stage: the lowest stage")
    x.done()
    x = stage_rig()
    verdicts(x, 3, 0)
    x.w.budget_v = None
    r = hold(x, 7)
    ok(r["rise_lacks"] == "budget unreadable" and r["stage"] == 3, "no rise on an unreadable budget")
    x.done()
    # the clone took the memory
    x = staffed()

    def eat(st):
        x.w.mem = 5.0
    x.w.prepare = eat
    x.tick()
    ok(not x.w.launches and all(st["status"] != "running" for st in x.s.states()), "memory gone in the clone: no launch")
    x.done()
    # every place a check that cannot start
    x = staffed(n=3, check_backlog_max=9)
    x.tick(), x.tick()
    finish_all(x)
    x.r["day_spend_limit"] = 0
    x.tick()
    r = reading(x)
    ok(r["under"] and r["live"] == 0 and r["why"] == "day_spend_limit", "places full of waiting checks read as under")
    x.done()
    x = staffed(n=3, check_backlog_max=9)
    x.tick(), x.tick()
    st = [s for s in x.s.states() if s["status"] == "running"][0]
    R.contract(x.s, st["item"], st["gen"], "proof", live="once: test")
    R.finish(x.s, st["item"], st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.r["day_spend_limit"] = 0
    x.tick()
    r = reading(x)
    ok(r["under"] and r["live"] >= 1 and r["why"] == "day_spend_limit", "one running, a check stuck: still under")
    x.done()
    # at most launch_per_tick clones a tick, builders and checkers together
    x = staffed(n=4, check_backlog_max=9, stages=[4])
    for _ in range(3):
        x.tick()
    finish_all(x)
    before = len(x.w.launches)
    x.tick()
    x.tick()
    ok(len(x.w.launches) - before <= 4, "clones per tick are shared")
    x.done()
    # a clone that leaves too little memory steps aside for the next candidate
    x = staffed(n=2, check_backlog_max=9, launch_per_tick=1)
    x.tick(), x.tick()
    finish_all(x)
    x.w.mem_after = 2.0
    x.tick()
    x.w.mem_after = None
    a = [s for s in x.s.states() if s.get("clone_again_at")]
    ok(len(a) == 1, "the clone that ran short steps aside")
    x.tick()
    ok(sum(1 for s in x.s.states() if s["status"] == "checking") == 1 and x.st(a[0]["item"])["status"] == "candidate",
       "and the other check goes first")
    x.done()
    # the other seat's tree unreadable
    x = staffed(n=0)
    x.w.words = None
    x.tick()
    r = reading(x)
    ok(r["under"] and not r["foreign_tree_read"] and "unreadable" in r["why"], "a blind pool is not an empty one")
    x.done()
    # a stopped timer is not under-staffed minutes, nor is a pause
    x = staffed(alarm_after_min=30)
    x.w.mem = 5.0
    x.tick()
    x.tick(86400)
    ok(not x.w.alarms and reading(x)["minutes_under"] <= 12, "a day with no ticks counts one gap")
    x.done()
    x = staffed(alarm_after_min=4)
    x.w.pause = True
    for _ in range(6):
        x.tick()
    x.w.pause = False
    x.w.mem = 5.0
    x.tick()
    ok(not x.w.alarms and reading(x)["minutes_under"] <= 2, "paused minutes do not count")
    x.done()
    # credit only for gaps full at both ends
    x = staffed(hold_s=99999)
    x.tick(), x.tick()
    before = R.stage_load(x.s).get("full_s", 0)
    x.tick()
    a = R.stage_load(x.s)
    ok(before == 0 and a["full_s"] == 120, "the gap before a stage fills earns nothing, the next one does")
    x.done()
    # evidence
    x = staffed(n=2)
    x.tick()
    d = os.path.join(x.s.item_dir("I0"), "attempts.jsonl")
    x.s.attempt("I0", {"at": R.iso(x.now), "end": "blind_fail"})
    with open(d, "a", encoding="utf-8") as f:
        f.write('{"torn\n')
    ok(any(a.get("end") == "blind_fail" for a in x.s.attempts("I0")), "a torn tail keeps the record before it")
    x.done()
    x = stage_rig()
    x.tick()
    for _ in range(2):
        x.s.attempt("I0", {"at": R.iso(x.now), "end": "done", "sha": "same"})
    x.s.attempt("I0", {"at": R.iso(x.now), "end": "blind_fail"})
    s = dict(R.stage_load(x.s), stage_since=x.now - 3600, full_s=999999, mem_min=30)
    ok(R.clean_window(x.s, s, x.w, x.r, x.now) == "2 of 3 verdicts", "one pass written twice counts once")
    x.done()
    x = stage_rig()
    verdicts(x, 3, 0)
    x.w.oom = None
    hold(x, 7)
    x.w.oom = 10
    r = hold(x, 1)
    ok(r["stage"] == 3 and R.stage_load(x.s)["full_s"] == 0, "a count back from unreadable restarts the window")
    x.done()
    # the off switch
    x = staffed()
    x.w.pause = True
    x.tick()
    x.w.pause = False
    x.r["share"] = 0
    x.tick()
    ok(not x.w.launches and reading(x)["why"] == "share 0", "share 0 launches nothing, queued work included")
    x.done()
    x = staffed(alarm_after_min=2)
    x.w.mem, x.w.alarm_fail = 5.0, "nowhere"
    hold(x, 3)
    ok(reading(x)["alarm_fail"] == "nowhere", "a dead alarm route is in the reading")
    x.done()


def finish_all(x):
    """Every running builder finishes with a receipt and exits."""
    for st in x.s.states():
        if st["status"] == "running":
            R.contract(x.s, st["item"], st["gen"], "proof", live="once: test")
            R.finish(x.s, st["item"], st["gen"], "sha1", "evidence")
            x.w.up[st["run"]["unit"]] = False


def t_alarm_routes():
    d = tempfile.mkdtemp(prefix="rla-")
    fx = R.Effects(dict(RULES, staffing=dict(STAFF)), R.Store(d))
    calls = []

    def rimflow(*a, timeout=60, seat=None):
        calls.append((a[0], seat))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")
    fx.rimflow = rimflow
    for state, want in ((None, ("file", None)), ("doing", ("note", None)), ("done", ("live", "RUNNER"))):
        calls.clear()
        fx.item_state = lambda i, s=state: None if s is None else {"state": s}
        ok(fx.staffing_alarm("A", "t") is None and calls == [want], "alarm on %s goes by %s" % (state, want[0]))
    fx.item_state = lambda i: {"state": "dropped"}
    calls.clear()
    ok(fx.staffing_alarm("A", "t") and not calls, "a dropped alarm item says it cannot land")
    shutil.rmtree(d, ignore_errors=True)


def parked(x, item, status, clone=None, **kw):
    """A store record for an item the pool holds a clone for, with nothing running."""
    st = R.new_state(item, x.now, "planted")
    st.update(status=status, clone=clone, ledger_started=True, **kw)
    if status == "held":
        st["hold"] = {"at": x.now, "delivered": True, "kind": "owner_call", "why": "planted"}
    x.s.save(st)
    x.w.items[item] = "doing"


def jammed(n=3):
    """The jam of 2026-11-01: `n` checks waiting, every one of ten clones held, no run live."""
    x = staffed(n=n, check_backlog_max=9, stages=[n])
    x.w.pool = {}
    x.tick(), x.tick()
    finish_all(x)
    x.w.pool = {x.w.clone_path(st["item"], 0): {} for st in x.s.states()}
    return x


def t_pool_jam():
    x = jammed()
    for i, status in enumerate(["retired", "retired", "held", "held", "held", "held", "held"]):
        c = "/c/P%d" % i
        parked(x, "P%d" % i, status, c)
        x.w.pool[c] = {}
    ok(len(x.w.pool) == 10, "planted: ten clones")
    x.tick()
    r = reading(x)
    ok("/c/P0" not in x.w.pool and "/c/P1" not in x.w.pool, "a retired item's clone is released on the next tick")
    ok(not R.load_breaker(x.s), "a full pool charges the breaker nothing")
    ok(r["checks"]["running"] >= 1, "the planted jam clears: a check really starts")
    ok(r["running"] == r["live"] and r["places"] == 3, "running means live, places what is held")
    x.done()

    # every clone live: nothing may be released, the check waits, and the cause reaches the Conductor
    x = jammed()
    x.w.pool = {"/c/L%d" % i: {"busy": True} for i in range(10)}
    x.tick()
    r = reading(x)
    ok(len(x.w.pool) == 10, "a live clone is never released")
    ok(not R.load_breaker(x.s), "a pool hold is a wait, not a launch failure")
    ok(r["under"] and str(r["why"]).startswith("pool full: 10 clones") and "L3" in r["why"],
       "the reading names the pool and who holds it, got %s" % r["why"])
    ok(r["running"] == 0 and r["places"] == 3, "three waiting checks: 0 running, 3 places")
    ok(not x.w.jams, "not alarmed on the first tick")
    x.w.jam_fail = "disk gone"
    x.tick(300)
    ok(reading(x)["alarm_fail"] == "disk gone", "an alarm that did not land says so")
    x.w.jam_fail = None
    x.tick(120)
    x.tick(120)
    ok(len(x.w.jams) == 1 and "pool full" in x.w.jams[0] and "L3" in x.w.jams[0],
       "within minutes, one line, the real cause: %s" % (x.w.jams,))
    ok(not x.w.alarms, "and the half-hour staffing alarm has not had to speak")
    for c in x.w.pool.values():
        c["busy"] = False
    del x.w.pool["/c/L0"]
    del x.w.pool["/c/L1"]
    x.tick()
    ok(reading(x)["checks"]["running"] >= 1, "room again: a check starts")
    ok("jam_said" not in R.stage_load(x.s), "the jam ended, the next one alarms again")
    x.done()

    # a refusal that gets past make_room (a seat's clone, a race) is a wait too, for checks and for builders
    x = jammed()
    x.w.pool = {}
    x.w.refuse = True
    x.tick()
    ok(not R.load_breaker(x.s), "a check's POOL REFUSED does not charge the breaker")
    x.done()
    x = Rig(n=1, share=1.0, launch_breaker=1)
    x.w.refuse = True
    x.tick()
    ok(not R.load_breaker(x.s) and x.st("I0")["status"] == "queued" and x.st("I0")["total_failures"] == 0,
       "a builder's POOL REFUSED does not charge the breaker or the item")
    x.done()

    # the place kept for checks
    x = staffed(n=3)
    x.w.pool = {"/c/L%d" % i: {"busy": True} for i in range(9)}
    x.tick()
    ok(not x.w.launches and str(reading(x)["why"]).startswith("pool full") and "kept for checks" in reading(x)["why"],
       "a builder may not take the last clone")
    del x.w.pool["/c/L0"]
    x.tick()
    ok(x.w.launches, "one below it, a builder starts")
    x.done()

    # the order and the limits of an eviction
    x = staffed(n=1)
    x.w.pool = {"/c/L%d" % i: {"busy": True} for i in range(7)}
    for i, (status, wip) in enumerate((("held", {"kept": True}), ("held", {"real": ["a.cs"]}), ("queued", {}))):
        parked(x, "H%d" % i, status, "/c/H%d" % i)
        x.w.pool["/c/H%d" % i] = wip
    ok(R.make_room(x.s, x.w, x.r, x.now, []) is None and sorted(c for c in x.w.pool if "H" in c) == ["/c/H0", "/c/H1"],
       "nothing at risk goes first")
    x.w.pool_max = 9
    ok(R.make_room(x.s, x.w, x.r, x.now, []) is None and "/c/H1" not in x.w.pool and x.st("H1").get("bundle") == "/bundle//c/H1",
       "WIP goes with a bundle the next clone restores")
    ok(R.make_room(x.s, x.w, dict(x.r, pool_check_reserve=1), x.now, [], reserve=1) is not None, "the reserve holds at a real cap")
    x.w.pool = {}
    x.w.pool_max = 1
    ok(R.make_room(x.s, x.w, x.r, x.now, [], reserve=1) is None, "a pool of one still takes a builder")
    x.w.pool = {"/c/H0": {"kept": True}, "/c/L0": {"busy": True}}
    x.w.pool_max = 2
    ok("H0 (commits)" in str(R.make_room(x.s, x.w, x.r, x.now, [])) and "/c/H0" in x.w.pool, "commits stay, and the hold says so")
    parked(x, "D0", "retired", "/c/D0")
    x.w.pool["/c/D0"] = {"kept": True}
    x.tick()
    ok("/c/D0" not in x.w.pool, "a dead item's commits are bundled and released")
    x.done()

    # a check that ended leaves its clone; one running keeps it
    x = staffed(n=1)
    parked(x, "C0", "queued", None, check={"clone": "/c/check-C0-c1", "run": {"charged": 5}}, not_before=x.now + 10**6)
    parked(x, "C1", "checking", None, check={"clone": "/c/check-C1-c1", "run": {"charged": None}, "at": x.now, "nonce": "n", "unit": "u"})
    x.w.up["u"] = True
    x.w.pool = {"/c/check-C0-c1": {}, "/c/check-C1-c1": {}}
    R.reclaim_dead(x.s, x.w, x.r, x.now, [])
    ok(list(x.w.pool) == ["/c/check-C1-c1"], "a dead check clone goes, a running one stays")
    x.done()

    # builders at budget 0: the checks still need clones, and a blocked one still alarms
    x = jammed()
    x.w.pool = {"/c/L%d" % i: {"busy": True} for i in range(10)}
    x.w.budget_v = 0
    x.tick()
    x.tick(400)
    x.tick(120)
    ok(len(x.w.jams) == 1, "a pool jam alarms at budget 0: %s" % (x.w.jams,))
    x.done()

    x = staffed(n=3)
    x.s._write(x.s.p("breaker.json"), json.dumps({"fails": 4, "why": "auth dead", "until": x.now + 10**5}))
    x.tick()
    ok("auth dead" in reading(x)["why"], "an open breaker's reading carries its cause")
    x.done()


def t_unpublished_enrol_waits():
    """Filed and enrolled, not published yet: the books read None. Five items ended this way, 2026-11-01."""
    d = tempfile.mkdtemp(prefix="rlunpub-")
    store, w = R.Store(d), FakeWorld(0)
    os.makedirs(store.dir, exist_ok=True)
    R.enrol_one(store, "EARLY_ITEM", "picked", 1000)
    acts = []
    R.retire(store, w, store.states(), 1000, acts, dict(RULES))
    R.retire(store, w, store.states(), 1100, acts, dict(RULES))
    ok(store.load("EARLY_ITEM")["status"] == "queued", "an unpublished item stays in line")
    ok([a["do"] for a in acts] == ["awaiting_ledger"], "and says so once: %s" % acts)
    ok(not R.in_line(store.load("EARLY_ITEM")), "and holds no place in the enrolment count")
    w.items["EARLY_ITEM"] = "proposed"
    R.retire(store, w, store.states(), 1150, acts, dict(RULES))
    ok(R.in_line(store.load("EARLY_ITEM")), "published, it counts again")
    w.items["EARLY_ITEM"] = "dropped"
    R.retire(store, w, store.states(), 1200, acts, dict(RULES))
    ok(store.load("EARLY_ITEM")["status"] == "retiring", "the published drop still ends it")
    st = store.load("EARLY_ITEM")
    st["status"] = "retired"
    store.save(st)
    gen = st["gen"]
    ok(R.enrol_one(store, "EARLY_ITEM", "again", 1300)["status"] == "retired", "enrol does not bring it back")
    for bad, why in (("EARLY_ITEM", " "), ("NEVER_ENROLLED", "w")):
        try:
            R.reenrol(store, bad, why, 1300)
            ok(False, "reenrol must refuse %s" % bad)
        except ValueError:
            ok(True, "reenrol refuses %r" % bad)
    st = store.load("EARLY_ITEM")
    st["check_count"] = 3
    store.save(st)
    st = R.reenrol(store, "EARLY_ITEM", "wrongly retired", 1300)
    ok(st["status"] == "queued" and st["gen"] == gen + 1, "the named verb does, with a new gen")
    ok(st["check_count"] == 3, "and a new checker cannot land on an old one's path")
    ok(any(j.get("do") == "reenrol" and j.get("why") == "wrongly retired" for j in map(json.loads, open(store.p("journal.jsonl"), encoding="utf-8"))), "and journals why")
    try:
        R.reenrol(store, "EARLY_ITEM", "twice", 1400)
        ok(False, "reenrol of a queued item must refuse")
    except ValueError:
        ok(True, "only a retired item")


def t_books_frozen():
    """Books that cannot move are an engine that cannot deploy, and nothing else in the readings shows it."""
    d = tempfile.mkdtemp(prefix="rlbooks-")
    store = R.Store(d)
    os.makedirs(store.dir, exist_ok=True)
    fx = R.Effects(dict(RULES), store)
    def git(c, *a):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True,
                              capture_output=True, text=True).stdout
    def put(c, rel, text):
        os.makedirs(os.path.dirname(os.path.join(c, rel)) or c, exist_ok=True)
        with open(os.path.join(c, rel), "w", encoding="utf-8") as f:
            f.write(text)
    L, I = "infrastructure/state/ledger/events/B.jsonl", "infrastructure/state/items/A.md"
    o, up, b = os.path.join(d, "o.git"), os.path.join(d, "up"), fx.books
    git(d, "init", "-q", "--bare", "-b", "main", o)
    git(d, "clone", "-q", o, up)
    git(up, "checkout", "-q", "-b", "main")
    put(up, L, "one\n")
    put(up, I, "item\n")
    put(up, "code.py", "v1\n")
    git(up, "add", ".")
    git(up, "commit", "-qm", "base")
    git(up, "push", "-q", "origin", "main")
    git(d, "clone", "-q", o, b)
    # the jam of the books: a ledger commit that landed, a rimflow move, upstream on the same item
    put(b, L, "one\ntwo\n")
    git(b, "commit", "-qam", "ledger")
    put(up, L, "one\ntwo\nthree\n")
    put(up, I, "item changed\n")
    put(up, "code.py", "v2\n")
    git(up, "commit", "-qam", "up")
    git(up, "push", "-q", "origin", "main")
    os.remove(os.path.join(b, I))
    put(b, "infrastructure/state/items/closed/A.md", "item\n")
    why = fx.sync()
    ok(why is None, "the frozen books level: %s" % why)
    with open(os.path.join(b, "code.py"), encoding="utf-8") as f:
        ok(f.read() == "v2\n", "and the push deploys")
    ok(git(b, "rev-parse", "HEAD") == git(up, "rev-parse", "HEAD"), "level with origin")
    ok(glob.glob(store.p("books_dirt", "*", "infrastructure/state/items/closed/A.md")), "the dirt is kept aside")
    # what is not landed stops it, and says what
    put(b, L, "one\ntwo\nthree\nunlanded\n")
    put(up, L, "one\ntwo\nthree\nfour\n")
    put(up, "code.py", "v3\n")
    git(up, "commit", "-qam", "up2")
    git(up, "push", "-q", "origin", "main")
    why = fx.sync()
    ok(why and "not landed" in why, "unlanded ledger is never levelled away: %s" % why)
    with open(os.path.join(b, L), encoding="utf-8") as f:
        ok("unlanded" in f.read(), "and is still there")
    put(b, L, "one\ntwo\nthree\n")
    put(b, "code.py", "hand edit\n")
    ok("outside the ledger" in str(fx.sync()), "a hand edit stops it")
    put(b, "code.py", git(b, "show", "HEAD:code.py"))
    put(b, L, "staged event\n")
    git(b, "add", L)
    ok("staged" in str(fx.sync()), "a staged change stops it")
    git(b, "reset", "-q")
    put(b, L, git(b, "show", "HEAD:" + L))
    # an ignored file origin newly tracks: status cannot see it, and a merge or reset --keep would overwrite it
    git(b, "fetch", "-q", "origin")
    git(b, "reset", "-q", "--hard", "origin/main")
    put(b, ".git/info/exclude", "ignored.cfg\n")
    put(b, "ignored.cfg", "local secret\n")
    put(up, "ignored.cfg", "upstream\n")
    git(up, "add", "-f", "ignored.cfg")
    git(up, "commit", "-qm", "track it")
    git(up, "push", "-q", "origin", "main")
    why = fx.sync()
    ok(why and "ignored file ignored.cfg" in why, "an ignored file origin now tracks stops the books: %s" % why)
    with open(os.path.join(b, "ignored.cfg"), encoding="utf-8") as f:
        ok(f.read() == "local secret\n", "and it keeps its bytes")
    put(b, "ignored.cfg", "upstream\n")
    ok(fx.sync() is None, "the same bytes level")
    # a folder where origin wants a file, and a file where origin wants a folder: both lose ignored bytes
    git(b, "fetch", "-q", "origin")
    git(b, "reset", "-q", "--hard", "origin/main")
    put(b, ".git/info/exclude", "cache/\nnote\n")
    os.makedirs(os.path.join(b, "cache"))
    put(b, "cache/local.db", "local\n")
    put(b, "note", "local\n")
    put(up, "cache", "upstream\n")
    git(up, "add", "-f", "cache")
    git(up, "commit", "-qm", "a file over the folder")
    git(up, "push", "-q", "origin", "main")
    why = fx.sync()
    ok(why and "ignored files under cache" in why, "an ignored folder stops the books: %s" % why)
    shutil.rmtree(os.path.join(b, "cache"))
    ok(fx.sync() is None, "gone, the books level")
    os.makedirs(os.path.join(up, "note"))
    put(up, "note/config.json", "upstream\n")
    git(up, "add", "-f", "note/config.json")
    git(up, "commit", "-qm", "a folder over the file")
    git(up, "push", "-q", "origin", "main")
    why = fx.sync()
    ok(why and "ignored file note stands" in why, "an ignored file in the way stops the books: %s" % why)
    os.remove(os.path.join(b, "note"))
    ok(fx.sync() is None, "gone, the books level again")
    # the same collision by a rename: git calls that R, and a filter on A alone never sees it
    git(b, "fetch", "-q", "origin")
    git(b, "reset", "-q", "--hard", "origin/main")
    put(b, ".git/info/exclude", "ignored.cfg\nmoved.cfg\n")
    put(b, "moved.cfg", "local secret\n")
    git(up, "fetch", "-q", "origin")
    git(up, "reset", "-q", "--hard", "origin/main")
    git(up, "mv", "code.py", "moved.cfg")
    git(up, "commit", "-qm", "rename onto it")
    git(up, "push", "-q", "origin", "main")
    why = fx.sync()
    ok(why and "ignored file moved.cfg" in why, "a rename onto an ignored file stops the books: %s" % why)
    put(b, "moved.cfg", git(up, "show", "HEAD:moved.cfg"))
    ok(fx.sync() is None, "the same bytes level, after a rename too")
    # a fetch that fails leaves origin/main old, and every check above would pass against it without a word
    url = git(b, "remote", "get-url", "origin").strip()
    git(b, "remote", "set-url", "origin", os.path.join(d, "gone.git"))
    why = fx.sync()
    ok(why and "cannot fetch" in why, "a failed fetch is said: %s" % why)
    git(b, "remote", "set-url", "origin", url)
    ok(fx.sync() is None, "and clears when it fetches")
    class W:
        said = []
        def conductor_alarm(self, t):
            self.said = self.said + [t]
    w, acts = W(), []
    R.books_alarm(store, w, "behind", 1000, acts, RULES)
    R.books_alarm(store, w, "behind", 1100, acts, RULES)
    ok(not w.said, "the books alarm waits out a push in flight")
    for t in (1400, 1600):
        R.books_alarm(store, w, "behind", t, acts, RULES)
    ok(len(w.said) == 1 and "not deploying" in w.said[0], "then says it once")
    R.books_alarm(store, w, None, 1800, acts, RULES)
    ok(not os.path.exists(store.p("books_stale.json")), "and clears")
    with open(store.p("books_stale.json"), "w", encoding="utf-8") as f:
        f.write("{")
    R.books_alarm(store, w, "behind", 2000, acts, RULES)
    ok(json.load(open(store.p("books_stale.json"), encoding="utf-8"))["since"] == 2000, "a torn file is a new count, not a dead tick")
    shutil.rmtree(d, ignore_errors=True)


def t_pool_real_git():
    """Effects' bundle and restore against real git: what is unpushed survives the clone's removal."""
    d = tempfile.mkdtemp(prefix="rlpool-")
    store = R.Store(d)
    fx = R.Effects(dict(RULES), store)
    def git(c, *a):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True, capture_output=True)
    o = os.path.join(d, "o.git")
    os.makedirs(os.path.join(d, "clones"))
    git(d, "init", "-q", "--bare", o)
    c = os.path.join(d, "clones", "I0")
    git(d, "clone", "-q", o, c)
    os.makedirs(os.path.join(c, "conversations"))
    def put(rel, text, base=None):
        with open(os.path.join(base or c, rel), "w", encoding="utf-8") as f:
            f.write(text)
    put("a.txt", "one\n")
    git(c, "add", "a.txt")
    git(c, "commit", "-qm", "a")
    git(c, "push", "-q", "origin", "HEAD")
    x = R.new_state("I0", 0, "t")
    x["clone"] = c
    store.save(x)
    ok(fx.remove_clone({"clone": c, "item": "I0"}) is None and not fx.clone_present(c), "a clean clone needs no bundle")
    git(d, "clone", "-q", o, c)
    os.makedirs(os.path.join(c, "conversations"))
    put("a.txt", "two\n")
    put("new one.txt", "wip\n")
    put("conversations/n.md", "noise\n")
    w = fx.clone_wip(c)
    ok(sorted(w["real"]) == ["a.txt", "new one.txt"] and not w["kept"], "noise is not WIP: %s" % (w,))
    b = fx.remove_clone({"clone": c, "item": "I0"})
    ok(b and not fx.clone_present(c) and b.startswith(store.p("items", "I0")), "bundled, then gone: %s %s" % (b, fx.clone_present(c)))
    git(d, "clone", "-q", o, c)
    ok(fx.restore_bundle("I0", b, c) == [], "the bundle applies")
    with open(os.path.join(c, "a.txt"), encoding="utf-8") as f:
        ok(f.read() == "two\n", "the changed file came back")
    ok(os.path.exists(os.path.join(c, "new one.txt")), "the new file came back")
    ok(not os.path.exists(os.path.join(c, "conversations/n.md")), "the noise stayed in the bundle")
    git(c, "checkout", "-q", "--", "a.txt")
    os.remove(os.path.join(c, "new one.txt"))
    put("b.txt", "committed\n")
    git(c, "add", "b.txt")
    git(c, "commit", "-qm", "b")
    ok(fx.clone_wip(c)["kept"], "an unpushed commit is kept")
    b = fx.remove_clone({"clone": c, "item": "I0"})
    ok(os.path.exists(os.path.join(b or "", "commits.bundle")), "a dead clone's commits are in the bundle")
    git(d, "clone", "-q", o, c)
    git(c, "commit", "-qm", "detached", "--allow-empty")
    git(c, "checkout", "-q", "--detach")
    os.remove(os.path.join(c, ".git", "HEAD"))
    ok(fx.clone_wip(c)["kept"], "a clone git cannot read is kept")
    ok(fx.remove_clone({"clone": c, "item": "I0"}) is None and os.path.isdir(c), "and a bundle that fails keeps the clone")
    # what a plain diff and a plain bundle do not carry
    shutil.rmtree(c)
    git(d, "clone", "-q", o, c)
    put("a.txt", "staged\n")
    git(c, "add", "a.txt")
    put("a.txt", "one\n")
    put(".gitignore", "*.local\n")
    git(c, "add", ".gitignore")
    git(c, "commit", "-qm", "ign", "--", ".gitignore")
    git(c, "push", "-q", "origin", "HEAD")
    put("a.txt", "staged\n")
    git(c, "add", "a.txt")
    put("a.txt", "one\n")
    put("keep.local", "ignored work\n")
    put("x.txt", "s1\n")
    git(c, "add", "x.txt")
    git(c, "stash", "push", "-q", "-m", "older", "x.txt")
    put("x.txt", "s2\n")
    git(c, "add", "x.txt")
    git(c, "stash", "push", "-q", "-m", "newer", "x.txt")
    ok("keep.local" in fx.clone_wip(c)["real"], "an ignored file is WIP")
    b = fx.remove_clone({"clone": c, "item": "I0"})
    with open(os.path.join(b, "index.patch"), encoding="utf-8") as f:
        ok("+staged" in f.read(), "content only the index holds is in the bundle")
    u = os.path.join(d, "unb")
    git(d, "clone", "-q", o, u)
    git(u, "fetch", "-q", os.path.join(b, "commits.bundle"), "refs/rm-stash/*:refs/rm-stash/*")
    shown = [subprocess.run(["git", "-C", u, "show", "refs/rm-stash/%d:x.txt" % i], capture_output=True, text=True).stdout for i in (0, 1)]
    ok(sorted(shown) == ["s1\n", "s2\n"], "every stash is in the bundle, not just the newest: %s" % (shown,))
    git(d, "clone", "-q", o, c)
    put("keep.local", "upstream's\n")
    ok(any("keep.local" in w for w in fx.restore_bundle("I0", b, c)), "a restore that meets a newer file says so")
    with open(os.path.join(c, "keep.local"), encoding="utf-8") as f:
        ok(f.read() == "upstream's\n", "and does not overwrite it")
    ok(R.clone_item("/x/check-AB_C-1-c12") == "AB_C-1" and R.clone_item("/x/AB.q2") == "AB", "clone names read back")
    shutil.rmtree(d, ignore_errors=True)


def main():
    for t in (t_pool_jam, t_pool_real_git, t_books_frozen, t_unpublished_enrol_waits, t_staffing_places, t_staffing_backlog, t_staffing_rise, t_foreign_take, t_foreign_tomb,
              t_foreign_eligible, t_foreign_tree, t_foreign_back_in_line, t_staffing_edges, t_staffing_alarm, t_alarm_routes,
              t_worker_dies, t_same_failure, t_stale_worker, t_stop_order, t_spend, t_top_of_queue, t_share,
              t_done_path, t_crash_recovery, t_crash_windows, t_third_review, t_real_effects, t_launch_fail, t_breaker_di2, t_retire, t_concurrency, t_live_line):
        print("--", t.__name__)
        t()
    print("selftest_relentless: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
