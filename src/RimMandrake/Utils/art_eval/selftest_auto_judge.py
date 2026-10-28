#!/usr/bin/env python3
"""Selftest for auto_judge.py (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE): the slot gate, owner series stops, the
facing rows' judged-by-artpipe-job check, HOLD_ERROR never a verdict, the fauna job filter. Pure parts + a pass with
every outside call (scan, gate, probe, subprocess) replaced; temp dirs only, no model call, no git."""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import auto_judge as AJ  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def main():
    # ---- the gate: the spawn hook's numbers decide; DARK is never a judging time
    check("DARK closes the gate even with slots", not AJ.gate_ok({"mode": "DARK", "n": 6, "running": 0})[0])
    check("N=0 closes the gate", not AJ.gate_ok({"mode": "CRUISE", "n": 0, "running": 0})[0])
    check("BENCH running N helpers closes the gate", not AJ.gate_ok({"mode": "BURN", "n": 3, "running": 3})[0])
    check("a free slot opens the gate", AJ.gate_ok({"mode": "CRUISE", "n": 3, "running": 2})[0])

    # ---- HOLD_ERROR is a transport failure: the job stays owed
    recs = [("audit_a", {"subject": "RM_A_n", "artpipe_job": "arteval_RM_A_r2_n", "decision": "REGEN"}),
            ("audit_b", {"subject": "RM_B", "artpipe_job": "arteval_RM_B_r3", "decision": "HOLD_ERROR"}),
            ("audit_t", {"subject": "RM_C", "decision": "ACCEPT"})]
    jj = AJ.judged_jobs(recs)
    check("judged_jobs: a verdict counts, HOLD_ERROR and job-less records do not", jj == {"arteval_RM_A_r2_n"}, jj)
    check("hold_errors lists the subjects", AJ.hold_errors([r for _, r in recs]) == ["RM_B"])

    # ---- facing rows: per-view subject keys come from the driver's state, never from a name scan
    state = {
        "RM_A_n": {"group": "g1", "row": {"id": "arteval_RM_A_r2_n", "target_def": "RM_A", "facings": ["north"]}},
        "RM_B": {"group": "g1", "row": {"id": "arteval_RM_B_r3", "target_def": "RM_B", "facings": ["south"]}},
        "RM_A__dessicated_n": {"group": "g2", "row": {"id": "arteval_RM_A__dessicated_r3_n", "target_def": "RM_A",
                                                      "facings": ["north"]}},
        "RM_D": {"group": "g2", "row": {"id": "arteval_RM_D_r1", "target_def": "RM_D", "facings": ["east"]}},
        "RM_E": {"group": "g2", "done": True, "row": {"id": "arteval_RM_E_r1", "target_def": "RM_E"}},
        "RM_F": {"group": "g3", "row": {"id": "arteval_RM_F_r2", "target_def": "RM_F", "facings": ["east"]}},
    }
    ok_jobs = lambda r: r["id"] != "arteval_RM_D_r1"          # D's render still pending
    stopped = lambda d: d == "RM_F"                         # owner ended F's series
    got = AJ.facing_owed(state, jj, ok_jobs, stopped)
    check("facing: judged row skipped, HOLD_ERROR row owed, pending/done/stopped skipped",
          got == [("RM_B", "g1"), ("RM_A__dessicated_n", "g2")], got)
    got2 = AJ.facing_owed(state, jj, ok_jobs, lambda d: d == "RM_A")
    check("facing: a stop on the target def covers its per-view rows", ("RM_A__dessicated_n", "g2") not in got2, got2)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # ---- fauna source: pipeline regen jobs only; a facing-audit job of the same id shape is not fauna
        done = td / "done"
        done.mkdir()
        for name, item in (("arteval_RM_Surrik_s2r2_south", AJ.FAUNA_ITEM),
                           ("arteval_RM_Surrik_s2r2_east", AJ.FAUNA_ITEM),
                           ("arteval_RM_Pyre_r1_north", AJ.FAUNA_ITEM),
                           ("arteval_RM_Shoal_r3_east", "FACING_AUDIT_BUILD_REDRAW_BATCH"),
                           ("arteval_RM_Odd_south", AJ.FAUNA_ITEM)):
            (done / f"{name}.json").write_text(json.dumps({"rimflow_item_id": item}))
        (done / "arteval_RM_Man_r1_south.manifest.json").write_text(json.dumps({"rimflow_item_id": AJ.FAUNA_ITEM}))
        fd = AJ.fauna_defs(done)
        check("fauna_defs: pipeline jobs by item id, series tags parsed, facing + manifests + untagged out",
              fd == ["RM_Pyre", "RM_Surrik"], fd)

        # ---- a fauna candidate judged under any production run (the facing audit) is not proposed again
        sp = []
        for job in ("arteval_RM_Fuzzrunner_s2r1", "arteval_RM_Surrik_s2r2"):
            p = td / f"{job}.spec.json"
            p.write_text(json.dumps({"artpipe_job": job}))
            sp.append(str(p))
        uj = AJ.unjudged_specs(sp, {"arteval_RM_Fuzzrunner_s2r1"})
        check("unjudged_specs drops a job judged elsewhere", [Path(x).name for x in uj] == ["arteval_RM_Surrik_s2r2.spec.json"], uj)
        check("chunks of 2", AJ.chunks([1, 2, 3, 4, 5]) == [[1, 2], [3, 4], [5]])

        # ---- a pass: nothing reaches a model unless something is owed, the gate is open and the probe passes
        AJ.SCRATCH, AJ.STATUS = td / "scratch", td / "scratch/status.json"
        calls = []
        owed = {"fauna_defs": [], "facing": [("RM_B", "g1")]}
        AJ.scan = lambda: owed
        AJ.probe = lambda: (calls.append("probe"), (False, "429"))[1]
        AJ.sh = lambda *a, **k: calls.append(("sh", a)) or 0

        class A:
            max_subjects, dry_run = 4, False

        AJ.gate = lambda now=None: calls.append("gate") or {"mode": "DARK", "n": 6, "running": 0}
        AJ.cmd_run(A)
        st = json.loads(AJ.STATUS.read_text())
        check("DARK: no probe, no command, result says gate closed",
              calls == ["gate"] and st["result"].startswith("gate closed"), (calls, st.get("result")))
        calls.clear()
        AJ.gate = lambda now=None: calls.append("gate") or {"mode": "CRUISE", "n": 2, "running": 2}
        AJ.cmd_run(A)
        check("running >= N: no probe, no command", calls == ["gate"], calls)
        calls.clear()
        owed.update(facing=[])
        AJ.cmd_run(A)
        check("nothing owed: the gate is not even asked", calls == [] and "nothing owed" in
              json.loads(AJ.STATUS.read_text())["result"], calls)
        calls.clear()
        owed.update(facing=[("RM_B", "g1")])
        AJ.gate = lambda now=None: {"mode": "CRUISE", "n": 3, "running": 0}
        AJ.cmd_run(A)
        st = json.loads(AJ.STATUS.read_text())
        check("failed quota probe: no judge command, backs off an hour",
              calls == ["probe"] and st["backoff_until"] > time.time() + 3000, (calls, st))
        calls.clear()
        AJ.cmd_run(A)
        check("inside the backoff: nothing runs", calls == [] and "backing off" in
              json.loads(AJ.STATUS.read_text())["result"], calls)
    print("FAILED: " + ", ".join(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
