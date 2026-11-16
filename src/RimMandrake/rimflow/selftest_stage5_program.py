#!/usr/bin/env python3
"""Selftest of stage five by program (RIMMANDRAKE_CARRY_STAGE_FIVE_BY_PROGRAM_TEN_RELAY_RUNS; cheap-guards spec 3.3):
after the pre-launch coverage judge, role_launch.stage5_program closes a stage-5 run through designer_stage.close_run
when the verdict leaves nothing to decide, and the unit ends without a model; a rejected close puts stage.json back and
the Designer runs. Fixture concepts in a temp dir; no network, no systemd, no model."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import concept_tree as CT  # noqa: E402
import designer_stage as DS  # noqa: E402
import role_launch as RL  # noqa: E402

FAILS = []
RUN = "rm-role-designer-1"


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def concept(root, name, verdict):
    d = os.path.join(root, "design", "concepts", name)
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(root, os.path.dirname(CT.OWNER_SHARD)), exist_ok=True)
    with open(os.path.join(d, "tree.json"), "w") as f:
        json.dump({"kind": "mod", "leaves": []}, f)
    st = {"stage": 5, "status": "ready", "item": "FOO_ITEM", "mod": name, "results": [], "history": [],
          "budget": {"cap": 4000000, "reserve": 60000, "spent": 0, "charges": []}}
    st["running"] = {"run": RUN, "stage": 5, "manifest": {}, "reserved": 90000, "at": DS.now_iso(),
                     "inputs": DS.inputs(d, st, root), "owner_uncited": []}
    DS.write_json(DS.state_path(d), st)
    if verdict is not None:
        DS.write_json(os.path.join(d, "coverage_verdict.json"), dict(verdict, tree=CT.tree_hash(CT.load(d))))
    return d


def gap(gid, to=3):
    return {"gid": gid, "ids": ["leaf_" + gid], "return_to": to, "what": "scene for %s lacks a control" % gid}


NC = {"verdict": "not_covered", "signed": False, "judge": "rm-coverage-judge-7", "gaps": [gap("g1"), gap("g2")]}


def test_close_and_reject(root):
    d = concept(root, "Returns", NC)
    how, line = RL.stage5_program(d, RUN, sync=False)
    st = DS.load_state(d)
    last = (st.get("results") or [{}])[-1]
    check(how == "closed" and st["stage"] == 3 and st.get("running") is None and last.get("by") == "program"
          and last.get("outcome") == "return" and "g2" in str(st.get("pending_decision")),
          "not_covered, every gap to 3: closed by program, the concept is at stage 3: %s %r" % (line, last))
    check(st["budget"]["spent"] == 0 and os.path.exists(os.path.join(d, "result.%s.json" % RUN)),
          "nothing charged, and the result file is kept as a Designer's would be")
    check(RL.program_closed(d, RUN) == ("closed", last), "program_closed finds the run the program closed")
    # covered and signed in the verdict, but the gate finds no valid signature on the tree: close_run rejects it
    d2 = concept(root, "Rejected", {"verdict": "covered", "signed": True, "judge": "rm-coverage-judge-8", "gaps": []})
    with open(DS.state_path(d2), "rb") as f:
        before = json.loads(f.read())
    how, line = RL.stage5_program(d2, RUN, sync=False)
    st2 = DS.load_state(d2)
    check(how == "designer" and "rejected" in line and st2.get("running", {}).get("run") == RUN
          and st2["stage"] == 5 and st2.get("results") == before["results"] and st2["budget"] == before["budget"],
          "a rejected program result leaves the run open, unchanged, for the Designer: %s" % line)
    check(any(h.get("what") == "program_rejected" for h in st2.get("history") or [])
          and os.path.exists(os.path.join(d2, "result.%s.program-rejected.json" % RUN))
          and not os.path.exists(os.path.join(d2, "result.json")),
          "the rejection is one history line and a kept file; no result.json is left for the Designer to trip on")
    check(RL.program_closed(d2, RUN) is None, "program_closed: a rejected program result is not a program close")
    # a gap that needs his answer, and no verdict at all: the Designer, nothing written
    d3 = concept(root, "Asks", dict(NC, gaps=[gap("g1"), gap("g2", 2)]))
    how, _ = RL.stage5_program(d3, RUN, sync=False)
    check(how == "designer" and DS.load_state(d3)["running"]["run"] == RUN, "a gap returning to stage 2: the Designer")
    d4 = concept(root, "NoVerdict", None)
    check(RL.stage5_program(d4, RUN, sync=False)[0] == "designer", "no verdict on file: the Designer")
    check(RL.stage5_program(concept(root, "Other", NC), "rm-role-designer-9", sync=False)[0] == "designer",
          "a unit that is not the open run closes nothing")
    # the CLI step: a crash says DID NOT RUN, exits 0 (the Designer runs) and leaves a line the supervisor alarms on
    d5 = concept(root, "Crash", NC)
    real = RL.stage5_program

    def boom(*a, **k):
        raise OSError("disk gone")
    RL.stage5_program = boom
    os.environ["RM_ROLE_UNIT"] = RUN
    try:
        rc = RL.main(["stage5-program", d5])
    finally:
        RL.stage5_program = real
        os.environ.pop("RM_ROLE_UNIT", None)
    check(rc == 0 and RL.program_closed(d5, RUN) == ("error", "run %s: stage5-program DID NOT RUN: OSError: disk gone; "
                                                     "the Designer runs as today" % RUN),
          "a step that cannot run: exit 0 (the Designer runs) and a program_error line: %r" % (
              RL.program_closed(d5, RUN),))
    env = dict(os.environ, RM_ROLE_UNIT=RUN, RM_JUDGE_SYNC="0")
    d6 = concept(root, "CliClose", NC)
    r = subprocess.run([sys.executable, os.path.join(HERE, "role_launch.py"), "stage5-program", d6], env=env,
                       capture_output=True, text=True)
    check(r.returncode == RL.PRE_DONE_EXIT and DS.load_state(d6)["stage"] == 3,
          "the CLI step exits PRE_DONE_EXIT when it closed the run (%d %s)" % (r.returncode, r.stdout.strip()[:120]))


def test_pre_steps(root):
    d = concept(root, "Pre", NC)
    pre = RL.coverage_pre(d)
    check(pre == [["python3", "src/RimMandrake/rimflow/role_launch.py", "stage5-judge", d],
                  ["python3", "src/RimMandrake/rimflow/role_launch.py", "stage5-program", d]],
          "stage 5: the judge (through its stage check), then the program step: %r" % pre)
    # Contagion 2026-11-16: a run asked at stage 5 reopened stage 3 at its open (inputs changed); the judge step then
    # skipped but exited STOP over an old advisory verdict and the stage-3 Designer never started. The step reads the
    # stage when it runs: not 5 -> exit 0, no judge (RIMMANDRAKE_UNSTICK_FIVE_STILL_MODS_TWO_OF_TWELVE_MOVING)
    d3 = concept(root, "Pre3", dict(NC, advisory="UNTESTED brief", stopped="judge spend over its limit"))
    st3 = DS.load_state(d3)
    st3["stage"] = 3
    DS.write_json(DS.state_path(d3), st3)
    called = []
    real_run = RL.subprocess.run
    RL.subprocess.run = lambda *a, **k: called.append(a) or type("P", (), {"returncode": 3})()
    try:
        rc = RL.main(["stage5-judge", d3])
    finally:
        RL.subprocess.run = real_run
    check(rc == 0 and not called, "stage5-judge at stage 3: exit 0 and no judge run (rc %r, calls %r)" % (rc, called))
    role = {"name": "Designer", "clone": "/c", "model": "opus", "seat": "BENCH"}
    with tempfile.TemporaryDirectory() as td:
        mark = os.path.join(td, "claude-ran")
        for rc, want_rc, want_ran in ((RL.PRE_DONE_EXIT, 0, False), (0, 0, True), (1, 1, False), (3, 3, False)):
            if os.path.exists(mark):
                os.remove(mark)
            argv = RL.launch_argv(dict(role, pre_launch=[["true"], ["sh", "-c", "exit %d" % rc]]), "u", "m", "/o", "/e",
                                  "/opt/bin/claude")
            body = argv[argv.index("--") + 1:]
            body = body[:4] + ["sh", "-c", "touch '%s'" % mark]
            p = subprocess.run(body, capture_output=True, text=True)
            check(p.returncode == want_rc and os.path.exists(mark) == want_ran,
                  "a pre-step exiting %d: unit exit %d, model %s" % (rc, p.returncode, "starts" if want_ran else
                                                                     "never starts"))


def test_supervisor():
    """A unit the program closed: harvested done with 0 tokens, no close_run a second time, chained to stage 3."""
    import selftest_designer_chain as SC
    rs = {"runs": [{"state": "running", "unit": RUN, "at": SC.T - 600, "day": RL.day_of(SC.T), "budget": 90000,
                    "mode": "run", "item": "X_ITEM", "concept": SC.C1, "scope": "S.scope", "marker": "M"}]}
    closes, acts = [], []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: None, "procs": lambda *a, **k: [],
           "program_closed": lambda c, u: ("closed", {"outcome": "return", "to": 3, "by": "program"}),
           "stage_close": lambda c, u, t: (closes.append(u), (True, []))[1], "stage_land": lambda c, u: None,
           "stage_turn": lambda c: None, "stage_status": lambda c: {"stage": 3, "status": "ready"}}
    RL._supervise_one("Designer", rs, dict(RL.ROLE_DEFAULTS, **SC.designer_row()), obs, SC.T,
                      lambda **kw: acts.append(kw), set())
    run = rs["runs"][0]
    check(run["state"] == "done" and run["tokens"] == 0 and run.get("by") == "program" and closes == []
          and not [a for a in acts if a["do"] == "alarm"],
          "a program-closed unit: done, 0 tokens, no second close, no alarm: %r" % [(a["do"], a.get("kind")) for a in acts])
    check(any(a["do"] == "role_done" and "no model started" in a["why"] for a in acts)
          and (rs.get("run_now") or {}).get("concept") == SC.C1,
          "it is said on the ledger and the concept chains to its stage-3 run: %r" % rs.get("run_now"))
    rs2 = {"runs": [{"state": "running", "unit": "u2", "at": SC.T - 600, "day": RL.day_of(SC.T), "budget": 90000,
                     "mode": "run", "item": "X_ITEM", "concept": SC.C1, "scope": "S.scope", "marker": "M"}]}
    acts2 = []
    obs2 = dict(obs, result=lambda r: {"subtype": "success", "usage": {k: 10 for k in RL.USAGE_KEYS}},
                program_closed=lambda c, u: ("error", "run u2: stage5-program DID NOT RUN: boom"))
    RL._supervise_one("Designer", rs2, dict(RL.ROLE_DEFAULTS, **SC.designer_row()), obs2, SC.T,
                      lambda **kw: acts2.append(kw), set())
    check(closes == ["u2"] and [a.get("kind") for a in acts2 if a["do"] == "alarm"] == ["role:Designer:stage5_program"],
          "a Designer run whose program step did not run: closed as today, and the step's alarm raised")


def main():
    saved = DS.REPO
    with tempfile.TemporaryDirectory() as root:
        DS.REPO = root
        try:
            test_close_and_reject(root)
            test_pre_steps(root)
        finally:
            DS.REPO = saved
    test_supervisor()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
