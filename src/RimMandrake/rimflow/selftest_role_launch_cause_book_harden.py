#!/usr/bin/env python3
"""Selftest of RELENTLESS_ROLE_LAUNCH_HARDEN_CAUSE_BOOK (Codex review of role_launch.py WP-15, 2026-11-06):
  A  the cause book's load-attach-save holds a writer lock that ops_watch's alarm pass holds too, so a concurrent
     update survives; a busy book defers the attach to the next tick (never written without the lock, never lost);
  B  the Setter route's exam reset and unit kick are a dispatcher action: a dry run resets and kicks nothing;
  C  a stage_close that raises after the run was marked finished is retried by the next supervision, not abandoned;
  D  a builder re-run of a rejected close is told every reason, in full (was: four, cut to 400 characters).
Temp stores and fake seams only: no systemd, no git, no real ops dir or relentless store."""
import json
import os
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest_cause_book_harden_")
os.environ["RM_OPS_WATCH_DIR"] = TMP          # ops_watch.ops_dir() and so cause_book_path(): the temp dir
import cause_book as CB  # noqa: E402
import role_launch as RL  # noqa: E402
from selftest_dispatcher import D, fresh, sched  # noqa: E402

FAILS = []
T = 1793953915
C1 = "/tmp/concepts/Pyrelands"
KEY = "role-env|Designer|x"
BOOK = os.path.join(TMP, "causes.json")


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def live_book():
    book = {}
    CB.begin(book, KEY, "lead", "REPAIR_ITEM", T)
    CB.filed(book, KEY, "REPAIR_ITEM", T)
    CB.save(BOOK, book)


class _Lk:
    def close(self):
        pass


FX = {"note": lambda i, t: (True, ""), "publish": lambda n: None, "lock": lambda: _Lk(), "paused": lambda: None,
      "off": lambda p: None}


def execute(acts, apply, st=None, **fx):
    st = st if st is not None else fresh()
    root = os.path.join(TMP, "root")
    os.makedirs(os.path.join(root, "inbox"), exist_ok=True)
    D.execute(acts, sched(), st, root, apply, time.time(), dict(FX, **fx), deadline=time.time() + 100)
    return st


def designer_cfg():
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json"), encoding="utf-8"))
    row = next(r for r in sch["roles"] if isinstance(r, dict) and r.get("stage_machine") == "designer_stage")
    return dict(RL.ROLE_DEFAULTS, **row)


GOOD = {"subtype": "success", "usage": {k: 10 for k in RL.USAGE_KEYS}}


def obs_for(close, res=GOOD, **more):
    o = {"unit_state": lambda u: "inactive", "result": lambda r: res, "procs": lambda *a, **k: [],
         "stage_close": close, "stage_land": lambda c, u: None, "stage_turn": lambda c: None,
         "stage_status": lambda c: {"stage": 4, "status": "ready"}}
    o.update(more)
    return o


def new_run(rs, unit="rm-role-designer-1"):
    run = {"state": "running", "unit": unit, "at": T - 600, "day": RL.day_of(T), "budget": 90000, "mode": "run",
           "item": "PYRE_ITEM", "concept": C1, "scope": "S.scope", "marker": "M"}
    rs.setdefault("runs", []).append(run)
    return run


def tick(rs, obs, now=T):
    acts = []
    RL._supervise_one("Designer", rs, designer_cfg(), obs, now, lambda **kw: acts.append(kw), set())
    return acts


# ---- A. the lock
def test_a_concurrent_update_survives():
    live_book()
    held, release = threading.Event(), threading.Event()

    def ops_pass():         # ops_watch's shape: lock, load, (a long filing), its own change, save
        with CB.locked(BOOK):
            book = CB.load(BOOK)
            held.set()
            release.wait(5)
            CB.attach(book, KEY, "ops-alarm", "ops reading", T + 1)
            CB.save(BOOK, book)

    t = threading.Thread(target=ops_pass)
    t.start()
    held.wait(5)
    out = {}
    a = threading.Thread(target=lambda: out.setdefault("ok", RL.cause_attach(KEY, "role reading", T + 2)))
    a.start()
    time.sleep(0.3)
    check(a.is_alive(), "A1 the role attach waits while ops_watch's pass holds the book (it did not write past it)")
    release.set()
    t.join(5)
    a.join(10)
    said = [r.get("said") for r in CB.load(BOOK)[KEY].get("readings") or []]
    check(out.get("ok") is True and "ops reading" in said and "role reading" in said,
          "A2 both updates survive a concurrent pass (before: the later save of a stale load erased one): %r" % said)


def test_a_busy_book_defers():
    live_book()
    with CB.locked(BOOK):
        t0 = time.monotonic()
        try:
            RL.cause_attach(KEY, "x", T, wait_s=0.2)
            raised = False
        except CB.Busy:
            raised = True
        check(raised and time.monotonic() - t0 < 2, "A3 a lock held past the wait raises Busy, nothing written")
        st = execute([dict(do="role_cause_attach", role="Designer", key=KEY, said="deferred one", at_s=T)], True,
                     cause_attach=lambda k, s, a, wait_s=None: RL.cause_attach(k, s, a, wait_s=0.1))
    check([o.get("said") for o in st.get("cause_owed") or []] == ["deferred one"],
          "A4 the Dispatcher keeps a busy book's attach in its state: %r" % st.get("cause_owed"))
    acts = []
    RL.supervise_roles({"roles": []}, st, {}, T, lambda **kw: acts.append(kw))
    again = [a for a in acts if a.get("do") == "role_cause_attach"]
    RL.supervise_roles({"roles": []}, st, {}, T, lambda **kw: acts.append(kw))
    check(len(again) == 1 and again[0]["key"] == KEY and len(st.get("cause_owed") or []) == 1,
          "A5 the next tick asks the owed attach again, and it stays owed until carried out (a fenced tick loses none)")
    execute(again, True, st=st)
    check("deferred one" in [r.get("said") for r in CB.load(BOOK)[KEY].get("readings") or []]
          and "cause_owed" not in st, "A6 and, the book free, it lands and leaves the owed list")


def test_a_busy_once_owes_the_rest():
    live_book()
    calls = []

    def busy(k, s, a, wait_s=None):
        calls.append(wait_s)
        raise CB.Busy("held")

    st = execute([dict(do="role_cause_attach", role="Designer", key=KEY, said="s%d" % i, at_s=T + i)
                  for i in range(5)], True, cause_attach=busy)
    check(len(calls) == 1 and len(st.get("cause_owed") or []) == 5 and 0 < calls[0] <= RL.CAUSE_ATTACH_WAIT_S,
          "A9 one busy wait per tick: the other attaches are owed at once (%r waits)" % calls)
    st2 = execute([dict(do="role_cause_attach", role="Designer", key=KEY, said="s0", at_s=T)], True, st=st,
                  cause_attach=busy)
    check(len(st2["cause_owed"]) == 5, "A10 an attach already owed is not owed twice")


def test_a_ops_watch_holds_the_lock():
    utils = os.path.join(os.path.dirname(HERE), "Utils")
    sys.path.insert(0, utils)
    import ops_watch
    done = threading.Event()
    with CB.locked(BOOK):
        th = threading.Thread(target=lambda: (ops_watch.file_held(None, {}, T), done.set()))
        th.start()
        time.sleep(0.3)
        check(not done.is_set(), "A7 ops_watch's held-filing pass waits for the book lock")
    th.join(10)
    check(done.is_set(), "A8 and runs once the lock is free")


# ---- B. the action boundary
def test_b_setter_is_an_action():
    import relentless
    import relentless_exam as RE
    store = relentless.Store(os.path.join(TMP, "rel"))
    RE.set_status(store, "PYRE_ITEM", state="validated", base="abc")
    kicked = []
    rs = {}
    new_run(rs)
    acts = tick(rs, obs_for(lambda c, u, t: (False, ["[cause:check] clause c3 asserts the old schema"]),
                            setter=lambda item, reasons, now, role=None: RL.to_setter(item, reasons, now, store=store,
                                                                                       role=role)))
    resit = [a for a in acts if a.get("do") == "role_setter_resit"]
    check(len(resit) == 1 and RE.status(store, "PYRE_ITEM").get("state") == "validated" and not kicked,
          "B1 deciding the check route resets no exam and kicks nothing; it hands one action on")
    calls = []
    execute(list(resit), False, setter_resit=lambda *a: calls.append(a))
    check(not calls and RE.status(store, "PYRE_ITEM").get("state") == "validated",
          "B2 a dry run of that action resits nothing and starts no Setter unit")
    execute(list(resit), True, setter_resit=lambda i, w, at: RL.setter_resit(
        i, w, at, store=store, kicker=lambda s, it: kicked.append(it)))
    stx = RE.status(store, "PYRE_ITEM")
    check(stx.get("state") == "owed" and kicked == ["PYRE_ITEM"] and "c3" in stx.get("resit_why", ""),
          "B3 applied, the exam is owed again with the reasons and its unit kicked: %r" % stx)


def test_b_cause_attach_dry_writes_nothing():
    live_book()
    execute([dict(do="role_cause_attach", role="Designer", key=KEY, said="dry", at_s=T)], False)
    check("role-stage" not in CB.load(BOOK)[KEY]["aids"], "B4 a dry run writes nothing into the cause book")


# ---- C. the close retry
def test_c_close_raise_is_retried():
    calls = []

    def flaky(c, u, t):
        calls.append(u)
        if len(calls) == 1:
            raise OSError("stage.json: transient read")
        return True, []

    rs = {}
    run = new_run(rs)
    acts = tick(rs, obs_for(flaky))
    check(run["state"] == "done" and run.get("close_owed", {}).get("tries") == 1
          and any(a.get("kind") == "role:Designer:stage_close" and "retried next tick" in a.get("why", "")
                  for a in acts), "C1 a close that raises leaves the finished run owing its close, said")
    acts = tick(rs, obs_for(flaky), now=T + 60)
    check(len(calls) == 2 and "close_owed" not in run
          and any(a.get("do") == "role_stage" and "accepted" in a.get("why", "") for a in acts),
          "C2 the next supervision closes it again and the stage advances")
    tick(rs, obs_for(flaky), now=T + 120)
    check(len(calls) == 2, "C3 a returned close is never repeated")
    old = {"state": "failed", "unit": "rm-role-designer-0", "at": T - 5 * 86400, "concept": C1,
           "close_owed": {"since": T - 86400, "tries": 9}}
    gone = {"state": "done", "unit": "rm-role-designer-00", "at": T - 5 * 86400}
    rs2 = {"runs": [old, gone]}

    def still_down(c, u, t):
        raise OSError("still down")

    tick(rs2, obs_for(still_down))
    kept = rs2.get("runs") or []
    check(old in kept and gone not in kept and old["close_owed"]["tries"] == 10,
          "C4 the two-day prune keeps a run that still owes its close (and retries it), drops the rest")
    rs3 = {"runs": [{"state": "failed", "unit": "rm-role-designer-9", "at": T - 3 * 86400, "concept": C1,
                     "close_owed": {"since": T - 3 * 86400, "tries": 99}}]}
    acts = tick(rs3, obs_for(still_down))
    check(not rs3["runs"] and any("given up" in a.get("why", "") and a.get("conductor_log") for a in acts),
          "C5 a close still failing past CLOSE_OWED_MAX_S is given up, said to the Conductor, and pruned")

    class Refused(Exception):
        pass

    def refused(c, u, t):
        raise Refused("run is not the open run")

    rs4 = {}
    run4 = new_run(rs4)
    acts = tick(rs4, obs_for(refused))
    check("close_owed" not in run4 and any("NOT retried" in a.get("why", "") for a in acts),
          "C6 designer_stage.Refused is final: said once, not retried")


# ---- D. every reason
def test_d_full_reasons():
    errs = ["reason %d: " % i + "x" * 350 + " end%d" % i for i in range(6)]
    rs = {}
    new_run(rs)
    tick(rs, obs_for(lambda c, u, t: (False, list(errs))))
    req = rs.get("run_now") or {}
    check(req.get("reasons") == errs, "D1 the re-chain request carries all %d reasons, untruncated" % len(errs))
    cfg = designer_cfg()
    job = RL.run_now_job(cfg, req, T)
    msg = RL.prompt(cfg, job["mode"], job["trigger"], "green", {}, 0, 0, 1.0, 0, "rm-role-designer-2",
                    rows=job.get("rows"), reasons=job.get("reasons"))
    check(all(e in msg for e in errs), "D2 the launch message holds every reason in full (the fifth and sixth too)")


TESTS = (test_a_concurrent_update_survives, test_a_busy_book_defers, test_a_busy_once_owes_the_rest,
         test_a_ops_watch_holds_the_lock,
         test_b_setter_is_an_action, test_b_cause_attach_dry_writes_nothing, test_c_close_raise_is_retried,
         test_d_full_reasons)


def main():
    for t in TESTS:
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
