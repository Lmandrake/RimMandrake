#!/usr/bin/env python3
"""Selftest: a Relentless backoff ends when its cause closes, not when its clock runs out (RELENTLESS_REWIRE_BACKOFFS_ON_CAUSE_CLOSE).

    python3 src/RimMandrake/rimflow/selftest_relentless_cause_close.py

Pins, on the supervisor's own ticks (FakeWorld from selftest_relentless) where the path is reachable:
  * BREAKER clone_exists: opened by the measured 'scratch_clone: FAILED: <path> already exists'; holds while the path
    stands; the tick after the path is gone closes it and a run launches, long before breaker_cool_s;
  * BREAKER publickey: a publish poke BEFORE the failure ends nothing; one after it closes the breaker;
  * BREAKER unclassified: no cause recorded, the clock alone ends it (the cap is still there);
  * SNAG repeat: a repeat snag naming an open item waits until that item closes, then is back in line at once; one
    naming only a closed item, or a --wait-hours snag, keeps its clock;
  * START refusal: a ledger start refusal waits until any wake poke after it;
  * RECHECK (legacy unmeasured route): recheck_at ends when the named open item closes; and through a real UNMEASURED
    verdict (R.main, reach_repair false), unmeasured() records the cause and the first tick after the item closes ends it;
  * the wake serve runs the cause sweep, and no clock key is still kind backoff_owed.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                       # noqa: E402
import relentless_cause as C                 # noqa: E402
import relentless_wake as W                  # noqa: E402
import selftest_relentless as SR             # noqa: E402

FAILS = []
COOL = 900


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def rig(**rules):
    return SR.Rig(n=1, share=1.0, max_workers=1, launch_breaker=2, breaker_cool_s=COOL, breaker_cool_max_s=1800,
                  **rules)


def poke(x, source, at):
    W.poke(source, "test", root=x.d, now=at)


def open_breaker(x, why):
    x.w.lfail = why
    x.tick()
    x.tick(10)
    x.w.lfail = None
    br = R.load_breaker(x.s)
    return br


def journal(x, do):
    try:
        with open(x.s.p("journal.jsonl"), encoding="utf-8") as f:
            return [j for j in map(json.loads, f) if j.get("do") == do]
    except OSError:
        return []


def t_breaker_clone_exists():
    x = rig()
    path = tempfile.mkdtemp(prefix="rl-clone-")
    br = open_breaker(x, "help clone failed: scratch_clone: FAILED: %s already exists" % path)
    ok(br.get("until", 0) > x.now and (br.get("cause") or {}).get("kind") == "clone_exists"
       and br["cause"].get("path") == path, "a clone-exists failure opens the breaker and records its path: %r" % br)
    n = len(x.w.launches)
    x.tick(20)
    ok(len(x.w.launches) == n and R.load_breaker(x.s).get("until", 0) > x.now, "the breaker holds while the clone stands")
    shutil.rmtree(path)
    x.tick(20)
    ok(not R.load_breaker(x.s).get("until"), "the clone gone, the breaker closes at the next tick (40 s, not %d s)" % COOL)
    ok(journal(x, "backoff_cause_closed"), "the close is journalled with its cause")
    x.tick(20)
    ok(len(x.w.launches) > n, "a run launches once the cause closed")
    ok(R.load_breaker(x.s).get("opens"), "the open stays counted for the same-cause emergency")
    x.done()


def t_breaker_publickey():
    x = rig()
    poke(x, "publish", x.now - 50)      # a publish before the failure proves nothing about the key now
    br = open_breaker(x, "fetch -q origin: git@github.com: Permission denied (publickey).\nfatal: Could not read")
    ok((br.get("cause") or {}).get("kind") == "publickey", "a publickey failure records its cause")
    x.tick(20)
    ok(R.load_breaker(x.s).get("until", 0) > x.now, "an older publish poke does not close it")
    poke(x, "job_mods_fp", x.now + 1)
    x.tick(20)
    ok(R.load_breaker(x.s).get("until", 0) > x.now, "a poke from another source does not close it")
    poke(x, "publish", x.now + 1)
    x.tick(20)
    ok(not R.load_breaker(x.s).get("until"), "a publish after the failure closes it")
    x.done()


def t_breaker_unclassified():
    x = rig()
    br = open_breaker(x, "launcher died")
    ok(br.get("until", 0) > x.now and not br.get("cause"), "an unclassified failure records no cause")
    poke(x, "publish", x.now + 1)
    x.tick(20)
    ok(R.load_breaker(x.s).get("until", 0) > x.now, "so no poke ends it")
    x.tick(COOL)
    x.tick(20)
    ok(x.w.launches, "its clock still ends it")
    x.done()


def snag_twice(x, detail, wait_hours=0):
    for _ in range(2):
        x.run_one("I0")
        st = x.st("I0")
        R.snag(x.s, "I0", st["gen"], "tests_red", detail, x.r, now=x.now, wait_hours=wait_hours)
        x.w.up[st["run"]["unit"]] = False
        x.tick(30)
    return x.st("I0")


def t_snag_repeat():
    x = rig(snag_again_wait_h=1, same_failure_limit=50, unchanged_returns_limit=500)
    x.w.items["OTHER_FIX_LANDS_FIRST"] = "doing"
    st = snag_twice(x, "red until OTHER_FIX_LANDS_FIRST lands; I0 itself is fine")
    cause = st.get("not_before_cause") or {}
    ok(st["not_before"] > x.now + 1800 and cause.get("kind") == "items", "a repeat snag waits and records its cause: %r"
       % cause)
    ok(cause.get("on") == ["OTHER_FIX_LANDS_FIRST"], "the open item is the cause, after the first read: %r" % cause)
    x.tick(30)
    ok(x.st("I0")["not_before"] > x.now, "the wait holds while the named item is open")
    x.w.items["OTHER_FIX_LANDS_FIRST"] = "done"
    n = len(x.w.launches)
    acts = x.tick(30)
    st = x.st("I0")
    ok(any(a.get("do") == "backoff_cause_closed" and a.get("key") == "not_before" for a in acts)
       and "not_before_cause" not in st, "the named item closed: the wait ends at the next tick")
    ok(st["status"] == "running" and len(x.w.launches) > n, "and a worker is sent that same tick, an hour early")
    x.done()

    x = rig(snag_again_wait_h=1, same_failure_limit=50, unchanged_returns_limit=500)
    x.w.items["OLD_FIX_ALREADY_CLOSED"] = "done"
    st = snag_twice(x, "red; see OLD_FIX_ALREADY_CLOSED for history")
    x.tick(30)
    st = x.st("I0")
    ok(st["not_before"] > x.now, "a snag naming only a closed item is history, not a cause: the clock stands")
    x.done()

    x = rig(snag_again_wait_h=1, same_failure_limit=50, unchanged_returns_limit=500)
    x.w.items["OTHER_FIX_LANDS_FIRST"] = "doing"
    x.run_one("I0")
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "sample_thin", "sample filling; OTHER_FIX_LANDS_FIRST", x.r, now=x.now, wait_hours=2)
    st = x.st("I0")
    ok(st["not_before"] > x.now and "not_before_cause" not in st, "a worker's --wait-hours is time: no cause recorded")
    x.done()


def t_start_refusal():
    x = rig()
    x.w.ledger_start = lambda item: "refused: rimflow start: item is not ready"
    x.tick()
    st = x.st("I0")
    ok(st.get("start_again_at", 0) > x.now and (st.get("start_again_cause") or {}).get("kind") == "poke",
       "a start refusal waits and records a state-change cause: %r" % st.get("start_again_cause"))
    x.w.ledger_start = SR.FakeWorld.ledger_start.__get__(x.w)
    x.tick(20)
    ok(x.st("I0").get("start_again_at", 0) > x.now, "no poke, still waiting")
    poke(x, "publish", x.now + 1)
    x.tick(20)
    st = x.st("I0")
    ok(st.get("start_again_at", 0) <= x.now and "start_again_cause" not in st, "a landed commit ends the wait")
    x.done()


def t_recheck():
    x = rig()
    x.tick()
    with x.s.lock():
        st = x.s.load("I0")
        st["recheck_at"] = x.now + 1800
        C.record(st, "recheck_cause", C.of("box cannot reach D:\\x; repair is HARNESS_REACH_FIX_OPEN", "I0"), x.now)
        x.s.save(st)
    x.w.items["HARNESS_REACH_FIX_OPEN"] = "doing"
    ok(C.sweep(x.s, x.w, x.now + 5, [], R.iso) == 0 and x.st("I0").get("recheck_at"), "recheck holds while the repair is open")
    x.w.items["HARNESS_REACH_FIX_OPEN"] = "done"
    ok(C.sweep(x.s, x.w, x.now + 10, [], R.iso) == 1 and "recheck_at" not in x.st("I0"),
       "the repair closed: the same sha is checked again now")
    x.done()


def t_recheck_through_verdict():
    """The real UNMEASURED end (rule reach_repair false): a verdict through R.main whose --unreached names an open item;
    unmeasured() itself records recheck_cause, and the first tick after that item closes ends recheck_at."""
    x = SR.Rig(n=1, reach_repair=False, share=1.0, same_failure_limit=2, unmeasured_limit=3, unmeasured_recheck_s=1800)
    x.w.items["HARNESS_REACH_FIX_OPEN"] = "doing"
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "grep -q free_bytes infrastructure/state/facts/steve_c_drive_fill_2026-11-03.md",
               live="once: test")
    R.finish(x.s, "I0", st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    for _ in range(4):
        if x.st("I0")["status"] == "checking":
            break
        x.tick()
    st = x.st("I0")
    ok(st["status"] == "checking", "the candidate is being checked: %s" % st["status"])
    os.environ["RELENTLESS_ROOT"] = x.d
    try:
        rc = R.main(["verdict", "--item", "I0", "--nonce", st["check"]["nonce"], "UNMEASURED",
                     "could not read the evidence", "--unreached",
                     "box cannot reach D:\\x; its repair is HARNESS_REACH_FIX_OPEN"])
    finally:
        os.environ.pop("RELENTLESS_ROOT", None)
    ok(rc in (0, None), "the CLI takes the UNMEASURED verdict: %r" % rc)
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    t0 = x.now
    cause = st.get("recheck_cause") or {}
    ok(st["status"] == "candidate" and st.get("recheck_at", 0) > x.now and (st.get("blind") or {}).get("n") == 1,
       "a real UNMEASURED end waits for a recheck: %s %r" % (st["status"], st.get("recheck_at")))
    ok("HARNESS_REACH_FIX_OPEN" in json.dumps(cause), "unmeasured() records the open item as the recheck's cause: %r" % cause)
    for _ in range(3):
        x.tick(60)
    ok(x.st("I0").get("recheck_at", 0) > x.now, "the recheck holds while the named item is open")
    x.w.items["HARNESS_REACH_FIX_OPEN"] = "done"
    acts = x.tick(30)
    st = x.st("I0")
    ok(any(a.get("do") == "backoff_cause_closed" and a.get("key") == "recheck_at" for a in acts)
       or any(j.get("key") == "recheck_at" for j in journal(x, "backoff_cause_closed")),
       "the item closed: backoff_cause_closed on recheck_at at the next tick")
    ok("recheck_at" not in st and "recheck_cause" not in st and x.now - t0 < 1800,
       "the recheck ended %d s after the verdict, not at unmeasured_recheck_s (1800 s): %s" % (x.now - t0, st["status"]))
    x.done()


def t_wiring():
    with open(os.path.join(HERE, "relentless.py"), encoding="utf-8") as f:
        src = f.read()
    i = src.index("def wake_enrol():")
    ok("relentless_cause.sweep(" in src[i:src.index("return got", i)], "the wake serve runs the cause sweep")
    with open(W.CONFIG, encoding="utf-8") as f:
        keys = json.load(f)["clock_keys"]
    owed = [k for k, v in keys.items() if v.get("kind") == "backoff_owed"]
    ok(not owed, "no clock key is still owed a cause wake: %r" % owed)
    for k in ("breaker_cool_s", "breaker_cool_max_s", "snag_again_wait_h", "unmeasured_recheck_s"):
        ok(keys.get(k, {}).get("kind") == "cause_cap", "%s is a cap over the cause sweep" % k)


def main():
    for t in (t_breaker_clone_exists, t_breaker_publickey, t_breaker_unclassified, t_snag_repeat, t_start_refusal,
              t_recheck, t_recheck_through_verdict, t_wiring):
        print("--", t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_relentless_cause_close: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
