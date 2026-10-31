#!/usr/bin/env python3
"""arena_replay_run: the replay DRIVING loop (`arena.py trial-runner --arm A`), the run loop arena_replay.py lacked.

WHAT. One process per replay arm (design 4.3: the replay arms run in parallel; the spend meter attributes calls by
per-arm task spans, so WITHIN an arm the tasks run strictly one after another). For each task of the frozen trial
list (arena_trial.DEFAULT_PATH, in that file's order: oldest first, a linear extension of the sibling relation, checked
with arena_rounds.check_rounds before anything runs - per ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM the replay
runs the list's own order) it calls arena_replay.run_one: a fresh no-future clone at the task's base (audited), the
arm's WORK in it, then the JUDGE, then the clone is deleted.

WORK, by arm (all model passes launch through RA.CmdModel.spawn -> arm_sandbox.wrap; nothing here runs a model):
  v3       v3_control.Procedure(...).work(spec); head = its sha (done/closed/live_owed), else the base.
  ralph_a  ralph_a_loop.Loop over [spec] in the clone, branch main made at the base, sync=None (a replay clone has no
           origin: no pull), publish_cmd="true" (no push: the tested head is ff-merged into the clone's main, which
           is all the judge reads); head = main.
  trio     trio_loop.TrioLoop the same way (its critic: trio_loop.default_critic()).
A parked task is judged too (head = base): the analysis counts a task as completed only on an accept/reject judge
verdict, and the era gate stays shut while any task of the newest era is uncompleted.

JUDGE: arena_gate.py (from the harness checkout, --repo the clone) writes the gate record, then
`arena_judge.py judge` (its own harness pass and signed judge event). Neither is edited or re-implemented here.

RESUME. <ctl>/<arm>/runner.json keeps each finished task's record; a restart skips them. A task whose work stopped
(STOP file, runway, sync, red start) or raised is NOT recorded and is retried on the next start; the runner waits
for runway before each task. <ctl>/<arm>/STOP stops it between tasks.

CLI: arena.py trial-runner --arm {ralph_a,trio,v3} [--ctl DIR] [--model-cmd CMD] [--only N]
     arena.py trial-runner --all   (ExecStart of rm-arena-replay.service: one child `--arm A` per [trial] replay_arms
     arm, all in parallel; exit = the worst child's). Each --arm process holds <ctl>/<arm>/runner.lock (flock): a
     second runner for the same arm refuses (exit 2) instead of working the same tasks twice.
     ($ARENA_REPLAY_MODEL_CMD, $ARENA_REPLAY_CTL). START GATE (each --arm): the model command must carry
     `--output-format json`, name its model by CLI alias or $VAR (read at each task's call, a missing one refused by
     name; never a literal id/account/host/key), and arena_model_snapshot.py --out <ctl>/<arm>/models/<stamp> must
     exit 0 (2: a model variable missing, 3: resolved model differs -> refused). Selftest: selftest_arena_replay_run.py.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

REPLAY_ARMS = ("ralph_a", "trio", "v3")
DEFAULT_CTL = "/mnt/d/ClaudeWork/rimmandrake/foundry_arena/replay/ctl"
HARNESS_REPO = HERE.parents[3]
STOPPED = ("STOP", "runway", "red start", "sync failed")
RUNWAY_WAIT_S = 600


class RunRefused(Exception):
    pass


def log(msg, out=None):
    (out or sys.stdout).write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), msg))
    (out or sys.stdout).flush()


# ------------------------------------------------------------------------------------------------ the plan
def plan(trial=None, *, p=None, source=None, contains=None, read_task=None, fixes=None):
    """-> [(task_id, {"base_sha", "fix_sha"})] in the trial list's order, sibling-checked; RunRefused otherwise."""
    import arena_replay as R
    import arena_rounds as RD
    import arena_trial as TR
    import arena_tasks as A
    p = p or A.paths()
    ids = R.trial_list(trial)
    fixes = fixes if fixes is not None else TR.hidden_fix_shas(p)
    read_task = read_task or (lambda tid: json.loads((Path(p["tasks"]) / ("%s.json" % tid)).read_text("utf-8")))
    tasks = {}
    for tid in ids:
        base = (read_task(tid) or {}).get("base_sha")
        if not (isinstance(base, str) and len(base) == 40):
            raise RunRefused("task %s has no 40-hex base_sha in its frozen file" % tid)
        if not isinstance(fixes.get(tid), str):
            raise RunRefused("task %s has no fix_sha in the judge's hidden file (the clone audit needs it)" % tid)
        tasks[tid] = {"base_sha": base, "fix_sha": fixes[tid]}
    R.check_trial(tasks, trial)
    if contains is None:
        contains = RD.contains_for(tasks, source or R.DEFAULT_SOURCE)
    RD.check_rounds(list(ids), contains)                 # refuses an order that gives a fix before its sibling's
    return [(tid, tasks[tid]) for tid in ids]


# ------------------------------------------------------------------------------------------------ state
class State:
    def __init__(self, ctl):
        self.f = Path(ctl) / "runner.json"
        self.d = json.loads(self.f.read_text()) if self.f.is_file() else {"done": {}, "errors": []}

    def done(self, tid):
        return tid in self.d["done"]

    def record(self, tid, rec):
        self.d["done"][tid] = rec
        self._save()

    def error(self, tid, why):
        self.d["errors"].append({"task": tid, "ts": time.time(), "why": why[:2000]})
        self._save()

    def _save(self):
        self.f.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.f.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.d, indent=1, sort_keys=True))
        os.replace(tmp, self.f)


# ------------------------------------------------------------------------------------------------ work per arm
def git(clone, *a):
    r = subprocess.run(["git", "-C", str(clone), *a], capture_output=True, text=True)
    if r.returncode != 0:
        raise RunRefused("git %s failed: %s" % (" ".join(a), r.stderr.strip()[:300]))
    return r.stdout.strip()


def work_v3(clone, spec, *, ctl, model_cmd, p, cap):
    import v3_control as V
    w = V.SignedWriter("v3", p, cap)
    pr = V.Procedure("v3", clone, Path(ctl) / "v3", model=V.CmdModel(model_cmd, "v3"), writer=w,
                     timeout_s=float(os.environ.get("V3_PASS_TIMEOUT_S", V.PASS_TIMEOUT_S)))
    out = pr.work(spec)
    if out.get("outcome") == "stop":
        raise RunRefused("v3 procedure stopped: STOP file in %s" % (Path(ctl) / "v3"))
    head = out.get("sha") if out.get("outcome") in ("done", "closed", "live_owed") else None
    return {"outcome": out.get("outcome"), "head": head or spec["base_sha"]}


def work_loop(arm, clone, spec, *, ctl, model_cmd, p, cap):
    import ralph_a_loop as RA
    git(clone, "switch", "-q", "-C", RA.MAIN, spec["base_sha"])
    tctl = Path(ctl) / arm / spec["id"]
    tctl.mkdir(parents=True, exist_ok=True)
    if arm == "trio":
        import trio_loop as TL
        lp = TL.TrioLoop(clone, tctl, [spec], model=TL.CmdModelT(model_cmd), writer=TL.SignedWriterT(p, cap),
                         lane=None, sync=None, publish_cmd="true",
                         timeout_s=float(os.environ.get("TRIO_PASS_TIMEOUT_S", RA.PASS_TIMEOUT_S)))
    else:
        lp = RA.Loop(clone, tctl, [spec], model=RA.CmdModel(model_cmd), writer=RA.SignedWriter(p, cap),
                     lane=None, sync=None, publish_cmd="true",
                     timeout_s=float(os.environ.get("RALPH_A_PASS_TIMEOUT_S", RA.PASS_TIMEOUT_S)))
    out = lp.run()
    last = out[-1] if out else ""
    if not last.startswith("done"):
        raise RunRefused("%s loop ended without finishing %s: %s" % (arm, spec["id"], last[:300]))
    head = git(clone, "rev-parse", RA.MAIN)
    return {"outcome": "parked" if head == spec["base_sha"] else "published", "head": head, "steps": out[-6:]}


def default_work(arm, clone, spec, *, ctl, model_cmd):
    import arena_eventlog as L
    import arena_tasks as A
    model_cmd = resolve_model_cmd(model_cmd)  # at call time: a variable unset since the start refuses by name
    p = A.paths()
    with L.harness_pass(p) as cap:
        if arm == "v3":
            return work_v3(clone, spec, ctl=ctl, model_cmd=model_cmd, p=p, cap=cap)
        return work_loop(arm, clone, spec, ctl=ctl, model_cmd=model_cmd, p=p, cap=cap)


def default_judge(arm, clone, spec, head, *, logdir):
    """arena_gate.py then arena_judge.py judge, both as the harness's own CLIs from the harness checkout."""
    logdir = Path(logdir)
    logdir.mkdir(parents=True, exist_ok=True)
    tid, base = spec["id"], spec["base_sha"]
    g = subprocess.run([sys.executable, str(HERE / "arena_gate.py"), "--task", tid, "--base", base, "--head", head,
                        "--arm", arm, "--repo", str(clone)], cwd=str(HARNESS_REPO), capture_output=True, text=True,
                       timeout=3 * 3600)
    gate = logdir / ("%s.gate.json" % tid)
    gate.write_text(g.stdout)
    (logdir / ("%s.gate.log" % tid)).write_text(g.stderr)
    try:
        json.loads(g.stdout)
    except ValueError:
        gate.write_text(json.dumps({"verdict": "invalid", "why": "gate printed no JSON (rc %s)" % g.returncode}))
    j = subprocess.run([sys.executable, str(HERE / "arena_judge.py"), "judge", "--task", tid, "--clone", str(clone),
                        "--base", base, "--head", head, "--arm", arm, "--gate", str(gate)], cwd=str(HARNESS_REPO),
                       capture_output=True, text=True, timeout=3 * 3600)
    (logdir / ("%s.judge.log" % tid)).write_text(j.stdout + "\n--- stderr\n" + j.stderr)
    try:
        rec = json.loads(j.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise RunRefused("judge printed no record for %s (rc %s): %s" % (tid, j.returncode, j.stderr[-400:]))
    return {"verdict": rec.get("verdict"), "judge_id": rec.get("judge_id"), "gate": gate.name,
            "gate_verdict": json.loads(gate.read_text()).get("verdict")}


# ------------------------------------------------------------------------------------------------ the run
def run_arm(arm, *, ctl, model_cmd, only=0, steps=None, load=None, run_one=None, work=None, judge=None,
            runway=None, sleep=time.sleep, out=None):
    """Every trial task for `arm`, in order. -> {"ran": [...], "skipped": [...], "stopped": why|None}."""
    if arm not in REPLAY_ARMS:
        raise RunRefused("arm %r is not a replay arm %s" % (arm, REPLAY_ARMS))
    if not model_cmd:
        raise RunRefused("no model command: pass --model-cmd or set ARENA_REPLAY_MODEL_CMD")
    import arena_replay as R
    import ralph_a_loop as RA
    steps = steps if steps is not None else plan()
    run_one = run_one or R.run_one
    work = work or (lambda a, c, s: default_work(a, c, s, ctl=ctl, model_cmd=model_cmd))
    judge = judge or (lambda a, c, s, h: default_judge(a, c, s, h, logdir=Path(ctl) / arm / "judge"))
    runway = runway or RA.default_runway
    if load is None:
        import arena_tasks as A
        p = A.paths()
        load = lambda tid: A.load_frozen(tid, p)              # noqa: E731
    actl = Path(ctl) / arm
    actl.mkdir(parents=True, exist_ok=True)
    st = State(actl)
    res = {"ran": [], "skipped": [], "stopped": None}
    log("%s: plan %d tasks, %d already done" % (arm, len(steps), sum(st.done(t) for t, _ in steps)), out)
    for tid, t in steps:
        if st.done(tid):
            res["skipped"].append(tid)
            continue
        if only and len(res["ran"]) >= only:
            break
        if (actl / "STOP").exists():
            res["stopped"] = "STOP file"
            break
        while True:
            r = runway()
            if isinstance(r, dict) and r.get("state") == "MEASURED" and isinstance(r.get("runway"), (int, float)) \
                    and r["runway"] >= RA.runway_min():
                break
            log("%s: runway %r below %s / unmeasured: waiting %ds" % (arm, r, RA.runway_min(), RUNWAY_WAIT_S), out)
            if (actl / "STOP").exists():
                break
            sleep(RUNWAY_WAIT_S)
        if (actl / "STOP").exists():
            res["stopped"] = "STOP file"
            break
        spec = load(tid)
        if spec.get("base_sha") != t["base_sha"]:
            raise RunRefused("task %s: frozen spec base %s != plan base %s" % (tid, spec.get("base_sha"), t["base_sha"]))
        log("%s: task %s START base %s" % (arm, tid, t["base_sha"][:12]), out)
        box = {}

        def w(clone):
            box.update(work(arm, clone, spec))
            log("%s: task %s work %s head %s" % (arm, tid, box.get("outcome"), str(box.get("head"))[:12]), out)

        try:
            v = run_one(arm, tid, t["base_sha"], t["fix_sha"], w, lambda clone: judge(arm, clone, spec, box["head"]))
        except Exception as e:                    # noqa: BLE001 - recorded and retried on the next start
            why = "%s: %s" % (type(e).__name__, e)
            st.error(tid, why)
            log("%s: task %s ERROR %s" % (arm, tid, why[:500]), out)
            res["stopped"] = "error on %s: %s" % (tid, why[:300])
            break
        rec = dict(box, judge=v, ts=time.time())
        st.record(tid, rec)
        res["ran"].append(tid)
        log("%s: task %s DONE %s verdict %s" % (arm, tid, box.get("outcome"), (v or {}).get("verdict")), out)
    log("%s: runner ends: ran %d, skipped %d, stopped %s" % (arm, len(res["ran"]), len(res["skipped"]),
                                                             res["stopped"]), out)
    return res


def pin_state_home(env=None):
    """arena_replay._arm_environ gives work()/judge() a private empty HOME, and the harness token's default path is
    ~/.local/state/... (arena_eventlog._default_token_path): unpinned, harness_pass and arena_judge.py look in the temp
    HOME and refuse 'no harness token'. Pin XDG_STATE_HOME to the REAL home's state dir (pwd, not $HOME) in the
    harness process. It never crosses into an arm: XDG_STATE_HOME is not on arm_sandbox's env allow-list."""
    import pwd
    env = os.environ if env is None else env
    if not env.get("XDG_STATE_HOME", "").strip():
        env["XDG_STATE_HOME"] = os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".local", "state")
    return env["XDG_STATE_HOME"]


def arm_lock(ctl, arm):
    """Take <ctl>/<arm>/runner.lock (flock, held for the process's life). Raises RunRefused if another runner of the
    same arm holds it."""
    import fcntl
    d = Path(ctl) / arm
    d.mkdir(parents=True, exist_ok=True)
    fh = open(d / "runner.lock", "a+")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fh.close()
        raise RunRefused("another %s runner holds %s" % (arm, d / "runner.lock"))
    return fh


MODEL_ALIASES = ("opus", "sonnet", "haiku")
_VAR_RE = __import__("re").compile(r"\$\{([A-Z_][A-Z0-9_]*)\}|\$([A-Z_][A-Z0-9_]*)")
_ACCOUNT_RE = __import__("re").compile(r"^(us|eu|apac|global)\.|arn:|://|@|\.amazonaws\.|bedrock|vertex", __import__("re").I)


def resolve_model_cmd(cmd, env=None):
    """The replay model command, checked and expanded AT CALL TIME (each task). It comes from --model-cmd /
    $ARENA_REPLAY_MODEL_CMD only. Refused: no `--output-format json` (the spend meter reconciles calls from the JSON
    result; the loops' CmdModel parses its `result`); a `--model` that is not a CLI alias (opus/sonnet/haiku, resolved
    by the CLI through the environment) nor a $VAR reference; anything naming an account, host, region or key. A
    $VAR / ${VAR} (e.g. $ANTHROPIC_DEFAULT_OPUS_MODEL) is read from the environment now and a missing one is refused
    BY NAME."""
    env = os.environ if env is None else env
    if not (cmd or "").strip():
        raise RunRefused("no model command: pass --model-cmd or set ARENA_REPLAY_MODEL_CMD")
    missing = sorted({a or b for a, b in _VAR_RE.findall(cmd) if not (env.get(a or b) or "").strip()})
    if missing:
        raise RunRefused("model command needs %s, unset in the environment" % ", ".join(missing))
    raw = shlex.split(cmd)
    for i, t in enumerate(raw):
        if t == "--model" and i + 1 < len(raw):
            v = raw[i + 1]
            if v not in MODEL_ALIASES and not _VAR_RE.fullmatch(v):
                raise RunRefused("model command --model %r: use a CLI alias (%s) or a $VAR from the environment, "
                                 "never a literal model id" % (v, "/".join(MODEL_ALIASES)))
        elif t.startswith("--model="):
            raise RunRefused("model command: write `--model ALIAS`, not %r" % t)
    out = _VAR_RE.sub(lambda m: env[m.group(1) or m.group(2)].strip(), cmd)
    toks = shlex.split(out)
    for t in toks[1:]:
        if not t.startswith("-") and _ACCOUNT_RE.search(t):
            raise RunRefused("model command names an account/host/key-shaped value %r" % t)
    fmt = [toks[i + 1] for i, t in enumerate(toks[:-1]) if t == "--output-format"] + \
          [t.split("=", 1)[1] for t in toks if t.startswith("--output-format=")]
    if fmt != ["json"]:
        raise RunRefused("model command must carry `--output-format json` exactly once (got %r)" % fmt)
    return out


def model_snapshot(arm, ctl, *, run=subprocess.run, out=None):
    """arena_model_snapshot.py --out <ctl>/<arm>/models/<stamp> at runner start: exit 2 (a model variable missing) or
    3 (the resolved model differs) refuses the start; any other non-zero refuses too."""
    d = Path(ctl) / arm / "models" / time.strftime("%Y%m%dT%H%M%S")
    d.mkdir(parents=True, exist_ok=True)
    r = run([sys.executable, str(HERE / "arena_model_snapshot.py"), "--out", str(d)],
            capture_output=True, text=True, timeout=300)
    why = {2: "a model variable is missing", 3: "the resolved model differs"}.get(r.returncode, "failed")
    if r.returncode != 0:
        raise RunRefused("model snapshot exit %s (%s): %s" % (r.returncode, why, (r.stderr or r.stdout).strip()[-400:]))
    log("%s: model snapshot ok -> %s" % (arm, d / "resolved_models.json"), out)
    return d


def run_all(arms, passthrough, *, arena_py=None, popen=subprocess.Popen, out=sys.stdout):
    """Fan out one `arena.py trial-runner --arm A` child per arm, in parallel; wait for all; worst exit code."""
    arms = list(arms or [])
    bad = [a for a in arms if a not in REPLAY_ARMS]
    if not arms or bad:
        raise RunRefused("replay_arms %r: must be a non-empty subset of %s" % (arms, REPLAY_ARMS))
    py = arena_py or str(Path(__file__).resolve().parent / "arena.py")
    kids = [(a, popen([sys.executable, py, "trial-runner", "--arm", a] + list(passthrough))) for a in arms]
    for a, k in kids:
        log("all: %s runner pid %s" % (a, k.pid), out)
    rcs = {a: k.wait() for a, k in kids}
    log("all: runners exited %s" % json.dumps(rcs), out)
    return max(rcs.values())


def main(argv=None, *, arms=None):
    """arms: the [trial] replay_arms list (arena.trial_runner reads arm.toml), used by --all only."""
    import argparse
    ap = argparse.ArgumentParser(prog="arena trial-runner", description=__doc__.split("\n")[0])
    ap.add_argument("--arm", choices=REPLAY_ARMS, help="the replay arm this process drives (one process per arm)")
    ap.add_argument("--all", action="store_true", help="one child runner per [trial] replay_arms arm, in parallel")
    ap.add_argument("--ctl", default=os.environ.get("ARENA_REPLAY_CTL", DEFAULT_CTL))
    ap.add_argument("--model-cmd", default=os.environ.get("ARENA_REPLAY_MODEL_CMD"))
    ap.add_argument("--only", type=int, default=0, help="stop after N tasks (0: all)")
    ap.add_argument("--plan", action="store_true", help="print the plan and exit")
    a = ap.parse_args(argv)
    if os.environ.get("RM_ARM"):
        print("refused: the replay runner is harness code; run it without RM_ARM", file=sys.stderr)
        return 2
    if a.all and a.arm:
        print("refused: --all and --arm are exclusive", file=sys.stderr)
        return 2
    if not a.arm and not a.plan and not a.all:
        print("refused: give --arm (one of %s) or --all; one runner process per replay arm" % ", ".join(REPLAY_ARMS),
              file=sys.stderr)
        return 2
    try:
        if a.all:
            rest = ["--ctl", a.ctl, "--only", str(a.only)]
            if a.model_cmd:
                rest += ["--model-cmd", a.model_cmd]
            return run_all(arms, rest)
        steps = plan()
        if a.plan:
            print(json.dumps([tid for tid, _ in steps], indent=1))
            return 0
        lock = arm_lock(a.ctl, a.arm)  # noqa: F841 - held until exit
        resolve_model_cmd(a.model_cmd)
        pin_state_home()
        model_snapshot(a.arm, a.ctl)
        res = run_arm(a.arm, ctl=a.ctl, model_cmd=a.model_cmd, only=a.only, steps=steps)
    except RunRefused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 2
    return 0 if res["stopped"] is None else 1


if __name__ == "__main__":
    print("run it as `arena.py trial-runner` (the signed log opens only for a harness entrypoint)", file=sys.stderr)
    sys.exit(2)
