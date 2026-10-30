#!/usr/bin/env python3
r"""ralph_a_loop.py - the `ralph_a` arm's loop driver: one build pass, then AT ONCE one fresh blind tester pass.

ARENA_RALPHA_BUILD_TESTER_PASS_EACH_BUILD. Design: architecture_switch_harness_2026-10-29.md step 8 and §1.8;
ralph_loop_design_2026-10-29.md §1.2 (the loop: the loop, not the agent, decides what is published) and §8 item 4
(a planted failing check and a killed pass both recover); testpilot_merged_2026-10-29.md §2.3 (owner, binding: a
different agent tests what was built, before the builder's next build pass). The arm's text files are beside this
one in `ralph_a/`: loop.sh (the supervisor's entry), PROMPT.md, POLICY.md, TESTER.md.

ONE STEP OF THE LOOP (Loop.step), in this order:
  0  STOP file -> stop. Runway below $RALPH_A_RUNWAY_MIN (default 0.15 x the time to reset) or UNMEASURED -> refuse
     to start any model pass (checked before EVERY build and tester pass; fail closed).
  1  a live candidate waiting on its minimal-list lane -> WAIT (no build, no tester pass) until the lane records a
     verdict for that exact sha: pass -> final gate -> publish; fail -> the failure feeds the next build pass.
  2  a gate-passed build with no tester verdict (state.pending: e.g. the loop was killed between build_end and the
     tester) -> the tester pass runs FIRST.
  3  otherwise a BUILD pass. HARD CHECK (require_tested, code not prompt): every build_end in the signed event log
     must have a later test_start of that build by a DIFFERENT agent id (arena_eventlog.untested_builds, the rule
     the gate's step 9 and the report use), and no test_start may be the builder testing itself
     (flagged_same_agent); otherwise NotTested is raised and no model is invoked.
     The build pass: run_selftests --quick pre-check (a red start is allowed only when last_failure.md explains it,
     else STOP), fresh model invocation (role build, agent id minted by THIS loop for this invocation), bridge
     released (`bridge release --mine`) whatever happened, then the BUILD-PHASE gate: every arena_gate step PASS or
     NA except `test_record` (it cannot pass before the tester) and `live` (it cannot pass before the lane), with
     scope and placeholders PASS. Pass -> `build_end` (builder, build_id) and IMMEDIATELY the tester pass. Fail or a
     non-zero / killed model -> unpublished, last_failure.md (outside git) feeds the next pass; 3 tries -> parked on
     ralph/failed/<task>, wip reset to main.
  The TESTER pass: a new agent id (refused if it equals the builder's), `test_start` written BEFORE the model runs,
     then a fresh invocation whose prompt is TESTER.md + the frozen spec + the test plan + the diff and NOTHING
     else (no builder transcript, no last_failure, no builder prompt); its cwd is a history-less export of the
     candidate tree (git archive: no commit messages, no reflog) outside the arm clone. It must end with
     `VERDICT: PASS` or `VERDICT: FAIL`; no verdict is retried once with another fresh tester, then counted as a
     fail. `test_end` carries the verdict. FAIL -> the tester's findings feed the next build pass (last_verdict.md
     + last_failure.md); PASS -> live task: published to the lane and the loop waits; else the FINAL gate (the
     whole arena_gate verdict must be `pass`, step 9 included) -> publish (ff-merge wip into main, publish cmd).

INJECTABLE (the selftest runs all of it offline with fakes): `model` (or --model-cmd / $RALPH_A_MODEL_CMD: argv,
prompt on stdin, env RALPH_A_ROLE / RALPH_A_AGENT_ID / RM_ARM=ralph_a, cwd = the arm clone or the tester export),
`gate` ($RALPH_A_GATE_CMD, default arena_gate.py run from the HARNESS checkout), `writer` (default: the signed
arena_eventlog.HarnessWriter; OWED: "ralph_a_loop.py" must be added to arena_eventlog.ENTRYPOINTS before the real
writer can sign), `lane` (default: ralph_c_runner's candidate queue, minimal profiles only), `runway`, `precheck`,
`release`, `publish_cmd`, `sync`, `new_id`, `tester_workdir`. No account, host or key is named here: the runway
reading resolves the account from the environment (role_launch.resolve_account / ops_watch status.json).

The loop process itself must NOT run with its cwd inside the arm clone and must not carry $RM_ARM (HarnessWriter
refuses both); every git call is `git -C <root>`, and only model subprocesses get cwd = the clone.
Control files (outside git): <ctl>/state.json, last_failure.md, last_verdict.md, status, STOP, loop.lock, log/.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tarfile
import io
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402

ARM = "ralph_a"
ARM_DIR = HERE / "ralph_a"
HARNESS_REPO = HERE.parents[3]
WIP, MAIN = "ralph/wip", "main"
MAX_TRIES = 3
TESTER_TRIES = 2
PASS_TIMEOUT_S = 90 * 60
DEFAULT_CTL = "/mnt/d/ClaudeWork/rimmandrake/ralph_a"
SPEC_FIELDS = ("id", "kind", "size", "area", "prompt", "criteria", "proof", "live", "base_sha")
VERDICT_RE = re.compile(r"^\s*VERDICT:\s*(PASS|FAIL)\b", re.I | re.M)
BUILD_EXEMPT = ("test_record", "live")          # steps that cannot pass before the tester / the lane
MUST_PASS_BUILD = ("scope", "placeholders")


class Refused(Exception):
    """A hard refusal by the loop's own code."""


class NotTested(Refused):
    """A build pass was asked for while an earlier build has no test_start from a different agent."""


# ------------------------------------------------------------------------------------------------ event writers
class ListWriter:
    """In-memory writer (selftests, --dry-run). Same emit signature and record shape as HarnessWriter."""

    def __init__(self):
        self.recs = []

    def emit(self, arm, event, *, lane, run_id, ts=None, **fields):
        rec = {"ts": ts or L.now_ts(), "arm": arm, "lane": lane, "run_id": run_id, "event": event}
        rec.update({k: v for k, v in fields.items() if v is not None})
        L.validate_record(rec)
        self.recs.append(rec)
        return rec

    def records(self):
        return list(self.recs)


class SignedWriter:
    """The signed arena log. Needs an open arena_eventlog.harness_pass in this process; the real loop can open one
    only once ralph_a_loop.py is in arena_eventlog.ENTRYPOINTS (owed)."""

    def __init__(self, p=None, cap=None):
        self.w = L.HarnessWriter(p, cap=cap)

    def emit(self, arm, event, **kw):
        return self.w.emit(arm, event, **kw)

    def records(self):
        return self.w.accepted(ARM)


# ------------------------------------------------------------------------------------------------ the hard check
def require_tested(recs):
    """Raise NotTested unless every build_end has a later test_start of that build by a different agent, and no
    test_start is its builder testing itself. Reads the event log, never loop memory."""
    mine = [r for r in recs if r.get("arm") == ARM]
    bad = L.untested_builds(mine)
    if bad:
        b = bad[0]
        raise NotTested("refused: build %s of %s (builder %s) has no test_start from a different agent; the tester "
                        "pass must start before the next build pass" % (
                            (b.get("detail") or {}).get("build_id") or b.get("sha"), b.get("task"),
                            (b.get("detail") or {}).get("builder")))
    same = L.flagged_same_agent(mine)
    if same:
        raise NotTested("refused: test_start by the builder itself (%s)" % (same[0].get("detail") or {}).get("tester"))


def build_gate_ok(rec):
    """The build-phase gate: every step PASS/NA except BUILD_EXEMPT, MUST_PASS_BUILD PASS. -> (ok, why)."""
    if not isinstance(rec, dict) or not isinstance(rec.get("steps"), dict):
        return False, "no gate record"
    st = {k: (v or {}).get("status") if isinstance(v, dict) else v for k, v in rec["steps"].items()}
    bad = {k: v for k, v in st.items() if k not in BUILD_EXEMPT and v not in ("PASS", "NA")}
    if bad:
        return False, "gate steps not passed: %s" % ", ".join("%s=%s" % kv for kv in sorted(bad.items()))
    miss = [k for k in MUST_PASS_BUILD if st.get(k) != "PASS"]
    if miss:
        return False, "gate steps that must PASS did not: %s" % ", ".join(miss)
    return True, "build-phase gate passed (test_record/live wait for the tester and the lane)"


def final_gate_ok(rec):
    if isinstance(rec, dict) and rec.get("verdict") == "pass":
        return True, "gate pass"
    return False, "final gate verdict %r" % (rec or {}).get("verdict")


def parse_verdict(text):
    m = VERDICT_RE.findall(text or "")
    return m[-1].lower() if m else None


def public_spec(task):
    return {k: task[k] for k in SPEC_FIELDS if k in task}


def test_plan(task):
    return ("Acceptance criteria:\n%s\n\nProof command (run it yourself):\n%s\n\nAlso run "
            "`python3 src/RimMandrake/Utils/run_selftests.py --only <selftest>` for every selftest the diff adds or "
            "changes, then try to break the change: inputs the criteria name but the tests do not, error paths, "
            "boundary values, anything the diff claims without a test.\n" % (task.get("criteria"), task.get("proof")))


# ------------------------------------------------------------------------------------------------ default hooks
class CmdModel:
    """argv from --model-cmd / $RALPH_A_MODEL_CMD; prompt on stdin; killed (process group) at the timeout."""

    def __init__(self, cmd):
        if not cmd:
            raise Refused("no model command: pass --model-cmd or set RALPH_A_MODEL_CMD")
        self.argv = shlex.split(cmd)

    def __call__(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("ARENA_", "RALPH_A_CTL"))}
        env.update(RALPH_A_ROLE=role, RALPH_A_AGENT_ID=agent_id, RM_ARM=ARM)
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


def cmd_gate(task, base, head, phase, *, root, log):
    """Default gate: arena_gate.py (or $RALPH_A_GATE_CMD) run from the HARNESS checkout, never the arm clone."""
    cmd = os.environ.get("RALPH_A_GATE_CMD")
    argv = shlex.split(cmd) if cmd else [sys.executable, str(HERE / "arena_gate.py")]
    argv += ["--task", task["id"], "--base", base, "--head", head, "--arm", ARM, "--repo", str(root)]
    r = subprocess.run(argv, cwd=str(HARNESS_REPO), capture_output=True, text=True, timeout=3 * 3600)
    Path(log).write_text(r.stdout + "\n--- stderr\n" + r.stderr)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {"verdict": "invalid", "steps": {}, "why": "gate printed no JSON record (rc %s)" % r.returncode}


def default_runway():
    """-> {"state": "MEASURED", "runway": float, ...} or {"state": "UNMEASURED", "why"} (role_launch's reading)."""
    sys.path.insert(0, str(HERE.parents[1] / "rimflow"))
    try:
        import role_launch as RL
        import ops_watch
        path = os.environ.get("RALPH_A_OPS_STATUS") or str(ops_watch.ops_dir() / "status.json")
        return RL.ops_reading(RL.read_ops(path), RL.resolve_account(), time.time())
    except Exception as e:  # noqa: BLE001 - an unreadable meter is UNMEASURED, never a pass
        return {"state": "UNMEASURED", "why": "runway reading failed: %s: %s" % (type(e).__name__, e)}


def runway_min():
    try:
        return float(os.environ.get("RALPH_A_RUNWAY_MIN", "0.15"))
    except ValueError:
        return float("inf")                     # a garbled threshold refuses, never waves through


def default_precheck(root, log):
    r = subprocess.run([sys.executable, "src/RimMandrake/Utils/run_selftests.py", "--quick"], cwd=str(root),
                       capture_output=True, text=True, timeout=3600, env=dict(os.environ, RM_ARM=ARM))
    Path(log).write_text(r.stdout + r.stderr)
    return r.returncode == 0


def default_release(root):
    subprocess.run([sys.executable, "src/RimMandrake/rimflow/cli.py", "bridge", "release", "--mine"],
                   cwd=str(root), capture_output=True, timeout=120)


class RalphCLane:
    """Default minimal-list lane: ralph_c_runner's queue (oldest first, one runner per lane, arena_lane rules)."""

    def __init__(self):
        import arena_tasks as A
        import ralph_c_runner as R
        self.A, self.R, self.p = A, R, R.rpaths()

    def publish(self, task, sha, builder, files):
        mods = sorted({m for m in (self.A._mod_of(f) for f in files) if m})
        self.R.publish(self.p, task["id"], sha, builder, mods, any(f.endswith(".cs") for f in files),
                       task["live"], task.get("tier"), shlex.split(task["proof"]))

    def result(self, task, sha):
        try:
            return self.R.lane_record(self.p, task["id"], sha)
        except (LookupError, self.R.StaleResult):
            return None


# ------------------------------------------------------------------------------------------------ the loop
class Loop:
    def __init__(self, root, ctl, tasks, *, model, gate=None, writer=None, lane=None, runway=None, precheck=None,
                 release=None, publish_cmd="./publish", sync=None, new_id=None, tester_workdir=None,
                 timeout_s=PASS_TIMEOUT_S, poll_s=60.0, sleep=time.sleep):
        self.root, self.ctl = Path(root), Path(ctl)
        self.tasks = list(tasks)
        self.model, self.writer = model, writer
        self.gate = gate or (lambda t, b, h, ph, log: cmd_gate(t, b, h, ph, root=self.root, log=log))
        self.lane = lane
        self.runway = runway or default_runway
        self.precheck = precheck or (lambda log: default_precheck(self.root, log))
        self.release = release or (lambda: default_release(self.root))
        self.publish_cmd, self.sync = publish_cmd, sync
        self.new_id = new_id or (lambda role: "ralph_a-%s-%s" % (role, uuid.uuid4().hex[:12]))
        self.tester_workdir = tester_workdir or self._export_tree
        self.timeout_s, self.poll_s, self.sleep = timeout_s, poll_s, sleep
        self.log = self.ctl / "log"
        self.log.mkdir(parents=True, exist_ok=True)
        self.state = self._load()

    # ---- control files
    def _load(self):
        f = self.ctl / "state.json"
        if f.is_file():
            return json.loads(f.read_text())
        return {"task_i": 0, "pending": None, "lane_wait": None, "tries": {}, "n": 0}

    def _save(self):
        f = self.ctl / "state.json"
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=1, sort_keys=True))
        os.replace(tmp, f)

    def status(self, what):
        (self.ctl / "status").write_text("%s pass=%s %s\n" % (L.now_ts(), self.state["n"], what))
        return what

    def emit(self, event, task, **kw):
        return self.writer.emit(ARM, event, lane="build", run_id="ralph_a.%s" % self.state["n"],
                                task=task["id"], **kw)

    def git(self, *a, check=True):
        r = subprocess.run(["git", "-C", str(self.root)] + list(a), capture_output=True, text=True)
        if check and r.returncode != 0:
            raise Refused("git %s failed: %s" % (" ".join(a), r.stderr.strip()[:300]))
        return r.stdout.strip()

    def task(self):
        i = self.state["task_i"]
        return self.tasks[i] if i < len(self.tasks) else None

    def _fail_note(self, task, text):
        (self.ctl / "last_failure.md").write_text(text)

    def _clear_notes(self):
        for n in ("last_failure.md", "last_verdict.md"):
            (self.ctl / n).unlink(missing_ok=True)

    def _note(self, name):
        f = self.ctl / name
        return f.read_text() if f.is_file() else ""

    # ---- runway
    def runway_refusal(self):
        r = self.runway()
        lim = runway_min()
        if not isinstance(r, dict) or r.get("state") != "MEASURED":
            return "runway UNMEASURED (%s): no pass started" % ((r or {}).get("why") if isinstance(r, dict) else r)
        v = r.get("runway")
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not v >= lim:
            return "runway %r below %s: no pass started" % (v, lim)
        return None

    # ---- one step
    def step(self):
        if (self.ctl / "STOP").exists():
            return self.status("STOP")
        task = self.task()
        if task is None:
            return self.status("done: no task left")
        if self.state.get("lane_wait"):
            return self._lane_step(task)
        why = self.runway_refusal()
        if why:
            return self.status("runway: " + why)
        if self.state.get("pending"):
            return self.tester_pass(task)
        return self.build_pass(task)

    def run(self, max_steps=0):
        lockf = open(self.ctl / "loop.lock", "w")
        try:
            fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lockf.close()
            raise Refused("another ralph_a loop holds %s" % (self.ctl / "loop.lock"))
        out, i = [], 0
        try:
            while not max_steps or i < max_steps:
                r = self.step()
                out.append(r)
                i += 1
                if r.startswith(("STOP", "done", "runway", "red start", "sync failed")):
                    break
                if r.startswith("waiting"):
                    self.sleep(self.poll_s)
        finally:
            self.release()
            fcntl.flock(lockf, fcntl.LOCK_UN)
            lockf.close()
        return out

    # ---- build
    def build_pass(self, task):
        require_tested(self.writer.records())                     # HARD CHECK: before anything else of the pass
        if self.sync is not None and not self.sync():
            return self.status("sync failed")
        if self.git("rev-parse", "--verify", "-q", WIP, check=False):
            self.git("switch", "-q", WIP)
        else:
            self.git("switch", "-q", "-c", WIP, MAIN)
        self.git("merge", "-q", "--ff-only", MAIN, check=False)
        base = self.git("merge-base", MAIN, "HEAD")      # main, not wip: an unpublished try stays in the diff
        before = self.git("rev-parse", "HEAD")
        n = self.state["n"]
        if not self.precheck(self.log / ("pre.%d" % n)) and not (self.ctl / "last_failure.md").exists():
            (self.ctl / "STOP").touch()
            return self.status("red start, unexplained: STOP written")
        builder = self.new_id("build")
        prompt = (ARM_DIR / "PROMPT.md").read_text() + "\n## TASK (frozen spec)\n" + \
            json.dumps(public_spec(task), indent=1, sort_keys=True) + "\n"
        for name, head_ in (("last_failure.md", "LAST FAILURE"), ("last_verdict.md", "TESTER VERDICT")):
            if self._note(name):
                prompt += "\n## %s\n%s\n" % (head_, self._note(name))
        self.status("build pass running (%s)" % builder)
        self.emit("pass_start", task, detail={"role": "build", "agent": builder})
        try:
            res = self.model("build", prompt, cwd=self.root, agent_id=builder, run_id=n, timeout_s=self.timeout_s,
                             log=self.log / ("build.%d.out" % n))
        finally:
            self.release()                                        # whatever the agent did, the bridge is free again
        rc = res.get("rc")
        head = self.git("rev-parse", "HEAD")
        self.state["n"] = n + 1
        ok, why = (False, "model exit %r (killed or failed)" % rc) if rc != 0 else (False, "empty candidate") \
            if head == before else (None, None)
        if ok is None:
            g = self.gate(task, base, head, "build", self.log / ("gate.build.%d" % n))
            ok, why = build_gate_ok(g)
        self.emit("pass_end", task, sha=head, verdict="pass" if ok else "fail",
                  detail={"role": "build", "agent": builder, "rc": rc, "why": why})
        if not ok:
            return self._failed(task, base, head, "build pass: " + why, n)
        bid = "%s.%s" % (task["id"], head[:12])
        self.emit("build_end", task, sha=head, detail={"builder": builder, "build_id": bid, "base": base})
        self.state["pending"] = {"build_id": bid, "base": base, "head": head, "builder": builder}
        self._save()
        return self.tester_pass(task)                             # AT ONCE: no other work between build and test

    def _failed(self, task, base, head, why, n):
        k = task["id"]
        t = self.state["tries"].get(k, 0) + 1
        self.state["tries"][k] = t
        self.state["pending"] = None
        self._fail_note(task, "item %s try %d\nwhy: %s\nbase %s head %s\nlogs %s (pass %d)\n"
                        % (k, t, why, base, head, self.log, n))
        if t >= MAX_TRIES:
            self.git("branch", "-f", "ralph/failed/%s" % k, head)
            self.git("switch", "-q", MAIN)
            self.git("branch", "-f", WIP, MAIN)
            self._clear_notes()
            self.state["tries"].pop(k, None)
            self.state["task_i"] += 1
            self._save()
            return self.status("parked %s after %d tries (evidence ralph/failed/%s)" % (k, t, k))
        self._save()
        return self.status("failed %s try %d: %s" % (k, t, why))

    # ---- tester
    def _export_tree(self, sha, dest):
        """A history-less copy of the candidate tree (git archive): no commit messages, no reflog, no transcript."""
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        data = subprocess.run(["git", "-C", str(self.root), "archive", "--format=tar", sha], capture_output=True,
                              check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            tf.extractall(dest, filter="data")
        return dest

    def tester_prompt(self, task, diff):
        return ((ARM_DIR / "TESTER.md").read_text() + "\n## FROZEN SPEC\n" +
                json.dumps(public_spec(task), indent=1, sort_keys=True) + "\n\n## TEST PLAN\n" + test_plan(task) +
                "\n## DIFF\n" + diff + "\n")

    def tester_pass(self, task):
        pend = self.state["pending"]
        n = self.state["n"]
        diff = self.git("diff", pend["base"], pend["head"])
        bundle = self.ctl / "tester" / pend["build_id"].replace("/", "_")
        work = self.tester_workdir(pend["head"], bundle / "tree")
        prompt = self.tester_prompt(task, diff)
        verdict, text, tester = None, "", None
        for _ in range(TESTER_TRIES):
            tester = self.new_id("test")
            if L.norm_id(tester) == L.norm_id(pend["builder"]):
                raise Refused("tester id %r equals the builder's: refused" % tester)
            self.emit("test_start", task, sha=pend["head"], detail={"tester": tester, "build_id": pend["build_id"]})
            self.status("tester pass running (%s on %s)" % (tester, pend["build_id"]))
            try:
                res = self.model("test", prompt, cwd=work, agent_id=tester, run_id=n,
                                 timeout_s=self.timeout_s, log=self.log / ("test.%d.%s.out" % (n, tester)))
            finally:
                self.release()
            text = res.get("text") or ""
            verdict = parse_verdict(text) if res.get("rc") == 0 else None
            self.emit("test_end", task, sha=pend["head"], verdict=verdict or "invalid",
                      detail={"tester": tester, "build_id": pend["build_id"], "rc": res.get("rc")})
            if verdict:
                break
        self.state["n"] = n + 1
        (self.ctl / "last_verdict.md").write_text("tester %s on %s: %s\n%s\n" % (
            tester, pend["build_id"], (verdict or "NO VERDICT").upper(), text[-6000:]))
        if verdict != "pass":
            return self._failed(task, pend["base"], pend["head"], "tester pass %s: %s" % (
                (verdict or "gave no verdict").upper(), text.strip()[-1500:]), n)
        if task.get("live", "none") != "none":
            if self.lane is None:
                raise Refused("task %s needs a live lane and none is configured" % task["id"])
            files = self.git("diff", "--name-only", pend["base"], pend["head"]).splitlines()
            self.lane.publish(task, pend["head"], pend["builder"], files)
            self.state["lane_wait"] = dict(pend)
            self.state["pending"] = None
            self._save()
            return self.status("waiting on lane for %s %s" % (task["id"], pend["head"][:12]))
        return self._final(task, pend, n)

    def _lane_step(self, task):
        lw = self.state["lane_wait"]
        r = self.lane.result(task, lw["head"])
        if r is None:
            return self.status("waiting on lane for %s %s" % (task["id"], lw["head"][:12]))
        self.state["lane_wait"] = None
        if r.get("verdict") != "pass":
            return self._failed(task, lw["base"], lw["head"], "live lane %s: %s" % (
                r.get("verdict"), r.get("why") or r.get("run_id")), self.state["n"])
        return self._final(task, lw, self.state["n"])

    def _final(self, task, pend, n):
        g = self.gate(task, pend["base"], pend["head"], "final", self.log / ("gate.final.%d" % n))
        ok, why = final_gate_ok(g)
        if not ok:
            return self._failed(task, pend["base"], pend["head"], "final gate: " + why, n)
        self.git("switch", "-q", MAIN)
        self.git("merge", "-q", "--ff-only", WIP)
        pub = subprocess.run(shlex.split(self.publish_cmd), cwd=str(self.root), capture_output=True, text=True)
        self.git("switch", "-q", WIP)
        if pub.returncode != 0:
            self.state["pending"] = None
            self._save()
            (self.ctl / "STOP").touch()
            return self.status("STOP: publish failed after a passed gate (%s)" % pub.stderr.strip()[:200])
        self.state.update(pending=None, task_i=self.state["task_i"] + 1)
        self.state["tries"].pop(task["id"], None)
        self._clear_notes()
        self._save()
        return self.status("published %s %s" % (task["id"], pend["head"][:12]))


# ------------------------------------------------------------------------------------------------ CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("run", "check-tested"))
    ap.add_argument("--root", required=True, help="the ralph_a arm clone")
    ap.add_argument("--ctl", default=os.environ.get("RALPH_A_CTL", DEFAULT_CTL))
    ap.add_argument("--tasks", default="", help="comma-separated frozen task ids, worked in order")
    ap.add_argument("--model-cmd", default=os.environ.get("RALPH_A_MODEL_CMD"))
    ap.add_argument("--max-steps", type=int, default=0)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if os.environ.get("RM_ARM") or Path.cwd().resolve().is_relative_to(root):
        print("refused: the loop is harness code; run it from outside the arm clone, without RM_ARM")
        return 2
    import arena_tasks as A
    p = A.paths()
    with L.harness_pass(p) as cap:                 # Rejected until ENTRYPOINTS lists ralph_a_loop.py (owed)
        w = SignedWriter(p, cap)
        if a.action == "check-tested":
            require_tested(w.records())
            print("every build has a test_start from a different agent")
            return 0
        tasks = [A.load_frozen(t, p) for t in a.tasks.split(",") if t]
        lp = Loop(root, a.ctl, tasks, model=CmdModel(a.model_cmd), writer=w, lane=RalphCLane(),
                  timeout_s=float(os.environ.get("RALPH_A_PASS_TIMEOUT_S", PASS_TIMEOUT_S)))
        for r in lp.run(a.max_steps):
            print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
