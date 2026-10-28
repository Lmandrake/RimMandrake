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
    installs_and_unfiled()
    print("FAILED: " + ", ".join(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


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
        (cmp_root / "RM_FurnaceBeast_r2/compare.json").write_text("{}")
        check("an existing compare is not paid for twice",
              len(AJ.install_cmds(acc, "fauna", spec="/s/x.json", cmp_root=cmp_root)) == 1)
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

        def fake_sh(cmd, cwd, log, timeout=0):
            calls.append([str(c) for c in cmd])
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
        check("post_run: ACCEPT compares (spec found in the cands dir) then installs; REGEN installs nothing",
              any(c[1].endswith("fauna_compare.py") and c[4].endswith("auto_1/RM_FurnaceBeast_r2.spec.json") for c in calls)
              and sum(c[1].endswith("fauna_drive.py") for c in calls) == 1, names)
        check("post_run: installed files come back for commit and deploy",
              every == ["src/RimMandrake/Pyrelands/Textures/Things/F/F_south.png"] and changed == every and not stt["follow_ups"], (every, stt))
        AJ.sh, AJ.STATE, AJ.FAUNA_INSTALLS, AJ.git_dirty, AJ.DATA = saved
        ok, why, _ = AJ.deploy_verdict("", rs, lambda ps: [])
        check("an empty plan (the tool died) is not 'in sync'", not ok and "in sync" not in why, why)


if __name__ == "__main__":
    sys.exit(main())
