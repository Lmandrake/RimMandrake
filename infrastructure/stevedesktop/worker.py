#!/usr/bin/env python3
"""worker.py - the durable SteveDesktop test worker (STEVEDESKTOP_WORKER_BUILD_DURABLE_ATTEMPTS).

Runs in SteveDesktop's WSL from the runner clone (~/rm/runner). The testq dispatcher on Archmagi drives it over ssh;
nothing here needs an LLM, and no ssh session has to stay open while a job runs.

  worker.py start [--retry] < job.json   admit one testq.job/1; prints one JSON line {attempt, state}
  worker.py status [--job ID]            JSON: the job's latest attempt, or the worker as a whole
  worker.py result --attempt A           the attempt's testq.result/1 JSON
  worker.py outbox                       attempt ids whose result the dispatcher has not acked yet
  worker.py ack --attempt A              the dispatcher has the result: move it out of the outbox
  worker.py stop --attempt A             stop a running attempt (it writes an INTERRUPTED result)

How a job runs (one attempt at a time on this machine):
  * `start` takes a file lock, refuses while another attempt is alive (state busy, exit 75), and answers a
    duplicate delivery with the existing attempt (running or finished) instead of running the job twice.
    `--retry` is the only way to make attempt n+1.
  * It pulls the runner (`git pull --ff-only`) BEFORE the attempt starts, and refuses SOURCE_SHA_MISSING when
    the job's source_sha is not in the pulled HEAD. The attempt is pinned: nothing pulls while
    TESTQ_HOME/current names a live attempt (the daily self-upgrade checks it too).
  * The attempt is detached as a transient systemd user unit (linger is on), so it survives the ssh session;
    without systemd-run it falls back to a new session.
  * The attempt holds this machine's game guard (rimflow/host_guard.py) for its whole life; the guard is
    exported to rw_game.sh and modcheck, so nothing else can drive the game meanwhile (GUARD_HELD otherwise).
  * Phases: deploy (plan; on drift: game down, --apply) -> load (rw_game.sh init, up --wait) -> attest (hash
    what is deployed) -> run (modcheck, MODCHECK_SKIP_DEPLOY=1) -> result. state.json is rewritten every 15 s
    as the heartbeat. A run past the job's timeout_s is killed, the game restarted once, and the run retried
    once; a second hang is INVALID/HANG.
  * Requested rows absent from the sheet, and rows modcheck's preview planned (its EXPECTED_ROWS line) that never
    reached the sheet, are added as NOT_RUN, so partial output never reads as a pass.
  * The attempt runs at EXACTLY the job's source_sha: when the pulled HEAD is newer, the clone is detached at
    source_sha for the attempt and put back on main when it ends (a crashed attempt is healed at the next start).
  * When load starts a FRESH game process, the bridge client's UNKNOWN-outcome markers older than that start are
    resolved as moot (their game is gone); otherwise one killed game refuses every later job's mutating calls.
    When load KEEPS a running game that carries markers older than the load (a driver killed mid-call), the game is
    restarted once first, so the fresh start resolves them, instead of the job ending INVALID/HARNESS. Only once per
    marker (TESTQ_HOME/marker_bounces.json): a marker a restart did not clear fails later jobs fast, no restart loop.
  * A start that finds this machine's game guard HELD by a live driver (no testq attempt running) is deferred: busy,
    exit 75, the job stays pending; no attempt is made.

Files (outside git): TESTQ_HOME (default /mnt/d/RimTest/testq)
  attempts/<attempt>/{job.json, state.json, worker.log, modcheck.log, result.json}
  jobs/<job id>       the job's latest attempt id
  current             the live attempt id (absent when idle)
  marker_bounces.json the bridge marker cids the last marker restart was for -> the attempt that restarted
  outbox/<attempt>.json, outbox/acked/

The testq Archmagi backfill runs this same worker locally on Archmagi (TESTQ_WORKER_HOST=archmagi, its own TESTQ_HOME
and runner clone) with src/RimMandrake/Utils/testq/archmagi_phases.py as the phase commands: a phase that prints a
`REFUSED: why` line and fails (drift it may not deploy, no game it may not launch, a game it may not stop) ends the
attempt REFUSED/DEPLOY or REFUSED/LOAD, or a hang INVALID/HANG with no restart, instead of INVALID.

Tests override the phase commands with TESTQ_CMD_DEPLOY / TESTQ_CMD_LOAD / TESTQ_CMD_DOWN / TESTQ_CMD_RUN (shell
command strings; RUN gets the modcheck arguments appended) and the bridge client with TESTQ_CMD_BRIDGE, skip the
pull with TESTQ_SKIP_PULL=1, and may set TESTQ_SHEET_DIR, TESTQ_MODS_DIR, TESTQ_RUN_TIMEOUT_S and TESTQ_NO_SYSTEMD=1.
"""
import argparse
import fcntl
import glob
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# TESTQ_REPO: an attempt runs from a COPY of the main-checkout worker (see spawn), so the repo it works in is named here
RUNNER = os.path.abspath(os.environ.get("TESTQ_REPO") or os.path.join(HERE, "..", ".."))
CLONE = os.environ.get("TESTQ_CLONE") or RUNNER     # the git clone a job is pinned in (tests point it at a scratch repo)
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "Utils", "testq"))
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "rimflow"))
if os.environ.get("TESTQ_REPO") and os.path.exists(os.path.join(HERE, "schema.py")):
    sys.path.insert(0, HERE)        # the outer copy's own schema, not the pinned tree's
import schema as S  # noqa: E402

HOME = os.environ.get("TESTQ_HOME", "/mnt/d/RimTest/testq")
HEARTBEAT_S = 15
DEAD_AFTER_S = 120          # a state.json older than this, with no result, is a dead attempt
EX_BUSY = 75
ATTEMPT_RE = re.compile(S.JOB_ID_RE.pattern[:-1] + r"\.a\d+$")
SEAT = "RUNNER"
# the machine this worker runs on, named in every result: the testq Archmagi backfill runs this same worker locally
HOST = os.environ.get("TESTQ_WORKER_HOST") or "stevedesktop"
GAME = "infrastructure/stevedesktop/rw_game.sh"
SHEET_DIR = os.environ.get("TESTQ_SHEET_DIR") or os.path.join(RUNNER, "Transient", "modcheck")


def p(*parts):
    return os.path.join(HOME, *parts)


def ensure_dirs():
    for d in ("attempts", "jobs", "outbox", os.path.join("outbox", "acked")):
        os.makedirs(p(d), exist_ok=True)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def write_text(path, text):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    os.replace(tmp, path)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pin_marker():
    return p("pinned_clone")


def runner_clone_only():
    """Self-heal of a dirty clone is only for the machine-owned runner clone (~/rm/runner), never a seat clone.
    Tests opt in by pointing TESTQ_CLONE at a scratch repo."""
    return bool(os.environ.get("TESTQ_CLONE")) or os.path.basename(CLONE.rstrip("/")) == "runner"


def save_dirty(logdir):
    """Record what is dirty in the clone (tracked files only): path list + diff, into logdir. Returns the paths."""
    rc, status = git("status", "--porcelain", "--untracked-files=no")
    paths = [ln for ln in status.splitlines() if ln.strip()]
    if logdir and paths:
        os.makedirs(logdir, exist_ok=True)
        write_text(os.path.join(logdir, "dirty_clone.txt"), "\n".join(paths) + "\n")
        r = subprocess.run(["git", "-C", CLONE, "diff", "HEAD"], capture_output=True, text=True, timeout=300)
        write_text(os.path.join(logdir, "dirty_clone.diff"), r.stdout)
    return paths


def unpin(logdir=None):
    """Put the clone back on main after an attempt that pinned it to a detached source_sha (idempotent, never raises).

    Called BEFORE an attempt publishes its result: the next start may follow the result at once, and a clone still
    detached (or a git index.lock still held) then refused that job SYNC. Also called by the OUTER (current-HEAD)
    process at every start, so it does not depend on what the pinned attempt's own worker.py did.
    A tracked file an attempt dirtied makes `checkout main` fail: in the runner clone (nobody edits it) the dirt is
    recorded (dirty_clone.txt/.diff in logdir) and the tracked files are restored, so the rig does not sit idle."""
    detached = git("symbolic-ref", "-q", "HEAD")[0] != 0 if runner_clone_only() else False
    if not os.path.exists(pin_marker()) and not detached:
        return 0, ""
    try:
        rc, msg = git("checkout", "-q", "main")
        if rc != 0 and runner_clone_only() and "index.lock" not in msg:
            paths = save_dirty(logdir or (p("attempts", read_text(p("current"))) if read_text(p("current")) else None))
            if paths:
                rc, msg = git("checkout", "-q", "-f", "main")
                msg = "restored %d dirty tracked file(s) (see dirty_clone.txt): %s" % (len(paths), msg)
    except (OSError, subprocess.SubprocessError) as e:
        return 1, "unpin: %s" % e
    if rc == 0:
        try:
            os.remove(pin_marker())
        except FileNotFoundError:
            pass
    return rc, msg


def git(*args):
    r = subprocess.run(["git", "-C", CLONE] + list(args), capture_output=True, text=True, timeout=300)
    return r.returncode, (r.stdout + r.stderr).strip()


# ---------------------------------------------------------------- attempt bookkeeping

def attempt_state(aid):
    """-> (state, info): finished | running | dead | none."""
    if not aid:
        return "none", {}
    d = p("attempts", aid)
    res = read_json(os.path.join(d, "result.json"))
    if res:
        return "finished", {"outcome": res.get("outcome"), "cause": res.get("cause"), "counts": res.get("counts")}
    st = read_json(os.path.join(d, "state.json")) or {}
    try:
        age = time.time() - os.stat(os.path.join(d, "state.json")).st_mtime
    except OSError:
        age = None
    info = {"phase": st.get("phase"), "heartbeat_age_s": None if age is None else int(age), "unit": st.get("unit")}
    if age is not None and age < DEAD_AFTER_S:
        return "running", info
    return "dead", info


def finalize_dead(aid, why):
    """An attempt that stopped beating without a result gets an INTERRUPTED/CRASH one, so nothing waits on it."""
    d = p("attempts", aid)
    if not os.path.isdir(d):
        if read_text(p("current")) == aid:
            os.remove(p("current"))
        return
    job = read_json(os.path.join(d, "job.json")) or {}
    st = read_json(os.path.join(d, "state.json")) or {}
    res = base_result(job.get("id") or aid.rsplit(".a", 1)[0], aid, st.get("runner_sha"))
    res.update(outcome="INTERRUPTED", cause="CRASH", note=why, phase_s=st.get("phase_s") or {})
    unpin()
    publish_result(d, res)
    if read_text(p("current")) == aid:
        os.remove(p("current"))


def base_result(job_id, aid, runner_sha):
    return {"schema": S.RESULT_SCHEMA, "job": job_id, "attempt": aid, "host": HOST,
            "runner_sha": runner_sha, "outcome": None, "cause": None, "deployed": {}, "rows": [], "counts": {},
            "phase_s": {}, "retries": 0, "modcheck_exit": None, "artifacts": [], "started": S.utcnow(),
            "finished": None, "note": ""}


def publish_result(d, res):
    res["finished"] = res.get("finished") or S.utcnow()
    res["counts"] = S.count_verdicts(res["rows"])
    S.validate_result(res)
    S.dump(res, os.path.join(d, "result.json"))
    S.dump(res, p("outbox", res["attempt"] + ".json"))


# ---------------------------------------------------------------- start

def cmd_start(retry):
    job = S.validate_job(json.load(sys.stdin))
    ensure_dirs()
    with open(p("start.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        cur = read_text(p("current"))
        if cur:
            state, info = attempt_state(cur)
            if state == "running" and not cur.startswith(job["id"] + ".a"):
                return out({"state": "busy", "busy_with": cur, **info}, EX_BUSY)
            if state == "dead":
                finalize_dead(cur, "no heartbeat for %ss before the next start" % info.get("heartbeat_age_s"))
            elif state == "finished":
                os.remove(p("current"))
        last = read_text(p("jobs", job["id"]))
        if last:
            state, info = attempt_state(last)
            if state == "dead":
                finalize_dead(last, "no heartbeat for %ss" % info.get("heartbeat_age_s"))
                state, info = attempt_state(last)
            if state == "running" or not retry:
                return out({"attempt": last, "state": state, "duplicate": True, **info})
        held = guard_held_by_other()
        if held:        # a live driver that is not a testq attempt owns this game: defer (busy), never INVALID
            return out({"state": "busy", "busy_with": "guard: " + held, "deferred": True}, EX_BUSY)
        n = int(last.rsplit(".a", 1)[1]) + 1 if last else 1
        aid = "%s.a%d" % (job["id"], n)
        d = p("attempts", aid)
        os.makedirs(d)
        S.dump(job, os.path.join(d, "job.json"))
        write_text(p("jobs", job["id"]), aid)

        unpin(d)    # a crashed attempt can leave the clone on its detached pin: pull needs main
        if os.environ.get("TESTQ_SKIP_PULL") != "1":
            rc, msg = git("pull", "-q", "--ff-only", "origin", "main")
            if rc != 0:
                res = base_result(job["id"], aid, git("rev-parse", "HEAD")[1])
                res.update(outcome="REFUSED", cause="SYNC", note="runner pull failed: " + msg[-300:])
                publish_result(d, res)
                return out({"attempt": aid, "state": "finished", "outcome": "REFUSED", "cause": "SYNC"})
        head = git("rev-parse", "HEAD")[1]
        if git("merge-base", "--is-ancestor", job["source_sha"], "HEAD")[0] != 0:
            res = base_result(job["id"], aid, head)
            res.update(outcome="REFUSED", cause="SOURCE_SHA_MISSING",
                       note="runner HEAD %s does not contain source_sha %s" % (head[:10], job["source_sha"]))
            publish_result(d, res)
            return out({"attempt": aid, "state": "finished", "outcome": "REFUSED", "cause": "SOURCE_SHA_MISSING"})
        # the attempt runs at EXACTLY source_sha, not at whatever newer HEAD happens to contain it (bolt 1)
        want = git("rev-parse", "--verify", job["source_sha"] + "^{commit}")[1]
        # (tests that skip the pull must not move the real checkout: they pin only in a scratch TESTQ_CLONE)
        no_pin = os.environ.get("TESTQ_SKIP_PULL") == "1" and CLONE == RUNNER
        if want and want != head and not no_pin:
            rc, msg = git("checkout", "-q", "--detach", want)
            if rc != 0:
                res = base_result(job["id"], aid, head)
                res.update(outcome="REFUSED", cause="SYNC", note="could not pin the clone to %s: %s" % (want[:10], msg[-300:]))
                publish_result(d, res)
                return out({"attempt": aid, "state": "finished", "outcome": "REFUSED", "cause": "SYNC"})
            write_text(pin_marker(), want)
            head = want
        S.dump({"phase": "starting", "ts": S.utcnow(), "runner_sha": head}, os.path.join(d, "state.json"))
        write_text(p("current"), aid)
        unit = spawn(aid, d)
    return out({"attempt": aid, "state": "started", "runner_sha": head, "unit": unit})


def guard_held_by_other():
    """-> 'SEAT (purpose)' when this machine's game guard is HELD by a live driver, else None (FREE, STALE, unreadable).

    Checked before an attempt is created (STEVE_RIG_FIX_OUTOFBAND_DRIVER_MARKER): a window or script driving the game
    makes the job wait (busy, exit 75: the dispatcher leaves it pending) instead of starting an attempt that its
    calls would collide with. No testq attempt is live here (current was checked first), so a HELD lock is someone
    else's. A STALE lock is taken over by the attempt's own acquire, as before."""
    try:
        import host_guard
        st = host_guard.status()
    except Exception as e:      # noqa: BLE001 - an unreadable lock is the attempt's acquire to judge, not a defer
        sys.stderr.write("worker: guard status unreadable (%s); the attempt's acquire decides\n" % e)
        return None
    if st.get("state") != "HELD":
        return None
    return "%s (%s)" % (st.get("seat"), st.get("purpose"))


def spawn(aid, d):
    """Detach `worker.py _run <attempt>`: a transient systemd user unit, else a new session."""
    # run a COPY of this (main-checkout) worker, not __file__ inside the clone that is about to be pinned: a pin older
    # than this code would otherwise run ITS worker.py and never unpin
    outer = p("outer")
    os.makedirs(outer, exist_ok=True)
    for src in (os.path.abspath(__file__), S.__file__):
        shutil.copy2(src, os.path.join(outer, os.path.basename(src)))
    os.environ["TESTQ_REPO"] = RUNNER
    argv = [sys.executable, os.path.join(outer, "worker.py"), "_run", aid]
    keep = [k for k in os.environ if k != "TESTQ_UNIT" and k.startswith(("RM_", "TESTQ_", "STEVE_", "RIMFLOW_"))
            or k in ("PATH", "HOME", "USER", "LANG", "WSLENV", "WSL_DISTRO_NAME")]
    unit = "testq-" + re.sub(r"[^A-Za-z0-9_-]", "_", aid)
    if shutil.which("systemd-run") and os.environ.get("TESTQ_NO_SYSTEMD") != "1":
        r = subprocess.run(["systemd-run", "--user", "--collect", "--quiet", "--unit", unit,
                            "--property=KillMode=control-group", "--working-directory", RUNNER]
                           + ["--setenv=%s=%s" % (k, os.environ[k]) for k in keep]
                           + ["--setenv=TESTQ_UNIT=" + unit, "--"] + argv,
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            return unit
        sys.stderr.write("worker: systemd-run failed (%s); detaching with a new session\n" % r.stderr.strip()[-200:])
    log = open(os.path.join(d, "worker.log"), "ab")
    env = {k: v for k, v in os.environ.items() if k != "TESTQ_UNIT"}
    subprocess.Popen(argv, cwd=RUNNER, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                     start_new_session=True)
    return None


def out(obj, rc=0):
    print(json.dumps(obj, sort_keys=True))
    return rc


# ---------------------------------------------------------------- the attempt itself

# The run phase. `--drivers on` (TESTQ_SWEEP_WIRE_FLOWWORKS_DRIVERS): the suite's external live drivers (FlowWorks
# thirst_live.py, drawbridge_proof.py, validation_v2.py --live ...) run before the chains they feed, so a sweep or a
# targeted job measures those rows instead of reading UNMEASURED (modcheck/drivers.py).
RUN_BASE = ("export MODCHECK_SKIP_DEPLOY=1 WSLENV=${WSLENV:+$WSLENV:}MODCHECK_SKIP_DEPLOY; "
            "python.exe src/RimMandrake/Utils/modcheck/cli.py run --drivers on")



def driver_budget_export(timeout_s):
    """The drivers share at most half the job's run timeout (and never more than 2 h), so a targeted job whose chains
    read a slow driver (thirst_live ~40 min) ends as a driver TIMEOUT receipt, not a whole-job HANG."""
    budget = max(0, min(7200, int(timeout_s) // 2))
    return ("export MODCHECK_DRIVERS_BUDGET_S=%d WSLENV=${WSLENV:+$WSLENV:}MODCHECK_DRIVERS_BUDGET_S; " % budget)


class Stopped(Exception):
    pass


class Attempt:
    def __init__(self, aid):
        self.aid = aid
        self.d = p("attempts", aid)
        self.job = S.validate_job(read_json(os.path.join(self.d, "job.json")))
        st = read_json(os.path.join(self.d, "state.json")) or {}
        self.res = base_result(self.job["id"], aid, st.get("runner_sha") or git("rev-parse", "HEAD")[1])
        self.phase = "guard"
        self.game_pid = None            # the RimWorld pid load() started or found; game_gone() compares against it
        self.liveness_unknown = None
        self.child = None
        self.stop = threading.Event()
        self.log = open(os.path.join(self.d, "worker.log"), "a", encoding="utf-8")

    def say(self, msg):
        self.log.write("%s %s\n" % (S.utcnow(), msg))
        self.log.flush()

    def beat(self):
        S.dump({"phase": self.phase, "ts": S.utcnow(), "pid": os.getpid(), "runner_sha": self.res["runner_sha"],
                "retries": self.res["retries"], "phase_s": self.res["phase_s"],
                "unit": os.environ.get("TESTQ_UNIT")},
               os.path.join(self.d, "state.json"))

    def heartbeat_loop(self):
        while not self.stop.wait(HEARTBEAT_S):
            try:
                self.beat()
            except OSError as e:
                self.say("heartbeat write failed: %s" % e)

    def sh(self, cmd, log_name=None, timeout=None):
        """Run a shell command in the runner clone; -> (rc or None on timeout, tail of output)."""
        logf = open(os.path.join(self.d, log_name or "worker.log"), "ab")
        self.say("$ " + cmd)
        self.child = subprocess.Popen(["bash", "-c", cmd], cwd=CLONE, stdin=subprocess.DEVNULL, stdout=logf,
                                      stderr=subprocess.STDOUT, start_new_session=True)
        try:
            rc = self.child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.kill_child()
            rc = None
        except BaseException:       # Stopped (SIGTERM) arrives here first: kill while we still know the child
            self.kill_child()
            raise
        finally:
            self.child = None
            logf.close()
        return rc, self.tail(log_name or "worker.log")

    def kill_child(self):
        c = self.child
        if c and c.poll() is None:
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(c.pid, sig)
                except ProcessLookupError:
                    break
                try:
                    c.wait(timeout=10)
                    break
                except subprocess.TimeoutExpired:
                    continue

    def tail(self, name, n=15):
        try:
            with open(os.path.join(self.d, name), encoding="utf-8", errors="replace") as f:
                return "".join(f.readlines()[-n:]).strip()
        except OSError:
            return ""

    def timed(self, name, fn):
        self.phase = name
        self.beat()
        t = time.time()
        try:
            return fn()
        finally:
            self.res["phase_s"][name] = self.res["phase_s"].get(name, 0) + int(time.time() - t)

    def fail(self, outcome, cause, note):
        self.res.update(outcome=outcome, cause=cause, note=note[-400:])
        return False

    # phases --------------------------------------------------------------
    def deploy(self):
        override = os.environ.get("TESTQ_CMD_DEPLOY")
        mods = [self.job["mod"]] + list(self.job.get("deploy") or [])
        if override:
            rc, tail = self.sh(override + " " + " ".join(shlex.quote(m) for m in mods), timeout=1200)
            if rc != 0 and refused_line(tail):     # a lane that may not deploy here (archmagi_phases.py): not a fault
                return self.fail("REFUSED", "DEPLOY", refused_line(tail))
            return rc == 0 or self.fail("INVALID", "DEPLOY", "deploy failed: " + tail)
        # a folded source (Pyrelands) or the composed target (RimMandrake.Biomes) is `--compose biomes`, never `--mod`
        args = " ".join(f + " " + shlex.quote(v) for f, v in S.deploy_flags(mods, os.path.join(RUNNER, "src")))
        plan = "python3 src/RimMandrake/Utils/deploy_custom_mods.py " + args
        rc, _ = self.sh(plan + " > %s 2>&1" % shlex.quote(os.path.join(self.d, "deploy_plan.txt")), timeout=600)
        if rc == 0:
            self.say("deploy: no drift, game kept")
            return True
        text = read_text(os.path.join(self.d, "deploy_plan.txt")) or ""
        if "Drift found" not in text:
            return self.fail("INVALID", "DEPLOY", "deploy plan failed: " + text[-300:])
        rc, tail = self.sh(self.cmd_down(), timeout=300)
        if rc != 0:
            return self.fail("INVALID", "DEPLOY", "game down before deploy failed: " + tail)
        rc, tail = self.sh(plan + " --apply", timeout=1200)
        return rc == 0 or self.fail("INVALID", "DEPLOY", "deploy --apply failed: " + tail)

    def cmd_down(self):
        return os.environ.get("TESTQ_CMD_DOWN") or GAME + " down"

    def load(self):
        cmd = os.environ.get("TESTQ_CMD_LOAD") or "%s init && %s up --wait" % (GAME, GAME)
        since = S.utcnow()
        rc, tail = self.sh(cmd, timeout=900)
        if rc != 0 and refused_line(tail):         # e.g. archmagi: no game running, and the lane never launches one
            return self.fail("REFUSED", "LOAD", refused_line(tail))
        if rc != 0:
            return self.fail("INVALID", "LOAD", "game load failed: " + tail)
        m = re.search(r"started pid (\d+)", tail)      # rw_game.sh up: a fresh process, not "already running"
        if not m:
            stale = self.pending_markers(since)
            if stale:
                # STEVE_RIG_FIX_OUTOFBAND_DRIVER_MARKER: a game kept from before this attempt carries a mutating call
                # whose outcome nobody knows (2026-10-26: a modcheck driver killed on its budget mid step_game_ticks).
                # Every mutating call this job makes would be refused (INVALID/HARNESS, three jobs in a row), and
                # nothing can read what that call did to a game we are about to reuse. We hold the guard, so no one
                # else is driving it: restart the game; the fresh start below resolves the markers as moot.
                # STEVEWORKER_FIX_MARKER_BOUNCE_EVERY_JOB: ONE restart per marker. A marker that survived a restart
                # (its resolve failed, or the client's delete silently gave up) would otherwise cost every later job
                # a cold load and then fail anyway: fail fast instead and name it for a human to reconcile.
                tried = read_json(p("marker_bounces.json")) or {}
                again = [c for c in stale if c in tried]
                if again:
                    return self.fail("INVALID", "HARNESS",
                                     "kept game carries bridge marker(s) %s that the restart by %s did not resolve; "
                                     "not restarting again: reconcile by hand (rimbridge_client.py --reconcile)"
                                     % (" ".join(again), tried[again[0]]))
                S.dump({c: self.aid for c in stale}, p("marker_bounces.json"))
                self.res["bounced_for_markers"] = stale
                self.say("kept game carries %d unknown-outcome bridge marker(s) older than this load (%s): "
                         "restarting it" % (len(stale), " ".join(stale)))
                rc, tail = self.sh(self.cmd_down(), timeout=300)
                if rc != 0:
                    return self.fail("REFUSED" if refused_line(tail) else "INVALID", "LOAD",
                                     "stale bridge marker(s) %s on a kept game; game down failed: %s"
                                     % (" ".join(stale), refused_line(tail) or tail))
                since = S.utcnow()
                rc, tail = self.sh(cmd, timeout=900)
                if rc != 0:
                    return self.fail("INVALID", "LOAD", "game reload after the marker restart failed: " + tail)
                m = re.search(r"started pid (\d+)", tail)
                if not m:
                    return self.fail("INVALID", "LOAD", "restarted the game for stale bridge marker(s) %s, but load "
                                     "did not report a fresh process: %s" % (" ".join(stale), tail[-200:]))
        if m:
            self.clear_moot_markers(since, m.group(1))
            if self.res.get("bounced_for_markers") is not None:   # remember only the ones the restart did not clear
                cleared = set(self.res.get("moot_markers") or [])
                S.dump({c: self.aid for c in self.res["bounced_for_markers"] if c not in cleared},
                       p("marker_bounces.json"))
        alive = m or re.search(r"already running \(pid (\d+)\)", tail)
        self.game_pid = alive.group(1) if alive else None
        return True

    def bridge_cmd(self):
        return os.environ.get("TESTQ_CMD_BRIDGE") or "python.exe src/RimMandrake/Utils/rimbridge_client.py"

    def pending_markers(self, before):
        """-> cids of the bridge client's unresolved UNKNOWN-outcome markers sent before `before` ([] if none or the
        list cannot be read: the job's own calls will then say if it matters)."""
        try:
            r = subprocess.run(["bash", "-c", self.bridge_cmd() + " --reconcile"], cwd=RUNNER, capture_output=True,
                               text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as e:
            self.say("could not list bridge markers: %s" % e)
            return []
        return [cid for cid, t in parse_markers(r.stdout) if t < before]

    def game_gone(self):
        """-> why the game this attempt loaded is no longer the one running, or None (alive, or cannot tell).

        A game killed mid-run still leaves modcheck a sheet (every row UNMEASURED: the bridge went away), which read
        DONE and was ingested as a partial verify (TESTQ_DEAD_GAME_RUN_FIX_READS_DONE, drill 2026-10-26). Only checked
        when load named the pid; a status that cannot tell keeps the verdict and says so in the note."""
        if not self.game_pid:
            return None
        cmd = os.environ.get("TESTQ_CMD_STATUS") or GAME + " status"
        try:
            r = subprocess.run(["bash", "-c", cmd], cwd=RUNNER, capture_output=True, text=True, timeout=120)
            text = r.stdout
        except (OSError, subprocess.TimeoutExpired) as e:
            text = "status failed: %s" % e
        m = re.search(r"running pid=(\d+)", text)
        if m:
            return None if m.group(1) == self.game_pid else (
                "the game loaded as pid %s is gone; pid %s runs now" % (self.game_pid, m.group(1)))
        if re.search(r"^stopped\b", text, re.M):
            return "the game loaded as pid %s is gone (rw_game.sh status: stopped)" % self.game_pid
        self.liveness_unknown = "game liveness unknown after the run (%s)" % text.strip()[-120:]
        self.say(self.liveness_unknown)
        return None

    def clear_moot_markers(self, since, pid):
        """Resolve the bridge client's UNKNOWN-outcome markers that predate a game this attempt just started.

        A mutating call whose reply was lost leaves a marker that refuses every later mutating call until reconciled
        (rimbridge_client.py). When the game it was sent to has died, its effect died with that process (RimWorld
        keeps nothing across a restart but saves), so the marker is moot for the fresh game; left in place it made
        every later job INVALID/HARNESS (killed-game drill, 2026-10-26: one jawa/time_clock marker wedged the lane).
        Only markers older than the start are touched, only after a fresh start, and only on this machine, whose game
        the attempt's guard owns; a marker while the same game kept running is a real unknown and stays."""
        base = self.bridge_cmd()
        cleared = []
        for cid in self.pending_markers(since):
            note = ("moot: sent to a game process that is gone; testq %s started a fresh game (pid %s) at %s"
                    % (self.aid, pid, since))
            try:
                rr = subprocess.run(["bash", "-c", "%s --reconcile --resolve %s --as not-applied --note %s"
                                     % (base, cid, shlex.quote(note))], cwd=RUNNER, capture_output=True,
                                    text=True, timeout=120)
            except (OSError, subprocess.TimeoutExpired) as e:
                self.say("could not resolve marker %s: %s" % (cid, e))
                continue
            if rr.returncode == 0:
                cleared.append(cid)
            else:
                self.say("could not resolve marker %s: %s" % (cid, (rr.stdout + rr.stderr).strip()[-200:]))
        if cleared:
            self.res["moot_markers"] = cleared
            self.say("resolved %d bridge marker(s) older than the fresh game as moot: %s" % (len(cleared),
                                                                                          " ".join(cleared)))

    def attest(self):
        mods_dir = os.environ.get("TESTQ_MODS_DIR") or os.path.join(os.environ.get("RM_STEAMAPPS", ""),
                                                                    "common", "RimWorld", "Mods")
        dep = {"mods": {}}
        _, folded, _c = S.deploy_catalog(os.path.join(RUNNER, "src"))
        for m in [self.job["mod"]] + list(self.job.get("deploy") or []):
            m = folded.get(m, m)                   # a folded source is deployed as its composed target
            root = os.path.join(mods_dir, m)
            dll, defs, n = hashlib.sha256(), hashlib.sha256(), 0
            for f in sorted(glob.glob(os.path.join(root, "**", "*"), recursive=True)):
                rel = os.path.relpath(f, root).replace(os.sep, "/")
                if not os.path.isfile(f):
                    continue
                n += 1
                if f.endswith(".dll"):
                    dll.update(rel.encode() + b"\0" + sha256_file(f).encode())
                elif f.endswith(".xml") and "/Defs/" in "/" + rel:
                    defs.update(rel.encode() + b"\0" + sha256_file(f).encode())
            dep["mods"][m] = {"dll_sha256": dll.hexdigest(), "defs_sha256": defs.hexdigest(), "files": n}
        mc = os.path.join(os.environ.get("RM_GAME_USERDATA", ""), "Config", "ModsConfig.xml")
        dep["modsconfig_sha256_prerun"] = sha256_file(mc) if os.path.isfile(mc) else None
        self.res["deployed"] = dep
        return True

    def run_modcheck(self):
        args = S.modcheck_args(self.job)
        timeout = int(os.environ.get("TESTQ_RUN_TIMEOUT_S") or self.job.get("timeout_s", 2700))
        base = os.environ.get("TESTQ_CMD_RUN") or (driver_budget_export(timeout) + RUN_BASE)
        cmd = base + " " + " ".join(shlex.quote(a) for a in args)
        for attempt_no in (1, 2):
            rc, tail = self.sh(cmd, log_name="modcheck.log", timeout=timeout)
            if rc is not None:
                self.res["modcheck_exit"] = rc
                ok = self.read_sheet(tail)
                gone = self.game_gone()
                if gone:
                    return self.fail("INVALID", "GAME_DIED", gone + "; modcheck exit %s, sheet %s"
                                     % (rc, S.count_verdicts(self.res["rows"])))
                if self.liveness_unknown:
                    self.res["note"] = (self.res.get("note") or "") + "; " + self.liveness_unknown
                return ok
            self.say("run %d hung past %ss: killed" % (attempt_no, timeout))
            if attempt_no == 2:
                return self.fail("INVALID", "HANG", "modcheck hung past %ss twice (one clean restart between)"
                                 % timeout)
            self.res["retries"] += 1
            self.phase = "restart"
            self.beat()
            rc_down, tail = self.sh(self.cmd_down(), timeout=300)
            if rc_down != 0 and refused_line(tail):    # the game may not be restarted here: no second run
                return self.fail("INVALID", "HANG", "modcheck hung past %ss; no restart (%s)"
                                 % (timeout, refused_line(tail)))
            if not self.load():
                return False
            self.phase = "run"
        return False

    def read_sheet(self, tail):
        text = open(os.path.join(self.d, "modcheck.log"), encoding="utf-8", errors="replace").read()
        names = re.findall(r"Transient[\\/]+modcheck[\\/]+([^\s\\/]+)\.html", text)
        sheet = os.path.join(SHEET_DIR, names[-1] + ".json") if names else None
        data = read_json(sheet) if sheet else None
        refusal = re.search(r"^REFUSED: (.+)$", text, re.M)
        if not data and refusal:
            return self.fail("INVALID", "BLOCKED_SELECTION", "modcheck refused the selection: " + refusal.group(1))
        if not data:
            return self.fail("INVALID", "HARNESS", "modcheck exit %s and no sheet JSON: %s"
                             % (self.res["modcheck_exit"], tail[-300:]))
        rows = S.rows_from_summary(data.get("summary") or {})
        # a red canary: every row the SHEET has is UNMEASURED for it (before NOT_RUN accounting, which used to hide a
        # red canary on a --rows job behind the requested rows it appended)
        canary_red = bool(rows) and all(r["verdict"] == "UNMEASURED" for r in rows) and "canary" in text.lower() \
            and any("canary" in (r["detail"] or "").lower() for r in rows)
        wanted = self.job["selector"].get("rows") or []
        seen = {r["row"] for r in rows}
        for w in wanted:
            if w not in seen:
                rows.append({"chain": None, "row": w, "verdict": "NOT_RUN", "validity": None, "freshness": None,
                             "detail": "requested, absent from the sheet"})
                seen.add(w)
        # bolt 2: modcheck's own preview (EXPECTED_ROWS) names every row the run was planned to execute, so a row
        # that never reached the sheet is NOT_RUN here instead of silently absent
        for w in expected_rows(text):
            if w not in seen:
                rows.append({"chain": None, "row": w, "verdict": "NOT_RUN", "validity": None, "freshness": None,
                             "detail": "in modcheck's preview plan, absent from the sheet"})
                seen.add(w)
        self.res["rows"] = rows
        for path in (sheet, sheet[:-5] + ".html", os.path.join(self.d, "modcheck.log")):
            if os.path.isfile(path):
                self.res["artifacts"].append({"name": os.path.basename(path), "path": path,
                                              "sha256": sha256_file(path), "bytes": os.path.getsize(path)})
        if canary_red:
            return self.fail("INVALID", "CANARY", "the vanilla canary was red: no mod row ran")
        self.res["outcome"] = "DONE"
        self.res["note"] = "modcheck exit %s; %s" % (self.res["modcheck_exit"], S.count_verdicts(rows))
        return True

    def run(self):
        hb = threading.Thread(target=self.heartbeat_loop, daemon=True)
        hb.start()
        try:
            import host_guard
            if os.environ.get("TESTQ_TEST_BEFORE_ACQUIRE"):     # selftest seam: a driver arriving in the race gap
                subprocess.run(os.environ["TESTQ_TEST_BEFORE_ACQUIRE"], shell=True, check=False)
            with host_guard.held(SEAT, "testq " + self.aid):
                self.say("guard held; runner %s" % self.res["runner_sha"])
                ok = self.timed("deploy", self.deploy)
                ok = ok and self.timed("load", self.load)
                ok = ok and self.timed("attest", self.attest)
                ok and self.timed("run", self.run_modcheck)
        except Stopped:
            self.kill_child()
            self.fail("INTERRUPTED", "HARNESS", "stopped (SIGTERM) in phase %s" % self.phase)
        except Exception as e:      # noqa: BLE001 - every attempt ends with a result, whatever broke
            self.kill_child()
            name = type(e).__name__
            if name == "Refused":
                self.fail("REFUSED", "GUARD_HELD", "game guard held: %s" % e)
            else:
                self.fail("INVALID", "CRASH", "%s in phase %s: %s" % (name, self.phase, e))
        finally:
            self.stop.set()
            if self.res["outcome"] is None:
                self.fail("INVALID", "HARNESS", "attempt ended in phase %s without a verdict" % self.phase)
            self.phase = "done"
            rc, msg = unpin(self.d)    # before the result: a start that follows it at once finds the clone on main
            if rc != 0:
                self.say("could not put the clone back on main (the next start retries): %s" % msg[-300:])
            publish_result(self.d, self.res)
            if read_text(p("current")) == self.aid:
                os.remove(p("current"))
            self.say("result %s %s %s" % (self.res["outcome"], self.res["cause"], self.res["counts"]))
        return 0


def parse_markers(text):
    """`rimbridge_client.py --reconcile` listing -> [(cid, sent_utc)] of its unresolved UNKNOWN-outcome markers."""
    found = []
    for line in (text or "").splitlines():
        f = line.split()
        if len(f) >= 2 and re.fullmatch(r"[0-9a-f]{16}", f[0]) and re.fullmatch(r"\d{4}-\S+Z", f[1]):
            found.append((f[0], f[1]))
    return found


def refused_line(text):
    """The `REFUSED: why` a phase command printed (archmagi_phases.py: a lane rule, not a failure), else None."""
    for line in reversed((text or "").splitlines()):
        if line.startswith("REFUSED:"):
            return line[len("REFUSED:"):].strip()[:300]
    return None


def expected_rows(log_text):
    """Row ids modcheck's preview promised to execute (`EXPECTED_ROWS [json list]`); [] when it printed none."""
    out = []
    for m in re.finditer(r"^EXPECTED_ROWS (\[.*\])\s*$", log_text, re.M):
        try:
            out += [str(x) for x in json.loads(m.group(1))]
        except ValueError:
            pass
    return out


def cmd_run(aid):
    a = Attempt(aid)

    def on_term(signum, frame):
        raise Stopped()
    signal.signal(signal.SIGTERM, on_term)
    return a.run()


# ---------------------------------------------------------------- read-side verbs

def cmd_status(job_id):
    ensure_dirs()
    if job_id:
        aid = read_text(p("jobs", job_id))
        state, info = attempt_state(aid)
        return out({"job": job_id, "attempt": aid, "state": state, **info})
    cur = read_text(p("current"))
    state, info = attempt_state(cur)
    return out({"busy": state == "running", "current": cur, "current_state": state, **info,
                "runner_sha": git("rev-parse", "HEAD")[1], "outbox": list_outbox()})


def list_outbox():
    return sorted(os.path.basename(f)[:-5] for f in glob.glob(p("outbox", "*.json")))


def cmd_result(aid):
    res = read_json(p("attempts", aid, "result.json"))
    if not res:
        return out({"attempt": aid, "error": "no result"}, 1)
    print(json.dumps(res, sort_keys=True))
    return 0


def cmd_ack(aid):
    src = p("outbox", aid + ".json")
    if os.path.exists(src):
        os.replace(src, p("outbox", "acked", aid + ".json"))
    return out({"attempt": aid, "acked": True})


def cmd_stop(aid):
    st = read_json(p("attempts", aid, "state.json")) or {}
    stopped = False
    if st.get("unit") and shutil.which("systemctl"):
        stopped = subprocess.run(["systemctl", "--user", "stop", st["unit"]], capture_output=True,
                                 timeout=120).returncode == 0
    if not stopped and st.get("pid"):
        try:
            os.kill(st["pid"], signal.SIGTERM)
        except ProcessLookupError:
            pass
    return out({"attempt": aid, "stop_sent": True})


def main(argv=None):
    ap = argparse.ArgumentParser(prog="worker.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--retry", action="store_true")
    s = sub.add_parser("status")
    s.add_argument("--job")
    for name in ("result", "ack", "stop"):
        sub.add_parser(name).add_argument("--attempt", required=True)
    sub.add_parser("outbox")
    sub.add_parser("_run").add_argument("attempt")
    a = ap.parse_args(argv)
    for v in (getattr(a, "attempt", None), getattr(a, "job", None)):
        if v and not ATTEMPT_RE.match(v) and not S.JOB_ID_RE.match(v):
            ap.error("not a job or attempt id: %r" % v)
    if a.cmd == "start":
        return cmd_start(a.retry)
    if a.cmd == "status":
        return cmd_status(a.job)
    if a.cmd == "result":
        return cmd_result(a.attempt)
    if a.cmd == "ack":
        return cmd_ack(a.attempt)
    if a.cmd == "stop":
        return cmd_stop(a.attempt)
    if a.cmd == "outbox":
        ensure_dirs()
        return out({"outbox": list_outbox()})
    return cmd_run(a.attempt)


if __name__ == "__main__":
    sys.exit(main())
