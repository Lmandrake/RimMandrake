#!/usr/bin/env python3
"""A run the account killed charges the item nothing; an ordinary lost run still strikes
(RELENTLESS_STRIKES_FIX_EMPTY_ACCOUNT_BLAMED). Engine rows run the real tick on selftest_relentless's rig; sign rows read
fixture files in the shapes measured on 2026-11-03 (~/.claude-accounts/log.jsonl, a transcript's API error record)."""
import datetime
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import relentless_account as A          # noqa: E402
import selftest_relentless as T         # noqa: E402

FAILS = []
OVER = {"kind": "change_over", "why": "account change-over at T closed every Claude process"}
EMPTY = {"kind": "account_error", "why": "the run ended on the account's own error: rate_limit"}


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def epoch(ts):
    return datetime.datetime.fromisoformat(ts).timestamp()


def worker_dies(x, sign, beat=True):
    """I0 running with a measured spend, then dead with no receipt, past the launch grace."""
    x.run_one("I0")
    st = x.st("I0")
    if beat:
        R.beat(x.s, "I0", st["gen"], now=x.now)
    x.w.tok = 500
    x.w.account_sign = sign
    x.w.up[st["run"]["unit"]] = False
    return st


def untouched(st, was, name):
    ok(st["failures"] == was["failures"] and st["total_failures"] == was["total_failures"], name + ": no strike")
    ok(st["returns"] == was["returns"], name + ": no return")
    ok(st["approach"] == was["approach"] and st["approach_changes"] == was["approach_changes"], name + ": approach kept")
    ok(st["gen"] == was["gen"] + 1, name + ": the dead worker is fenced")
    ok(st["clone"] == was["clone"] and st["clone"], name + ": its clone stays, uncommitted work and all")
    ok(st["status"] != "held" and not st["hold"], name + ": not held")


def t_change_over_and_empty_charge_nothing():
    for sign, name in ((OVER, "change-over"), (EMPTY, "empty account")):
        x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=240, max_workers=1)
        was = worker_dies(x, sign)
        x.r["max_workers"] = 0          # hold the next worker back: the state read is the one the death left
        x.tick(30)
        st = x.st("I0")
        untouched(st, was, name)
        ok(st["status"] == "queued" and st["run"] is None, name + ": back in line")
        a = x.s.attempts("I0")[-1]
        ok(a["end"] == "account_lost" and "approach_next" not in a, name + ": recorded, and no approach")
        ok(R.failed_approaches(x.s, "I0") == [], name + ": off the approach list")
        ok(x.s.load("I0").get("spent", 0) >= 500, name + ": what it spent stays charged")
        x.done()


def t_breaker_only_for_empty():
    x = T.Rig(n=1, share=1.0, max_workers=1)
    worker_dies(x, EMPTY)
    x.r["max_workers"] = 0
    x.tick(30)
    ok(R.load_breaker(x.s).get("fails") == 1, "an empty account counts on the launch breaker")
    x.done()
    x = T.Rig(n=1, share=1.0, max_workers=1)
    worker_dies(x, OVER)
    x.r["max_workers"] = 0
    x.tick(30)
    ok(not R.load_breaker(x.s).get("fails"), "a change-over does not: the login works")
    x.done()


def t_many_change_overs_never_flip():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, max_workers=1)
    was = None
    for _ in range(4):
        st = worker_dies(x, OVER)
        was = was or st
        x.tick(30)
        ok(x.st("I0")["status"] != "stopping", "a change-over goes straight back")
    st = x.st("I0")
    ok(st["approach"] == was["approach"] and st["approach_changes"] == 0 and not st["failures"].get("worker_lost"),
       "four change-overs leave the approach and the strikes alone (limit 2)")
    x.done()


def t_ordinary_death_still_strikes():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=240, max_workers=1)
    was = worker_dies(x, None)
    x.r["max_workers"] = 0
    x.tick(30)
    ok(x.st("I0")["status"] == "running" and not x.st("I0")["failures"].get("worker_lost"),
       "no sign yet: it waits out the switch's own minutes before striking")
    x.tick(120)
    ok(x.st("I0")["status"] == "running", "still inside account_settle_s")
    x.tick(120)
    st = x.st("I0")
    ok(st["failures"].get("worker_lost") == 1 and st["total_failures"] == was["total_failures"] + 1,
       "past account_settle_s with no sign: worker_lost, one strike")
    x.done()
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=240, max_workers=1)
    was = worker_dies(x, None)
    x.r["max_workers"] = 0
    x.tick(30)
    x.w.account_sign = OVER         # the event lands while it waits: the race this wait exists for
    x.tick(60)
    untouched(x.st("I0"), was, "an event that lands during the wait")
    x.done()


def t_shipped_wait_outlasts_a_switch():
    shipped = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    ok(shipped["account_settle_s"] >= 21 + 90, "the shipped wait outlasts claude-account's stop (21 s) and verify (90 s)")


def t_receipt_beats_sign():
    x = T.Rig(n=1, share=1.0, account_settle_s=240, max_workers=1)
    was = worker_dies(x, None)
    R.contract(x.s, "I0", was["gen"], "proof", live="once: test")
    x.tick(30)
    ok(x.st("I0")["status"] == "running", "dead with no receipt: it waits")
    R.finish(x.s, "I0", was["gen"], "sha1", "evidence")
    x.w.account_sign = OVER
    x.tick(30)
    st = x.st("I0")
    ok(st["status"] != "queued" and st["candidate"] and not st["failures"].get("worker_lost"),
       "a finish that lands during the wait is taken: a receipt outranks any sign (%s)" % st["status"])
    x.done()


def t_launch_fail_unchanged():
    x = T.Rig(n=1, share=1.0, max_workers=1)
    worker_dies(x, OVER, beat=False)
    x.w.tok = None
    x.r["max_workers"] = 0
    x.tick(30)
    ok(x.s.attempts("I0")[-1]["end"] == "launch_fail", "dead at once with nothing spent is still a launch failure")
    x.done()


def to_check(x):
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "proof", live="once: test")
    R.finish(x.s, "I0", st["gen"], "sha1", "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "checking", "the rig reaches the checker")
    return st


def t_checker_killed_counts_nothing():
    for sign, name in ((OVER, "change-over"), (EMPTY, "empty account")):
        x = T.Rig(n=1, share=1.0, same_failure_limit=2)
        for _ in range(3):      # past the limit of 2, which would be a checker_lost strike
            st = to_check(x) if x.st("I0") is None or x.st("I0")["status"] != "checking" else x.st("I0")
            was = st
            x.w.account_sign = sign
            x.w.up[st["check"]["run"]["unit"]] = False
            x.tick(30)
            st = x.st("I0")
            ok(st.get("check_lost", 0) == 0 and not st["failures"].get("checker_lost") and st["gen"] == was["gen"],
               name + ": a killed checker counts nothing and fences nothing")
            ok(st["status"] == "candidate" or st["status"] == "checking", name + ": the candidate stands (%s)" % st["status"])
            if x.s.attempts("I0")[-1]["end"] != "account_lost":
                ok(False, name + ": recorded")
            x.w.account_sign = None
            R.launch_ok(x.s)      # the breaker has its own row
            for _ in range(3):
                if x.st("I0")["status"] == "checking":
                    break
                x.tick()
            ok(x.st("I0")["status"] == "checking", name + ": a new checker runs")
        x.done()
    x = T.Rig(n=1, share=1.0, same_failure_limit=2)
    st = to_check(x)
    x.w.account_sign = None
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick(30)
    ok(x.st("I0").get("check_lost") == 1, "a checker lost with no sign still counts")
    x.done()


def real_signs(x, log):
    """The rig's account sign replaced by the real reader on a log this test writes."""
    x.w.account_loss = lambda run, clone, since, box=None: A.loss(run, clone, since, log, box)


def kill_checker(x):
    st = x.st("I0")
    if st["status"] != "checking":
        for _ in range(3):
            x.tick()
            if x.st("I0")["status"] == "checking":
                break
        st = x.st("I0")
    ok(st["status"] == "checking", "a checker runs")
    x.w.up[st["check"]["run"]["unit"]] = False
    return st


def t_checker_event_lands_after_it_is_found_dead():
    """claude-account logs op=use once the fleet is back up (stop 21 s, verify 90 s): the tick that finds the checker dead
    usually comes first. Limit 2, three change-overs in a row: the shipped order of events, on the real reader."""
    d = tempfile.mkdtemp(prefix="rl-acct-")
    log = os.path.join(d, "log.jsonl")
    open(log, "w").close()
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=240)
    real_signs(x, log)
    was = to_check(x)
    for n in range(3):
        kill_checker(x)
        for dt in (30, 90):
            x.tick(dt)
            st = x.st("I0")
            ok(st["status"] == "checking" and not st.get("check_lost"), "round %d, +%d s: no event yet, it waits" % (n, dt))
        with open(log, "a") as f:
            f.write(json.dumps({"op": "use", "changed": True, "ts": R.iso(x.now)}) + "\n")
        x.tick(30)
        st = x.st("I0")
        ok(x.s.attempts("I0")[-1]["end"] == "account_lost", "round %d: the late event clears it" % n)
        ok(st["failures"] == was["failures"] and st["total_failures"] == was["total_failures"] and st["returns"] == was["returns"]
           and st["gen"] == was["gen"] and not st.get("check_lost"), "round %d: nothing added, nothing carried over" % n)
        ok(st["candidate"] and st["approach"] == was["approach"], "round %d: the candidate and the approach stand" % n)
    x.done()
    shutil.rmtree(d, ignore_errors=True)


def t_checker_no_sign_strikes_after_the_wait():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=240)
    was = to_check(x)
    for n, then in ((1, lambda st: st.get("check_lost") == 1 and st["status"] == "candidate"),
                    (2, lambda st: st["failures"].get("checker_lost") == 1 and st["total_failures"] == was["total_failures"] + 1)):
        kill_checker(x)
        x.tick(30)
        x.tick(120)
        st = x.st("I0")
        ok(st.get("check_lost", 0) == n - 1 and not st["failures"].get("checker_lost"), "checker %d: inside the wait nothing is counted" % n)
        x.tick(120)
        ok(then(x.st("I0")), "checker %d: past account_settle_s with no sign it counts, each waiting its own" % n)
    x.done()


def t_checker_verdict_never_waits():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=240)
    st = to_check(x)
    R.verdict(x.s, "I0", st["check"]["nonce"], "FAIL", "broken", x.now)
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick(30)
    ok(x.st("I0")["failures"].get("blind_fail") == 1, "a checker that gave its verdict is judged at once: the wait is for no word only")
    x.done()


def t_walled_checker_transcript():
    """A walled checker's ~/.claude/projects is its box's (relentless_wall.props), not the one its clean clone maps to."""
    d = tempfile.mkdtemp(prefix="rl-acct-")
    absent = os.path.join(d, "no-log")
    box = os.path.join(d, "box")
    home = os.path.join(box, "projects", "-box-tree")
    os.makedirs(home)
    err = {"type": "assistant", "isApiErrorMessage": True, "error": "rate_limit", "message": {"content": []}}
    path = os.path.join(home, "s.jsonl")
    with open(path, "w") as f:
        f.write(json.dumps(err) + "\n")
    shipped = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    prof = R.relentless_wall.profile(shipped, "marker")
    ok(prof and any(a.startswith("BindPaths=%s:" % os.path.join(box, "projects")) for a in R.relentless_wall.props(prof, box)),
       "the wall binds the very folder this sign reads")
    os.utime(path, (2000, 2000))
    run = {"at": 1000, "out": None}
    ok(A.loss(run, "/nowhere/clean", 1000, absent) is None, "looking under the clean clone sees nothing: the reason for the box")
    got = A.loss(run, "/nowhere/clean", 1000, absent, box)
    ok(got and got["kind"] == "account_error" and "rate_limit" in got["why"], "the box's transcript speaks for a walled checker")
    os.utime(path, (500, 500))
    ok(A.loss(run, "/nowhere/clean", 1000, absent, box) is None, "a transcript older than the run says nothing")
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=240)
    real_signs(x, absent)
    st = to_check(x)
    with x.s.lock():
        cur = x.s.load("I0")
        cur["check"]["box"] = box
        x.s.save(cur)
    os.utime(path, (x.now + 5, x.now + 5))
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick(30)
    ok(x.s.attempts("I0")[-1]["end"] == "account_lost", "the engine hands the checker's box to the reader")
    ok(not x.st("I0").get("check_lost") and not x.st("I0")["failures"].get("checker_lost"), "so a walled checker on an empty account counts nothing")
    x.done()
    shutil.rmtree(d, ignore_errors=True)


def t_real_effects_reach_the_log():
    d = tempfile.mkdtemp(prefix="rl-acct-")
    log = os.path.join(d, "log.jsonl")
    with open(log, "w") as f:
        f.write(json.dumps({"op": "use", "changed": True, "ts": "2026-11-01T17:37:52-08:00"}) + "\n")
    old, A.ACCOUNT_LOG = A.ACCOUNT_LOG, log
    try:
        got = R.Effects.account_loss(None, {"at": epoch("2026-11-01T17:29:00-08:00"), "out": None}, None, 0)
    finally:
        A.ACCOUNT_LOG = old
    ok(got and got["kind"] == "change_over", "the engine's real effects read the account log")
    ok(os.path.expanduser(A.ACCOUNT_LOG).startswith(os.path.expanduser("~")), "the real log path is the machine's own")
    shutil.rmtree(d, ignore_errors=True)


def t_signs():
    d = tempfile.mkdtemp(prefix="rl-acct-")
    log = os.path.join(d, "log.jsonl")
    rows = [{"op": "capture", "acct": "a", "ts": "2026-11-01T20:18:12-08:00"},
            {"op": "use", "from": "a", "to": "b", "changed": True, "stopped": 8, "ts": "2026-11-01T17:37:52-08:00"},
            {"op": "warm", "ts": "2026-11-03T11:15:47-08:00"}]
    with open(log, "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in rows))
    use = epoch("2026-11-01T17:37:52-08:00")
    # the two real deaths of 2026-11-02T01:40:23Z: units launched 17:29 and 16:59 local (the files' own times)
    for started in ("2026-11-01T17:29:00-08:00", "2026-11-01T16:59:00-08:00"):
        ok(bool(A.change_over(epoch(started), log)), "replay: a worker started %s reads as the change-over" % started)
    ok(A.change_over(use + 1, log) is None, "a worker launched after the event is not its victim")
    ok(A.change_over(use, log) is None, "the instant of the event is not after it")
    ok(A.change_over(0, os.path.join(d, "absent")) is None, "no log, no sign")
    noop = os.path.join(d, "noop.jsonl")
    with open(noop, "w") as f:
        f.write(json.dumps({"op": "use", "changed": False, "ts": "2026-11-01T17:37:52-08:00"}) + "\n")
    ok(A.change_over(0, noop) is None, "a switch to the live account closes nothing: changed false is no sign")
    ok("b" not in A.change_over(0, log).replace("Claude", "").replace("closed", "").replace("by", ""), "the reason names no account")

    def tx(name, *recs):
        p = os.path.join(d, name)
        with open(p, "w") as f:
            f.write("".join(json.dumps(r) + "\n" for r in recs))
        return p
    err = {"type": "assistant", "isApiErrorMessage": True, "error": "rate_limit",
           "message": {"stop_reason": "stop_sequence", "content": [{"type": "text", "text": "You've hit your weekly limit"}]}}
    auth = dict(err, error="authentication_failed")
    srv = dict(err, error="server_error")
    work = {"type": "assistant", "message": {"content": []}}
    user = {"type": "user", "message": {"content": "go on"}}
    ok(A.transcript_error([tx("a", work, err)]) == "rate_limit", "a transcript ending on the limit is the account's")
    ok(A.transcript_error([tx("b", work, auth)]) == "authentication_failed", "so is one ending on a dead login")
    ok(A.transcript_error([tx("c", work, srv)]) is None, "a service error is not the account's")
    ok(A.transcript_error([tx("d", err, user, work)]) is None, "an error the run went on past did not end it")
    ok(A.transcript_error([tx("e", work, err, {"type": "system"}, {"type": "last-prompt"})]) == "rate_limit",
       "bookkeeping records after the error do not hide it")
    ok(A.transcript_error([tx("f", work, dict(err, isSidechain=True))]) is None, "a subagent's error did not end the run")
    ok(A.transcript_error([]) is None, "no transcripts, no sign")
    old, new = tx("g", work, err), tx("h", work)
    os.utime(old, (1000, 1000))
    ok(A.transcript_error([old, new]) is None, "only the newest transcript speaks")
    big = tx("i", {"type": "user", "pad": "x" * (A.TAIL + 500)}, work, err)
    ok(A.transcript_error([big]) == "rate_limit", "a long transcript reads from its tail, torn first line and all")

    def res(name, obj):
        p = os.path.join(d, name)
        with open(p, "w") as f:
            json.dump(obj, f)
        return p
    ok(A.result_error(res("r1", {"is_error": True, "result": "You've hit your session limit · resets 1pm"})), "an error result with the limit words")
    ok(A.result_error(res("r2", {"is_error": True, "result": "Failed to authenticate: OAuth session expired"})), "an error result with the login words")
    ok(A.result_error(res("r3", {"is_error": False, "result": "fixed the usage limit bug"})) is None, "a good result that mentions a limit is no sign")
    ok(A.result_error(res("r4", {"is_error": True, "result": "tool blew up"})) is None, "another error is no sign")
    empty = os.path.join(d, "r5")
    open(empty, "w").close()
    ok(A.result_error(empty) is None and A.result_error(None) is None, "an empty or absent result is no sign")
    ok(A.loss({"at": use - 60, "out": empty}, None, use - 60, log)["kind"] == "change_over", "loss: the change-over")
    ok(A.loss({"at": use + 60, "out": res("r6", {"is_error": True, "result": "Not logged in · Please run /login"})},
              None, use + 60, log)["kind"] == "account_error", "loss: the result")
    ok(A.loss({"at": use + 60, "out": empty}, None, use + 60, log) is None, "loss: neither, so the death strikes")
    ok(A.loss(None, None, None, log) is None, "loss: no run, no start")
    shutil.rmtree(d, ignore_errors=True)


def main():
    picked = sys.argv[1:]
    ran = 0
    for k, t in sorted(globals().items()):
        if k.startswith("t_") and (not picked or k in picked):
            ran += 1
            print("--", k)
            t()
    if not ran:
        print("selftest_relentless_account_lost: FAIL ran none")
        return 1
    print("selftest_relentless_account_lost: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
