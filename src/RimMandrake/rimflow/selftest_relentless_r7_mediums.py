#!/usr/bin/env python3
"""RELENTLESS_REVIEW_FIX_R7_MEDIUMS_MAY_STAY: the graded r7 review's non-high findings that held, each row red without its
fix. The two it rejected are reasoned in infrastructure/state/items/RELENTLESS_REVIEW_FIX_R7_MEDIUMS_MAY_STAY.md."""
import os
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                  # noqa: E402
import relentless_prooflines as PL      # noqa: E402
import selftest_relentless as T         # noqa: E402
import selftest_relentless_resume as SR  # noqa: E402

FAILS = []
LOST = {"why": "the account ran dry", "kind": "usage_limit", "session": "sess-1"}


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def retire_with(lease, state="ready", job=False):
    """One queued item never started here, the ledger holding `lease`. -> its status after retire()."""
    x = T.Rig(n=1, share=1.0, max_workers=0)
    try:
        x.tick()
        with x.s.lock():
            cur = x.s.load("I0")
            cur.update(status="queued", ledger_started=False, start_intent=False)
            if job:
                cur["proof_lines"] = {"at": x.now}
            x.s.save(cur)
        if job:
            ok(PL.is_job(x.s.load("I0")), "the rig holds a proof-lines job")
        led = {"state": state, "lease": lease(x.now) if lease else None, "owner": "BENCH", "needs": "offline"}
        fx = types.SimpleNamespace(item_state=lambda i: led)
        R.retire(x.s, fx, x.s.states(), x.now, [], x.r)
        return x.s.load("I0")["status"]
    finally:
        x.done()


def t_retire_reads_a_live_lease():
    """retire() took any recorded lease for a seat holding the item, where enrolment reads lease_live."""
    lapsed = lambda now: {"expires": R.iso(now - 3600)}         # noqa: E731
    released = lambda now: {"expires": R.iso(now + 3600), "released": True}     # noqa: E731
    live = lambda now: {"expires": R.iso(now + 3600)}           # noqa: E731
    ok(retire_with(lapsed) == "queued", "an expired lease does not retire a queued item")
    ok(retire_with(released) == "queued", "a released lease does not retire a queued item")
    ok(retire_with(live) == "retired", "control: a live lease still retires it, a seat took it")
    ok(retire_with(None) == "queued", "control: no lease, a proposed or ready item stays")
    ok(retire_with(lapsed, state="built", job=True) == "queued", "an expired lease does not retire a proof-lines job")
    ok(retire_with(live, state="built", job=True) == "retired", "control: a live lease retires a proof-lines job")


def t_check_resume_gets_a_new_deadline():
    """A checker resumed past its deadline did work no verdict could record."""
    real = R.tree_present
    R.tree_present = lambda p: True
    x = T.Rig(n=1, share=1.0, same_failure_limit=5)
    try:
        SR.to_check(x)
        with x.s.lock():
            cur = x.s.load(SR.ITEM)
            cur["check"]["resume"] = {"session": SR.SID, "at": x.now}
            cur["check"]["deadline"] = x.now - 7200
            x.s.save(cur)
        acts = []
        R.check_resume(x.s, x.w, x.r, SR.ITEM, x.now, acts)
        chk = x.st(SR.ITEM)["check"]
        ok(chk.get("resumed") == SR.SID, "the rig resumes the checker: %s" % acts)
        ok(chk["deadline"] == x.now + x.r["check_max_s"] + x.r["launch_grace_s"], "the resumed checker has the time it was given")
        ok(R.past_deadline(chk, x.now + x.r["check_max_s"]) is None, "its answer inside that time is not late")
        ok(R.past_deadline(chk, chk["deadline"] + 1), "control: an answer past the new deadline is still late")
    finally:
        x.done()
        R.tree_present = real


def t_quarantine_holds_a_wanted_consult():
    """quarantine() promises no consult starts until a ruling; help_step() only looked at ended and retiring items."""
    x = T.Rig(n=1, share=1.0, max_workers=0, circling=T.HELP)
    real = R.help_start
    started = []
    R.help_start = lambda store, fx, r, item, now, acts: started.append(item)
    try:
        x.tick()
        old = x.now - 10 * x.r["circling"]["help_wait_s"]
        with x.s.lock():
            cur = x.s.load("I0")
            cur["status"] = "held"
            cur["hold"] = {"why": "quarantine", "kind": R.QUARANTINE, "at": x.now, "back": "queued", "under": None}
            cur["help"] = {"status": "wanted", "why": "stuck", "by": "worker", "at": old, "tries": 0, "gen": cur["gen"], "round": 1}
            x.s.save(cur)
        acts = []
        R.help_step(x.s, x.w, x.r, "I0", x.now, acts)
        ok(not started, "a quarantined item's wanted consult does not start")
        ok(x.st("I0")["help"]["status"] == "wanted", "it stays wanted for after the ruling")
        ok(x.st("I0")["help"]["at"] == x.now, "its wait for room starts over, so the quarantine reads as no failed consult")
        with x.s.lock():
            cur = x.s.load("I0")
            cur["hold"] = None
            cur["status"] = "queued"
            x.s.save(cur)
        R.help_step(x.s, x.w, x.r, "I0", x.now, [])
        ok(started == ["I0"], "control: with no hold the consult starts")
    finally:
        R.help_start = real
        x.done()


def cut_pilot(x):
    """I0's pilot step is sitting in the run the account cuts, its session resumable."""
    x.run_one("I0")
    st = x.st("I0")
    x.w.up[st["run"]["unit"]] = False
    with x.s.lock():
        cur = x.s.load("I0")
        cur["pilot_step"] = {"at": 1, "after": 2, "class": "game_fail", "sat_gen": cur["gen"]}
        x.s.save(cur)
        R.account_lost(x.s, cur, LOST, x.r, x.now)
    return x.st("I0")


def t_cut_pilot_never_resumes_as_a_builder():
    """The cut pilot's session came back as a builder: the worker agent, its sitting read as stale, the step still owed."""
    x = T.Rig(n=1, share=1.0, max_workers=1)
    try:
        cut_pilot(x)
        x.run_one("I0")
        st = x.st("I0")
        ok(x.w.launches[-1][3] == x.r["pilot_agent"], "the resumed session runs as the pilot: %s" % x.w.launches[-1][3])
        ok(st["run"].get("resume") == "sess-1", "and it is the session the account cut, nothing read twice")
        ok(R.piloting(st) and st["pilot_step"]["sat_gen"] == st["gen"], "its sitting is this generation's")
        ok(x.s.attempts("I0")[-1].get("pilot_step") is True, "the start is recorded as the pilot step")
    finally:
        x.done()
    x = T.Rig(n=1, share=1.0, max_workers=1)
    try:
        cut_pilot(x)
        with x.s.lock():            # something moved the lease between the cut and the next launch (a hold, a fence)
            cur = x.s.load("I0")
            cur["gen"] += 1
            x.s.save(cur)
        x.run_one("I0")
        st = x.st("I0")
        ok(x.w.launches[-1][3] == x.r["pilot_agent"], "a stale resume leaves a fresh pilot, the step still owed")
        ok(not st["run"].get("resume"), "and that fresh pilot resumes nothing")
        ok(st["pilot_step"]["sat_gen"] == st["gen"], "and it is the one sitting the step")
    finally:
        x.done()


def main():
    for t in (t_retire_reads_a_live_lease, t_check_resume_gets_a_new_deadline, t_quarantine_holds_a_wanted_consult,
              t_cut_pilot_never_resumes_as_a_builder):
        print("--", t.__name__)
        t()
    # the sibling item RELENTLESS_R7_FIX_THIRTEEN_MEDIUMS_MAY_STAY: its rows live in their own file, run from here too
    print("-- selftest_relentless_r7_thirteen")
    run = subprocess.run([sys.executable, os.path.join(HERE, "selftest_relentless_r7_thirteen.py")], capture_output=True,
                         text=True, timeout=120)
    print(run.stdout[-1500:])
    ok(run.returncode == 0, "the thirteen mediums' rows pass")
    print("selftest_relentless_r7_mediums: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
