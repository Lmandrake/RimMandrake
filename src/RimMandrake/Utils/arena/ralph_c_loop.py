#!/usr/bin/env python3
r"""ralph_c_loop.py - the `ralph_c` arm assembled: two builder loops split by area, both runners, one tester pass per
loop, and runner back-pressure (ARENA_RALPHC_BUILD_BUILDERS_WAIT_ON_TESTERS).

Design: architecture_switch_harness_2026-10-29.md step 14 and section 1.8; testpilot_merged_2026-10-29.md section 2.3
(owner, binding: a different agent tests what was built, before the builder's next build pass; "a builder does not
take a new live-needing item while one of its candidates waits for a lane"); ralph_loop_design_2026-10-29.md
section 3.1 (variant C: builders A1 and A2 own fixed areas, steal only when their own list is empty, the gate refuses
an edit outside the item's area unless the item lists the file as shared, builders never take the bridge, both
runners pull one queue oldest first) and the `+sub` option (bounded read/search subagents inside a pass).

WHAT IS REUSED, NOT REWRITTEN
  * each builder loop IS ralph_a_loop.Loop (build pass, AT ONCE a fresh blind tester pass, the build-phase and final
    gates, the lane wait, parking after 3 tries, runway, precheck, bridge release). LoopC overrides only: the arm tag
    and run ids, where the next task comes from (the shared Board), the area guard in front of the gate, the
    per-loop tested check, the build prompt's ralph_c section, and the status the switch reads.
  * the live lane is ralph_a_loop.RalphCLane (ralph_c_runner's candidate queue); the runners are
    ralph_c_runner.run_one on lanes steve and archmagi, driven here by `runner_loop`.

THE RULES THIS FILE ADDS, each enforced in code:
  R1 AREAS.  areas.json maps each member (a1, a2) to path globs; the two lists may not overlap. A task's HOME is the
     one member whose globs cover every glob of the task's `area`; none or both -> the task is refused at load.
  R2 STEAL.  Board.assign gives a member its own oldest open task; a task homed on the other member only when the
     member has NO open task of its own (a "steal", logged on the `assign` event as stolen=true).
  R3 AREA GUARD (before the gate, both phases). Every changed path must lie in the task's `area` or its `shared`
     list, and no changed path may lie in a member's area other than the task's home unless it is `shared`.
     Otherwise the gate record is a scope FAIL: the candidate is not published and the refusal feeds the next pass.
  R4 BACK-PRESSURE.  A member with a live candidate waiting is given NO live-needing task. "Waiting" is read from
     two places, either suffices: the loop's own lane_wait state, and the RUNNER QUEUE (ralph_c_runner.pending: a
     pending candidate published by a builder id of this member), so a restarted loop with lost state still holds.
     The loop itself also does no build pass while its live candidate waits (ralph_a's lane wait; the design
     table: "the back-pressure rule above stops a builder while its live candidate waits").
  R5 TESTED PER LOOP.  Before every build pass of member M: every `build_end` in M's run ids (ralph_c.M.<n>) has a
     later `test_start` of that build by a different agent, and none is the builder testing itself
     (arena_eventlog.untested_builds / flagged_same_agent over M's records). Otherwise NotTested, no model call.
  R6 SUBAGENTS.  The build prompt allows at most $RALPH_C_MAX_SUBAGENTS (default 4) read/search subagents per pass
     that never edit, build, test or touch the bridge. PROMPT-LEVEL ONLY: nothing here can count a model's
     subagents; the env var is passed to the model command so a wrapper that can enforce it may.
  SWITCH ADAPTER.  Every loop and runner honours <arena>/STOP.ralph_c (arena.py's stop file) as well as its own
     <ctl>/STOP, writes <arena>/status/ralph_c.<member>.json, and recomputes <arena>/status/ralph_c.json
     (state idle iff no member file reads busy) - the one file arena.py's is_idle reads.

    ralph_c_loop.py run      --member a1|a2 --root CLONE --tasks ID,ID,... [--ctl DIR] [--areas areas.json]
    ralph_c_loop.py runner   --lane steve|archmagi --clone CLONE [--max-steps N]
    ralph_c_loop.py board    [--tasks ...]                 print who holds what and what each member would get
    ralph_c_loop.py check-tested --member a1|a2

WIRED (ARENA_RALPHC_WIRE_ENTRYPOINT_AND_UNITS): "ralph_c_loop.py" is in arena_eventlog.ENTRYPOINTS; the rm-ralph-loop@ and
rm-runner@ unit templates are infrastructure/arena/systemd/*.service.tmpl, planned by arena_install.py units.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import shlex
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import ralph_a_loop as RA  # noqa: E402
from arena_gate import in_area  # noqa: E402

ARM = "ralph_c"
MEMBERS = ("a1", "a2")
RUNNER_LANES = ("steve", "archmagi")
C_DIR = HERE / "ralph_c"
DEFAULT_CTL = "/mnt/d/ClaudeWork/rimmandrake/ralph_c"
MAX_SUBAGENTS = 4

Refused = RA.Refused
NotTested = RA.NotTested


class AreaRefused(Refused):
    """An area map, a task's home, or a candidate's paths break R1/R3."""


# ------------------------------------------------------------------------------------------------ areas (R1, R3)
def load_areas(src) -> dict:
    """areas.json (path or dict) -> {member: [globs]}. Exactly MEMBERS, each non-empty, no glob of one covered by the
    other's (overlap would let both loops own a file)."""
    d = json.loads(Path(src).read_text()) if not isinstance(src, dict) else src
    if not isinstance(d, dict) or sorted(d) != sorted(MEMBERS):
        raise AreaRefused("areas must name exactly %s, got %r" % (MEMBERS, sorted(d) if isinstance(d, dict) else d))
    out = {}
    for m in MEMBERS:
        g = d[m]
        if not isinstance(g, list) or not g or not all(isinstance(x, str) and x.strip() for x in g):
            raise AreaRefused("areas[%s] must be a non-empty list of globs" % m)
        out[m] = [x.strip() for x in g]
    a, b = out[MEMBERS[0]], out[MEMBERS[1]]
    clash = [x for x in a if in_area(x, b)] + [x for x in b if in_area(x, a)]
    if clash:
        raise AreaRefused("areas overlap: %s" % ", ".join(sorted(set(clash))))
    return out


def home_of(task: dict, areas: dict) -> str:
    """The one member whose globs cover every glob of the task's area (R1)."""
    area = task.get("area")
    area = [area] if isinstance(area, str) else area
    if not area or not all(isinstance(x, str) and x for x in area):
        raise AreaRefused("task %s has no area" % task.get("id"))
    homes = [m for m in MEMBERS if all(in_area(x, areas[m]) for x in area)]
    if len(homes) != 1:
        raise AreaRefused("task %s: area %s is covered by %s member(s) %s; it needs exactly one home"
                          % (task.get("id"), area, len(homes), homes))
    return homes[0]


def owner_of(path: str, areas: dict):
    return next((m for m in MEMBERS if in_area(path, areas[m])), None)


def area_violations(task: dict, files: list, areas: dict) -> list:
    """R3 -> ["path: why", ...] (empty = clean)."""
    area = task.get("area")
    area = [area] if isinstance(area, str) else list(area or [])
    shared = list(task.get("shared") or [])
    home = home_of(task, areas)
    bad = []
    for f in files:
        if in_area(f, shared):
            continue
        if not in_area(f, area):
            bad.append("%s: outside the task's area %s" % (f, area))
            continue
        o = owner_of(f, areas)
        if o is not None and o != home:
            bad.append("%s: in %s's area, the task's home is %s" % (f, o, home))
    return bad


# ------------------------------------------------------------------------------------------------ the board (R2, R4)
class Board:
    """Shared assignment for both loops: <dir>/board.json under flock. State only (holder, outcome); the task specs
    are the frozen tasks both loops were started with, in one order that the board pins on first use."""

    def __init__(self, path, tasks, areas, runner_pending=None):
        self.path = Path(path)
        self.areas = areas
        self.tasks = {t["id"]: t for t in tasks}
        self.order = [t["id"] for t in tasks]
        if len(self.tasks) != len(self.order):
            raise Refused("duplicate task ids")
        self.home = {t["id"]: home_of(t, areas) for t in tasks}          # R1 refuses a homeless task here
        self.runner_pending = runner_pending or (lambda: [])

    @contextlib.contextmanager
    def _locked(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path.with_suffix(".lock"), "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                st = json.loads(self.path.read_text()) if self.path.is_file() else \
                    {"order": self.order, "holder": {}, "done": {}}
                if st["order"] != self.order:
                    raise Refused("board %s pins task order %s; this loop was started with %s"
                                  % (self.path, st["order"], self.order))
                yield st
                tmp = self.path.with_suffix(".tmp")
                tmp.write_text(json.dumps(st, indent=1, sort_keys=True))
                os.replace(tmp, self.path)
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)

    def task(self, tid):
        return self.tasks[tid]

    def snapshot(self):
        with self._locked() as st:
            return json.loads(json.dumps(st))

    def waiting_in_runner(self, member) -> list:
        """R4's queue half: pending runner candidates published by a builder id of `member`."""
        pre = "%s-%s-" % (ARM, member)
        return [c for c in self.runner_pending() if str(c.get("builder", "")).startswith(pre)]

    def assign(self, member, lane_wait=False):
        """-> (task, why). A task the member already holds comes back first (a restarted loop resumes it); else its
        own oldest open task, else (own list empty) the oldest open task of the other member, a steal. A live-needing
        task is skipped while the member has a live candidate waiting (R4). (None, why) when nothing may be given."""
        if member not in MEMBERS:
            raise Refused("member %r is not one of %s" % (member, MEMBERS))
        waiting = bool(lane_wait) or bool(self.waiting_in_runner(member))
        with self._locked() as st:
            held = [t for t in self.order if st["holder"].get(t) == member and t not in st["done"]]
            if held:
                t = self.tasks[held[0]]
                if waiting and t.get("live", "none") != "none" and not lane_wait:
                    # its own candidate is the one waiting: resuming it would replace that candidate, so wait
                    return None, "held live task %s has a candidate waiting in the runner queue" % t["id"]
                return t, "resume"
            free = [t for t in self.order if t not in st["holder"] and t not in st["done"]]
            own = [t for t in free if self.home[t] == member]
            pool, stolen = (own, False) if own else ([t for t in free if self.home[t] != member], True)
            skipped = []
            for tid in pool:
                t = self.tasks[tid]
                if waiting and t.get("live", "none") != "none":
                    skipped.append(tid)
                    continue
                st["holder"][tid] = member
                return dict(t, _stolen=stolen, _home=self.home[tid]), "steal" if stolen else "own"
            if skipped:
                return None, "back-pressure: live candidate waiting; live task(s) %s not given" % ", ".join(skipped)
            return None, "no open task for %s" % member

    def finish(self, member, tid, outcome):
        with self._locked() as st:
            if st["holder"].get(tid) != member:
                raise Refused("%s does not hold %s (holder %r)" % (member, tid, st["holder"].get(tid)))
            st["done"].setdefault(tid, outcome)            # idempotent: crash recovery may finish twice


# ------------------------------------------------------------------------------------------------ switch adapter
def arena_root(root=None) -> Path:
    if root:
        return Path(root)
    import arena_tasks as A
    return A.arena_root()


def write_status(aroot: Path, member: str, state: str, what: str):
    """<arena>/status/ralph_c.<member>.json, then the arm file arena.py reads: idle iff no member reads busy."""
    d = Path(aroot) / "status"
    d.mkdir(parents=True, exist_ok=True)
    with open(d / (".%s.lock" % ARM), "w") as lk:      # one writer at a time: no stale "idle" aggregate overwrites
        fcntl.flock(lk, fcntl.LOCK_EX)                 # a member's fresh "busy"
        try:
            _atomic(d / ("%s.%s.json" % (ARM, member)), {"state": state, "what": what, "ts": L.now_ts()})
            busy = []
            for f in sorted(d.glob("%s.*.json" % ARM)):
                try:
                    if json.loads(f.read_text()).get("state") != "idle":
                        busy.append(f.name)
                except (OSError, ValueError, AttributeError):
                    busy.append(f.name)                # unreadable is not idle (arena.py's rule)
            _atomic(d / ("%s.json" % ARM), {"state": "busy" if busy else "idle", "busy": busy, "ts": L.now_ts()})
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


def _atomic(f: Path, obj):
    tmp = f.with_name(f.name + ".%d.tmp" % os.getpid())
    tmp.write_text(json.dumps(obj, sort_keys=True))
    os.replace(tmp, f)


def arm_stopped(aroot: Path) -> bool:
    return (Path(aroot) / ("STOP.%s" % ARM)).exists()


# ------------------------------------------------------------------------------------------------ the tested check
def require_tested(recs, member):
    """R5 over this member's records only (run ids ralph_c.<member>.<n>)."""
    pre = "%s.%s." % (ARM, member)
    mine = [r for r in recs if r.get("arm") == ARM and str(r.get("run_id", "")).startswith(pre)]
    bad = L.untested_builds(mine)
    if bad:
        b = bad[0]
        raise NotTested("refused (%s): build %s of %s (builder %s) has no test_start from a different agent; the "
                        "tester pass must start before this loop's next build pass" % (
                            member, (b.get("detail") or {}).get("build_id") or b.get("sha"), b.get("task"),
                            (b.get("detail") or {}).get("builder")))
    same = L.flagged_same_agent(mine)
    if same:
        raise NotTested("refused (%s): test_start by the builder itself (%s)"
                        % (member, (same[0].get("detail") or {}).get("tester")))


def max_subagents() -> int:
    try:
        return max(0, int(os.environ.get("RALPH_C_MAX_SUBAGENTS", MAX_SUBAGENTS)))
    except ValueError:
        return 0                                       # garbled -> none, never unbounded


# ------------------------------------------------------------------------------------------------ default gate/precheck
def cmd_gate_c(task, base, head, phase, *, root, log):
    """ralph_a's default gate with --arm ralph_c: the gate reads THIS arm's records (build_end/test_start of ralph_c);
    under --arm ralph_a it would find none and refuse every candidate."""
    cmd = os.environ.get("RALPH_C_GATE_CMD")
    argv = shlex.split(cmd) if cmd else [sys.executable, str(HERE / "arena_gate.py")]
    argv += ["--task", task["id"], "--base", base, "--head", head, "--arm", ARM, "--repo", str(root)]
    r = subprocess.run(argv, cwd=str(RA.HARNESS_REPO), capture_output=True, text=True, timeout=3 * 3600)
    Path(log).write_text(r.stdout + "\n--- stderr\n" + r.stderr)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {"verdict": "invalid", "steps": {}, "why": "gate printed no JSON record (rc %s)" % r.returncode}


def precheck_c(root, log):
    r = subprocess.run([sys.executable, "src/RimMandrake/Utils/run_selftests.py", "--quick"], cwd=str(root),
                       capture_output=True, text=True, timeout=3600, env=dict(os.environ, RM_ARM=ARM))
    Path(log).write_text(r.stdout + r.stderr)
    return r.returncode == 0


# ------------------------------------------------------------------------------------------------ the builder loop
class LoopC(RA.Loop):
    def __init__(self, member, root, ctl, board, *, arena=None, model, **kw):
        if member not in MEMBERS:
            raise Refused("member %r is not one of %s" % (member, MEMBERS))
        self.member, self.board = member, board
        self.aroot = arena_root(arena)
        inner = model
        kw.setdefault("new_id", lambda role: "%s-%s-%s-%s" % (ARM, member, role, uuid.uuid4().hex[:12]))
        if kw.get("gate") is None:
            kw["gate"] = lambda t, b, h, ph, log: cmd_gate_c(t, b, h, ph, root=self.root, log=log)
        if kw.get("precheck") is None:
            kw["precheck"] = lambda log: precheck_c(self.root, log)
        super().__init__(root, ctl, [], model=lambda role, prompt, **k: inner(
            role, self.build_prompt(prompt) if role == "build" else prompt, **k), **kw)
        inner_gate = self.gate
        self.gate = lambda t, b, h, ph, log: self.guarded_gate(inner_gate, t, b, h, ph, log)

    # ---- identity and records
    def emit(self, event, task, **kw):
        return self.writer.emit(ARM, event, lane="build", run_id="%s.%s.%s" % (ARM, self.member, self.state["n"]),
                                task=task["id"], **kw)

    def status(self, what):
        super().status(what)
        busy = "running" in what
        write_status(self.aroot, self.member, "busy" if busy else "idle", what)
        return what

    def task(self):
        cur = self.state.get("current")
        return self.board.task(cur) if cur else None

    # ---- R6 + the ralph_c section of the build prompt
    def build_prompt(self, prompt):
        head = (RA.ARM_DIR / "PROMPT.md").read_text()
        if prompt.startswith(head):
            prompt = head.replace("ralph_a", ARM) + prompt[len(head):]
        t = self.task() or {}
        home = self.board.home.get(t.get("id"))
        sec = (C_DIR / "PROMPT_C.md").read_text().format(
            member=self.member, own=", ".join(self.board.areas[self.member]), home=home,
            stolen="yes, a STEAL from %s" % home if home and home != self.member else "no",
            area=", ".join(t.get("area") if isinstance(t.get("area"), list) else [str(t.get("area"))]),
            shared=", ".join(t.get("shared") or []) or "(none)", max_sub=max_subagents())
        return prompt + "\n" + sec

    # ---- R3 in front of the gate
    def guarded_gate(self, inner, task, base, head, phase, log):
        # --no-renames: a rename lists BOTH paths, so moving a file out of another member's area is seen
        files = self.git("diff", "--no-renames", "--name-only", base, head).splitlines() if head != base else []
        bad = area_violations(task, files, self.board.areas)
        wip = self.git("rev-parse", "--verify", "-q", RA.WIP, check=False)
        if wip != head:                                 # _final publishes wip: guard exactly what gets published
            bad.append("guarded head %s is not %s (%s): the candidate must be committed on %s"
                       % (head[:12], RA.WIP, (wip or "missing")[:12], RA.WIP))
        self._guard_why = "; ".join(bad)[:600] or None
        if bad:
            Path(log).write_text("ralph_c area guard refused:\n" + "\n".join(bad) + "\n")
            return {"verdict": "fail", "why": "area guard", "steps": {
                "scope": {"status": "FAIL", "why": "ralph_c area guard: " + "; ".join(bad)[:600]}}}
        rec = inner(task, base, head, phase, log)
        if self.git("rev-parse", "--verify", "-q", RA.WIP, check=False) != head:
            self._guard_why = "%s moved during the gate: refusing to publish an unguarded commit" % RA.WIP
            return {"verdict": "fail", "why": "area guard", "steps": {
                "scope": {"status": "FAIL", "why": "ralph_c area guard: " + self._guard_why}}}
        return rec

    def _failed(self, task, base, head, why, n):
        """The area guard's reasons ride in the failure note the next build pass reads (the gate's own `why` names
        only the failed step)."""
        g, self._guard_why = getattr(self, "_guard_why", None), None
        if g:
            why = "%s\nralph_c area guard refused: %s\n(remove these paths from the candidate; it is diffed against "\
                  "main, so an unpublished try's files stay in it until deleted)" % (why, g)
        return super()._failed(task, base, head, why, n)

    # ---- R5 then ralph_a's build pass
    def build_pass(self, task):
        require_tested(self.writer.records(), self.member)
        return super().build_pass(task)

    # ---- one step: STOP, then assignment from the board (R2, R4), then ralph_a's step
    def step(self):
        if (self.ctl / "STOP").exists() or arm_stopped(self.aroot):
            return self.status("STOP")
        if self.state.get("current") and self.state["task_i"] != 0:
            self._release_current("published-or-parked (recovered after a crash)")
        if self.task() is None:
            if self.state.get("lane_wait") or self.state.get("pending"):
                raise Refused("state holds a candidate but no current task: refusing to assign over it")
            t, why = self.board.assign(self.member, lane_wait=False)
            if t is None:
                return self.status("idle: " + why)
            self.state["current"] = t["id"]
            self._save()
            if why != "resume":
                self.emit("assign", t, detail={"member": self.member, "home": t.get("_home"),
                                               "stolen": bool(t.get("_stolen")), "live": t.get("live", "none")})
        before = self.state["task_i"]
        r = super().step()
        if self.state["task_i"] != before:                       # published or parked: the task leaves this loop
            self._release_current("published" if r.startswith("published") else "parked")
        return r

    def _release_current(self, outcome):
        """task_i != 0 means ralph_a's step finished the task (it only ever counts up on publish/park, and ralph_c
        resets it to 0 here). Board first, loop state second; finish() is idempotent, so a crash between the two
        is repaired on the next step instead of re-running a finished task."""
        self.board.finish(self.member, self.state["current"], outcome)
        self.state.pop("current")
        self.state["task_i"] = 0
        self._save()

    def run(self, max_steps=0):
        """ralph_a's run, plus: one process per MEMBER (a lock beside the board, not in the ctl dir, so a second a1
        started with another --ctl is refused), "idle: no open task" ends the loop, any other idle (back-pressure, a
        held live task waiting) sleeps like "waiting" instead of spinning."""
        self.board.path.parent.mkdir(parents=True, exist_ok=True)
        mlock = open(self.board.path.parent / ("loop.%s.lock" % self.member), "w")
        try:
            fcntl.flock(mlock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            mlock.close()
            raise Refused("another ralph_c %s loop is running (%s)" % (self.member, mlock.name))
        lockf = open(self.ctl / "loop.lock", "w")
        try:
            fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lockf.close()
            mlock.close()
            raise Refused("another loop holds %s" % (self.ctl / "loop.lock"))
        out, i = [], 0
        try:
            while not max_steps or i < max_steps:
                r = self.step()
                out = (out + [r])[-200:]
                i += 1
                if r.startswith(("STOP", "done", "runway", "red start", "sync failed", "idle: no open task")):
                    break
                if r.startswith(("waiting", "idle")):
                    self.sleep(self.poll_s)
        finally:
            self.release()
            write_status(self.aroot, self.member, "idle", "loop exited")
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
            fcntl.flock(mlock, fcntl.LOCK_UN)
            mlock.close()
        return out


# ------------------------------------------------------------------------------------------------ both runners
def runner_loop(lane, clone, *, p=None, driver=None, aroot=None, poll_s=60.0, sleep=time.sleep, max_steps=0,
                run_one=None):
    """One live runner: ralph_c_runner.run_one on `lane` until STOP; the queue is shared, oldest first, claimed."""
    import ralph_c_runner as RC
    if lane not in RUNNER_LANES:
        raise Refused("lane %r is not one of %s" % (lane, RUNNER_LANES))
    p = p or RC.rpaths()
    aroot = arena_root(aroot)
    member = "runner-%s" % lane
    one = run_one or (lambda: RC.run_one(p, lane, driver or RC.RunnerDriver(), clone,
                                         runner_id="%s_runner@%s" % (ARM, lane)))
    out, i = [], 0
    try:
        while not max_steps or i < max_steps:
            if arm_stopped(aroot):
                out.append("STOP")
                break
            write_status(aroot, member, "busy", "run_one")
            r = one()
            write_status(aroot, member, "idle", "between runs")
            out.append(r)
            i += 1
            if r is None:
                sleep(poll_s)
    finally:
        write_status(aroot, member, "idle", "runner exited")
    return out


# ------------------------------------------------------------------------------------------------ CLI
class SignedWriterC(RA.SignedWriter):
    def records(self):
        return self.w.accepted(ARM)


class CmdModelC(RA.CmdModel):
    """ralph_a's CmdModel with the child tagged RM_ARM=ralph_c (the pre-push hook keys on it) and told its member
    and subagent bound."""

    def __init__(self, cmd, member):
        super().__init__(cmd)
        self.member = member

    def __call__(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        if role == "test":     # the tester pass: ralph_a's sandboxed, scrubbed-env path (bwrap, own home/tmp, pidfile)
            return super().__call__(role, prompt, cwd=cwd, agent_id=agent_id, run_id=run_id, timeout_s=timeout_s,
                                    log=log, sandbox=sandbox)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ARENA_", "RALPH_A_CTL", "RALPH_C_CTL"))}
        env.update(RALPH_A_ROLE=role, RALPH_A_AGENT_ID=agent_id, RM_ARM=ARM, RALPH_C_MEMBER=self.member,
                   RALPH_C_MAX_SUBAGENTS=str(max_subagents()))
        with open(log, "w") as out:
            pr = subprocess.Popen(self.argv, cwd=str(cwd), env=env, stdin=subprocess.PIPE, stdout=out,
                                  stderr=subprocess.STDOUT, text=True, start_new_session=True)
            try:
                pr.communicate(prompt, timeout=timeout_s)
                rc = pr.returncode
            except subprocess.TimeoutExpired:
                os.killpg(pr.pid, signal.SIGKILL)
                pr.wait()
                rc = -9
        raw = Path(log).read_text(errors="replace")
        try:
            j = json.loads(raw)
            text = j.get("result") if isinstance(j, dict) and isinstance(j.get("result"), str) else raw
        except ValueError:
            text = raw
        return {"rc": rc, "text": text}


def make_board(task_ids, areas_path, p=None):
    import arena_tasks as A
    import ralph_c_runner as RC
    tp = A.paths()
    tasks = [A.load_frozen(t, tp) for t in task_ids if t]
    rp = RC.rpaths()
    return Board(rp["rc"] / "board.json", tasks, load_areas(areas_path), runner_pending=lambda: RC.pending(rp))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("run", "runner", "board", "check-tested"))
    ap.add_argument("--member", choices=MEMBERS)
    ap.add_argument("--lane", choices=RUNNER_LANES)
    ap.add_argument("--root", help="this member's arm clone")
    ap.add_argument("--clone", help="the runner's clone")
    ap.add_argument("--ctl", default=None, help="control dir (default %s/<member>)" % DEFAULT_CTL)
    ap.add_argument("--tasks", default=os.environ.get("RALPH_C_TASKS", ""))
    ap.add_argument("--areas", default=os.environ.get("RALPH_C_AREAS", str(Path(DEFAULT_CTL) / "areas.json")))
    ap.add_argument("--model-cmd", default=os.environ.get("RALPH_C_MODEL_CMD"))
    ap.add_argument("--max-steps", type=int, default=0)
    a = ap.parse_args(argv)
    if os.environ.get("RM_ARM"):
        print("refused: the loop is harness code; run it without RM_ARM")
        return 2
    if a.action == "runner":
        if not (a.lane and a.clone):
            ap.error("runner needs --lane and --clone")
        for r in runner_loop(a.lane, a.clone, max_steps=a.max_steps):
            print(json.dumps(r, sort_keys=True, default=str))
        return 0
    ids = [t for t in a.tasks.split(",") if t]
    if a.action == "board":
        b = make_board(ids, a.areas)
        print(json.dumps({"state": b.snapshot(), "home": b.home,
                          "waiting": {m: [c["item"] for c in b.waiting_in_runner(m)] for m in MEMBERS}}, indent=1))
        return 0
    if not a.member:
        ap.error("%s needs --member" % a.action)
    import arena_tasks as A
    p = A.paths()
    with L.harness_pass(p) as cap:
        w = SignedWriterC(p, cap)
        if a.action == "check-tested":
            require_tested(w.records(), a.member)
            print("%s: every build has a test_start from a different agent" % a.member)
            return 0
        root = Path(a.root or "").resolve()
        if not a.root or Path.cwd().resolve().is_relative_to(root):
            print("refused: --root is required and the loop must run from outside the arm clone")
            return 2
        lp = LoopC(a.member, root, a.ctl or str(Path(DEFAULT_CTL) / a.member), make_board(ids, a.areas),
                   model=CmdModelC(a.model_cmd, a.member), writer=w, lane=RA.RalphCLane(),
                   timeout_s=float(os.environ.get("RALPH_C_PASS_TIMEOUT_S", RA.PASS_TIMEOUT_S)))
        for r in lp.run(a.max_steps):
            print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
