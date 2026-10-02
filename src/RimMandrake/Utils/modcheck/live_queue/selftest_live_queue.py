"""Offline selftest for the northstar live queue: every job dry-runs on FakeWorld, run_next walks the queue in
order and skips past an UNMEASURED job, and every criterion CAN fail (a sabotaged world turns each job's
verdict to FAIL or UNMEASURED, never PASS).
Run: python3 src/RimMandrake/Utils/modcheck/live_queue/selftest_live_queue.py
"""
import json
import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import common            # noqa: E402
import jobs              # noqa: E402

_results = []


def check(name, cond, detail=""):
    _results.append(bool(cond))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + str(detail)[:400]) if (detail and not cond) else ""))


def run_body(mod_name, sabotage=None, builder=None):
    """Import a job module and run its body on a (possibly sabotaged) FakeWorld; return the record."""
    m = __import__(mod_name)
    job = common.Job(mod_name + "_selftest", dry_run=True)
    from rimdrive.fake import FakeWorld, pawn_row
    w = (builder or getattr(m, "fake_world", None) or
         (lambda: FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103), pawn_row("Col3", x=106)])))()
    if sabotage:
        sabotage(w)
    try:
        m.body(w, job)
    except common.Unmeasurable as e:
        job.unmeasured(e)
    except Exception as e:                                       # noqa: BLE001
        job.unmeasured("%s: %s" % (type(e).__name__, e))
    return job.finish()


def main():
    tmp = tempfile.mkdtemp(prefix="lq_self_")
    res = os.path.join(tmp, "r.jsonl")
    os.environ["LIVE_QUEUE_RESULTS"] = res
    old_argv = sys.argv
    sys.argv = [sys.argv[0]]
    try:
        # ---- every job passes its dry run
        for j in jobs.JOBS:
            mod = j["file"][:-3]
            rec = run_body(mod)
            check("%s dry run is MEASURED PASS" % j["id"], rec["status"] == "MEASURED" and rec["verdict"] == "PASS",
                  rec.get("failed") or rec.get("unmeasured_reason"))

        # ---- criteria can FAIL
        def no_census(w):
            w._t_jawa_pawn_census = lambda **k: {"success": False, "message": "absent"}
        rec = run_body("j0_preflight", no_census)
        check("J0 FAILs when the companion does not answer", rec["verdict"] == "FAIL", rec["failed"])

        import j1_situational_rerun as j1
        jb = common.Job("j1_judge_selftest", dry_run=True)
        bad = [{"mod": "FlowWorks", "refused": "validated must-show lines no component claims: x", "budget_unmeasured": [],
                "unbland_chains": [], "surprises": [{"chain": "c", "sidecar": "/nonexistent.json", "png": None}]},
               {"mod": "Antiquities", "refused": "", "budget_unmeasured": ["reading/x"], "unbland_chains": ["reading"],
                "surprises": []}]
        j1.judge(jb, bad, ["Ninefold: KeyError: x"])
        check("J1 judge FAILs each of: crash, FlowWorks refused, budget, unbland, missing evidence",
              [c["ok"] for c in jb.checks] == [False] * 5, jb.checks)

        def blind_hostiles(w):
            orig = w._t_jawa_spawn_pawn

            def spawn(**k):        # hostiles arrive non-hostile and invisible to the detector
                r = orig(**k)
                for p in r["pawns"]:
                    w.pawns[p["id"]]["hostile"] = False
                    w.pawns[p["id"]]["faction"] = "PlayerColony" if k.get("faction") == "player" else w.pawns[p["id"]]["faction"]
                return r
            w._t_jawa_spawn_pawn = spawn
            w._t_jawa_ordered_job = lambda **k: {"success": True, "accepted": True}   # the hunt never starts
            w._t_jawa_incident_schedule = lambda **k: {"success": True}                # nothing queued
        rec = run_body("j2_abort_proof", blind_hostiles)
        check("J2 FAILs when hazards do not reach the detectors",
              rec["verdict"] == "FAIL" and "hazard hostile_raid: aborts via hostile_pawns with sidecar on disk, game paused"
              in rec["failed"] and any("predator" in f for f in rec["failed"]), rec["failed"])

        def noisy(w):
            w.at(w.ticks + 300, lambda W: W.add_fire(100, 100))   # a fire nobody asked for, inside the quiet control
        rec = run_body("j2_abort_proof", noisy)
        check("J2 FAILs when the quiet control is not quiet", any("control_quiet" in f for f in rec["failed"]), rec["failed"])

        def wildlife_stays(w):
            w._t_jawa_destroy_bulk = lambda **k: {"success": True, "matchedCount": 0, "destroyed": []}
        rec = run_body("j3_bland_tile", wildlife_stays)
        check("J3 FAILs when the arrival wildlife is not cleared", "no wildlife left on the map" in rec["failed"], rec["failed"])

        def roads(w):
            w.tile_overrides = {4375: {"roadCount": 1}}
        rec = run_body("j3_bland_tile", roads)
        check("J3 FAILs when the only candidate tile carries a road", rec["verdict"] == "FAIL", rec["failed"])

        def no_damage_log(w):
            w.recorder_installed = False
        rec = run_body("j4_companion_live", no_damage_log)
        check("J4 FAILs when damage_log cannot be read (no direct read -> no colonist_damaged)",
              rec["verdict"] == "FAIL" and any("damage" in f for f in rec["failed"]), rec["failed"])

        def frozen_frames(w):
            from rimdrive.fake import make_png
            png = make_png(1280, 720, 1)

            def shot(fileName="x", **_):
                p = os.path.join(w.shot_dir, "%s.png" % fileName)
                with open(p, "wb") as f:
                    f.write(png)
                return {"success": True, "path": p}
            w._t_rimworld_take_screenshot = shot
        rec = run_body("j5_motion_frames", frozen_frames)
        check("J5 FAILs when every frame is byte-identical", "frames are not all byte-identical" in rec["failed"], rec["failed"])

        # ---- run_next: order, skip-past-UNMEASURED, done
        open(res, "w").close()
        check("empty results -> next is J0", jobs.next_job(path=res)["id"] == "J0_preflight")
        with open(res, "a") as f:
            f.write(json.dumps({"job": "J0_preflight", "status": "MEASURED", "verdict": "PASS"}) + "\n")
            f.write(json.dumps({"job": "J1_situational_rerun", "status": "UNMEASURED", "verdict": None}) + "\n")
        check("J0 done, J1 UNMEASURED -> next is J1 again", jobs.next_job(path=res)["id"] == "J1_situational_rerun")
        check("--all skips past an UNMEASURED job", jobs.next_job(path=res, skip={"J1_situational_rerun"})["id"] == "J2_abort_proof")
        with open(res, "a") as f:
            for j in jobs.JOBS:
                f.write(json.dumps({"job": j["id"], "status": "MEASURED", "verdict": "FAIL"}) + "\n")
        check("a MEASURED FAIL counts as done (a finding, not a re-run)", jobs.next_job(path=res) is None)
        out = subprocess.run([sys.executable, os.path.join(_HERE, "run_next.py"), "--list", "--dry-run"],
                             capture_output=True, text=True, env=dict(os.environ))
        check("run_next --list prints every job and the next pointer",
              all(j["id"] in out.stdout for j in jobs.JOBS) and "next: (queue done)" in out.stdout, out.stdout[-300:])
        check("job ids are unique and every job file exists",
              len({j["id"] for j in jobs.JOBS}) == len(jobs.JOBS) and
              all(os.path.isfile(os.path.join(_HERE, j["file"])) for j in jobs.JOBS))
        check("suite_mods() derives a non-empty list from the status registry", len(jobs.suite_mods()) >= 1)
    finally:
        sys.argv = old_argv
    n = sum(_results)
    print("\n%d/%d passed" % (n, len(_results)))
    return 0 if n == len(_results) else 1


if __name__ == "__main__":
    sys.exit(main())
