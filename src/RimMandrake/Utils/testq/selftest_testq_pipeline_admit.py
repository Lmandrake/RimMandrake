#!/usr/bin/env python3
"""selftest_testq_pipeline_admit.py - what SteveDesktop's test queue admits (pipeline_admit.py).

The owner, 2026-11-17 about 11:00 AM PST: "Drop 11-14 limits, old rule. Clear its limitations." His card of 2026-11-14
(spec 18c, "Pipeline tests only") is dropped (item RIMMANDRAKE_DROP_STEVEDESKTOP_PIPELINE_ONLY_LIMIT): any mod's job is
admitted whatever its pipeline stage, a --full sweep and an --item selection included. What stays refused: a mod on his
hold (rimflow/mod_owner_hold.json, 2026-11-16), and every test when that list cannot be read. Ops jobs are never refused.

  python3 selftest_testq_pipeline_admit.py               every check; exit 1 on any failure
  python3 selftest_testq_pipeline_admit.py --mutant M    the same checks with guard M reverted: must exit 1
  python3 selftest_testq_pipeline_admit.py --mutants     run every mutant; exit 0 only if each one is caught

A temp design/concepts tree, a temp hold list and a temp queue stand in for the real ones; no git push, ledger, ssh or
game is touched.
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
HOLDS = os.path.join(TMP, "mod_owner_hold.json")
SAID = "And stop the new biome mods work. Only Pyrelands as a biome mod right now."
with open(HOLDS, "w") as f:
    json.dump({"holds": [{"mod": "Heldmod", "date": "2026-11-16", "said": SAID}]}, f)
os.environ["RM_OWNER_HOLD_FILE"] = HOLDS

import pipeline_admit as P  # noqa: E402
import testq as T  # noqa: E402
import brake_release as BR  # noqa: E402
import fault_monitor as FM  # noqa: E402
import steward as ST  # noqa: E402
import coverage as C  # noqa: E402

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
concept("Building", "offline_build")                         # before the blind challenge
concept("Blind", "blind_challenge")                          # Pyrelands' and Graffiti's stage on 2026-11-17
concept("Draft", "in_game", state="draft")                   # not locked
concept("Skew", "in_game", rec_version="0.0.9")              # the record is for another version
concept("NoTq", "in_game", tests={"sc_bar": {"id": "sc_bar", "stage": "6"}})    # a bar check with no queue selection
concept("Heldmod", "in_game")                                # on his hold: refused even past blind


def record_checks():
    q = P.qualifying(ROOT)      # the pipeline record reader testq_blocks.py and coverage.pipeline_mods use
    check(set(q) == {"Ready", "Passed", "NoTq", "Heldmod"}, "the record reader still names the mod versions past the "
          "blind challenge (it admits and refuses nothing): %s" % sorted(q))
    check(q.get("Ready", {}).get("chains") == {"c_bar"}, "and the chains their stage-6 bars name: %s" % q.get("Ready"))


def admission_checks():
    for mod, sel, why in (("Ready", {"chains": ["c_bar", "c_other"]}, "a chain no bar names"),
                          ("Ready", {"chains": ["c_offline"]}, "an offline-stage check"),
                          ("Ready", {"full": True}, "a whole --full sweep"),
                          ("Ready", {"item": "SOME_ITEM"}, "an --item selection"),
                          ("Building", {"chains": ["c_bar"]}, "a mod at offline_build"),
                          ("Blind", {"chains": ["c_any"]}, "a mod at blind_challenge"),
                          ("Draft", {"chains": ["c_bar"]}, "an unlocked version"),
                          ("Skew", {"chains": ["c_bar"]}, "a record for another version"),
                          ("NoTq", {"chains": ["c_x"]}, "a mod whose bars name no queue selection"),
                          ("Nowhere", {"chains": ["c_x"]}, "a mod with no pipeline record (GimmeSomeSlack's case)")):
        r = P.refusal(mod, sel, "BENCH", ROOT)
        check(r is None, "admitted whatever its pipeline stage: %s%s" % (why, "" if r is None else ": " + r["text"]))
    for spelling in ("Heldmod", "design/concepts/Heldmod", "RimMandrake/Heldmod/"):
        r = P.refusal(spelling, {"chains": ["c_bar"]}, "BENCH", ROOT)
        check(bool(r), "a mod on his hold is refused (%s)" % spelling)
        if r:
            ok = all(str(r.get(k) or "").strip() for k in ("clause", "observed", "would_pass", "criterion_why")) \
                and str((r.get("smallest_fix") or {}).get("what") or "").strip()
            check(ok and SAID in r["text"] and "2026-11-16" in r["text"] and "lift" in r["text"],
                  "  and its refusal quotes his words and date and names the lift: %s" % r.get("text"))
    check(P.refusal("Heldmod", {"chains": ["c_bar"]}, "BENCH.filler", ROOT) is not None, "the filler is not ops")
    for by in P.OPS_REQUESTERS:
        check(P.refusal("Heldmod", {"chains": ["c_any"]}, by, ROOT) is None,
              "an ops job (%s) is not a test and is never refused" % by)
    os.environ["RM_OWNER_HOLD_FILE"] = os.path.join(TMP, "absent.json")
    try:
        r = P.refusal("Building", {"chains": ["c_x"]}, "BENCH", ROOT)
        check(bool(r) and "hold" in r["text"], "an unreadable hold list refuses every test (nothing is queued that "
              "cannot be proved unheld): %s" % (r or {}).get("text"))
    finally:
        os.environ["RM_OWNER_HOLD_FILE"] = HOLDS


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
        for a, why in ((ns("Blind", "BENCH"), "a blind_challenge mod's chain"),
                       (ns("Nowhere", "BENCH"), "a mod with no pipeline record"),
                       (ns("Ready", "BENCH", chains=None, full=True, purpose="sweep"), "a --full sweep")):
            rc, out = run_submit(a)
            check(REACHED in out, "submit passes %s to the usual checks: %r" % (why, out.strip()[:160]))
        rc, out = run_submit(ns("Heldmod", "BENCH"))
        check(rc == 2 and "REFUSED" in out and REACHED not in out and "HELD BY OWNER" in out,
              "submit refuses a held mod before anything else: %r" % out.strip()[:200])
        check(not os.listdir(T.q("pending")), "and nothing is queued")
        rc, out = run_submit(ns("Heldmod", "BENCH.steward-wake"))
        check(REACHED in out, "the steward's repair job is not gated: %r" % out.strip()[:120])
        saved_rank = T.fill_rank
        T.fill_rank = lambda mod, n, now, today=None, exclude=(): {"verdict": "pick", "pick": ["c_x"], "purpose": "guard",
                                                                    "row_items": {}}
        try:
            rc, line = BR.submit("Heldmod", BR.canary_request("Heldmod", [], 0))
        finally:
            T.fill_rank = saved_rank
        check(REACHED in line, "the brake-release canary is not gated: %r" % line[:120])
        for mod, held in (("Heldmod", True), ("Blind", False)):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = T.cmd_sweep(argparse.Namespace(mod=mod, by="BENCH", for_item=None, priority=None))
            o = out.getvalue()
            if held:
                check(rc == 0 and "no sweep" in o and "HELD BY OWNER" in o and REACHED not in o,
                      "the nightly sweep of a held mod stops quietly (exit 0): %r" % o.strip()[:160])
            else:
                check(REACHED in o, "the nightly sweep of a blind_challenge mod reaches submit: %r" % o.strip()[:160])
    finally:
        T.preview = saved
    plan = T.fill_plan("Heldmod", 4, 200, 8 * 3600, 0)
    check(plan.get("verdict") == "held" and SAID in plan.get("text", ""),
          "the filler is off for a held mod and quotes his hold: %s" % plan.get("text"))
    plan = T.fill_plan("Blind", 4, 200, 8 * 3600, 0)
    check(plan.get("verdict") not in ("held", "pipeline"), "the filler walks a blind_challenge mod: %s %s"
          % (plan.get("verdict"), plan.get("text", "")[:120]))
    saved_span = FM.job_span
    FM.job_span = lambda rec: (0, 10 ** 12)
    try:
        for mod, want in (("Blind", True), ("Heldmod", False)):
            job = dict(T.S.make_job(mod, {"chains": ["c_x"]}, "guard", "BENCH.filler", "abc1234", item="SOME_ITEM"))
            got = FM.rerun_job({"job": job}, now=10 ** 12) is not None
            check(got == want, "a fault-window rerun of %s %s queued" % (mod, "is" if want else "is not"))
        job = dict(T.S.make_job("Heldmod", {"chains": ["c_x"]}, "guard", "Operations.canary", "abc1234", item="X"))
        check(FM.rerun_job({"job": job}, now=10 ** 12) is not None, "an ops job's fault-window rerun still is")
    finally:
        FM.job_span = saved_span


def steward_checks():
    saved = (C.read_wired, C.pipeline_mods, os.environ.pop("TESTQ_FILL_MODS", None))
    C.read_wired, C.pipeline_mods = (lambda path=None: ["FlowWorks", "Heldmod", "Blind"]), (lambda: ["Ready"])
    try:
        got = C.fill_mods()
    finally:
        C.read_wired, C.pipeline_mods = saved[:2]
        if saved[2] is not None:
            os.environ["TESTQ_FILL_MODS"] = saved[2]
    check(got == ["FlowWorks", "Blind", "Ready"], "the filler's mod list drops held mods and keeps the rest: %s" % got)
    check(not hasattr(ST, "BY_RULE_SETTLED"), "the steward has no IDLE_BY_RULE state left (the 18c lane idle)")


MUTANTS = {
    "stage_gate_back": lambda: setattr(P, "refusal", (lambda real: lambda mod, sel, by, root=None: real(
        mod, sel, by, root) or (None if P.standing(mod, root)[0] or by in P.OPS_REQUESTERS else {"text": "18c"}))(
        P.refusal)),
    "full_refused": lambda: setattr(P, "refusal", (lambda real: lambda mod, sel, by, root=None: real(
        mod, sel, by, root) or ({"text": "full"} if (sel or {}).get("full") else None))(P.refusal)),
    "no_hold": lambda: setattr(P, "held_by_owner", lambda mod: None),
    "ops_gated": lambda: setattr(P, "OPS_REQUESTERS", ()),
    "unreadable_calm": lambda: setattr(P, "_holds", lambda: {}),
    "fill_held": lambda: setattr(T, "held_fill", lambda mod: None),
    "fill_mods_held": lambda: setattr(C, "unheld", lambda mods: list(mods)),
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
    for f in (record_checks, admission_checks, testq_checks, steward_checks):
        f()
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
