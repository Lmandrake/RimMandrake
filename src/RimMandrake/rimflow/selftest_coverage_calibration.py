#!/usr/bin/env python3
"""selftest_coverage_calibration.py - coverage_calibration.judge's re-ask counts the session once
(RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE). A `--resume` result's total_cost_usd is the whole claude session so
far (measured: the 2026-11-18 run's five re-asked cases each recorded 2 x the first ask + the re-ask, e.g.
bad_scene_no_control $1.1804 = 295,100 weighted against its transcript's 2 x 126,101 + 15,697), so the case's cost is
that total, not the first ask's added to it; an unreadable re-ask total is UNMEASURED (None), never the first ask's
figure. The claude call and the contract check are stubbed: no network, no model."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage_calibration as CC  # noqa: E402

CJ = CC.CJ
FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def case(d, first, second):
    """-> detail["cost_usd"] of one planted case whose first answer has a broken record and is re-asked once."""
    outs = [first, second]
    errs = [["refusal 1: no smallest_fix"]]

    class P:
        def __init__(self, res):
            self.returncode, self.stdout, self.stderr = 0, json.dumps(res), ""
    saved = (subprocess.run, CJ.prior_verdict, CJ.required_ids, CJ.prompt, CJ.contract_errors)
    subprocess.run = lambda argv, **kw: P(outs.pop(0))
    CJ.prior_verdict = lambda d: None
    CJ.required_ids = lambda d, tree: []
    CJ.prompt = lambda *a, **k: "p"
    CJ.contract_errors = lambda d, rec, item: (None, None, errs.pop(0) if errs else [])
    try:
        _got, detail = CC.judge(os.path.dirname(d), d, reader=None)
    finally:
        subprocess.run, CJ.prior_verdict, CJ.required_ids, CJ.prompt, CJ.contract_errors = saved
    return detail.get("cost_usd"), detail


def answer(usd, gaps=True, **kw):
    res = {"type": "result", "session_id": "sess", "structured_output": {
        "verdict": "covered", "checklist": [], "gaps": [{"what": "w", "ids": []}] if gaps else []}}
    if usd is not None:
        res["total_cost_usd"] = usd
    res.update(kw)
    return res


def main():
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, "Foo")
        os.makedirs(d)
        with open(os.path.join(d, "tree.json"), "w") as f:
            json.dump({"kind": "mod", "leaves": []}, f)
        usd, det = case(d, answer(0.5), answer(0.8, gaps=False))
        check("a resumed re-ask: the case costs the session's total once", usd == 0.8 and det.get("reasked"), (usd, det))
        usd, det = case(d, answer(0.5), answer(None, gaps=False))
        check("an unreadable re-ask total -> UNMEASURED, never the first ask's figure", usd is None, (usd, det))
        usd, det = case(d, answer(0.5), answer(0.25, gaps=False, stopped_by="spend_watchdog"))
        check("a spend watchdog stop measured its launch only: added to the first ask's", usd == 0.75, (usd, det))
    print("selftest_coverage_calibration: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
