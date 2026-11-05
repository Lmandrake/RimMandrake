#!/usr/bin/env python3
"""CONTRACT_BINDING_UNTANGLE_WHAT_FROM_HOW: a contract is a versioned obligation (what must be true) and a versioned
binding (scenario, proof, execution location, fixtures, freshness); an independent Setter/Judge may approve a binding
repair that preserves the obligation, read from a before/after comparison; a weakening is refused.

Each row below is one clause of the item:
  O  split: obligation and binding come apart, each hashed and versioned; a redesign alone moves the obligation.
  R  a broken binding is repairable by a NON-redesign worker (the trap behind LEANINGSCRUB, TESTQ_WORKER_MIGRATE,
     DONOR_COATS, GUBBRA): the proposal is recorded, the contract does not move until a judge approves.
  J  the judge is independent: a worker session (RELENTLESS_GEN) and the proposer are refused; approve applies it with
     binding_version + 1 and the obligation hash unchanged; reject drops it; ambiguous keeps it pending and unapplied.
  W  weakening refused: worker-typed numbers, a changed obligation, changed behaviour, a dropped live line / game clause /
     adapter, a blank comparison.
  P  the packet shows the judge the obligation, the binding field by field, before/after and moved thresholds.
"""
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402
import relentless_binding as B  # noqa: E402

FAILS = []
RULES = dict(R.rules(), wall={})    # an unwalled Marker: reach is relentless_reach's own test


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def refused(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def rig(approach="build"):
    base = tempfile.mkdtemp(prefix="bind_")
    s = R.Store(base)
    st = R.new_state("I0", 1000.0, "t")
    st.update(status="running", gen=1, approach=approach)
    with s.lock():
        s.save(st)
    return base, s


GOOD = {"before": "ran selftest_x.py, which no longer exists under that name",
        "after": "runs selftest_x_renamed.py: the same assertions on the same module",
        "behaviour": "same", "defect": "python3: can't open file selftest_x.py (renamed in a1b2c3)"}


def t_split():
    c = {"proof": "python3 a/selftest_x.py", "live": None, "by_gen": 1, "why": None}
    sp = B.split(c, "I0")
    ok(sp["obligation"]["version"] == 1 and "I0" in sp["obligation"]["text"], "O: an old contract's obligation is the item's text, v1")
    ok(sp["binding"] == {"proof": "python3 a/selftest_x.py", "version": 1}, "O: binding holds the proof only, v1")
    c2 = dict(c, proof="python3 a/selftest_y.py")
    ok(B.obligation_hash(c, "I0") == B.obligation_hash(c2, "I0") and B.binding_hash(c) != B.binding_hash(c2),
       "O: a proof change moves the binding hash, never the obligation hash")
    c3 = dict(c, obligation={"text": "the gourd selects", "version": 1})
    ok(B.obligation_hash(c3) != B.obligation_hash(c, "I0") and B.binding_hash(c3) == B.binding_hash(c),
       "O: an obligation change moves the obligation hash, never the binding hash")


def t_contract_fields():
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", obligation="the gourd selects", scenario="offline",
                   fixtures=["a/fx.json"], freshness="same sha", r=RULES)
        c = s.load("I0")["contract"]
        ok(c["obligation"] == {"text": "the gourd selects", "version": 1} and c["fixtures"] == ["a/fx.json"]
           and c["scenario"] == "offline" and c["freshness"] == "same sha", "O: contract records obligation and binding fields")
        e = refused(R.contract, s, "I0", 1, "python3 a/selftest_x.py", obligation="the gourd exists", why="w", r=RULES)
        ok(e is not None and "redesign" in e, "O: a build worker cannot move the obligation: %s" % (e or "")[:80])
        st = s.load("I0")
        st["approach"] = "redesign"
        with s.lock():
            s.save(st)
        R.contract(s, "I0", 1, "python3 a/selftest_y.py", obligation="the gourd selects and stacks", why="redesign", r=RULES)
        c = s.load("I0")["contract"]
        ok(c["obligation"]["version"] == 2 and c["binding_version"] == 2, "O: a redesign moves the obligation (v2) and binding (v2)")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_rebind_and_judge():
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", obligation="the gourd selects", r=RULES)
        e = refused(R.contract, s, "I0", 1, "python3 a/selftest_x_renamed.py", why="renamed", r=RULES)
        ok(e is not None, "R: the lock still refuses a plain contract change by a build worker")
        ob0 = B.obligation_hash(s.load("I0")["contract"], "I0")
        pk = R.rebind(s, "I0", 1, {"proof": "python3 a/selftest_x_renamed.py"}, dict(GOOD), r=RULES)
        st = s.load("I0")
        ok(st["binding_proposal"]["binding"]["proof"] == "python3 a/selftest_x_renamed.py"
           and st["contract"]["proof"] == "python3 a/selftest_x.py", "R: a build worker's repair is recorded; the contract waits")
        ok("OBLIGATION v1" in pk and "CHANGED" in pk and "MEASURED BEFORE" in pk and "MEASURES AFTER" in pk,
           "P: the packet shows obligation, the changed field, before and after")
        e = refused(R.bind_judge, s, "I0", "rm-judge", "approve", "same test renamed", env={"RELENTLESS_GEN": "1"}, r=RULES)
        ok(e is not None and "independent" in e, "J: a worker session may not judge")
        e = refused(R.bind_judge, s, "I0", "gen 1 of I0", "approve", "mine", env={}, r=RULES)
        ok(e is not None and ("proposer" in e or "worker of the work" in e), "J: the proposer may not judge its own repair")
        e = refused(R.bind_judge, s, "I0", "rm-judge", "approve", "", env={}, r=RULES)
        ok(e is not None, "J: a ruling with no why is refused")
        out = R.bind_judge(s, "I0", "rm-judge", "ambiguous", "cannot tell if the renamed test asserts the same", env={}, r=RULES)
        st = s.load("I0")
        ok("AMBIGUOUS" in out and st.get("binding_proposal") and st["contract"]["proof"] == "python3 a/selftest_x.py",
           "J: ambiguous stays pending and unapplied (ambiguity blocks)")
        R.bind_judge(s, "I0", "rm-judge", "approve", "the renamed file holds the same assertions", env={}, r=RULES)
        st = s.load("I0")
        c = st["contract"]
        ok(c["proof"] == "python3 a/selftest_x_renamed.py" and c["binding_version"] == 2 and not st.get("binding_proposal"),
           "J: approve applies the binding, version 2")
        ok(B.obligation_hash(c, "I0") == ob0 and c["obligation"]["text"] == "the gourd selects", "J: approve keeps the obligation")
        rec = [a for a in s.attempts("I0") if a.get("end") == "rebind_approve"]
        ok(rec and rec[-1]["before"]["binding"]["proof"] != rec[-1]["after"]["binding"]["proof"]
           and rec[-1]["before"]["obligation_hash"] == rec[-1]["after"]["obligation_hash"],
           "J: the attempt record names before/after binding and one obligation hash")
        R.rebind(s, "I0", 1, {"proof": "python3 a/selftest_z.py"}, dict(GOOD), r=RULES)
        R.bind_judge(s, "I0", "conductor", "reject", "z does not test selection", env={}, r=RULES)
        st = s.load("I0")
        ok(not st.get("binding_proposal") and st["contract"]["proof"] == "python3 a/selftest_x_renamed.py",
           "J: reject drops the proposal and leaves the contract")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_stale_approval():
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", r=RULES)
        R.rebind(s, "I0", 1, {"proof": "python3 a/selftest_y.py"}, dict(GOOD), r=RULES)
        st = s.load("I0")
        st["contract"]["proof"] = "python3 a/selftest_w.py"     # the binding moved under the proposal
        with s.lock():
            s.save(st)
        e = refused(R.bind_judge, s, "I0", "rm-judge", "approve", "ok", env={}, r=RULES)
        ok(e is not None and "changed since" in e, "J: a proposal against an older binding cannot be approved")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_weakening():
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py && test -s out.json", live="once: test",
                   game={"clauses": ["A2"], "why": "only the game"}, offbox=None, r=RULES)
        cases = [
            ("typed number", {"proof": "echo 42 | python3 a/check_free.py"}, GOOD, None, "typed"),
            ("constant proof", {"proof": "echo PASS && true"}, GOOD, None, "measures nothing"),
            ("literal comparison", {"proof": "python3 a/x.py; [ 37 -ge 30 ]"}, GOOD, None, "compares two numbers"),
            ("python literal", {"proof": "python3 -c 'assert 37 >= 30'"}, GOOD, None, "compares two numbers"),
            ("typed flag", {"proof": "python3 a/check.py --free-gb 42"}, GOOD, None, "typed number"),
            ("worker note", {"proof": "grep PASS /mnt/d/ClaudeWork/rimmandrake/relentless_progress/I0.md"}, GOOD, None,
             "worker-written"),
            ("changed behaviour", {"proof": "python3 a/selftest_y.py"}, dict(GOOD, behaviour="move did not occur"), None,
             "new obligation"),
            ("changed obligation", {"proof": "python3 a/selftest_y.py"}, GOOD, "the move did not occur", "obligation"),
            ("blank before", {"proof": "python3 a/selftest_y.py"}, dict(GOOD, before=" "), None, "ambiguous"),
            ("blank defect", {"proof": "python3 a/selftest_y.py"}, dict(GOOD, defect=""), None, "ambiguous"),
            ("nothing changed", {}, GOOD, None, "nothing to repair"),
        ]
        for name, b, cmp_, ob, word in cases:
            e = refused(R.rebind, s, "I0", 1, dict(b), dict(cmp_), obligation=ob, r=RULES)
            ok(e is not None and word in e, "W: %s refused (%s)" % (name, (e or "NOT REFUSED")[:90]))
        st = s.load("I0")
        st["contract"]["offbox"] = ["git_origin_main"]
        st["contract"]["fixtures"] = ["a/fx.json"]
        with s.lock():
            s.save(st)
        for name, b, word in [("dropped live", {"live": None}, "live line"),
                              ("dropped fixture", {"fixtures": ["a/other.json"]}, "fixture")]:
            new = dict(B.binding_of(s.load("I0")["contract"]), proof="python3 a/selftest_y.py", **b)
            new.pop("version")
            why = B.screen(s.load("I0")["contract"], {k: v for k, v in new.items() if v}, GOOD)
            ok(any(word in w for w in why), "W: %s refused (%s)" % (name, why[:1]))
        new = {"proof": "python3 a/selftest_y.py", "live": "once: test", "game": {"clauses": [], "why": "x"},
               "offbox": [], "fixtures": ["a/fx.json"]}
        why = B.screen(s.load("I0")["contract"], new, GOOD)
        ok(any("A2" in w for w in why) and any("offbox" in w for w in why), "W: dropped game clause and adapters refused")
        ok(s.load("I0").get("binding_proposal") is None, "W: no refused repair left a proposal behind")
        ok(any(a.get("end") == "rebind_refused" for a in s.attempts("I0")), "W: a refusal is on the attempt record")
        # the same screen on a proof-only contract change (no rebind)
        st = s.load("I0")
        st["proof_only"] = {"sha": "x", "at": 1}
        with s.lock():
            s.save(st)
        e = refused(R.contract, s, "I0", 1, "echo 42 | python3 a/check_free.py", why="w", r=RULES)
        ok(e is not None and "typed" in e, "W: a proof-only contract change may not type a number either")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_legit_repairs():
    """The spec's two lawful examples pass the screen; real proofs are not mistaken for typed numbers."""
    for p in ["python3 src/RimMandrake/Utils/run_selftests.py --only a/selftest_x.py",
              "python3 a/x.py > out.txt 2>&1; tail -n 30 out.txt", "test -s out.json && python3 a/check.py --min 3",
              "python3 a/check.py | grep -c PASS"]:
        ok(B.typed_numbers(p) == [], "W: a real proof passes: %s" % p)
    old = {"proof": "ssh steve df -h /", "by_gen": 1}
    why = B.screen(old, {"proof": "python3 a/read_adapter.py", "offbox": ["steve_c_free"]},
                   dict(GOOD, before="df over ssh from the box (unreachable)", after="the same df, read by the supervisor"))
    ok(why == [], "R: moving a measurement to a supervisor adapter passes the screen: %s" % why)
    ok(B.new_numbers("check.py --min 3", "check.py --min 1") == ["1"], "P: a moved threshold is shown to the judge")


def t_review_findings():
    """The independent review's six findings (2026-11-05), each a row."""
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", offbox=None, r=RULES)
        st = s.load("I0")
        st["contract"]["offbox"] = ["git_origin_main", "git_log_candidate"]
        with s.lock():
            s.save(st)
        e = refused(R.rebind, s, "I0", 1, {"proof": "python3 a/selftest_y.py", "offbox": ["git_origin_main"]}, dict(GOOD),
                    r=RULES)
        ok(e is not None and "git_log_candidate" in e, "#1 dropping one of two adapters is refused")
        st = s.load("I0")
        st["proof_only"] = {"sha": "x", "at": 1}    # a proof-only worker: the one non-redesign that may change a contract
        with s.lock():
            s.save(st)
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", fixtures=["a/fx.json"], why="widen", r=RULES)
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", fixtures=["a/fy.json"], freshness="same sha", why="widen", r=RULES)
        c = s.load("I0")["contract"]
        ok(c["fixtures"] == ["a/fx.json", "a/fy.json"], "#2 a non-redesign contract merges fixtures, never drops one")
        e = refused(R.contract, s, "I0", 1, "python3 a/selftest_x.py", freshness="max_age=30d", why="w", r=RULES)
        ok(e is not None and "rebind" in e, "#2 a non-redesign contract may not change the freshness rule")
        v = s.load("I0")["contract"]["binding_version"]
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", why="same again", r=RULES)
        ok(s.load("I0")["contract"]["binding_version"] == v, "#3 an unchanged binding keeps its version (offbox set)")
        for name in ("worker3", "gen 2", "I0 judge", "builder"):
            R.rebind(s, "I0", 1, {"proof": "python3 a/selftest_y.py"}, dict(GOOD), r=RULES) \
                if not s.load("I0").get("binding_proposal") else None
            e = refused(R.bind_judge, s, "I0", name, "approve", "ok", env={}, r=RULES)
            ok(e is not None and "worker of the work" in e, "#4 --as %r is refused" % name)
        st = s.load("I0")
        st["clone"] = HERE
        with s.lock():
            s.save(st)
        e = refused(R.bind_judge, s, "I0", "rm-judge", "approve", "ok", env={}, r=RULES, cwd=HERE)
        ok(e is not None and "own clone" in e, "#4 a judge inside the item's clone is refused")
        e = refused(R.rebind, s, "I0", 1, {"proof": "python3 a/selftest_z.py"}, dict(GOOD), r=RULES)
        ok(e is not None and "already waits" in e, "#5 a pending repair is never written over")
        R.bind_judge(s, "I0", "rm-judge", "reject", "y is not the same test", env={}, r=RULES, cwd="/")
        e = refused(R.rebind, s, "I0", 1, {"proof": "python3 a/selftest_y.py"}, dict(GOOD), r=RULES)
        ok(e is not None and "REJECTED" in e, "#5 the binding a judge rejected cannot be proposed again")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    for p in ["[ $(grep -c PASS out) -ge 5 ]", "python3 tools/progress.py --check", "pytest --count=3 t.py"]:
        ok(B.typed_numbers(p) == [], "#6 not a typed number: %s" % p)


def t_cli():
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", r=RULES)
        env = dict(os.environ, RELENTLESS_ROOT=base)
        env.pop("RELENTLESS_GEN", None)
        old = dict(os.environ)
        os.environ.clear()
        os.environ.update(env)
        try:
            e, o = io.StringIO(), io.StringIO()
            with redirect_stderr(e), redirect_stdout(o):
                rc = R.main(["snag", "--item", "I0", "--gen", "1", "--class", "binding_repair", "--blocker", "judge", "x"])
            ok(rc == 2 and "rebind" in e.getvalue(), "R: snag binding_repair with no proposal is refused")
            with redirect_stderr(e), redirect_stdout(o):
                rc = R.main(["rebind", "--item", "I0", "--gen", "1", "--proof", "python3 a/selftest_y.py", "--before", "b",
                             "--after", "a", "--behaviour", "same", "--defect", "d"])
            ok(rc == 0 and "OBLIGATION" in o.getvalue(), "R: rebind via the CLI prints the judge's packet")
            o2 = io.StringIO()
            with redirect_stderr(e), redirect_stdout(o2):
                rc = R.main(["bind-judge", "--item", "I0", "--packet"])
            ok(rc == 0 and "BINDING REPAIR" in o2.getvalue(), "P: bind-judge --packet prints it")
            with redirect_stderr(e), redirect_stdout(o2):
                rc = R.main(["bind-judge", "--item", "I0", "--as", "rm-judge", "--verdict", "approve", "--why", "same"])
            ok(rc == 0 and R.Store(base).load("I0")["contract"]["proof"] == "python3 a/selftest_y.py",
               "J: bind-judge approve via the CLI applies it")
        finally:
            os.environ.clear()
            os.environ.update(old)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_checker_gaps():
    """The blind check's two gaps (2026-11-05, gen 1 WEAK): a proof-only worker moving the obligation, and a binding
    repair dropping the freshness rule. Each row goes red when its guard is removed."""
    base, s = rig()
    try:
        R.contract(s, "I0", 1, "python3 a/selftest_x.py", obligation="the gourd selects", freshness="same sha", r=RULES)
        st = s.load("I0")
        st["proof_only"] = {"sha": "x", "at": 1}    # the one non-redesign worker that may call contract again
        with s.lock():
            s.save(st)
        e = refused(R.contract, s, "I0", 1, "python3 a/selftest_x.py", obligation="anything at all", why="w", r=RULES)
        c = s.load("I0")["contract"]
        ok(e is not None and "moves only in a redesign" in e,
           "G(a): a proof-only worker may not move the obligation (%s)" % (e or "NOT REFUSED")[:80])
        ok(c["obligation"] == {"text": "the gourd selects", "version": 1},
           "G(a): the refused change leaves obligation text and version as set: %r" % (c.get("obligation"),))
        new = {k: v for k, v in B.binding_of(c).items() if k not in ("version", "freshness")}
        new["proof"] = "python3 a/selftest_y.py"
        why = B.screen(c, new, GOOD)
        ok(any("freshness" in w for w in why), "G(b): a binding repair without the freshness rule is refused: %s" % why[:2])
        ok(not any("freshness" in w for w in B.screen(c, dict(new, freshness="same sha"), GOOD)),
           "G(b): the same repair keeping freshness is not refused for freshness")
        pk = R.rebind(s, "I0", 1, {"proof": "python3 a/selftest_y.py", "freshness": None}, dict(GOOD), r=RULES)
        ok(s.load("I0")["binding_proposal"]["binding"].get("freshness") == "same sha",
           "G(b): rebind leaving freshness out keeps it in the proposal (a left-out key is kept, never dropped)")
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    for t in (t_split, t_contract_fields, t_rebind_and_judge, t_stale_approval, t_weakening, t_legit_repairs, t_review_findings, t_checker_gaps, t_cli):
        t()
    print("\n%d FAIL" % len(FAILS) if FAILS else "\nALL OK")
    sys.exit(1 if FAILS else 0)
