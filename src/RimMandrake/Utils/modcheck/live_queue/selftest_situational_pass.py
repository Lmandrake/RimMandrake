"""Offline selftest for situational_pass.py (NORTHSTAR_SITUATIONAL_ROLLOUT_1): the rollup's verdict from testq results, each
pass case with a failing twin, and the record it writes passing rollout_gate.evaluate."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rollout_gate as G       # noqa: E402
import situational_pass as P   # noqa: E402

FAILS = []


def check(name, ok):
    print("%s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)


def dg(mod, **kw):
    d = {"mod": mod, "refused": "", "verdicts": {"PASS": 1}, "all_green": True, "surprises": [], "serious_detectors": [],
         "budget_unmeasured": [], "unbland_chains": [], "evidence_missing": []}
    d.update(kw)
    return d


def ok(mod, **kw):
    return {"outcome": "DONE", "cause": None, "finished": "2026-11-06T10:00:00Z", "situational": dg(mod, **kw)}


def verdict(results, suites=("A", "B")):
    return P.judge_pass(results, suites, "s" * 40, finished="t")


def main():
    r = verdict({"A": ok("A"), "B": ok("B")})
    check("a full clean pass is MEASURED PASS", (r["status"], r["verdict"]) == ("MEASURED", "PASS"))
    check("the record passes the gate's evaluate",
          G.evaluate(r, {"A", "B"}, {"A", "B"}, [], "g", lambda a, b: True) == [])
    r = verdict({"A": ok("A")})
    check("a missing suite is UNMEASURED, not a verdict", (r["status"], r["verdict"]) == ("UNMEASURED", None))
    check("and the gate refuses it", G.evaluate(r, {"A", "B"}, {"A", "B"}, [], "g", lambda a, b: True) != [])
    for name, res, word in (
            ("an unbland chain", {"A": ok("A", unbland_chains=["c"]), "B": ok("B")}, "bland"),
            ("a budget UNMEASURED", {"A": ok("A", budget_unmeasured=["c/x"]), "B": ok("B")}, "BudgetExceeded"),
            ("a refused suite", {"A": ok("A", refused="no floor"), "B": ok("B")}, "refused"),
            ("evidence missing on the host", {"A": ok("A", evidence_missing=["c sidecar"]), "B": ok("B")}, "evidence"),
            ("a job that died", {"A": {"outcome": "INVALID", "cause": "HARNESS", "note": "n"}, "B": ok("B")}, "raised"),
            ("a result with no digest", {"A": {"outcome": "DONE", "cause": None}, "B": ok("B")}, "raised"),
            ("a digest error", {"A": {"outcome": "DONE", "situational": {"mod": "A", "digest_error": "boom"}}, "B": ok("B")},
             "raised")):
        r = verdict(res)
        check("%s fails the pass" % name, r["verdict"] == "FAIL" and any(word in f for f in r["failed"]))
    r = verdict({"A": ok("A", surprises=[{"chain": "c", "sidecar": "/nowhere/x.json", "png": None}]), "B": ok("B")})
    check("a surprise whose evidence the worker saw is not re-looked-for here, and stays listed",
          r["verdict"] == "PASS" and r["evidence"]["digests"][0]["surprises"])
    old, new = {"finished": "1"}, {"finished": "2"}
    got = P.latest_results([{"job": {"mod": "A"}, "result": new}, {"job": {"mod": "A"}, "result": old}])
    check("the newest attempt per suite stands", got["A"] is new)
    with tempfile.TemporaryDirectory() as t:
        for state, body in (("pending", {"id": "p", "mod": "A", "situational": True, "source_sha": "x"}),
                            ("running", {"job": {"mod": "B", "situational": True, "source_sha": "x"}, "attempt": "a"}),
                            ("done", {"job": {"mod": "C", "situational": True, "source_sha": "x"}, "result": {}})):
            os.makedirs(os.path.join(t, state))
            with open(os.path.join(t, state, "j.json"), "w") as f:
                json.dump(body, f)
            with open(os.path.join(t, state, "other.json"), "w") as f:
                json.dump({"id": "q", "mod": "Z", "source_sha": "x"}, f)
        got = P.read_jobs("x", t)
        check("read_jobs finds this sha's situational jobs in each state and nothing else",
              sorted(P.job_of(r)["mod"] for s in P.STATES for r in got[s]) == ["A", "B", "C"])
        check("another sha reads empty", not any(P.read_jobs("y", t).values()))
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
