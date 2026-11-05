#!/usr/bin/env python3
"""Selftest: `relentless.py hold` (RELENTLESS_HOLD_BUILD_A_VERB_FOR_CONDUCTOR).

    python3 src/RimMandrake/rimflow/selftest_relentless_hold_verb.py

Pins:
  * a candidate held keeps its candidate, is never checked while held, and unhold sends the SAME sha to its check;
  * a running item held is fenced (its worker's beat is refused) and settles to held, not queued; unhold re-queues it;
  * a queued item held launches no worker; a held, checking or unknown item refuses a second hold;
  * the hold is the seat's own act: no ledger note is routed back to the seat, no strike is counted;
  * the CLI refuses a hold without --owner-said or the Conductor ruling, and holds with either.
Runs on selftest_relentless's FakeWorld and a throwaway store; no ledger of the repo is touched.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import selftest_relentless as T         # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def to_candidate(x, i, sha="sha1"):
    x.run_one(i)
    st = x.st(i)
    R.contract(x.s, i, st["gen"], "run the test", live="once: test")
    R.finish(x.s, i, st["gen"], sha, "evidence")
    x.w.up[st["run"]["unit"]] = False


def refused(fn):
    try:
        fn()
    except ValueError as e:
        return str(e)
    return None


def t_candidate():
    x = T.Rig(n=1, share=1.0)
    to_candidate(x, "I0")
    ok(x.st("I0")["status"] == "candidate", "setup: I0 is a candidate")
    was = R.hold(x.s, "I0", "PER RULING X: Conductor: hold it", now=x.now)
    st = x.st("I0")
    ok(was == "candidate" and st["status"] == "held" and st["hold"]["kind"] == R.MANUAL_HOLD,
       "a held candidate reads held, kind manual")
    ok((st.get("candidate") or {}).get("sha") == "sha1", "the candidate (sha) is kept")
    ok(not R.hold_is_his(st["hold"]), "a manual hold is the seat's, never needs=owner")
    checks = len(x.w.launches)
    notes = len(getattr(x.w, "notes", []) or [])
    for _ in range(5):
        x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and not st.get("check") and len(x.w.launches) == checks,
       "five ticks: still held, no check and no worker launched")
    ok(len(getattr(x.w, "notes", []) or []) == notes, "no ledger note is routed back to the seat that held it")
    ok(st["total_failures"] == 0 and not st["failures"], "a hold counts no strike")
    ok(refused(lambda: R.hold(x.s, "I0", "again")) and "held already" in refused(lambda: R.hold(x.s, "I0", "again")),
       "a second hold is refused")
    R.unhold(x.s, "I0", "go on", now=x.now)
    st = x.st("I0")
    ok(st["status"] == "candidate" and st["candidate"]["sha"] == "sha1" and not st["hold"],
       "unhold sends the same sha back to its check")
    for _ in range(4):
        x.tick()
        if x.st("I0").get("check") or x.st("I0")["status"] in ("checking", "closing", "done"):
            break
    st = x.st("I0")
    ok(st.get("check") or st["status"] in ("checking", "closing", "done"), "after unhold the check runs: %s" % st["status"])
    x.done()


def t_running():
    x = T.Rig(n=1, share=1.0)
    x.run_one("I0")
    st = x.st("I0")
    g, unit = st["gen"], st["run"]["unit"]
    was = R.hold(x.s, "I0", "Conductor: stop it", now=x.now)
    st = x.st("I0")
    ok(was == "running" and st["status"] == "stopping" and st["gen"] == g + 1, "a running item held is fenced")
    try:
        R.beat(x.s, "I0", g)
        ok(False, "the fenced worker's beat is refused")
    except R.Fenced:
        ok(True, "the fenced worker's beat is refused")
    for _ in range(6):
        x.tick()
        if x.st("I0")["status"] != "stopping":
            break
        x.w.up[unit] = False
    st = x.st("I0")
    ok(st["status"] == "held" and st["hold"]["kind"] == R.MANUAL_HOLD, "it settles to held: %s" % st["status"])
    launches = len(x.w.launches)
    for _ in range(4):
        x.tick()
    ok(x.st("I0")["status"] == "held" and len(x.w.launches) == launches, "held: no new worker")
    R.unhold(x.s, "I0", "go on", now=x.now)
    ok(x.st("I0")["status"] == "queued", "unhold of a held running item re-queues it")
    x.done()


def t_queued_and_refusals():
    x = T.Rig(n=2, share=1.0, max_workers=1)
    x.tick()
    sts = {s["item"]: s for s in x.s.states()}
    q = next((i for i, s in sts.items() if s["status"] == "queued"), None)
    if q is None:
        ok(False, "setup: a queued item exists: %s" % {i: s["status"] for i, s in sts.items()})
        x.done()
        return
    R.hold(x.s, q, "hold the queued one", now=x.now)
    x.r["max_workers"] = 2      # a place is free for it now
    for _ in range(4):
        x.tick()
    ok(x.st(q)["status"] == "held" and not x.st(q).get("run"), "a held queued item launches no worker with a place free")
    R.unhold(x.s, q, "go on", now=x.now)
    x.run_one(q)
    ok(x.st(q)["status"] == "running", "control: unheld, the same place launches it")
    with x.s.lock():
        st = x.s.load(q)
        st["status"] = "checking"
        x.s.save(st)
    ok("a check is running" in (refused(lambda: R.hold(x.s, q, "x")) or ""), "a checking item is refused")
    ok("not in the Relentless store" in (refused(lambda: R.hold(x.s, "NOPE", "x")) or ""), "an unknown item is refused")
    ok("needs a why" in (refused(lambda: R.hold(x.s, q, " ")) or ""), "an empty why is refused")
    x.done()


def t_cli():
    x = T.Rig(n=1, share=1.0)
    to_candidate(x, "I0")
    env = dict(os.environ, RELENTLESS_ROOT=x.d)
    cli = os.path.join(HERE, "relentless.py")
    bare = subprocess.run([sys.executable, cli, "hold", "I0", "--why", "mine"], capture_output=True,
                          text=True, env=env, timeout=60)
    ok(bare.returncode == 2 and "hold needs --owner-said" in bare.stderr,
       "the CLI refuses a bare --why: %d %s" % (bare.returncode, bare.stderr.strip()[-160:]))
    ok(R.Store(x.d).load("I0")["status"] == "candidate", "a refused hold leaves the candidate as it was")
    good = subprocess.run([sys.executable, cli, "hold", "I0", "--per-ruling",
                           "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM", "--why", "Conductor: hold it"],
                          capture_output=True, text=True, env=env, timeout=60)
    st = R.Store(x.d).load("I0")
    ok(good.returncode == 0 and st["status"] == "held" and "PER RULING" in st["hold"]["why"],
       "the CLI holds with the Conductor ruling: %d %s" % (good.returncode, (good.stderr or good.stdout).strip()[-160:]))
    x.done()

if __name__ == "__main__":
    for t in (t_candidate, t_running, t_queued_and_refusals, t_cli):
        t()
    print("%d failure(s)" % len(FAILS))
    sys.exit(1 if FAILS else 0)
