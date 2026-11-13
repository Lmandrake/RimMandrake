#!/usr/bin/env python3
"""selftest_judge_calibration.py - the judge calibration registry (RIMMANDRAKE_SEED_JUDGE_CALIBRATION_FROM_CORPORA, T6 of
design/specs/2026-11-12-refusal-contract-for-judges-and-gates.md section 5).

Every live judge brief has a row keyed by its brief hash; an edit to a brief resets it to UNTESTED; a free deterministic
check (the evidence gate's corpus) sets CALIBRATED or FAILED; only a CALIBRATED brief's refusal has a consequence: an
UNTESTED coverage judge's refusal is stored and shown but does not send the Designer back. No model, no network."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402

FAILS = []
LIVE = ("coverage_judge", "art_judge_brief", "scene_look_judge_brief", "art_eval_first_pass", "evidence_gate")


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def main():
    reg = RC.load_calibration(os.path.join(REPO, RC.CALIBRATION_REL))
    check("the committed registry has a row for every live judge brief",
          all(f in reg["families"] for f in LIVE), sorted(reg["families"]))
    check("every row names its brief files, a hash, a status and its seed cases",
          all(set(("brief", "hash", "status", "cases")) <= set(r) and r["status"] in RC.CAL_STATUS
              for r in reg["families"].values()), reg["families"])
    check("each row's cases hold at least one known-good and one known-bad, or say why not",
          all((r["cases"].get("good") and r["cases"].get("bad")) or r["cases"].get("gap")
              for r in reg["families"].values()))
    with tempfile.TemporaryDirectory() as root:
        # a copy of the brief files, so an edit can be planted without touching the repo
        fam = {"brief": ["b.md"], "hash": None, "status": "CALIBRATED", "cases": {"good": ["g"], "bad": ["b"]}}
        with open(os.path.join(root, "b.md"), "w") as f:
            f.write("judge brief v1\n")
        fam["hash"] = RC.brief_hash(fam["brief"], root)
        path = os.path.join(root, "cal.json")
        with open(path, "w") as f:
            json.dump({"families": {"fam": fam}}, f)
        out = RC.calibrate(path, root, run_free=False)
        check("an unedited CALIBRATED brief stays CALIBRATED", out["families"]["fam"]["status"] == "CALIBRATED", out)
        os.environ["RM_JUDGE_CALIBRATION"] = path
        os.environ["RM_CALIBRATION_ROOT"] = root
        check("a CALIBRATED brief at its hash is not advisory", RC.advisory("fam") is False)
        with open(os.path.join(root, "b.md"), "a") as f:
            f.write("one more line\n")
        check("an edited brief reads UNTESTED at once, before any calibrate run", RC.status("fam") == "UNTESTED")
        out = RC.calibrate(path, root, run_free=False)
        check("an edit to the brief resets it to UNTESTED", out["families"]["fam"]["status"] == "UNTESTED", out)
        os.environ["RM_JUDGE_CALIBRATION"] = path
        os.environ["RM_CALIBRATION_ROOT"] = root
        check("an UNTESTED brief's refusals are advisory", RC.advisory("fam") is True)
        check("a family with no row is advisory (UNTESTED)", RC.advisory("no_such_family") is True)
        # the free check: a command that passes calibrates, one that fails marks FAILED
        reg2 = {"families": {"ok": {"brief": ["b.md"], "hash": None, "status": "UNTESTED", "cases": {"gap": "x"},
                                    "free_check": [sys.executable, "-c", "raise SystemExit(0)"]},
                             "bad": {"brief": ["b.md"], "hash": None, "status": "UNTESTED", "cases": {"gap": "x"},
                                     "free_check": [sys.executable, "-c", "raise SystemExit(1)"]}}}
        with open(path, "w") as f:
            json.dump(reg2, f)
        out = RC.calibrate(path, root, run_free=True)
        check("a passing free check sets CALIBRATED at the current hash",
              out["families"]["ok"]["status"] == "CALIBRATED"
              and out["families"]["ok"]["hash"] == RC.brief_hash(["b.md"], root), out["families"]["ok"])
        check("a failing free check sets FAILED", out["families"]["bad"]["status"] == "FAILED", out["families"]["bad"])
        check("CALIBRATED is not advisory, FAILED is", RC.advisory("ok") is False and RC.advisory("bad") is True)

        # the coverage judge: an UNTESTED brief's well-formed refusal does not send the Designer back
        import selftest_coverage_refusal_record as T
        import coverage_judge as CJ
        import designer_stage as DS
        import concept_tree as CT
        saved = (CT.coverage_problem, CT.sign, DS.exam_errors, DS.owner_away)
        CT.coverage_problem = lambda d, repo, tree: "no coverage signature"
        DS.exam_errors = lambda ex, d, st, repo=None: []
        CT.sign = lambda d, by, repo=None, **kw: []
        DS.owner_away = lambda: (False, "selftest: attended")
        CJ.delta_plan = lambda d, prior, read=None: None
        os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "store"), RM_OPS_WATCH_DIR=os.path.join(root, "ops"),
                          RM_DISPATCHER_STATE=os.path.join(root, "dispatcher"))
        os.makedirs(os.path.join(root, "ops"))
        try:
            with open(path, "w") as f:
                json.dump({"families": {}}, f)
            croot = os.path.join(root, "c")
            d = T.concept(croot)
            rec, msg = CJ.run(d, croot, T.script([T.answer("not_covered", [T.good_gap()])], []))
            check("an UNTESTED coverage judge's not_covered is stored, marked advisory, and stops the Designer's rework",
                  rec["verdict"] == "not_covered" and rec.get("advisory") and CJ.stop_exit(rec), (rec.get("advisory"), msg))
            with open(path, "w") as f:
                json.dump({"families": {"coverage_judge": {"brief": ["b.md"], "hash": RC.brief_hash(["b.md"], root),
                                                           "status": "CALIBRATED", "cases": {"gap": "x"}}}}, f)
            shutil.rmtree(croot)
            d = T.concept(croot)
            rec, msg = CJ.run(d, croot, T.script([T.answer("not_covered", [T.good_gap()])], []))
            check("a CALIBRATED coverage judge's not_covered sends the Designer back (no stop)",
                  rec["verdict"] == "not_covered" and not rec.get("advisory") and not CJ.stop_exit(rec), msg)
        finally:
            CT.coverage_problem, CT.sign, DS.exam_errors, DS.owner_away = saved
            for k in ("RM_JUDGE_CALIBRATION", "RM_CALIBRATION_ROOT", "RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR",
                      "RM_DISPATCHER_STATE"):
                os.environ.pop(k, None)
    print("selftest_judge_calibration: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
