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
        # the free check (RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS): exit 0 is not enough; every planted case must have
        # run and come out as planted, both ways, before a brief is CALIBRATED
        def writes(cases, code=0):
            body = "import json,os\nif os.environ.get('RM_CALIBRATION_RESULTS'):\n" \
                   "    json.dump({'cases': %r}, open(os.environ['RM_CALIBRATION_RESULTS'], 'w'))\n" \
                   "raise SystemExit(%d)\n" % (cases, code)
            return [sys.executable, "-c", body]
        planted = [{"id": "p_good", "expect": "pass"}, {"id": "p_bad", "expect": "refuse"}]
        both = [{"id": "p_good", "expect": "pass", "got": "pass"}, {"id": "p_bad", "expect": "refuse", "got": "refuse"}]

        def row(cmd, pl=planted):
            return {"brief": ["b.md"], "hash": None, "status": "UNTESTED", "cases": {"gap": "x"}, "planted": pl,
                    "free_check": cmd}
        reg2 = {"families": {"ok": row(writes(both)),
                             "bad": row(writes(both, code=1)),
                             "silent": row(writes([])),
                             "nowrite": row([sys.executable, "-c", "raise SystemExit(0)"]),
                             "short": row(writes(both[:1])),
                             "wrong": row(writes([both[0], dict(both[1], got="pass")])),
                             "oneway": row(writes(both[:1]), pl=planted[:1])}}
        with open(path, "w") as f:
            json.dump(reg2, f)
        out = RC.calibrate(path, root, run_free=True)
        F = out["families"]
        check("every planted case ran and came out as planted: CALIBRATED at the current hash",
              F["ok"]["status"] == "CALIBRATED" and F["ok"]["hash"] == RC.brief_hash(["b.md"], root), F["ok"])
        check("a failing free check sets FAILED", F["bad"]["status"] == "FAILED", F["bad"])
        check("exit 0 with no case results stays UNTESTED", F["silent"]["status"] == "UNTESTED"
              and F["nowrite"]["status"] == "UNTESTED", (F["silent"], F["nowrite"]))
        check("exit 0 with a planted case that did not run stays UNTESTED and names it",
              F["short"]["status"] == "UNTESTED" and "p_bad" in str(F["short"].get("last_run")), F["short"])
        check("a planted case that came out the other way sets FAILED and names it",
              F["wrong"]["status"] == "FAILED" and "p_bad" in str(F["wrong"].get("last_run")), F["wrong"])
        check("planted cases one way only stay UNTESTED (a gate is trusted both ways)",
              F["oneway"]["status"] == "UNTESTED", F["oneway"])
        check("CALIBRATED is not advisory, FAILED and UNTESTED are",
              RC.advisory("ok") is False and RC.advisory("bad") is True and RC.advisory("short") is True)
        # calibrate --no-run is a read-only status: the registry's bytes do not move, even over an edited brief
        with open(path, "rb") as f:
            before = f.read()
        with open(os.path.join(root, "b.md"), "a") as f:
            f.write("an edit the status must report, not write\n")
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = RC.main(["calibrate", "--no-run"])
        with open(path, "rb") as f:
            after = f.read()
        check("calibrate --no-run leaves the registry bytes unchanged", rc == 0 and before == after)
        check("calibrate --no-run reports the edited brief as UNTESTED", "UNTESTED" in buf.getvalue()
              and "CALIBRATED" not in buf.getvalue().split("ok", 1)[-1].splitlines()[0], buf.getvalue())

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
            # covered signs only under a CALIBRATED brief (RIMMANDRAKE_EARN_CALIBRATION_BOTH_WAYS)
            ok_rows = [T.ROWS[0], dict(T.ROWS[1], parts=[{"what": "a wall stops a throw", "scene": "sc_throw", "ok": True}])]
            signed = []
            CT.sign = lambda d, by, repo=None, **kw: signed.append(d) or []
            shutil.rmtree(croot)
            d = T.concept(croot)
            rec, msg = CJ.run(d, croot, T.script([T.answer("covered", [], rows=ok_rows)], []))
            check("a CALIBRATED coverage judge's covered signs and records its calibration",
                  rec["verdict"] == "covered" and rec["signed"] and signed and rec.get("calibration") == "CALIBRATED",
                  (msg, rec.get("calibration")))
            with open(path, "w") as f:
                json.dump({"families": {}}, f)
            signed[:] = []
            shutil.rmtree(croot)
            d = T.concept(croot)
            rec, msg = CJ.run(d, croot, T.script([T.answer("covered", [], rows=ok_rows)], []))
            check("an UNTESTED coverage judge's covered does not sign: advisory, and the Designer's run stops",
                  rec["verdict"] == "covered" and not rec["signed"] and not signed and rec.get("advisory")
                  and CJ.stop_exit(rec) and rec.get("calibration") == "UNTESTED", (msg, rec.get("advisory")))
            # not retroactive: a signature already made under an unproven brief is flagged in the status, not voided
            srepo = os.path.join(root, "srepo")
            for name, verdict in (("Old", {"verdict": "covered", "signed": True}),
                                  ("New", {"verdict": "covered", "signed": True, "calibration": "CALIBRATED"})):
                cd = os.path.join(srepo, "design", "concepts", name)
                os.makedirs(cd)
                with open(os.path.join(cd, "tree.json"), "w") as f:
                    json.dump({"coverage": {"signed_by": "CoverageJudge", "at": "2026-11-15T05:54:32Z"}}, f)
                with open(os.path.join(cd, CJ.VERDICT_FILE), "w") as f:
                    json.dump(verdict, f)
            flagged = CJ.unproven_signatures(srepo)
            check("a signature made under an unproven brief is flagged; one under CALIBRATED is not",
                  [f["concept"] for f in flagged] == ["design/concepts/Old"], flagged)
            with open(os.path.join(srepo, "design", "concepts", "Old", "tree.json")) as f:
                check("the flagged signature is not voided", json.load(f)["coverage"]["signed_by"] == "CoverageJudge")
        finally:
            CT.coverage_problem, CT.sign, DS.exam_errors, DS.owner_away = saved
            for k in ("RM_JUDGE_CALIBRATION", "RM_CALIBRATION_ROOT", "RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR",
                      "RM_DISPATCHER_STATE"):
                os.environ.pop(k, None)
    print("selftest_judge_calibration: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
