#!/usr/bin/env python3
"""selftest_art_first_pass_calibration.py - the promises of design/specs/2026-11-24-first-pass-calibration/boundary.md.
No model, no network: the judge is a fake. The real run is `refusal_contract.py calibrate --model art_eval_first_pass`,
which spends."""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import art_first_pass_calibration as F  # noqa: E402
import refusal_contract as RC  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def reply(prompt, overall, findings=(), drop=0):
    ids = [l.split("`")[1] for l in prompt.split("# Checklist")[1].split("# Images")[0].splitlines() if l.startswith("- `")]
    return json.dumps({"schema": "rm-art-eval/opus@v1", "subject": "x", "observed": {}, "findings": list(findings),
                       "checklist": {i: {"status": "ok", "seen": "-"} for i in ids[drop:]}, "overall": overall})


def ran(ask, path=None, **env):
    with tempfile.TemporaryDirectory() as tmp:
        os.environ[RC.RESULTS_ENV] = os.path.join(tmp, "r.json")
        try:
            rc = F.run(ask=ask, path=path, out=lambda *_: None)
            return rc, {c["id"]: c for c in json.load(open(os.environ[RC.RESULTS_ENV]))["cases"]}
        finally:
            os.environ.pop(RC.RESULTS_ENV, None)


META = {"models_reported": ["fake"]}


def weak(seen):
    def ask(p, _d):
        seen.append(p)
        return reply(p, "good", [{"code": "DESC_MISS", "confidence": 0.2}]), META
    return ask


def all_rows_():
    with open(F.REGRESSION, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def t_planted_rows():
    all_rows = all_rows_()
    pl = F.planted()
    keep = [r for r in all_rows if not r.get("taste")]
    check("planted-rows: one case per row with no taste, his verdict", [p["expect"] for p in pl] ==
          [{"ACCEPT": "pass", "NOT_ACCEPT": "refuse"}[r["expect"]] for r in keep], pl)
    check("planted-rows: unique ids, both ways", len({p["id"] for p in pl}) == len(pl)
          and {p["expect"] for p in pl} == {"pass", "refuse"}, pl)
    reg = json.load(open(os.path.join(REPO, RC.CALIBRATION_REL)))["families"]["art_eval_first_pass"]
    check("planted-rows: the registry row lists the same cases", reg.get("planted") == pl, reg.get("planted"))
    check("planted-rows: the registry names this check", reg.get("model_check") ==
          ["python3", "src/RimMandrake/rimflow/art_first_pass_calibration.py", "run"], reg.get("model_check"))


def t_band_is_the_answer():
    pl = F.planted()
    _rc, w = ran(weak([]))
    check("band-is-the-answer: WEAK with the model's word good is `second look`, never pass",
          len(w) == len(pl) and all(c["got"] == "second look" and c["overall"] == "good" for c in w.values()), w)
    check("band-is-the-answer: all-WEAK is not CALIBRATED", RC.judge_cases(pl, {"cases": list(w.values())})[0] == "FAILED")
    _rc, g = ran(lambda p, d: (reply(p, "good"), META))
    check("band-is-the-answer: GOOD is pass", all(c["got"] == "pass" for c in g.values()), g)
    _rc, b = ran(lambda p, d: (reply(p, "really_bad", [{"code": "STYLE_EARTHLY", "confidence": 0.95},
                                                      {"code": "DESC_MISS", "confidence": 0.95}]), META))
    check("band-is-the-answer: a confident blocking finding is refuse", all(c["got"] == "refuse" for c in b.values()), b)
    check("band-is-the-answer: accept-all and refuse-all both read FAILED", all(
        RC.judge_cases(pl, {"cases": list(x.values())})[0] == "FAILED" for x in (g, b)))
    mix = [dict(c, got=c["expect"]) for c in g.values()]
    check("band-is-the-answer: every case as planted reads CALIBRATED (the instrument can say yes)",
          RC.judge_cases(pl, {"cases": mix})[0] == "CALIBRATED")


def t_could_not_look():
    pl = F.planted()
    _rc, e = ran(lambda p, d: ("", {"error": "You've hit your session limit"}))
    check("could-not-look: a failed call leaves its case out", e == {}, e)
    check("could-not-look: the family then reads UNTESTED", RC.judge_cases(pl, {"cases": []})[0] == "UNTESTED")
    with tempfile.TemporaryDirectory() as tmp:
        spec = json.load(open(os.path.join(REPO, "infrastructure/state/art_eval/regression_specs/owner_RM_DecayDrake_C.json")))
        spec["images"] = dict(spec["images"], south=os.path.join(tmp, "gone.png"))
        case = {"id": "x", "expect": "pass", "spec": spec}
        check("could-not-look: a missing picture did not run, and no judge is asked",
              F.judge(case, Path(tmp) / "c", lambda p, d: 1 / 0)[0] is None)


def t_malformed_is_not_missing():
    pl = F.planted()
    n = []
    _rc, m = ran(lambda p, d: (n.append(1) or reply(p, "good", drop=1), META))
    check("malformed-is-not-missing: an incomplete reply is re-asked once, then `malformed`",
          all(c["got"] == "malformed" for c in m.values()) and len(n) == 2 * len(pl), (len(n), m))


def t_blind():
    all_rows, pl, seen = all_rows_(), F.planted(), []
    ran(weak(seen))
    leaks = [w_ for p in seen for w_ in ("NOT_ACCEPT", "owner kept Shadefern", "PURGED", "owner REDO", "PICKED",
                                         "POOLED", "KEPT live", "known_miss", "regression.jsonl", "CL-0") if w_ in p]
    check("blind: no verdict, expectation or provenance of a row is in a prompt", len(seen) == len(pl) and not leaks, leaks)

    specs = [(r, F.C.load_spec(Path(REPO) / r["spec"])) for r in all_rows if r.get("spec")]
    bad = [s["subject"] for _r, s in specs if "owner" in str(s.get("provenance")) or "CL-0" in str(s.get("provenance"))]
    check("blind: no regression spec (a taste row's too) prints his verdict as its provenance", specs and not bad, bad)


def t_no_second_reviewer():
    pl = F.planted()

    def boom(*a, **k):
        raise AssertionError("called")
    saved = (F.R.call_gpt, F.R.file_regen_jobs, F.R.run)
    F.R.call_gpt = F.R.file_regen_jobs = F.R.run = boom
    try:
        rc, x = ran(weak([]))
    finally:
        F.R.call_gpt, F.R.file_regen_jobs, F.R.run = saved
    check("no-second-reviewer: a WEAK band asks nobody else and files nothing", rc == 0 and len(x) == len(pl), x)


def main():
    t_planted_rows()
    t_band_is_the_answer()
    t_could_not_look()
    t_malformed_is_not_missing()
    t_blind()
    t_no_second_reviewer()
    print("selftest_art_first_pass_calibration: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
