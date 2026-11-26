#!/usr/bin/env python3
"""Offline kill-and-resume test for the holder session (item RIMMANDRAKE_RESUME_HOLDER_SESSIONS_TO_400K_KILL_AND_RESUME;
spec design/specs/2026-11-15-holder-pipeline-fusion.md §3.4, Option B). Temp root, faked claude (a fake runner and a
fake transcript): no unit starts, nothing in the repo is written.

    python3 src/RimMandrake/rimflow/selftest_holder_resume.py      # "ALL PASS"

The run: a holder's run records its session; the next launch resumes it with `--resume` and the transcript carried
into the new clone; the holder is killed mid-stage; the next launch reconciles first, resumes the same session, and its
brief points at a packet that still lists the refuted cause and his answer; past the ceiling the holder rotates (no
`--resume`); the holder's cap is what is left of the stage ceiling, not the per-run cap.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as ML              # noqa: E402
import detached_helper as DH        # noqa: E402
import maturation as M              # noqa: E402
import maturation_dispatch as MD    # noqa: E402

res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))


tmp = tempfile.mkdtemp(prefix="holder_resume_")
root = os.path.join(tmp, "repo")
projects = os.path.join(tmp, "projects")
MOD = ML.config()["pilot_mods"][0]
# hermetic: the temp ledger stands for a backfilled one. Unstubbed, ledger_ready ran the backfill acceptance on the REAL
# pilot ledger, so this test went red whenever that drifted (2026-11-16: ExplosiveKnockback's ledger stage offline_build
# vs its stage record in_game), whatever the code under test did (RIMMANDRAKE_STUB_HOLDER_RESUME_READINESS_REAL_LEDGER_LEAKED).
MD.ledger_ready = lambda r, m: (True, "PASS 7/7 (stubbed)")
os.makedirs(os.path.join(root, "design", "concepts", MOD, "ledger"))
SID = "0a1b2c3d-1111-2222-3333-444455556666"
clone1, clone2 = os.path.join(tmp, "clones", "A.det"), os.path.join(tmp, "clones", "B.det")


def transcript(clone, ctx):
    d = DH.project_dir(clone, projects)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, SID + ".jsonl"), "w", encoding="utf-8") as fh:
        u = {"input_tokens": 2, "cache_creation_input_tokens": 1000, "cache_read_input_tokens": ctx - 1102,
             "output_tokens": 100}
        fh.write(json.dumps({"type": "assistant", "message": {"usage": u}}) + "\n")
        side = dict(u, cache_read_input_tokens=5)
        fh.write(json.dumps({"type": "assistant", "isSidechain": True, "message": {"usage": side}}) + "\n")


try:
    ML.append(root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
    tok = ML.grant(root, MOD, lease="H1")
    F = "finding:RIMMANDRAKE_TRACE_TICK_FIXTURE_FOR_KILL_RESUME"
    ML.append(root, MOD, "JUDGE.J1", "finding.open", F, run="J1", evidence=["run:J1"],
              body={"class": "problem", "bars": [], "tags": ["code"], "text": "the comp does not tick",
                    "proposed_fix": "tick the comp from CompTickLong", "accept": "none, fixture"})
    ML.append(root, MOD, "HOLDER.H1", "cause.refuted", "cause:c-tick", token=tok, code_sha="abc123",
              body={"text": "not the tick (C_TICK)", "finding": F, "depends_on": ["Source/Comp.cs"]})
    ML.append(root, MOD, "OWNER", "question.answer", "q:r", body={"said": "radius 4"},
              authority={"owner_said": "radius 4"})

    # the first run ran in clone1; its transcript says 150k of context
    transcript(clone1, 150000)
    t = DH.find_transcript(SID, projects)
    check("the transcript is found by session id", t and t.startswith(DH.project_dir(clone1, projects)), t)
    check("context is the last main-thread turn, not a subagent's", DH.context_tokens(t) == 150000, DH.context_tokens(t))

    cfg = {"stage_ceiling_usd": 100}
    landed = []
    ended = {}
    fx = {"session_of": lambda unit: (SID, DH.context_tokens(DH.find_transcript(SID, projects))),
          "record": lambda unit: ended.get(unit) or {"status": "running"},
          "land_ledger": lambda paths: landed.append(paths) or "landed"}
    st = {"mods": {MOD: {}}}

    def run(lease, unit, result):      # a pilot stage run: started from the packet, then ended with this result
        ML.launch(root, MOD, lease, "holder", stage="offline_build")
        st["mods"][MOD].setdefault("ledger_runs", []).append({"run": lease, "unit": unit, "item": "X", "at": 1})
        ended[unit] = {"status": "finished", "result": result}
        return MD.end_ledger_runs(root, st, {}, 2, fx)

    out = run("run-1", "rm-detached-bench-run1", "success")
    S = ML.reduce(ML.read(root, MOD))["session"] or {}
    check("the ended run's session is recorded with its context", S.get("session_id") == SID and
          S.get("context_tokens") == 150000, (S, out))
    check("the session is in the DISPATCH shard, which is landed", any(p.endswith("DISPATCH.jsonl") for p in landed[-1])
          and not os.path.exists(os.path.join(ML.ledger_dir(root, MOD), "HOLDER.run-1.jsonl")), landed)
    row = {"mod": MOD, "stage_usd": 22.5}
    s = {}
    cap, kw = MD.holder_launch(root, cfg, s, row, 15, fx)
    check("under the ceiling the launch resumes that session", kw.get("session") == SID and "reconcile" not in kw, kw)
    check("the holder's cap is what is left of the stage ceiling", cap == 77.5 and row["cap"] == 77.5, cap)

    # the resumed launch: DH carries the transcript into the new clone and passes --resume
    rec = {"clone": clone2, "unit": "u2", "seat": "BENCH", "model": "opus", "item": "X", "budget_usd": cap,
           "out": "/dev/null", "err": "/dev/null", "state": tmp, "resume_session": SID}
    dst = DH.carry_session(SID, clone2, projects)
    check("the transcript is carried into the new clone's project folder", dst and os.path.exists(dst) and
          dst.startswith(DH.project_dir(clone2, projects)), dst)
    argv = DH.launch_argv(rec, "brief", "/usr/bin/claude")
    i = argv.index("--resume") if "--resume" in argv else -1
    check("claude is started with --resume <session>", i > 0 and argv[i + 1] == SID, argv[-6:])
    check("an unknown session is refused, not resumed blind", DH.carry_session("ffffffff-0000", clone2, projects) is None)

    # killed mid-stage: the second run's unit was SIGTERMed (its result is finish's "killed: ...")
    transcript(clone2, 190000)
    run("run-2", "rm-detached-bench-run2", "killed: signal TERM")
    cap2, kw2 = MD.holder_launch(root, cfg, s, dict(row), 15, fx)
    check("after the kill the next launch reconciles first", "killed" in (kw2.get("reconcile") or ""), kw2)
    check("and resumes the same session", kw2.get("session") == SID, kw2)

    # the brief the resumed, reconciling holder gets (maturation.launch_mod with a fake runner)
    seen = {}

    def fake_runner(argv, **k):
        seen["argv"] = argv
        seen["brief"] = open(argv[argv.index("--brief-file") + 1], encoding="utf-8").read()

        class R:
            returncode, stdout, stderr = 0, "DETACHED rm-detached-bench-run3\n", ""
        return R()
    old_bt, old_bd = M.brief_text, M.brief_dir
    M.brief_text = lambda root_, mod, budget, bars=None: ("# stage brief\n\nbuild it", {"stage": "offline_build",
                                                                                         "owed": "build"})
    M.brief_dir = lambda: tmp
    try:
        rc, out, unit = M.launch_mod(root, MOD, cap2, "SOME_ITEM", runner=fake_runner, **kw2)
    finally:
        M.brief_text, M.brief_dir = old_bt, old_bd
    b = seen.get("brief", "")
    check("the holder's resume is marked --planned-resume (resume_plan decided it; the 150k rule does not apply)",
          "--planned-resume" in seen.get("argv", []), seen.get("argv"))
    check("the launch passes --resume to the detached launcher", rc == 0 and "--resume" in seen.get("argv", []) and
          seen["argv"][seen["argv"].index("--resume") + 1] == SID, seen.get("argv"))
    check("the brief opens with the resume and the reconcile step", b.index("resumed (session") < b.index(
        "Reconcile first") < b.index("# stage brief"), b[:300])
    # the run.start of that launch names the session it resumes and the reconcile: the live outcome is read from the ledger
    led3 = MD.ledger_open(root, MOD, "fixer", "", now=1795000000, fx=fx, session=kw2.get("session"),
                          reconcile=kw2.get("reconcile"))
    st3 = [e for e in ML.read(root, MOD) if e.get("kind") == "run.start" and e.get("run") == led3["run"]]
    check("the run.start names the resumed session and the reconcile", st3 and (st3[-1].get("body") or {}).get(
        "resume_session") == SID and (st3[-1].get("body") or {}).get("reconcile") is True, st3[-1:] or None)
    import holder_kill_check as HK

    def ev(kind, run, **body):
        return {"writer": "DISPATCH", "kind": kind, "body": dict({"run": run}, **body)}
    s1 = ev("run.start", "r1", lease="r1", resume_session=SID)
    k1 = ev("run.end", "r1", lease="r1", status="killed: signal (TERM)")
    check("the live check fails before a resumed run is killed", not HK.seen([s1])[0], HK.seen([s1]))
    check("the live check fails on a relaunch that did not resume and reconcile",
          not HK.seen([s1, k1, ev("run.start", "r2", lease="r2")])[0])
    check("the live check holds on a killed resumed run relaunched in the same session, reconciling",
          HK.seen([s1, k1, ev("run.start", "r2", lease="r2", resume_session=SID, reconcile=True)])[0])
    txt, _ = ML.packet(root, MOD)
    check("the packet it is told to re-read lists the refuted cause and his answer",
          "modledger.py packet --mod %s" % MOD in b and "C_TICK" in txt and "radius 4" in txt)

    # a clean end clears the reconcile; past the ceiling the holder rotates
    transcript(clone2, ML.config()["holder_context_ceiling_tokens"] + 5000)
    run("run-3", "rm-detached-bench-run3", "success")
    cap3, kw3 = MD.holder_launch(root, cfg, s, dict(row), 15, fx)
    _, kw3b = MD.holder_launch(root, cfg, s, dict(row, retry_of={"unit": "rm-x"}), 15, fx)
    check("a launch retrying a killed unit reconciles too", "rm-x" in (kw3b.get("reconcile") or ""), kw3b)
    check("past the ceiling: no --resume, a fresh holder from the packet", "session" not in kw3 and "reconcile" not in
          kw3 and ML.resume_plan(root, MOD)["action"] == "rotate", kw3)

    # the landing carries every view, closed_<version>.md included (RIMMANDRAKE_LAND_EVERY_LEDGER_VIEW_CLOSED_WENT_STALE)
    vd = os.path.join(ML.ledger_dir(root, MOD), "views")
    open(os.path.join(vd, "closed_0.1.0.md"), "w").close()
    got = MD.ledger_paths(root, [MOD])
    check("ledger_paths lands every view, closed ones too", any(p.endswith("closed_0.1.0.md") for p in got) and
          all(any(p.endswith("views/" + v) for p in got) for v in ML.VIEWS), got)

    # outside the pilot list nothing changes
    cap4, kw4 = MD.holder_launch(root, cfg, s, {"mod": "NotAPilotMod", "stage_usd": 0}, 15, fx)
    check("a mod outside pilot_mods keeps the per-run cap and no resume", cap4 == 15 and kw4 == {}, (cap4, kw4))
    check("the ledger lints clean of fenced or malformed lines",
          not [f for f in ML.lint(root, MOD, base=None)[0] if f[0] in ("MALFORMED", "FENCED", "NO_NEWLINE")])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("ALL PASS" if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
