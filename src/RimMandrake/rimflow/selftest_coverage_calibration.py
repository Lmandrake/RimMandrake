#!/usr/bin/env python3
"""selftest_coverage_calibration.py - coverage_calibration.judge's re-ask counts the session once
(RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE). A `--resume` result's total_cost_usd is the whole claude session so
far (measured: the 2026-11-18 run's five re-asked cases each recorded 2 x the first ask + the re-ask, e.g.
bad_scene_no_control $1.1804 = 295,100 weighted against its transcript's 2 x 126,101 + 15,697), so the case's cost is
that total, not the first ask's added to it; an unreadable re-ask total is UNMEASURED (None), never the first ask's
figure. A judge that fixes scenes.json while it judges (RIMMANDRAKE_LET_BLIND_READERS_FIX_TWO_STILL_FORBIDDEN_IN_CODE)
is read as run() reads it: its covered word over its own fix is not_covered, and the later-look rule reads the entry texts
it was shown, never its own edit. The claude call and the contract check are stubbed: no network, no model."""
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


def fixing_case(d):
    """-> (detail, the texts classify_new was handed, the texts before the judge ran) of one later look whose judge edits
    scenes.json and answers covered with a gap it says it fixed."""
    class P:
        def __init__(self, res):
            self.returncode, self.stdout, self.stderr = 0, json.dumps(res), ""

    def judge_run(argv, **kw):
        with open(os.path.join(d, "scenes.json"), "w") as f:
            json.dump({"scenes": [{"id": "sc_a", "expect": "the lantern goes out"}]}, f)
        return P(answer(0.5, gaps=False, structured_output={"verdict": "covered", "checklist": [], "repairs": [], "gaps": [
            {"what": "sc_a expects the lantern lit at zero oil", "ids": [], "judge_fixed": "sc_a: expect now dark"}]}))
    seen = {}
    saved = (subprocess.run, CJ.prior_verdict, CJ.required_ids, CJ.prompt, CJ.contract_errors, CJ.delta_plan,
             CJ.rejudge_slots, CJ.classify_new)
    before = CJ.entry_texts(d)
    subprocess.run = judge_run
    CJ.prior_verdict = lambda d: {"verdict": "not_covered", "judge": "j0", "gaps": [{"gid": "g1", "ids": []}],
                                  "entry_text": {}}
    CJ.required_ids = lambda d, tree: []
    CJ.prompt = lambda *a, **k: "p"
    CJ.contract_errors = lambda d, rec, item: (None, None, [])
    CJ.delta_plan = lambda d, prior, read=None: None
    CJ.rejudge_slots = lambda rec, prior, repairs: None
    CJ.classify_new = lambda rec, old, new, judge: seen.update(texts=new)
    try:
        _got, detail = CC.judge(os.path.dirname(d), d, reader=lambda items: [
            {"criterion_verdict": "sound", "criterion_why": "w", "bar_kind": "experience", "serious": False}] * len(items))
    finally:
        (subprocess.run, CJ.prior_verdict, CJ.required_ids, CJ.prompt, CJ.contract_errors, CJ.delta_plan,
         CJ.rejudge_slots, CJ.classify_new) = saved
    return detail, seen.get("texts"), before


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
        with open(os.path.join(d, "scenes.json"), "w") as f:
            json.dump({"scenes": [{"id": "sc_a", "expect": "the lantern stays lit"}]}, f)
        det, texts, before = fixing_case(d)
        check("a judge's own fix: its covered word reads not_covered and its fix is recorded",
              det.get("verdict") == "not_covered" and (det.get("judge_fixed") or {}).get("files") == ["scenes.json"], det)
        check("a judge's own fix: the later-look rule reads the texts it was shown, not its edit",
              texts == before and texts != CJ.entry_texts(d), (texts, before))
    print("selftest_coverage_calibration: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
