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
import tarfile
import tempfile
import io
import time
import unicodedata
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
UNISOLATED_OK_ENV = "RALPH_A_ALLOW_UNISOLATED_TESTER"
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


def tester_env(agent_id, home, tmp):
    """The tester's WHOLE environment (review M4): an allow-list (TESTER_ENV, LC_*, and the names listed in
    $RALPH_A_TESTER_ENV_KEEP, e.g. the model CLI's auth variable), a fresh HOME/TMPDIR inside the tester root, and a
    NEUTRAL id TESTER_ID = tester-<sha256(real id)[:12]>. No RM_ARM, no RALPH_A_*, no ARENA_*, no clone path: the
    real id appears only in the harness's own events."""
    keep = set(TESTER_ENV) | {k for k in os.environ.get("RALPH_A_TESTER_ENV_KEEP", "").split(",") if k.strip()}
    env = {k: v for k, v in os.environ.items()
           if (k in keep or k.startswith("LC_")) and not k.startswith(("RALPH_A", "ARENA_", "RM_ARM"))}
    env.update(HOME=str(home), TMPDIR=str(tmp), TESTER_ID=neutral_id(agent_id))
    return env


def neutral_id(agent_id):
    return "tester-" + hashlib.sha256(str(agent_id).encode()).hexdigest()[:12]


def bwrap_argv(sandbox, cwd):
    """bubblewrap prefix for the tester (review M3), or [] when $RALPH_A_TESTER_SANDBOX=none or no working bwrap.
    The whole filesystem read-only, a tmpfs over every builder-side path (ctl, the arm clone, the harness checkout,
    ~/.claude transcripts, $RALPH_A_TESTER_HIDE), the private tester root bound read-write, a fresh /proc and pid
    namespace (no /proc/<pid>/cwd of the builder), killed with its parent."""
    mode = os.environ.get("RALPH_A_TESTER_SANDBOX", "auto")
    exe = shutil.which("bwrap") or ("/usr/bin/bwrap" if os.path.exists("/usr/bin/bwrap") else None)
    if mode == "none" or not exe:
        if mode == "bwrap":
            raise Refused("RALPH_A_TESTER_SANDBOX=bwrap and no bwrap on PATH")
        # GPT r1 P1: no real isolation = the tester can read the clone, ctl and transcripts by absolute path, so it is
        # not blind. Fail loud unless the owner named the override; the override is logged by the caller.
        if os.environ.get(UNISOLATED_OK_ENV) != "1":
            raise Refused("refused: no bubblewrap isolation for the tester (%s); the tester would not be blind. "
                          "Install bwrap, or set %s=1 to run it unisolated (logged)." % (
                              "RALPH_A_TESTER_SANDBOX=none" if mode == "none" else "bwrap not found",
                              UNISOLATED_OK_ENV))
        return []
    hide = [str(x) for x in sandbox.get("hide", ())]
    hide += [x for x in os.environ.get("RALPH_A_TESTER_HIDE", "").split(":") if x]
    argv = [exe, "--ro-bind", "/", "/", "--dev", "/dev", "--unshare-pid", "--proc", "/proc", "--die-with-parent"]
    for h in sorted({os.path.realpath(h) for h in hide if os.path.isdir(h)}):
        argv += ["--tmpfs", h]
    root = str(sandbox["root"])
    return argv + ["--bind", root, root, "--chdir", str(cwd), "--"]


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
        bwrap_argv(sandbox, cwd)

    def __call__(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        argv = self.argv
        warn = ""
        if role == "test":
            sb = sandbox or {}
            root = Path(sb.get("root") or cwd)
            (root / "home").mkdir(exist_ok=True)
            (root / "tmp").mkdir(exist_ok=True)
            env = tester_env(agent_id, root / "home", root / "tmp")
            if sandbox:
                pre = bwrap_argv(sandbox, cwd)
                if not pre:                                       # only reachable with the named override set
                    msg = "WARNING: tester running UNISOLATED (%s=1): not blind\n" % UNISOLATED_OK_ENV
                    sys.stderr.write(msg)
                    warn = msg
                argv = pre + argv
        else:
            env = {k: v for k, v in os.environ.items() if not k.startswith(("ARENA_", "RALPH_A_CTL"))}
            env.update(RALPH_A_ROLE=role, RALPH_A_AGENT_ID=agent_id, RM_ARM=ARM)
        with open(log, "w") as out:
            out.write(warn)
            out.flush()
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


def default_precheck(root, log):
    r = subprocess.run([sys.executable, "src/RimMandrake/Utils/run_selftests.py", "--quick"], cwd=str(root),
                       capture_output=True, text=True, timeout=3600, env=dict(os.environ, RM_ARM=ARM))
    Path(log).write_text(r.stdout + r.stderr)
    return precheck_verdict(r.returncode, r.stdout)


def default_sync(root, sleep=time.sleep, tries=3):
    """The Ralph doc's pull (ralph_loop_design §1.2: `for n in 1 2 3; do git pull --rebase -q && break; sleep
    $((n*30)); done`), on main, before every build pass (review L6). -> True when a pull succeeded."""
    top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0 or os.path.realpath(top.stdout.strip()) != os.path.realpath(str(root)):
        return False                                              # never touch a tree that is not the loop's own clone
    # GPT r1 P1: a builder killed mid-edit leaves a dirty tree that blocks switch/pull --rebase. Park it (evidence
    # kept in the stash, untracked files too) in the loop's own clone, abort any half-done rebase, then sync.
    for a in (["rebase", "--abort"], ["merge", "--abort"]):
        subprocess.run(["git", "-C", str(root), *a], capture_output=True)
    if subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True,
                      text=True).stdout.strip():
        if subprocess.run(["git", "-C", str(root), "stash", "push", "-u", "-q", "-m", "ralph-a dirty after killed build"],
                          capture_output=True).returncode != 0:
            return False
    if subprocess.run(["git", "-C", str(root), "switch", "-q", MAIN], capture_output=True).returncode != 0:
        return False
    for n in range(1, tries + 1):
        if subprocess.run(["git", "-C", str(root), "pull", "--rebase", "-q"], capture_output=True,
                          timeout=600).returncode == 0:
            return True
        if n < tries:
            sleep(n * 30)
    return False


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
                 release=None, publish_cmd="./publish", sync="default", new_id=None, tester_workdir=None,
                 timeout_s=PASS_TIMEOUT_S, poll_s=60.0, sleep=time.sleep, procs=procs_in, tester_tmp=None):
        self.root, self.ctl = Path(root), Path(ctl)
        self.tasks = list(tasks)
        self.model, self.writer = model, writer
        self.gate = gate or (lambda t, b, h, ph, log: cmd_gate(t, b, h, ph, root=self.root, log=log))
        self.lane = lane
        self.runway = runway or default_runway
        self.precheck = precheck or (lambda log: default_precheck(self.root, log))
        self.release = release or (lambda: default_release(self.root))
        self.publish_cmd = publish_cmd
        self.sync = (lambda: default_sync(self.root, self.sleep)) if sync == "default" else sync   # None: no pull
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
        if any(r.get("event") in ("test_start", "test_end") and (r.get("detail") or {}).get("build_id") == bid
               for r in recs[last + 1:]):
            return None
        sha = b.get("sha")
        if not (isinstance(sha, str) and d.get("base") and d.get("builder")) or \
                subprocess.run(["git", "-C", str(self.root), "cat-file", "-e", sha + "^{commit}"],
                               capture_output=True).returncode != 0 or \
                subprocess.run(["git", "-C", str(self.root), "merge-base", "--is-ancestor", sha, MAIN],
                               capture_output=True).returncode == 0:
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

    # ---- build
    def build_pass(self, task):
        require_tested(self.writer.records())                     # HARD CHECK: before anything else of the pass
        busy = self.procs(self.root) if self.procs else []
        if busy:
            raise Refused("refused: process(es) %s have their cwd in the clone %s; no build pass beside them"
                          % (busy[:8], self.root))
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
        diff = self.git("diff", pend["base"], pend["head"])
        return self._tester_in(task, pend, n, diff)

    def _tester_in(self, task, pend, n, diff):
        prompt = self.tester_prompt(task, diff)
        verdict, text, tester = None, "", None
        for _ in range(TESTER_TRIES):
            tester = self.new_id("test")
            if agent_key(tester) == agent_key(pend["builder"]) or not agent_key(tester):
                raise Refused("tester id %r equals the builder's: refused" % tester)
            troot = self._tester_root()          # GPT r1 P2: export, sandbox root and HOME are fresh PER ATTEMPT
            try:
                work = self.tester_workdir(pend["head"], troot / "tree")
                sandbox = {"root": troot, "hide": [self.ctl, self.root, HARNESS_REPO, Path.home() / ".claude"]}
                pf = getattr(self.model, "preflight", None)    # refusal must precede test_start (a refused tester never ran)
                if pf:
                    pf(sandbox, work)
                self.emit("test_start", task, sha=pend["head"], detail={"tester": tester, "build_id": pend["build_id"]})
                self.status("tester pass running (%s on %s)" % (tester, pend["build_id"]))
                try:
                    res = self.model("test", prompt, cwd=work, agent_id=tester, run_id=n, sandbox=sandbox,
                                     timeout_s=self.timeout_s, log=self.log / ("test.%d.%s.out" % (n, tester)))
                finally:
                    self.release()
            finally:
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
        self.git("merge", "-q", "--ff-only", pend["head"])    # GPT r2: the TESTED sha, never the mutable WIP ref
        if self.git("rev-parse", "HEAD") != pend["head"]:
            raise Refused("refused: main is not at the tested sha %s after the merge" % pend["head"])
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
