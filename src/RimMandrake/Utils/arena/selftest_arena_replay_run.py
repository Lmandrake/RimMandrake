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
Fakes only: no clone, no model, no judge, no signed log.
"""
import io
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


def main():
    tmp = Path(tempfile.mkdtemp(prefix="st_replay_run_"))
    try:
        for fn, a in ((t_order, (tmp,)), (t_plan_refusals, ()), (t_resume, (tmp,)), (t_stop_runway, (tmp,)),
                      (t_arms, (tmp,)), (t_wired, ()),
                      (t_unit_all, (tmp,)), (t_lock, (tmp,)), (t_token_home, ())):
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
