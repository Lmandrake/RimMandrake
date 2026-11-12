#!/usr/bin/env python3
"""A Marker that dies at start writes its reason to .err and nothing to .json. On 2026-11-03 thirty such deaths (EACCES
under its own wall) read as checker_lost and raised no alarm (CHECKER_DEATH_MONITOR_THIRTY_QUIET_FUNERALS). Now the
.err text charges the launch breaker, so repeats open it and one cause opened twice is the emergency; the item is not
struck for the launcher's fault. Engine rows run the real tick on selftest_relentless's rig; reader rows read files."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import selftest_relentless as T         # noqa: E402
from selftest_relentless_account_lost import to_check   # noqa: E402

FAILS = []
EACCES = "Error: EACCES: permission denied, mkdir '/home/mandrake/.seat-tmp/runs/rm-relentless-check-x'"


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def t_reader():
    d = tempfile.mkdtemp(prefix="rl-death-")
    out, err = os.path.join(d, "u.json"), os.path.join(d, "u.err")
    run = {"out": out, "err": err}
    ok(R.death_note(run) is None, "no files: nothing to say (a plain lost run)")
    open(out, "w").close()
    with open(err, "w") as f:
        f.write("   \n")
    ok(R.death_note(run) is None, "an empty .json and a blank .err: nothing to say")
    with open(err, "w") as f:
        f.write("noise\n" * 100 + EACCES + "\n")
    got = R.death_note(run)
    ok(got == ("noise\n" * 100 + EACCES).strip(), "an empty .json and .err text: the whole .err is the note (no 300 cut)")
    with open(out, "w") as f:
        json.dump({"result": "done", "is_error": False}, f)
    ok(R.death_note(run) is None, "a result object on .json: the run spoke, stderr is not its death")
    ok(R.Effects.death_note(None, run) is None and R.death_note(None) is None, "the real effect reads the same; no run, None")
    shutil.rmtree(d, ignore_errors=True)


def t_engine_charges_the_breaker():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=0)
    to_check(x)
    deaths = 0
    for _ in range(12):     # past same_failure_limit and launch_breaker both
        st = x.st("I0")
        if st["status"] != "checking":
            for _ in range(4):
                x.tick()
                if x.st("I0")["status"] == "checking":
                    break
            st = x.st("I0")
        if st["status"] != "checking":
            break
        was = st
        x.w.death_err = EACCES
        x.w.up[st["check"]["run"]["unit"]] = False
        acts = x.tick(30)
        st = x.st("I0")
        deaths += 1
        ok(not st.get("check_lost") and not st["failures"].get("checker_lost") and st["total_failures"] == was["total_failures"]
           and st["gen"] == was["gen"] and st["candidate"], "death %d: no checker_lost count, no strike, the candidate stands" % deaths)
        a = x.s.attempts("I0")[-1]
        ok(a["end"] == "check_launch_fail" and EACCES in a.get("detail", ""), "death %d: recorded with the .err text" % deaths)
        ok(any(z.get("do") == "check_launch_fail" for z in acts or []),
           "death %d: told in the tick's acts" % deaths)
        x.w.death_err = None
        if R.load_breaker(x.s).get("until", 0) > x.now:
            break
    br = R.load_breaker(x.s)
    ok(deaths == x.r["launch_breaker"], "the breaker opens on the %dth death (%d)" % (x.r["launch_breaker"], deaths))
    ok(br.get("until", 0) > x.now and EACCES in br.get("why", ""), "it opens, quoting the .err: %s" % br.get("why"))
    opens = list((br.get("opens") or {}).values())
    ok(len(opens) == 1 and opens[0]["n"] == 1, "one cause, counted once toward the same-cause emergency: %s" % opens)
    x.done()


def t_plain_loss_still_counts():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=0)
    st = to_check(x)
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick(30)
    st = x.st("I0")
    ok(st.get("check_lost") == 1 and not R.load_breaker(x.s).get("fails"), "no .err text: checker_lost counts as before, no breaker")
    x.done()


def t_stopped_at_the_limit_is_not_a_death():
    x = T.Rig(n=1, share=1.0, same_failure_limit=2, account_settle_s=0)
    st = to_check(x)
    x.w.death_err = "Terminated"
    x.now += x.r["check_max_s"] + x.r["launch_grace_s"]
    x.tick(30)
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick(30)
    st = x.st("I0")
    ok(st.get("check_lost") == 1 and not R.load_breaker(x.s).get("fails"),
       "a checker stopped at check_max_s with .err text is a lost check, not a launch failure")
    x.done()


def t_emergency_on_repeat():
    """Two opens on the cause inside the window is breaker_emergency's: the death's why keys one cause across runs."""
    a = "checker rm-relentless-check-aaaa-g1 died with no output: " + EACCES
    b = "checker rm-relentless-check-bbbbbbbb-g7 died with no output: " + EACCES.replace("check-x", "check-y")
    ok(R.cause_key(a) == R.cause_key(b), "two Markers' deaths are one cause to the breaker")


if __name__ == "__main__":
    for t in (t_reader, t_engine_charges_the_breaker, t_plain_loss_still_counts, t_stopped_at_the_limit_is_not_a_death,
              t_emergency_on_repeat):
        t()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
