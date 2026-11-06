#!/usr/bin/env python3
"""selftest_relentless_broker.py -- the game broker (relentless_broker.py, LIVELANE_BUILD_GAME_BROKER_PROOF_LINES).

No game, no bridge, no ledger: selftest_relentless_game's GW world plus a broker launcher that records. What must hold,
each red under its planted break (--plant NAME):
  a built item at its prove launch queues its lines and is put down: no prove round of its own, its clone is not kept
    (plant offer_launches);
  the broker drains only when the game is idle: not while another item stages, not while the bridge is held (an OWNER
    hold included), not while a round runs; idle, it launches one job for the queue (plant drain_ignores_busy);
  the job runs each item's round, logs its clauses, and the item reads its rows as before and finishes;
  an OWNER hold that arrives between rounds skips the rest, nothing overridden (plant job_ignores_owner);
  an abandoned job (killed: its lock released by the kernel) has its entries marked lost and its items walk on
    (plant no_reconcile);
  a game restart makes a queued entry stale and the item queues again on the new game;
  a broker fault falls back to the lane as it was (the item's own prove round), and a fix that lands clears it
    (plant fault_sticks);
  the SLIs: clauses completed in 24 h and the oldest queued age (plant sli_blind).
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
import relentless as R                  # noqa: E402
import relentless_broker as B           # noqa: E402
import relentless_game as G             # noqa: E402
import relentless_jobs as J             # noqa: E402
import selftest_relentless as S         # noqa: E402
import selftest_relentless_game as SG   # noqa: E402

FAILS = S.FAILS
ok = S.ok
SHA = SG.SHA
STARTED = 5000.0
PLANT = None


class BW(SG.GW):
    """GW with the live launcher: broker_launch records, it starts nothing (the selftest runs the job in process)."""
    def __init__(self, n=2):
        SG.GW.__init__(self, n)
        self.blaunches = 0
        self.launch_why = None

    def broker_launch(self):
        self.blaunches += 1
        self.events.append("broker")
        return self.launch_why


def rig(n=1, **kw):
    x = SG.rig(n, **kw)
    x.w = BW(n)
    x.w.started = STARTED
    return x


def round_stub(calls, outcome="PASS"):
    def fn(root, item, timeout):
        calls.append(item)
        return 0, json.dumps({"at": "x", "why": "done", "runs": [
            {"item": item, "criterion": "A2", "outcome": outcome, "sha": SHA}]}, indent=1) + "\n"
    return fn


def run_job(x, owner=None, outcome="PASS"):
    calls = []
    B.BRIDGE_WHY = (lambda root: owner)
    B.ROUND = round_stub(calls, outcome)
    B.WAKE = (lambda root: None)
    word = B.job(x.s)
    return word, calls


def to_prove(x, i="I0"):
    SG.to_game(x, i)
    x.tick()
    ok(x.st(i)["game"]["phase"] == "prove", "%s: implemented, at its prove phase" % i)


def entry(x, i="I0"):
    return B.entry(x.s, i) or {}


def apply_plants():
    if PLANT == "offer_launches":
        G._broker_offer = lambda *a, **k: False
    if PLANT == "drain_ignores_busy":
        B.idle_why = lambda store, fx, rd, queued: None
    if PLANT == "job_ignores_owner":
        real = B.job

        def job(store):
            B.BRIDGE_WHY = (lambda root: None)
            return real(store)
        B.job = job
    if PLANT == "no_reconcile":
        B.reconcile = lambda store, now, acts: []
        B.job_alive = lambda store, now=None: J.running(store, B.KIND) or J.table(store, B.KIND).get("state") == "running"
    if PLANT == "fault_sticks":
        B.faulted = lambda store: B._read(os.path.join(B._dir(store), "fault.json"), {}) or None
    if PLANT == "sli_blind":
        B.VERDICTS = ()


# ---------------------------------------------------------------- tests

def t_built_item_queues_and_holds_nothing():
    x = rig(1)
    to_prove(x)
    x.w.idle = "NOT TAKEABLE  OWNER holds it"
    x.tick()
    st = x.st("I0")
    ok(not x.w.proves, "queued, not its own prove round")
    ok(entry(x).get("state") == "queued" and (st["game"].get("broker") or {}).get("queued_at"),
       "the item's lines are in the broker queue: %s" % entry(x))
    ok("broker" in ((st.get("put_down") or {}).get("on") or ""), "put down while queued: %s" % st.get("put_down"))
    ok(x.w.blaunches == 0 and "take" not in x.w.events, "his hold: the broker launches nothing, takes nothing")
    rows = [r for r in R.pool_rows(x.s, x.w, x.r) if r["item"] == "I0"] if hasattr(R, "pool_rows") else []
    ok(all(r["rank"] < 2 for r in rows), "a queued item's clone is not kept: %s" % rows)
    x.tick()
    ok(not x.w.proves and entry(x).get("state") == "queued", "it stays queued, still no round of its own")
    x.done()


def t_drains_only_when_idle():
    x = rig(2, share=1.0, max_workers=2)
    x.w.idle = "NOT TAKEABLE  BENCH holds it"
    to_prove(x, "I0")
    to_prove(x, "I1")
    x.tick()
    ok(entry(x, "I0").get("state") == entry(x, "I1").get("state") == "queued", "both queued while the bridge is held")
    ok(x.w.blaunches == 0, "bridge held: no broker job")
    x.w.idle = None
    with open(x.s.p("showings.json"), "w") as f:      # another live user has the game: a showing build holds it
        json.dump({"rows": {"SHOW_X": {"phase": "build", "bridge": True}}}, f)
    ok(G.busy(x.s, None), "the showing is a live user")
    x.tick()
    ok(x.w.blaunches == 0, "another live user has the game: no broker job")
    os.remove(x.s.p("showings.json"))
    os.makedirs(os.path.join(x.s.root, "live"), exist_ok=True)
    import fcntl
    lk = open(os.path.join(x.s.root, "live", "round.lock"), "w")
    fcntl.flock(lk, fcntl.LOCK_EX)
    x.tick()
    ok(x.w.blaunches == 0, "a live round runs: no broker job")
    lk.close()
    x.tick()
    ok(x.w.blaunches == 1, "idle game: one broker job (%d)" % x.w.blaunches)
    st = x.st("I0")
    ok(st["game"]["phase"] == "proving" and st["game"]["broker"].get("batch") and not st.get("put_down"),
       "the batch item holds the game as a live user (phase proving): %s" % st["game"].get("phase"))
    ok(G.busy(x.s, "I1") is not None, "while the batch is out, nobody else starts")
    x.done()


def t_job_runs_and_item_finishes():
    x = rig(1)
    to_prove(x)
    x.tick()
    ok(x.w.blaunches == 1 and entry(x).get("state") == "running", "idle: queued and launched in one tick")
    word, calls = run_job(x)
    ok(word == "done" and calls == ["I0"], "the job ran the item's own round: %s %s" % (word, calls))
    ok(entry(x).get("state") == "ran", "the entry is ran: %s" % entry(x).get("state"))
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "PASS"}]
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "game" and not st["game"].get("broker"), "turn over: the item reads its rows as before")
    ok(not x.w.proves, "never a prove round of its own")
    x.w.led["I0"]["state"] = "done"
    x.tick()
    ok(x.st("I0")["status"] == "done", "the ledger's done finishes it")
    s = B.slis(x.s, time.time())
    ok(s["clauses_completed_day"] == 1 and s["oldest_queued_s"] is None and s["queued"] == 0,
       "SLIs: one clause completed, nothing queued: %s" % s)
    x.done()


def t_owner_hold_between_rounds_skips():
    x = rig(1)
    to_prove(x)
    x.tick()
    word, calls = run_job(x, owner="NOT TAKEABLE  OWNER holds it")
    ok(calls == [] and entry(x).get("state") == "skipped", "his hold mid-batch: no round, entry skipped (%s)" % calls)
    x.tick()
    ok(not x.st("I0")["game"].get("broker"), "the skipped item walks on")
    x.done()


def t_abandoned_job_is_recovered():
    x = rig(1)
    to_prove(x)
    x.tick()
    ok(entry(x).get("state") == "running", "launched")
    # a job that took the lock and was killed: the kernel releases its flock, the table still says running
    lock = J._path(x.s, B.KIND, ".lock")
    p = subprocess.Popen([sys.executable, "-c", "import fcntl,os,sys,time\nfd=os.open(sys.argv[1],os.O_RDWR)\n"
                          "fcntl.flock(fd,fcntl.LOCK_EX)\nprint('held',flush=True)\ntime.sleep(60)", lock],
                         stdout=subprocess.PIPE, text=True)
    ok(p.stdout.readline().strip() == "held", "the stand-in job holds the lock")
    with J._table(x.s, B.KIND):
        t = J.table(x.s, B.KIND)
        t.update(state="running", pid=p.pid)
        J._write(J._path(x.s, B.KIND, ".json"), t)
    x.tick()
    ok(entry(x).get("state") == "running" and B.job_alive(x.s), "alive: the batch is left alone")
    p.send_signal(signal.SIGKILL)
    p.wait()
    acts = x.tick()
    ok(any(a.get("do") == "broker_lost" for a in acts or []), "killed: broker_lost journalled")
    ok(entry(x).get("state") in ("lost", None) and J.table(x.s, B.KIND).get("lost") == 1,
       "the entry is lost and the table counts it: %s %s" % (entry(x).get("state"), J.table(x.s, B.KIND).get("lost")))
    st = x.st("I0")
    ok(st["status"] == "game" and st["game"]["phase"] in ("prove", "proving") and
       (st["game"].get("broker") or {}).get("batch") is None, "the item walks on, not stuck in the dead batch: %s"
       % st["game"].get("broker"))
    x.done()


def t_restart_makes_queued_stale():
    x = rig(1)
    to_prove(x)
    x.w.idle = "NOT TAKEABLE  BENCH holds it"
    x.tick()
    ok(entry(x).get("game") == STARTED, "queued on the running game")
    x.w.started = STARTED + 900
    x.tick()        # drain marks it stale
    x.tick()        # the item walks on and queues on the new game
    ok(entry(x).get("state") == "queued" and entry(x).get("game") == STARTED + 900,
       "re-queued on the new game: %s" % entry(x))
    x.done()


def t_fault_falls_back_to_the_lane():
    x = rig(1)
    to_prove(x)
    real_offer, real_fp = B.offer, B.code_fp
    B.offer = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("planted broker fault"))
    try:
        x.tick()
    finally:
        B.offer = real_offer
    ok(x.w.proves == ["I0"], "a broker fault: the item launches its own round, as before (%s)" % x.w.proves)
    ok(B.faulted(x.s) and not B.active(x.s, x.w), "the fault holds the broker off on this code")
    ok("FAULT" in B.sli_line(B.slis(x.s)), "the reading says the old lane is in use")
    B.code_fp = lambda: "a-fix-landed"
    try:
        ok(B.active(x.s, x.w), "a fix that lands (new code fingerprint) clears it")
    finally:
        B.code_fp = real_fp
    x.done()


def t_fault_fallback_still_asks_the_lease():
    x = rig(1)
    to_prove(x)
    x.w.idle = "NOT TAKEABLE  OWNER holds it"
    real = B.offer
    B.offer = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("planted broker fault"))
    try:
        x.tick()
    finally:
        B.offer = real
    ok(x.w.proves == [], "a broker fault under his bridge hold: the fallback launches no round (%s)" % x.w.proves)
    x.done()


def t_reconcile_leaves_a_job_that_just_started():
    x = rig(1)
    to_prove(x)
    x.tick()
    ok(entry(x).get("state") == "running", "launched")
    fd = J.os.open(J._path(x.s, B.KIND, ".lock"), J.os.O_CREAT | J.os.O_RDWR, 0o644)
    J.fcntl.flock(fd, J.fcntl.LOCK_EX)
    real = B.job_alive
    B.job_alive = lambda store, now=None: False     # the first look said dead; the job took its lock right after
    try:
        got = B.reconcile(x.s, time.time(), [])
    finally:
        B.job_alive = real
        J.os.close(fd)
    ok(got == [] and entry(x).get("state") == "running", "a live job's running entries are not marked lost (%s)" % got)
    x.done()


def t_off_without_launcher():
    x = SG.rig(1)
    x.w.started = STARTED
    SG.to_game(x, "I0")
    x.tick()
    x.tick()
    ok(x.w.proves == ["I0"] and not B.entry(x.s, "I0"), "no launcher (not the live supervisor): the lane as it was")
    x.done()


def t_slis_report_oldest_queued():
    x = rig(1)
    to_prove(x)
    x.w.idle = "NOT TAKEABLE  OWNER holds it"
    x.tick()
    at = entry(x)["queued_at"]
    s = B.slis(x.s, at + 600)
    ok(s["queued"] == 1 and s["oldest_queued_s"] == 600, "oldest queued age read: %s" % s)
    rec = R.reading(x.s, x.r, at + 600, [], fx=x.w)
    ok((rec.get("broker") or {}).get("oldest_queued_s") == 600, "relentless.py reading carries it: %s" % rec.get("broker"))
    B._log(x.s, [{"at": at, "item": "I0", "criterion": "A2", "outcome": "FAIL"},
                 {"at": at, "item": "I0", "criterion": "A3", "outcome": "UNMEASURED"},
                 {"at": at - 90000, "item": "I0", "criterion": "A4", "outcome": "PASS"}])
    s = B.slis(x.s, at + 600)
    ok(s["clauses_completed_day"] == 1 and s["clauses_run_day"] == 2, "24 h window, verdicts only: %s" % s)
    x.done()


TESTS = (t_built_item_queues_and_holds_nothing, t_drains_only_when_idle, t_job_runs_and_item_finishes,
         t_owner_hold_between_rounds_skips, t_abandoned_job_is_recovered, t_restart_makes_queued_stale,
         t_fault_falls_back_to_the_lane, t_fault_fallback_still_asks_the_lease,
         t_reconcile_leaves_a_job_that_just_started, t_off_without_launcher, t_slis_report_oldest_queued)
PLANTS = ("offer_launches", "drain_ignores_busy", "job_ignores_owner", "no_reconcile", "fault_sticks", "sli_blind")


def main(argv=None):
    global PLANT
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", choices=PLANTS)
    ap.add_argument("only", nargs="*")
    a = ap.parse_args(argv)
    PLANT = a.plant
    real_cfg = B.cfg
    B.cfg = lambda: dict(real_cfg(), enabled=True)      # the selftest never depends on the live switch
    apply_plants()
    ran = 0
    for t in TESTS:
        if a.only and t.__name__ not in a.only:
            continue
        ran += 1
        print("--", t.__name__)
        t()
    if a.only and ran != len(a.only):
        print("selftest_relentless_broker: FAIL ran %d of the %d named" % (ran, len(a.only)))
        return 1
    print("selftest_relentless_broker: %s%s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS",
                                                " (plant %s)" % PLANT if PLANT else ""))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
