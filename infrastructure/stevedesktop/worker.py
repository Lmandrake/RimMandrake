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
    the job's source_sha is not in the pulled HEAD. The attempt is pinned to that HEAD: nothing pulls while
    TESTQ_HOME/current names a live attempt (the daily self-upgrade checks it too).
  * The attempt is detached as a transient systemd user unit (linger is on), so it survives the ssh session;
    without systemd-run it falls back to a new session.
  * The attempt holds this machine's game guard (rimflow/host_guard.py) for its whole life; the guard is
    exported to rw_game.sh and modcheck, so nothing else can drive the game meanwhile (GUARD_HELD otherwise).
  * Phases: deploy (plan; on drift: game down, --apply) -> load (rw_game.sh init, up --wait) -> attest (hash
    what is deployed) -> run (modcheck, MODCHECK_SKIP_DEPLOY=1) -> result. state.json is rewritten every 15 s
    as the heartbeat. A run past the job's timeout_s is killed, the game restarted once, and the run retried
    once; a second hang is INVALID/HANG.
  * Requested rows absent from the sheet are added as NOT_RUN, so partial output never reads as a pass.
  * When load starts a FRESH game process, the bridge client's UNKNOWN-outcome markers older than that start are
    resolved as moot (their game is gone); otherwise one killed game refuses every later job's mutating calls.

Files (outside git): TESTQ_HOME (default /mnt/d/RimTest/testq)
  attempts/<attempt>/{job.json, state.json, worker.log, modcheck.log, result.json}
  jobs/<job id>       the job's latest attempt id
  current             the live attempt id (absent when idle)
  outbox/<attempt>.json, outbox/acked/

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
RUNNER = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "Utils", "testq"))
sys.path.insert(0, os.path.join(RUNNER, "src", "RimMandrake", "rimflow"))
import schema as S  # noqa: E402

HOME = os.environ.get("TESTQ_HOME", "/mnt/d/RimTest/testq")
HEARTBEAT_S = 15
DEAD_AFTER_S = 120          # a state.json older than this, with no result, is a dead attempt
EX_BUSY = 75
ATTEMPT_RE = re.compile(S.JOB_ID_RE.pattern[:-1] + r"\.a\d+$")
SEAT = "RUNNER"
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


def git(*args):
    r = subprocess.run(["git", "-C", RUNNER] + list(args), capture_output=True, text=True, timeout=300)
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
    publish_result(d, res)
    if read_text(p("current")) == aid:
        os.remove(p("current"))


def base_result(job_id, aid, runner_sha):
    return {"schema": S.RESULT_SCHEMA, "job": job_id, "attempt": aid, "host": "stevedesktop",
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
        n = int(last.rsplit(".a", 1)[1]) + 1 if last else 1
        aid = "%s.a%d" % (job["id"], n)
        d = p("attempts", aid)
        os.makedirs(d)
        S.dump(job, os.path.join(d, "job.json"))
        write_text(p("jobs", job["id"]), aid)

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
        S.dump({"phase": "starting", "ts": S.utcnow(), "runner_sha": head}, os.path.join(d, "state.json"))
        write_text(p("current"), aid)
        unit = spawn(aid, d)
    return out({"attempt": aid, "state": "started", "runner_sha": head, "unit": unit})


def spawn(aid, d):
    """Detach `worker.py _run <attempt>`: a transient systemd user unit, else a new session."""
    argv = [sys.executable, os.path.abspath(__file__), "_run", aid]
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
        self.child = subprocess.Popen(["bash", "-c", cmd], cwd=RUNNER, stdin=subprocess.DEVNULL, stdout=logf,
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
            return rc == 0 or self.fail("INVALID", "DEPLOY", "deploy failed: " + tail)
        args = " ".join("--mod " + shlex.quote(m) for m in mods)
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
        if rc != 0:
            return self.fail("INVALID", "LOAD", "game load failed: " + tail)
        m = re.search(r"started pid (\d+)", tail)      # rw_game.sh up: a fresh process, not "already running"
        if m:
            self.clear_moot_markers(since, m.group(1))
        alive = m or re.search(r"already running \(pid (\d+)\)", tail)
        self.game_pid = alive.group(1) if alive else None
        return True

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
        base = os.environ.get("TESTQ_CMD_BRIDGE") or "python.exe src/RimMandrake/Utils/rimbridge_client.py"
        try:
            r = subprocess.run(["bash", "-c", base + " --reconcile"], cwd=RUNNER, capture_output=True, text=True,
                               timeout=120)
        except (OSError, subprocess.TimeoutExpired) as e:     # the job's own bridge calls will say if it matters
            self.say("could not list bridge markers: %s" % e)
            return
        cleared = []
        for line in r.stdout.splitlines():
            f = line.split()
            if len(f) < 2 or not re.fullmatch(r"[0-9a-f]{16}", f[0]) or not re.fullmatch(r"\d{4}-\S+Z", f[1]) \
                    or f[1] >= since:
                continue
            note = ("moot: sent to a game process that is gone; testq %s started a fresh game (pid %s) at %s"
                    % (self.aid, pid, since))
            try:
                rr = subprocess.run(["bash", "-c", "%s --reconcile --resolve %s --as not-applied --note %s"
                                     % (base, f[0], shlex.quote(note))], cwd=RUNNER, capture_output=True,
                                    text=True, timeout=120)
            except (OSError, subprocess.TimeoutExpired) as e:
                self.say("could not resolve marker %s: %s" % (f[0], e))
                continue
            if rr.returncode == 0:
                cleared.append(f[0])
            else:
                self.say("could not resolve marker %s: %s" % (f[0], (rr.stdout + rr.stderr).strip()[-200:]))
        if cleared:
            self.res["moot_markers"] = cleared
            self.say("resolved %d bridge marker(s) older than the fresh game as moot: %s" % (len(cleared),
                                                                                          " ".join(cleared)))

    def attest(self):
        mods_dir = os.environ.get("TESTQ_MODS_DIR") or os.path.join(os.environ.get("RM_STEAMAPPS", ""),
                                                                    "common", "RimWorld", "Mods")
        dep = {"mods": {}}
        for m in [self.job["mod"]] + list(self.job.get("deploy") or []):
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
            self.sh(self.cmd_down(), timeout=300)
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
            publish_result(self.d, self.res)
            if read_text(p("current")) == self.aid:
                os.remove(p("current"))
            self.say("result %s %s %s" % (self.res["outcome"], self.res["cause"], self.res["counts"]))
        return 0


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
