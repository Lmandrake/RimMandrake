#!/usr/bin/env python3
"""selftest_testq_pipeline_admit.py - SteveDesktop runs pipeline tests only (spec question 18c, owner by card 2026-11-14:
"What may be queued on SteveDesktop -> Pipeline tests only"; item RIMMANDRAKE_DESIGN_MATURATION_PIPELINE_WHOLE_MOD_IS_THE_UNIT).

  python3 selftest_testq_pipeline_admit.py               every check; exit 1 on any failure
  python3 selftest_testq_pipeline_admit.py --mutant M    the same checks with guard M reverted: must exit 1
  python3 selftest_testq_pipeline_admit.py --mutants     run every mutant; exit 0 only if each one is caught

A temp design/concepts tree and a temp queue stand in for the real ones; no git push, ledger, ssh or game is touched.
"""
import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="pipeline_admit_")
os.environ["TESTQ_QUEUE"] = os.path.join(TMP, "q")
os.environ["RIMFLOW_ITEMS"] = os.path.join(TMP, "items")
ROOT = os.path.join(TMP, "repo")
os.environ["TESTQ_PIPELINE_ROOT"] = ROOT

import pipeline_admit as P  # noqa: E402
import testq as T  # noqa: E402
import brake_release as BR  # noqa: E402
import fault_monitor as FM  # noqa: E402
import steward as ST  # noqa: E402

FAILS = []


def check(ok, msg):
    print("%s  %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def concept(mod, stage, version="0.1.0", state="locked", rec_version=None, tests=None):
    d = os.path.join(ROOT, "design", "concepts", mod, "version")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "VERSION.json"), "w") as f:
        json.dump({"mod": mod, "version": version, "state": state}, f)
    with open(os.path.join(d, "stage_record.json"), "w") as f:
        json.dump({"mod": mod, "version": rec_version or version, "stage": stage}, f)
    with open(os.path.join(d, "test_table.json"), "w") as f:
        json.dump({"mod": mod, "version": version, "tests": tests if tests is not None else {
            "sc_bar": {"id": "sc_bar", "stage": "6", "testq": {"chains": ["c_bar"], "rows": ["r_bar"]}},
            "sc_tier": {"id": "sc_tier", "stage": "6", "testq": {"proofs": ["p_bar"]}},
            "T_OFF": {"id": "T_OFF", "stage": "4-5", "testq": {"chains": ["c_offline"]}},
        }}, f)


concept("Ready", "in_game")                                  # past the blind challenge, locked, versions agree
concept("Passed", "passed")
concept("Building", "offline_build")                         # every real mod today
concept("Draft", "in_game", state="draft")                   # not locked
concept("Skew", "in_game", rec_version="0.0.9")              # the record is for another version
concept("NoTq", "in_game", tests={"sc_bar": {"id": "sc_bar", "stage": "6"}})    # a bar check with no queue selection


def pipeline_checks():
    q = P.qualifying(ROOT)
    check(set(q) == {"Ready", "Passed", "NoTq"}, "qualifying mod versions: past the blind challenge, locked, record = "
          "VERSION.json: %s" % sorted(q))
    check(q.get("Ready", {}).get("chains") == {"c_bar"} and "c_offline" not in q["Ready"]["chains"],
          "only stage-6 bar checks are queueable, never an offline one: %s" % q.get("Ready"))
    check(P.refusal("Ready", {"chains": ["c_bar"]}, "BENCH", ROOT) is None, "a locked bar's chain is admitted")
    check(P.refusal("Ready", {"rows": ["r_bar"]}, "BENCH", ROOT) is None, "a locked bar's row is admitted")
    check(P.refusal("Ready", {"proofs": ["p_bar"]}, "BENCH", ROOT) is None, "a locked bar's proof is admitted")
    for mod, sel, why in (("Ready", {"chains": ["c_bar", "c_other"]}, "one chain no bar names"),
                          ("Ready", {"chains": ["c_offline"]}, "an offline-stage check"),
                          ("Ready", {"full": True}, "a whole sweep"),
                          ("Ready", {"item": "SOME_ITEM"}, "an item selection"),
                          ("Building", {"chains": ["c_bar"]}, "a mod at Stage 3"),
                          ("Draft", {"chains": ["c_bar"]}, "an unlocked version"),
                          ("Skew", {"chains": ["c_bar"]}, "a record for another version"),
                          ("NoTq", {"chains": ["c_bar"]}, "a bar check that names no queue selection"),
                          ("Nowhere", {"chains": ["c_bar"]}, "a mod with no pipeline record")):
        r = P.refusal(mod, sel, "BENCH", ROOT)
        check(bool(r), "refused before queueing: %s" % why)
        if r:
            ok = all(str(r.get(k) or "").strip() for k in ("clause", "observed", "would_pass", "criterion_why")) \
                and str((r.get("smallest_fix") or {}).get("what") or "").strip() and r.get("criterion_verdict") == "sound"
            check(ok, "  and its refusal says what was seen, what would pass and the smallest fix: %s" % r.get("text"))
    r = P.refusal("Building", {"chains": ["c_bar"]}, "BENCH", ROOT) or {}
    check("maturation.py advance Building" in r.get("would_pass", "") + str(r.get("smallest_fix")),
          "a Stage 3 mod's refusal names the move that lets it run: %s" % r.get("would_pass"))
    for by in P.OPS_REQUESTERS:
        check(P.refusal("Building", {"chains": ["c_any"]}, by, ROOT) is None,
              "an ops job (%s) is not a test and is never refused" % by)
    check(P.refusal("Building", {"chains": ["c_any"]}, "BENCH.filler", ROOT) is not None, "the filler is not ops")
    q = os.environ["TESTQ_QUEUE"]
    os.environ["TESTQ_PIPELINE_ADMIT"] = "open"
    try:
        check(P.refusal("Building", {"chains": ["c_any"]}, "BENCH", ROOT) is None, "the selftest seam opens on a temp queue")
        os.environ["TESTQ_QUEUE"] = "/mnt/d/ClaudeWork/rimmandrake/testq"     # the real queue, by its literal path
        check(P.refusal("Building", {"chains": ["c_any"]}, "BENCH", ROOT) is not None,
              "and never on the real queue SteveDesktop runs")
        del os.environ["TESTQ_QUEUE"]
        check(P.refusal("Building", {"chains": ["c_any"]}, "BENCH", ROOT) is not None, "nor with TESTQ_QUEUE unset")
    finally:
        os.environ["TESTQ_QUEUE"] = q
        del os.environ["TESTQ_PIPELINE_ADMIT"]


def ns(mod, by, chains="c_x", **kw):
    d = dict(mod=mod, chains=chains, rows=None, item=None, full=False, purpose="guard", by=by, sha="abc1234",
             for_item=None, profile=None, priority=30, not_before=None, supersedes=None, owner_gate=None,
             lane="stevedesktop", deploy=None, timeout=7200, no_canary=False, no_validity=False, no_sha_check=True,
             retest_why=None, row_item=[])
    d.update(kw)
    return argparse.Namespace(**d)


REACHED = "PREVIEW_REACHED"


def run_submit(a):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = T.cmd_submit(a)
    return rc, out.getvalue()


def testq_checks():
    T.ensure_dirs()
    saved = T.preview
    T.preview = lambda mod, sel: {"refusal": REACHED, "rows": None, "drivers": [], "chains": []}
    try:
        rc, out = run_submit(ns("Building", "BENCH"))
        check(rc == 2 and "REFUSED" in out and REACHED not in out and "pipeline" in out.lower(),
              "submit refuses a non-pipeline test before anything else: %r" % out.strip()[:200])
        check(not os.listdir(T.q("pending")), "and nothing is queued")
        rc, out = run_submit(ns("Ready", "BENCH", chains="c_bar"))
        check(REACHED in out, "a pipeline test passes the gate to the usual checks: %r" % out.strip()[:120])
        rc, out = run_submit(ns("Building", "BENCH.steward-wake"))
        check(REACHED in out, "the steward's repair job is not gated: %r" % out.strip()[:120])
        # the brake-release canary: Operations' own submit path, on a mod no pipeline names
        saved_rank = T.fill_rank
        T.fill_rank = lambda mod, n, now, today=None, exclude=(): {"verdict": "pick", "pick": ["c_x"], "purpose": "guard",
                                                                    "row_items": {}}
        try:
            req = BR.canary_request("Building", [], 0)
            rc, line = BR.submit("Building", req)
        finally:
            T.fill_rank = saved_rank
        check(REACHED in line, "the brake-release canary is not gated: %r" % line[:120])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = T.cmd_sweep(argparse.Namespace(mod="Building", by="BENCH", for_item=None, priority=None))
        check(rc == 0 and "no sweep" in out.getvalue() and REACHED not in out.getvalue(),
              "the nightly sweep of a non-pipeline mod stops quietly (exit 0, the timer stays green): %r"
              % out.getvalue().strip()[:160])
    finally:
        T.preview = saved
    plan = T.fill_plan("Building", 4, 200, 8 * 3600, 0)
    check(plan.get("verdict") == "pipeline" and "advance" in plan.get("text", ""),
          "the filler is off for a mod no pipeline names, and says what would turn it on: %s" % plan.get("text"))
    job = dict(T.S.make_job("Building", {"chains": ["c_x"]}, "guard", "BENCH.filler", "abc1234", item="SOME_ITEM"))
    saved_span = FM.job_span
    FM.job_span = lambda rec: (0, 10 ** 12)
    try:
        check(FM.rerun_job({"job": job}, now=10 ** 12) is None, "a fault-window rerun of a non-pipeline test is not queued")
        ops = dict(job, requested_by="Operations.canary")
        check(FM.rerun_job({"job": ops}, now=10 ** 12) is not None, "an ops job's fault-window rerun still is")
    finally:
        FM.job_span = saved_span


def steward_checks():
    saved = (T.steve_running, T.paused, ST.tick_timer_state)
    T.steve_running, T.paused, ST.tick_timer_state = (lambda: []), (lambda host=None: None), (lambda: "active")
    for d in ("pending", "running"):
        for f in os.listdir(T.q(d)):
            os.remove(T.q(d, f))
    try:
        ls = ST.lane_state(1.0e9, mods=["Building", "Draft"])
    finally:
        T.steve_running, T.paused, ST.tick_timer_state = saved
    check(ls["state"] == "IDLE_BY_RULE" and ls["fault_at"] is None and ls["settled"],
          "a queue empty by rule is settled, never a stall or idle fault: %s" % ls)


MUTANTS = {
    "no_gate": lambda: setattr(P, "refusal", lambda *a, **k: None),
    "ops_gated": lambda: setattr(P, "OPS_REQUESTERS", ()),
    "offline_counts": lambda: setattr(P, "BAR_STAGES", ("6", "4-5")),
    "stage_ignored": lambda: setattr(P, "PAST_BLIND", P.PAST_BLIND + ("offline_build",)),
    "filler_on": lambda: setattr(T, "pipeline_fill", lambda mod: (None, None)),
    "idle_is_fault": lambda: setattr(ST, "BY_RULE_SETTLED", False),
    "seam_on_real_queue": lambda: setattr(P, "REAL_QUEUE", "/nonexistent/testq"),
}


def main():
    if "--mutants" in sys.argv:
        bad = []
        for m in MUTANTS:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mutant", m], capture_output=True,
                               text=True, timeout=300)
            n = r.stdout.count("\nFAIL") + r.stdout.startswith("FAIL")
            print("%s  mutant %s: exit %d, %d check(s) failed" % ("ok  " if r.returncode == 1 else "FAIL", m,
                                                                   r.returncode, n))
            if r.returncode != 1:
                bad.append(m)
        print("%d of %d mutants caught" % (len(MUTANTS) - len(bad), len(MUTANTS)))
        return 1 if bad else 0
    if "--mutant" in sys.argv:
        MUTANTS[sys.argv[sys.argv.index("--mutant") + 1]]()
    for f in (pipeline_checks, testq_checks, steward_checks):
        f()
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
