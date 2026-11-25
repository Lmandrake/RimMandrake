#!/usr/bin/env python3
"""Selftest for auto_judge.py (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE): the slot gate, owner series stops, the
facing rows' judged-by-artpipe-job check, HOLD_ERROR never a verdict, the fauna job filter. Pure parts + a pass with
every outside call (scan, gate, probe, subprocess) replaced; temp dirs only, no model call, no git."""
from __future__ import annotations

import contextlib
import json
import sys
import tempfile
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import auto_judge as AJ  # noqa: E402

FAILS = []
REAL_SH = AJ.sh


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def main():
    # ---- the gate: the spawn hook's numbers decide; DARK is never a judging time
    check("DARK closes the gate even with slots", not AJ.gate_ok({"mode": "DARK", "n": 6, "running": 0})[0])
    # RIMMANDRAKE_FIX_ART_JUDGE_TIMER_IDLE_SINCE_NOV_EIGHT: N is the window's helper count, and token limits are advisory
    # (owner 2026-11-02). 80 of 170 passes since 11-07 read "allocator N=0" while the account had room.
    check("N=0 does not close the gate", AJ.gate_ok({"mode": "CRUISE", "n": 0, "running": 0})[0])
    check("helpers running in the window do not close the gate", AJ.gate_ok({"mode": "BURN", "n": 3, "running": 3})[0])
    check("the pipeline's own pause or account hold closes the gate, by its words",
          AJ.gate_ok({"mode": "CRUISE", "n": 3, "running": 0, "held": "the pipeline is paused"}) ==
          (False, "the pipeline is paused"))
    check("no reading of the mode is not DARK", AJ.gate_ok({"mode": None, "held": None})[0])

    # ---- HOLD_ERROR is a transport failure: the job stays owed
    recs = [("audit_a", {"subject": "RM_A_n", "artpipe_job": "arteval_RM_A_r2_n", "decision": "REGEN"}),
            ("audit_b", {"subject": "RM_B", "artpipe_job": "arteval_RM_B_r3", "decision": "HOLD_ERROR"}),
            ("audit_t", {"subject": "RM_C", "decision": "ACCEPT"})]
    jj = AJ.judged_jobs(recs)
    check("judged_jobs: a verdict counts, HOLD_ERROR and job-less records do not", jj == {"arteval_RM_A_r2_n"}, jj)
    hc = [("f", {"subject": "RM_D", "artpipe_job": "arteval_RM_D_r1", "decision": "HOLD_CANVAS"})]
    check("a canvas hold is a verdict for a facing row and none for a fauna candidate",
          AJ.judged_jobs(hc) == {"arteval_RM_D_r1"} and AJ.judged_jobs(hc, AJ.NO_VERDICT_FAUNA) == set())
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
        AJ.gate = lambda now=None: calls.append("gate") or {"mode": "CRUISE", "n": 2, "running": 0, "held": "pipe off: x"}
        AJ.cmd_run(A)
        check("held: no probe, no command", calls == ["gate"], calls)
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
    idle_since_nov_eight()
    installs_and_unfiled()
    compare_veto()
    for t in (t_newest_verdict_decides,
              t_no_fourth_round,
              t_discharged_leaves_the_list,
              t_regen_below_the_cap_is_filed,
              t_unfiled_is_an_item,
              t_capped_is_noted_once,
              t_vetoed_escalation_is_noted,
              t_same_pass_files_the_next_round,
              t_due_tells_four_answers,
              t_files_from_the_judging_clone):
        t()
    print("FAILED: " + ", ".join(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


def idle_since_nov_eight():
    """RIMMANDRAKE_FIX_ART_JUDGE_TIMER_IDLE_SINCE_NOV_EIGHT: a row whose def is gone, a driver that fails, a commit with
    nothing in it, and a first redraw filed as <DEF>__live, each read as "judged 0" or as a failed commit for 15 days."""
    import subprocess
    # ---- a facing row whose def is gone is not owed; a def that could not be looked up stays owed
    owed = [("RM_Gone__Larva", "g"), ("RM_Here", "g"), ("RM_Blind", "g")]
    st = {"RM_Gone__Larva": {"row": {"target_def": "RM_Gone"}}, "RM_Here": {"row": {}}, "RM_Blind": {"row": {"target_def": "RM_Blind"}}}
    keep, gone = AJ.split_gone(owed, st, lambda d: {"RM_Gone": False, "RM_Here": True}.get(d))
    check("a row whose def is gone leaves the owed list and is named; unknown stays owed",
          keep == [("RM_Here", "g"), ("RM_Blind", "g")] and gone == ["RM_Gone__Larva"], (keep, gone))
    here = AJ.def_exists
    check("def_exists reads src: a real def True, a made-up one False", here("RM_Harrok") is True and here("RM_NoSuchDefEver") is False)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        # ---- <DEF>__live_r1 is the def's round r1, filed under its first pass's candidate name
        done = td / "done"
        done.mkdir()
        (done / "arteval_RM_Harrok__live_r1_south.json").write_text(json.dumps({"rimflow_item_id": AJ.FAUNA_ITEM}))
        check("a __live redraw is owed under its def", AJ.fauna_defs(done) == ["RM_Harrok"], AJ.fauna_defs(done))

        # ---- a commit with nothing new is not a failure
        repo = td / "repo"
        repo.mkdir()
        for c in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", *c], cwd=repo, check=True)
        (repo / "a.json").write_text("{}")
        saved, saved_sleep, saved_sh = AJ.ROOT, AJ.time.sleep, AJ.sh
        AJ.ROOT, AJ.sh = repo, REAL_SH
        slept = []
        AJ.time.sleep = lambda s: slept.append(s) if s >= 1 else saved_sleep(s)
        try:
            one = AJ.commit(["a.json"], "first", td / "log")
            two = AJ.commit(["a.json"], "again", td / "log")
        finally:
            AJ.ROOT, AJ.time.sleep, AJ.sh = saved, saved_sleep, saved_sh
        check("the first commit lands", len(one) == 10 and "failed" not in one, one)
        check("a commit with nothing new says so, and does not retry", two == "nothing to commit" and not slept, (two, slept))

        # ---- the driver imports pnglib from where the image skills live now
        env = AJ.driver_env()
        r = subprocess.run([sys.executable, "-c", "import pnglib"], env=env, cwd=str(td), capture_output=True, text=True)
        check("the driver's environment can import pnglib", r.returncode == 0, r.stderr[-200:])

        # ---- a driver that makes no spec is said, fails the pass, and commits nothing
        keep = (AJ.SCRATCH, AJ.STATUS, AJ.scan, AJ.gate, AJ.probe, AJ.sh, AJ.load_drv, AJ.DRV, AJ.commit)
        AJ.SCRATCH, AJ.STATUS, AJ.DRV = td / "scratch", td / "scratch/status.json", td / "drv.py"
        (td / "state.json").write_text(json.dumps({"RM_B": {"row": {}}}))
        commits = []
        AJ.scan = lambda: {"fauna_defs": [], "facing": [("RM_B", "g1")]}
        AJ.gate = lambda now=None: {"mode": "CRUISE", "n": 0, "running": 0, "held": None}
        AJ.probe = lambda: (True, "probe ok")
        AJ.sh = lambda *a, **k: 1
        AJ.load_drv = lambda: None
        AJ.commit = lambda *a, **k: commits.append(a) or "x"

        class A:
            max_subjects, dry_run = 4, False
        try:
            rc = AJ.cmd_run(A)
            got = json.loads(AJ.STATUS.read_text())
        finally:
            AJ.SCRATCH, AJ.STATUS, AJ.scan, AJ.gate, AJ.probe, AJ.sh, AJ.load_drv, AJ.DRV, AJ.commit = keep
        check("a row the driver made no spec for is named and the pass fails",
              rc == 1 and got.get("spec_failed") == ["RM_B"] and "no spec" in got["result"], (rc, got.get("result")))
        check("a pass that judged nothing commits nothing", commits == [], commits)


PLAN = """RimMandrake.Biomes mandrake.rm.biomes         9 file(s) HELD
    H  Biomes/Cauldron/northstar/live.json   (repo-only; not deployed)
           held: live result JSONs
    ~  Biomes/LeaningScrub/Textures/Things/Pawn/Animal/RM_Fuzzviper/RM_Fuzzviper_north.png
    +  Biomes/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/FurnaceBeast/FurnaceBeast_Giant_south.png
"""


def installs_and_unfiled():
    """ARTEVAL_REGEN_ROWS_FIX_MISSING_TARGET (a REGEN that files nothing becomes an item) and the install of ACCEPTed
    art through fauna_drive install / drv.py install, then a deploy applied only when the plan is all committed art."""
    check("slug strips the tier prefix", AJ.slug("RM_FireHawk") == "FIREHAWK" and AJ.slug("RM_Foo__dessicated_n") == "FOO_DESSICATED_N")
    with tempfile.TemporaryDirectory() as td:
        st = Path(td)
        r1 = st / "runs/fauna_auto_x"
        r1.mkdir(parents=True)
        (r1 / "regen_jobs.json").write_text(json.dumps([{"id": "arteval_RM_FireHawk_r2", "target_def": "RM_FireHawk"},
                                                       {"id": "arteval_RM_Ok_r2", "target_def": "RM_Ok"}]))
        (r1 / "regen_filing.json").write_text(json.dumps({"ok": False, "rc": 1, "why": "fill_queue exit 1",
                                                         "filed": ["arteval_RM_Ok_r2"], "unfiled": ["arteval_RM_FireHawk_r2"]}))
        r2 = st / "runs/fauna_auto_y"
        r2.mkdir(parents=True)
        (r2 / "regen_filing.json").write_text(json.dumps({"ok": True, "unfiled": []}))
        r3 = st / "runs/fauna_auto_z"
        r3.mkdir(parents=True)
        (r3 / "regen_filing.json").write_text(json.dumps({"ok": False, "rc": None, "why": "fill_queue timed out", "unfiled": []}))
        r4 = st / "runs/fauna_auto_old"          # a pre-verification record: ok false, no unfiled list -> ask the queue
        r4.mkdir(parents=True)
        (r4 / "regen_jobs.json").write_text(json.dumps([{"id": "arteval_RM_A_r2", "target_def": "RM_A", "facings": ["south"]},
                                                       {"id": "arteval_RM_B_r2", "target_def": "RM_B", "facings": ["south"]}]))
        (r4 / "regen_filing.json").write_text(json.dumps({"ok": False, "rc": 1, "why": "fill_queue exit 1"}))
        q = st / "queue"
        (q / "done").mkdir(parents=True)
        (q / "done/arteval_RM_A_r2_south.json").write_text("{}")
        u = AJ.unfiled_rows(["fauna_auto_x", "fauna_auto_y", "fauna_auto_z", "fauna_auto_old", "fauna_auto_none"], state=st, queue=q)
        check("unfiled rows: one per unfiled row with its def; an unverified filing asks the queue; no jobs file -> lost",
              [(x["def"], x["id"]) for x in u] == [("RM_FireHawk", "arteval_RM_FireHawk_r2"), (None, None),
                                                   ("RM_B", "arteval_RM_B_r2")], u)
        check("an unfiled row's item is named for its def", AJ.unfiled_item_id(u[0]) == "ARTEVAL_FIX_REGEN_UNFILED_FIREHAWK")
        check("a filing with no jobs file is one shared item", AJ.unfiled_item_id(u[1]) == "ARTEVAL_REGEN_FILING_FIX_JOBS_LOST")
        long_id = AJ.unfiled_item_id({"def": "RM_Somewhat_Very_Long_Defname_2", "run": "r"})
        check("a long def still names a valid item (<=44 chars, one twist word, no trailing number)",
              len(long_id) <= 44 and long_id.count("_") == 4 and not long_id[-1].isdigit(), long_id)

        # ---- ACCEPT -> the commands that install it (never a hand copy)
        cmp_root = st / "cmp"
        acc = {"subject": "RM_FurnaceBeast", "candidate": "r2", "decision": "ACCEPT"}
        cmds = AJ.install_cmds(acc, "fauna", spec="/s/RM_FurnaceBeast_r2.spec.json", cmp_root=cmp_root)
        flat = [" ".join(map(str, c)) for c in cmds]
        check("fauna ACCEPT: head-to-head compare then fauna_drive install of that round",
              len(flat) == 2 and "fauna_compare.py RM_FurnaceBeast --cand /s/RM_FurnaceBeast_r2.spec.json --out " + str(cmp_root / "RM_FurnaceBeast_r2") in flat[0]
              and flat[1].endswith("fauna_drive.py install RM_FurnaceBeast --round 2"), flat)
        (cmp_root / "RM_FurnaceBeast_r2").mkdir(parents=True)
        (cmp_root / "RM_FurnaceBeast_r2/compare.json").write_text(json.dumps({"winner": "B", "install_b": True}))
        check("an existing compare is not paid for twice",
              len(AJ.install_cmds(acc, "fauna", spec="/s/x.json", cmp_root=cmp_root)) == 1)
        (cmp_root / "RM_FireWasp_r2").mkdir(parents=True)
        (cmp_root / "RM_FireWasp_r2/compare.json").write_text(json.dumps({"error": "reply JSON does not parse"}))
        check("a compare that errored is paid for again (an error is no verdict)",
              len(AJ.install_cmds(dict(acc, subject="RM_FireWasp"), "fauna", spec="/s/x.json", cmp_root=cmp_root)) == 2)
        check("series tag s2r1 installs round 1", AJ.install_cmds(dict(acc, candidate="s2r1"), "fauna", spec="/s/x.json",
                                                                  cmp_root=cmp_root)[-1][-1] == "1")
        check("a REGEN installs nothing", AJ.install_cmds(dict(acc, decision="REGEN"), "fauna", spec="/s/x", cmp_root=cmp_root) == [])
        check("fauna ACCEPT with no spec found installs nothing (compare needs it)",
              AJ.install_cmds(dict(acc, candidate="r3"), "fauna", spec=None, cmp_root=cmp_root) == [])
        fc = AJ.install_cmds({"subject": "RM_Fuzzviper_n", "decision": "ACCEPT"}, "facing", drv=Path("/d/drv.py"))
        check("facing ACCEPT: drv.py install <subject>", [list(map(str, c)) for c in fc] == [["python3", "/d/drv.py", "install", "RM_Fuzzviper_n"]], fc)

        # ---- which repo files an install wrote (its own records, not a git scan that would sweep a peer's files)
        fi = [json.dumps({"def": "RM_FurnaceBeast", "tag": "r2", "files": [{"mod": "RimMandrake/Pyrelands", "rel": "Things/F/F_south.png"}]}),
              json.dumps({"def": "RM_Other", "tag": "r2", "files": [{"mod": "RimMandrake/Pyrelands", "rel": "Things/O_south.png"}]})]
        check("fauna installed paths from fauna_installs.jsonl", AJ.fauna_installed(fi, "RM_FurnaceBeast", "r2") ==
              ["src/RimMandrake/Pyrelands/Textures/Things/F/F_south.png"])
        ev = [json.dumps({"type": "live", "mod": "src/RimMandrake/LeaningScrub", "rel": "Things/V/RM_Fuzzviper_north.png"}),
              json.dumps({"type": "live", "mod": "src/RimMandrake/LeaningScrub", "rel": "Things/V/RM_Fuzzviperling_north.png"}),
              json.dumps({"type": "ruling", "rel": "Things/V/RM_Fuzzviper_north.png"})]
        check("facing installed paths from the art ledger's live events under the row's texPath",
              AJ.facing_installed(ev, "Things/V/RM_Fuzzviper") == ["src/RimMandrake/LeaningScrub/Textures/Things/V/RM_Fuzzviper_north.png"])

        # ---- deploy: target, plan line -> repo file, and the apply rule
        fold = {"LeaningScrub": ("RimMandrake.Biomes", "LeaningScrub"), "Wreckage": ("RimMandrake.Biomes", "Wreckage")}
        check("a folded biome deploys through the composite",
              AJ.deploy_target("src/RimMandrake/LeaningScrub/Textures/a.png", fold) == ("compose:biomes", ["--compose", "biomes"]))
        check("a standalone mod deploys with --mod", AJ.deploy_target("src/RimStarWars/Foo/Textures/a.png", fold) ==
              ("src/RimStarWars/Foo", ["--mod", "Foo"]))
        rs = AJ.plan_resolver("compose:biomes", fold)
        check("composite plan line -> source file", rs("Biomes/LeaningScrub/Textures/x.png") == "src/RimMandrake/LeaningScrub/Textures/x.png"
              and rs("Biomes/_Kits/Wreckage/Defs/a.xml") == "src/RimMandrake/Wreckage/Defs/a.xml" and rs("Biomes/Nope/x.png") is None)
        check("standalone plan line -> mod file", AJ.plan_resolver("src/RimStarWars/Foo", fold)("Textures/x.png") == "src/RimStarWars/Foo/Textures/x.png")
        fold["Pyrelands"] = ("RimMandrake.Biomes", "Pyrelands")
        rs = AJ.plan_resolver("compose:biomes", fold)
        ok, why, files = AJ.deploy_verdict(PLAN, rs, lambda ps: [])
        check("all drift committed png: apply", ok and len(files) == 2, (ok, why, files))
        ok, why, _ = AJ.deploy_verdict(PLAN, rs, lambda ps: [ps[0]])
        check("an uncommitted png holds the deploy", not ok and "uncommitted" in why, why)
        ok, why, _ = AJ.deploy_verdict(PLAN + "    -  Biomes/Pyrelands/Defs/x.xml   (in game, not in repo)\n", rs, lambda ps: [])
        check("a '-' line holds the deploy", not ok and "-" in why, why)
        ok, why, _ = AJ.deploy_verdict(PLAN + "    ~  Biomes/Pyrelands/Defs/x.xml\n", rs, lambda ps: [])
        check("a non-texture line holds the deploy", not ok and "x.xml" in why, why)
        ok, why, _ = AJ.deploy_verdict(PLAN + "    ~  Biomes/Nope/a.png\n", rs, lambda ps: [])
        check("an unresolvable line holds the deploy", not ok and "Nope" in why, why)
        ok, why, _ = AJ.deploy_verdict(PLAN + "DEF GUARD: --apply of this plan would be REFUSED\n", rs, lambda ps: [])
        check("a def-guard refusal holds the deploy", not ok, why)
        ok, why, _ = AJ.deploy_verdict(PLAN.split("    ~")[0], rs, lambda ps: [])
        check("no drift: nothing to apply", not ok and "in sync" in why, why)
        # ---- post_run: the ACCEPT runs its installers, the unfiled row becomes an item, installed paths come back
        calls = []
        saved = (AJ.sh, AJ.STATE, AJ.FAUNA_INSTALLS, AJ.git_dirty, AJ.DATA)
        AJ.STATE, AJ.DATA = st, st
        (st / "art_eval/fauna_cands/auto_1").mkdir(parents=True)
        (st / "art_eval/fauna_cands/auto_1/RM_FurnaceBeast_r2.spec.json").write_text("{}")
        AJ.FAUNA_INSTALLS = st / "fi.jsonl"

        envs = []

        def fake_sh(cmd, cwd, log, timeout=0, env=None):     # the signature of AJ.sh
            calls.append([str(c) for c in cmd])
            envs.append(env)
            if "install" in calls[-1] and "fauna_drive.py" in calls[-1][1]:
                AJ.FAUNA_INSTALLS.write_text(fi[0] + "\n")
            return 1 if calls[-1][-2:] == ["show", "ARTEVAL_FIX_REGEN_UNFILED_FIREHAWK"] else 0
        AJ.sh = fake_sh
        AJ.git_dirty = lambda ps: list(ps)
        import runner as RR
        RR.storage_root = lambda: st / "nostore"
        stt = {"follow_ups": []}
        AJ.ARTPIPE_QUEUE = st / "queue"
        changed, every = AJ.post_run([("fauna_auto_x", {"subject": "RM_FurnaceBeast", "candidate": "r2", "decision": "ACCEPT"}),
                                      ("fauna_auto_x", {"subject": "RM_FireHawk", "candidate": "r1", "decision": "REGEN"})],
                                     [], st / "log", stt)
        names = [" ".join(c[1:3]) for c in calls]
        check("post_run: unfiled row is filed as an item", any(c[-2:] == ["show", "ARTEVAL_FIX_REGEN_UNFILED_FIREHAWK"] for c in calls)
              and any("file" in c and "ARTEVAL_FIX_REGEN_UNFILED_FIREHAWK" in c for c in calls), calls)
        filed = [e for c, e in zip(calls, envs) if "file" in c and "ARTEVAL_FIX_REGEN_UNFILED_FIREHAWK" in c]
        check("post_run: the filing names its program (filing_gate.py)", filed and all(
            (e or {}).get("RM_FILING_PROGRAM") == "auto_judge.file_item" for e in filed),
            [(e or {}).get("RM_FILING_PROGRAM") for e in filed])
        check("post_run: ACCEPT compares (spec found in the cands dir) then installs; REGEN installs nothing",
              any(c[1].endswith("fauna_compare.py") and c[4].endswith("auto_1/RM_FurnaceBeast_r2.spec.json") for c in calls)
              and sum(c[1].endswith("fauna_drive.py") for c in calls) == 1, names)
        check("post_run: installed files come back for commit and deploy",
              every == ["src/RimMandrake/Pyrelands/Textures/Things/F/F_south.png"] and changed == every and not stt["follow_ups"], (every, stt))
        AJ.sh, AJ.STATE, AJ.FAUNA_INSTALLS, AJ.git_dirty, AJ.DATA = saved
        ok, why, _ = AJ.deploy_verdict("", rs, lambda ps: [])
        check("an empty plan (the tool died) is not 'in sync'", not ok and "in sync" not in why, why)


def compare_veto():
    """ARTEVAL_COMPARE_VETO_FIX_ACCEPT_LIMBO: an ACCEPT the head-to-head refuses becomes a REGEN carrying the compare's
    reason, never limbo (FireHawk r2: burning-log perch in every facing; FireWasp r2: north an overhead view)."""
    why = "B is better but every facing has a burning log perch baked in as a ground prop, a hard defect."
    check("install_b false is a veto with its reason", AJ.compare_veto({"winner": "B", "install_b": False, "reason": why}) == why)
    check("install_b true is no veto", AJ.compare_veto({"winner": "B", "install_b": True, "reason": "x"}) is None)
    check("an errored compare is no verdict, no veto", AJ.compare_veto({"error": "reply JSON does not parse"}) is None)
    check("no compare is no veto", AJ.compare_veto(None) is None)
    acc = {"subject": "RM_FireHawk", "candidate": "r2", "decision": "ACCEPT", "module": "walker", "reasons": ["gpt strong_accept"],
           "round": 1, "canvas_rule": 512}
    v = AJ.veto_record(acc, {"install_b": False, "reason": why}, "A lean raptor. Painterly.", nreg=1)
    check("veto: ACCEPT becomes REGEN of the next round", v["decision"] == "REGEN" and v["round"] == 2 and v["candidate"] == "r2", v.get("round"))
    pr = v["regen"]["request"]["prompt"]
    check("veto: next prompt keeps the base prompt and carries the compare's reason",
          "A lean raptor." in pr and "burning log perch" in pr, pr)
    check("veto: finding names the compare", v["regen"]["findings"] == ["COMPARE_VETO"] and any("head-to-head" in x for x in v["reasons"]))
    check("veto: the original record is untouched", acc["decision"] == "ACCEPT")
    ow = "The north facing is an overhead view of the creature, a top-down plan, not a rear view."
    import runner as RR0
    vo = AJ.veto_record(dict(acc, subject="RM_FireWasp"), {"install_b": False, "reason": ow}, "A wasp. Show all facings alike.", nreg=1)
    rows = RR0.regen_jobs([vo], "run_x", neutralize=lambda p: ("A wasp.", "sonnet"), texpath_of=lambda d: "Things/X")
    pr = rows[0]["prompt"]
    check("veto reason naming an overhead view survives the per-facing gate into the filed prompt",
          rows[0]["facings"] and not RR0._gate_hits(pr) and "Correct what the previous attempt got wrong" in pr
          and "north facing" in pr and "from above" in pr, pr)
    e = AJ.veto_record(acc, {"install_b": False, "reason": why}, "x", nreg=3)
    check("veto at the round cap escalates, files nothing", e["decision"] == "ESCALATE" and not e.get("regen"), e["decision"])
    with tempfile.TemporaryDirectory() as td:
        st = Path(td)
        run = st / "runs/fauna_auto_q"
        run.mkdir(parents=True)
        (run / "run.json").write_text(json.dumps({"test": False}))
        (run / "decisions.jsonl").write_text(json.dumps(dict(acc, decision="REGEN", candidate=None, round=1, image_sha256={"south": "0"})) + "\n"
                                             + json.dumps(dict(acc, decision="REGEN", candidate="r1", round=2, image_sha256={"south": "a"})) + "\n"
                                             + json.dumps(dict(acc, image_sha256={"south": "b"})) + "\n")
        (run / "regen_jobs.json").write_text(json.dumps([{"id": "arteval_RM_FireHawk_r2", "prompt": "A lean raptor. Painterly."}, {"id": "arteval_RM_FireHawk__x_s1r2", "prompt": "WRONG VARIANT"}]))
        filed = []
        import runner as RR
        saved = (AJ.STATE, RR.file_regen_jobs)
        AJ.STATE = st
        RR.file_regen_jobs = lambda f, **k: (filed.append(json.loads(Path(f).read_text())) or {"ok": True, "unfiled": []})
        stt = {"follow_ups": []}
        try:
            out = AJ.veto_to_regen("fauna_auto_q", acc, {"install_b": False, "reason": why}, stt)
            rows = [json.loads(x) for x in (run / "decisions.jsonl").read_text().splitlines()]
            check("veto_to_regen appends the REGEN record to the run's decisions", rows[-1]["decision"] == "REGEN" and rows[-1]["candidate"] == "r2" and len(rows) == 4, rows[-1])
            check("veto_to_regen files the next round to the queue with the reason in its prompt",
                  len(filed) == 1 and filed[0][0]["id"] == "arteval_RM_FireHawk_r3" and "burning log perch" in filed[0][0]["prompt"] and "WRONG VARIANT" not in filed[0][0]["prompt"], filed)
            check("a vetoed ACCEPT is not vetoed twice", AJ.already_vetoed(AJ.run_records("fauna_auto_q"), acc))
        finally:
            AJ.STATE, RR.file_regen_jobs = saved


# ---- follow-ups (design/specs/2026-11-24-art-auto-judge/boundary.md). RIMMANDRAKE_RENDER_TWELVE_FACING_REDRAWS_JUDGED_
# REGEN_NOBODY_FILED: 12 rows judged REGEN with rounds left waited from 11-06 to 11-24, and 86 follow-ups had no reader.
A1, A2, A3 = "2026-11-06T10:00:00-08:00", "2026-11-07T10:00:00-08:00", "2026-11-08T10:00:00-08:00"
VETO = {"at": A1, "subject": "RM_V", "run": "fv", "owed": "escalate to the owner (round cap) after a compare veto"}


class A:
    max_subjects, dry_run = 4, False


def row(i, d="RM_A"):
    return {"id": i, "target_def": d, "target_texpath": "T/" + d, "facings": ["north"]}


def rec(job, dec, at, sub="x"):
    return {"artpipe_job": job, "decision": dec, "at": at, "subject": sub}


@contextlib.contextmanager
def rig():
    """The driver, the queue, the ledger and the pass, all faked; every replaced name is put back."""
    keep = {n: getattr(AJ, n) for n in ("SCRATCH", "STATUS", "DRV", "sh", "in_queue", "commit", "file_item", "scan", "gate",
                                        "probe", "load_drv", "STATE", "run_records", "post_run", "def_exists", "kept_after")}
    keep_rs = AJ.RS.production_decisions
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        AJ.SCRATCH, AJ.STATUS, AJ.DRV = td / "s", td / "s/status.json", td / "drv.py"
        sf, log = td / "state.json", td / "log"
        calls, items, commits, opt = [], [], [], {"regen": True, "file": True, "note": 0}
        queue = set()

        def put(st):
            sf.write_text(json.dumps(st))

        def sh(cmd, cwd, lg, timeout=0, env=None):
            c = [str(x) for x in cmd[1:]]
            calls.append([Path(c[0]).name] + c[1:])
            st = json.loads(sf.read_text())
            if c[1] == "regen" and opt["regen"]:
                for k in c[3:]:
                    st[k]["round"] += 1
                    st[k]["row"]["id"] += "n"
                put(st)
            if c[1] == "file" and opt["file"]:
                queue.add(st[c[3]]["row"]["id"])
            if c[1] == "spec":
                (td / "x.spec.json").write_text("{}")
                st[c[3]]["spec"] = str(td / "x.spec.json")
                put(st)
            return opt["note"] if c[1] == "note" else 0

        AJ.sh, AJ.in_queue = sh, lambda r: r["id"] in queue
        AJ.commit = lambda paths, msg, lg: commits.append(paths) or "c"
        AJ.file_item = lambda iid, *a, **k: items.append(iid) or iid
        AJ.RS.production_decisions = lambda d=None: []
        AJ.def_exists, AJ.kept_after = lambda d: True, lambda r, at: False
        AJ.gate = lambda now=None: {"mode": "CRUISE", "n": 1, "held": None}
        AJ.STATUS.parent.mkdir(parents=True, exist_ok=True)
        AJ.STATUS.write_text(json.dumps({"follow_ups": []}))
        put({"RM_A_n": {"group": "g", "round": 2, "row": row("j2")}})
        try:
            yield types.SimpleNamespace(td=td, sf=sf, log=log, calls=calls, items=items, commits=commits, opt=opt, queue=queue, put=put)
        finally:
            for n, x in keep.items():
                setattr(AJ, n, x)
            AJ.RS.production_decisions = keep_rs


def t_newest_verdict_decides():
    """HOLD_ERROR is no verdict."""
    v = AJ.verdicts([("run_b", rec("j", "REGEN", A2)), ("run_a", rec("j", "ACCEPT", A1)), ("run_c", rec("j", "HOLD_ERROR", A3)),
                     ("run_d", rec("k", "HOLD_ERROR", A3))])
    check("verdicts: the newest by time, HOLD_ERROR is none", v["j"][0] == "run_b" and "k" not in v, v)


def t_no_fourth_round():
    """What each open row is owed: the cap, an ESCALATE, a newer keep and an unread keep are never a redraw."""
    state = {"two": {"group": "g", "round": 2, "row": row("j2")}, "one": {"group": "g", "round": 1, "row": row("j1")},
             "cap": {"group": "g", "round": 3, "row": row("j3")}, "esc": {"group": "g", "round": 2, "row": row("j4")},
             "acc": {"group": "g", "round": 2, "row": row("j5")}, "done": {"group": "g", "round": 2, "done": "ACCEPT", "row": row("j2")},
             "stop": {"group": "g", "round": 2, "row": row("j2")}, "gone": {"group": "g", "round": 2, "row": row("j2", "RM_Gone")},
             "kept": {"group": "g", "round": 2, "row": row("j6")}, "blind": {"group": "g", "round": 3, "row": row("j7")},
             "lost": {"group": "g", "round": 2, "row": row("j8")}, "wait": {"group": "g", "round": 2, "row": row("j9")},
             "fresh": {"group": "g", "round": 1, "row": row("j10")}, "stopdef": {"group": "g", "round": 2, "row": row("j2", "RM_S")}}
    jd = {f"j{n}": (f"run{n}", rec(f"j{n}", "REGEN", A1)) for n in (1, 2, 3, 6, 7)}
    jd["j4"] = ("run4", rec("j4", "ESCALATE", A1))
    jd["j5"] = ("run5", rec("j5", "ACCEPT", A1))
    got = AJ.facing_next(state, jd, lambda d: d in ("stop", "RM_S"), lambda d: {"RM_Gone": False}.get(d),
                         lambda r, at: {"j6": True, "j7": None}.get(r["id"], False), lambda r: r["id"] == "j9")
    check("facing_next: below the cap is a regen of the run that judged it; done, stopped, gone, kept and ACCEPT rows are not",
          got["regen"] == [("two", "g", "run2"), ("one", "g", "run1")], got)
    check("facing_next: the cap and an ESCALATE are capped, never a fourth round", got["capped"] == [("cap", "run3"), ("esc", "run4")], got)
    check("facing_next: a later round whose jobs are not in the queue is filed again; one in the queue is not",
          got["refile"] == [("lost", "g")], got)
    check("facing_next: keeps that could not be read hold the row and name it", got["unread"] == ["blind"], got)


def t_discharged_leaves_the_list():
    """Done, filed on, judged again or stopped."""
    fus = [{"at": A1, "subject": "d", "run": "r1", "owed": "o"}, {"at": A1, "subject": "again", "run": "r1", "owed": "o"},
           {"at": A1, "subject": "stop", "run": "r1", "owed": "o"}, {"at": A1, "subject": "live", "run": "r1", "owed": "old"},
           {"at": A2, "subject": "live", "run": "r2", "owed": "new"}, {"at": A1, "subject": "err", "run": "r1", "owed": "o"},
           {"at": A2, "subject": "before", "run": "r2", "owed": "o"}, {"at": A2, "subject": "moved", "run": "r1", "owed": "o"},
           {"at": A2, "subject": "same", "run": "r1", "owed": "o"}]
    left = AJ.open_follow_ups(fus, {"d": {"done": "ACCEPT"}, "live": {}, "moved": {"row": row("jm2")}, "same": {"row": row("js")}},
                              [("r9", rec("", "REGEN", A3, "again")), ("r9", rec("", "HOLD_ERROR", A3, "err")),
                               ("r1", rec("", "REGEN", A1, "before")), ("r1", rec("jm", "REGEN", A1, "moved")),
                               ("r1", rec("js", "REGEN", A1, "same"))], lambda k: k == "stop")
    check("a follow-up whose row is done, filed on, judged again or stopped leaves the list; the rest stay once",
          [(f["subject"], f["owed"]) for f in left] == [("live", "new"), ("err", "o"), ("before", "o"), ("same", "o")], left)


def t_regen_below_the_cap_is_filed():
    """drv.py regen, then drv.py file."""
    with rig() as R:
        log, calls, items, put = R.log, R.calls, R.items, R.put
        put({"RM_A_n": {"group": "g", "round": 2, "row": row("j2")}})
        st = {"follow_ups": []}
        wrote = AJ.follow({"regen": [("RM_A_n", "g", "run2")]}, st, log)
        check("a REGEN below the cap runs drv.py regen, then drv.py file for that row",
              calls == [["drv.py", "regen", "run2", "RM_A_n"], ["drv.py", "file", "g", "RM_A_n"]], calls)
        check("a filed regen is named by its new job, and owes nothing",
              st.get("regens_filed") == ["j2n"] and not st["follow_ups"] and not items and not wrote, st)


def t_unfiled_is_an_item():
    """Read back from the state and the queue, never from an exit code."""
    with rig() as R:
        log, calls, items, opt, queue = R.log, R.calls, R.items, R.opt, R.queue
        opt["regen"] = False
        st = {"follow_ups": []}
        AJ.follow({"regen": [("RM_A_n", "g", "run2")]}, st, log)
        check("a regen that moved nothing is never filed, and becomes an item and a follow-up",
              [c[1] for c in calls] == ["regen"] and items == [AJ.unfiled_item_id({"def": "RM_A"})]
              and [f["subject"] for f in st["follow_ups"]] == ["RM_A_n"] and not st.get("regens_filed"), (calls, items, st))

        calls.clear(); items.clear(); queue.clear()
        opt.update(regen=True, file=False)
        st = {"follow_ups": []}
        wrote = AJ.follow({"refile": [("RM_A_n", "g")]}, st, log)
        check("a filing whose jobs are not in the queue is an item, whatever the exit code",
              wrote and len(items) == 1 and len(st["follow_ups"]) == 1 and not st.get("regens_filed"), (items, st))


def t_capped_is_noted_once():
    """One item; a note that did not land leaves the row open."""
    with rig() as R:
        sf, log, calls, opt, put = R.sf, R.log, R.calls, R.opt, R.put
        put({"RM_C_n": {"group": "g", "round": 3, "row": row("j3")}, "RM_D_n": {"group": "g", "round": 1, "row": row("j4")}})
        opt["note"] = 4
        st = {"follow_ups": []}
        AJ.follow({"capped": [("RM_C_n", "run3")]}, st, log)
        check("a capped row whose note did not land stays open and is listed",
              not json.loads(sf.read_text())["RM_C_n"].get("done") and len(st["follow_ups"]) == 1, st)
        opt["note"] = 0
        st = {"follow_ups": []}
        wrote = AJ.follow({"capped": [("RM_C_n", "run3")]}, st, log)
        got = json.loads(sf.read_text())
        check("a capped row is noted on the one capped item and closed, with no other row touched",
              wrote and got["RM_C_n"]["done"] == "ESCALATE" and got["RM_C_n"]["escalated_to"] == AJ.CAPPED_ITEM
              and "done" not in got["RM_D_n"] and calls[-1][1:3] == ["note", AJ.CAPPED_ITEM] and "RM_C_n (run run3)" in calls[-1][4]
              and not any(c[1] == "regen" for c in calls), (got, calls))


def t_vetoed_escalation_is_noted():
    """A compare veto at the cap."""
    with rig() as R:
        log, calls, opt = R.log, R.calls, R.opt
        other = {"at": A1, "subject": "RM_W", "run": "fw", "owed": "install of ACCEPT r2: rc 1"}
        opt["note"] = 4
        st = {"follow_ups": [VETO, other]}
        AJ.follow({}, st, log)
        check("a compare veto at the cap stays listed while its note does not land", st["follow_ups"] == [VETO, other], st)
        opt["note"] = 0
        AJ.follow({}, st, log)
        check("a compare veto at the cap is noted on the capped item and leaves the list",
              st["follow_ups"] == [other] and "RM_V (run fv)" in calls[-1][4], (st, calls[-1]))

        AJ.scan = lambda: {"fauna_defs": [], "facing": []}
        AJ.STATUS.write_text(json.dumps({"follow_ups": [VETO]}))
        calls.clear()
        AJ.cmd_run(A)
        check("a pass with only a vetoed escalation to do does it", any(c[1:2] == ["note"] for c in calls), calls)


def t_same_pass_files_the_next_round():
    """The row this pass judged; a pass with only a redraw owed; held and dry passes file nothing."""
    with rig() as R:
        td, calls, commits, opt, put = R.td, R.calls, R.commits, R.opt, R.put
        # ---- a whole pass: the row that this pass judges REGEN is regenerated in this pass, after its gate
        AJ.STATE = td / "st"
        put({"RM_B_n": {"group": "g", "round": 1, "row": row("jb", "RM_B")}})
        opt.update(regen=True, file=True)
        judged = []
        AJ.scan = lambda: {"fauna_defs": [], "facing": [("RM_B_n", "g")],
                           "next": {"regen": [], "refile": [], "capped": [], "unread": []}}
        AJ.gate = lambda now=None: {"mode": "CRUISE", "n": 1, "held": None}
        AJ.probe, AJ.load_drv = (lambda: (True, "ok")), (lambda: object())
        AJ.run_records = lambda rid: judged.append(dict(rec("jb", "REGEN", A1, "RM_B_n"), candidate="r1")) or judged[-1:]
        AJ.RS.production_decisions = lambda d=None: [("audit_x", rec("jb", "REGEN", A1, "RM_B_n"))]
        AJ.post_run = lambda *a, **k: ([], [])
        calls.clear(); commits.clear()
        AJ.STATUS.parent.mkdir(parents=True, exist_ok=True)
        AJ.STATUS.write_text(json.dumps({"follow_ups": [{"at": A1, "subject": "RM_B_n", "run": "old", "owed": "drv.py regen old RM_B_n"}]}))
        AJ.cmd_run(A)
        got = json.loads(AJ.STATUS.read_text())
        check("a pass that judges a row REGEN files its next round in the same pass",
              [c[:2] for c in calls if c[0] == "drv.py"] == [["drv.py", "spec"], ["drv.py", "regen"], ["drv.py", "file"]]
              and got.get("regens_filed") == ["jbn"], (calls, got))

        # ---- an owed regen alone makes the pass work, behind the same gate
        AJ.scan = lambda: {"fauna_defs": [], "facing": [], "next": {"regen": [("RM_B_n", "g", "r")], "refile": [], "capped": [], "unread": []}}
        calls.clear()
        AJ.gate = lambda now=None: {"mode": "CRUISE", "n": 1, "held": "the pipeline is paused"}
        AJ.cmd_run(A)
        check("a held pass files no redraw", calls == [], calls)
        AJ.gate = lambda now=None: {"mode": "CRUISE", "n": 1, "held": None}
        A.dry_run = True
        AJ.cmd_run(A)
        check("a dry run files no redraw", not any(c[0] == "drv.py" for c in calls), calls)
        A.dry_run = False
        AJ.cmd_run(A)
        check("an owed regen with nothing to judge is still filed",
              [c[1] for c in calls if c[0] == "drv.py"] == ["regen", "file"], calls)


def t_due_tells_four_answers():
    """0 clear, 1 owed or stale, 2 could not look."""
    with rig() as R:
        put = R.put
        # ---- due: 0 nothing owed, 1 owed or a discharged entry listed, 2 could not look
        empty = {"regen": [], "refile": [], "capped": [], "unread": []}
        AJ.RS.production_decisions = lambda d=None: []
        res = {}
        for name, nxt, fu in (("clear", empty, []), ("regen", dict(empty, regen=[("k", "g", "r")]), []),
                              ("capped", dict(empty, capped=[("k", "r")]), []), ("refile", dict(empty, refile=[("k", "g")]), []),
                              ("stale", empty, [{"at": A1, "subject": "Z", "run": "r", "owed": "o"}]),
                              ("held", empty, [{"at": A1, "subject": "Y", "run": "r", "owed": "o"}]),
                              ("veto", empty, [VETO]), ("blind", dict(empty, unread=["k"]), []), ("nodrv", None, [])):
            put({"Z": {"done": "ACCEPT"}})
            AJ.scan = lambda nxt=nxt: {} if nxt is None else {"next": nxt}
            AJ.STATUS.write_text(json.dumps({"follow_ups": fu}))
            res[name] = AJ.cmd_due(A)
        check("due: owed, discharged, clear and could-not-look are different exits",
              res == {"clear": 0, "regen": 1, "capped": 1, "refile": 1, "stale": 1, "held": 0, "veto": 1, "blind": 2, "nodrv": 2}, res)


def t_files_from_the_judging_clone():
    check("the driver files from the clone that judged", AJ.driver_env()["FAB_REPO"] == str(AJ.ROOT))


if __name__ == "__main__":
    sys.exit(main())
