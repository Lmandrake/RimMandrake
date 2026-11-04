#!/usr/bin/env python3
"""relentless.py with planted faults: worker dies, same failure repeats, stale worker publishes, spend limit, restart
returns to the top, share 0 and 1, plus crash recovery, a two-way lease race and live_line. No units, no ledger, no
network: Effects is replaced by FakeWorld."""
import atexit
import glob
import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
import time
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_line  # noqa: E402
import relentless as R  # noqa: E402

RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, only_system_and_live=False, share=0.5, max_workers=2,
             enrol_per_tick=50, max_queued=50, run_reserve=1000, item_spend_limit=10**7, day_spend_limit=10**9,
             staffing=None, circling=None, walls=None,   # the machinery test runs with no wall; the wall has its own selftest
             same_failure_limit=3, max_approach_changes=None, account_settle_s=0)   # the ladder's machinery; the shipped 2 and its hold: selftest_relentless_block
STAFF = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json"))["staffing"], hold_s=600, stages=[3, 5, "budget"],
             launch_per_tick=2, work_launch_per_tick=2, check_backlog_max=2)  # mechanism tests pin their own numbers, not the live rules (card 2026-11-02 widened them)
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
        self.seat_holds = []
        self.tok = 0
        self.lfail = None
        self.close_fail = None
        self.unkillable = set()
        self.stops = []
        self.mem = 30.0
        self.is_pub = True
        self.changed_calls, self.live_nb = [], []
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
        self.pool = {}          # per world: a class-level dict leaks one test's clones into the next

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
                                        "owner": self.owners.get(item, "BENCH"),
                                        "guard_owed": item in getattr(self, "guard_owed", ())}

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
    def ledger_hold_to_seat(self, item, hold): self.seat_holds.append(item)
    needs_fail = None
    needs_back = "offline"
    def ledger_needs(self, item, to, why):
        self.needs.append((item, to))
        return self.needs_fail
    def needs_after_hold(self, item): return self.needs_back
    def clone_path(self, item, q=0): return "/c/%s.%d" % (item, q)
    def prepare(self, st):
        return "clone failed: POOL REFUSED: pool full" if self.refuse else None
    # the clone pool: path -> {busy, kept, real}. Empty unless a test plants one
    pool_max = 10
    refuse = False
    jams = ()
    jam_fail = None
    attn = ()
    signals = ()
    def conductor_attention(self, text):
        self.attn = list(self.attn) + [text]
    def alarm_signal(self, rec):
        self.signals = list(self.signals) + [rec["kind"]]
    def pool_clones(self): return sorted(self.pool)
    def pool_load(self): return len(self.pool), 0, self.pool_max, 10**12
    def clone_present(self, c): return c in self.pool
    def clone_busy(self, c): return self.pool[c].get("busy", False)
    def clone_idle_s(self, c): return self.pool[c].get("idle", 7200)
    def clone_wip(self, c): return {"kept": self.pool[c].get("kept", False), "carry": self.pool[c].get("carry", False), "carry_real": self.pool[c].get("carry_real", False), "real": self.pool[c].get("real", [])}
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
        c = "/c/check-%s-c%d" % (st["item"], (st.get("check_count") or 0) + 1)    # as Effects names it
        if self.pool:
            self.pool[c] = {"busy": True}
        return c, None
    def help_checkout(self, st, sha):
        if self.refuse or (self.pool and len(self.pool) >= self.pool_max):
            return None, "help clone failed: scratch_clone: FAILED: POOL REFUSED: pool full: 10 clones, cap 10\n"
        c = "/c/help-%s-c%d" % (st["item"], (st.get("help_count") or 0) + 1)
        if self.pool:
            self.pool[c] = {"busy": False}
        return c, None
    def published(self, sha): return self.is_pub
    def changed(self, base, sha, item):
        self.changed_calls.append((base, sha, item))
        return self.touched
    def head(self): return "base"
    def commit_time(self, sha): return 5000 if sha == "sha1" else 0

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
    def account_loss(self, run, clone, since, box=None): return getattr(self, "account_sign", None)
    def mem_gb(self):
        v, self.mem_once = getattr(self, "mem_once", None), None
        return self.mem if v is None else v
    def paused(self): return self.pause
    def live_check(self, line, nb):
        self.live_nb.append(nb)
        return self.live_broken


class Rig:
    def __init__(self, n=4, **rules):
        self.d = tempfile.mkdtemp(prefix="rl-")
        self.s = R.Store(self.d)
        self.w = FakeWorld(n)
        # pool_parked_lists names repo prose (infrastructure/state/items/...); a fixture must not read the real tree,
        # which a blind export lacks (OPS_RELENTLESS_BOOKS_UNSTICK_WGYL). Tests of parked lists set their own.
        self.r = dict(RULES, **{"snag_again_wait_h": 0, "pool_parked_lists": [], **rules})
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
    with open(x.s.p("queue_next.json"), encoding="utf-8") as f:
        ok(json.load(f)["t"] == x.now, "the tick writes the line's next names for RUNNING_NOW")
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


def t_snag_wait():
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "sample_thin", "time, not work", x.r, now=x.now, wait_hours=1)
    x.w.up[st["run"]["unit"]] = False
    n = len(x.w.launches)
    for _ in range(5):
        x.tick(600)
    ok(len(x.w.launches) == n, "snag --wait-hours: no worker before the hour is up")
    x.tick(1200)
    x.tick(120)
    ok(len(x.w.launches) > n, "snag --wait-hours: a worker after it")
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "sample_thin", "again", x.r, now=x.now, wait_hours=1000)
    ok(x.st("I0")["not_before"] == x.now + R.MAX_WAIT_HOURS * 3600, "a worker's word parks an item for the cap at most")


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
    ok(x.st("I0")["status"] != "held", "spend limit is advisory: not held (owner 2026-11-02)")
    ok("I0" not in x.w.needs, "spend limit: nothing routed to the owner")
    att = [j for j in journal(x) if j.get("do") == "attention" and j.get("key") == "item_spend_limit:I0"]
    ok(len(att) == 1 and "over the advisory item_spend_limit" in att[0]["why"], "spend limit: one attention, journalled")
    ok(any("I0 spent" in a and "nothing stopped" in a for a in x.w.attn), "spend limit: one line for the Conductor")
    ok(any(k == "relentless_attention_item_spend_limit:I0" for k in x.w.signals), "spend limit: told to Operations")
    x.tick()
    ok(len([j for j in journal(x) if j.get("do") == "attention"]) == 1, "spend limit: attention once, not per tick")
    ok(not any(st["status"] == "held" for st in x.s.states()), "spend limit: holds nothing")
    # unmeasured run charged at the reserve
    y = Rig(n=1, share=1.0)
    y.run_one("I0")
    st = y.st("I0")
    y.now += 400
    y.w.tok = 0
    y.w.up[st["run"]["unit"]] = False
    y.tick()
    ok(y.st("I0")["spent"] == y.r["run_reserve"], "unmeasured run costs the reserve")
    # day limit is advisory: the launch goes ahead and the Conductor hears of it
    z = Rig(n=1, share=1.0, day_spend_limit=500)
    z.tick()
    ok(z.st("I0")["status"] == "running" and z.w.launches, "day limit is advisory: the run starts")
    ok(any(j.get("do") == "attention" and j.get("key") == "day_spend_limit" for j in journal(z)),
       "day limit: attention journalled")
    ok(any("day_spend_limit 500" in a for a in z.w.attn), "day limit: the Conductor line says the limit")
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


def weak_round(x, i, sha, word="WEAK"):
    """One proof-only worker: finish at sha, then the check speaks if the gate let it through."""
    x.run_one(i)
    st = x.st(i)
    R.finish(x.s, i, st["gen"], sha, "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st(i)
    if st["status"] == "checking":
        R.verdict(x.s, i, st["check"]["nonce"], word, "holds; mutant M stays green")
        x.w.up[st["check"]["run"]["unit"]] = False
        x.tick()
        x.tick()


def t_proof_weak():
    x = Rig(n=1, share=1.0)
    full_pass(x, "I0", "WEAK")
    st = x.st("I0")
    ok(x.w.closes == [] and st["status"] != "done", "WEAK does not close: a weak proof is not a pass")
    ok(st["failures"].get("proof_weak") == 1 and st["proof_only"]["sha"] == "sha1", "WEAK returns the item, proof only, at that sha")
    ok(st["approach"] == "build" and st.get("failures").get("blind_fail") is None, "WEAK is no failed approach and no FAIL")
    ok(any("the proof has holes and the work is unproven" in n and "sha1" in n for n in x.w.notes), "the ledger says why the item is still open")
    x.run_one("I0")
    p = x.w.launches[-1][2]
    ok("PROOF ONLY" in p and "Leave the code alone" in p and "mutant M" not in p and "ran it" in p, "the next worker is told proof only, with the gaps")
    gen = x.st("I0")["gen"]
    R.contract(x.s, "I0", gen, "stronger proof", why="reach the skipped clause")
    ok(x.st("I0")["contract"]["proof"] == "stronger proof", "a proof-only worker may strengthen the contract")
    x.done()

    x = Rig(n=1, share=1.0)
    full_pass(x, "I0", "WEAK")
    checks = sum(1 for l in x.w.launches if "blind checker" in l[2] and "You did not do this work" in l[2])
    ok(checks == 1, "the WEAK check is seen by the counter, or the Marker row below is 0 == 0")
    weak_round(x, "I0", "sha1")
    st = x.st("I0")
    ok(st["failures"].get("proof_unchanged") == 1, "a finish on the weak sha is refused")
    x.w.touched = ["src/foo.py", "src/selftest_foo.py"]
    x.w.changed_calls.clear()
    weak_round(x, "I0", "sha2")
    ok(("sha1", "sha2", "I0") in x.w.changed_calls, "the proof gate compares the weak sha with the new one: %s" % x.w.changed_calls)
    st = x.st("I0")
    ok(st["failures"].get("proof_rework") == 1 and "src/foo.py" in st["last_fail"]["detail"] and "selftest_foo" not in st["last_fail"]["detail"],
       "code moved after a WEAK is refused, proof files are not named")
    now = sum(1 for l in x.w.launches if "blind checker" in l[2] and "You did not do this work" in l[2])
    ok(now == checks, "neither refusal spent a Marker")
    ok(st["status"] == "held" or st["hold"], "three returns on the proof stop, open and said")
    ok(st["hold"]["kind"] == "proof_weak" and st["approach"] == "build" and x.w.closes == [], "no redesign of good code, however long the proof takes")
    x.tick()
    x.tick()
    ok(x.st("I0")["status"] == "held" and x.w.seat_holds == ["I0"] and "I0" not in x.w.needs,
       "the stop reaches the seat, never needs=owner: %s %s" % (x.w.seat_holds, x.w.needs))
    x.tick()
    ok(x.w.seat_holds == ["I0"], "said once")
    R.unhold(x.s, "I0", "go on")
    st = x.st("I0")
    ok(st["proof_only"] and not any(st["failures"].get(k) for k in R.PROOF_ENDS), "unhold buys the proof fresh tries, still proof only")
    x.done()

    x = Rig(n=1, share=1.0)
    full_pass(x, "I0", "WEAK")
    x.w.touched = ["src/RimMandrake/rimflow/selftest_foo.py", "infrastructure/state/items/I0.md"]
    weak_round(x, "I0", "sha2", "PASS")
    ok(x.w.closes and x.w.closes[-1][1] == "sha2", "a stronger proof read PASS by a fresh Marker closes at the new sha")
    x.done()

    x = Rig(n=1, share=1.0)
    full_pass(x, "I0", "WEAK")
    x.w.touched = ["src/selftest_foo.py"]
    weak_round(x, "I0", "sha2", "FAIL")
    st = x.st("I0")
    ok(st["proof_only"] is None and st["failures"].get("blind_fail") == 1, "a FAIL on the stronger proof frees the code")
    x.done()

    x = Rig(n=1, share=1.0)
    full_pass(x, "I0", "WEAK")
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], R.PROOF_DEFECT, "new test red on the code", x.r)
    x.w.up[st["run"]["unit"]] = False
    ok(x.st("I0")["proof_only"] is None, "a proof that goes red on the held code frees the code")
    x.done()

    x = Rig(n=1, share=1.0)
    full_pass(x, "I0", "WEAK")
    ok(R.proof_gate(x.w, x.r, x.st("I0"), {"sha": "sha1"})[0] == "proof_unchanged", "the gate reads the sha it was held at")
    ok(R.proof_gate(x.w, x.r, dict(x.st("I0"), proof_only=None), {"sha": "sha1"}) == (None, None), "no WEAK, no gate")
    x.w.touched = ["tools/check_it.sh"]
    st = dict(x.st("I0"), contract={"proof": "bash tools/check_it.sh"})
    ok(R.proof_gate(x.w, x.r, st, {"sha": "sha2"}) == (None, None), "a path the contract names is proof")
    x.done()
    bad = None
    try:
        R.verdict(Rig(n=0).s, "I0", "n", "MAYBE", "x")
    except ValueError as e:
        bad = str(e)
    ok(bad and "WEAK" in bad, "a fourth word is refused")


def t_shadow_narrow_weak():
    W = R.relentless_wall
    ok(W.narrow_word("WEAK", " gap:other a mutant I wrote") == "PASS", "an invented mutant is no gap under the narrow rule")
    ok(W.narrow_word("WEAK", "GAP:DIFF hunk 2 put back, proof green") == "WEAK", "a hunk of the diff stays WEAK")
    ok(W.narrow_word("WEAK", "ran it") == "UNTAGGED", "an untagged WEAK is never guessed")
    ok(W.narrow_word("FAIL", "GAP:OTHER") == "FAIL" and W.narrow_word("PASS", "") == "PASS", "only WEAK moves")
    x = Rig(n=1, share=1.0)
    full_pass(x, "I0", "WEAK")
    t = R.shadow_tally(x.s)
    ok(t["verdicts"] == 1 and t["weak"] == 1 and t["untagged"] == 1 and t["differ"] == 0, "a live verdict is shadowed beside itself")
    ok(R.shadow_tally(x.s, "no_such_rule")["verdicts"] == 0, "a shadow rule counts only its own rows")
    x.done()


def t_marker_prompts_one_rule():
    st = {"item": "I", "candidate": {"sha": "S", "evidence": "E"}, "contract": {}}
    a, b = R.checker_prompt(st, "T", "N"), R.relentless_wall.marker_prompt(st, "T", "/b")
    for p in (a, b):
        ok("a contract that is easier than the item is a FAIL" in p, "the line stays, word for word")
        ok(all(line in p for line in R.relentless_wall.RULE), "both prompts carry the whole rule")
        ok("WEAK" in p and "is not a pass" in p, "WEAK is offered and is no pass")


def t_done_path():
    x = Rig(n=1, share=1.0)
    x.close_fail = None
    x.w.close_fail = "git hiccup"
    full_pass(x, "I0")
    x.tick()
    ok(x.st("I0")["status"] == "done" and x.w.closes == [("I0", "sha1")], "PASS closes, a failed close retries")
    ok(x.w.live_nb and all(n == 5000 for n in x.w.live_nb), "the live line is judged against the candidate's own commit time: %s" % x.w.live_nb)
    x.done()
    x = Rig(n=1, share=1.0)
    x.w.close_fail = "close: I0 has not earned its close at sha1: owed still owes C1 L1"
    full_pass(x, "I0")
    st = x.st("I0")
    ok(st["failures"].get("close_refused") == 1 and st["status"] != "closing" and x.w.closes == [],
       "a close the gate refuses goes back to the top with its reason: no retry for ever")
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
    ok(x.st("I0")["failures"].get("live_broken") == 1 and x.w.closes == [] and x.st("I0")["status"] not in ("closing", "done"),
       "a broken live line returns the item, it does not close")
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
    # rimflow's close refuses a fix that died with no guard: the candidate gate catches that first too
    x = Rig(n=1, share=1.0)
    x.w.guard_owed = {"I0"}
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    R.finish(x.s, "I0", st["gen"], "s", "e", now=x.now)
    x.tick()
    ok(x.st("I0")["failures"].get("bad_candidate") == 1 and "rimflow guard I0" in x.st("I0")["last_fail"]["detail"],
       "a fix that died, with no guard on record, is a bad candidate that says the way")
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
    acts = []
    R.spend_holds(x.s, x.w, RULES, x.now, acts)
    ok(x.st("I0")["status"] == "queued" and any(a["do"] == "spend_attention" for a in acts),
       "an unreaped quarantined run counts toward the item's advisory spend limit; it is not held")
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


def t_breaker_forgets_when_proved():
    """A worker started after the last failure has reported: the count starts over. It stood at 4 for days, so one
    failure reopened at once for the longest cool under a cause fixed the day before (TICK_SPEED_FIX_GAME_IDLES_WAITING)."""
    x = Rig(n=1, share=1.0, launch_breaker=2, breaker_cool_s=900, breaker_cool_max_s=1800)
    for i in range(2):
        R.launch_failed(x.s, x.r, x.now, "launcher died")
    ok(R.load_breaker(x.s)["fails"] == 2 and R.load_breaker(x.s)["at"] == x.now, "a failure stamps when: %s" % R.load_breaker(x.s))
    parked(x, "OLD", "running", "/c/O", run={"at": x.now - 50, "unit": "u"}, last_beat=x.now + 2500)
    x.now = R.load_breaker(x.s)["until"] + 1
    at = R.load_breaker(x.s)["at"]
    ok(not R.launch_proved(x.s, at + 1) and R.load_breaker(x.s)["fails"] == 2, "an open breaker runs its cool")
    ok(not R.launch_proved(x.s, x.now) and R.load_breaker(x.s)["fails"] == 2, "a worker older than the failure proves nothing")
    parked(x, "NEW", "running", "/c/N", run={"at": x.now + 10, "unit": "u"}, last_beat=None)
    ok(not R.launch_proved(x.s, x.now) and R.load_breaker(x.s)["fails"] == 2, "started but silent proves nothing")
    parked(x, "NEW", "running", "/c/N", run={"at": x.now + 10, "unit": "u"}, last_beat=x.now + 40)
    ok(R.launch_proved(x.s, x.now) and not R.load_breaker(x.s).get("fails"), "started after and reported: the count is gone")
    x.done()


def t_one_sha_checkout_charges_no_launcher():
    """The clone cannot read one sha: the launcher is fine, and the other items must still launch."""
    live = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    x = Rig(n=1)
    x.r = dict(x.r, **{k: live[k] for k in ("breaker_refusal_words",)})
    for why in ("checkout 567b22f: fatal: unable to read tree (567b22f)", "fatal: reference is not a tree: 567b22f"):
        R.launch_failed(x.s, x.r, x.now, why)
        ok(not R.load_breaker(x.s).get("fails"), "no charge: %s" % why)
    R.launch_failed(x.s, x.r, x.now, "No medium found")
    ok(R.load_breaker(x.s).get("fails") == 1, "a real launcher failure still charges")
    x.done()


def t_tick_budget_reaches_lease():
    """Deploy plans over the Windows mount outlived the unit's 20-minute kill, so no tick reached lease or flush. Past the
    budget game items wait for the next tick and the rest of the tick still runs."""
    live = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    ok(0 < live["tick_game_budget_s"] <= 600, "with one plan's 500 s still to finish, the budget stays inside the 1200 s kill: %s" % live["tick_game_budget_s"])
    for budget, skipped in ((420, 2), (None, 0)):
        x = Rig(n=2, share=1.0, tick_game_budget_s=budget)
        clock = [0]

        def wall():
            clock[0] += 500
            return clock[0]
        x.w.wall = wall
        parked(x, "G0", "game", "/c/G0", game={"phase": "prove", "sha": "s"})
        parked(x, "G1", "game", "/c/G1", game={"phase": "prove", "sha": "s"})
        leased = []
        real = R.lease
        R.lease = lambda *a, **k: (leased.append(1), real(*a, **k))[1]
        try:
            x.tick()
        finally:
            R.lease = real
        with open(x.s.p("journal.jsonl"), encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        rows = [r for r in rows if r.get("do") == "tick"]
        acts = [a for r in rows for a in r["acts"] if a.get("do") == "tick_budget"]
        ok(leased == [1], "lease ran (budget %s)" % budget)
        if skipped:
            ok(acts and acts[0]["skipped"] == skipped, "both game items wait: %s" % acts)
            ok(rows[-1]["wall_s"] > 0, "the journal says how long a tick took: %s" % rows[-1].get("wall_s"))
        else:
            ok(not acts, "no budget, no skip: %s" % acts)
        x.done()


def t_level_books_leaves_run_output():
    """A proof run in books dirties Transient/ and the registry; refusing on them froze the engine on old code for 52
    ticks of 2026-11-03. They stay as they are, origin moving one refuses, and any other dirt refuses as before."""
    reg = R.BOOKS_LEFT_IN_PLACE[1]
    d = tempfile.mkdtemp(prefix="rlbk-")

    def g(cwd, *a):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout

    def put(root, p, text):
        os.makedirs(os.path.dirname(os.path.join(root, p)) or root, exist_ok=True)
        with open(os.path.join(root, p), "w") as f:
            f.write(text)

    def read(root, p):
        with open(os.path.join(root, p)) as f:
            return f.read()
    origin, up, books = (os.path.join(d, n) for n in ("o.git", "up", "books"))
    g(d, "init", "-q", "--bare", "-b", "main", origin)
    g(d, "clone", "-q", origin, up)
    g(up, "checkout", "-q", "-B", "main")
    for p in (reg, "Transient/n.json", "code.py"):
        put(up, p, "one\n")
    g(up, "add", "--", reg, "Transient/n.json", "code.py")
    g(up, "commit", "-qm", "one")
    g(up, "push", "-q", "origin", "main")
    g(d, "clone", "-q", origin, books)
    fx = R.Effects.__new__(R.Effects)
    fx.books, fx.store = books, R.Store(os.path.join(d, "store"))

    def advance(p, text):
        put(up, p, text)
        g(up, "add", "--", p)
        g(up, "commit", "-qm", "move " + p)
        g(up, "push", "-q", "origin", "main")
        g(books, "fetch", "-q", "origin")

    put(books, reg, "from a proof run\n")
    put(books, "Transient/n.json", "from a proof run\n")
    put(books, "Transient/new.json", "untracked\n")
    advance("code.py", "two\n")
    ok(fx.level_books() is None, "run output does not stop a level")
    ok(read(books, "code.py") == "two\n" and not g(books, "rev-list", "--count", "HEAD..origin/main").strip() != "0", "the clone is level")
    ok(read(books, reg) == "from a proof run\n" and read(books, "Transient/n.json") == "from a proof run\n"
       and read(books, "Transient/new.json") == "untracked\n", "and the run's output is still there, byte for byte")

    advance(reg, "origin moved it\n")
    try:
        why = fx.level_books()
    except RuntimeError as e:
        why = str(e)
    ok(why and read(books, reg) == "from a proof run\n", "origin moving a left file refuses, nothing overwritten: %s" % why)
    g(books, "show", "HEAD:" + reg)     # the refusal is git's own; a run's output is cleared by whoever owns it, not here
    put(books, reg, "one\n")
    ok(fx.level_books() is None, "level again once the run's output has gone")

    put(books, "code.py", "a hand edit\n")
    advance("other.py", "x\n")
    why = fx.level_books()
    ok(why and "code.py" in why and read(books, "code.py") == "a hand edit\n", "other dirt refuses as before: %s" % why)
    shutil.rmtree(d, ignore_errors=True)


def t_level_books_shard_under_lock():
    """level_books restores a ledger shard under the flock model.append takes: an event appended while it waits on the
    lock is never truncated away (GPT review 2026-11-03: the check-then-truncate window lost it from tree and backup)."""
    d = tempfile.mkdtemp(prefix="rlbl-")
    shard = R.LEDGER_DIR + "BENCH.jsonl"

    def g(cwd, *a):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout

    def put(root, p, text, mode="w"):
        os.makedirs(os.path.dirname(os.path.join(root, p)), exist_ok=True)
        with open(os.path.join(root, p), mode) as f:
            f.write(text)

    def read(root, p):
        with open(os.path.join(root, p)) as f:
            return f.read()
    origin, up, books = (os.path.join(d, n) for n in ("o.git", "up", "books"))
    g(d, "init", "-q", "--bare", "-b", "main", origin)
    g(d, "clone", "-q", origin, up)
    g(up, "checkout", "-q", "-B", "main")
    put(up, shard, "a\n")
    g(up, "add", "--", shard)
    g(up, "commit", "-qm", "one")
    g(up, "push", "-q", "origin", "main")
    g(d, "clone", "-q", origin, books)
    put(up, shard, "b\n", "a")
    g(up, "commit", "-qam", "landed")
    g(up, "push", "-q", "origin", "main")
    g(books, "fetch", "-q", "origin")
    put(books, shard, "b\n", "a")      # the local event origin already holds: levelling may restore it
    fx = R.Effects.__new__(R.Effects)
    fx.books, fx.store = books, R.Store(os.path.join(d, "store"))
    ready = os.path.join(d, "ready")
    holder = subprocess.Popen([sys.executable, "-c", (
        "import fcntl, os, sys, time\n"
        "fd = os.open(sys.argv[1], os.O_WRONLY | os.O_APPEND)\n"
        "fcntl.flock(fd, fcntl.LOCK_EX)\n"
        "open(sys.argv[2], 'w').close()\n"
        "time.sleep(1.0)\n"
        "os.write(fd, b'c\\n')\n"
        "fcntl.flock(fd, fcntl.LOCK_UN)\n"), os.path.join(books, shard), ready])
    for _ in range(200):
        if os.path.exists(ready):
            break
        time.sleep(0.02)
    why = fx.level_books()
    holder.wait(timeout=30)
    ok(why and "moved while levelling" in why and read(books, shard) == "a\nb\nc\n",
       "an event appended under the lock refuses the level and survives: %s %r" % (why, read(books, shard)))
    put(books, shard, "a\nb\n")
    ok(fx.level_books() is None and read(books, shard) == "a\nb\n"
       and g(books, "rev-list", "--count", "HEAD..origin/main").strip() == "0", "with the shard quiet it levels")
    kept = glob.glob(fx.store.p("books_dirt", "*", shard))
    ok(len(kept) == 1, "and the restored shard is backed up: %s" % kept)

    # an untracked shard origin now tracks: renamed into the backup (a writer waiting on its lock appends there), and an
    # event that lands on that inode after the rename is carried back onto the shard
    new = R.LEDGER_DIR + "RUNNER.jsonl"
    put(up, new, "r\n")
    g(up, "add", "--", new)
    g(up, "commit", "-qm", "runner")
    g(up, "push", "-q", "origin", "main")
    g(books, "fetch", "-q", "origin")
    put(books, new, "r\n")
    ok(fx.level_books() is None and read(books, new) == "r\n", "an untracked landed shard levels")
    kept = glob.glob(fx.store.p("books_dirt", "*", new))
    ok(len(kept) == 1 and read(os.path.dirname(kept[0]), os.path.basename(kept[0])) == "r\n", "renamed into the backup: %s" % kept)
    with open(kept[0], "a") as f:
        f.write("late\n")
    fx._carry_late({new: b"r\n"}, {new: kept[0]})
    ok(read(books, new) == "r\nlate\n", "a late event on the renamed inode is carried back: %r" % read(books, new))
    fx._carry_late({new: b"r\nlate\n"}, {new: kept[0]})
    ok(read(books, new) == "r\nlate\n", "and nothing new carries nothing")
    probe = [sys.executable, "-c", "import fcntl, os, sys\nfd = os.open(sys.argv[1], os.O_RDONLY)\n"
             "try:\n    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)\nexcept OSError:\n    sys.exit(1)",
             os.path.join(books, shard)]
    with fx.shards_locked():
        held = subprocess.run(probe).returncode
    ok(held == 1 and subprocess.run(probe).returncode == 0, "git's replacement of the shards runs under their flock: %s" % held)
    shutil.rmtree(d, ignore_errors=True)


def t_real_effects():
    """The fakes cannot see an import that fails: walk the real read paths once against this tree's ledger."""
    d = tempfile.mkdtemp(prefix="rlfx-")
    store = R.Store(d)
    fx = R.Effects(dict(RULES, pool_seats=["BENCH"], pool_needs=["offline"], pool_targets=["v1"],
                        pool_kinds_exclude=[], pool_ids_exclude=[]), store)
    order, w = fx.pool_order(fx.r)
    ok(isinstance(order, list) and len(w.items) > 100, "real: pool_order reads the real ledger")
    want = {i.id for i in w.items.values() if R.eligible(i, fx.r, w) and i.target in (None, "v1")}
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


def journal(x):
    try:
        with open(x.s.p("journal.jsonl"), encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except OSError:
        return []


def shut(x):
    """The breaker open: admission refuses every start (a non-spend reason; spend limits are advisory)."""
    x.s._write(x.s.p("breaker.json"), json.dumps({"fails": 1, "until": x.now + 600, "why": "test"}))


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


def t_refused_start_is_held():
    """RELENTLESS_START_SILENCE_REFUSED_RETRY_LOOP: put down held and told, not retried and not retired."""
    x = Rig(n=1)
    calls = []
    x.w.ledger_start = lambda item: calls.append(item) or "BENCH may not `start` I0: it belongs to OWNER"
    for _ in range(2):
        x.tick()
        ok(x.st("I0")["status"] == "queued", "a refused start waits its turn in line")
        x.tick(x.r["breaker_cool_s"] + 1)
    st = x.st("I0")
    ok(len(calls) == 3 and st["status"] == "held" and st["hold"]["kind"] == "start_refused", "the third is held: %s" % st)
    ok("belongs to OWNER" in st["hold"]["why"] and not R.hold_is_his(st["hold"]), "the reason is on the hold, the seat's to read")
    x.tick(x.r["breaker_cool_s"] * 5)
    x.tick(x.r["breaker_cool_s"] * 5)
    ok(len(calls) == 3 and not x.w.launches and x.st("I0")["status"] == "held", "no more tries: %s" % calls)
    ok(x.w.seat_holds == ["I0"], "told once: %s" % x.w.seat_holds)
    R.unhold(x.s, "I0", "fixed", x.now)
    ok(x.st("I0")["status"] == "queued" and not x.st("I0").get("start_refusals") and not x.st("I0")["needs_back"],
       "unhold is a fresh count, no owner routing to undo")
    x.tick()
    ok(len(calls) == 4 and x.st("I0")["status"] == "queued", "and tries at once, three more before a new hold")
    x.done()
    # the count is of refusals in a row
    x = Rig(n=1)
    x.w.ledger_start, orig = (lambda item: "no"), x.w.ledger_start
    x.tick()
    ok(x.st("I0").get("start_refusals") == 1, "setup: one refusal")
    x.w.ledger_start = orig
    x.tick(x.r["breaker_cool_s"] + 1)
    ok(x.w.launches and "start_refusals" not in x.st("I0"), "a start that lands clears the count")
    x.done()
    # after a hand-over the item stayed in line for good, so this was a loop nothing ever ended
    x = foreign_rig()
    x.w.ledger_start = lambda item: "no"
    for _ in range(3):
        x.tick()
        x.tick(x.r["breaker_cool_s"] + 1)
    ok(x.st("I0")["status"] == "held" and x.st("I0")["hold"]["kind"] == "start_refused" and x.w.takes == ["I0"],
       "a foreign item is held too, taken once: %s %s" % (x.st("I0")["status"], x.w.takes))
    x.done()
    # the reason survives the cut
    long_advice = "\n".join(["advice line %d, of no use as a reason" % i for i in range(40)])
    r = types.SimpleNamespace(stderr="BENCH may not `start` I0: it belongs to OWNER.\n" + long_advice, stdout="")
    w = R.refusal_words(r)
    ok("belongs to OWNER" in w and len(w) <= 300, "the first line stays: %r" % w)
    r = types.SimpleNamespace(stderr="Traceback (most recent call last):\n" + long_advice + "\nKeyError: 'x'", stdout="")
    ok("KeyError" in R.refusal_words(r), "and a traceback's last line")
    ok(R.refusal_words(types.SimpleNamespace(stderr="", stdout="short")) == "short", "a short one is whole")


def t_refused_start_reason_reaches_hold():
    """The wiring t_refused_start_is_held plants over: the real Effects.ledger_start, only the rimflow subprocess stubbed,
    through lease to the hold. A refusal over ledger_start's cap is the real shape (515 bytes from cli.py start)."""
    x = Rig(n=1)
    real = R.Effects(x.r, x.s)
    calls = []
    advice = "\n".join("advice line %d, of no use as a reason" % i for i in range(40))
    refusal = types.SimpleNamespace(returncode=2, stdout="", stderr="BENCH may not `start` I0: it belongs to OWNER.\n" + advice)
    answer = [refusal]
    real.rimflow = lambda *a, **k: calls.append(a) or answer[0]
    x.w.ledger_start = real.ledger_start
    ok(len(refusal.stderr) > 300, "setup: the refusal is over the cap")
    for _ in range(3):
        x.tick()
        x.tick(x.r["breaker_cool_s"] + 1)
    st = x.st("I0")
    ok(len(calls) == 3 and all(c[:2] == ("start", "I0") for c in calls), "the real start was asked 3 times: %s" % calls)
    hold = st.get("hold") or {}
    ok(st["status"] == "held" and hold.get("kind") == "start_refused", "held: %s" % st["status"])
    ok("it belongs to OWNER" in hold.get("why", ""), "the first line is on the hold: %r" % hold.get("why"))
    ok("it belongs to OWNER" in st.get("start_refused_why", ""), "and in the item's last refusal: %r" % st.get("start_refused_why"))
    R.unhold(x.s, "I0", "fixed", x.now)
    answer[0] = types.SimpleNamespace(returncode=0, stdout="started", stderr="")
    x.tick()
    ok(x.st("I0").get("ledger_started") and x.w.launches and "start_refusals" not in x.st("I0"),
       "exit 0 from the real start is no refusal: %s" % x.st("I0")["status"])
    x.done()


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


def t_parked_list():
    """RELENTLESS_FILLER_FIX_TOO_KEEN_ON_PARKED: the filler staffed WARSCAR_PILGRIM_CAMP_SITES_1, which the owner's card
    parked on the paint list; it looked proposed+offline and foreign_ok had no parked test."""
    d = tempfile.mkdtemp(prefix="rlt-park-")
    items = os.path.join(d, "items")
    os.makedirs(os.path.join(items, "closed"))
    lst = os.path.join(items, "PAINT_LIST_X.md")
    with open(lst, "w", encoding="utf-8") as f:
        f.write("# PAINT_LIST_X\n\n## addition\n\nparked: `X_PARKED_FIX`\nparked: Y_PARKED_FIX\n"
                "Prose that says it is parked: Z_FREE_FIX does not park it.\n")
    r = dict(RULES, pool_seats=["BENCH", "FOUNDRY"], staffing=dict(STAFF), pool_ids_exclude=[], pool_parked_lists=[lst])

    def it(id, owner="FOUNDRY"):
        return types.SimpleNamespace(id=id, owner=owner, state="proposed", kind="task", title="a title", blocked=False,
                                     needs="offline", lease=None, target="v1")
    ok(R.parked_ids(r) == {"PAINT_LIST_X", "X_PARKED_FIX", "Y_PARKED_FIX"}, "parked lines and the list item: %s" % R.parked_ids(r))
    ok(not R.eligible(it("X_PARKED_FIX"), r), "a parked proposed+offline item of the other seat is not eligible")
    ok(not R.eligible(it("Y_PARKED_FIX", owner="BENCH"), r), "nor one of our own seat")
    ok(not R.eligible(it("PAINT_LIST_X", owner="BENCH"), r), "nor the list item itself")
    ok(R.eligible(it("Z_FREE_FIX"), r), "a mid-line 'parked:' in prose parks nothing")
    ok(R.pool_excluded("X_PARKED_FIX", r), "pool_excluded says so")
    with open(lst, "a", encoding="utf-8") as f:
        f.write("parked: Z_FREE_FIX\n")
    os.utime(lst, ns=(1, 2))
    ok(not R.eligible(it("Z_FREE_FIX"), r), "a line added to the list parks at once (no stale cache)")
    os.rename(lst, os.path.join(items, "closed", "PAINT_LIST_X.md"))
    ok(R.parked_ids(r) == set() and R.eligible(it("X_PARKED_FIX"), r), "the list item closed: its list is released")
    try:
        R.parked_ids(dict(r, pool_parked_lists=[os.path.join(items, "NO_SUCH_LIST.md")]))
        ok(False, "a listed file found nowhere must raise")
    except FileNotFoundError:
        ok(True, "a listed file found nowhere raises, never reads as empty")
    live = R.parked_ids(R.rules(os.path.join(R.HERE, "relentless_rules.json")))
    ok({"BIOME_PAINT_ONCE_AT_THE_END_1", "WARSCAR_PILGRIM_CAMP_SITES_1"} <= live, "the live rules park the paint list: %s" % sorted(live))
    # a snag on a parked item: never relaunched at the top, handed back to the ledger, out of the line
    with open(lst + ".2", "w", encoding="utf-8") as f:
        f.write("parked: I0\n")
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "gate_not_met", "done at the final painting", x.r, now=x.now)
    x.w.up[st["run"]["unit"]] = False
    x.r["pool_parked_lists"] = [lst + ".2"]
    launched = len(x.w.launches)
    x.tick(600)
    x.tick(600)
    x.tick(600)
    ok(len(x.w.launches) == launched, "a parked item back from a snag is not relaunched")
    ok(x.st("I0")["status"] == "retired" and x.w.items["I0"] == "ready", "it leaves the line and the ledger gets it back")
    x.done()


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
    acts = res["acts"] if isinstance(res, dict) else res
    ok(isinstance(acts, list) and any("staffing" in str(a.get("why")) for a in acts), "and says so")
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
    shut(x)
    x.tick()
    r = reading(x)
    ok(r["under"] and r["live"] == 0 and r["why"].startswith("breaker open"), "places full of waiting checks read as under")
    x.done()
    x = staffed(n=3, check_backlog_max=9)
    x.tick(), x.tick()
    st = [s for s in x.s.states() if s["status"] == "running"][0]
    R.contract(x.s, st["item"], st["gen"], "proof", live="once: test")
    R.finish(x.s, st["item"], st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    shut(x)
    x.tick()
    r = reading(x)
    ok(r["under"] and r["live"] >= 1 and r["why"].startswith("breaker open"), "one running, a check stuck: still under")
    x.done()
    # builders and checkers each draw on their own clone budget a tick, never more
    x = staffed(n=4, check_backlog_max=9, stages=[4])
    for _ in range(3):
        x.tick()
    finish_all(x)
    for _ in range(2):
        acts = x.tick()
        work = R.clones_this_tick(acts, "work")
        check = R.clones_this_tick(acts, "check")
        ok(work <= x.r["staffing"]["work_launch_per_tick"] and check <= x.r["staffing"]["launch_per_tick"],
           "clones per tick: at most work_launch_per_tick builders and launch_per_tick checks (%d, %d)" % (work, check))
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


def t_put_down_frees_places():
    """RELENTLESS_SLOTS_UNSTICK_BLOCKED_PUT_DOWN (owner 2026-11-02): nothing waiting holds a place."""
    # 16:36:58Z: two checks started, the shared clone count stopped every builder; 1 of 4 places ran with 8 ready
    x = staffed(n=8, check_backlog_max=9, stages=[4])
    x.tick()
    first = [st["item"] for st in x.s.states() if st["status"] == "running"]
    ok(len(first) == 2, "planted: two builders on the first tick")
    finish_all(x)
    acts = x.tick()
    live = sum(1 for st in x.s.states() if st["status"] in ("running", "checking"))
    ok(R.clones_this_tick(acts, "check") == 2 and R.clones_this_tick(acts, "work") == 2,
       "two checks starting do not stop the builders of the same tick: %s" % [a.get("do") for a in acts])
    ok(live == 4, "running + checking reach the cap of 4 with ready items, got %d" % live)
    x.done()
    # a candidate waiting on its judge holds no place: four builders run beside two waiting checks
    x = staffed(n=8, check_backlog_max=9, stages=[4])
    x.tick(), x.tick()
    finish_all(x)
    x.w.pool_max = 0        # no clone for a check: both wait as candidates
    x.r["staffing"]["launch_per_tick"] = 0
    x.tick(), x.tick()
    states = x.s.states()
    cand = sum(1 for st in states if st["status"] == "candidate")
    run = sum(1 for st in states if st["status"] == "running")
    ok(cand >= 2 and run == 4, "waiting checks are put down: %d candidates, %d builders running" % (cand, run))
    rd = json.load(open(x.s.p("reading.json")))
    ok(rd["places_live"] == 4 and {p["on"] for p in rd["put_down"]} == {"its check"} and len(rd["put_down"]) == cand,
       "the reading says what runs and what is put down on what: %s" % rd["put_down"])
    x.done()
    # a game item waiting parks its clone: released at once, its WIP bundled
    x = staffed(n=1)
    parked(x, "G0", "game", "/c/G0", game={"phase": "prove", "sha": "s"})
    parked(x, "G1", "game", "/c/G1", game={"phase": "staging", "sha": "s"})
    x.w.pool["/c/G0"] = {"idle": 5, "real": ["a.cs"]}
    x.w.pool["/c/G1"] = {"idle": 5}
    parked(x, "G2", "game", "/c/G2", game={"phase": "prove", "sha": "s"})      # the item's own case: parked on the game behind a trailing lesson
    x.w.pool["/c/G2"] = {"idle": 5, "carry": True}
    R.release_parked(x.s, x.w, x.r, x.now, [])
    ok(sorted(x.w.pool) == ["/c/G1"], "a waiting game item's clone goes; a staging one's stays: %s" % sorted(x.w.pool))
    ok(x.st("G0").get("bundle") == "/bundle//c/G0", "and its WIP goes with a bundle")
    ok(x.st("G2").get("bundle") == "/bundle//c/G2", "and its state-only commit goes with a bundle")
    x.done()


def t_prepare_remakes_clone():
    """BLUEDESERT_FLORA_PLANT_REFUSAL_1: a clone missing what a launch needs is bundled, removed and made again."""
    d = tempfile.mkdtemp(prefix="rl-prep-")
    try:
        books = os.path.join(d, "books")
        os.makedirs(os.path.join(books, "src/RimMandrake/Utils"))
        with open(os.path.join(books, "src/RimMandrake/Utils/scratch_clone.py"), "w") as f:    # makes a whole clone
            f.write("import os, sys\nc = os.path.join(os.environ['RM_SCRATCH_ROOT'], 'clones', sys.argv[sys.argv.index('--name') + 1])\n"
                    "os.makedirs(os.path.join(c, '.git'))\nos.makedirs(os.path.join(c, 'src/RimMandrake/Utils'))\n"
                    "open(os.path.join(c, 'src/RimMandrake/Utils/claude_bounded.sh'), 'w').close()\n")
        fx = object.__new__(R.Effects)
        fx.base, fx.books, fx.store = d, books, R.Store(os.path.join(d, "store"))
        bundled = []
        fx.bundle_clone = lambda item, c: bundled.append(c) or "/b/" + item
        fx.restore_bundle = lambda item, b, c: bundled.append(("restore", b))
        c = os.path.join(d, "clones", "I0.0")
        os.makedirs(os.path.join(c, ".git"))        # a .git and nothing else: the checkout was cut short
        st = R.new_state("I0", 0, "t")
        st["clone"] = c
        fx.store.save(st)
        why = fx.prepare(dict(st))
        ok(why is None and R.clone_gap(c) is None, "an incomplete clone is made again whole: %s" % why)
        ok(bundled[0] == c and bundled[1] == ("restore", "/b/I0"), "its WIP was bundled first and restored: %s" % bundled)
        ok(R.clone_gap(os.path.join(d, "clones", "gone")) == ".git", "a missing clone has a gap")
        st["clone"] = os.path.join(d, "elsewhere")
        os.makedirs(os.path.join(st["clone"], ".git"))
        ok("not the pool's" in fx.prepare(dict(st)) and os.path.isdir(st["clone"]), "a path outside the pool is never removed")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_close_idempotent():
    """A close that already landed writes nothing more (the 2026-11-02 doubled closes were union-merge copies)."""
    fx = object.__new__(R.Effects)
    calls = []
    fx.marked = set()
    fx.rimflow = lambda *a, **k: calls.append(a) or subprocess.CompletedProcess(a, 0, "", "")
    fx.closed = lambda item: True
    ok(fx.ledger_close("I0", "abc", "blind PASS") is None and not calls, "an item already done: no verify, no close")
    fx.closed = lambda item: False
    ok(fx.ledger_close("I0", "abc", "blind PASS") is None and [c[0] for c in calls] == ["verify", "close"],
       "an open item: verify then close, once: %s" % [c[0] for c in calls])


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
    ok(r["running"] == r["live"] and r["places"] == r["live"], "running means live; a waiting check is put down, no place")
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
    ok(r["running"] == 0 and r["places"] == 0, "three waiting checks: 0 running, put down, 0 places")
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
    wip_was = dict(x.w.pool["/c/H0"])       # H0 is held: the same commits, carryable, give the place back
    x.w.pool["/c/H0"].update(carry_real=True)
    ok(R.make_room(x.s, x.w, x.r, x.now, []) is None and "/c/H0" not in x.w.pool and x.st("H0").get("bundle") == "/bundle//c/H0",
       "a put-down item's carryable commits give room, with a bundle on its record: %s" % x.st("H0").get("bundle"))
    x.w.pool["/c/H0"] = wip_was
    held_again = x.st("H0")
    held_again.pop("bundle", None)
    x.s.save(held_again)
    parked(x, "D0", "retired", "/c/D0")
    x.w.pool["/c/D0"] = {"kept": True}
    x.tick()
    ok("/c/D0" not in x.w.pool, "a dead item's commits are bundled and released")
    x.done()

    # POOL_FIX_STATE_COMMITS_PIN_CLONES: make_room treats a carry-only clone as holding something: after the empty one, and with a bundle
    x = staffed(n=1)
    x.w.pool = {"/c/L%d" % i: {"busy": True} for i in range(8)}
    for name, wip in (("C0", {"carry": True}), ("C1", {})):
        parked(x, name, "held", "/c/" + name)
        x.w.pool["/c/" + name] = wip
    ok(R.make_room(x.s, x.w, x.r, x.now, []) is None and "/c/C0" in x.w.pool and "/c/C1" not in x.w.pool,
       "a clone with state commits to carry goes after one with nothing at risk: %s" % sorted(x.w.pool))
    ok(x.st("C1").get("bundle") is None, "nothing to carry, nothing recorded")
    x.w.pool_max = 9
    ok(R.make_room(x.s, x.w, x.r, x.now, []) is None and "/c/C0" not in x.w.pool and x.st("C0").get("bundle") == "/bundle//c/C0",
       "a state-only commit goes with a bundle the next clone restores: %s" % x.st("C0").get("bundle"))
    x.done()

    # a parked item's idle clone goes back before the idle hour reads it stranded, whatever the pool's load
    x = staffed(n=1)
    for name, status, wip in (("P0", "held", {"real": ["a.cs"]}), ("P1", "held", {"idle": 60, "real": ["a.cs"]}),
                              ("P2", "held", {"kept": True, "real": ["a.cs"]}), ("P3", "held", {"busy": True}),
                              ("P4", "queued", {}), ("P5", "held", {}), ("P6", "queued", {"idle": 60}),
                              ("P7", "blocked", {"idle": 5, "real": ["b.cs"]}),
                              ("P8", "blocked", {"kept": True, "carry_real": True}),
                              # idle past the release wait, so the put-down gate itself is what keeps it, not the wait
                              ("P9", "queued", {"idle": x.r["pool_parked_release_s"] + 60, "kept": True, "carry_real": True}),
                              ("PA", "held", {"carry": True})):
        parked(x, name, status, "/c/" + name)
        x.w.pool["/c/" + name] = wip
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
    import scratch_clone
    ok(x.r["pool_parked_release_s"] < scratch_clone.POOL_IDLE_S, "released before the alarm's idle hour, not after it")
    R.release_parked(x.s, x.w, x.r, x.now, [])
    ok(sorted(x.w.pool) == ["/c/P2", "/c/P3", "/c/P6", "/c/P9"],
       "put down (held, blocked): its clone goes at once, carryable commits too; a fresh queued one, uncarryable commits, a queued item's commits and busy stay: %s" % sorted(x.w.pool))
    ok(x.st("P8").get("bundle") == "/bundle//c/P8", "a blocked item's real commits go with a bundle: nothing strands")
    ok(x.st("P7").get("bundle") == "/bundle//c/P7", "a blocked item's WIP goes with a bundle")
    ok(x.st("P0").get("bundle") == "/bundle//c/P0", "WIP goes with a bundle the next clone restores")
    ok(x.st("PA").get("bundle") == "/bundle//c/PA", "a state-only commit goes with a bundle, or the next clone silently loses it")
    ok(x.st("P5").get("bundle") is None and x.st("P4").get("bundle") is None, "nothing to carry, nothing recorded")
    x.done()

    # and tick() is what does it: the call above proves the rule, this the wiring
    x = staffed(n=1)
    parked(x, "P0", "held", "/c/P0")
    x.w.pool["/c/P0"] = {"real": ["a.cs"]}
    x.tick()
    ok("/c/P0" not in x.w.pool, "a tick releases an idle parked clone, unpressed")
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


def t_flush_lands_prose_moves():
    """A close in the books moves the prose; the ledger line lands, so the move must too, or items/ keeps a done item."""
    d = tempfile.mkdtemp(prefix="rlprose-")
    store = R.Store(d)
    os.makedirs(store.dir, exist_ok=True)
    fx = R.Effects(dict(RULES), store)
    b, items = fx.books, R.ITEMS_DIR
    def git(*a):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=b, check=True,
                              capture_output=True, text=True).stdout
    os.makedirs(os.path.join(b, items, "closed"))
    subprocess.run(["git", "init", "-q", "-b", "main", b], check=True)
    for n in ("MOVED.md", "ALONE.md", "live.md"):
        with open(os.path.join(b, items, n), "w") as f:
            f.write(n)
    with open(os.path.join(b, "publish"), "w") as f:
        f.write('#!/bin/sh\nprintf "%s\\n" "$@" > published.txt\n')
    os.chmod(os.path.join(b, "publish"), 0o755)
    git("add", ".")
    git("commit", "-qm", "base")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    ok(fx.prose_moves() == [], "prose: a clean tree has no move")
    os.rename(os.path.join(b, items, "MOVED.md"), os.path.join(b, items, "closed", "MOVED.md"))     # what rimflow close does
    os.remove(os.path.join(b, items, "ALONE.md"))
    with open(os.path.join(b, items, "closed", "NEW.md"), "w") as f:
        f.write("no live twin")
    with open(os.path.join(b, items, "live.md"), "a") as f:
        f.write("edited")
    want = [items + "MOVED.md", items + "closed/MOVED.md"]
    ok(fx.prose_moves() == want, "prose: only the moved pair, never a lone deletion, new file or edit")
    ok(fx.flush() is None, "prose: flush publishes")
    with open(os.path.join(b, "published.txt")) as f:
        said = f.read().split("\n")
    ok(all(p in said for p in want), "prose: flush names both paths of the move, with no shard dirty")
    ok(not any(items + n in said for n in ("ALONE.md", "live.md", "closed/NEW.md")), "prose: and nothing else")
    shutil.rmtree(d, ignore_errors=True)


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
    # one seat shard is written by several clones, so landing order differs from write order: the same lines in another
    # order (BOOKS_STALE_FIX_ART_SHARD_REORDER) is landed, not "unlanded", and must not freeze the books
    put(b, L, "three\none\ntwo\n")
    put(up, L, "one\ntwo\nthree\nfive\n")
    git(up, "commit", "-qam", "up-reorder")
    git(up, "push", "-q", "origin", "main")
    why = fx.sync()
    ok(why is None, "a reordered shard with every line landed levels: %s" % why)
    ok(git(b, "rev-parse", "HEAD") == git(up, "rev-parse", "HEAD"), "reordered shard: level with origin")
    # the same reorder in a shard OUTSIDE the ledger dir (code_review, art; BOOKS_STALE_FIX_ART_SHARD_REORDER)
    RV = "infrastructure/state/code_review/B.jsonl"
    put(up, RV, "a\nb\nc\n")
    git(up, "add", RV)
    git(up, "commit", "-qm", "shard")
    git(up, "push", "-q", "origin", "main")
    fx.sync()
    put(b, RV, "c\na\nb\n")
    put(up, "code.py", "v2b\n")
    git(up, "commit", "-qam", "up-shard")
    git(up, "push", "-q", "origin", "main")
    why = fx.sync()
    ok(why is None, "a set-equal reorder of a code_review shard levels: %s" % why)
    ok(git(b, "rev-parse", "HEAD") == git(up, "rev-parse", "HEAD"), "shard reorder: level with origin")
    # that push never touched the shard, so the fast-forward alone took it. Origin moving the shard is the case that
    # jammed: the fast-forward refuses and only shuffled_shards lets the level through
    def restored():
        if not os.path.exists(store.p("journal.jsonl")):
            return 0
        with open(store.p("journal.jsonl"), encoding="utf-8") as f:
            return sum('"books_reorder_restored"' in x for x in f)
    ok(restored() == 0, "a fast-forward restored nothing and journals nothing")
    put(up, RV, "a\nb\nc\nd0\n")
    git(up, "commit", "-qam", "up-shard-moved")
    git(up, "push", "-q", "origin", "main")
    why = fx.sync()
    ok(why is None, "a reordered shard origin also moved levels: %s" % why)
    ok(git(b, "rev-parse", "HEAD") == git(up, "rev-parse", "HEAD"), "moved shard: level with origin")
    with open(os.path.join(b, RV), encoding="utf-8") as f:
        ok(f.read() == "a\nb\nc\nd0\n", "and the shard holds origin's bytes")
    ok(restored() == 1, "the journal says the shard was restored once it was")
    put(b, RV, "d0\nc\na\nb\n")
    put(b, "code.py", "a hand edit\n")
    put(up, RV, "a\nb\nc\n")
    git(up, "commit", "-qam", "up-refused")
    git(up, "push", "-q", "origin", "main")
    why = str(fx.sync())
    ok("code.py" in why, "other dirt beside the reorder still refuses: %s" % why)
    ok(restored() == 1, "and a refused level journals no restore")
    put(b, "code.py", "v2b\n")
    ok(fx.sync() is None, "level again once the other dirt has gone")
    ok(restored() == 2, "and that level journals its restore")
    put(b, RV, "c\na\nb\nextra\n")
    put(up, "code.py", "v2c\n")
    put(up, RV, "a\nb\nc\nd\n")
    git(up, "commit", "-qam", "up-shard2")
    git(up, "push", "-q", "origin", "main")
    why = str(fx.sync())
    ok("outside the ledger" in why, "an added line in a shard still stops it: %s" % why)
    put(b, RV, "a\nb\nc\n")
    fx.sync()
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


def t_put_down_real_commit_end_to_end():
    """POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG, through the real release_parked, Effects, Store and git: a blocked item's commit
    leaves the pool in its bundle and comes back whole; a queued item's stays. t_put_down_every_shape: the rest of what a clone can hold."""
    d = tempfile.mkdtemp(prefix="rlcarry-")
    store = R.Store(d)
    r = dict(RULES, pool_parked_release_s=0, warm_clones=0)
    fx = R.Effects(r, store)
    def git(c, *a):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True, capture_output=True, text=True).stdout
    o = os.path.join(d, "o.git")
    os.makedirs(os.path.join(d, "clones"))
    git(d, "init", "-q", "--bare", o)
    def clone_with_commit(item, status):
        c = os.path.join(d, "clones", item)
        git(d, "clone", "-q", o, c)
        with open(os.path.join(c, item + ".txt"), "w", encoding="utf-8") as f:
            f.write("base\n")
        git(c, "add", item + ".txt")
        git(c, "commit", "-qm", "base")
        git(c, "push", "-q", "origin", "HEAD")
        with open(os.path.join(c, "real.cs"), "w", encoding="utf-8") as f:
            f.write("real work\n")
        git(c, "add", "real.cs")
        git(c, "commit", "-qm", "real work")
        st = R.new_state(item, 0, "t")
        st.update(clone=c, status=status)
        store.save(st)
        return c
    def release():
        acts = []
        R.release_parked(store, fx, r, R.time.time(), acts)
        return acts
    # blocked, one real commit: the clone frees, the commit is on the record
    c = clone_with_commit("BLK", "blocked")
    ok(not os.path.exists(store.p("items", "BLK", "bundles")), "no earlier bundle can answer for this one")
    acts = release()
    b = store.load("BLK").get("bundle")
    ok(not fx.clone_present(c) and [x["do"] for x in acts] == ["clone_released"], "a blocked item's real commit frees its clone: %s" % (acts,))
    ok(b and os.path.exists(os.path.join(b, "carry")) and os.path.exists(os.path.join(b, "commits.bundle")), "and is carried, on the item's record: %s" % (b,))
    # the next clone gets it back as an unlanded commit, and the next worker is told
    git(d, "clone", "-q", o, c)
    ok(fx.restore_bundle("BLK", b, c) == [], "the bundle restores")
    ok(os.path.exists(os.path.join(c, "real.cs")), "real.cs came back")
    ok(git(c, "rev-list", "--count", "HEAD", "--not", "--remotes").strip() == "1", "as one unlanded commit, not as loose files")
    ok("1 unlanded commit(s) came back by cherry-pick: land them or drop them" in store.learned("BLK"), "the next worker reads it: %r" % store.learned("BLK"))
    shutil.rmtree(c)
    store.save(dict(store.load("BLK"), clone=None))
    # queued: not put down, so past the wait its commit still stays in the clone
    c = clone_with_commit("QUE", "queued")
    ok(release() == [] and fx.clone_present(c) and store.load("QUE").get("bundle") is None, "a queued item's real commit stays in its clone")
    store.save(dict(store.load("QUE"), status="retired", clone=None))
    shutil.rmtree(c)
    shutil.rmtree(d, ignore_errors=True)


def t_put_down_every_shape():
    """Every commit a blocked item holds leaves the pool and is back, or it is named and alarmed: a merge, a commit beside a stash, a
    stash alone, a side branch, a tag, a clashing branch name, a conflict; and the clone that truly cannot go stays."""
    d = tempfile.mkdtemp(prefix="rlshape-")
    store = R.Store(d)
    alarms = []
    store.on_alarm = alarms.append
    r = dict(RULES, pool_parked_release_s=0, warm_clones=0)
    fx = R.Effects(r, store)
    def git(c, *a):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True, capture_output=True, text=True).stdout
    def put(c, name, text):
        with open(os.path.join(c, name), "w", encoding="utf-8") as f:
            f.write(text)
    def commit(c, name, text, msg="w"):
        put(c, name, text)
        git(c, "add", name)
        git(c, "commit", "-qm", msg)
    o = os.path.join(d, "o.git")
    os.makedirs(os.path.join(d, "clones"))
    git(d, "init", "-q", "--bare", o, "-b", "main")
    def clone(item, status="blocked"):
        c = os.path.join(d, "clones", item)
        git(d, "clone", "-q", o, c)
        commit(c, item + ".txt", "base\nline\n", "base")
        git(c, "push", "-q", "origin", "HEAD")
        st = R.new_state(item, 0, "t")
        st.update(clone=c, status=status)
        store.save(st)
        return c
    def out_and_back(item, c):
        """release_parked takes it, and the next clone gets it back. -> (fresh clone, bad)"""
        R.release_parked(store, fx, r, R.time.time(), [])
        b = store.load(item).get("bundle")
        ok(not fx.clone_present(c) and b and os.path.exists(os.path.join(b, "carry")), "%s: the blocked clone is released, bundle on the record: %s" % (item, b))
        git(d, "clone", "-q", o, c)
        return c, fx.restore_bundle(item, b, c)
    def text(c, name):
        return open(os.path.join(c, name), encoding="utf-8").read()
    def gone(item, c):
        shutil.rmtree(c)
        store.save(dict(store.load(item), status="retired", clone=None))
    def unlanded(c):
        return int(git(c, "rev-list", "--count", "HEAD", "--not", "--remotes").strip())

    # a merge, with a resolution only the merge commit holds
    c = clone("MRG")
    trunk = git(c, "rev-parse", "--abbrev-ref", "HEAD").strip()
    git(c, "checkout", "-qb", "side")
    commit(c, "MRG.txt", "side\nline\n", "side")
    commit(c, "side.cs", "side\n", "side file")
    git(c, "checkout", "-q", trunk)
    commit(c, "MRG.txt", "main\nline\n", "main")
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "merge", "-q", "side"], cwd=c, capture_output=True)   # conflicts: exit 1 is expected
    ok(os.path.exists(os.path.join(c, ".git", "MERGE_HEAD")), "the merge stopped on its conflict, not on setup")
    put(c, "MRG.txt", "resolved\nline\n")
    git(c, "add", "MRG.txt")
    git(c, "commit", "-qm", "merge")
    w = fx.clone_wip(c)
    ok(w["kept"] and w["carry_real"], "a merge is carried: %s" % (w,))
    c, bad = out_and_back("MRG", c)
    ok(bad == [], "a merge restores: %s" % (bad,))
    ok(text(c, "MRG.txt") == "resolved\nline\n" and text(c, "side.cs") == "side\n", "with the merge's resolution and the side's file")
    ok(unlanded(c) == 2 and fx.clone_wip(c)["kept"], "as unlanded commits along the first parents: %d" % unlanded(c))
    ok("2 unlanded commit(s) came back by cherry-pick: land them or drop them" in store.learned("MRG"), "the next worker reads it: %r" % store.learned("MRG"))
    gone("MRG", c)

    # a real commit beside a stash
    c = clone("STA")
    commit(c, "real.cs", "real\n")
    put(c, "real.cs", "stashed\n")
    git(c, "stash", "push", "-q", "-m", "keep me", "real.cs")
    ok(fx.clone_wip(c)["carry_real"], "a commit beside a stash is carried")
    c, bad = out_and_back("STA", c)
    ok(bad == [] and text(c, "real.cs") == "real\n" and unlanded(c) == 1, "the commit is back: %s" % (bad,))
    ok("keep me" in git(c, "stash", "list"), "the stash is back on the list, by name")
    git(c, "stash", "pop", "-q")
    ok(text(c, "real.cs") == "stashed\n", "and pops to what it held")
    ok("1 stash(es) back" in store.learned("STA"), "the next worker is told of the stash")
    gone("STA", c)

    # stashes alone, no commit: in order
    c = clone("SOL")
    put(c, "SOL.txt", "older\nline\n")
    git(c, "stash", "push", "-q", "-m", "older")
    put(c, "SOL.txt", "newer\nline\n")
    git(c, "stash", "push", "-q", "-m", "newer")
    ok(fx.clone_wip(c)["carry_real"], "a stash alone is carried")
    c, bad = out_and_back("SOL", c)
    ok(bad == [] and unlanded(c) == 0, "two stashes restore with no commit: %s" % (bad,))
    subj = git(c, "stash", "list", "--format=%gs").splitlines()
    ok(len(subj) == 2 and "newer" in subj[0] and "older" in subj[1], "newest still on top: %s" % (subj,))
    gone("SOL", c)

    # a real commit on HEAD and another on a side branch and a tag
    c = clone("OTH")
    commit(c, "real.cs", "real\n")
    trunk = git(c, "rev-parse", "--abbrev-ref", "HEAD").strip()
    git(c, "checkout", "-qb", "other", "HEAD~1")
    commit(c, "oth.cs", "other\n")
    git(c, "checkout", "-q", trunk)
    git(c, "checkout", "-q", "--detach", "HEAD~1")
    commit(c, "tagged.cs", "tagged\n")
    git(c, "tag", "keep-this")
    git(c, "checkout", "-q", trunk)
    c, bad = out_and_back("OTH", c)
    ok(bad == [] and text(c, "real.cs") == "real\n", "HEAD's commit is back: %s" % (bad,))
    ok(git(c, "show", "other:oth.cs") == "other\n", "the side branch's commit is back on its branch")
    ok(git(c, "show", "keep-this:tagged.cs") == "tagged\n", "the tag's commit is back on its tag")
    ok(not git(c, "for-each-ref", "refs/rm-carried"), "no working ref left behind")
    said = store.learned("OTH")
    ok("refs/heads/other" in said and "refs/tags/keep-this" in said, "and the next worker is told: %r" % said)
    ok(set(git(c, "rev-list", "--branches", "--tags", "--not", "--remotes").split()) and fx.clone_wip(c)["kept"], "still reads as unlanded work")
    gone("OTH", c)

    # HEAD left on a branch: main's own unpushed commit may not overwrite the fresh main
    c = clone("NAM")
    commit(c, "m.cs", "main's\n")
    git(c, "checkout", "-qb", "fix", "HEAD~1")
    commit(c, "f.cs", "fix\n")
    c, bad = out_and_back("NAM", c)
    ok(bad == [] and text(c, "f.cs") == "fix\n", "HEAD's line comes back: %s" % (bad,))
    ok(git(c, "show", "carried/main:m.cs") == "main's\n", "the clashing branch comes back under carried/")
    gone("NAM", c)

    # already landed under another hash: skipped, and what follows it still comes
    c = clone("RED")
    commit(c, "red.cs", "red\n")
    commit(c, "after.cs", "after\n")
    u = os.path.join(d, "up")
    git(d, "clone", "-q", o, u)
    commit(u, "red.cs", "red\n", "landed elsewhere")
    git(u, "push", "-q", "origin", "HEAD")
    c, bad = out_and_back("RED", c)
    ok(bad == [] and text(c, "after.cs") == "after\n" and unlanded(c) == 1, "a commit origin already holds is skipped, the next one comes: %s" % (bad,))
    ok("1 already on origin" in store.learned("RED"), "and that is said: %r" % store.learned("RED"))
    gone("RED", c)
    shutil.rmtree(u)

    # a conflict: not silent, not lost
    c = clone("CON")
    commit(c, "CON.txt", "mine\nline\n")
    u = os.path.join(d, "up")
    git(d, "clone", "-q", o, u)
    commit(u, "CON.txt", "theirs\nline\n", "upstream")
    git(u, "push", "-q", "origin", "HEAD")
    sha = git(c, "rev-parse", "HEAD").strip()
    b_alarms = len(alarms)
    c, bad = out_and_back("CON", c)
    ok(any("did not re-apply" in x for x in bad), "a conflict is named: %s" % (bad,))
    ok(text(c, "CON.txt") == "theirs\nline\n" and not git(c, "status", "--porcelain"), "the next clone is left clean")
    said = store.learned("CON")
    ok("did not all come back" in said and "/bundles/" in said, "the next worker is told where it is: %r" % said)
    ok([x["kind"] for x in alarms[b_alarms:]] == ["restore_incomplete"], "and it is an alarm: %s" % (alarms[b_alarms:],))
    bundle = [x for x in alarms if x["kind"] == "restore_incomplete"][-1]["bundle"]
    git(u, "fetch", "-q", os.path.join(bundle, "commits.bundle"), "HEAD")
    ok(git(u, "rev-parse", "FETCH_HEAD").strip() == sha, "the commit is in that bundle")
    gone("CON", c)
    shutil.rmtree(u)

    # the one clone that cannot go: unreadable. It stays; scratch_clone's alarm covers it (selftest_scratch_clone)
    c = clone("BAD")
    os.remove(os.path.join(c, ".git", "HEAD"))
    w = fx.clone_wip(c)
    ok(w["kept"] and not w["carry_real"], "an unreadable clone is not carried: %s" % (w,))
    R.release_parked(store, fx, r, R.time.time(), [])
    ok(fx.clone_present(c) and store.load("BAD").get("bundle") is None, "and stays")
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
    # POOL_UNLANDED_COMMITS_NEVER_RELEASE: a worker's trailing lesson/ledger commit must not pin its clone for good
    shutil.rmtree(c)
    git(d, "clone", "-q", o, c)
    os.makedirs(os.path.join(c, "infrastructure/state/lessons"))
    put("infrastructure/state/lessons/l1.md", "a lesson\n")
    git(c, "add", "infrastructure/state/lessons/l1.md")
    git(c, "commit", "-qm", "lesson")
    w = fx.clone_wip(c)
    ok(not w["kept"] and w["carry"], "a state-only commit does not pin the clone: %s" % (w,))
    b = fx.remove_clone({"clone": c, "item": "I0"})
    ok(b and os.path.exists(os.path.join(b, "carry")) and not fx.clone_present(c), "released with the commit in the bundle")
    git(d, "clone", "-q", o, c)
    ok(fx.restore_bundle("I0", b, c) == [], "the next clone re-applies it")
    ok(os.path.exists(os.path.join(c, "infrastructure/state/lessons/l1.md")) and fx.clone_wip(c)["carry"], "the lesson came back as a commit")
    put("b2.txt", "real\n")
    git(c, "add", "b2.txt")
    git(c, "commit", "-qm", "real work")
    w = fx.clone_wip(c)
    ok(w["kept"] and w["carry_real"], "a commit with real work pins it unless put down, when a bundle can carry it: %s" % (w,))
    # POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG: a blocked item's real commit leaves the pool and comes back whole
    # a fresh item name: bundle dirs are named by the second and the clone, so I0's earlier state-only bundle would answer for this one
    store.save(R.new_state("I1", 0, "t"))
    ok(not os.path.exists(store.p("items", "I1", "bundles")), "no earlier bundle of this item can answer for this one")
    b = fx.remove_clone({"clone": c, "item": "I1"})
    ok(b and os.path.exists(os.path.join(b, "carry")) and not fx.clone_present(c), "a real commit is released in the bundle")
    git(d, "clone", "-q", o, c)
    ok(fx.restore_bundle("I1", b, c) == [], "the next clone re-applies the real commit")
    ok(os.path.exists(os.path.join(c, "b2.txt")) and fx.clone_wip(c)["carry_real"], "the real work came back as a commit, still unlanded")
    ok("came back by cherry-pick: land them or drop them" in store.learned("I1"), "the next worker is told to land what came back: %r" % store.learned("I1"))
    # the item says lesson OR LEDGER: a ledger-only commit takes the same road out and back
    led = "infrastructure/state/ledger/events/BENCH.jsonl"
    shutil.rmtree(c)
    git(d, "clone", "-q", o, c)
    os.makedirs(os.path.join(c, os.path.dirname(led)), exist_ok=True)
    put(led, '{"tail":"after the landing"}\n')
    git(c, "add", led)
    git(c, "commit", "-qm", "ledger tail")
    w = fx.clone_wip(c)
    ok(not w["kept"] and w["carry"], "a ledger-only commit does not pin the clone: %s" % (w,))
    b = fx.remove_clone({"clone": c, "item": "I0"})
    ok(b and os.path.exists(os.path.join(b, "carry")) and not fx.clone_present(c), "released with the ledger commit in the bundle")
    git(d, "clone", "-q", o, c)
    ok(fx.restore_bundle("I0", b, c) == [], "the next clone re-applies the ledger commit")
    ok(os.path.exists(os.path.join(c, led)) and fx.clone_wip(c)["carry"], "the ledger line came back as a commit")
    # one commit holding a ledger line AND real work is real work
    put(led, '{"tail":"after the landing"}\n{"tail":"and more"}\n')
    put("b3.txt", "real\n")
    git(c, "add", led, "b3.txt")
    git(c, "commit", "-qm", "ledger and real work")
    w = fx.clone_wip(c)
    ok(w["kept"] and not w["carry"], "a ledger line beside real work in one commit still pins it: %s" % (w,))
    ok(R.clone_item("/x/check-AB_C-1-c12") == "AB_C-1" and R.clone_item("/x/AB.q2") == "AB", "clone names read back")
    shutil.rmtree(d, ignore_errors=True)


HELP = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json"))["circling"], enabled=False)      # the consult, not the watch


def consults(rig):
    return [x for x in rig.w.launches if "-help-" in x[1]]


def workers(rig):
    return [x for x in rig.w.launches if "-work-" in x[1]]


def circle(rig, item="I0", detail="went round"):
    """A hit by the path RW2's tick rule will use: the fence-first fail, class circling, then the unit goes down."""
    rig.run_one(item)
    gen = rig.st(item)["gen"]
    unit = rig.st(item)["run"]["unit"]
    R.snag(rig.s, item, gen, "circling", detail, rig.r, now=rig.now)
    rig.w.up[unit] = False


def answer(rig, item="I0", *options):
    R.help_answer(rig.s, item, rig.st(item)["help"]["nonce"], list(options) or ["try the other seam | seam log shows X"],
                  rig.r, now=rig.now)
    rig.w.up[rig.st(item)["help"]["run"]["unit"]] = False


def t_help_forced_once():
    """S1: two circling hits, exactly one consult. One hit, none. Hits inside the cool wait; after it, one more."""
    g = Rig(1, circling=HELP)
    circle(g, detail="first round")
    for _ in range(3):
        g.tick()
    ok(not consults(g), "one circling hit asks for no consult")
    ok(g.st("I0")["status"] == "running", "and the item simply goes on")
    circle(g, detail="second round")
    ok(g.st("I0")["help"]["status"] == "wanted", "the second hit wants the consult at once, under the fail's own lock")
    runs = len(workers(g))
    for _ in range(4):
        g.tick()
    ok(len(consults(g)) == 1, "two hits give exactly one consult: %d" % len(consults(g)))
    ok(consults(g)[0][3] == g.r["help_agent"] == "rm-consult", "it is the read-only agent")
    ok(len(workers(g)) == runs, "no worker starts while the consult is out")
    answer(g)
    g.tick()
    ok(g.st("I0")["help"]["status"] == "answered" and len(consults(g)) == 1, "answered, and no second one")
    circle(g)
    circle(g)
    for _ in range(4):
        g.tick()
    answered_alone = g.st("I0")["status"] == "running"
    ok(len(consults(g)) == 1 and answered_alone, "two more hits inside help_cool_h: no second consult, no wait either")
    g.now += g.r["circling"]["help_cool_h"] * 3600
    for _ in range(2):
        g.tick()
    ok(len(consults(g)) == 2, "past the cool the hits held back get their one: %d" % len(consults(g)))
    g.done()


def t_help_own_call_spends_hits():
    g = Rig(1, circling=HELP)
    circle(g)
    circle(g)
    g.tick()
    g.tick()
    answer(g)
    g.tick()
    g.now += g.r["circling"]["help_cool_h"] * 3600
    g.tick()
    g.tick()
    ok(len(consults(g)) == 1, "the cool running out is no hit: spent hits never ask twice")
    g.done()
    g = Rig(1, circling=HELP)
    circle(g)
    g.run_one("I0")
    R.ask_help(g.s, "I0", g.st("I0")["gen"], "stuck", g.r, now=g.now)
    g.tick()
    answer(g)
    circle(g)
    circle(g)
    g.tick()
    ok(len(consults(g)) == 1, "the hit before a worker's own call is spent, and the two after wait out its cool")
    g.now += g.r["circling"]["help_cool_h"] * 3600
    g.tick()
    g.tick()
    ok(len(consults(g)) == 2, "two hits after a worker's own call earn their one, past the cool: %d" % len(consults(g)))
    with open(os.path.join(R.HERE, "..", "..", "..", ".claude", "agents", g.r["help_agent"] + ".md"), encoding="utf-8") as f:
        head = f.read().split("---")[1]
    ok("tools: Bash, Read\n" in head, "the consult's agent exists and cannot Write or Edit")
    g.done()


def t_help_round_two_vendor():
    """Design section 7: round one the same model, round two a second vendor through the gpt_consult port. A round
    is a consult, never a launch try: a dead round-one try relaunches round one's agent."""
    g = Rig(1, circling=HELP)
    circle(g)
    circle(g)
    g.tick()
    g.w.up[g.st("I0")["help"]["run"]["unit"]] = False       # round one's first try dies with no answer
    g.tick()
    g.tick()
    ok([c[3] for c in consults(g)] == ["rm-consult", "rm-consult"], "a retried round one stays round one: %s"
       % [c[3] for c in consults(g)])
    answer(g)
    g.tick()
    ok(g.st("I0")["help_options"]["vendor"] == "rm-consult", "round one's options name their agent")
    g.now += g.r["circling"]["help_cool_h"] * 3600
    circle(g)
    circle(g)
    g.tick()
    g.tick()
    two = consults(g)[-1]
    ok(len(consults(g)) == 3 and two[3] == R.VENDOR_AGENT, "round two goes to the second vendor: %s" % two[3])
    ok("OPTION: <idea> | <the one observation>" in two[2] and "help-answer" not in two[2],
       "its prompt asks for OPTION lines and names no command it cannot run")
    ok("--- failed approaches ---" in two[2] and "Why you were called" in two[2], "the cold record goes along")
    # the unit body, through a fake port: junk is refused and answers nothing
    pf = os.path.join(g.d, "p.md")
    with open(pf, "w") as f:
        f.write(two[2])
    nonce = g.st("I0")["help"]["nonce"]
    rc = R.help_vendor_run(g.s, "I0", pf, g.r, nonce=nonce, consult=lambda p, o, t: "I think the seam is wrong.")
    ok(rc == 3 and not g.st("I0")["help"].get("answered_at"), "an answer with no OPTION line answers nothing")
    wrongcalls = []
    expect_fence(lambda: R.help_vendor_run(g.s, "I0", pf, g.r, nonce="wrong", consult=lambda p, o, t: wrongcalls.append(t) or "OPTION: a | b"),
                 "a vendor answer under a wrong nonce")
    ok(wrongcalls == [], "a wrong nonce is fenced before any provider call")
    calls = []
    R.help_vendor_run(g.s, "I0", pf, dict(g.r, circling=dict(g.r["circling"], help_max_s=400)), nonce=nonce,
                      consult=lambda p, o, t: calls.append(t) or "")
    ok(len(calls) == R.VENDOR_FAST_TRIES and all(t <= 400 - R.VENDOR_RESERVE_S for t in calls),
       "empty fast answers are retried, each inside the unit's one bound: %s" % calls)
    said = "\n".join(["Here you go:", "OPTION: the cache key omits the tier | rerun with tier in key: red goes green",
                       "- **OPTION 2:** the guard runs at base | guard log shows base sha",
                       "OPTION:", "commentary | not an option", "OPTION: no observation here", "OPTION: x | y",
                       "OPTION: z | w"])
    rc = R.help_vendor_run(g.s, "I0", pf, g.r, nonce=nonce, consult=lambda p, o, t: said)
    got = g.st("I0")["help_options"]
    ok(rc == 0 and [o["idea"] for o in got["options"]] == ["the cache key omits the tier", "the guard runs at base", "x"],
       "OPTION lines become options, an untestable one is dropped, at most help_options_max: %s" % got["options"])
    ok(got["vendor"] == R.VENDOR_AGENT, "and they say which vendor gave them")
    spent = []
    expect_fence(lambda: R.help_vendor_run(g.s, "I0", pf, g.r, nonce=nonce, consult=lambda p, o, t: spent.append(t) or "OPTION: a | b"),
                 "an already-answered consult takes no new answer")
    ok(spent == [], "and a fenced vendor unit spends no provider call")
    g.w.up[g.st("I0")["help"]["run"]["unit"]] = False
    g.tick()
    ok(g.st("I0")["help"]["status"] == "answered", "round two closes like round one")
    ok("(a second vendor)" in workers(g)[-1][2] and "the cache key omits the tier" in workers(g)[-1][2],
       "the next brief carries round two's options and says whose")
    rows = [a for a in g.s.attempts("I0") if a.get("help") == "answered" and "options" in a]
    ok([a.get("agent") for a in rows] == ["rm-consult", R.VENDOR_AGENT] and [a.get("round") for a in rows] == [1, 2],
       "the record scores help by round and vendor: %s" % rows)
    g.done()
    r = dict(g.r, circling=dict(g.r["circling"], help_vendor_from_round=None))
    ok(R.help_vendor({"help": {"round": 5}}, r) == "rm-consult", "unset in the rules: every round is round one's agent")


def t_help_reaches_brief():
    """S2: the options reach the next worker's brief, and the consult itself is cold."""
    g = Rig(1, circling=HELP)
    g.run_one("I0")
    R.learn(g.s, "I0", g.st("I0")["gen"], "THE STORY THAT DROVE IT", now=g.now)
    circle(g, detail="evidence one")
    circle(g, detail="evidence two")
    g.tick()
    g.tick()
    p = consults(g)[0][2]
    ok("evidence one" in p and "evidence two" in p, "the consult reads the failed approaches")
    ok("THE STORY THAT DROVE IT" not in p, "and not learned.md")
    ok(g.st("I0")["contract"] is None and "text of I0" in p, "it reads the problem")
    answer(g, "I0", "swap the seam | seam log names X", "the fixture lies | rerun on clean tree")
    ok(g.st("I0")["help_options"]["options"][1]["observe"] == "rerun on clean tree", "the options are in the state file")
    n = len(workers(g))
    for _ in range(3):
        g.tick()
    ok(len(workers(g)) == n + 1, "the worker the consult held back starts")
    b = workers(g)[-1][2]
    ok("FRESH EYES" in b and "swap the seam" in b and "seam log names X" in b and "the fixture lies" in b,
       "the next brief carries each option and its test")
    ok("refute each" in b, "and what the worker owes for them")
    ok("relentless.py help --item I0" in workers(g)[0][2], "every brief names the call")
    g.done()


def t_help_refused():
    """S3, by the real command: no failed approach on record, no consult."""
    g = Rig(1, circling=HELP)
    g.run_one("I0")
    env = {k: v for k, v in os.environ.items() if k != "RELENTLESS_GEN"}
    env["RELENTLESS_ROOT"] = g.d
    tool = os.path.join(R.HERE, "relentless.py")
    def call(*a):
        return subprocess.run(["python3", tool, "help", "--item", "I0", *a], env=env, capture_output=True, text=True, timeout=60)
    res = call("--gen", str(g.st("I0")["gen"]), "stuck")
    ok(res.returncode == 2 and "no failed approach" in res.stderr, "refused, by name: %d %s" % (res.returncode, res.stderr[-120:]))
    ok(not g.st("I0").get("help"), "and nothing is wanted")
    g.tick()
    ok(not consults(g), "and the tick sends nobody")
    res = call("--gen", "99")
    ok(res.returncode == R.FENCED, "a stale worker is fenced, not refused: %d" % res.returncode)
    # a process that died tried nothing
    R.fail(g.s, g.st("I0"), "worker_lost", "unit gone", g.r, g.now)
    g.w.up[g.st("I0")["run"]["unit"]] = False
    g.run_one("I0")
    res = call()
    ok(res.returncode == 2 and "no failed approach" in res.stderr, "worker_lost is no failed approach: %s" % res.stderr[-120:])
    # with one on record the same call goes through, once
    R.snag(g.s, "I0", g.st("I0")["gen"], "dead_end", "tried the pump", g.r, now=g.now)
    g.w.up[g.st("I0")["run"]["unit"]] = False
    res = call()
    ok(res.returncode == 0 and g.st("I0")["help"]["by"] == "operator", "with one on record it goes: %s" % res.stderr[-120:])
    res = call()
    ok(res.returncode == 2 and "already has a consult" in res.stderr, "a second while one is out is refused")
    g.tick()
    ok(len(consults(g)) == 1, "one consult")
    g.done()


def t_help_lifecycle():
    g = Rig(1, circling=HELP)
    circle(g)
    circle(g)
    g.tick()
    g.tick()
    nonce = g.st("I0")["help"]["nonce"]
    for bad in ([], ["no test here"], ["a | b"] * 4):
        expect = False
        try:
            R.help_answer(g.s, "I0", nonce, bad, g.r, now=g.now)
        except ValueError:
            expect = True
        ok(expect, "a malformed answer is refused: %s" % (bad,))
    expect_fence(lambda: R.help_answer(g.s, "I0", "wrong", ["a | b"], g.r, now=g.now), "a wrong nonce")
    # dies with no answer: another try, then the item carries on without
    for n in range(1, g.r["circling"]["help_launch_tries"] + 1):
        g.w.up[g.st("I0")["help"]["run"]["unit"]] = False
        ok(len(consults(g)) == n, "try %d launched: %d" % (n, len(consults(g))))
        g.tick()
        if n < g.r["circling"]["help_launch_tries"]:
            ok(g.st("I0")["status"] == "queued", "the worker waits for the retry")
            g.tick()
    ok(g.st("I0")["help"]["status"] == "failed", "three dead consults: failed")
    ok(any("consult" in x for x in g.w.notes), "said on the item")
    g.tick()
    ok(g.st("I0")["status"] == "running", "and a dead consult does not hold the worker for good")
    ok(not g.st("I0").get("help_options") and "FRESH EYES" not in workers(g)[-1][2], "no options, no paragraph")
    g.done()
    # overrun: stopped, the nonce fenced before the stop
    g = Rig(1, circling=HELP)
    circle(g)
    circle(g)
    g.tick()
    g.tick()
    h = g.st("I0")["help"]
    g.now += g.r["circling"]["help_max_s"]
    g.tick()
    ok(h["run"]["unit"] in [u for u, _ in g.w.stops], "an overrun consult is stopped")
    expect_fence(lambda: R.help_answer(g.s, "I0", h["nonce"], ["a | b"], g.r, now=g.now), "a late answer")
    g.done()
    # no room: bounded
    g = Rig(1, circling=HELP)
    circle(g)
    circle(g)
    g.w.refuse = True
    g.tick()
    ok(g.st("I0")["help"]["status"] == "wanted" and g.st("I0")["status"] == "queued", "a full pool waits, the item keeps its place")
    g.w.refuse = False
    g.w.help_checkout = lambda st, sha: (None, "x POOL REFUSED y")
    g.now += g.r["circling"]["help_wait_s"]
    g.tick()
    ok(g.st("I0")["help"]["status"] == "failed", "the wait is bounded")
    g.tick()
    ok(g.st("I0")["status"] == "running", "and the worker goes")
    g.done()
    # the item ends under a running consult
    g = Rig(1, circling=HELP)
    circle(g)
    circle(g)
    g.tick()
    g.tick()
    u = g.st("I0")["help"]["run"]["unit"]
    with g.s.lock():
        st = g.st("I0")
        st["status"] = "retired"
        g.s.save(st)
    g.tick()
    g.tick()
    ok(g.st("I0")["help"]["status"] == "dropped" and not g.w.up[u], "an ended item takes its consult down")
    g.done()
    # the pool sees the clone
    g = Rig(1, circling=HELP)
    g.w.pool = {"/c/other": {"busy": True}}
    g.w.pool_max = 10
    circle(g)
    circle(g)
    g.tick()
    g.tick()
    c = g.st("I0")["help"]["clone"]
    row = [x for x in R.pool_rows(g.s, g.w, g.r) if x["clone"] == c][0]
    ok(row["kind"] == "help" and row["rank"] == 2, "a running consult's clone is live: %s" % row)
    answer(g)
    g.tick()
    ok(c not in g.w.pool, "and an answered consult gives it back")
    ok(R.clone_item("/x/help-AB_C-c2") == "AB_C", "help clones read back")
    g.done()


def t_review_findings_core():
    """Five findings of the first full review of relentless.py, each by its failing sequence."""
    # the fence: a marker there but unreadable fails closed; absent still says nothing
    x = Rig(n=1, share=1.0, max_workers=1)
    x.run_one("I0")
    gitd = os.path.join(x.d, "cl", ".git")
    os.makedirs(gitd)
    for torn in ("", '{"item": "I0"', '{"gen": 1}', '{"item": "I0", "gen": "x"}', "[]"):
        with open(os.path.join(gitd, "relentless.json"), "w") as f:
            f.write(torn)
        ok(R.hook_fence(os.path.join(x.d, "cl"), x.s), "a torn marker refuses the push: %r" % torn)
    os.remove(os.path.join(gitd, "relentless.json"))
    ok(R.hook_fence(os.path.join(x.d, "cl"), x.s) is None, "no marker still says nothing")
    x.done()
    # the ignored symlink: dangling, its target string is what would be lost
    d = tempfile.mkdtemp(prefix="rlsym-")
    def g(*a):
        subprocess.run(("git", "-C", d) + a, check=True, capture_output=True,
                       env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t"))
    g("init", "-q", "-b", "main")
    with open(os.path.join(d, ".gitignore"), "w") as f:
        f.write("local.cfg\n")
    g("add", ".gitignore")
    g("commit", "-qm", "a")
    base = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    with open(os.path.join(d, "local.cfg"), "w") as f:
        f.write("origin\n")
    g("add", "-f", "local.cfg")
    g("commit", "-qm", "b")
    tip = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    g("update-ref", "refs/remotes/origin/main", tip)
    g("reset", "-q", "--soft", base)
    g("reset", "-q")
    os.remove(os.path.join(d, "local.cfg"))
    os.symlink("/nowhere/at/all", os.path.join(d, "local.cfg"))
    fx = R.Effects.__new__(R.Effects)
    fx.books = d
    ok("local.cfg" in (fx.ignored_collision() or ""), "a dangling ignored symlink is a collision")
    os.remove(os.path.join(d, "local.cfg"))
    with open(os.path.join(d, "local.cfg"), "w") as f:
        f.write("origin\n")
    ok(fx.ignored_collision() is None, "same bytes in a plain file is none")
    os.remove(os.path.join(d, "local.cfg"))
    os.symlink("origin\n", os.path.join(d, "local.cfg"))
    ok("local.cfg" in (fx.ignored_collision() or ""), "a link whose target equals the file's bytes still is one")
    shutil.rmtree(d, ignore_errors=True)
    # reenrol keeps what is still live and the consult count
    x = Rig(n=1)
    with x.s.lock():
        st = R.new_state("Z", x.now, "t")
        st.update(status="retired", help_count=3, help={"status": "stopping", "run": {"unit": "h", "charged": None}})
        x.s.save(st)
    try:
        R.reenrol(x.s, "Z", "wrong", x.now)
        ok(False, "reenrol must refuse while a consult is unsettled")
    except ValueError as e:
        ok("help" in str(e), "reenrol waits for a live consult: %s" % e)
    with x.s.lock():
        st = x.s.load("Z")
        st["help"]["run"]["charged"] = 5
        x.s.save(st)
    ok(R.reenrol(x.s, "Z", "wrong", x.now)["help_count"] == 3, "and the consult count stays, so its path is never reused")
    x.done()
    # a running consult takes a place at check admission too
    x = Rig(n=3, share=1.0, max_workers=1, staffing=None)
    for i in ("A", "B"):
        with x.s.lock():
            st = R.new_state(i, x.now, "t")
            x.w.items[i] = "doing"
            st.update(status="candidate", gen=1, ledger_started=True, candidate={"sha": "s", "at": x.now - 10, "evidence": "e"},
                      contract={"proof": "p"}, base="b")
            x.s.save(st)
    with x.s.lock():
        st = x.s.load("A")
        st["help"] = {"status": "running", "run": {"unit": "h", "charged": None}, "at": x.now, "tries": 1}
        x.s.save(st)
    acts = []
    for i in ("A", "B"):
        R.step(x.s, x.w, x.r, i, x.now, acts)
    running = sum(1 for i in ("A", "B") if x.st(i)["status"] == "checking")
    ok(running == 1, "cap 1 plus one check, one consult running: one checker, not two: %d %s" % (running, acts))
    x.done()
    # a quarantined checker keeps its clone until the reaper
    x = Rig(n=1)
    x.w.pool = {"/c/check-Q-c1": {}, "/c/Q.0": {}}
    st = R.new_state("Q", x.now, "t")
    st.update(status="closing", clone="/c/Q.0", check={"clone": "/c/check-Q-c1"},
              quarantined=[{"clone": "/c/check-Q-c1", "run": {"unit": "u"}, "reaped": False}])
    x.s.save(st)
    R.finished(x.s, x.w, "Q", {"sha": "s"}, x.now, [])
    ok("/c/check-Q-c1" in x.w.pool and "/c/Q.0" not in x.w.pool, "completion leaves a quarantined checker's clone")
    st = x.s.load("Q")
    st["quarantined"][0]["reaped"] = True
    x.s.save(st)
    R.remove_check_clone(x.w, x.s.load("Q"))
    ok("/c/check-Q-c1" not in x.w.pool, "reaped, it may go")
    x.done()


def t_weak_is_not_good():
    ok("proof_weak" in R.REJECT_ENDS, "the reading counts WEAK as a rejection, not a pass")
    for m in (R, R.relentless_wall):
        src = open(m.__file__, encoding="utf-8").read().replace("the work holds and only the proof is short", "")
        ok("work holds" not in src, "%s: no WEAK text calls the work good" % m.__name__)


def t_live_line_widens():
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    with R.Store.lock(x.s):
        st = x.st("I0")
        st["contract"] = {"proof": "p", "live": None, "by_gen": 1, "why": None}
        x.s.save(st)
    g = st["gen"]
    for live, proof, why in (("once: x", "q", "w"),):
        try:
            R.contract(x.s, "I0", g, proof, live, why, now=x.now)
            ok(False, "a build worker may not change the proof")
        except ValueError:
            pass
    try:
        R.contract(x.s, "I0", g, "p", None, "w", now=x.now)
        ok(False, "nor rewrite it with no live line")
    except ValueError:
        pass
    try:
        R.contract(x.s, "I0", g, "p", "once: x", None, now=x.now)
        ok(False, "the widening says why")
    except ValueError:
        pass
    R.contract(x.s, "I0", g, "p", "once: x", "the hook needs it", now=x.now)
    ok(x.st("I0")["contract"]["live"] == "once: x", "any worker adds a missing live line, proof unchanged")
    try:
        R.contract(x.s, "I0", g, "p", "once: y", "w", now=x.now)
        ok(False, "a live line once set is frozen")
    except ValueError:
        pass


def t_time_is_no_failed_approach():
    x = Rig(n=1, share=1.0, snag_again_wait_h=1)
    for i in range(4):
        x.run_one("I0")
        st = x.st("I0")
        R.snag(x.s, "I0", st["gen"], "sample_thin", "time", x.r, now=x.now, wait_hours=0.5)
        x.w.up[st["run"]["unit"]] = False
        got = x.st("I0")
        ok(got["approach"] == "build", "a time wait is no failed approach (%d)" % i)
        ok(got["not_before"] == x.now + max(0.5, i) * 3600, "the same class waits longer each time (%d)" % i)
        x.tick(max(0.5, i) * 3600 + 1)
        x.tick(240)
    x = Rig(n=1, share=1.0, snag_again_wait_h=1)
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "thin", "first", x.r, now=x.now)
    ok(x.st("I0")["not_before"] == x.now, "a first snag with no wait named waits nothing")
    x.w.up[st["run"]["unit"]] = False
    x.tick(240)
    x.tick(240)
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "thin", "second", x.r, now=x.now)
    ok(x.st("I0")["not_before"] == x.now + 3600, "the same class again waits though no wait was named")


def t_one_builder_per_mod():
    x = Rig(n=3, share=1.0, max_workers=3, staffing=None)
    x.r["one_builder_per_mod"] = True
    m = {"I0": ["RimMandrake/Abyss"], "I1": ["RimMandrake/Abyss", "RimUtinni/Rites"], "I2": ["RimUtinni/Other"]}
    x.w.item_mods = lambda st: m[st["item"]]
    for i in range(6):
        x.tick(60)
    run = {i for i in m if x.st(i) and x.st(i)["status"] in R.HOLDS_A_PLACE}
    ok(run == {"I0", "I2"}, "one mod, one builder; another mod still starts: %s" % sorted(run))
    x.r["one_builder_per_mod"] = False
    x.tick(60)
    ok(x.st("I1") and x.st("I1")["status"] in R.HOLDS_A_PLACE, "the rule is the only thing that kept it out")


def t_parked_items_hold_no_place():
    """The 2026-11 deadlock: a line full of same-mod items behind one builder enrolled nothing for hours."""
    x = Rig(n=8, share=1.0, max_workers=4, staffing=None)
    x.r["one_builder_per_mod"] = True
    x.r["max_queued"] = 3
    x.w.item_mods = lambda st: ["RimMandrake/Abyss"] if st["item"] in ("I0", "I1", "I2", "I3") else ["RimUtinni/" + st["item"]]
    for i in range(10):
        x.tick(60)
    others = [i for i in ("I4", "I5", "I6", "I7") if x.st(i) is not None]
    ok(len(others) >= 2, "ready work on other mods is enrolled past a line of parked same-mod items: %s" % others)
    ok(any(x.st(i)["status"] in R.HOLDS_A_PLACE for i in others), "and one of them starts")
    x.done()


def t_enrol_skips_taken_mod():
    """Pool order puts one mod first: enrol must walk past its items to others instead of filling the line with them."""
    x = Rig(n=8, share=1.0, max_workers=4, staffing=None)
    x.r["one_builder_per_mod"] = True
    x.r["max_queued"] = 8
    x.w.item_mods = lambda st: ["RimMandrake/Abyss"] if st["item"] in ("I0", "I1", "I2", "I3") else ["RimUtinni/" + st["item"]]
    for i in range(6):
        x.tick(60)
    abyss = [i for i in ("I0", "I1", "I2", "I3") if x.st(i) is not None]
    others = [i for i in ("I4", "I5", "I6", "I7") if x.st(i) is not None]
    ok(len(abyss) == 1 and len(others) == 4, "one Abyss item, the rest enrolled from other mods: %s %s" % (abyss, others))
    x.done()


def _abyss_line(n=8, abyss=("I0", "I1", "I2", "I3"), **rules):
    x = Rig(n=n, max_workers=4, staffing=None, **{"share": 1.0, **rules})
    x.r["one_builder_per_mod"] = True
    x.w.item_mods = lambda st: ["RimMandrake/Abyss"] if st["item"] in abyss else ["RimUtinni/" + st["item"]]
    return x


def t_line_full_of_one_mod_still_leases_another():
    """The line is ALREADY full of one mod (enrolled by hand, or back from a stop), so walking past taken mods in enrol
    cannot help: only parked items holding no max_queued place lets another mod in."""
    x = _abyss_line(max_queued=3)
    for i in ("I0", "I1", "I2", "I3"):
        R.enrol_one(x.s, i, "seeded", x.now)
    x.tick(60)
    ok(x.st("I0")["status"] in R.HOLDS_A_PLACE, "one builder on the mod")
    ok(all(x.st(i)["status"] == "queued" for i in ("I1", "I2", "I3")), "the other three wait their turn in the line")
    for _ in range(4):
        x.tick(60)
    others = [i for i in ("I4", "I5", "I6", "I7") if x.st(i) is not None]
    ok(others, "a different mod is enrolled past a full line of that mod: %s" % others)
    ok(any(x.st(i)["status"] in R.HOLDS_A_PLACE for i in others), "and leased")
    ok(all(x.st(i)["status"] == "queued" for i in ("I1", "I2", "I3")), "the same-mod line kept its places, unstarted")
    x.done()


def t_waiting_items_hold_no_line_place():
    """Same clog, other cause: items sitting out a wait cannot start, and a wait on one item does not shut its mod."""
    x = _abyss_line(abyss=("I0", "I1"), max_queued=2)
    for i in ("I0", "I2"):
        R.enrol_one(x.s, i, "seeded", x.now)
        st = x.st(i)
        st["not_before"] = x.now + 3600
        x.s.save(st)
    x.tick(60)
    ok(x.st("I1") is not None and x.st("I1")["status"] in R.HOLDS_A_PLACE,
       "the waiting I0 does not shut its mod to I1, which starts: %s" % (x.st("I1") or {}).get("status"))
    ok(all(x.st(i)["status"] == "queued" for i in ("I0", "I2")), "the two waiting items did not start")
    ok(any(x.st(i) is not None for i in ("I3", "I4", "I5", "I6", "I7")), "two waits filling max_queued clog nothing")
    x.done()


def t_parked_system_items_hold_no_sys_room():
    """A system item behind a held mod holds no system place: another system item on another mod still enrols, even with
    the share spent (room <= 0, so sys_room alone decides)."""
    x = _abyss_line(abyss=("I0", "I1", "I2"), share=0.25, max_queued=2)
    x.w.first = {"I0": 0, "I1": 1, "I2": 2, "I3": 3}
    for i in ("I0", "I1", "I2"):
        R.enrol_one(x.s, i, "seeded", x.now)
    x.tick(60)
    ok(x.st("I0")["status"] in R.HOLDS_A_PLACE, "the first system item builds")
    x.tick(60)
    ok(x.st("I3") is not None, "the system item on another mod enrols past its parked fellows")
    x.done()


def _line_of_two(mark):
    """I0 (the Abyss) and I2 (another mod) fill max_queued 2, each marked by `mark`; I1 is also the Abyss. -> what enrol took."""
    x = _abyss_line(abyss=("I0", "I1"), max_queued=2)
    for i in ("I0", "I2"):
        R.enrol_one(x.s, i, "seeded", x.now)
        st = x.st(i)
        mark(st, x.now)
        x.s.save(st)
    took = R.enrol(x.s, x.w, x.r, x.now)
    x.done()
    return took


def t_plain_queued_items_hold_their_places():
    """The control for every parked clause: an item that CAN start still holds its place, or max_queued means nothing."""
    ok(_line_of_two(lambda st, now: None) == [], "a line of two startable items at max_queued 2 enrols nothing")


def t_consulting_item_holds_no_line_place():
    """Its next brief is the consult's answer, so lease() walks past it: while one is out it holds no place, then it does."""
    for word in ("wanted", "running"):
        def mark(st, now, word=word):
            st["help"] = {"status": word}
        took = _line_of_two(mark)
        ok(len(took) == 2 and "I1" in took, "consult %s: two others enrol, I1 of the same mod among them: %s" % (word, took))
    def over(st, now):
        st["help"] = {"status": "answered"}
    ok(_line_of_two(over) == [], "a consult that answered: the item can start and holds its place again")


def t_refused_start_holds_no_line_place():
    """The filed case's second cause (EGROWTH start_refused): cooling after a refused start holds no place; cooled, it does."""
    def cooling(st, now):
        st["start_again_at"] = now + 3600
    took = _line_of_two(cooling)
    ok(len(took) == 2 and "I1" in took, "start refused and cooling: two others enrol, I1 of the same mod among them: %s" % took)
    def cooled(st, now):
        st["start_again_at"] = now - 1
    ok(_line_of_two(cooled) == [], "the cool over: it can start and holds its place again")


def t_incident_line_fills_every_place():
    """The filed numbers, the line brim-full: max_queued 8 and four places; one FlowWorks and one EGROWTH run, eight wait
    behind them (seven and one). Every place must fill from other mods and the eight stay in line, unstarted."""
    flow = ["I%d" % i for i in range(8)]
    egrowth = ["I8", "I9"]
    others = ["I%d" % i for i in range(10, 16)]
    x = Rig(n=16, share=1.0, max_workers=4, staffing=None, max_queued=8)
    x.r["one_builder_per_mod"] = True
    x.w.item_mods = lambda st: (["RimMandrake/FlowWorks"] if st["item"] in flow else
                                ["RimMandrake/EGrowth"] if st["item"] in egrowth else ["RimUtinni/" + st["item"]])
    for i in flow + egrowth:
        R.enrol_one(x.s, i, "seeded", x.now)
    for _ in range(6):
        x.tick(60)
    places = lambda ids: [i for i in ids if x.st(i) and x.st(i)["status"] in R.HOLDS_A_PLACE]
    got = (len(places(flow)), len(places(egrowth)), len(places(others)))
    ok(got == (1, 1, 2), "all four places filled, one builder per held mod, two from other mods: %s" % (got,))
    ok(sum(1 for i in flow + egrowth if x.st(i)["status"] == "queued") == 8, "the eight behind the held mods keep their places")
    x.done()


def t_enrol_reads_store_once_per_line():
    """parked() gets the states enrol already read: the line's length must not multiply store reads (the file read per item
    per tick that a long line pays)."""
    def reads(n):
        x = _abyss_line(n=12, abyss=tuple("I%d" % i for i in range(n)), max_queued=50)
        for i in range(n):
            R.enrol_one(x.s, "I%d" % i, "seeded", x.now)
        count = [0]
        real = x.s.states
        def states():
            count[0] += 1
            return real()
        x.s.states = states
        R.enrol(x.s, x.w, x.r, x.now)
        x.done()
        return count[0]
    a, b = reads(2), reads(8)
    ok(a == b, "store reads in one enrol do not grow with the line: %d for 2 queued, %d for 8" % (a, b))


def t_item_mods_real():
    import tempfile
    b = tempfile.mkdtemp()
    for p in ("RimMandrake/Abyss", "RimMandrake/RustCathedral", "RimUtinni/Rites"):
        os.makedirs(os.path.join(b, "src", p, "About"))
        open(os.path.join(b, "src", p, "About", "About.xml"), "w").close()
    os.makedirs(os.path.join(b, "src", "RimMandrake", "Utils"))
    os.makedirs(os.path.join(b, "infrastructure", "state", "items"))
    with open(os.path.join(b, "infrastructure", "state", "items", "RUST_CATHEDRAL_X.md"), "w") as f:
        f.write("see src/RimUtinni/Rites/Defs/a.xml and src/RimMandrake/Utils/b.py")
    fx = R.Effects.__new__(R.Effects)
    fx.books = b
    class It:
        title = "fix the abyss floor"
    fx.ledger_items = lambda: (None, type("W", (), {"items": {"RUST_CATHEDRAL_X": It}}))
    got = fx.item_mods({"item": "RUST_CATHEDRAL_X", "last_sha": None})
    ok(got == ["RimMandrake/Abyss", "RimMandrake/RustCathedral", "RimUtinni/Rites"], "real: mods from id, title and prose paths: %s" % got)


def t_review_findings_rig():
    a, b = FakeWorld(0), FakeWorld(0)
    a.pool["/c/L0"] = {"busy": True}
    ok(b.pool_load()[0] == 0, "worlds share no clone pool")
    w = FakeWorld(0)
    w.pool = {"/c/L%d" % i: {} for i in range(9)}
    c, _ = w.clean_checkout({"item": "I0"}, "s")
    ok(c in w.pool, "the checkout returns the path it records")
    w.remove_clone({"clone": c})
    ok(len(w.pool) == 9, "so it can be removed")
    d, _ = w.clean_checkout({"item": "I0", "check_count": 1}, "s")
    ok(c != d, "and two checks of an item are two clones")


def t_review_wrong_verdicts():
    """GPT review of the verdict machinery: each row is red without its fix."""
    # a moving ref is no candidate
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    for bad in ("origin/main", "HEAD", "main", "abc~1", "a..b", "a b", "-x"):
        try:
            R.finish(x.s, "I0", st["gen"], bad, "e")
            ok(False, "finish refuses %r" % bad)
        except ValueError:
            ok(True, "finish refuses %r" % bad)
    x.done()
    # contract prose does not authorize a production edit for a proof-only worker
    class FxC:
        def changed(self, b, s, i): return ["src/runtime.py"]
    st = {"item": "I", "proof_only": {"sha": "A"}, "contract": {"proof": "run t", "why": "leave src/runtime.py unchanged"}}
    k, _ = R.proof_gate(FxC(), RULES, st, {"sha": "B"})
    ok(k == "proof_rework", "a path named only in the why prose is still rework")
    st["contract"]["proof"] = "python3 src/runtime.py"
    k, _ = R.proof_gate(FxC(), RULES, st, {"sha": "B"})
    ok(k is None, "a path the proof command names is the proof")
    # an unreadable spend record blocks, never reads as an empty day
    x = Rig(n=1, share=1.0)
    ok(R.spent_today(x.s, x.now) == 0, "no day file is a new day")
    with open(x.s.p("spend-%s.json" % R.day_key(x.now)), "w") as f:
        f.write('{"spent": 5, "ru')
    ok(R.spent_today(x.s, x.now) >= R.UNREADABLE_SPEND, "a truncated day file blocks spending")
    R.charge(x.s, {"spent": 0}, 7, x.now, RULES, "u1")
    with open(x.s.p("spend-%s.json" % R.day_key(x.now))) as f:
        ok(f.read() == '{"spent": 5, "ru', "and is not overwritten by a partial history")
    x.done()
    # the pause that cannot be read is a pause
    sys.modules["dispatcher"] = types.SimpleNamespace(paused_now=lambda: 1 / 0)
    try:
        ok(R.Effects.paused(None) is True, "an unreadable pause gate holds the launch")
    finally:
        del sys.modules["dispatcher"]
    # a refusal survives the cut
    out = "w" * 650 + " I0 has not earned its close"
    ok("has not earned its close" in R.close_why(out) and len(R.close_why(out)) <= 700, "the refusal words survive the cut")
    ok(R.close_why("x" * 900) == "x" * 400, "other output keeps its tail")
    # an origin that cannot be asked is a wait, not a verdict on the candidate
    x = Rig(n=1, share=1.0)
    x.w.is_pub = None
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p")
    R.finish(x.s, "I0", st["gen"], "sha1", "e")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "candidate" and not st["failures"], "published()=None waits: no bad_candidate")
    x.w.is_pub = True
    x.tick()
    ok(x.st("I0")["status"] in ("checking", "candidate"), "and proceeds once origin answers")
    x.done()
    # a close retry asks again whether the sha is still on origin
    x = Rig(n=1, share=1.0)
    tries = []
    x.w.ledger_close = lambda item, sha, reason, live=None: tries.append(sha) or "git hiccup"     # fails every time
    full_pass(x, "I0")
    ok(x.st("I0")["status"] == "closing" and x.w.closes == [] and tries, "the close failed and the item waits in closing")
    x.w.is_pub = None
    n_tries = len(tries)
    x.tick()
    ok(not x.st("I0")["failures"] and len(tries) == n_tries and x.st("I0")["status"] == "closing",
       "unknown publication while closing waits: no failure, no close attempt")
    x.w.is_pub = False
    x.tick()
    ok(x.st("I0")["failures"].get("live_broken") == 1 and x.w.closes == [] and len(tries) == n_tries,
       "a retry does not even try to close a sha that left origin")
    x.done()
    # the pause that arrives while the clone is prepared stops the launch
    x = Rig(n=1, share=1.0)
    def prep(st):
        x.w.pause = True
    x.w.prepare = prep
    for _ in range(4):
        x.tick()
    ok(not x.w.launches, "a pause set during prepare launches nothing")
    x.done()


def t_review_wrong_verdicts_two():
    """Round 2 of the GPT review of relentless.py."""
    # a ref the worker names is pinned to its commit id
    d = tempfile.mkdtemp(prefix="rl-git-")
    def g(*a): return subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True, check=True).stdout.strip()
    g("init", "-q"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
    open(os.path.join(d, "f"), "w").write("1"); g("add", "f"); g("commit", "-qm", "a")
    a = g("rev-parse", "HEAD"); g("branch", "origin")
    cwd = os.getcwd()
    os.chdir(d)
    try:
        ok(R.canonical_commit("origin") == a, "a moving ref name resolves to the full commit id")
        for bad in ("nosuchref", "origin;ls"):
            try:
                R.canonical_commit(bad); ok(False, "refuses %r" % bad)
            except ValueError:
                ok(True, "refuses %r" % bad)
    finally:
        os.chdir(cwd)
        shutil.rmtree(d, ignore_errors=True)
    # the proof gate matches whole path tokens, not substrings
    class FxC:
        def changed(self, b, s, i): return ["engine.py"]
    st = {"item": "I", "proof_only": {"sha": "A"}, "contract": {"proof": "python selftest_engine.py"}}
    k, _ = R.proof_gate(FxC(), RULES, st, {"sha": "B"})
    ok(k == "proof_rework", "engine.py is not named by 'selftest_engine.py'")
    # yesterday's damaged record, or a day record of the wrong shape, blocks spending
    x = Rig(n=1, share=1.0)
    with open(x.s.p("spend-%s.json" % R.day_key(x.now - 86400)), "w") as f:
        f.write("{bad")
    ok(R.spent_today(x.s, x.now) >= R.UNREADABLE_SPEND, "a damaged yesterday blocks today")
    os.unlink(x.s.p("spend-%s.json" % R.day_key(x.now - 86400)))
    with open(x.s.p("spend-%s.json" % R.day_key(x.now)), "w") as f:
        f.write("{}")
    ok(R.spent_today(x.s, x.now) >= R.UNREADABLE_SPEND, "an empty object is not an empty day")
    x.done()
    # a record with a bool or negative charge understates the day: blocked
    x = Rig(n=1, share=1.0)
    for bad in ('{"spent": false, "runs": {"u": 1200000}}', '{"spent": -5, "runs": {}}', '{"spent": 3, "runs": {"u": "9"}}'):
        with open(x.s.p("spend-%s.json" % R.day_key(x.now)), "w") as f:
            f.write(bad)
        ok(R.spent_today(x.s, x.now) >= R.UNREADABLE_SPEND, "damaged spend record blocks: %s" % bad)
    x.done()
    # a nonfinite wait is refused, not a wait that never comes due
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    for bad in (float("nan"), float("inf"), -1.0):
        try:
            R.snag(x.s, "I0", x.st("I0")["gen"], "k", "t", x.r, wait_hours=bad)
            ok(False, "snag refuses wait %r" % bad)
        except ValueError:
            ok(True, "snag refuses wait %r" % bad)
    x.done()
    # a git failure is not "absent from origin"
    class G(R.Effects):
        def __init__(self, rcs): self.rcs, self.books = rcs, "b"
        def git(self, d, *a):
            return types.SimpleNamespace(returncode=self.rcs[a[0]], stdout="", stderr="")
    ok(G({"fetch": 0, "merge-base": 1}).published("s") is False, "exit 1 is not an ancestor")
    ok(G({"fetch": 0, "merge-base": 128}).published("s") is None, "exit 128 is unknown")
    ok(G({"fetch": 1, "merge-base": 0}).published("s") is None, "a failed fetch is unknown")
    ok(G({"fetch": 0, "merge-base": 0}).published("s") is True, "exit 0 is published")
    # a verdict is single-assignment
    x = Rig(n=1, share=1.0)
    x.w.close_fail = None
    full_pass(x, "I0", "FAIL")
    st = x.st("I0")
    ok(st["failures"].get("blind_fail") == 1, "FAIL recorded")
    x.done()
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p", live="once: t")
    R.finish(x.s, "I0", st["gen"], "sha1", "e")
    x.w.up[st["run"]["unit"]] = False
    x.tick(); x.tick()
    chk = x.st("I0")["check"]
    R.verdict(x.s, "I0", chk["nonce"], "PASS", "ok")
    try:
        R.verdict(x.s, "I0", chk["nonce"], "FAIL", "changed my mind")
        ok(False, "a second verdict is refused")
    except R.Fenced:
        ok(True, "a second verdict is refused")
    ok(x.st("I0")["check"]["verdict"] == "PASS", "and the refused write left the first word standing")
    x.done()
    # a process list that cannot be read is not a death
    class Rl:
        ACTIVE = ("active",)
        def unit_state(self, u): return "inactive"
        def scan_marked(self, *a, **k): raise OSError("ps failed")
    fx = types.SimpleNamespace(RL=Rl())
    ok(R.Effects.alive(fx, {"unit": "u", "scope": None, "marker": "m", "at": 0}) is True, "a failed process scan keeps the run owned")
    # a crash inside the first close attempt is already a retry
    x = Rig(n=1, share=1.0)
    def boom(item, sha, reason, live=None): raise RuntimeError("killed mid-close")
    x.w.ledger_close = boom
    try:
        full_pass(x, "I0")
    except RuntimeError:
        pass
    x.w.is_pub = False
    x.w.ledger_close = lambda item, sha, reason, live=None: x.w.closes.append((item, sha))
    x.tick()
    ok(x.w.closes == [] and x.st("I0")["failures"].get("live_broken") == 1, "the attempt after a crash re-asks publication")
    x.done()
    # a pause that arrives while a checker's clone is made stops the launch
    x = Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p", live="once: t")
    R.finish(x.s, "I0", st["gen"], "sha1", "e")
    x.w.up[st["run"]["unit"]] = False
    cc = x.w.clean_checkout
    def pausing(st_, sha):
        x.w.pause = True
        return cc(st_, sha)
    x.w.clean_checkout = pausing
    n0 = len(x.w.launches)
    x.tick(); x.tick()
    ok(len(x.w.launches) == n0 and x.st("I0")["status"] == "candidate", "a pause set during the checker's clone launches no checker")
    x.done()


def t_hold_routing():
    """RELENTLESS_HOLD_FIX_TOOLING_ISNT_OWNERS: only owner_call and a flyer's flight are his; a legacy supervisor-set
    needs=owner goes back, a person's does not."""
    flyer = "game phase: flyer: a flyer's flight is never live-tested without the owner present"
    for h, his in (({"kind": "owner_call", "why": "x"}, True), ({"kind": "game", "why": flyer}, True),
                   ({"kind": "proof_weak", "why": "x"}, False), ({"kind": "strikes", "why": "x"}, False),
                   ({"kind": "spend", "why": "x"}, False), ({"kind": "game", "why": "game phase: refused again"}, False),
                   ({"kind": "proof_weak", "why": "a flyer: in the words"}, False), (None, False)):
        ok(R.hold_is_his(h) is his, "hold_is_his %s -> %s" % (h, his))
    ok(R.put_down_on({"status": "held", "hold": {"kind": "strikes", "why": "w"}}) == "seat: w", "put down on the seat")
    ok(R.put_down_on({"status": "held", "hold": {"kind": "owner_call", "why": "w"}}) == "owner: w", "put down on him")

    class It:
        def __init__(self, needs, state, history, owed=()):
            self.needs, self.state, self.history, self.owed = needs, state, history, owed

        def owed_levels(self):
            return list(self.owed)

    class W:
        items = {}

    class Fx(R.Effects):
        def __init__(self, evs, it):
            self.evs0, self.calls, self.fail = evs, [], None
            W.items = {"I": it}

        def ledger_items(self):
            return self.evs0, W()

        def ledger_needs(self, item, to, why):
            self.calls.append(("needs", to))
            return self.fail

        def ledger_note(self, item, text):
            self.calls.append(("note", text))
            return self.fail

        def conductor_attention(self, text):
            self.calls.append(("told", text))

    # The words on the legacy events already in the ledger, spelt out: a fixture built from R.SUPERVISOR_WHY moves with
    # the constant and would stay green while no real legacy hold is restored (blind check, gap 2).
    ok(R.SUPERVISOR_WHY == "relentless supervisor", "the provenance is still what the legacy events say")
    ours = [{"event": "needs", "to": "owner", "why": "relentless supervisor"}]
    his = [{"event": "needs", "to": "owner", "why": "an L4 look"}]
    hold = {"kind": "proof_weak", "why": "weak", "delivered": False}
    fx = Fx(ours, It("owner", "doing", [0]))
    ok(fx.ledger_hold_to_seat("I", hold) is None, "a fresh hold lands")
    ok(fx.calls[0] == ("needs", "offline") and [c[0] for c in fx.calls[1:]] == ["note", "told"],
       "the supervisor's own routing goes back, then the seat is told: %s" % fx.calls)
    fx = Fx(ours, It("owner", "built", [0], ["L2"]))
    fx.ledger_hold_to_seat("I", dict(hold, delivered=True))
    ok(fx.calls == [("needs", "bridge")], "a delivered legacy hold: a built item's needs comes back derived, said once: %s" % fx.calls)
    fx = Fx(his, It("owner", "doing", [0]))
    fx.ledger_hold_to_seat("I", hold)
    ok(not any(c[0] == "needs" for c in fx.calls), "a person's needs=owner is not ours to move: %s" % fx.calls)
    # filed_needs alone keeps a person's `needs --to owner`; this is the case only _owner_routing_is_ours can tell
    fx = Fx(ours + [{"event": "block", "kind": "owner"}], It("owner", "doing", [0, 1]))
    fx.ledger_hold_to_seat("I", hold)
    ok(not any(c[0] == "needs" for c in fx.calls), "blocked on him after our old routing: the block is his, not ours to move: %s" % fx.calls)
    fx = Fx([], It("bridge", "built", [], ["L2"]))
    fx.ledger_hold_to_seat("I", hold)
    ok(not any(c[0] == "needs" for c in fx.calls), "a hold writes no needs on an item not routed to him: %s" % fx.calls)
    fx = Fx(ours, It("owner", "doing", [0]))
    fx.fail = "ledger down"
    ok(fx.ledger_hold_to_seat("I", hold) == "ledger down", "a failure says so and the tick retries")

    # The two readers of a hold cannot disagree: Fleet Watch's owner_queue and this supervisor's routing. Both sides of the
    # word trap are pinned on real wrapped text (blind check: a bare "flyer" in a why made a hold that was nobody's).
    sys.path.insert(0, os.path.join(os.path.dirname(R.HERE), "Utils"))
    import owner_queue as Q
    import relentless_live as L
    site = L.refused_site("python.exe src/RimMandrake/bridgetools/prove_venomvine_flyer.py")
    ok(site and "flyer" in site, "a real refusal names a flyer path: %s" % site)
    again = "game phase: refused again unchanged after a return (cut, first x): "
    free = [again + site, again + "proof selftest_flyer_body.py changed since the build",
            again + "proof selftest_flyer: changed since the build",
            "game phase: modlist_swap.py --enable RM_Flyer refused: flyer: in no tier", "game phase: Flyer pack missing"]
    for w in free:
        ok(not R.hold_is_his({"kind": "game", "why": w}), "free text naming a flyer is no flyer hold: %s" % w)
        ok(Q.tooling_hold({"status": "held", "hold": {"kind": "game", "why": w}}), "and it is on the seat's list: %s" % w)
    for h in ({"kind": "owner_call", "why": "x"}, {"kind": "game", "why": flyer}, {"kind": "proof_weak", "why": "x"},
              {"kind": "strikes", "why": "x"}, {"kind": "spend", "why": "x"}, {"kind": "game", "why": "game phase: refused again"},
              {"kind": "proof_weak", "why": "a flyer: in the words"}, {"kind": "owner_call", "why": "flyer"},
              {"kind": "proof_weak", "why": "game phase: flyer: not a game hold"}):
        ok((Q.tooling_hold({"status": "held", "hold": h}) is None) is R.hold_is_his(h), "owner_queue agrees on %s" % h)
    ok(not hasattr(Q, "FLYER"), "owner_queue holds no second copy of the flyer test")


def t_hold_routing_real_ledger():
    """The same road with nothing faked but the Conductor's log: the real rimflow CLI on a temp ledger, the event it really
    writes read back, and the real legacy events in this tree's ledger (blind check, gap 2 and its untested mutant)."""
    model = R.pkg("model")
    real = [e for e in model.read() if e.get("event") == "needs" and e.get("to") == "owner" and e.get("why") == "relentless supervisor"]
    ok(real, "real: the ledger holds legacy supervisor-set needs=owner events in this exact shape")
    it = types.SimpleNamespace(history=[0])
    ok(real and R.Effects._owner_routing_is_ours(it, real[:1]), "real: a real legacy event reads as this supervisor's own routing")

    d = tempfile.mkdtemp(prefix="rlhold-")
    os.makedirs(os.path.join(d, "items"))
    env = dict(RIMFLOW_LEDGER=os.path.join(d, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(d, "items"), RIMFLOW_PROBE="no-reading",
               RIMFLOW_SCHEDULE=os.path.join(d, "no_schedule.json"), RIMFLOW_DRIVER_LOCK="", RIMFLOW_SHARED_BRIDGE="",
               RIMFLOW_BRIDGE_LOCK=os.path.join(d, "bridge.lock"), RM_HOST="archmagi")
    saved, saved_events = {k: os.environ.get(k) for k in env}, model.EVENTS
    os.environ.update(env)
    model.EVENTS = env["RIMFLOW_LEDGER"]    # the reader in this process took its path at import; the CLI takes the env
    try:
        fx = R.Effects(dict(RULES), R.Store(os.path.join(d, "store")))
        fx.books = os.path.abspath(os.path.join(R.HERE, "..", "..", ".."))    # this tree's cli; the env above points it at d
        told = []
        fx.conductor_attention = told.append

        def needs_of(item):
            fx._ledger = None
            return fx.ledger_items()[1].items[item].needs

        def events(item, kind):
            fx._ledger = None
            return [e for e in fx.ledger_items()[0] if e.get("id") == item and e.get("event") == kind]

        for i in ("LEGACY_PROBE_FIXTURE", "PERSON_PROBE_FIXTURE", "CALL_PROBE_FIXTURE", "PLAIN_PROBE_FIXTURE"):
            r = fx.rimflow("file", i, "--for", "BENCH", "--title", "t")
            ok(r.returncode == 0, "cli: filed %s: %s" % (i, r.stderr[-200:]))
        hold = {"kind": "proof_weak", "why": "weak", "delivered": False}

        ok(fx.ledger_needs_owner("LEGACY_PROBE_FIXTURE", "an old hold") is None, "cli: the old supervisor's road still writes")
        e = events("LEGACY_PROBE_FIXTURE", "needs")
        ok(e and e[-1].get("to") == "owner" and e[-1].get("why") == "relentless supervisor",
           "cli: ledger_needs writes the provenance the restore reads back: %s" % e[-1:])
        ok(needs_of("LEGACY_PROBE_FIXTURE") == "owner", "cli: routed to him before the hold")
        fx._ledger = None
        ok(fx.ledger_hold_to_seat("LEGACY_PROBE_FIXTURE", hold) is None, "cli: the legacy hold lands")
        ok(needs_of("LEGACY_PROBE_FIXTURE") == "offline", "cli: a legacy supervisor-set needs=owner is restored")
        ok(len(events("LEGACY_PROBE_FIXTURE", "note")) == 1 and len(told) == 1, "cli: a note and one Conductor line: %s" % told)

        r = fx.rimflow("needs", "PERSON_PROBE_FIXTURE", "--to", "owner", "--reason", "r", "--why", "an L4 look")
        ok(r.returncode == 0, "cli: a person's routing: %s" % r.stderr[-200:])
        fx._ledger = None
        ok(fx.ledger_hold_to_seat("PERSON_PROBE_FIXTURE", dict(hold, kind="strikes")) is None, "cli: a strikes hold lands")
        ok(needs_of("PERSON_PROBE_FIXTURE") == "owner", "cli: a person's needs=owner stays")
        ok(len(events("PERSON_PROBE_FIXTURE", "note")) == 1 and len(told) == 2, "cli: still noted and told")

        fx._ledger = None
        ok(fx.ledger_hold_to_seat("PLAIN_PROBE_FIXTURE", dict(hold, kind="game", why="game phase: refused again")) is None,
           "cli: a non-flyer game hold lands")
        ok(needs_of("PLAIN_PROBE_FIXTURE") == "offline" and not events("PLAIN_PROBE_FIXTURE", "needs"),
           "cli: a tooling hold writes no needs event at all")
        ok(len(events("PLAIN_PROBE_FIXTURE", "note")) == 1 and len(told) == 3, "cli: and is noted and told")

        ok(fx.ledger_needs_owner("CALL_PROBE_FIXTURE", "section 2") is None and needs_of("CALL_PROBE_FIXTURE") == "owner",
           "cli: owner_call's road still routes to him")
    finally:
        model.EVENTS = saved_events
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(d, ignore_errors=True)


def t_hold_lift_needs():
    """RELENTLESS_GAME_FIX_HOLD_LIFT_FORGETS_GAME: a lifted hold restores the needs people gave the item, never a blanket
    offline: a game item is in the pool for its needs, and a person's own routing stays where it is."""
    class It:
        def __init__(self, evs, needs="owner", state="doing", owed=()):
            self.needs, self.state, self.owed, self.history = needs, state, owed, list(range(len(evs)))

        def owed_levels(self):
            return list(self.owed)

    class W:
        items = {}

    class Fx(R.Effects):
        def __init__(self, evs):
            self.evs0, self._ledger = evs, None

        def ledger_items(self):
            return self.evs0, W()

    def after(evs, **kw):
        W.items = {"I": It(evs, **kw)}
        return Fx(evs).needs_after_hold("I")

    ours = {"event": "needs", "to": "owner", "why": R.SUPERVISOR_WHY}
    bug = {"event": "needs", "to": "offline", "why": R.SUPERVISOR_WHY, "reason": "relentless: the owner lifted the hold"}
    for want in ("bridge", "game-up", "deploy", "offline"):
        ok(after([{"event": "file", "needs": want}, ours]) == want, "a filed %s comes back" % want)
    ok(after([{"event": "file"}, ours]) == "offline", "a filing naming no needs is offline, as the model reads it")
    ok(after([{"event": "spawn", "needs": "bridge"}, ours]) == "bridge", "a spawned item's needs comes back")
    ok(after([{"event": "file"}, {"event": "needs", "to": "game-up", "why": "a person"}, ours]) == "game-up",
       "a person's later needs beats the filing")
    ok(after([{"event": "file", "needs": "deploy"}, ours, bug, ours]) == "deploy",
       "the offline an older lift wrote is the supervisor's own, stepped over")
    ok(after([{"event": "file", "needs": "deploy"}, ours], state="built", owed=["L2"]) == "bridge",
       "a built item keeps its derived needs")
    ok(after([{"event": "file", "needs": "bridge"}, ours], needs="game-up") is None, "moved off owner since: no write")
    ok(after([{"event": "file", "needs": "bridge"}, {"event": "needs", "to": "owner", "why": "an L4 look"}]) is None,
       "a person's needs=owner is not ours to move")
    ok(after([{"event": "needs", "to": "owner", "why": "an L4 look"}, ours]) is None,
       "routed to him over a person's needs=owner: it stays his")
    W.items = {}
    ok(Fx([]).needs_after_hold("I") is None, "an item the ledger has not heard of: no write")

    x = Rig(n=1, share=1.0)
    x.tick()

    def lift(why="x"):
        with x.s.lock():
            st = x.s.load("I0")
            st.update(status="held", hold={"kind": "owner_call", "why": why, "delivered": True})
            x.s.save(st)
        R.unhold(x.s, "I0", "go on")
        ok(x.st("I0")["needs_back"] is True, "his hold lifted: the ledger is owed its needs")
        del x.w.needs[:]

    def step():
        R.step(x.s, x.w, x.r, "I0", x.now, [])

    lift()
    x.w.needs_back = "bridge"
    x.w.needs_fail = "ledger down"
    step()
    ok(x.w.needs == [("I0", "bridge")] and x.st("I0")["needs_back"] is True, "a failed write stays owed: %s" % x.w.needs)
    x.w.needs_fail = None
    step()
    ok(x.w.needs[-1] == ("I0", "bridge") and x.st("I0")["needs_back"] is False, "the filed needs lands, never offline: %s" % x.w.needs)
    lift()
    x.w.needs_back = None
    step()
    ok(x.w.needs == [] and x.st("I0")["needs_back"] is False, "nothing ours to move: no write, and the item is free: %s" % x.w.needs)
    x.done()


def main():
    picked, ran = set(sys.argv[1:]), 0      # no names: every test
    # the real launcher's TMPDIR, kept off the real root: a dir left there made the next run's t_breaker_di2 read "still in use"
    os.environ["RM_RUN_TMP_ROOT"] = tempfile.mkdtemp(prefix="rlruntmp-")
    atexit.register(shutil.rmtree, os.environ["RM_RUN_TMP_ROOT"], ignore_errors=True)
    for t in (t_refused_start_is_held, t_refused_start_reason_reaches_hold, t_hold_routing, t_hold_routing_real_ledger, t_hold_lift_needs, t_help_round_two_vendor, t_weak_is_not_good, t_live_line_widens, t_time_is_no_failed_approach, t_one_builder_per_mod, t_parked_items_hold_no_place, t_line_full_of_one_mod_still_leases_another, t_waiting_items_hold_no_line_place, t_parked_system_items_hold_no_sys_room, t_plain_queued_items_hold_their_places, t_consulting_item_holds_no_line_place, t_refused_start_holds_no_line_place, t_incident_line_fills_every_place, t_enrol_reads_store_once_per_line, t_enrol_skips_taken_mod, t_item_mods_real, t_review_findings_core, t_review_findings_rig, t_review_wrong_verdicts, t_review_wrong_verdicts_two, t_proof_weak, t_shadow_narrow_weak, t_marker_prompts_one_rule, t_pool_jam, t_put_down_frees_places, t_prepare_remakes_clone, t_close_idempotent, t_pool_real_git, t_put_down_real_commit_end_to_end, t_put_down_every_shape, t_books_frozen, t_flush_lands_prose_moves, t_unpublished_enrol_waits, t_staffing_places, t_staffing_backlog, t_staffing_rise, t_foreign_take, t_foreign_tomb,
              t_foreign_eligible, t_parked_list, t_foreign_tree, t_foreign_back_in_line, t_staffing_edges, t_staffing_alarm, t_alarm_routes,
              t_worker_dies, t_same_failure, t_snag_wait, t_stale_worker, t_stop_order, t_spend, t_top_of_queue, t_share,
              t_done_path, t_crash_recovery, t_crash_windows, t_third_review, t_breaker_forgets_when_proved, t_one_sha_checkout_charges_no_launcher, t_tick_budget_reaches_lease, t_level_books_leaves_run_output, t_level_books_shard_under_lock, t_real_effects, t_launch_fail, t_breaker_di2, t_retire, t_concurrency, t_live_line,
              t_help_forced_once, t_help_own_call_spends_hits, t_help_reaches_brief, t_help_refused, t_help_lifecycle):
        if picked and t.__name__ not in picked:
            continue
        ran += 1
        print("--", t.__name__)
        t()
    if picked and ran != len(picked):     # a misspelt name must not read as a clean run
        print("selftest_relentless: FAIL ran %d of the %d named" % (ran, len(picked)))
        return 1
    print("selftest_relentless: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
