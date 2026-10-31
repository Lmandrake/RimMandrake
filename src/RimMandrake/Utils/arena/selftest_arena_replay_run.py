#!/usr/bin/env python3
"""selftest_arena_replay_run.py - arena_replay_run.py (the replay driving loop), each criterion by FORCED FAILURE.

  order     run_arm works the tasks in exactly the plan's order, one at a time; a plan whose order gives a task before
            a sibling its base contains is REFUSED by plan() (check_rounds); a task set unlike the trial list is refused
  resume    a finished task is skipped on restart; a task whose work raised is NOT recorded (retried next start) and
            stops the runner (never a silent skip to the next task)
  stop      a STOP file stops between tasks; runway below the minimum waits (no task starts) until it recovers
  arms      a non-replay arm (v3c, bench) is refused; no model command is refused
  judged    every finished task (a parked one included) carries the judge's record, judged on the work's head
  wired     `arena.py trial-runner` without --arm refuses (exit 2) and never pretends to run; the rendered
            rm-arena-replay.service runs `trial-runner --all` (ARENA_REPLAY_UNIT_FIX_NO_ARM_REFUSED: the unit gave no
            --arm and was refused); --all fans out one --arm child per replay arm and refuses a non-replay arm
  token     the harness state dir is pinned to the REAL home (XDG_STATE_HOME), so the scrubbed temp HOME of
            work()/judge() still finds the harness token; XDG_STATE_HOME is not let into an arm sandbox
  lock      a second runner of the same arm refuses (runner.lock held) instead of double-running
  model     the model command needs `--output-format json`; --model is a CLI alias or a $VAR read at call time (a
            missing one refused by name); a literal id, account/region prefix or host is refused
  snapshot  arena_model_snapshot.py exit 2/3/other refuses the arm's start; exit 0 starts it
Fakes only: no clone, no model, no judge, no signed log.
"""
import io
import os
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_replay_run as RR  # noqa: E402

FAILS = []
OK_RUNWAY = lambda: {"state": "MEASURED", "runway": 1.0}  # noqa: E731


def check(c, what):
    print("%s  %s" % ("ok  " if c else "FAIL", what))
    if not c:
        FAILS.append(what)


def steps(ids):
    return [(t, {"base_sha": ("%x" % i).rjust(40, "0"), "fix_sha": ("f%x" % i).rjust(40, "0")})
            for i, t in enumerate(ids, 1)]


def fakes(st, seen, fail_on=()):
    def run_one(arm, tid, base, fix, work, judge):
        seen.append(("start", tid))
        work("/clone/" + tid)
        v = judge("/clone/" + tid)
        seen.append(("end", tid))
        return v

    def work(arm, clone, spec):
        if spec["id"] in fail_on:
            raise RuntimeError("model died")
        parked = spec["id"].endswith("P")
        return {"outcome": "parked" if parked else "published", "head": spec["base_sha"] if parked else "e" * 40}

    def judge(arm, clone, spec, head):
        return {"verdict": "reject" if head == spec["base_sha"] else "accept", "head": head}

    load = lambda tid: {"id": tid, "base_sha": dict(st)[tid]["base_sha"], "live": "none"}  # noqa: E731
    return dict(run_one=run_one, work=work, judge=judge, load=load)


def t_order(tmp):
    st = steps(["T3", "T1", "T2P"])
    seen = []
    r = RR.run_arm("v3", ctl=tmp / "o", model_cmd="x", steps=st, runway=OK_RUNWAY, out=io.StringIO(), **fakes(st, seen))
    check([t for k, t in seen if k == "start"] == ["T3", "T1", "T2P"], "tasks run in exactly the plan's order")
    check(all(seen[i][0] == "start" and seen[i + 1] == ("end", seen[i][1]) for i in range(0, len(seen), 2)),
          "one task at a time: each ends before the next starts")
    d = json.loads((tmp / "o" / "v3" / "runner.json").read_text())["done"]
    check(d["T2P"]["outcome"] == "parked" and d["T2P"]["judge"]["verdict"] == "reject",
          "a parked task is judged too (on the base), never left uncompleted")
    check(d["T1"]["judge"]["head"] == "e" * 40, "the judge gets the work's head")
    check(r["stopped"] is None and len(r["ran"]) == 3, "a clean run ends unstopped")


def t_plan_refusals():
    import arena_tasks as A
    ids = ["A1", "B2"]
    fx = {"A1": "1" * 40, "B2": "2" * 40}
    rt = lambda tid: {"base_sha": {"A1": "a" * 40, "B2": "b" * 40}[tid]}  # noqa: E731
    out = RR.plan(ids, p={"tasks": "/nonexistent"}, contains={}, read_task=rt, fixes=fx)
    check([t for t, _ in out] == ids, "plan keeps the trial list's order")
    try:
        RR.plan(ids, p={"tasks": "/x"}, contains={"A1": ["B2"]}, read_task=rt, fixes=fx)
        check(False, "a fix given before its sibling is refused")
    except A.TaskRefused:
        check(True, "a fix given before its sibling is refused")
    try:
        RR.plan(ids, p={"tasks": "/x"}, contains={}, read_task=rt, fixes={"A1": "1" * 40})
        check(False, "a task with no fix sha is refused")
    except RR.RunRefused:
        check(True, "a task with no fix sha is refused")


def t_resume(tmp):
    st = steps(["T1", "T2", "T3"])
    seen = []
    r = RR.run_arm("trio", ctl=tmp / "r", model_cmd="x", steps=st, runway=OK_RUNWAY, out=io.StringIO(),
                   **fakes(st, seen, fail_on=("T2",)))
    d = json.loads((tmp / "r" / "trio" / "runner.json").read_text())
    check(r["stopped"] and "T2" in r["stopped"] and "T3" not in d["done"], "a raising task stops the runner")
    check("T2" not in d["done"] and d["errors"][-1]["task"] == "T2", "a raising task is not recorded as done")
    seen2 = []
    r2 = RR.run_arm("trio", ctl=tmp / "r", model_cmd="x", steps=st, runway=OK_RUNWAY, out=io.StringIO(),
                    **fakes(st, seen2))
    check([t for k, t in seen2 if k == "start"] == ["T2", "T3"] and r2["skipped"] == ["T1"],
          "restart skips the finished task and retries the failed one first")


def t_stop_runway(tmp):
    st = steps(["T1", "T2"])
    (tmp / "s" / "ralph_a").mkdir(parents=True)
    (tmp / "s" / "ralph_a" / "STOP").touch()
    seen = []
    r = RR.run_arm("ralph_a", ctl=tmp / "s", model_cmd="x", steps=st, runway=OK_RUNWAY, out=io.StringIO(),
                   **fakes(st, seen))
    check(not seen and r["stopped"] == "STOP file", "a STOP file stops before any task")
    readings = [{"state": "MEASURED", "runway": 0.01}, {"state": "UNMEASURED"}, {"state": "MEASURED", "runway": 1.0}]
    slept = []
    seen = []
    RR.run_arm("ralph_a", ctl=tmp / "w", model_cmd="x", steps=st[:1], runway=lambda: readings.pop(0),
               sleep=slept.append, out=io.StringIO(), **fakes(st, seen))
    check(len(slept) == 2 and seen[0] == ("start", "T1"), "low/unmeasured runway waits; the task starts once it is back")


def t_arms(tmp):
    for bad in ("v3c", "bench", "ralph_c"):
        try:
            RR.run_arm(bad, ctl=tmp / "a", model_cmd="x", steps=[], out=io.StringIO())
            check(False, "arm %s refused" % bad)
        except RR.RunRefused:
            check(True, "arm %s refused" % bad)
    try:
        RR.run_arm("v3", ctl=tmp / "a", model_cmd="", steps=[], out=io.StringIO())
        check(False, "no model command refused")
    except RR.RunRefused:
        check(True, "no model command refused")


def t_wired():
    r = subprocess.run([sys.executable, str(HERE / "arena.py"), "trial-runner"], capture_output=True, text=True)
    check(r.returncode == 2 and "--arm" in r.stderr, "trial-runner without --arm refuses (exit 2)")


def t_unit_all(tmp):
    import arena as AR
    u = AR.render_replay_unit(str(tmp / "arm.toml"), "/x/arena.py")
    ex = [l for l in u.splitlines() if l.startswith("ExecStart=")]
    check(ex == ["ExecStart=/usr/bin/python3 /x/arena.py trial-runner --all"], "rendered replay unit runs trial-runner --all")
    r = subprocess.run([sys.executable, str(HERE / "arena.py"), "trial-runner", "--all", "--arm", "v3"],
                       capture_output=True, text=True)
    check(r.returncode == 2 and "exclusive" in r.stderr, "--all with --arm refuses (exit 2)")
    calls = []

    class K:
        def __init__(self, argv):
            calls.append(argv)
            self.pid = len(calls)

        def wait(self):
            return 1 if "trio" in calls[self.pid - 1] else 0
    rc = RR.run_all(["ralph_a", "trio", "v3"], ["--ctl", "C"], arena_py="/x/arena.py", popen=K, out=io.StringIO())
    check([c[2:5] for c in calls] == [["trial-runner", "--arm", a] for a in ("ralph_a", "trio", "v3")]
          and all(c[-2:] == ["--ctl", "C"] for c in calls), "--all starts one --arm child per replay arm")
    check(rc == 1, "--all exits with the worst child's code")
    for bad in (["v3c"], [], None):
        try:
            RR.run_all(bad, [], popen=K, out=io.StringIO())
            check(False, "--all refuses replay_arms %r" % (bad,))
        except RR.RunRefused:
            check(True, "--all refuses replay_arms %r" % (bad,))


def t_lock(tmp):
    h = RR.arm_lock(tmp / "L", "v3")
    r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import arena_replay_run as RR\n"
                        "try:\n RR.arm_lock(%r, 'v3'); print('took')\nexcept RR.RunRefused: print('refused')"
                        % (str(HERE), str(tmp / "L"))], capture_output=True, text=True)
    check(r.stdout.strip() == "refused", "a second v3 runner refuses while the lock is held")
    h.close()
    h2 = RR.arm_lock(tmp / "L", "v3")
    check(h2 is not None, "the lock is free again once its holder exits")
    h2.close()


def t_token_home():
    import os
    import pwd
    import arm_sandbox as SB
    real = os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".local", "state")
    env = {"HOME": "/tmp/arm_home_x"}
    check(RR.pin_state_home(env) == real and env["XDG_STATE_HOME"] == real,
          "state dir pinned to the real home, not the scrubbed HOME")
    env = {"XDG_STATE_HOME": "/s"}
    check(RR.pin_state_home(env) == "/s", "an explicit XDG_STATE_HOME is kept")
    keep = SB.env_keep("model")
    check("XDG_STATE_HOME" not in keep and not SB.ENV_ALLOW_RE.match("XDG_STATE_HOME"),
          "XDG_STATE_HOME never crosses into an arm sandbox")


def t_model_cmd():
    good = "/x/claude -p --model opus --dangerously-skip-permissions --output-format json"
    check(RR.resolve_model_cmd(good, {}) == good, "alias + --output-format json passes unchanged")

    def refused(cmd, env, what, needle=""):
        try:
            RR.resolve_model_cmd(cmd, env)
            check(False, what)
        except RR.RunRefused as e:
            check(needle in str(e), what + (" (names %s)" % needle if needle else ""))
    refused("/x/claude -p --model opus", {}, "no --output-format json refused", "--output-format json")
    refused("/x/claude -p --model opus --output-format text", {}, "--output-format text refused")
    refused("/x/claude -p --model $ANTHROPIC_DEFAULT_OPUS_MODEL --output-format json", {},
            "an unset $ANTHROPIC_DEFAULT_OPUS_MODEL refused by name", "ANTHROPIC_DEFAULT_OPUS_MODEL")
    out = RR.resolve_model_cmd("/x/claude -p --model ${ANTHROPIC_DEFAULT_OPUS_MODEL} --output-format json",
                               {"ANTHROPIC_DEFAULT_OPUS_MODEL": "fam-1"})
    check("--model fam-1" in out, "a set $VAR is read from the environment at call time")
    refused("/x/claude -p --model claude-opus-x --output-format json", {}, "a literal model id refused", "literal")
    refused("/x/claude -p --model $M --output-format json", {"M": "us.vendor.model-1"},
            "an account/region-prefixed id via env refused", "account")
    refused("/x/claude -p --model opus --output-format json --endpoint https://h", {}, "a host in the cmd refused")
    refused("", {}, "an empty model command refused")


def t_snapshot_gate(tmp):
    class R:
        def __init__(self, rc):
            self.returncode, self.stdout, self.stderr = rc, "", "why"
    seen = []
    for rc, ok in ((0, True), (2, False), (3, False), (1, False)):
        try:
            d = RR.model_snapshot("v3", tmp / "snap", run=lambda argv, **k: seen.append(argv) or R(rc),
                                  out=io.StringIO())
            check(ok and d.parent.name == "models", "snapshot exit %d starts the arm" % rc)
        except RR.RunRefused as e:
            check(not ok and ("exit %d" % rc) in str(e), "snapshot exit %d refuses the start" % rc)
    check(seen[0][1].endswith("arena_model_snapshot.py") and seen[0][2] == "--out", "the snapshot tool is the one run")


def t_start_repair(tmp):
    """ARENA_REPLAY_SWEEP_REPAIR_ORPHAN_CLONE / ARENA_LOOP_STOP_REPAIR_STALE_ON_RETRY / ARENA_ORPHAN_BUILD_UNSTICK_V3_ARM_BRICKED:
    the start repair sweeps a free orphan clone (marker or not), leaves a held one and a non-task dir, removes a
    per-task stale STOP but never the operator's <ctl>/<arm>/STOP, and voids v3 orphans only through void_orphans."""
    import arena_replay as R
    import v3_control as V
    root = tmp / "sr_arena"
    ctl = tmp / "sr_ctl"
    steps = [("T1", {}), ("T2", {}), ("T3", {})]
    a = R.replay_dir(root) / "ralph_a"
    for n in ("T1", "T2", "NOT_A_TASK"):
        (a / n / ".git").mkdir(parents=True)
        (a / n / "f").write_text("x")
    for d in ("T1", "T3"):
        (ctl / "ralph_a" / d).mkdir(parents=True)
        (ctl / "ralph_a" / d / "STOP").touch()
    (ctl / "ralph_a" / "STOP").touch()
    with R._lock("ralph_a", "T2", root):
        res = RR.start_repair("ralph_a", ctl, steps, root=root, out=io.StringIO())
    check(not (a / "T1").exists() and res["clones"] == [str(a / "T1")], "a free orphan clone with no marker is swept")
    check((a / "T2").exists(), "a clone whose run lock is held is left alone")
    check((a / "NOT_A_TASK").exists(), "a dir that is not a trial task is left alone")
    check(not (ctl / "ralph_a" / "T1" / "STOP").exists() and not (ctl / "ralph_a" / "T3" / "STOP").exists()
          and len(res["stops"]) == 2, "stale per-task STOP files are removed")
    check((ctl / "ralph_a" / "STOP").exists(), "the operator's arm-level STOP is never removed")
    check(res["voided"] == [], "a non-v3 arm voids nothing")
    seen = []
    real = V.void_orphans
    V.void_orphans = lambda w, arm, why, out=None: seen.append((w, arm, why)) or ["B1"]
    try:
        r3 = RR.start_repair("v3", ctl, steps, root=root, writer="W", out=io.StringIO())
        r0 = RR.start_repair("v3", ctl, steps, root=root, writer=None, out=io.StringIO())
    finally:
        V.void_orphans = real
    check(r3["voided"] == ["B1"] and seen and seen[0][:2] == ("W", "v3") and seen[0][2],
          "v3 start voids orphans through void_orphans with a reason")
    check(r0["voided"] == [] and len(seen) == 1, "no writer: nothing voided")
    os.symlink(str(tmp), str(R.replay_dir(root) / "v3"))
    try:
        RR.start_repair("v3", ctl, steps, root=root, out=io.StringIO())
        check(False, "a symlinked arm dir refuses")
    except RR.RunRefused:
        check(True, "a symlinked arm dir refuses")
    check("_start_repair_live(a.arm, a.ctl, steps)" in Path(RR.__file__).read_text(), "main runs the start repair")


def t_tester_tmp(tmp):
    """ARENA_TESTER_TMP_RELOCATE_TMPFS_RAM_BOMB: the tester base is per arm/task, emptied first, removed after, never
    on tmpfs, never relative; every loop gets it."""
    base = Path(tempfile.mkdtemp(prefix="st_rr_tt_", dir="/var/tmp"))
    try:
        d = RR.tester_tmp("v3", "T1", env={"RALPH_A_TESTER_TMP": str(base)})
        check(d == Path(os.path.realpath(base)) / "v3" / "T1" and d.is_dir(), "tester tmp is <base>/<arm>/<task>")
        (d / "junk").write_text("x")
        d2 = RR.tester_tmp("v3", "T1", env={"RALPH_A_TESTER_TMP": str(base)})
        check(d2 == d and not (d / "junk").exists(), "a leftover from an earlier attempt is emptied")
        RR.tester_tmp_done(d)
        check(not d.exists(), "removed after the task")
        for env, why in (({"RALPH_A_TESTER_TMP": "rel/x"}, "relative"),
                         ({"RALPH_A_TESTER_TMP": "/dev/shm/st_rr_tt"}, "tmpfs")):
            try:
                RR.tester_tmp("v3", "T1", env=env)
                check(False, "a %s tester base refuses" % why)
            except RR.RunRefused:
                check(True, "a %s tester base refuses" % why)
        check(RR._fs_type(RR.TESTER_TMP_DEFAULT.rsplit("/", 1)[0]) not in ("tmpfs", "ramfs"), "the default is not RAM")
        src = Path(RR.__file__).read_text()
        check(src.count("tester_tmp=str(tt) if tt else None") == 3, "all three loops get the per-task tester base")
    finally:
        shutil.rmtree(base, ignore_errors=True)
        shutil.rmtree("/dev/shm/st_rr_tt", ignore_errors=True)


def t_judge_home(tmp):
    """ARENA_JUDGE_HOME_REWIRE_ARM_TMP_LEAK: the gate and judge CLIs get the REAL home even inside _arm_environ, and
    RM_DATA_ROOT is pinned at start from the real environment."""
    import pwd
    import arena_replay as R
    real = pwd.getpwuid(os.getuid()).pw_dir
    env = {"PATH": "/usr/bin"}
    v = RR.pin_data_root(env)
    check(v and env["RM_DATA_ROOT"] == v, "RM_DATA_ROOT pinned when unset")
    env2 = {"RM_DATA_ROOT": "/x"}
    check(RR.pin_data_root(env2) == "/x", "an explicit RM_DATA_ROOT is kept")
    with R._arm_environ():
        check(os.environ["HOME"] != real, "fixture: _arm_environ moves HOME")
        e = RR.harness_env()
        check(e["HOME"] == real and e.get("GIT_CONFIG_GLOBAL") == "/dev/null", "harness_env: real HOME, git scrub kept")
    seen = []

    class P:
        returncode, stdout, stderr = 0, "{}", ""
    real_run = RR.subprocess.run
    RR.subprocess.run = lambda argv, **k: seen.append(k.get("env")) or P()
    try:
        with R._arm_environ():
            try:
                RR.default_judge("v3", tmp, {"id": "T", "base_sha": "b"}, "h", logdir=tmp / "jl")
            except RR.RunRefused:
                pass
    finally:
        RR.subprocess.run = real_run
    check(len(seen) == 2 and all(e and e.get("HOME") == real for e in seen), "gate and judge both run with the real HOME")
    check("pin_data_root()" in Path(RR.__file__).read_text(), "main pins RM_DATA_ROOT")


def t_fail_loud(tmp):
    """ARENA_GATE_WORK_REWIRE_OFF_DRVFS: an all-UNMEASURED or invalid gate, or an invalid judge, stops the runner
    loudly; a measured pass/fail goes through; the gate's checkouts are on ext4, not the /mnt/d data root."""
    U = {"status": "UNMEASURED"}
    check(RR.unmeasured_result({"verdict": "invalid", "steps": {"a": U, "b": U}}, {"verdict": "fail"}),
          "all-UNMEASURED gate refuses")
    check(RR.unmeasured_result({"verdict": "invalid", "steps": {"a": U, "b": {"status": "PASS"}}}, {}),
          "an invalid gate refuses")
    check(RR.unmeasured_result({"verdict": "pass", "steps": {"a": {"status": "PASS"}}}, {"verdict": "invalid"}),
          "an invalid judge refuses")
    for v in ("pass", "fail"):
        check(RR.unmeasured_result({"verdict": v, "steps": {"a": {"status": v.upper()}, "b": {"status": "NA"}}},
                                   {"verdict": v}) is None, "a measured %s goes through" % v)
    import arena_gate as G
    saved = os.environ.pop("ARENA_GATE_WORK", None)
    try:
        r = str(G.gate_work_root())
        check(not r.startswith("/mnt/") and RR._fs_type(os.path.realpath(r.rsplit("/judge", 1)[0])) not in
              ("9p", "drvfs", "v9fs", "virtiofs"), "gate work root is not on a Windows mount: %s" % r)
    finally:
        if saved is not None:
            os.environ["ARENA_GATE_WORK"] = saved
    seen = []

    class P:
        def __init__(self, out):
            self.returncode, self.stdout, self.stderr = 0, out, ""
    outs = [json.dumps({"verdict": "invalid", "steps": {"a": U}}), json.dumps({"verdict": "invalid"})]
    real_run = RR.subprocess.run
    RR.subprocess.run = lambda argv, **k: seen.append(1) or P(outs[len(seen) - 1])
    try:
        RR.default_judge("v3", tmp, {"id": "T", "base_sha": "b"}, "h", logdir=tmp / "jl2")
        check(False, "an all-UNMEASURED task stops the runner")
    except RR.RunRefused as e:
        check("all-UNMEASURED" in str(e), "an all-UNMEASURED task stops the runner: %s" % e)
    finally:
        RR.subprocess.run = real_run


def main():
    tmp = Path(tempfile.mkdtemp(prefix="st_replay_run_"))
    try:
        for fn, a in ((t_order, (tmp,)), (t_plan_refusals, ()), (t_resume, (tmp,)), (t_stop_runway, (tmp,)),
                      (t_arms, (tmp,)), (t_wired, ()),
                      (t_unit_all, (tmp,)), (t_lock, (tmp,)), (t_token_home, ()),
                      (t_model_cmd, ()), (t_snapshot_gate, (tmp,)), (t_start_repair, (tmp,)),
                      (t_tester_tmp, (tmp,)), (t_judge_home, (tmp,)), (t_fail_loud, (tmp,))):
            try:
                fn(*a)
            except Exception as e:  # noqa: BLE001
                check(False, "%s crashed: %s: %s" % (fn.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
