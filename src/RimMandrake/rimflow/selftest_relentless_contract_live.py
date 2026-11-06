#!/usr/bin/env python3
"""selftest_relentless_contract_live.py: CONTRACT_LIVE_FIX_MISSED_FLAG_COSTS_RETURNS.

A build worker whose contract lacks --live, and whose work turns out to need one (a hook, unit, schedule or watch
rule), must not be locked out until a redesign: an earlier contract() refused the add, so finished work burned
same_failure_limit returns to reach redesign.
1. contract(): on a build attempt, adding --live with the proof unchanged is allowed (it only asks more); replacing a
   live line already set, or changing the proof, is still refused.
2. finish(): a sha whose paths need a live line the contract lacks is refused at once, naming the contract call that
   fixes it, instead of being taken and returned by the check as bad_candidate. After the add, the same sha finishes.
3. finish(): a sha that touches nothing needing a line, or that the tree cannot read, is not refused here.

Runs on selftest_relentless's FakeWorld plus a throwaway git repo under TMPDIR; no ledger or clone is touched.

    python3 src/RimMandrake/rimflow/selftest_relentless_contract_live.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import selftest_relentless as SR    # noqa: E402

R = SR.R
FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def refused(f):
    try:
        f()
    except ValueError as e:
        return str(e)
    return None


def repo(paths):
    """-> (dir, sha) of a one-commit repo holding `paths`."""
    d = tempfile.mkdtemp(prefix="contract_live_")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    for p in paths:
        os.makedirs(os.path.join(d, os.path.dirname(p)) or d, exist_ok=True)
        with open(os.path.join(d, p), "w") as f:
            f.write("x\n")
    for argv in (["init", "-q", "-b", "main"], ["add", "--", *paths],
                 ["commit", "-q", "-m", "I0: test", "--no-verify"]):
        subprocess.run(["git", *argv], cwd=d, env=env, check=True, capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    return d, sha


def rig():
    x = SR.Rig(n=1, share=1.0)
    x.run_one("I0")
    return x, x.st("I0")["gen"]


def t_build_worker_may_add_live():
    x, g = rig()
    ok(x.st("I0")["approach"] != "redesign", "the rig's attempt is not a redesign: %r" % x.st("I0")["approach"])
    R.contract(x.s, "I0", g, "proof")
    why = refused(lambda: R.contract(x.s, "I0", g, "proof", live="once: t", why="the work touched a hook"))
    ok(why is None and x.st("I0")["contract"].get("live") == "once: t",
       "a build worker adds a missing --live with the same proof: %r" % why)
    why = refused(lambda: R.contract(x.s, "I0", g, "proof", live="once: other", why="swap"))
    ok(why is not None and "only a redesign" in why, "a set live line is not replaced: %r" % why)
    why = refused(lambda: R.contract(x.s, "I0", g, "proof2", live="once: t", why="swap"))
    ok(why is not None and "only a redesign" in why, "a changed proof is still refused: %r" % why)


def t_finish_refuses_then_accepts():
    x, g = rig()
    R.contract(x.s, "I0", g, "proof")
    d, sha = repo(["src/RimMandrake/rimflow/systemd/rm-foo.timer"])
    why = refused(lambda: R.finish(x.s, "I0", g, sha, "e", root=d))
    ok(why is not None and "needs a live line" in why and "contract --item I0" in why and "--live" in why,
       "finish refuses a hook-touching sha without a live line, naming the fix: %r" % why)
    ok(x.st("I0")["status"] != "candidate", "the refused sha is not taken as a candidate")
    R.contract(x.s, "I0", g, "proof", live="once: t", why="the work touched a timer")
    why = refused(lambda: R.finish(x.s, "I0", g, sha, "e", root=d))
    ok(why is None and x.st("I0")["status"] == "candidate", "after the add the same sha finishes: %r" % why)


def t_finish_lets_the_rest_through():
    x, g = rig()
    R.contract(x.s, "I0", g, "proof")
    d, sha = repo(["src/RimMandrake/rimflow/plain.py"])
    why = refused(lambda: R.finish(x.s, "I0", g, sha, "e", root=d))
    ok(why is None, "a sha needing no line finishes without one: %r" % why)
    x, g = rig()
    R.contract(x.s, "I0", g, "proof")
    why = refused(lambda: R.finish(x.s, "I0", g, "f" * 40, "e", root=d))
    ok(why is None, "a sha the tree cannot read is left to the check: %r" % why)


if __name__ == "__main__":
    try:
        t_build_worker_may_add_live()
        t_finish_refuses_then_accepts()
        t_finish_lets_the_rest_through()
    except Exception as e:      # noqa: BLE001  a crash is a FAIL with its reason
        import traceback
        traceback.print_exc()
        FAILS.append("crashed: %s" % e)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
