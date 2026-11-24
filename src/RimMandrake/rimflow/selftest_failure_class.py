#!/usr/bin/env python3
"""selftest_failure_class.py -- one test per promise of design/specs/2026-11-23-one-failure-classifier/boundary.md that
is the function's own, then the mutants (a fault planted in the function must turn a test red)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import failure_class as FC  # noqa: E402
import live_kinds as LK  # noqa: E402


def t_only_the_works_own_outcome_counts(F):
    assert {w for w in F.WORDS if F.read(w).counts} == {"MOD FAILURE", "ENDED", "BAD REQUEST"}
    assert set(LK.OUTCOMES) <= set(F.WORDS), "the seven outcomes are live_kinds' own"
    assert len(F.WORDS) == len(set(F.WORDS)) == 15
    assert F.read("mod_failure").counts and not F.read("could-not look").counts, "any letter case, _ or - for a space"
    assert F.of_row({"outcome": "MOD FAILURE", "verdict": "FAIL"}).counts
    assert not F.of_row({"outcome": "RANDOM MISS", "verdict": "FAIL"}, {"test_kind": "B", "x_of_y": [1, 2]}).counts
    assert F.of_row({"outcome": "SUCCESS", "verdict": "PASS", "forbidden": ["a pawn died"]}).counts, "a forbidden effect"
    for row, w in (({"verdict": "FAIL", "class": "MOD"}, "MOD FAILURE"), ({"verdict": "FAIL"}, "MOD FAILURE"),
                   ({"verdict": "FAIL", "class": "HARNESS"}, "APPARATUS FAULT"), ({"verdict": "FAIL", "class": "site"},
                   "APPARATUS FAULT"), ({"verdict": "UNMEASURED"}, "COULD NOT LOOK"), ({"verdict": "PASS"}, "SUCCESS"),
                   ({"verdict": "NOT_RUN"}, "COULD NOT LOOK"), ({"outcome": "ENVIRONMENT FAULT"}, "UNRESOLVED")):
        assert F.of_row(row).word == w, (row, F.of_row(row))
    assert not F.of_launch("REFUSED by control: pool full").counts and F.of_launch("x").word == "NEVER STARTED"


def t_an_outcome_nobody_can_class_does_not_count_and_is_named(F):
    for w in ("EXPLODED", "", None, 3, [], {}):
        r = F.read(w)
        assert not r.counts and not r.classed and r.word == F.UNCLASSED and repr(w if isinstance(w, str) else w) in r.why, r
    for r in (F.of_row(None), F.of_row({}), F.of_row({"verdict": "MAYBE"}), F.of_run(None), F.of_testq(None),
              F.of_testq({"result": {"outcome": "ODD"}}), F.of_error(""), F.of_artpipe(None),
              F.of_artpipe({"worker_status": "new word"})):
        assert not r.counts and not r.classed, r
    assert "ODD" in F.of_testq({"result": {"outcome": "ODD"}}).why and "MAYBE" in F.of_row({"verdict": "MAYBE"}).why
    assert F.of_row({"outcome": "SUCCESS", "verdict": "FAIL"}).classed is False, "a row that contradicts itself"


def t_a_run_record_reads_as_run_void_reads_it(F):
    for rec, w in (({"status": "finished", "result": "killed: signal (exited 143)"}, "KILLED"),
                   ({"status": "finished", "result": "timeout (killed KILL)"}, "TIMED OUT"),
                   ({"status": "finished", "result": "exit-code (exited 1)"}, "KILLED"),
                   ({"status": "launch_failed"}, "NEVER STARTED"), ({"status": "refused", "result": "pool"}, "REFUSED"),
                   ({"status": "finished", "result": "success (exited 0)"}, "ENDED"),
                   ({"status": "finished", "result": "exit-code/claude-error (exited 1)"}, "ENDED"),
                   ({"status": "finished", "result": "unknown (read from out)"}, "ENDED"),
                   ({"status": "finished"}, "UNCLASSED"), ({}, "UNCLASSED")):
        assert F.of_run(rec).word == w, (rec, F.of_run(rec))
    refusal = "pool is full: " + "x" * 600 + " retry when a clone is free"
    assert F.of_run({"status": "refused", "result": refusal}).why == refusal, "the run reading keeps the whole refusal"


def tq(outcome, cause=None, rows=(), **kw):
    res = {"outcome": outcome, "cause": cause, "rows": [dict(chain=c, row="r", verdict=v) for c, v in rows],
           "note": kw.pop("note", "")}
    return dict({"job": {}, "result": res}, **kw)


def t_a_testq_job_reads_its_cause(F):
    for rec, w in ((tq("DONE", rows=[("a", "PASS"), ("b", "FAIL")]), "SUCCESS"), (tq("DONE", rows=[("a", "FAIL")]), "MOD FAILURE"),
                   (tq("DONE", rows=[("a", "UNMEASURED")]), "COULD NOT LOOK"), (tq("DONE", rows=[("b", "FAIL")]), "COULD NOT LOOK"),
                   (tq("REFUSED", "LOAD"), "REFUSED"), (tq("REFUSED", "SOURCE_SHA_MISSING"), "REFUSED"),
                   (tq("REFUSED", "PREFLIGHT"), "BAD REQUEST"), (tq("INVALID", "BLOCKED_SELECTION"), "BAD REQUEST"),
                   (tq("REFUSED", "SCHEMA"), "BAD REQUEST"),
                   (tq("INTERRUPTED", "CRASH"), "KILLED"), (tq("INVALID", "CANARY"), "APPARATUS FAULT"),
                   (tq("INVALID", "GAME_DIED"), "UNRESOLVED"), (tq("INVALID", "HANG"), "UNRESOLVED"),
                   (tq("INVALID", "LOAD", note="unknown chain(s) for FlowWorks"), "APPARATUS FAULT"),
                   (tq("DONE", rows=[("a", "FAIL")], cancelled=True), "STOPPED")):
        assert F.of_testq(rec, "a").word == w, (rec, F.of_testq(rec, "a"))
    assert F.of_testq(tq("DONE", rows=[("a", "PASS"), ("b", "FAIL")])).word == "MOD FAILURE", "the whole job: any FAIL row"


def t_the_count_names_what_it_left_out(F):
    n, left = F.count([F.read(w) for w in ("MOD FAILURE", "KILLED", "KILLED", "SUCCESS", "odd", "ENDED")])
    assert (n, left) == (2, {"KILLED": 2, "UNCLASSED": 1}), (n, left)
    assert F.named(left) == "2 KILLED, 1 UNCLASSED" and F.named({}) == "" and F.count([]) == (0, {})


def t_an_error_text_is_the_tools_or_the_records(F):
    for text, counts in (("crash: TimeoutExpired: x", False), ("crash: OSError: [Errno 5]", False), ("git: index.lock exists", False),
                         ("Traceback (most recent call last): KeyError", False), ("verify refused: no item X", True)):
        assert F.of_error(text).counts is counts, (text, F.of_error(text))
    refusal = "verify refused: " + "x" * 600 + " check the item id"
    assert F.of_error(refusal).why == refusal, "the error reading keeps the whole refusal"


MUTANTS = (("COUNTS = (LK.MOD_FAILURE, ENDED, BAD_REQUEST)", "COUNTS = (LK.MOD_FAILURE, ENDED, BAD_REQUEST, KILLED)"),
           ("COUNTS = (LK.MOD_FAILURE, ENDED, BAD_REQUEST)", "COUNTS = (LK.MOD_FAILURE, ENDED)"),
           ("return Reading(False, UNCLASSED,", "return Reading(True, UNCLASSED,"),
           ('if rec.get("cancelled"):', 'if False:'), ('if "FAIL" in v:', 'if "FAIL" in v and "PASS" in v:'),
           ("(chain is None or r.get(\"chain\") == chain)", "True"),
           ('return read(KILLED, said)', 'return read(ENDED, said)'),
           ("LK.APPARATUS if klass in", "LK.UNRESOLVED if klass in"),
           ("TIMED_OUT if res.startswith", "KILLED if res.startswith"), ("elif r.word != LK.SUCCESS", "else"),
           ('if v == "FAIL" and c in LK.WRONG:', 'if False:'), ('if low.startswith("crash:")', 'if False'),
           ("out in (\"REFUSED\", \"INVALID\") and", 'out == "REFUSED" and'))


def run(F, tests):
    bad = []
    for t in tests:
        try:
            t(F)
        except Exception as e:  # noqa: BLE001
            bad.append("%s: %s: %s" % (t.__name__, type(e).__name__, str(e)[:200]))
    return bad


def main():
    tests = (t_only_the_works_own_outcome_counts, t_an_outcome_nobody_can_class_does_not_count_and_is_named,
             t_a_run_record_reads_as_run_void_reads_it, t_a_testq_job_reads_its_cause, t_the_count_names_what_it_left_out,
             t_an_error_text_is_the_tools_or_the_records)
    bad = run(FC, tests)
    for b in bad:
        print("FAIL " + b)
    src = open(os.path.join(HERE, "failure_class.py"), encoding="utf-8").read()
    for a, b in MUTANTS:
        if src.count(a) < 1:
            bad.append("mutant not planted")
            print("FAIL the mutant's text is gone: %s" % a)
            continue
        import types
        m = types.ModuleType("fc_mutant")
        m.__file__ = os.path.join(HERE, "failure_class.py")
        exec(compile(src.replace(a, b, 1), "fc_mutant", "exec"), m.__dict__)
        if not run(m, tests):
            bad.append("survived")
            print("FAIL a planted fault is not caught: %s -> %s" % (a, b))
    print("selftest_failure_class: %d tests, %d mutants, %s" % (len(tests), len(MUTANTS), "FAIL %d" % len(bad) if bad else "OK"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
