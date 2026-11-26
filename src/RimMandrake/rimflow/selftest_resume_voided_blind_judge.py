#!/usr/bin/env python3
"""Offline test: a voided blind judge run is resumed, never read as a verdict (item
RIMMANDRAKE_RESUME_VOIDED_BLIND_JUDGE_NOT_READ_AS_VERDICT; page design/specs/2026-11-23-resume-voided-blind-judge/
boundary.md). Each test is named for its promise. Temp roots and a temp Dispatch state: nothing launches, nothing in
the repo is written. Written before the fix and watched failing on the parent.

    python3 src/RimMandrake/rimflow/selftest_resume_voided_blind_judge.py      # "ALL PASS"

The fixture is ExplosiveKnockback's concept folder at FIXTURE_SHA (2026-11-23, blind cycle 6 holding the voided
judge's interim block "exit_met false") and the Dispatch state's books as the void left them.
"""
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="resume_void_judge_")
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "dispatch")
os.environ["RM_RUN_VOIDS_FILE"] = os.path.join(TMP, "dispatch", "voids.jsonl")
os.environ["MATURATION_BRIEF_DIR"] = os.path.join(TMP, "briefs")
os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
os.makedirs(os.environ["MATURATION_BRIEF_DIR"])
import maturation as M              # noqa: E402
import maturation_dispatch as MD    # noqa: E402
import modledger as ML              # noqa: E402
import run_void as RV               # noqa: E402

FIXTURE_SHA = "bc42c3698905cd2c2db60e0e592feedc490908ed"
MOD = "ExplosiveKnockback"
VID = "0.1.0#5"
UNIT = "rm-detached-bench-rimmandrake-judge-explosiveknockback-bli-1795437194"
RUN = "judge-1795437145"
AT = 1795437145.3956928
SID = "d5d2bcfd-fcd8-45f5-bcbe-52b6319c201e"
NOW = 1795442400.0
CFG = {"advancing": [MOD], "cap_tokens": 3_750_000, "blind_cap_tokens": 5_000_000, "blind_enabled": True, "max_live": 4,
       "blind_auto_cycles_per_visit": 1, "settle_s": 180, "launch_tries": 3, "stage_ceiling_tokens": 250_000_000, "seat": "BENCH",
       "model": "opus"}
res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:700]))


def section(fn):
    try:
        fn()
    except Exception as e:      # noqa: BLE001  a missing function on the parent is a FAIL, not a crash
        check("%s ran" % fn.__name__, False, "%s: %s\n%s" % (type(e).__name__, e, traceback.format_exc()[-900:]))


def fixture_root():
    root = os.path.join(TMP, "repo")
    if os.path.isdir(root):
        return root
    os.makedirs(root)
    r = subprocess.run(["git", "-C", REPO, "archive", FIXTURE_SHA, "design/concepts/%s" % MOD], capture_output=True,
                       timeout=300)
    assert r.returncode == 0, r.stderr[-300:]
    tarfile.open(fileobj=io.BytesIO(r.stdout)).extractall(root)
    return root


CYCLE5 = {"visit_id": VID, "cycle": 5, "unit": "rm-detached-bench-rimmandrake-judge-explosiveknockback-bli-1794890452",
          "item": "RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_FIVE", "at": 1794890427.0, "cap": 20, "failed": None,
          "tries": 1, "filed": True, "never_started": False}
VOID_ENTRY = {"visit_id": VID, "cycle": 6, "unit": UNIT, "item": "RIMMANDRAKE_JUDGE_EXPLOSIVEKNOCKBACK_BLIND_CYCLE_SIX_TESTS_FIRST",
              "at": AT, "cap": 87.41, "failed": None, "tries": 1, "filed": True, "never_started": False, "tried": None}
VOIDED = [{"book": "blind_auto", "key": None, "entry": VOID_ENTRY, "class": "void_hand", "void": "void-5ae28fe22cb2",
           "why": "killed from outside while working", "unit": UNIT, "faults": 1, "was": "void_system"},
          {"book": "ledger_runs", "key": None, "entry": {"run": RUN, "unit": UNIT, "item": VOID_ENTRY["item"], "at": AT,
                                                         "stage": "blind_challenge", "writer": "JUDGE.%s" % RUN,
                                                         "ended": AT + 2884, "status": "timeout (killed TERM)",
                                                         "flags": ["NO_VERDICTS"]},
           "class": "void_hand", "void": "void-5ae28fe22cb2", "why": "killed from outside while working", "unit": UNIT}]


def write_state(blind_auto=None, voided=None):
    s = {"blind_auto": copy.deepcopy([CYCLE5] if blind_auto is None else blind_auto),
         "voided": copy.deepcopy(VOIDED if voided is None else voided)}
    with open(os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "state.json"), "w") as f:
        json.dump({"mods": {MOD: s}}, f)
    with open(os.environ["RM_RUN_VOIDS_FILE"], "w") as f:     # the hand void stands (its line in voids.jsonl)
        f.write(json.dumps({"act": "void", "id": "void-5ae28fe22cb2", "unit": UNIT, "mod": MOD, "kind": "hand",
                            "item": VOID_ENTRY["item"], "why": "killed from outside while working"}) + "\n"
                if any(m.get("unit") == UNIT for m in s["voided"]) else "")
    return s


def put_for(row):
    def put(decision, why, need=None):
        row["decision"], row["why"] = decision, why
        if need:
            row["need"] = need
    put.row = row
    return put


def tick_facts(session=(SID, 378832, "its clone's transcript"), blind_runs=(), run_at=None):
    f = M.blind_facts(fixture_root(), MOD)
    f.update(live_units=[], last_end=NOW - 3000, blind_runs=list(blind_runs), blind_run_at=dict(run_at or {}),
             killed={}, certificate={"ok": False, "rows": [{"bar": "x", "ok": False}]}, box_runs={}, run_tokens={},
             cycle_decision=None, void_session=session)
    return f


def decide(f, s):
    row = {"mod": MOD, "stage": "blind_challenge"}
    go = MD.decide_blind(CFG, s, f, row, put_for(row), NOW, (True, "acct ok"), 0, releases=[])
    return go, row


# ---- promises ---------------------------------------------------------------------------------------------------

def t_a_voided_judges_block_is_no_verdict():
    root = fixture_root()
    write_state(voided=[])
    base = M.blind_facts(root, MOD)
    check("a-voided-judges-block-is-no-verdict: control, no void: the fixture's cycle 6 reads exit not met",
          base.get("owed") == "exit not met" and base.get("cycle") == 6, {k: base.get(k) for k in ("owed", "cycle")})
    write_state()
    bf = M.blind_facts(root, MOD)
    check("a-voided-judges-block-is-no-verdict: the voided judge's block reads owed resume",
          bf.get("owed") == "resume" and (bf.get("void_run") or {}).get("unit") == UNIT
          and (bf.get("void_run") or {}).get("run") == RUN, {k: bf.get(k) for k in ("owed", "void_run")})
    nx = M.gate_step(root, MOD)
    check("a-voided-judges-block-is-no-verdict: next never reads launch: none",
          not str(nx.get("launch")).startswith("none") and "resumes blind cycle 6" in str(nx.get("launch"))
          and "resumes" in nx.get("next", ""), (nx.get("launch"), nx.get("next")))
    ex = [r for r in nx.get("refusals") or [] if r["clause"] == "exit_met"]
    check("a-voided-judges-block-is-no-verdict: the exit_met clause names the void", ex and "voided" in ex[0][
        "observed"], ex)
    with open(os.path.join(os.environ["RM_MATURATION_DISPATCH_DIR"], "state.json"), "w") as f:
        f.write("{not json")
    bf = M.blind_facts(root, MOD)
    check("a-voided-judges-block-is-no-verdict: an unreadable Dispatch state is blocked (UNMEASURED), never a "
          "verdict", bf.get("owed") == "blocked" and any("UNMEASURED" in b for b in bf.get("blocked") or []),
          {k: bf.get(k) for k in ("owed", "blocked")})


def t_the_tick_resumes_the_voided_judges_own_session():
    s = write_state()
    go, row = decide(tick_facts(), s)
    jr = row.get("judge_resume") or {}
    check("the-tick-resumes-the-voided-judges-own-session: launch, not exit_not_met",
          go and row.get("decision") == "launch", row)
    check("the-tick-resumes-the-voided-judges-own-session: its own session, ledger run and unit",
          jr.get("session") == SID and jr.get("run") == RUN and jr.get("unit") == UNIT
          and (row.get("retry_of") or {}).get("unit") == UNIT, row)
    kw = MD.resume_kw(row)
    check("the-tick-resumes-the-voided-judges-own-session: the launch resumes the unit with its session",
          kw.get("resume") == UNIT and (kw.get("judge_resume") or {}).get("session") == SID, kw)
    go, row = decide(tick_facts(blind_runs=["rm-before"], run_at={"rm-before": AT - 500}), write_state())
    check("the-tick-resumes-the-voided-judges-own-session: a blind run from before the void does not stop it",
          go and row.get("decision") == "launch", row)
    go, row = decide(tick_facts(blind_runs=["rm-after"], run_at={"rm-after": AT + 500}), write_state())
    check("the-tick-resumes-the-voided-judges-own-session: a blind run after the void stops it",
          not go and row.get("decision") == "hand_run_seen", row)


def t_a_fresh_judge_when_the_session_cannot_resume():
    for label, sess in (("no session", (None, None, "no transcript written during the run")),
                        ("at the ceiling", (SID, ML.config()["holder_context_ceiling_tokens"], "x"))):
        go, row = decide(tick_facts(session=sess), write_state())
        check("a-fresh-judge-when-the-session-cannot-resume: %s opens fresh" % label,
              go and row.get("judge_fresh", {}).get("unit") == UNIT and not row.get("judge_resume"), row)
        kw = MD.resume_kw(row)
        check("a-fresh-judge-when-the-session-cannot-resume: %s: fresh_of only, no resume" % label,
              set(kw) == {"fresh_of"}, kw)
    seen = {}

    def runner(argv, **kw):
        seen["brief"] = open(argv[argv.index("--brief-file") + 1]).read()
        seen["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, "DETACHED rm-fake-unit\n", "")
    write_state()
    rc, text, unit = M.launch_mod(fixture_root(), MOD, 20, "RIMMANDRAKE_X_Y_Z_Q", runner=runner,
                                  twins=lambda *a: ([], "none"), fresh_of={"unit": UNIT, "why": "no transcript"})
    b = seen.get("brief", "")
    check("a-fresh-judge-when-the-session-cannot-resume: launch_mod launches on owed resume", rc == 0, text)
    check("a-fresh-judge-when-the-session-cannot-resume: the brief moves the folder aside unread, no resume section",
          "open cycle 6 fresh" in b and "Do NOT open or read it" in b and "## Resume" not in b
          and "--resume" not in seen.get("argv", []), b[:600])


def t_a_counted_run_after_the_void_reads_normally():
    later = dict(VOID_ENTRY, unit="rm-resumed", at=AT + 900)
    write_state(blind_auto=[CYCLE5, later])
    bf = M.blind_facts(fixture_root(), MOD)
    check("a-counted-run-after-the-void-reads-normally: the block reads as before", bf.get("owed") == "exit not met"
          and not bf.get("void_run"), {k: bf.get(k) for k in ("owed", "void_run")})
    check("a-counted-run-after-the-void-reads-normally: another visit's void is not this cycle's",
          RV.voided_cycle_run({"voided": VOIDED, "blind_auto": []}, "0.1.0#9", 6) is None
          and RV.voided_cycle_run({"voided": VOIDED, "blind_auto": []}, VID, 6)["unit"] == UNIT)


def ledger_root():
    root = os.path.join(TMP, "ledger_repo_%d" % len(os.listdir(TMP)))
    os.makedirs(ML.ledger_dir(root, MOD))
    ML.append(root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0",
              views=False)
    return root


def judge_line(root, run, tag):
    w = "JUDGE.%s" % run
    ML.append(root, MOD, w, "test.run", "run", run=run, views=False,
              body={"result": "UNRUN", "command": "python3 selftest_%s.py" % tag})


def t_the_voided_runs_shard_seal_reopens_for_its_own_lines():
    root = ledger_root()
    judge_line(root, RUN, "one")
    ML.seal(root, MOD, RUN, views=False)
    try:
        judge_line(root, RUN, "two")
        refused = ""
    except ML.ModLedgerError as e:
        refused = str(e)
    check("the-voided-runs-shard-seal-reopens-for-its-own-lines: control: a sealed shard refuses a line",
          "is sealed" in refused, refused)
    eid = ML.unseal(root, MOD, RUN, "voided: test", views=False)
    judge_line(root, RUN, "two")
    codes = [x[0] for x in ML.lint(root, MOD, base=None)[0]]
    check("the-voided-runs-shard-seal-reopens-for-its-own-lines: unsealed, its line appends and lints clean",
          eid and "SEALED_CHANGED" not in codes, (eid, codes))
    ML.seal(root, MOD, RUN, views=False)
    check("the-voided-runs-shard-seal-reopens-for-its-own-lines: sealed again it refuses", "JUDGE.%s" % RUN in
          ML.seals(ML.read(root, MOD)))
    # judge-reopen: the bundle's lines land on the sealed-empty shard of a void run only
    root = ledger_root()
    ML.seal(root, MOD, RUN, views=False)
    src = ledger_root()
    judge_line(src, RUN, "a")
    judge_line(src, RUN, "b")
    judge_line(src, "judge-999", "foreign")
    lines = os.path.join(TMP, "bundle_lines.jsonl")
    with open(lines, "w") as f:
        for sh in ("JUDGE.%s" % RUN, "JUDGE.judge-999"):
            f.write(open(os.path.join(ML.ledger_dir(src, MOD), sh + ".jsonl")).read())
    st = {"mods": {MOD: {"voided": VOIDED}}}
    rc, text, _ = MD.reopen_void_judge(root, {"mods": {MOD: {}}}, MOD, RUN, lines, "t")
    check("the-voided-runs-shard-seal-reopens-for-its-own-lines: judge-reopen refuses a run that is not void",
          rc == 2 and "not void" in text, text)
    rc, text, paths = MD.reopen_void_judge(root, st, MOD, RUN, lines, "t")
    mine = [e for e in ML.read(root, MOD) if e.get("_shard") == "JUDGE.%s" % RUN]
    codes = [x[0] for x in ML.lint(root, MOD, base=None)[0]]
    check("the-voided-runs-shard-seal-reopens-for-its-own-lines: judge-reopen lands only its own lines, sealed, "
          "lint clean", rc == 0 and len(mine) == 2 and "1 other line(s) refused" in text and "SEALED_CHANGED" not in
          codes and "JUDGE.%s" % RUN in ML.seals(ML.read(root, MOD)), (rc, text, len(mine), codes))


def t_the_resumed_judge_writes_its_old_shard():
    root = ledger_root()
    ML.seal(root, MOD, RUN, views=False)
    seen = {}

    def launch(root_, mod, cap, item, **kw):
        seen.update(kw)
        return 0, "DETACHED rm-new", "rm-new"
    real, real_load = MD.pilot_ledger, M.load
    MD.pilot_ledger = lambda r, m: True
    M.load = lambda r, m: {"stage": "blind_challenge", "version": "0.1.0"} if r == root else real_load(r, m)
    try:
        st = {"mods": {MOD: {}}}
        rc, text, unit = MD.launch_stage(root, CFG, st, MOD, 20, "RIMMANDRAKE_X_Y_Z_Q", now=NOW,
                                         fx={"land_ledger": lambda paths: "landed"}, launch=launch, resume=UNIT,
                                         judge_resume={"run": RUN, "session": SID, "unit": UNIT})
    finally:
        MD.pilot_ledger, M.load = real, real_load
    starts = [e for e in ML.read(root, MOD) if e.get("kind") == "run.start"]
    check("the-resumed-judge-writes-its-old-shard: no new judge run, its shard reopened",
          rc == 0 and not starts and "JUDGE.%s" % RUN not in ML.seals(ML.read(root, MOD)), (rc, text, starts))
    check("the-resumed-judge-writes-its-old-shard: the unit writes its old shard and resumes its session",
          (seen.get("env") or {}).get("RM_MODLEDGER_WRITER") == "JUDGE.%s" % RUN and seen.get("session") == SID
          and seen.get("resume") == UNIT and "judge_resume" not in seen, seen)
    check("the-resumed-judge-writes-its-old-shard: its run end seals it again",
          [x.get("run") for x in st["mods"][MOD].get("ledger_runs") or []] == [RUN], st)
    seen.clear()

    def runner(argv, **kw):
        seen["brief"] = open(argv[argv.index("--brief-file") + 1]).read()
        seen["argv"] = argv
        return subprocess.CompletedProcess(argv, 0, "DETACHED rm-fake-unit\n", "")
    write_state()
    rc, text, unit = M.launch_mod(fixture_root(), MOD, 20, "RIMMANDRAKE_X_Y_Z_Q", runner=runner,
                                  twins=lambda *a: ([], "none"), resume=UNIT, session=SID)
    b = seen.get("brief", "")
    check("the-resumed-judge-writes-its-old-shard: the brief opens with the judge's resume text, not the holder's",
          rc == 0 and b.startswith("**You are the same blind judge, resumed") and "holder, resumed" not in b
          and SID in seen.get("argv", []), (rc, text, b[:300]))


def main():
    for t in (t_a_voided_judges_block_is_no_verdict, t_the_tick_resumes_the_voided_judges_own_session,
              t_a_fresh_judge_when_the_session_cannot_resume, t_a_counted_run_after_the_void_reads_normally,
              t_the_voided_runs_shard_seal_reopens_for_its_own_lines, t_the_resumed_judge_writes_its_old_shard):
        section(t)
    shutil.rmtree(TMP, ignore_errors=True)
    print("ALL PASS" if all(res) else "FAILED %d of %d" % (res.count(False), len(res)))
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
