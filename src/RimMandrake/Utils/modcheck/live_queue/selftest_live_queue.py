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
    common.sandbox_dry_outputs(job.outdir)
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
    common.DRY_OUTDIR = os.path.join(tmp, "out")          # job outdirs (fake PNGs) live and die with this test
    res = os.path.join(tmp, "r.jsonl")
    os.environ["LIVE_QUEUE_RESULTS"] = res
    old_argv = sys.argv
    sys.argv = [sys.argv[0]]
    sv = os.path.join(tmp, "Saves")
    os.makedirs(sv)
    with open(os.path.join(sv, "keeper.rws"), "wb") as f:
        f.write(b"k" * 5000)
    os.environ["LQ_SAVES_DIR"], os.environ["LQ_SAVE_WAIT"] = sv, "0"
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
        rec = run_body("preflight", no_census)
        check("preflight FAILs when the companion does not answer", rec["verdict"] == "FAIL", rec["failed"])

        import situational_rerun as rerun
        jb = common.Job("judge_selftest", dry_run=True)
        bad = [{"mod": "FlowWorks", "refused": "validated must-show lines no component claims: x", "budget_unmeasured": [],
                "unbland_chains": [], "surprises": [{"chain": "c", "sidecar": "/nonexistent.json", "png": None}]},
               {"mod": "Antiquities", "refused": "", "budget_unmeasured": ["reading/x"], "unbland_chains": ["reading"],
                "surprises": []}]
        rerun.judge(jb, bad, ["Ninefold: KeyError: x"])
        check("situational_rerun judge FAILs each of: crash, FlowWorks refused, budget, unbland, missing evidence",
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
        rec = run_body("abort_proof", blind_hostiles)
        check("abort_proof FAILs when hazards do not reach the detectors",
              rec["verdict"] == "FAIL" and "hazard hostile_raid: aborts via hostile_pawns with sidecar on disk, game paused"
              in rec["failed"] and any("predator" in f for f in rec["failed"]), rec["failed"])

        def noisy(w):
            w.at(w.ticks + 300, lambda W: W.add_fire(100, 100))   # a fire nobody asked for, inside the quiet control
        rec = run_body("abort_proof", noisy)
        check("abort_proof FAILs when the quiet control is not quiet", any("control_quiet" in f for f in rec["failed"]), rec["failed"])

        def wildlife_stays(w):
            w._t_jawa_destroy_bulk = lambda **k: {"success": True, "matchedCount": 0, "destroyed": []}
        rec = run_body("bland_tile", wildlife_stays)
        check("bland_tile FAILs when the arrival wildlife is not cleared", "no wildlife left on the map" in rec["failed"], rec["failed"])

        def roads(w):
            w.tile_overrides = {4375: {"roadCount": 1}}
        rec = run_body("bland_tile", roads)
        check("bland_tile FAILs when the only candidate tile carries a road", rec["verdict"] == "FAIL", rec["failed"])

        def no_damage_log(w):
            w.recorder_installed = False
        rec = run_body("companion_live", no_damage_log)
        check("companion_live FAILs when damage_log cannot be read (no direct read -> no colonist_damaged)",
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
        rec = run_body("motion_frames", frozen_frames)
        check("motion_frames FAILs when every frame is byte-identical", "frames are not all byte-identical" in rec["failed"], rec["failed"])

        # ---- saved_base: naming, save proof, load-reset, cleanup fallback
        import saved_base as BW
        for n_ in os.listdir(sv):
            if n_ != 'keeper.rws':
                os.remove(os.path.join(sv, n_))      # bland_base's dry run wrote the base; start the unit tests clean
        from rimdrive.fake import FakeWorld, pawn_row
        def clean_world():
            w = FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103), pawn_row("Col3", x=106)])
            w.settled, w.saves_dir = {4375}, sv
            w.dialogs = ["Dialog_NamePlayerFactionAndSettlement"]
            return w
        w = clean_world()
        check("naming dialog is open before naming", bool(BW._window_types(w)[0]))
        check("induce_and_finish_naming names the colony and leaves no dialog", BW.induce_and_finish_naming(w) == [] and w.named)
        w2 = clean_world()
        w2._t_jawa_name_colony = lambda **k: {"success": False, "message": "refused"}
        w2._t_jawa_window_list_close = lambda **k: {"success": True, "windows": [{"typeName": "Dialog_NamePlayerSettlement"}]}
        check("naming FAILs when the tool refuses and a dialog stays", len(BW.induce_and_finish_naming(w2)) == 2)
        before = BW.snapshot_saves(sv)
        r = BW.save_base(w, sv, wait=0)
        check("save_base verifies a NEW file and no changed keeper", r["verified"] and r["sizeBytes"] > 1000, r)
        check("keeper untouched", BW.snapshot_saves(sv)["keeper.rws"] == before["keeper.rws"])
        wl = clean_world()
        wl.modes.add("save_wrong_slot")
        wl.current_save = "keeper"
        wl.saves_dir = sv
        wl._t_rimworld_save_game_orig = wl._t_rimworld_save_game
        r2 = BW.save_base(wl, sv, name="OTHER", wait=0)
        check("save_base FAILs when save_game writes the wrong slot (no new file)", not r2["verified"], r2)
        r3 = BW.save_base(w, sv, wait=0)
        check("save_base refuses to overwrite an existing base", not r3["verified"])
        # dirty world: hostile + wildlife + fire + dead colonist + 21 colonists + queued incident
        def dirty(w):
            w.pawns["Raider1"] = pawn_row("Raider1", kind="Pirate", faction="TribeRough", is_player=False, hostile=True)
            w.pawns["Wolf1"] = pawn_row("Wolf1", kind="Wolf", faction=None, is_player=False, intelligence="Animal")
            w.pawns["Col1"]["dead"], w.pawns["Col1"]["spawned"] = True, False
            for i in range(18):
                w.pawns["Extra%d" % i] = pawn_row("Extra%d" % i, x=120 + i)
            w.add_fire(90, 90)
            w.queue.append({"defName": "RaidEnemy", "fireTick": 999})
        import helpers as H
        dw = clean_world()
        BW.induce_and_finish_naming(dw)
        BW.save_base(dw, sv, name="SELFTEST_BASE", wait=0)
        dirty(dw)
        check("dirty world FAILs assert_bland before reset", len(H.assert_bland(dw)) >= 3, H.assert_bland(dw))
        rr = BW.world_reset(dw, save_name="SELFTEST_BASE", saves_dir=sv)
        check("world_reset by LOAD passes assert_bland", rr["method"] == "load" and rr["problems"] == [], rr)
        dw2 = clean_world()
        dirty(dw2)
        dw2.dialogs = []
        rf = BW.world_reset(dw2, save_name="NO_SUCH_SAVE", saves_dir=sv, keep_colonists=3)
        check("fallback cleanup: removes hostile/wildlife/fire/queue, revives, but 20 colonists remain -> still FAILs honestly",
              rf["method"] == "cleanup" and any("colonists, expected" in p for p in rf["problems"])
              and not any("hostiles" in p or "wildlife" in p or "fires" in p or "dead colonists" in p for p in rf["problems"])
              and dw2.queue == [], rf)
        rn = BW.world_reset(dw2, save_name="NO_SUCH_SAVE", saves_dir=sv, fallback=False)
        check("no save and no fallback is a failure", rn["problems"])

        # ---- run_next: order, skip-past-UNMEASURED, done
        open(res, "w").close()
        check("empty results -> next is preflight", jobs.next_job(path=res)["id"] == "preflight")
        with open(res, "a") as f:
            f.write(json.dumps({"job": "preflight", "status": "MEASURED", "verdict": "PASS"}) + "\n")
            f.write(json.dumps({"job": "situational_rerun", "status": "UNMEASURED", "verdict": None}) + "\n")
        check("preflight done, situational_rerun UNMEASURED -> next is situational_rerun again", jobs.next_job(path=res)["id"] == "situational_rerun")
        check("--all skips past an UNMEASURED job", jobs.next_job(path=res, skip={"situational_rerun"})["id"] == "abort_proof")
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
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    n = sum(_results)
    print("\n%d/%d passed" % (n, len(_results)))
    return 0 if n == len(_results) else 1


if __name__ == "__main__":
    sys.exit(main())
