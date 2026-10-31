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
     tester) -> the tester pass runs FIRST. RECOVERY PATH: state.pending is only a cache; when it is missing (the loop
     died after logging build_end, before saving state.json) Loop._recover re-derives it from the signed log: the
     task's latest build_end with no later test_start/test_end of its build, not yet on main -> pending -> a build
     with no tester runs the tester next. Idempotent (a second call finds pending set, or the test_start).
  3  otherwise a BUILD pass. HARD CHECK (require_tested, code not prompt): every build_end in the signed event log
     must have a later test_start of that build by a DIFFERENT agent id (arena_eventlog.untested_builds, the rule
     the gate's step 9 and the report use), and no test_start may be the builder testing itself
     (flagged_same_agent); otherwise NotTested is raised and no model is invoked.
     The signed log is read only after its anchor/witness/roster check (arena_eventlog.report) passes: a log
     shorter than its anchor, deleted or rewritten refuses (fail closed). No process may have its cwd in the clone.
     The build pass: `git pull --rebase` on main (3 tries, 30/60 s apart; failed -> stop), run_selftests --quick
     pre-check (green needs `RESULT: GREEN`; a QUICK green is logged as pre-check only; a red start is allowed only
     when last_failure.md explains it, else STOP), fresh model invocation (role build, agent id minted by THIS loop for this invocation), bridge
     released (`bridge release --mine`) whatever happened, then the BUILD-PHASE gate: every arena_gate step PASS or
     NA except `test_record` (it cannot pass before the tester) and `live` (it cannot pass before the lane), with
     scope and placeholders PASS. Pass -> `build_end` (builder, build_id) and IMMEDIATELY the tester pass. Fail or a
     non-zero / killed model -> unpublished, last_failure.md (outside git) feeds the next pass; 3 tries -> parked on
     ralph/failed/<task>, wip reset to main.
  The TESTER pass: a new agent id (refused if it equals the builder's), `test_start` written BEFORE the model runs,
     then a fresh invocation whose prompt is TESTER.md + the frozen spec + the test plan + the diff and NOTHING
     else (no builder transcript, no last_failure, no builder prompt); its cwd is a history-less export of the
     candidate tree (git archive: no commit messages, no reflog) in a FRESH private temp root (no ancestor holds the
     control dir, the clone or the harness; removed after the pass), under bubblewrap when present (every
     builder-side path a tmpfs, the root the only writable bind, own pid namespace), with an ALLOW-LISTED env and a
     neutral TESTER_ID (no RM_ARM, no RALPH_A_*; the real id is only in the harness's events). It must end with
     `VERDICT: PASS` or `VERDICT: FAIL`; no verdict is retried once with another fresh tester, then counted as a
     fail. `test_end` carries the verdict. FAIL -> the tester's findings feed the next build pass (last_verdict.md
     + last_failure.md); PASS -> live task: published to the lane and the loop waits; else the FINAL gate (the
     whole arena_gate verdict must be `pass`, step 9 included) -> publish (ff-merge wip into main, publish cmd).

INJECTABLE (the selftest runs all of it offline with fakes): `model` (or --model-cmd / $RALPH_A_MODEL_CMD: argv,
prompt on stdin, env RALPH_A_ROLE / RALPH_A_AGENT_ID / RM_ARM=ralph_a, cwd = the arm clone or the tester export),
Every model pass runs in its own session/process group recorded in <ctl>/pass.pid; the group is killed at the
timeout and after the pass, and on loop start a pass left by a killed loop is killed (or the start refused).
`gate` ($RALPH_A_GATE_CMD, default arena_gate.py run from the HARNESS checkout), `writer` (default: the signed
arena_eventlog.HarnessWriter; OWED: "ralph_a_loop.py" must be added to arena_eventlog.ENTRYPOINTS before the real
writer can sign), `lane` (default: ralph_c_runner's candidate queue, minimal profiles only), `runway`, `precheck`,
`release`, `publish_cmd`, `sync`, `new_id`, `tester_workdir`. No account, host or key is named here: the runway
reading resolves the account from the environment (role_launch.resolve_account / ops_watch status.json).

The loop process itself must NOT run with its cwd inside the arm clone and must not carry $RM_ARM (HarnessWriter
refuses both); every git call is `git -C <root>`, and only model subprocesses get cwd = the clone.
Control files (outside git): <ctl>/state.json, last_failure.md, last_verdict.md, status, STOP, loop.lock, pass.pid,
log/.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unicodedata
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arm_sandbox as AS  # noqa: E402
import helper_capture as HC  # noqa: E402
import arena_eventlog as L  # noqa: E402
import arena_safe_git as SG  # noqa: E402

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
        """The accepted chain, ONLY after the anchor/witness/roster check (arena_eventlog.report) passes for this arm:
        a log deleted, truncated or rewritten below its anchor is refused, never read as 'nothing untested'
        (review M6). A fresh log with no record and no roster entry has no report row and passes."""
        rep = L.report(self.w.p, self.w._token).get(ARM) or {}
        if rep.get("refused"):
            raise Refused("refused: the signed %s log fails its anchor check: %s" % (ARM, "; ".join(
                str(x) for x in rep["refused"])[:600]))
        return self.w.accepted(ARM)


# ------------------------------------------------------------------------------------------------ the hard check
# Latin look-alikes norm_id (NFKC + Cf + casefold) does not fold: Cyrillic and Greek letters that render as ASCII.
_CONFUSABLE = str.maketrans({
    "а": "a", "в": "b", "е": "e", "ѐ": "e", "ё": "e", "һ": "h", "і": "i", "ї": "i", "ј": "j", "к": "k", "м": "m",
    "н": "h", "о": "o", "р": "p", "с": "c", "ѕ": "s", "т": "t", "у": "y", "х": "x", "ԁ": "d", "ԛ": "q", "ԝ": "w",
    "ɡ": "g", "ı": "i", "α": "a", "β": "b", "ε": "e", "ι": "i", "κ": "k", "ν": "v", "ο": "o", "ρ": "p", "τ": "t",
    "υ": "u", "χ": "x", "ϲ": "c", "ϳ": "j", "ѵ": "v", "ս": "u", "օ": "o", "ӏ": "l", "ǀ": "l", "‐": "-", "‑": "-",
    "‒": "-", "–": "-", "—": "-", "−": "-", "＿": "_"})


def agent_key(x):
    """An agent id for the different-agent comparison, STRICTER than arena_eventlog.norm_id (review L1): norm_id,
    then combining marks dropped (NFKD, Mn), Cyrillic/Greek look-alikes mapped to Latin, casefold. A key that is
    still not ASCII is returned `unattributed:`-prefixed, which never counts as a different agent (fail closed).
    None for an unusable id."""
    n = L.norm_id(x)
    if n is None or n.startswith(L.UNATTRIBUTED):
        return n
    d = "".join(c for c in unicodedata.normalize("NFKD", n) if not unicodedata.combining(c))
    d = unicodedata.normalize("NFKC", d.translate(_CONFUSABLE)).casefold()
    return d if d.isascii() else L.UNATTRIBUTED + d


def canon_records(recs):
    """This arm's records with builder/tester ids replaced by agent_key, and a REPEATED build_end of the same
    (task, build_id, sha) dropped (the first is kept: a test after it tests that build; review L2)."""
    out, seen = [], set()
    for r in L.ordered([r for r in recs if r.get("arm") == ARM]):
        d = r.get("detail")
        if isinstance(d, dict) and r.get("event") in ("build_end", "test_start"):
            k = "builder" if r["event"] == "build_end" else "tester"
            if k in d:
                r = dict(r, detail=dict(d, **{k: agent_key(d[k])}))
            if r["event"] == "build_end":
                key = (L.norm_id(r.get("task")), L.norm_id(str(d.get("build_id"))), r.get("sha"))
                if key in seen:
                    continue
                seen.add(key)
        out.append(r)
    return out


def require_tested(recs):
    """Raise NotTested unless every build_end has a later test_start of that build by a different agent, and no
    test_start is its builder testing itself. Reads the event log, never loop memory."""
    mine = canon_records(recs)
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
    bid = open_tester_build(mine)                 # DRILL: a tester pass killed after test_start leaves the builder blocked
    if bid:
        raise NotTested("refused: a tester pass of build %s started and never ended (killed?); it must be "
                        "re-run before the next build pass" % bid)


def open_tester_build(recs):
    """The build_id whose tester pass is UNFINISHED, else None. Per build, not per (build, tester): a retry killed
    after an earlier attempt ended is open (GPT r1), and a killed attempt that a LATER attempt of the same build
    finished is closed, or the builder stays blocked forever (tester drill: the per-attempt match deadlocked every
    recovered tester pass). Unfinished = the last tester event is a test_start, OR no pass/fail verdict yet and fewer
    than TESTER_TRIES attempts ended (killed between two tries: GPT drill r3)."""
    last, verdict, ends = {}, set(), {}
    for r in recs:
        d = r.get("detail") or {}
        if r.get("event") in ("test_start", "test_end") and d.get("build_id"):
            last[d["build_id"]] = r["event"]
            if r["event"] == "test_end":
                ends[d["build_id"]] = ends.get(d["build_id"], 0) + 1
                if r.get("verdict") in ("pass", "fail"):
                    verdict.add(d["build_id"])
    for bid, ev in last.items():
        if ev == "test_start" or (bid not in verdict and ends.get(bid, 0) < TESTER_TRIES):
            return bid
    return None


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
TESTER_ENV = ("PATH", "LANG", "LANGUAGE", "TERM", "TZ", "SHELL", "USER", "LOGNAME")


def tester_env(agent_id, home, tmp, *, gpt=None):
    """The tester's WHOLE environment (review M4): an allow-list (TESTER_ENV, LC_*, and the names listed in
    $RALPH_A_TESTER_ENV_KEEP, e.g. the model CLI's auth variable), a fresh HOME/TMPDIR inside the tester root, and a
    NEUTRAL id TESTER_ID = tester-<sha256(real id)[:12]>. No RM_ARM, no RALPH_A_*, no ARENA_*, no clone path: the
    real id appears only in the harness's own events. Spend metering (ARENA_TESTER_SPEND_ENFORCE_METERED_HOME):
    RM_GPT_CALL_LOG=<gpt> (a directory inside the tester root) is SET by the harness, so the tester's GPT calls land
    where capture_tester copies them before the root is deleted; an inherited RM_GPT_CALL_LOG never passes. The arm
    stays hidden from the tester: its spend is attributed by WHERE the harness files the capture (the arm of the
    test_start record), never by a name the tester writes."""
    keep = set(TESTER_ENV) | {k for k in os.environ.get("RALPH_A_TESTER_ENV_KEEP", "").split(",") if k.strip()}
    env = {k: v for k, v in os.environ.items()
           if (k in keep or k.startswith("LC_")) and not k.startswith(("RALPH_A", "ARENA_", "RM_ARM", "RM_GPT_CALL_LOG"))}
    env.update(HOME=str(home), TMPDIR=str(tmp), TESTER_ID=neutral_id(agent_id))
    if gpt:
        env["RM_GPT_CALL_LOG"] = str(gpt).rstrip("/") + "/"
    return env


def capture_tester(rec, troot, rc=None, *, home=None, gpt=True):
    """Before a tester root is deleted: copy its Claude transcripts and GPT call log to the meter's helper store
    (helper_capture), keyed by the test_start record `rec`. Never raises: a failed capture leaves no manifest, and
    arena_spend.meter() then BLOCKS that tester (UNMEASURED), which is the fail-closed outcome."""
    if not rec:
        return None
    try:
        return HC.capture(rec, home=home or Path(troot) / "home", gpt_dir=(Path(troot) / "gpt") if gpt else None, rc=rc)
    except Exception as e:                       # noqa: BLE001 - the meter blocks on the missing manifest
        print("helper capture failed for %s: %s" % (HC.ident(rec), e), file=sys.stderr)
        return None


def neutral_id(agent_id):
    return "tester-" + hashlib.sha256(str(agent_id).encode()).hexdigest()[:12]


def sandbox_plan(role, cwd, sandbox):
    """(rw dirs, private HOME) for arm_sandbox.wrap. The tester: its fresh private root only (review M3: no builder
    material: ctl, the clone, transcripts). Every other role: the arm clone + a persistent scratch outside it."""
    if role == "test":
        root = Path((sandbox or {}).get("root") or cwd)
        return [root], root / "home"
    scratch = AS.scratch_dir(cwd, role)
    return [Path(cwd), scratch], scratch / "home"


def proc_start(pid):
    """/proc/<pid>/stat start time (clock ticks since boot), or None when the pid is gone."""
    try:
        return Path("/proc/%d/stat" % pid).read_text().rsplit(")", 1)[1].split()[19]
    except (OSError, IndexError, ValueError):
        return None


def group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def reap_stale_pass(pidfile, kill=os.killpg, wait_s=5.0):
    """On loop start (review M2): a model pass left running by a killed loop (its own session, so it outlives the
    loop) is killed as a GROUP: SIGTERM, then SIGKILL. Refused when it is still alive after that, so a new pass
    never runs beside an orphan in the same clone. A pidfile whose leader pid now belongs to another process (start
    time differs) and whose group is gone is stale and dropped."""
    pidfile = Path(pidfile)
    try:
        rec = json.loads(pidfile.read_text())
        pgid, start = int(rec["pgid"]), rec.get("start")
    except FileNotFoundError:
        return None
    except (OSError, ValueError, KeyError, TypeError):
        pidfile.unlink(missing_ok=True)
        return None
    now = proc_start(pgid)
    if now is not None and start is not None and now != start:
        pidfile.unlink(missing_ok=True)            # the leader pid was reused by an unrelated process
        return None
    for sig in (signal.SIGTERM, signal.SIGKILL):
        if not group_alive(pgid):
            break
        try:
            kill(pgid, sig)
        except ProcessLookupError:
            break
        t0 = time.time()
        while group_alive(pgid) and time.time() - t0 < wait_s:
            time.sleep(0.1)
    if group_alive(pgid):
        raise Refused("refused: the model pass of a previous loop (process group %d, %s) is still alive after "
                      "SIGTERM+SIGKILL; no pass starts beside it" % (pgid, pidfile))
    pidfile.unlink(missing_ok=True)
    return pgid


def proc_cmd(pid):
    """what a pid is running, for a refusal message (the process may already be gone)"""
    try:
        return open("/proc/%s/cmdline" % pid, "rb").read().replace(b"\0", b" ").decode("utf-8", "replace")[:120]
    except OSError:
        return "?"


def procs_in(root, me=None):
    """pids (not this process) whose cwd is inside `root` (review M2: nothing may be working in the clone when a
    build pass starts). /proc/*/cwd that cannot be read (another user's process) are skipped."""
    root = os.path.realpath(str(root))
    me = os.getpid() if me is None else me
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit() or int(d) == me:
            continue
        try:
            c = os.readlink("/proc/%s/cwd" % d)
        except OSError:
            continue
        if c == root or c.startswith(root + os.sep):
            out.append(int(d))
    return out


class CmdModel:
    """argv from --model-cmd / $RALPH_A_MODEL_CMD; prompt on stdin; its own session + process group, recorded in
    `pidfile` (set by the Loop) while it runs, the whole group killed at the timeout AND after every pass."""

    def __init__(self, cmd):
        if not cmd:
            raise Refused("no model command: pass --model-cmd or set RALPH_A_MODEL_CMD")
        self.argv = shlex.split(cmd)
        self.pidfile = None

    def preflight(self, sandbox, cwd):
        """Raise Refused now, before the loop logs test_start, when the tester could not be isolated."""
        rw, home = sandbox_plan("test", cwd, sandbox)
        self.wrap(["true"], dict(os.environ), cwd=cwd, rw=rw, home=home)

    @staticmethod
    def wrap(argv, env, *, cwd, rw, home, net="model"):
        """arm_sandbox.wrap (THE choke point; item ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE): no sandbox, no launch.
        net="model": own network namespace whose only route is the allow-listed model API relay; "none": no route."""
        try:
            return AS.wrap(argv, env, cwd=cwd, rw=rw, home=home, net=net)
        except AS.SandboxRefused as e:
            raise Refused(str(e))

    def spawn(self, role, argv, env, *, cwd, sandbox, agent_id, log, prompt, timeout_s):
        """Every arm model pass of every loop (ralph_a, ralph_c, trio, v3) launches HERE, sandboxed: own session and
        process group, recorded in the pidfile, the group killed at the timeout and after the pass. Returns rc."""
        rw, home = sandbox_plan(role, cwd, sandbox)
        argv, env = self.wrap(list(argv), env, cwd=cwd, rw=rw, home=home)
        with open(log, "w") as out:
            pr = subprocess.Popen(argv, cwd=str(cwd), env=env, stdin=subprocess.PIPE, stdout=out,
                                  stderr=subprocess.STDOUT, text=True, start_new_session=True)
            if self.pidfile:
                Path(self.pidfile).write_text(json.dumps({"pgid": pr.pid, "start": proc_start(pr.pid),
                                                          "role": role, "agent": agent_id}))
            try:
                pr.communicate(prompt, timeout=timeout_s)
                rc = pr.returncode
            except subprocess.TimeoutExpired:
                os.killpg(pr.pid, signal.SIGKILL)
                pr.wait()
                rc = -9
            finally:
                try:
                    os.killpg(pr.pid, signal.SIGKILL)  # whatever it left behind in its group dies with the pass
                except (ProcessLookupError, PermissionError):
                    pass
                if self.pidfile and not group_alive(pr.pid):
                    Path(self.pidfile).unlink(missing_ok=True)
        return rc

    def __call__(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        if role == "test":
            root = Path((sandbox or {}).get("root") or cwd)
            (root / "home").mkdir(exist_ok=True)
            (root / "tmp").mkdir(exist_ok=True)
            (root / "gpt").mkdir(exist_ok=True)
            env = tester_env(agent_id, root / "home", "/tmp", gpt=root / "gpt")
        else:
            env = {k: v for k, v in os.environ.items() if not k.startswith(("ARENA_", "RALPH_A_CTL"))}
            env.update(RALPH_A_ROLE=role, RALPH_A_AGENT_ID=agent_id, RM_ARM=ARM)
            env.update(GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="maintenance.auto", GIT_CONFIG_VALUE_0="false",
                       GIT_CONFIG_KEY_1="gc.auto", GIT_CONFIG_VALUE_1="0")      # the builder's own commits too
        rc = self.spawn(role, self.argv, env, cwd=cwd, sandbox=sandbox, agent_id=agent_id, log=log, prompt=prompt,
                        timeout_s=timeout_s)
        return self.result(log, rc)

    @staticmethod
    def result(log, rc):
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
        v = float(os.environ.get("RALPH_A_RUNWAY_MIN", "0.15"))
    except ValueError:
        return float("inf")                     # a garbled threshold refuses, never waves through
    return v if math.isfinite(v) and v >= 0 else float("inf")   # negative / NaN / inf: refuses (review L5)


RESULT_RE = re.compile(r"^RESULT: (GREEN|RED)\b(.*)$", re.M)
QUICK_RE = re.compile(r"QUICK: (\d+) skipped")


def precheck_verdict(rc, out):
    """-> (green, note). Green needs exit 0 AND a `RESULT: GREEN` line (review H1); a QUICK green is recorded as
    'pre-check only' with its skip count, never as a full-suite green."""
    m = RESULT_RE.findall(out or "")
    if rc != 0 or not m or m[-1][0] != "GREEN":
        return False, "pre-check red (rc %s, RESULT %s)" % (rc, m[-1][0] if m else "missing")
    q = QUICK_RE.search(m[-1][1])
    return True, ("quick pre-check only: QUICK: %s skipped (not a full-suite green)" % q.group(1)) if q else \
        "pre-check green"


def run_clone_code(root, argv, *, env=None, timeout=3600, role="harness"):
    """EVERY execution of clone-controlled code by a loop harness goes through HERE (item
    ARENA_SANDBOX_HARDEN_HARNESS_RUNS_ARM_CODE): the builder can rewrite run_selftests.py, every selftest, rimflow's
    cli.py, ./publish in its clone, so the harness runs them inside arm_sandbox.wrap exactly like a model pass (rw: the
    clone + a scratch outside it; everything else masked). -> CompletedProcess (text). A refused sandbox raises
    Refused: the code does not run unsandboxed."""
    rw, home = sandbox_plan(role, root, None)
    env = dict(os.environ if env is None else env)
    data = Path(rw[-1]) / "data"                       # the real data root (D:\ClaudeWork) is masked: a private one
    data.mkdir(parents=True, exist_ok=True)
    env["RM_DATA_ROOT"] = str(data)
    env.pop("AGENT_STORAGE_ROOT", None)
    a, e = CmdModel.wrap(list(argv), env, cwd=root, rw=rw, home=home, net="none")    # clone code needs no network
    return subprocess.run(a, cwd=str(root), env=e, capture_output=True, text=True, errors="replace",
                          timeout=timeout, stdin=subprocess.DEVNULL)


def precheck_run(root, log, arm):
    """The clone's `run_selftests.py --quick`, sandboxed. -> (rc, stdout); a refused sandbox is red (rc None)."""
    try:
        r = run_clone_code(root, [AS.PY, "src/RimMandrake/Utils/run_selftests.py", "--quick"],
                           env=dict(os.environ, RM_ARM=arm))
    except Refused as e:
        Path(log).write_text("precheck not run: %s\n" % e)
        return None, ""
    Path(log).write_text(r.stdout + r.stderr)
    return r.returncode, r.stdout


SANDBOX_RED_RE = re.compile(r"^\[\d+/\d+\]\s+(?:FAIL|CRASH)\s+\S+\s+(\S+)\s*$", re.M)


def _tree_of(root, rev):
    r = git_run(root, "rev-parse", "--verify", "-q", "%s^{tree}" % rev, capture_output=True, text=True, timeout=60)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _clean(root):
    r = git_run(root, "status", "--porcelain", "--untracked-files=all", capture_output=True, text=True, timeout=300)
    return r.returncode == 0 and not r.stdout.strip()


def base_export_run(root, base, log):
    """The quick pre-check on the BASE commit's tree, not the clone: a harness-side export of `base` (export_tree:
    object by object, verified) beside the log, given a fresh harness-made .git (`--template=`: no hooks, no config
    from the clone) so git-using selftests see a repo, then run sandboxed exactly like the clone's run. -> (rc, out)."""
    d = Path(log).parent / "base_export"
    export_tree(root, base, d)
    if os.path.lexists(d / ".git"):     # a crafted tree can hold .git/config (fsmonitor, hooksPath): never git there
        raise Refused("refused: base %s's tree carries a top-level .git" % base)
    for a in (["init", "-q", "--template=", "-b", MAIN], ["add", "-A", "-f"],
              ["commit", "-q", "--no-verify", "-m", "base export %s" % base]):
        r = subprocess.run(["git", "-C", str(d), "-c", "user.name=harness", "-c", "user.email=harness@local",
                            "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false"] + a, env=SG.safe_env(), capture_output=True, text=True,
                           timeout=600)
        if r.returncode != 0:
            raise Refused("base export git %s failed: %s" % (a[0], r.stderr.strip()[:300]))
    return precheck_run(d, str(log) + ".base", ARM)


BASE_RUNS = 2       # base observations a sandbox red must be red in to be baselined (ARENA_PRECHECK_FIX_FLAKY_BASE_RED)


def baseline_verdict(rc, out, log, *, root=None, base=None, base_run=None):
    """-> (green, note) for a SANDBOXED quick pre-check. The repo's suite was written for the host: some selftests
    are red in the arm sandbox whatever the clone holds (the game dirs, the bench clone, nested bwrap are masked).
    Those reds are accepted only when the BASE commit (merge-base of main and wip: owner or harness-published code,
    never the builder's unpublished try) is red on the same tests (item ARENA_PRECHECK_HARDEN_BASELINE_FIRST_RED: a
    loop's first red run used to be taken as the baseline, so a try that broke tests before it got them accepted).
    The baseline is keyed by base TREE (log-dir/sandbox_red.<tree>.json, harness-side, outside every arm bind): when
    the clone is clean at base's tree the run itself is one base observation; base is exported and run (base_run,
    default base_export_run) until there are BASE_RUNS, and only reds common to all are baselined. Main advancing = a new tree = a fresh baseline: nothing to delete. The old
    unkeyed sandbox_red.json is never read. A refused sandbox, a run with no RESULT line, no base, or a base that
    cannot be run is red."""
    v = precheck_verdict(rc, out)
    if v[0] or rc is None or not RESULT_RE.findall(out or ""):
        return v
    red = set(SANDBOX_RED_RE.findall(out or ""))
    if not red:
        return v
    if root is None or not base:
        return False, "%s; no base commit to pin a sandbox baseline from (%d red)" % (v[1], len(red))
    tree = _tree_of(root, base)
    if not tree:
        return False, "%s; base %s has no tree in the clone" % (v[1], base)
    b = Path(log).parent / ("sandbox_red.%s.json" % tree)
    how = "cached"
    if not b.exists():
        # item ARENA_PRECHECK_FIX_FLAKY_BASE_RED: one base run let a test red at base by chance stay excused for every
        # try on that tree. The baseline is the reds common to BASE_RUNS base observations (a flaky test must be red
        # in all of them); a clean clone at base's tree counts its own run as one observation.
        runs, how = [], "%d runs of base %s" % (BASE_RUNS, base[:12])
        if _tree_of(root, "HEAD") == tree and _clean(root):
            runs, how = [red], "this run (clone clean at base's tree) + %d export(s)" % (BASE_RUNS - 1)
        while len(runs) < BASE_RUNS:
            i = len(runs)
            try:
                brc, bout = (base_run or base_export_run)(root, base, log if i == 0 else "%s.%d" % (log, i))
            except Refused as e:
                return False, "%s; base %s could not be run for a baseline: %s" % (v[1], base[:12], e)
            if brc is None or not RESULT_RE.findall(bout or ""):
                return False, "%s; the base %s pre-check gave no RESULT (rc %s): no baseline" % (v[1], base[:12], brc)
            runs.append(set(SANDBOX_RED_RE.findall(bout or "")))
        base_red = set.intersection(*runs)
        b.write_text(json.dumps({"red": sorted(base_red), "flaky": sorted(set.union(*runs) - base_red),
                                 "base": base, "tree": tree, "how": how,
                                 "at": time.strftime("%Y-%m-%dT%H:%M:%S")}, indent=1) + "\n")
    new = sorted(red - set(json.loads(b.read_text()).get("red") or ()))
    if new:
        return False, "pre-check red in the arm sandbox beyond base %s's baseline (%s): %s" % (
            base[:12], b, ", ".join(new[:8]))
    return True, ("quick pre-check only: green but for %d sandbox-environment reds that base %s also has "
                  "(baseline %s, %s)" % (len(red), base[:12], b, how))


def default_precheck(root, log, base=None):
    rc, out = precheck_run(root, log, ARM)
    return baseline_verdict(rc, out, log, root=root, base=base)


def default_sync(root, sleep=time.sleep, tries=3, pin=None, report=None):
    """The Ralph doc's pull (ralph_loop_design §1.2: `for n in 1 2 3; do git pull --rebase -q && break; sleep
    $((n*30)); done`), on main, before every build pass (review L6). -> True when a pull succeeded.
    A merge driver in the clone's config (`merge.<name>.driver`, builder-set) is never run: the pull pins it to
    `false`, which turns even a clean merge of a `merge=<name>` file into a conflict. Refusing to run it is right;
    wedging the loop on it is not, so: `report` gets a defect detail, the half-done rebase is aborted, the driver
    keys are unset in the clone (git then merges those files as plain text, running nothing) and the pull is retried."""
    top = git_run(root, "rev-parse", "--show-toplevel", capture_output=True, text=True)
    if top.returncode != 0 or os.path.realpath(top.stdout.strip()) != os.path.realpath(str(root)):
        return False                                              # never touch a tree that is not the loop's own clone
    # GPT r1 P1: a builder killed mid-edit leaves a dirty tree that blocks switch/pull --rebase. Park it (evidence
    # kept in the stash, untracked files too) in the loop's own clone, abort any half-done rebase, then sync.
    for a in (["rebase", "--abort"], ["merge", "--abort"]):
        git_run(root, *a, capture_output=True)
    if git_run(root, "status", "--porcelain", capture_output=True, text=True).stdout.strip():
        if git_run(root, "-c", "user.name=ralph_a", "-c", "user.email=ralph_a@localhost", "stash", "push", "-u", "-q",
                   "-m", "ralph-a dirty after killed build", capture_output=True).returncode != 0:
            return False
    if git_run(root, "switch", "-q", MAIN, capture_output=True).returncode != 0:
        return False
    # The builder owns .git/config: the pull never reads the remote from it. The URL is pinned on first sight (file
    # `pin`, harness-owned), the ssh/credential/askpass keys are the owner's, the protocols are allow-listed.
    url = Path(pin).read_text().strip() if pin and Path(pin).exists() else \
        git_run(root, "config", "--get", "remote.origin.url", capture_output=True, text=True).stdout.strip()
    if not url:
        return False                                  # no URL to pin: never pull the literal name "origin" (its section is the clone's)
    if pin and not Path(pin).exists():
        try:
            SG.net_cfg(root, url)                     # refuse (CloneRefused) before pinning a url the clone redirects
        except SG.CloneRefused:
            return False
        Path(pin).write_text(url + "\n")
    def pull():
        try:
            return SG.git_run(root, "pull", "--rebase", "-q", "--upload-pack=git-upload-pack", url, MAIN,
                              transport=True, url=url, capture_output=True, timeout=600).returncode == 0
        except SG.CloneRefused:                       # url.*.insteadOf / a remote section named like the pin
            return None
    recovered = False
    for n in range(1, tries + 1):
        ok = pull()
        if ok is None:
            return False
        if not ok and not recovered:
            drivers = SG.merge_drivers(root)
            if drivers:                               # the pinned-false driver is the likely cause: recover, retry now
                recovered = True
                if report:
                    report({"kind": "sync_merge_driver_refused", "drivers": drivers,
                            "note": "builder-set merge drivers are never run; unset in the clone, pull retried"})
                for a in (["rebase", "--abort"], ["merge", "--abort"]):
                    git_run(root, *a, capture_output=True)
                for k in drivers:
                    git_run(root, "config", "--local", "--unset-all", k, capture_output=True)
                ok = pull()
                if ok is None:
                    return False
        if ok:
            return True
        if n < tries:
            sleep(n * 30)
    return False


def default_release(root):
    """The clone's own `rimflow bridge release --mine`, sandboxed (its lock lives in the clone's .git; inside the
    sandbox a builder's take never reached the real bridge either). Best effort, as before."""
    try:
        run_clone_code(root, [AS.PY, "src/RimMandrake/rimflow/cli.py", "bridge", "release", "--mine"], timeout=120)
    except (Refused, subprocess.TimeoutExpired) as e:
        print("bridge release not run in %s: %s" % (root, e), file=sys.stderr)


def clone_relative_cmd(root, argv) -> str:
    """-> the first argv word that names clone-controlled code (./publish, `python3 publish.py` run from the clone, any
    existing path inside the clone), else ''. A bare word with no slash is a PATH lookup (python3, git) unless it
    exists in the clone (then `python3 publish.py` with cwd=clone would run it)."""
    c = os.path.realpath(str(root))
    for a in argv or ():
        p = a if os.path.isabs(a) else os.path.join(c, a)
        if "/" not in a and not os.path.lexists(p):
            continue
        r = os.path.realpath(p)
        if (r == c or r.startswith(c + os.sep)) and os.path.lexists(p):
            return a
    return ""


def harness_publish(root, pin=None):
    """The default publish (item ARENA_SANDBOX_HARDEN_HARNESS_RUNS_ARM_CODE): the HARNESS pushes the tested main to
    the pinned origin URL with arena_safe_git (hooks off, no clone-local transport config), never the clone's
    ./publish (builder-rewritable code). The url: the pin file default_sync wrote, else the clone's remote.origin.url
    (checked by SG.net_cfg, then pinned). -> (ok, why)."""
    url = Path(pin).read_text().strip() if pin and Path(pin).exists() else \
        git_run(root, "config", "--get", "remote.origin.url", capture_output=True, text=True).stdout.strip()
    if not url:  # never push to the literal name "origin" (its section is the clone's)
        return False, "no origin url to publish to (no pin, no remote.origin.url)"
    try:
        SG.net_cfg(root, url)
        if pin and not Path(pin).exists():
            Path(pin).write_text(url + "\n")
        r = SG.git_run(root, "push", "-q", url, "%s:%s" % (MAIN, MAIN),
                       transport=True, url=url, capture_output=True, text=True, timeout=600)
    except SG.CloneRefused as e:
        return False, "refused: %s" % e
    except subprocess.TimeoutExpired:
        return False, "push timed out"
    return r.returncode == 0, (r.stderr or r.stdout).strip()[:300]


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


# ------------------------------------------------------------------------------------------------ git the builder cannot steer
# The build helper owns the clone's .git (v3_control has the same hardening; it imports this module, so the copy
# lives here). A replace ref or graft makes `git archive`/`git diff` of sha A show commit B, export-ignore /
# export-subst in its .gitattributes change an archive, and a diff driver, textconv, fsmonitor or hooksPath in
# .git/config runs its code as the harness. Every git call on the clone ignores replace objects and grafts, loads no
# system/global/attributes file and disables those execution hooks; diffs also pass --no-ext-diff --no-textconv.
# One definition lives in arena_safe_git (SG); these names stay for callers (trio_loop, v3_control, the selftests).
GIT_SAFE_ENV = SG.GIT_SAFE_ENV
GIT_SAFE_CFG = SG.GIT_SAFE_CFG
NO_DRIVER = SG.NO_DRIVER
no_filter_cfg = SG.no_filter_cfg
net_cfg = SG.net_cfg
GPG_OFF = SG.GPG_OFF


def git_run(root, *a, **kw):
    """SG.git_run on the clone (the pull goes through SG.git_run(..., transport=True, url=...) in default_sync)."""
    return SG.git_run(root, *a, **kw)


def export_tree(root, sha, dest):
    """A history-less copy of exactly `sha`'s tree, read object by object (ls-tree + cat-file): replace refs and
    grafts are ignored and no attribute applies (`git archive` honours the builder's export-ignore/export-subst).
    Submodule entries are skipped; a symlink is kept only if it stays inside dest; a path may not escape dest."""
    ok, why = SG.verify_tree(root, sha)                         # a builder can store other bytes under an object's name
    if not ok:
        raise Refused("refused: tree of %s does not verify: %s" % (sha, why))
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    top = dest.resolve()
    r = git_run(root, "ls-tree", "-r", "-z", "--full-tree", sha, capture_output=True)
    if r.returncode != 0:
        raise Refused("git ls-tree failed: %s" % r.stderr.decode(errors="replace").strip()[:300])
    ents = []
    for e in r.stdout.split(b"\0"):
        if not e:
            continue
        meta, path = e.split(b"\t", 1)
        mode, kind, obj = meta.decode().split()
        if kind == "blob":
            ents.append((mode, obj, path.decode("utf-8", "surrogateescape")))
    if not ents:
        return dest
    r = git_run(root, "cat-file", "--batch", input="".join(o + "\n" for _, o, _ in ents).encode(),
                capture_output=True)
    if r.returncode != 0:
        raise Refused("git cat-file failed: %s" % r.stderr.decode(errors="replace")[:300])
    buf, pos = r.stdout, 0
    for mode, obj, path in ents:
        nl = buf.index(b"\n", pos)
        head = buf[pos:nl].split()
        if len(head) != 3 or head[0].decode() != obj:
            raise Refused("git cat-file: unexpected header %r for %s" % (buf[pos:nl][:80], path))
        size = int(head[2])
        data = buf[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
        f = dest / path
        if ".." in Path(path).parts or not f.resolve().is_relative_to(top):
            raise Refused("refused: tree path %r escapes the export" % path)
        f.parent.mkdir(parents=True, exist_ok=True)
        if mode == "120000":
            tgt = data.decode("utf-8", "surrogateescape")
            if not os.path.isabs(tgt) and (f.parent / tgt).resolve().is_relative_to(top):
                os.symlink(tgt, f)
            continue
        f.write_bytes(data)
        if mode == "100755":
            f.chmod(0o755)
    return dest


# ------------------------------------------------------------------------------------------------ the loop
class Loop:
    def __init__(self, root, ctl, tasks, *, model, gate=None, writer=None, lane=None, runway=None, precheck=None,
                 release=None, publish_cmd=None, sync="default", new_id=None, tester_workdir=None,
                 timeout_s=PASS_TIMEOUT_S, poll_s=60.0, sleep=time.sleep, procs=procs_in, tester_tmp=None):
        self.root, self.ctl = Path(root), Path(ctl)
        self.tasks = list(tasks)
        self.model, self.writer = model, writer
        self.gate = gate or (lambda t, b, h, ph, log: cmd_gate(t, b, h, ph, root=self.root, log=log))
        self.lane = lane
        self.runway = runway or default_runway
        self.pre_base = None                                      # the pass's base: its pre-check baseline pins here
        self.precheck = precheck or (lambda log: default_precheck(self.root, log, base=self.pre_base))
        self.release = release or (lambda: default_release(self.root))
        bad = clone_relative_cmd(self.root, shlex.split(publish_cmd)) if publish_cmd else ""
        if bad:      # item ARENA_SANDBOX_HARDEN_HARNESS_RUNS_ARM_CODE: the builder can rewrite any file of its clone
            raise Refused("refused: publish_cmd runs %r from the clone (builder-writable code); leave it unset to "
                          "publish with the harness's own push" % bad)
        self.publish_cmd = publish_cmd                            # None: harness_publish (the default)
        self._sync_notes = []                                     # defect details default_sync reports; drained per pass
        self.sync = (lambda: default_sync(self.root, self.sleep, pin=self.ctl / "origin.url",
                                          report=self._sync_notes.append)) if sync == "default" else sync   # None: no pull
        self.new_id = new_id or (lambda role: "ralph_a-%s-%s" % (role, uuid.uuid4().hex[:12]))
        self.tester_workdir = tester_workdir or self._export_tree
        self.timeout_s, self.poll_s, self.sleep = timeout_s, poll_s, sleep
        self.procs = procs
        self.tester_tmp = tester_tmp
        self.log = self.ctl / "log"
        self.log.mkdir(parents=True, exist_ok=True)
        self.pidfile = self.ctl / "pass.pid"
        if hasattr(model, "pidfile"):
            model.pidfile = self.pidfile
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
        r = git_run(self.root, *a, capture_output=True, text=True)
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
        self._recover(task)
        if self.state.get("pending"):
            return self.tester_pass(task)
        return self.build_pass(task)

    def _recover(self, task):
        """RECOVERY FROM THE SIGNED LOG (review M1), idempotent: state.pending is a cache of the log, not the truth.
        When neither pending nor lane_wait is set but the log's latest build_end of this task has NO later
        test_start or test_end of its build (the loop died between writing build_end and saving state.json), that
        build becomes pending again, so the next step runs its tester instead of refusing forever. A build already
        on main, or whose commit is gone, is left alone (the hard check then refuses, loudly)."""
        if self.state.get("pending") or self.state.get("lane_wait"):
            return None
        recs = canon_records(self.writer.records())
        tid = L.norm_id(task["id"])
        last = None
        for i, r in enumerate(recs):
            if r.get("event") == "build_end" and L.norm_id(r.get("task")) == tid:
                last = i
        if last is None:
            return None
        b = recs[last]
        d = b.get("detail") or {}
        bid = d.get("build_id")
        if open_tester_build(recs[last + 1:]) != bid and any(
                r.get("event") == "test_end" and (r.get("detail") or {}).get("build_id") == bid
                for r in recs[last + 1:]):
            return None                       # a tester pass FINISHED (a start alone, or an unfinished try sequence, is not)
        sha = b.get("sha")
        if not (isinstance(sha, str) and d.get("base") and d.get("builder")) or self.already_failed(task, sha) or \
                git_run(self.root, "cat-file", "-e", sha + "^{commit}", capture_output=True).returncode != 0 or \
                git_run(self.root, "merge-base", "--is-ancestor", sha, MAIN, capture_output=True).returncode == 0:
            return None
        self.state["pending"] = {"build_id": bid, "base": d["base"], "head": sha, "builder": d["builder"],
                                 "recovered": True}
        self._save()
        self.status("recovered from the log: build %s has no tester yet; the tester runs next" % bid)
        return bid

    def run(self, max_steps=0):
        lockf = open(self.ctl / "loop.lock", "w")
        try:
            fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lockf.close()
            raise Refused("another ralph_a loop holds %s" % (self.ctl / "loop.lock"))
        out, i = [], 0
        try:
            reap_stale_pass(self.pidfile)                         # an orphaned pass of a killed loop dies first
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

    def _sync_wip(self, task):
        """wip must contain main before a build. A wip that diverged from main (main advanced while an unpublished
        try survived) cannot fast-forward: LOUD recovery - the old try is kept on a backup branch, wip restarts
        at main, an event records it. Never a silent failed ff (candidates that could not merge)."""
        self.git("merge", "-q", "--ff-only", MAIN, check=False)
        if git_run(self.root, "merge-base", "--is-ancestor", MAIN, "HEAD", capture_output=True).returncode == 0:
            return
        old = self.git("rev-parse", "HEAD")
        backup = "ralph/wip-diverged-%s" % old[:12]
        self.git("branch", "-f", backup, old)
        self.git("switch", "-q", "-C", WIP, MAIN)
        self.emit("defect", task, detail={"kind": "wip_diverged", "old_wip": old, "backup": backup,
                                          "main": self.git("rev-parse", MAIN)})

    # ---- build
    def build_pass(self, task):
        require_tested(self.writer.records())                     # HARD CHECK: before anything else of the pass
        busy = self.procs(self.root) if self.procs else []
        if busy:
            raise Refused("refused: process(es) %s have their cwd in the clone %s; no build pass beside them"
                          % ([(b, proc_cmd(b)) for b in busy[:8]], self.root))
        synced = self.sync is None or self.sync()
        for d in self._sync_notes:
            self.emit("defect", task, detail=d)
        self._sync_notes.clear()
        if not synced:
            return self.status("sync failed")
        if self.git("rev-parse", "--verify", "-q", WIP, check=False):
            self.git("switch", "-q", WIP)
        else:
            self.git("switch", "-q", "-c", WIP, MAIN)
        self._sync_wip(task)
        base = self.git("merge-base", MAIN, "HEAD")      # main, not wip: an unpublished try stays in the diff
        n = self.state["n"]
        self.pre_base = base
        pre = self.precheck(self.log / ("pre.%d" % n))
        green, pre_note = pre if isinstance(pre, tuple) else (bool(pre), "pre-check %s" % ("green" if pre else "red"))
        if not green and not (self.ctl / "last_failure.md").exists():
            (self.ctl / "STOP").touch()
            return self.status("red start, unexplained: STOP written (%s)" % pre_note)
        builder = self.new_id("build")
        prompt = (ARM_DIR / "PROMPT.md").read_text() + "\n## TASK (frozen spec)\n" + \
            json.dumps(public_spec(task), indent=1, sort_keys=True) + "\n"
        for name, head_ in (("last_failure.md", "LAST FAILURE"), ("last_verdict.md", "TESTER VERDICT")):
            if self._note(name):
                prompt += "\n## %s\n%s\n" % (head_, self._note(name))
        self.status("build pass running (%s)" % builder)
        self.emit("pass_start", task, detail={"role": "build", "agent": builder, "precheck": pre_note})
        try:
            res = self.model("build", prompt, cwd=self.root, agent_id=builder, run_id=n, timeout_s=self.timeout_s,
                             log=self.log / ("build.%d.out" % n))
        finally:
            self.release()                                        # whatever the agent did, the bridge is free again
        rc = res.get("rc")
        head = self.git("rev-parse", "HEAD")
        self.state["n"] = n + 1
        ok, why = (False, "model exit %r (killed or failed)" % rc) if rc != 0 else (False, "empty candidate") \
            if head == base else (False, "no new commit: wip still holds the candidate that already FAILED") \
            if self.already_failed(task, head) else (None, None)  # DRILL: a leftover unchecked commit of a killed pass IS gated
        gated = ok is None                            # only a candidate the gate actually judged is remembered as failed
        if ok is None:
            g = self.gate(task, base, head, "build", self.log / ("gate.build.%d" % n))
            ok, why = build_gate_ok(g)
        self.emit("pass_end", task, sha=head, verdict="pass" if ok else "fail",
                  detail={"role": "build", "agent": builder, "rc": rc, "why": why})
        if not ok:
            return self._failed(task, base, head, "build pass: " + why, n, record=gated)
        bid = "%s.%s" % (task["id"], head[:12])
        self.emit("build_end", task, sha=head, detail={"builder": builder, "build_id": bid, "base": base})
        self.state["pending"] = {"build_id": bid, "base": base, "head": head, "builder": builder}
        self._save()
        return self.tester_pass(task)                             # AT ONCE: no other work between build and test

    def _tree(self, sha):
        r = git_run(self.root, "rev-parse", "--verify", "-q", "%s^{tree}" % sha, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None

    def already_failed(self, task, sha):
        """True when this sha OR its tree already FAILED a gate, the tester, the lane or the final gate for this task:
        it is never gated or tested again. The TREE is the key (an amend --no-edit or an empty commit is a new sha
        with the same tree), so a builder that changes nothing after a FAIL cannot resubmit the failed diff."""
        k = task["id"]
        if sha in (self.state.get("failed_heads") or {}).get(k, []):
            return True
        tree = self._tree(sha)
        if tree and tree in (self.state.get("failed_trees") or {}).get(k, []):
            return True
        tid = L.norm_id(k)
        return any(r.get("event") == "test_end" and r.get("verdict") == "fail" and L.norm_id(r.get("task")) == tid
                   and (r.get("sha") == sha or (tree and self._tree(r.get("sha") or "") == tree))
                   for r in canon_records(self.writer.records()))

    def _failed(self, task, base, head, why, n, record=True):
        k = task["id"]
        if record and head != base:
            fh = self.state.setdefault("failed_heads", {}).setdefault(k, [])
            if head not in fh:
                fh.append(head)
            ft = self.state.setdefault("failed_trees", {}).setdefault(k, [])
            tree = self._tree(head)
            if tree and tree not in ft:
                ft.append(tree)
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
            self.state.get("failed_heads", {}).pop(k, None)
            self.state.get("failed_trees", {}).pop(k, None)
            self.state["task_i"] += 1
            self._save()
            return self.status("parked %s after %d tries (evidence ralph/failed/%s)" % (k, t, k))
        self._save()
        return self.status("failed %s try %d: %s" % (k, t, why))

    # ---- tester
    def _export_tree(self, sha, dest):
        """A history-less copy of the candidate tree: no commit messages, no reflog, no transcript, and nothing of
        the builder's .git steers it (export_tree)."""
        return export_tree(self.root, sha, dest)

    def tester_prompt(self, task, diff):
        return ((ARM_DIR / "TESTER.md").read_text() + "\n## FROZEN SPEC\n" +
                json.dumps(public_spec(task), indent=1, sort_keys=True) + "\n\n## TEST PLAN\n" + test_plan(task) +
                "\n## DIFF\n" + diff + "\n")

    def _tester_root(self):
        """A FRESH private root for one tester pass (review M3): mkdtemp (mode 0700) under $RALPH_A_TESTER_TMP or
        the system temp dir, refused when that base lies inside the control dir, the arm clone or the harness
        checkout, so no ancestor of the tester's cwd holds builder material (logs, last_failure.md, transcripts)."""
        base = Path(self.tester_tmp or os.environ.get("RALPH_A_TESTER_TMP") or tempfile.gettempdir()).resolve()
        for bad in (self.ctl, self.root, HARNESS_REPO):
            b = Path(bad).resolve()
            if base.is_relative_to(b) or b.is_relative_to(base):
                raise Refused("refused: tester temp base %s and builder material %s nest (a ../ from the tester's "
                              "cwd would reach it)" % (base, b))
        base.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix="rt-", dir=str(base)))

    def tester_pass(self, task):
        why = self.runway_refusal()                               # re-checked here too: build_pass calls straight in
        if why:
            return self.status("runway: " + why)
        pend = self.state["pending"]
        n = self.state["n"]
        diff = self.git("diff", *NO_DRIVER, pend["base"], pend["head"])
        return self._tester_in(task, pend, n, diff)

    def _tester_in(self, task, pend, n, diff):
        prompt = self.tester_prompt(task, diff)
        verdict, text, tester = None, "", None
        for _ in range(TESTER_TRIES):
            tester = self.new_id("test")
            if agent_key(tester) == agent_key(pend["builder"]) or not agent_key(tester):
                raise Refused("tester id %r equals the builder's: refused" % tester)
            troot = self._tester_root()          # GPT r1 P2: export, sandbox root and HOME are fresh PER ATTEMPT
            rec, res = None, {}
            try:
                work = self.tester_workdir(pend["head"], troot / "tree")
                sandbox = {"root": troot}             # the tester's only rw dir (arm_sandbox: all else masked)
                pf = getattr(self.model, "preflight", None)    # refusal must precede test_start (a refused tester never ran)
                if pf:
                    pf(sandbox, work)
                rec = self.emit("test_start", task, sha=pend["head"],
                                detail={"tester": tester, "build_id": pend["build_id"]})
                self.status("tester pass running (%s on %s)" % (tester, pend["build_id"]))
                try:
                    res = self.model("test", prompt, cwd=work, agent_id=tester, run_id=n, sandbox=sandbox,
                                     timeout_s=self.timeout_s, log=self.log / ("test.%d.%s.out" % (n, tester)))
                finally:
                    self.release()
            finally:
                capture_tester(rec, troot, res.get("rc"))     # the meter reads the copy; the root dies next
                shutil.rmtree(troot, ignore_errors=True)
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
                (verdict or "gave no verdict").upper(), text.strip()[-1500:]), n,
                record=verdict == "fail")      # no verdict = the tester's infrastructure failed, not the candidate
        if task.get("live", "none") != "none":
            if self.lane is None:
                raise Refused("task %s needs a live lane and none is configured" % task["id"])
            files = self.git("diff", *NO_DRIVER, "--name-only", pend["base"], pend["head"]).splitlines()
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
                r.get("verdict"), r.get("why") or r.get("run_id")), self.state["n"], record=r.get("verdict") == "fail")
        return self._final(task, lw, self.state["n"])

    def _publish(self):
        """-> (ok, why). Default: harness_publish (never the clone's ./publish). A test or owner publish_cmd (vetted
        at construction: nothing from the clone) runs as given."""
        if not self.publish_cmd:
            return harness_publish(self.root, self.ctl / "origin.url")
        pub = subprocess.run(shlex.split(self.publish_cmd), cwd=str(self.root), capture_output=True, text=True)
        return pub.returncode == 0, pub.stderr.strip()

    def _final(self, task, pend, n):
        if git_run(self.root, "merge-base", "--is-ancestor", MAIN, pend["head"], capture_output=True).returncode != 0:
            # main moved under a tested-but-unpublished build (killed between build_end and publish, then a pull): the
            # ff-only merge can never succeed, and raising here would refuse on every restart. LOUD: a defect event,
            # the build counts as a failed try, and the next build pass restarts wip at the new main (_sync_wip).
            self.emit("defect", task, sha=pend["head"], detail={
                "kind": "tested_build_main_advanced", "main": self.git("rev-parse", MAIN), "base": pend["base"]})
            return self._failed(task, pend["base"], pend["head"], "main advanced past the tested build's base; "
                                "rebuild on the new main", n)
        g = self.gate(task, pend["base"], pend["head"], "final", self.log / ("gate.final.%d" % n))
        ok, why = final_gate_ok(g)
        if not ok:
            return self._failed(task, pend["base"], pend["head"], "final gate: " + why, n)
        self.git("switch", "-q", MAIN)
        self.git("merge", "-q", "--ff-only", pend["head"])    # GPT r2: the TESTED sha, never the mutable WIP ref
        if self.git("rev-parse", "HEAD") != pend["head"]:
            raise Refused("refused: main is not at the tested sha %s after the merge" % pend["head"])
        ok, why = self._publish()
        self.git("switch", "-q", WIP)
        if not ok:
            self.state["pending"] = None
            self._save()
            (self.ctl / "STOP").touch()
            return self.status("STOP: publish failed after a passed gate (%s)" % why[:200])
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
