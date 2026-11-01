#!/usr/bin/env python3
"""relentless.py with planted faults: worker dies, same failure repeats, stale worker publishes, spend limit, restart
returns to the top, share 0 and 1, plus crash recovery, a two-way lease race and live_line. No units, no ledger, no
network: Effects is replaced by FakeWorld."""
import json
import multiprocessing
import os
import shutil
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_line  # noqa: E402
import relentless as R  # noqa: E402

RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, share=0.5, max_workers=2,
             enrol_per_tick=50, max_queued=50, run_reserve=1000, item_spend_limit=10**7, day_spend_limit=10**9)
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

    def sync(self): pass
    def flush(self): return None

    def pool_order(self, r):
        return [i for i in sorted(self.items) if self.items[i] in ("proposed", "ready")
                and i not in getattr(self, "taken", ())], None

    def item_state(self, item):
        st = self.items.get(item)
        return None if st is None else {"state": st, "lease": None, "needs": "offline"}

    def item_text(self, item): return "text of " + item
    def ledger_start(self, item):
        self.items[item] = "doing"
    def ledger_close(self, item, sha, reason, live=None):
        if self.close_fail:
            why, self.close_fail = self.close_fail, None
            return why
        self.closes.append((item, sha))
        self.items[item] = "done"
    def ledger_note(self, item, text): self.notes.append(text)
    def ledger_needs_owner(self, item, why): self.needs.append(item)
    def ledger_needs(self, item, to, why): self.needs.append((item, to))
    def clone_path(self, item, q=0): return "/c/%s.%d" % (item, q)
    def prepare(self, st): return None
    def remove_clone(self, st): pass
    def clean_checkout(self, st, sha): return "/c/check", None
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
    def mem_gb(self): return self.mem
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


def main():
    for t in (t_worker_dies, t_same_failure, t_stale_worker, t_stop_order, t_spend, t_top_of_queue, t_share,
              t_done_path, t_crash_recovery, t_crash_windows, t_third_review, t_real_effects, t_launch_fail, t_retire, t_concurrency, t_live_line):
        print("--", t.__name__)
        t()
    print("selftest_relentless: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
