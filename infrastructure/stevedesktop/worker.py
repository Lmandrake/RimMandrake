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
  * Phases: deploy (plan; on drift: game down, --apply; then the JawaBench companion must carry the source hash of
    the job's companion sources, else a FRESH one staged in TESTQ_HOME/companion/ is installed with the game down, else
    INVALID/DEPLOY before any row runs: Attempt.companion) -> load (rw_game.sh init, up --wait) -> attest (hash
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
  * A run that ends with a red canary or with the bridge's no_game (INVALID/HARNESS) stops the game, so the next job
    cold-starts instead of inheriting it; a lane that may not stop the game says so in the note. BEFORE a job commits
    to a game load() kept, the same wound is looked for in that process's Player.log and in the last result published
    here (kept_game_unmappable): a process that answers the bridge can still be unable to generate a map ever again,
    and that one burned three jobs on 11-14. With both of those unreadable the game is kept, and worker.log says so.
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

Tests override the phase commands with TESTQ_CMD_DEPLOY / TESTQ_CMD_LOAD / TESTQ_CMD_DOWN / TESTQ_CMD_RUN, and an exact-tier
job's TESTQ_CMD_TIERCHECK / TESTQ_CMD_TIERSWAP and its proofs folder TESTQ_PROOFS_DIR (shell
command strings; RUN gets the modcheck arguments appended) and the bridge client with TESTQ_CMD_BRIDGE, skip the
pull with TESTQ_SKIP_PULL=1, and may set TESTQ_SHEET_DIR, TESTQ_MODS_DIR, TESTQ_RUN_TIMEOUT_S and TESTQ_NO_SYSTEMD=1.
"""
import argparse
import fcntl
import glob
import hashlib
import importlib.util
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
# the companion's source-hash check (STEVE_COMPANION_FIX_DLL_STALE_NO_PRIORITIES); spawn copies it beside the outer
# worker, so a job pinned to a sha older than the module still checks its companion
sys.path.append(os.path.join(RUNNER, "src", "RimMandrake", "bridgetools"))
if os.environ.get("TESTQ_REPO") and os.path.exists(os.path.join(HERE, "companion_identity.py")):
    sys.path.insert(0, HERE)
import companion_identity as CI  # noqa: E402

# TESTQ_WORKER_MIGRATE_PYDANTIC_CONTRACT: a result is published only when contracts.models.TestqResult (pydantic v2,
# pinned by src/RimMandrake/contracts/requirements.lock) accepts it. WSL python is PEP 668 managed, so the lock is
# installed with `pip install --target` into TESTQ_PYDEPS; spawn copies models.py beside the outer worker, so a job
# pinned to an older sha is checked by this contract, not its own.
PYDEPS = os.path.expanduser(os.environ.get("TESTQ_PYDEPS") or "~/rm/pydeps")
MODELS_SRC = os.path.join(RUNNER, "src", "RimMandrake", "contracts", "models.py")
OUTER_MODELS = "contracts_models.py"
INSTALL_HINT = "python3 -m pip install --target %s -r src/RimMandrake/contracts/requirements.lock" % PYDEPS
_MODELS = []


class ContractMissing(RuntimeError):
    """contracts.models cannot load here (pydantic absent or broken): nothing may be admitted or published."""


def contract_models():
    """contracts.models, loaded once by path (the outer copy when running as one). Raises ContractMissing."""
    if _MODELS:
        return _MODELS[0]
    outer = os.path.join(HERE, OUTER_MODELS)
    path = outer if os.environ.get("TESTQ_REPO") and os.path.exists(outer) else MODELS_SRC
    if os.path.isdir(PYDEPS) and PYDEPS not in sys.path:
        sys.path.insert(0, PYDEPS)
    try:
        with open(path, "rb") as f:
            text = f.read()     # spawn writes THESE bytes: by then the clone may be pinned to an older models.py
        spec = importlib.util.spec_from_file_location("contracts_models", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["contracts_models"] = mod
        spec.loader.exec_module(mod)
    except (ImportError, OSError, SyntaxError) as e:
        sys.modules.pop("contracts_models", None)
        raise ContractMissing("contracts.models (%s) does not load: %s: %s; install it: %s"
                              % (path, type(e).__name__, e, INSTALL_HINT)) from None
    _MODELS.extend((mod, text))
    return mod


_OUTER = {}     # basename -> bytes of the outer worker's files, captured before the pin (STEVE_SPAWN_FIX_COPIES_THE_PAST)


def capture_outer():
    """Read worker.py, schema.py and companion_identity.py NOW, while the clone is still on the pulled main.

    With CLONE == RUNNER the pin checks these very files out at source_sha; copying them after it ran the OLD outer
    worker, the thing the copy exists to prevent. Like contract_models(), spawn writes these bytes, not the disk's."""
    _OUTER.clear()
    memo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy_memo.py")
    for src in (os.path.abspath(__file__), S.__file__, CI.__file__) + ((memo,) if os.path.isfile(memo) else ()):
        with open(src, "rb") as f:
            _OUTER[os.path.basename(src)] = f.read()


def contract_errors(res):
    """-> [] when TestqResult accepts `res`, else its 'loc: msg' lines. Raises ContractMissing."""
    m = contract_models()
    return m.errors(m.TestqResult, res)

HOME = os.environ.get("TESTQ_HOME", "/mnt/d/RimTest/testq")
HEARTBEAT_S = 15
DEAD_AFTER_S = 120          # a state.json older than this, with no result, is a dead attempt
EX_BUSY = 75
ATTEMPT_RE = re.compile(S.JOB_ID_RE.pattern[:-1] + r"\.a\d+$")
SEAT = "RUNNER"
# the machine this worker runs on, named in every result: the testq Archmagi backfill runs this same worker locally
HOST = os.environ.get("TESTQ_WORKER_HOST") or "stevedesktop"
# Steve1 ("stevedesktop") and Steve2 ("stevedesktop.b") own their games: the list repair, the kept-game probe and the
# dump are theirs; the archmagi lane's game is the owner's (design/specs/2026-11-23-steve-two-games-lane/boundary.md)
STEVE_LANE = HOST.split(".")[0] == "stevedesktop"
GAME = "infrastructure/stevedesktop/rw_game.sh"
# budget: danger=a hung minidump of a hung game holds the kill of that game; never reached in the 14 days to 2026-11-24; no
# budget: record of its run
DUMP_TIMEOUT_S = 180      # one small (no full memory) dump before a kill; the kill follows either way
# budget: danger=a wedged kept game holds the lane at its bridge probe; never reached in the 14 days to 2026-11-24; no record of
# budget: its run
PROBE_TIMEOUT_S = 30    # the kept-game bridge probe: modcheck's own client timeout (ensure_playing_map)
PROBE_GAP_S = 15        # between its two tries, so a game mid-autosave is not mistaken for a wedged one
# modcheck's refusal when the running load is not the list it composed (runner.verify_loaded_list), and its line saying
# it left ModsConfig on the composed list for a restart (runner.stale_keep_composed)
STALE_LOAD_RE = re.compile(r"HARNESS UNMEASURED: the running load is not the composed list[^:]*: (.+)$", re.M)
STALE_KEPT_RE = re.compile(r"^STALE_LOAD: ", re.M)
# MODCHECK_STALE_LOAD_FIX_UNINSTALLED_MOD: modcheck names a composed mod with no folder on this host as its own cause
NOT_INSTALLED_RE = re.compile(r"HARNESS UNMEASURED: mod_not_installed: (.+)$", re.M)
NO_GAME_RE = re.compile(r'"status":\s*"no_game"')      # the bridge's answer when the game has no current game
# modcheck's own words when the debug quicktest never reached a map (11-14: AlienRace.HarmonyPatches died with
# TypeInitializationException "Token 0x0 is not a valid MethodBase token"; the bridge never said no_game, so the
# wounded pid 4400 was handed to Bacta and the filler lane braked)
WORLD_START_FAILED_RE = re.compile(r"quicktest world start FAILED")
# live_site's refusal of a kept game whose tick the bridge cannot read (11-13: J20261113T100132Z-0f3ad6 and
# J20261113T114138Z-7ba5eb each kept it; RIMMANDRAKE_DIAGNOSE_STEVE_GAME_VANISHES_FIVE_BEFORE_BREAKFAST gap a)
TICK_UNREAD_RE = re.compile(r"a game is Playing at tick None")
GAME_FATAL_RE = re.compile(r"BadImageFormat|TypeLoadException|TypeInitializationException")   # loads, cannot make a world
# RIMMANDRAKE_RESTART_GAME_AFTER_MAPDATA_TIMEOUT_THREE_JOBS_BURNED: the evidence that a RUNNING process can never make
# a map again, so the next job must not inherit it (kept_game_unmappable). Two instruments, two sets of words.
# 1. the process's own Player.log. Only a wound that is PERMANENT for a process counts, and these two are:
#    * a WorldGenStep that threw. Nothing a later quicktest does reloads defs or re-JITs, so the same step throws for
#      every world this process ever tries (11-14; and pid 30296 on 10-31, AlienRace BadImageFormat then WorldGenStep
#      TypeLoadException, design/RimMandrake/ops_diagnoses/steve_invalid_2026-11-01.md).
#    * Harmony wrote a patch over IL it could not read, so that method is broken for the life of the process
#      (11-14: "Token 0x19c1 is not a valid MethodBase token in Assembly-CSharp.dll").
LOG_WOUND_RE = re.compile(r"Error in WorldGenStep|is not a valid MethodBase token")
#    A dead static constructor is a wound ONLY with the type-load family (GAME_FATAL_RE) on the same line, because a
#    type initializer that threw never runs again in the same process. The pair is the whole point:
#    vendor/wisdom/benign_log_errors.md records "Error in static constructor of ChooseWildAnimalSpawns.Main:
#    ArgumentNullException" as a line the lane ran through for weeks, so the line alone proves nothing; 11-14's
#    "Error in static constructor of AlienRace.HarmonyPatches: System.TypeInitializationException" is the pair.
CTOR_RE = re.compile(r"Error in static constructor of")
# 2. the most recently finished attempt's result: the harness-side words no Player.log ever carries. Its own table, not
#    invalid_class.SIGNATURES, which answers a different question (whose fault an INVALID was) and has no WorldGenStep
#    row; and a cross-tree import of it would crash a job pinned to a sha from before that module existed.
NOTE_WOUND_RE = re.compile(r"readiness .mapData|quicktest world start FAILED|" + LOG_WOUND_RE.pattern)
# A row that says the MAP is spoiled (its colony is dead or downed, or its site cannot be held): nothing on that map can be
# measured, so the kept game goes down before the next job. 33 lane jobs had such a row in 21 days (2026-11-23 study);
# the game went on to the next job each time.
SPOILED_RE = re.compile(r"dead colonists|no live colonist|RESTART \(damage to the test|could not hold the site quiet")
# stop_game_for_next_job's own words: an attempt that stopped its game says nothing about the process running now.
STOPPED_NOTE = "game stopped so the next job cold-starts"
# A cap on scanning a healthy giant Player.log once per kept load, not a measurement of one: every line above is
# written during load or during a quicktest's worldgen, far inside this much text. OUR rule, not a bar.
LOG_SCAN_CHARS = 32_000_000
# STEVE_GAME_FIX_UNBOUNDED_MAPS: a kept game is recycled before a job at either limit, both under pid 7460 (17 h, 27 maps,
# 20.9 GB on a 128 GB host, then deaf). Maps grow because river_site.py founds a site per run and keeps earlier sites.
MAX_GAME_AGE_S = int(os.environ.get("TESTQ_MAX_GAME_AGE_S") or 8 * 3600)
MAX_GAME_MAPS = int(os.environ.get("TESTQ_MAX_GAME_MAPS") or 20)
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


def game_log_path(name="Player.log"):
    """The running game's log, as the host exports it (RM_GAME_LOGDIR, else the user data dir)."""
    return os.path.join(os.environ.get("RM_GAME_LOGDIR") or os.environ.get("RM_GAME_USERDATA", ""), name)


def game_log_wound(text):
    """-> the first line of a game log proving that process can never make a map, or None (none in what was read).

    One line, both instruments on it: the permanent-wound patterns, and a dead static constructor only when the same
    line names the type-load family. An empty log is an answer ("nothing in it"), not a blindness."""
    for ln in text.splitlines():
        if LOG_WOUND_RE.search(ln) or (CTOR_RE.search(ln) and GAME_FATAL_RE.search(ln)):
            return ln.strip()[:200]
    return None


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def write_text(path, text):
    tmp = "%s.tmp.%d.%d" % (path, os.getpid(), threading.get_ident())
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
    """Self-heal of a dirty clone is only for the machine-owned runner clones (~/rm/runner, ~/rm/runner_b), never a seat clone.
    Tests opt in by pointing TESTQ_CLONE at a scratch repo."""
    return bool(os.environ.get("TESTQ_CLONE")) or os.path.basename(CLONE.rstrip("/")) in ("runner", "runner_b")


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


def heal_dirty(logdir):
    """STEVE_LANE_UNSTICK_PAUSED_UNOWNED_D1A4: a tracked file an attempt dirtied while the clone was ON MAIN (an
    in-tree writer such as modcheck's GREEN/STALE status registry) does not make `checkout main` fail, so unpin()
    never saw it, and the next `pull --ff-only` refused SYNC and paused the lane.
    In the runner clone only: record the dirt (dirty_clone.txt/.diff in logdir) and restore the tracked files.
    -> (number restored, message). Never raises."""
    if not runner_clone_only():
        return 0, ""
    try:
        paths = save_dirty(logdir)
        if not paths:
            return 0, ""
        rc, msg = git("reset", "-q", "HEAD", "--", ".")
        rc2, msg2 = git("checkout", "-q", "-f", "HEAD", "--", ".")
        return len(paths), "restored %d dirty tracked file(s) before the pull (rc %d/%d): %s %s" % (
            len(paths), rc, rc2, msg, msg2)
    except (OSError, subprocess.SubprocessError) as e:
        return 0, "heal_dirty: %s" % e


def boot_time():
    """-> epoch seconds of this (WSL) boot, from /proc/stat btime; None if unreadable."""
    try:
        with open("/proc/stat") as f:
            for ln in f:
                if ln.startswith("btime "):
                    return float(ln.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return None


def clear_boot_stale_index_lock(logdir):
    """RIMMANDRAKE_FIX_STEVE_WORKER_STALE_INDEX_LOCK_BEFORE_PULL: a reboot mid-git left .git/index.lock in the runner
    clone, and the next job's `pull --ff-only` refused SYNC and paused the lane (J20261120T213808Z-8aa00b).
    Runner clone only: a lock OLDER THAN THIS BOOT is removed, since no process that held it survived the reboot.
    A lock from this boot is left alone (a live git may hold it); the pull then refuses as before.
    -> message ('' when nothing was done). Never raises; a removal is recorded in logdir/index_lock_cleared.txt."""
    if not runner_clone_only():
        return ""
    lock = os.path.join(CLONE, ".git", "index.lock")
    try:
        mtime = os.path.getmtime(lock)
    except OSError:
        return ""
    bt = boot_time()
    if bt is None or mtime >= bt:
        return ""
    try:
        os.remove(lock)
        msg = "removed .git/index.lock left from before this boot (lock %s, boot %s)" % (
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime)), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(bt)))
    except OSError as e:
        return "pre-boot index.lock could not be removed: %s" % e
    try:
        if logdir:
            os.makedirs(logdir, exist_ok=True)
            write_text(os.path.join(logdir, "index_lock_cleared.txt"), msg)
    except OSError:
        pass
    return msg


NO_COMMIT_HOOK = """#!/bin/sh
# written by infrastructure/stevedesktop/worker.py (STEVE_RUNNER_CLONE_ENFORCE_NO_LLM_WRITES)
echo "REFUSED: this is the test lane's pinned runner clone; a commit here makes the next pull refuse and stops the lane." >&2
echo "Work in your own clone: git clone git@github.com:Lmandrake/RimMandrake.git ~/rm/<name>" >&2
exit 1
"""


def guard_clone():
    """A commit in a runner clone is refused (its history may only fast-forward). -> message; never raises."""
    if not runner_clone_only():
        return ""
    hook = os.path.join(CLONE, ".git", "hooks", "pre-commit")
    try:
        if read_text(hook) == NO_COMMIT_HOOK.strip() or read_text(hook) == NO_COMMIT_HOOK:
            return ""
        os.makedirs(os.path.dirname(hook), exist_ok=True)
        write_text(hook, NO_COMMIT_HOOK)
        os.chmod(hook, 0o755)
        return "pre-commit guard written"
    except OSError as e:
        return "pre-commit guard could not be written: %s" % e


def ready_for_pull(d):
    """The start's steps before `pull --ff-only`, each of which once refused a job SYNC: a leftover pin, dirt on
    main, and a reboot's leftover index.lock."""
    clear_boot_stale_index_lock(d)  # first: a reboot mid-git leaves index.lock, and the two checkouts below need the index
    unpin(d)    # a crashed attempt can leave the clone on its detached pin: pull needs main
    heal_dirty(d)   # dirt left on main by the last attempt would make the pull refuse SYNC
    guard_clone()   # and a commit made there would make it refuse for good


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
    errs = contract_errors(res)
    if errs:    # never publish what the contract refuses, and never crash here (finalize_dead calls this again)
        S.dump(res, os.path.join(d, "result.refused.json"))
        bad = res
        res = base_result(bad.get("job"), bad.get("attempt"), bad.get("runner_sha"))
        res.update(outcome="INVALID", cause="HARNESS", started=bad.get("started") or res["started"],
                   finished=S.utcnow(), note=("the worker's result broke contracts.models.TestqResult (kept as "
                                               "result.refused.json): " + "; ".join(errs))[:3000])
        res["counts"] = S.count_verdicts(res["rows"])
        errs = contract_errors(res)
        if errs:
            raise S.SchemaError("even the INVALID/HARNESS stand-in breaks TestqResult: " + "; ".join(errs))
    S.dump(res, os.path.join(d, "result.json"))
    S.dump(res, p("outbox", res["attempt"] + ".json"))


# ---------------------------------------------------------------- start

def cmd_start(retry):
    global S
    job = json.load(sys.stdin)
    refresh_schema = False
    try:
        job = S.validate_job(job)
    except S.SchemaError:
        if (os.environ.get("TESTQ_SKIP_PULL") == "1" or not isinstance(job, dict)
                or not isinstance(job.get("id"), str) or not S.JOB_ID_RE.fullmatch(job["id"])):
            raise
        refresh_schema = True
    try:        # admit nothing whose result could not be checked: the job stays pending and the error is logged
        contract_models()
    except ContractMissing as e:
        return out({"error": str(e), "state": "contract_missing"}, 1)
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

        def refuse(cause, note):
            rc, head = git("rev-parse", "HEAD")
            res = base_result(job["id"], aid, head if rc == 0 else None)
            res.update(outcome="REFUSED", cause=cause, note=note)
            publish_result(d, res)
            return out({"attempt": aid, "state": "finished", "outcome": "REFUSED", "cause": cause})

        ready_for_pull(d)
        if os.environ.get("TESTQ_SKIP_PULL") != "1":
            if refresh_schema:
                if os.path.exists(os.path.join(CLONE, ".git", "index.lock")):
                    return refuse("SYNC", "runner clone still holds index.lock before schema refresh")
                if git("symbolic-ref", "-q", "HEAD") != (0, "refs/heads/main"):
                    return refuse("SYNC", "runner clone could not be put on main before schema refresh")
                rc, msg = git("status", "--porcelain", "--untracked-files=no")
                if rc:
                    return refuse("SYNC", "could not read runner status before schema refresh: " + msg[-300:])
                if msg:
                    return refuse("SYNC", "runner clone is still dirty before schema refresh: " + msg[-300:])
            rc, msg = git("pull", "-q", "--ff-only", "origin", "main")
            if rc != 0:
                return refuse("SYNC", "runner pull failed: " + msg[-300:])
            # STEVE_LANE_UNSTICK_BRAKED_UNOWNED_8EB8: the contract was loaded BEFORE this pull, while spawn copies the
            # worker and schema from disk AFTER it; a landing that adds a result field then had the new worker write
            # it and the old contract refuse it (the 07:33Z canary). The outer copy carries the pulled contract.
            before = list(_MODELS)
            _MODELS.clear()
            try:
                contract_models()
            except ContractMissing as e:
                _MODELS[:] = before     # the refusal itself is checked by the contract that did load
                return refuse("SYNC", "the pulled contract does not load: %s" % str(e)[-300:])
            if refresh_schema:
                path = os.path.join(CLONE, "src", "RimMandrake", "Utils", "testq", "schema.py")
                try:
                    pulled = importlib.util.module_from_spec(importlib.util.spec_from_file_location("schema", path))
                    with open(path, "rb") as f:   # read the pulled source even if a cached .pyc appears current
                        exec(compile(f.read(), path, "exec"), pulled.__dict__)
                except (ImportError, OSError, SyntaxError) as e:
                    return refuse("SYNC", "the pulled job schema does not load: %s" % str(e)[-300:])
                sys.modules["schema"] = S = pulled
                try:
                    job = S.validate_job(job)
                except S.SchemaError as e:
                    return refuse("SCHEMA", str(e))
        repair_reset_list(d)    # the last attempt may have died before its own repair
        head = git("rev-parse", "HEAD")[1]
        if git("merge-base", "--is-ancestor", job["source_sha"], "HEAD")[0] != 0:
            res = base_result(job["id"], aid, head)
            res.update(outcome="REFUSED", cause="SOURCE_SHA_MISSING",
                       note="runner HEAD %s does not contain source_sha %s" % (head[:10], job["source_sha"]))
            publish_result(d, res)
            return out({"attempt": aid, "state": "finished", "outcome": "REFUSED", "cause": "SOURCE_SHA_MISSING"})
        pre = preflight_job(job, d)     # RIMMANDRAKE_TESTQ_PREFLIGHT_REFUSE_BEFORE_THE_GAME: what would end INVALID is refused here
        if pre and pre["refused"]:
            res = base_result(job["id"], aid, head)
            res.update(outcome="REFUSED", cause="PREFLIGHT", note=PF.note_of(pre))
            publish_result(d, res)
            return out({"attempt": aid, "state": "finished", "outcome": "REFUSED", "cause": "PREFLIGHT"})
        # the attempt runs at EXACTLY source_sha, not at whatever newer HEAD happens to contain it (bolt 1)
        want = git("rev-parse", "--verify", job["source_sha"] + "^{commit}")[1]
        capture_outer()     # before the pin: with CLONE == RUNNER it rewrites these very files
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


# `init && up --wait`: rw_game.sh waits up to RW_UP_WAIT_S (1200 s) for the bridge, after init and Steam. This outer limit
# guards a load command that hangs past its own wait (selftest_rw_game_up_wait.py keeps the two in order).
LOAD_TIMEOUT_S = 6300  # budget: danger=a hung game load holds the lane; longest=602s (testq done records, phase_s, 14 days to 2026-11-24)
PF = None   # the preflight module, once preflight_job has imported it


def preflight_job(job, d):
    """preflight.check on the pulled tree (a worker older than the module, or a check that crashed, lets the job
    through); what it fixed or skipped is written to the attempt's preflight.json for the result note."""
    global PF
    try:
        import preflight as PF      # noqa: PLW0603 - beside this worker; the outer copy is not involved here
    except ImportError:
        return None
    try:
        res = PF.check(job, RUNNER, clone=CLONE)
    except Exception as e:      # noqa: BLE001 - a preflight that crashes must not stop a job
        sys.stderr.write("worker: preflight crashed: %s: %s\n" % (type(e).__name__, str(e)[:200]))
        return None
    S.dump(res, os.path.join(d, "preflight.json"))
    return res


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


VERDICT_RX = re.compile(r"\b(FAIL|PASS)\b")
UNCAUGHT_RX = re.compile(r"^(?:[A-Za-z_][\w.]*\.)?[A-Za-z_]\w*(?:Error|Exception|Interrupt)(?::.*)?$")


def proof_verdict(rc, tail):
    """A live-proof line's (verdict, crash) from its exit code and output tail: 0 PASS, 1 FAIL, else UNMEASURED. An exit
    1 whose output ends in an uncaught Python exception (the last traceback's unindented exception line, with no PASS or
    FAIL word after it; an exit hook's line may follow) is a crash: UNMEASURED,
    could not look, never FAIL (2026-11-23: a missing numpy under SteveDesktop's Windows python read FAIL,
    J20261123T115429Z-9dd04f). A FAIL line printed after a quoted traceback is still the script's FAIL."""
    if rc == 0:
        return "PASS", None
    if rc == 1:
        lines = (tail or "").splitlines()
        tb = [i for i, x in enumerate(lines) if x.startswith("Traceback (most recent call last)")]
        if tb:
            after = lines[tb[-1] + 1:]
            exc = [i for i, x in enumerate(after) if UNCAUGHT_RX.match(x.rstrip())]     # unindented: the exception line
            if exc and not any(VERDICT_RX.search(x) for x in after[exc[0] + 1:]):        # exit hooks may print after it
                return "UNMEASURED", after[exc[0]].strip()[:160]
        return "FAIL", None
    return "UNMEASURED", None


def kept_env_keys(environ):
    """The environment a detached attempt keeps: the RM_/TESTQ_/STEVE_/RIMFLOW_ seams, and GABP_ (Steve2's bridge port
    and token, from `game_instance.py env b`; without them its modcheck would knock on Steve1's 5174)."""
    return [k for k in environ if k != "TESTQ_UNIT" and k.startswith(("RM_", "TESTQ_", "STEVE_", "RIMFLOW_", "GABP_"))
            or k in ("PATH", "HOME", "USER", "LANG", "WSLENV", "WSL_DISTRO_NAME")]


def staged_companion():
    """Where a FRESH companion waits to be installed: TESTQ_COMPANION_INBOX (Steve2 reads Steve1's inbox, the one the
    stager fills), else this worker's own TESTQ_HOME/companion."""
    inbox = os.environ.get("TESTQ_COMPANION_INBOX")
    return os.path.join(inbox, CI.DLL_NAME) if inbox else p("companion", CI.DLL_NAME)


def spawn(aid, d):
    """Detach `worker.py _run <attempt>`: a transient systemd user unit, else a new session."""
    # run a COPY of this (main-checkout) worker, not __file__ inside the clone that is about to be pinned: a pin older
    # than this code would otherwise run ITS worker.py and never unpin
    outer = p("outer")
    os.makedirs(outer, exist_ok=True)
    if not _OUTER:
        capture_outer()
    for name, data in _OUTER.items():
        with open(os.path.join(outer, name), "wb") as f:
            f.write(data)
    contract_models()           # loaded by cmd_start before the pin; a no-op then
    with open(os.path.join(outer, OUTER_MODELS), "wb") as f:
        f.write(_MODELS[1])
    os.environ["TESTQ_REPO"] = RUNNER
    argv = [sys.executable, os.path.join(outer, "worker.py"), "_run", aid]
    keep = kept_env_keys(os.environ)
    unit = "testq-" + re.sub(r"[^A-Za-z0-9_-]", "_", aid)
    if shutil.which("systemd-run") and os.environ.get("TESTQ_NO_SYSTEMD") != "1":
        r = subprocess.run(["systemd-run", "--user", "--collect", "--quiet", "--unit", unit,
                            "--property=KillMode=control-group", "--working-directory", RUNNER]
                           + ["--setenv=%s=%s" % (k, os.environ[k]) for k in keep]
                           + ["--setenv=TESTQ_UNIT=" + unit, "--"] + argv,
                           # budget: danger=a hung systemd-run holds the spawn of the worker, and so the lane; never reached in
                           # budget: the 14 days to 2026-11-24; no record of its run
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
# STEVE_LANE_UNSTICK_BRAKED_UNOWNED_8EB8: this worker owns its game, so a modcheck run refused because the running load is
# not the list it composed leaves ModsConfig on that list (MODCHECK_STALE_KEEP_COMPOSED) and the worker restarts onto it.
RUN_BASE = ("export MODCHECK_SKIP_DEPLOY=1 MODCHECK_STALE_KEEP_COMPOSED=1 "
            "WSLENV=${WSLENV:+$WSLENV:}MODCHECK_SKIP_DEPLOY:MODCHECK_STALE_KEEP_COMPOSED; "
            # -X faulthandler: 0xC0000005 reaches WSL as "exit 5" with no output (MODCHECK_DIAGNOSE_EXIT_FIVE_NO_SHEET)
            "python.exe -X faulthandler src/RimMandrake/Utils/modcheck/cli.py run --drivers on")

# An exact-tier job (profile tier:<name>, LANE_TIER_WIRE_A_WHOLE_LIST_LOAD; owner by card 2026-11-05: SteveDesktop is the
# exact-tier host): the tier is loaded as the WHOLE list, the running load is checked against it, then the item's
# live-proof lines run. Tests override both with TESTQ_CMD_TIERCHECK / TESTQ_CMD_TIERSWAP (the tier is appended).
TIER_CHECK = "python.exe src/RimMandrake/Utils/testq/tier_load.py check --tier"
TIER_SWAP = "python3 src/RimMandrake/Utils/modset_builder.py --apply --not-my-bridge %s --tier"
PROOFS_DIR = os.path.join("infrastructure", "state", "live_proofs")
# STEVE_MODSCONFIG_REPAIR_CRASH_RESETS_LIST: a load that crashes makes RimWorld reset ModsConfig to Core+DLC, and every tier
# swap then refused it as "neither tier nor before-copy" until a hand restore. It runs only with the clone on main (before
# the pin, after the unpin), because a job's source_sha may predate the flag. Tests override it with TESTQ_CMD_RESETREPAIR.
RESET_REPAIR = ("python3 src/RimMandrake/Utils/modset_builder.py --repair-reset --not-my-bridge "
                "'testq on SteveDesktop: the runner owns this machine list'")
RESET_REPAIR_LOG = "modsconfig_repair.log"
# A stage-6 checks job (selector.checks): each check's own script, run and read by stage6_checks.py at source_sha. A test
# overrides both with TESTQ_CMD_CHECKS / TESTQ_CMD_PROOFBUILD (the arguments are appended).
CHECKS_RUN = "python3 src/RimMandrake/Utils/testq/stage6_checks.py run"
PROOF_BUILD = "python3 src/RimMandrake/Utils/testq/proof_build.py"


def repair_reset_list(d):
    """Put the before-copy back if a crash reset the live list; never raises, and a refusal costs the job nothing (the
    swap itself refuses by name). Only SteveDesktop's runner owns its list: the archmagi lane's is the owner's. The
    account lands in the attempt's RESET_REPAIR_LOG."""
    if not STEVE_LANE:
        return
    cmd = os.environ.get("TESTQ_CMD_RESETREPAIR")
    if not cmd and os.environ.get("TESTQ_SKIP_PULL") == "1":    # a test's worker never touches this machine's real list
        return
    try:
        r = subprocess.run(["bash", "-c", cmd or RESET_REPAIR], cwd=CLONE, stdin=subprocess.DEVNULL,
                           # budget: danger=a hung repair of the mod list holds the lane's reset; never reached in the 14 days
                           # budget: to 2026-11-24; no record of its run
                           capture_output=True, text=True, timeout=120)
        text = "exit %s: %s" % (r.returncode, ((r.stdout or "") + (r.stderr or "")).strip())
    except (OSError, subprocess.SubprocessError) as e:
        text = "could not run: %s" % e
    try:
        with open(os.path.join(d, RESET_REPAIR_LOG), "a") as f:
            f.write("%s %s\n" % (S.utcnow(), text))
    except OSError as e:
        sys.stderr.write("worker: %s unwritable: %s; it said %s\n" % (RESET_REPAIR_LOG, e, text))


def reset_repair_note(d):
    """The lines of this attempt's repair log that repaired something or refused to, for the result's note."""
    found = []
    for line in (read_text(os.path.join(d, RESET_REPAIR_LOG)) or "").splitlines():
        m = re.search(r"(REPAIRED|REFUSING --repair-reset).*", line)
        if m:
            found.append(m.group(0))
    return "; ".join(found)

# a mod with no src folder answers []: deploy_custom_mods.py refuses that name itself, loudly, in the deploy step; a
# tree with no modcheck runner composes nothing (modcheck run fails there by itself), so it answers [] too
CLOSURE_PY = ("import glob, json, os, sys; M = 'src/RimMandrake/Utils/modcheck'; "
              "os.path.isfile(M + '/runner.py') or (print('[]'), sys.exit(0)); "
              "sys.path.insert(0, M); import runner; f = getattr(runner, 'deploy_closure', None); "
              "known = glob.glob('src/*/%s/About/About.xml' % sys.argv[1]) or runner.composed_into(sys.argv[1]); "
              "print(json.dumps(f(sys.argv[1]) if f and known else []))")


def deploy_closure(mod, clone=None):
    """RELAPSE_STEVE_FIX_DIED_TWICE: the mods of ours that the job's composed list names besides `mod`, read from the
    job's own tree (modcheck runner.deploy_closure; a tree older than it answers []). modcheck composes a mod's hard
    dependencies and tier closure, and RimWorld drops an id whose folder is not deployed: TerminalBiomes jobs ended
    INVALID/HARNESS stale_load `not loaded: mandrake.rm.luminouspigment` (2026-11-04) because only the composed biomes
    were deployed. Raises on any failure: guessing an empty closure is the defect itself."""
    r = subprocess.run([sys.executable, "-c", CLOSURE_PY, mod], cwd=clone or CLONE, capture_output=True, text=True,
                       # budget: danger=a hung closure read holds the attempt, and so the lane; never reached in the 14 days to
                       # budget: 2026-11-24; no record of its run
                       timeout=120)
    if r.returncode != 0:
        raise RuntimeError("exit %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[-200:]))
    out = json.loads(r.stdout.strip().splitlines()[-1])
    if not isinstance(out, list) or not all(isinstance(m, str) for m in out):
        raise RuntimeError("not a list of mod names: %r" % (out,))
    return out



def situational_digest(mod, summary):
    """A situational job's suite digest for its result (situational_rerun.digest, plus which surprise evidence this host
    lacks: the sidecars stay on this machine, so the rollup cannot look). A digest that cannot be made says so by name."""
    try:
        sys.path.insert(0, os.path.join(CLONE, "src", "RimMandrake", "Utils", "modcheck", "live_queue"))
        import situational_rerun as R
        d = R.digest(mod, summary)
        d["evidence_missing"] = ["%s %s" % (s["chain"], p) for s in d["surprises"] for p in (s.get("sidecar"), s.get("png"))
                                 if p and not R.evidence_present(p)]
        d["evidence_missing"] += ["%s sidecar" % s["chain"] for s in d["surprises"] if not s.get("sidecar")]
        return d
    except Exception as e:                                      # noqa: BLE001
        return {"mod": mod, "digest_error": "%s: %s" % (type(e).__name__, e)}


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
        self.companion_state = None     # companion(): the JawaBench DLL's source-hash verdict, attested in deployed
        self.liveness_unknown = None
        self.child = None
        self.stop = threading.Event()
        self.state_lock = threading.Lock()  # beat(): the main thread and the heartbeat both write state.json
        self.log = open(os.path.join(self.d, "worker.log"), "a", encoding="utf-8")

    def say(self, msg):
        self.log.write("%s %s\n" % (S.utcnow(), msg))
        self.log.flush()

    def beat(self):
        # One writer at a time, the record built inside the lock: a phase change landing on a heartbeat tick crashed an
        # attempt with no verdict, and on drvfs two renames onto one target refuse each other (HARNESS_REPAIR_CAUSE_B338C64C).
        with self.state_lock:
            S.dump({"phase": self.phase, "ts": S.utcnow(), "pid": os.getpid(), "runner_sha": self.res["runner_sha"],
                    "retries": self.res["retries"], "phase_s": dict(self.res["phase_s"]),
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
        # RIMMANDRAKE_FIX_STEVE_LANE_REFUSES_JOBS_BRIDGE_IDLE_SILENT: the lane is ssh-started with no seat env, and the
        # restart's `game down` asks `rimflow bridge idle`, which refuses a caller it cannot name (exit 2, 2026-11-20).
        # The worker is the testq RUNNER seat unless a seat is already named (a test or the owner's own export wins).
        env = dict(os.environ)
        if not (env.get("RIMFLOW_SEAT") or env.get("AGENT_SEAT")):
            env["RIMFLOW_SEAT"] = "RUNNER"
        self.child = subprocess.Popen(["bash", "-c", cmd], cwd=CLONE, stdin=subprocess.DEVNULL, stdout=logf,
                                      stderr=subprocess.STDOUT, start_new_session=True, env=env)
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
                    # budget: danger=a child that ignores SIGTERM holds the attempt; SIGKILL follows; its reach leaves no
                    # budget: record; no record of its run
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
        return self.deploy_release() and self.deploy_proof()

    def deploy_proof(self):
        """A job with proof_build: each named mod's PROOF DLL over the game's release DLL, the game down, the clone's
        Assemblies untouched (proof_build.py). The next job's deploy plan sees the drift and puts the release back."""
        for m in self.job.get("proof_build") or []:
            # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane; never
            # budget: reached in the 14 days to 2026-11-24; no record of its run
            rc, tail = self.sh(self.cmd_down(), timeout=300)
            if rc != 0:
                return self.fail("INVALID", "DEPLOY", "game down before the proof build failed: " + tail)
            cmd = os.environ.get("TESTQ_CMD_PROOFBUILD") or PROOF_BUILD
            rc, tail = self.sh("%s --mod %s --mods-dir %s" % (cmd, shlex.quote(m), shlex.quote(self.mods_dir())),
                               log_name="proof_build.log", timeout=10800)  # budget: class=deploy
            if rc != 0:
                return self.fail("INVALID", "DEPLOY", "proof build of %s failed: %s" % (m, tail[-300:]))
            self.memo_mods = None       # the game's DLL is no longer what any memo recorded
        return True

    def deploy_release(self):
        override = os.environ.get("TESTQ_CMD_DEPLOY")
        mods = self.deploy_mods()
        if not mods:        # an exact-tier job whose build changed no mod: the tier's own trees stand as deployed
            self.say("deploy: the job names no mod to deploy")
            return self.companion()
        try:
            extra = [] if S.is_proofs(self.job) else deploy_closure(self.job["mod"])
        except Exception as e:  # noqa: BLE001 - a deploy that cannot name its closure would drop mods silently
            return self.fail("INVALID", "DEPLOY", "deploy closure of %s failed: %s: %s"
                             % (self.job["mod"], type(e).__name__, str(e)[:200]))
        if extra:
            self.say("deploy: with the mods of ours its composed list names: " + ", ".join(extra))
        mods += [m for m in extra if m not in mods]
        if override:
            rc, tail = self.sh(override + " " + " ".join(shlex.quote(m) for m in mods), timeout=10800)  # budget: class=deploy
            if rc != 0 and refused_line(tail):     # a lane that may not deploy here (archmagi_phases.py): not a fault
                return self.fail("REFUSED", "DEPLOY", refused_line(tail))
            return (rc == 0 or self.fail("INVALID", "DEPLOY", "deploy failed: " + tail)) and self.companion()
        if self.memo_hit(mods):
            return self.companion()
        # a folded source (Pyrelands) or the composed target (RimMandrake.Biomes) is `--compose biomes`, never `--mod`
        args = " ".join(f + " " + shlex.quote(v) for f, v in S.deploy_flags(mods, os.path.join(RUNNER, "src")))
        plan = "python3 src/RimMandrake/Utils/deploy_custom_mods.py " + args
        rc, _ = self.sh(plan + " > %s 2>&1" % shlex.quote(os.path.join(self.d, "deploy_plan.txt")), timeout=10800)  # budget: class=deploy
        if rc == 0:
            self.say("deploy: no drift, game kept")
            return self.companion()
        text = read_text(os.path.join(self.d, "deploy_plan.txt")) or ""
        if "Drift found" not in text:
            return self.fail("INVALID", "DEPLOY", "deploy plan failed: " + text[-300:])
        # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane; never
        # budget: reached in the 14 days to 2026-11-24; no record of its run
        rc, tail = self.sh(self.cmd_down(), timeout=300)
        if rc != 0:
            return self.fail("INVALID", "DEPLOY", "game down before deploy failed: " + tail)
        rc, tail = self.sh(plan + " --apply", timeout=10800)  # budget: class=deploy
        return (rc == 0 or self.fail("INVALID", "DEPLOY", "deploy --apply failed: " + tail)) and self.companion()

    def memo_state(self, mods):
        """-> (deploy_memo module, memo path, key, game signature) or None: TESTQ_DEPLOY_MEMO=1, and only on a lane that
        deploys itself (a TESTQ_CMD_DEPLOY lane has its own rules). Cached for the attest that follows."""
        if getattr(self, "_memo", 0) != 0:
            return self._memo
        self._memo = None
        try:
            import deploy_memo as M
            if M.enabled(home=HOME) and not os.environ.get("TESTQ_CMD_DEPLOY"):
                mp = os.path.join(HOME, "deploy_memo.json")
                self._memo = (M, mp, M.key_for(S, CLONE, self.job["source_sha"], mods, os.path.join(RUNNER, "src")),
                              None)
        except Exception as e:      # noqa: BLE001 - a memo that cannot run is no memo
            self.say("deploy memo unavailable: %s: %s" % (type(e).__name__, str(e)[:120]))
        return self._memo

    def memo_hit(self, mods):
        """Nothing deployed changed since the previous job: skip the plan, keep its attest record. -> bool."""
        st = self.memo_state(mods)
        if not st or st[2] is None:
            return False
        M, mp, key, _ = st
        sig = M.game_sig(self.mods_dir(), key["mods"])
        hit = M.lookup(mp, key, sig)
        _, folded, _c = S.deploy_catalog(os.path.join(RUNNER, "src"))
        if not hit or set(hit[0]) != {folded.get(m, m) for m in self.deploy_mods()}:
            return False        # the attest record must cover exactly the mods THIS job attests
        self.memo_mods = hit[0]
        self.say("deploy: UNCHANGED since %s (same sources, game files untouched): plan and attest hashing skipped" % hit[1])
        self.res["deploy_memo"] = {"hit": True, "since": hit[1]}
        return True

    def deploy_mods(self):
        """The mods this attempt deploys and attests: the job's mod and its --deploy list; an exact-tier job's `mod` is
        its item id, so only its deploy list (the mods the item's build changed)."""
        own = [] if S.is_proofs(self.job) else [self.job["mod"]]
        return own + [m for m in self.job.get("deploy") or [] if m not in own]

    def companion_dir(self):
        """The game's BridgeTools/JawaBench: the sibling of the Mods folder attest hashes (TESTQ_COMPANION_DIR overrides)."""
        return os.environ.get("TESTQ_COMPANION_DIR") or os.path.join(os.path.dirname(os.path.normpath(
            self.mods_dir())), "BridgeTools", "JawaBench")

    def companion(self):
        """STEVE_COMPANION_FIX_DLL_STALE_NO_PRIORITIES: the JawaBench companion must be compiled from the job's sources.

        J20261029T211737Z-3af227 ran droid_dig on a companion older than jawa/set_work_priority's manualPrioritiesOn
        (1b5adb3c5a): both rows read UNMEASURED/HARNESS, and nothing in deploy or attest looked at the companion at
        all. Now the DLL's embedded source hash (bridgetools/companion_identity.py) is compared with the hash of the
        companion sources at the job's source_sha. Not FRESH (stale, unstamped, missing): a fresh DLL staged in
        TESTQ_HOME/companion/ (sync_test_mods.py --apply puts it there) is installed with the game DOWN, since the
        game holds the DLL mapped and only discovers companions at start; with none staged, or a lane that may not
        stop the game, the attempt ends before load - INVALID/DEPLOY (REFUSED/DEPLOY on a lane that never deploys)
        naming the DLL - instead of running rows that can only read UNMEASURED."""
        target = os.path.join(self.companion_dir(), CI.DLL_NAME)
        v = CI.verdict(target, CLONE, self.job["source_sha"])
        self.companion_state = v
        if v["state"] == "FRESH":
            self.say("companion: " + CI.describe(v))
            return True
        never = not STEVE_LANE and os.environ.get("TESTQ_CMD_DEPLOY")    # archmagi_phases: may not deploy
        outcome = "REFUSED" if never else "INVALID"
        if v["state"] == "UNMEASURED":
            return self.fail(outcome, "DEPLOY", "companion check UNMEASURED: cannot hash %s at source_sha %s"
                             % (CI.SRC_REL, self.job["source_sha"][:10]))
        staged = staged_companion()
        sv = CI.verdict(staged, CLONE, self.job["source_sha"], want=v["want"])
        if sv["state"] != "FRESH" or never:
            # the note is clipped to its last 400 chars (fail): state and DLL name first, the paths go to the log
            self.say("companion: game copy " + CI.describe(v))
            self.say("companion: staged copy " + CI.describe(sv))
            return self.fail(outcome, "DEPLOY", "companion %s %s not built from this job's sources (embedded %s, want "
                             "%s, staged copy %s); %s" % (
                                 v["state"], CI.DLL_NAME, (v["embedded"] or "none")[:12], v["want"][:12], sv["state"],
                                 "this lane never deploys it" if never else
                                 "fix: build.py --gm at the job's sha, then sync_test_mods.py --apply on Archmagi "
                                 "(stages it in TESTQ_HOME/companion/; the next job installs it with the game down)"))
        # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane; never
        # budget: reached in the 14 days to 2026-11-24; no record of its run
        rc, tail = self.sh(self.cmd_down(), timeout=300)
        if rc != 0:
            return self.fail("REFUSED" if refused_line(tail) else "INVALID", "DEPLOY",
                             "stale companion %s; game down before installing the staged one failed: %s"
                             % (target, refused_line(tail) or tail))
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            tmp = target + ".testq.part"
            shutil.copy2(staged, tmp)
            os.replace(tmp, target)
        except OSError as e:
            return self.fail("INVALID", "DEPLOY", "installing the staged companion over %s failed: %s" % (target, e))
        v2 = CI.verdict(target, CLONE, self.job["source_sha"], want=v["want"])
        self.companion_state = dict(v2, installed_from=staged, replaced=v)
        if v2["state"] != "FRESH":
            return self.fail("INVALID", "DEPLOY", "installed the staged companion, still not fresh: " + CI.describe(v2))
        self.say("companion: was %s, installed the staged one with the game down: %s" % (v["state"], CI.describe(v2)))
        return True

    def cmd_down(self):
        return os.environ.get("TESTQ_CMD_DOWN") or GAME + " down"

    def load(self):
        cmd = os.environ.get("TESTQ_CMD_LOAD") or "%s init && %s up --wait" % (GAME, GAME)
        since = S.utcnow()
        rc, tail = self.sh(cmd, timeout=LOAD_TIMEOUT_S)
        if rc != 0 and refused_line(tail):         # e.g. archmagi: no game running, and the lane never launches one
            return self.fail("REFUSED", "LOAD", refused_line(tail))
        if rc != 0:
            return self.fail("INVALID", "LOAD", "game load failed: " + tail)
        m = fresh_pid_line(tail)
        if not m:
            kept = last_pid_line(r"already running \(pid \d+\)", tail)
            wedged = kept and self.kept_game_wedged()
            overgrown = kept and not wedged and self.kept_game_overgrown(tail)
            # RIMMANDRAKE_RESTART_GAME_AFTER_MAPDATA_TIMEOUT_THREE_JOBS_BURNED: a game that answers the bridge, is young
            # and holds few maps can still be unable to make one ever again. Last of the three, because it is the only
            # one whose evidence a wedged or overgrown game would not even be asked for.
            unmappable = kept and not wedged and not overgrown and self.kept_game_unmappable(tail)
            if wedged or overgrown or unmappable:
                # STEVE_LANE_FIX_WEDGED_KEPT_GAME: 2026-10-30 08:10Z the kept game (pid 7460, 17 h old, 27 maps, 21 GB)
                # stopped answering; `up --wait` only sees the process, so five jobs each reused it (load 1 s), died in
                # ensure_playing_map on the same 30 s timeout, braked the filler and left the lane dark 14 h. We hold
                # the guard: restart it. A wedged game cannot run a job, so this needs no once-only memory; an overgrown
                # one comes back fresh, under both limits.
                self.res["bounced_unresponsive" if wedged else "recycled_kept_game"] = (wedged or overgrown
                                                                                        or unmappable)
                why = ("kept game does not answer the bridge (%s)" % wedged if wedged
                       else "kept game %s" % (overgrown or unmappable))
                self.say(why + ": restarting it")
                if wedged:
                    self.dump_game("wedged")
                    self.keep_game_log("Player_wedged.log")
                if unmappable:
                    # the next cold start overwrites Player.log and the one after takes its -prev copy (keep_game_log):
                    # this is the only chance to read why the process could not make a map
                    self.keep_game_log("Player_unmappable.log")
                # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane;
                # budget: never reached in the 14 days to 2026-11-24; no record of its run
                rc, tail = self.sh(self.cmd_down(), timeout=300)
                if rc != 0:
                    return self.fail("REFUSED" if refused_line(tail) else "INVALID", "LOAD",
                                     "%s; game down failed: %s" % (why, refused_line(tail) or tail))
                since = S.utcnow()
                rc, tail = self.sh(cmd, timeout=LOAD_TIMEOUT_S)
                if rc != 0:
                    return self.fail("INVALID", "LOAD", "game reload failed, %s: %s" % (why, tail))
                m = fresh_pid_line(tail)
                if not m:
                    return self.fail("INVALID", "LOAD", "restarted the game, %s, but load did not report a fresh "
                                     "process: %s" % (why, tail[-200:]))
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
                # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane;
                # budget: never reached in the 14 days to 2026-11-24; no record of its run
                rc, tail = self.sh(self.cmd_down(), timeout=300)
                if rc != 0:
                    return self.fail("REFUSED" if refused_line(tail) else "INVALID", "LOAD",
                                     "stale bridge marker(s) %s on a kept game; game down failed: %s"
                                     % (" ".join(stale), refused_line(tail) or tail))
                since = S.utcnow()
                rc, tail = self.sh(cmd, timeout=LOAD_TIMEOUT_S)
                if rc != 0:
                    return self.fail("INVALID", "LOAD", "game reload after the marker restart failed: " + tail)
                m = fresh_pid_line(tail)
                if not m:
                    return self.fail("INVALID", "LOAD", "restarted the game for stale bridge marker(s) %s, but load "
                                     "did not report a fresh process: %s" % (" ".join(stale), tail[-200:]))
        if m:
            self.clear_moot_markers(since, m.group(1))
            if self.res.get("bounced_for_markers") is not None:   # remember only the ones the restart did not clear
                cleared = set(self.res.get("moot_markers") or [])
                S.dump({c: self.aid for c in self.res["bounced_for_markers"] if c not in cleared},
                       p("marker_bounces.json"))
        alive = m or last_pid_line(r"already running \(pid (\d+)\)", tail)
        self.game_pid = alive.group(1) if alive else None
        return True

    def bridge_cmd(self):
        return os.environ.get("TESTQ_CMD_BRIDGE") or "python.exe src/RimMandrake/Utils/rimbridge_client.py"

    def kept_game_wedged(self):
        """-> why the game load kept does not answer the bridge, or None (it answers, or the probe cannot tell).

        `rw_game.sh up --wait` proves a process, not a game that serves calls. A read-only call answered, or a refused
        one, is a live bridge; only a call that ran and got no answer, twice, is a wedged game. A probe that could not
        run at all (no client here: rc 126/127) keeps the old behaviour: the job's own calls will say if it matters."""
        if not STEVE_LANE and not os.environ.get("TESTQ_CMD_PROBE"):
            return None                     # the archmagi lane's kept game is the owner's: never probed, never stopped
        cmd = os.environ.get("TESTQ_CMD_PROBE") or (self.bridge_cmd()
                                                    + " --timeout %d --call rimworld/get_ui_state" % PROBE_TIMEOUT_S)
        why = None
        for attempt_no in (1, 2):
            if attempt_no == 2:
                time.sleep(float(os.environ.get("TESTQ_PROBE_GAP_S") or PROBE_GAP_S))
            try:
                r = subprocess.run(["bash", "-c", cmd], cwd=RUNNER, capture_output=True, text=True,
                                   timeout=PROBE_TIMEOUT_S + 30)
            except OSError as e:
                self.say("could not probe the kept game: %s" % e)
                return None
            except subprocess.TimeoutExpired:
                why = "bridge probe hung past %ds" % (PROBE_TIMEOUT_S + 30)
                continue
            if r.returncode == 0:
                return None
            if r.returncode in (126, 127):
                self.say("could not probe the kept game: rc %s" % r.returncode)
                return None
            why = "bridge probe rc %s: %s" % (r.returncode, ((r.stderr or "") + (r.stdout or "")).strip()[-160:])
        return why

    def kept_game_overgrown(self, load_tail):
        """-> why a kept game (it answered the probe) is past a limit, or None. Age comes from `rw_game.sh up`'s status
        line (age_s=), the map count from a read-only call. Either unreadable decides nothing: the other limit stands."""
        if not STEVE_LANE and not os.environ.get("TESTQ_CMD_MAPS"):
            return None                     # the archmagi lane's kept game is the owner's: never probed, never stopped
        age = re.search(r"\bage_s=(\d+)", load_tail)
        if age and int(age.group(1)) >= MAX_GAME_AGE_S:
            return "is %.1f h old (limit %.1f h)" % (int(age.group(1)) / 3600, MAX_GAME_AGE_S / 3600)
        cmd = os.environ.get("TESTQ_CMD_MAPS") or (self.bridge_cmd()
                                                   + " --timeout %d --call rimworld/get_game_info" % PROBE_TIMEOUT_S)
        try:
            r = subprocess.run(["bash", "-c", cmd], cwd=RUNNER, capture_output=True, text=True,
                               timeout=PROBE_TIMEOUT_S + 30)
        except (OSError, subprocess.TimeoutExpired) as e:
            self.say("could not count the kept game's maps: %s" % e)
            return None
        maps = re.search(r'mapCount\\?"\s*:\s*(\d+)', r.stdout or "")
        if not maps:
            self.say("could not count the kept game's maps: rc %s, no mapCount" % r.returncode)
            return None
        self.res["kept_game_maps"] = int(maps.group(1))
        if int(maps.group(1)) >= MAX_GAME_MAPS:
            return "holds %s maps (limit %d)" % (maps.group(1), MAX_GAME_MAPS)
        return None

    def prior_result(self):
        """-> (the most recently published result on this host, its path), or (None, path|None) when there is one this
        worker cannot read, or (None, None) when there is none at all.

        Those are three different answers (owner, 2026-11-17): no attempt has ever finished here, and an attempt
        finished but its record is corrupt, are not the same thing, and neither is a record that says the game was
        healthy. Publish order (result.json's mtime) IS finish order: publish_result writes it once, last."""
        files = []
        for path in glob.glob(p("attempts", "*", "result.json")):
            if os.path.dirname(path) == self.d:         # our own, if we somehow already published: never evidence
                continue
            try:
                files.append((os.stat(path).st_mtime, path))
            except OSError:
                continue
        if not files:
            return None, None
        path = max(files)[1]
        return read_json(path), path

    def kept_game_unmappable(self, load_tail):
        """-> why the kept game can never make a map (for recycled_kept_game), or None (it can, as far as can be read).

        RIMMANDRAKE_RESTART_GAME_AFTER_MAPDATA_TIMEOUT_THREE_JOBS_BURNED. 2026-11-14 10:35 PST the game came up with
        AlienRace.HarmonyPatches dead in its static constructor ("Token 0x19c1 is not a valid MethodBase token"), then
        Error in WorldGenStep on every quicktest, so no map ever appeared. It answered the bridge, it was young and it
        held no maps, so `up --wait` kept it and all three gates above passed it: three jobs in a row timed out on
        readiness 'mapData' and the lane stayed braked 57 min until rw_game.sh down by hand. The run's own stop
        (run_modcheck: no_game, quicktest world start FAILED) fires only AFTER a job has been spent, and the three jobs
        were three DIFFERENT jobs, so a per-job memory would not have caught it either. Two instruments, read before
        the job commits to this process:

          * the process's own Player.log, for the wounds that are permanent for a process (LOG_WOUND_RE, CTOR_RE
            paired with GAME_FATAL_RE). This is the only instrument that sees a wound dealt at load, before any job.
          * the most recently published result on this host, for the harness-side words no Player.log carries
            (NOTE_WOUND_RE) -- unless it also says it stopped its game, in which case that process is gone and its
            wound says nothing about this one. A wounded record is the newest only until this attempt publishes its
            own, so a healthy process that inherits one pays one cold start, never a job.

        Could not look is a fourth answer, not a failure (owner, 2026-11-17): with BOTH instruments blind the game is
        KEPT and the blindness is logged. Stopping on ignorance would cold-start the first job of every fresh
        TESTQ_HOME (no result exists yet) and would kill a game a human had started by hand; and a real wound is still
        caught by this job's own run, costing one job, never the three this item was filed for. The two outcomes are
        told apart by their words: a stop says "cannot make a map: ...", a blind keep is only in worker.log."""
        if not STEVE_LANE:
            return None                     # the archmagi lane's kept game is the owner's: never probed, never stopped
        blind = []
        log = game_log_path()
        try:
            with open(log, encoding="utf-8", errors="replace") as f:
                text = f.read(LOG_SCAN_CHARS)
        except OSError as e:
            blind.append("the kept game's log (%s)" % e)
            text = ""
        wound = game_log_wound(text)
        if wound:
            return "cannot make a map: %s says %s" % (os.path.basename(log), wound)
        res, path = self.prior_result()
        if res is None:
            blind.append("the last result (%s)" % ("none published here yet" if path is None
                                                   else "unreadable: " + path))
        elif STOPPED_NOTE in (res.get("note") or ""):
            self.say("the last result (%s) stopped its own game: its fault is not this process's" % res.get("attempt"))
        else:
            rows = res.get("rows") if isinstance(res.get("rows"), list) else []
            said = "\n".join([str(res.get("note") or "")]
                             + [str(r.get("detail") or "") for r in rows if isinstance(r, dict)])
            hit = NOTE_WOUND_RE.search(said)
            if hit:
                return "cannot make a map: %s ended %s/%s saying %s" % (res.get("attempt"), res.get("outcome"),
                                                                        res.get("cause"), hit.group(0))
        if blind:
            self.say("kept the game: could not read %s; nothing says this process cannot make a map" % " or ".join(blind))
        return None

    def pending_markers(self, before):
        """-> cids of the bridge client's unresolved UNKNOWN-outcome markers sent before `before` ([] if none or the
        list cannot be read: the job's own calls will then say if it matters)."""
        try:
            r = subprocess.run(["bash", "-c", self.bridge_cmd() + " --reconcile"], cwd=RUNNER, capture_output=True,
                               # budget: danger=a hung bridge client holds the attempt, and so one game of the lane; never
                               # budget: reached in the 14 days to 2026-11-24; no record of its run
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
            # budget: danger=a hung status command holds the attempt, and so one game of the lane; never reached in the 14 days
            # budget: to 2026-11-24; no record of its run
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
                                    # budget: danger=a hung bridge client holds the attempt, and so one game of the lane; never
                                    # budget: reached in the 14 days to 2026-11-24; no record of its run
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

    def mods_dir(self):
        """The Mods folder the game of THIS worker loads. A named game (Steve2: `game_instance.py env b`) has its own install
        under its data folder; with no data folder named the answer does not exist, never Steve1's (J20261124T001426Z-9581b9
        read Steve1's companion, said FRESH, and Steve2 loaded the old one)."""
        if os.environ.get("TESTQ_MODS_DIR"):
            return os.environ["TESTQ_MODS_DIR"]
        if (os.environ.get("RM_GAME_INSTANCE") or "a") != "a":
            return os.path.join(os.environ.get("RM_GAME_USERDATA") or "/no-RM_GAME_USERDATA", "game", "Mods")
        return os.path.join(os.environ.get("RM_STEAMAPPS", ""), "common", "RimWorld", "Mods")

    def attest(self):
        mods_dir = self.mods_dir()
        dep = {"mods": {}}
        if self.companion_state:
            dep["companion"] = self.companion_state
        _, folded, _c = S.deploy_catalog(os.path.join(RUNNER, "src"))
        memo_mods = getattr(self, "memo_mods", None)
        for m in ([] if memo_mods else self.deploy_mods()):
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
        if memo_mods:
            dep["mods"] = memo_mods
        else:
            self.memo_save(dep["mods"])
        mc = os.path.join(os.environ.get("RM_GAME_USERDATA", ""), "Config", "ModsConfig.xml")
        dep["modsconfig_sha256_prerun"] = sha256_file(mc) if os.path.isfile(mc) else None
        self.res["deployed"] = dep
        return True

    def memo_save(self, dep_mods):
        """Record this attempt's deploy+attest as the lane's memo, or forget a stale one."""
        st = getattr(self, "_memo", None)
        if not st:
            return
        M, mp, key, _ = st
        sig = M.game_sig(self.mods_dir(), key["mods"]) if key else None
        if key is None or sig is None or not dep_mods or self.job.get("proof_build"):   # a proof DLL is never the memo
            M.forget(mp)
            return
        M.save(mp, key, sig, dep_mods, self.job.get("id"))

    # exact-tier jobs -----------------------------------------------------
    def tier_reading(self, tier):
        """tier_load.py check -> its JSON reading; a check that printed none is a reading that measured nothing."""
        cmd = (os.environ.get("TESTQ_CMD_TIERCHECK") or TIER_CHECK) + " " + shlex.quote(tier)
        rc, tail = self.sh(cmd, log_name="tier_check.log", timeout=2500)  # budget: danger=a hung tier check holds the lane; longest=241s (the whole attest phase, an upper bound) (testq done records, phase_s, 14 days to 2026-11-24)
        for line in reversed((tail or "").splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict):
                    r["exact"] = bool(r.get("exact")) and rc == 0
                    return r
        return {"tier": tier, "running": None, "exact": False,
                "why": "tier check printed no reading (exit %s): %s" % (rc, (tail or "")[-200:])}

    def tier_load(self):
        """Load the job's tier as the whole list, unless the running game already is it (the train stays on a tier),
        then read what actually runs. The reading lands in the result whatever it says; run_proofs refuses to judge
        on a load that is not the tier."""
        tier = S.tier_of(self.job)
        r = self.tier_reading(tier)
        if r.get("exact"):
            # kept, through load(): its wedged/overgrown/marker restarts still apply to a game already on the tier,
            # and a restart comes back on the same list (ModsConfig is the tier's)
            self.say("tier %s: the running game already is the tier, kept" % tier)
            if not self.load():
                return False
            self.res["tier"] = self.tier_reading(tier)
            return True
        self.say("tier %s: the running load is not it (%s): whole-list swap" % (tier, (r.get("why") or "")[:160]))
        # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane; never
        # budget: reached in the 14 days to 2026-11-24; no record of its run
        rc, tail = self.sh(self.cmd_down(), timeout=300)
        if rc != 0:
            return self.fail("INVALID", "LOAD", "game down before the tier swap failed: " + tail)
        swap = os.environ.get("TESTQ_CMD_TIERSWAP") or TIER_SWAP % shlex.quote(
            "testq %s on SteveDesktop: the worker holds this machine's game guard" % self.aid)
        rc, tail = self.sh(swap + " " + shlex.quote(tier), log_name="tier_swap.log", timeout=10800)  # budget: class=deploy
        if rc != 0:
            return self.fail("INVALID", "LOAD", "modset_builder --tier %s --apply failed: %s" % (tier, tail[-300:]))
        if not self.load():
            return False
        self.res["tier"] = self.tier_reading(tier)
        return True

    def run_proofs(self):
        """Each selected clause's live-proof line, from the item's proofs file at source_sha: exit 0 PASS, 1 FAIL, else
        UNMEASURED. On a load that is not the tier nothing runs: every row UNMEASURED, INVALID/LOAD, never a verdict."""
        clauses = list(self.job["selector"]["proofs"])
        r = self.res.get("tier") or {}
        self.res["running"] = r.get("running")
        if not r.get("exact"):
            why = r.get("why") or "the tier-exact load check did not read"
            self.res["rows"] = [{"chain": "proofs", "row": c, "verdict": "UNMEASURED", "detail": why[:S.DETAIL_CAP]}
                                for c in clauses]
            self.res["counts"] = S.count_verdicts(self.res["rows"])
            return self.fail("INVALID", "LOAD", why)
        rel = os.path.join(PROOFS_DIR, self.job["item"] + ".txt")
        # TESTQ_PROOFS_DIR: a selftest's proofs folder; the real one is the pinned clone's, at source_sha
        path = os.path.join(os.environ["TESTQ_PROOFS_DIR"], self.job["item"] + ".txt") if os.environ.get(
            "TESTQ_PROOFS_DIR") else os.path.join(CLONE, rel)
        lines = S.proof_lines(read_text(path) or "")
        budget = int(os.environ.get("TESTQ_RUN_TIMEOUT_S") or self.job.get("timeout_s", 21600))
        per = max(60, budget // max(1, len(clauses)))
        rows = []
        for c in clauses:
            cmd = lines.get(c)
            if not cmd:
                rows.append({"chain": "proofs", "row": c, "verdict": "UNMEASURED",
                             "detail": "no `live-proof %s:` line in %s at %s" % (c, rel, self.job["source_sha"])})
                continue
            log = "proof_%s.log" % c
            rc, tail = self.sh(cmd, log_name=log, timeout=per)
            verdict, crashed = proof_verdict(rc, tail)
            head = ("exit %d" % rc + (", crashed (%s): could not look" % crashed if crashed else "")) \
                if rc is not None else "timed out after %d s" % per
            rows.append({"chain": "proofs", "row": c, "verdict": verdict,
                         "detail": ("%s: %s" % (head, tail))[-S.DETAIL_CAP:]})
            path = os.path.join(self.d, log)
            if os.path.isfile(path):
                self.res["artifacts"].append({"name": log, "path": path, "sha256": sha256_file(path),
                                              "bytes": os.path.getsize(path)})
        self.res["rows"] = rows
        self.res["counts"] = S.count_verdicts(rows)
        self.res.update(outcome="DONE", cause=None, note="tier %s, %d running mods; %s" % (
            S.tier_of(self.job), len(r.get("running") or []), S.count_verdicts(rows)))
        return True

    def run_checks(self):
        """Each selected check's own script on the exact tier -> one row per check (stage6_checks.py run). On a load that
        is not the tier nothing runs: every row UNMEASURED, INVALID/LOAD. A runner that wrote no record is INVALID/HARNESS."""
        ids = list(self.job["selector"]["checks"])
        r = self.res.get("tier") or {}
        self.res["running"] = r.get("running")

        def none_ran(why, outcome, cause):
            self.res["rows"] = [{"chain": "checks", "row": c, "verdict": "UNMEASURED", "detail": why[:S.DETAIL_CAP]}
                                for c in ids]
            self.res["counts"] = S.count_verdicts(self.res["rows"])
            return self.fail(outcome, cause, why)
        if not r.get("exact"):
            return none_ran(r.get("why") or "the tier-exact load check did not read", "INVALID", "LOAD")
        out = os.path.join(self.d, "checks")
        budget = int(os.environ.get("TESTQ_RUN_TIMEOUT_S") or self.job.get("timeout_s", 21600))
        cmd = os.environ.get("TESTQ_CMD_CHECKS") or CHECKS_RUN
        rc, tail = self.sh("%s --mod %s --tier %s --checks %s --out %s --timeout %d" % (
            cmd, shlex.quote(self.job["mod"]), shlex.quote(S.tier_of(self.job)), shlex.quote(",".join(ids)),
            shlex.quote(out), budget), log_name="checks.log", timeout=budget + 1800)
        doc = read_json(os.path.join(out, "checks.json"))
        if rc != 0 or not isinstance(doc, dict) or not isinstance(doc.get("rows"), dict):
            return none_ran("the checks runner wrote no record (exit %s): %s" % (rc, (tail or "")[-300:]), "INVALID", "HARNESS")
        rows, facts = [], {}
        for c in ids:
            x = doc["rows"].get(c) or {"verdict": "UNMEASURED", "detail": "the runner wrote no row of this check"}
            v = x.get("verdict") if x.get("verdict") in ("PASS", "FAIL") else "UNMEASURED"
            rows.append({"chain": "checks", "row": c, "verdict": v, "detail": str(x.get("detail") or "")[:S.DETAIL_CAP]})
            facts[c] = {k: x.get(k) for k in ("site", "held", "command", "log") if x.get(k) is not None}
        for path in [os.path.join(out, "checks.json")] + sorted(glob.glob(os.path.join(out, "run_*.log*"))):
            self.res["artifacts"].append({"name": os.path.basename(path), "path": path, "sha256": sha256_file(path),
                                          "bytes": os.path.getsize(path)})
        self.res["rows"], self.res["counts"] = rows, S.count_verdicts(rows)
        self.res["checks"] = {"identity": doc.get("identity"), "rows": facts}
        gone = self.game_gone()
        if gone:
            self.keep_game_log("Player_died.log", "Player-prev.log" if " runs now" in gone else "Player.log")
            return self.fail("INVALID", "GAME_DIED", gone + "; %s" % S.count_verdicts(rows))
        self.res.update(outcome="DONE", cause=None, note="tier %s, %d running mods; %s" % (
            S.tier_of(self.job), len(r.get("running") or []), S.count_verdicts(rows)))
        return True

    def run_modcheck(self):
        args = S.modcheck_args(self.job)
        timeout = int(os.environ.get("TESTQ_RUN_TIMEOUT_S") or self.job.get("timeout_s", 21600))
        base = os.environ.get("TESTQ_CMD_RUN") or (driver_budget_export(timeout) + RUN_BASE)
        cmd = base + " " + " ".join(shlex.quote(a) for a in args)
        for attempt_no in (1, 2):
            rc, tail = self.sh(cmd, log_name="modcheck.log", timeout=timeout)
            if rc is not None:
                self.res["modcheck_exit"] = rc
                stale = self.stale_load()
                if stale is not None:
                    return stale
                ok = self.read_sheet(tail)
                gone = self.game_gone()
                if gone:
                    self.fail("INVALID", "GAME_DIED", gone + "; modcheck exit %s, sheet %s"
                              % (rc, S.count_verdicts(self.res["rows"])))
                    self.keep_game_log("Player_died.log", "Player-prev.log" if " runs now" in gone else "Player.log")
                    return False
                if self.liveness_unknown:
                    self.res["note"] = (self.res.get("note") or "") + "; " + self.liveness_unknown
                spoiled = next((r for r in self.res.get("rows") or [] if r.get("verdict") in ("UNMEASURED", "NOT_RUN")
                                and SPOILED_RE.search(r.get("detail") or "")), None)
                if self.res.get("cause") == "CANARY":
                    self.stop_game_for_next_job("canary red")
                elif spoiled:
                    self.stop_game_for_next_job("the map is spoiled (%s: %s)" % (spoiled.get("row"), (spoiled.get("detail") or "")[:80]))
                elif self.res.get("cause") == "HARNESS" and (NO_GAME_RE.search(tail or "")
                                                             or WORLD_START_FAILED_RE.search(tail or "")
                                                             or TICK_UNREAD_RE.search(tail or "")):
                    # STEVE_WORKER_UNSTICK_WOUNDED_GAME_KEPT_UP: pid 30296 answered the bridge but could not make a map
                    # (10-31, AlienRace BadImageFormat): 00238b and dd60e2 both reused it. Other HARNESS deaths keep it.
                    # 11-14: the same wound reached as modcheck's "quicktest world start FAILED" (no no_game string).
                    self.keep_game_log()
                    self.stop_game_for_next_job("no game loaded")
                return ok
            self.say("run %d hung past %ss: killed" % (attempt_no, timeout))
            if attempt_no == 2:
                return self.fail("INVALID", "HANG", "modcheck hung past %ss twice (one clean restart between)"
                                 % timeout)
            self.res["retries"] += 1
            self.phase = "restart"
            self.beat()
            self.dump_game("hang%d" % attempt_no)
            self.keep_game_log("Player_hang%d.log" % attempt_no)
            # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane; never
            # budget: reached in the 14 days to 2026-11-24; no record of its run
            rc_down, tail = self.sh(self.cmd_down(), timeout=300)
            if rc_down != 0 and refused_line(tail):    # the game may not be restarted here: no second run
                return self.fail("INVALID", "HANG", "modcheck hung past %ss; no restart (%s)"
                                 % (timeout, refused_line(tail)))
            if not self.load():
                return False
            self.phase = "run"
        return False

    def stale_load(self):
        """STEVE_LANE_UNSTICK_BRAKED_UNOWNED_8EB8. load() starts the game on whatever ModsConfig holds - FULL, which the
        previous modcheck run restored - and modcheck composes MINIMAL + the mod only afterwards, so the game never ran
        the composed list. Since MODCHECK_SESSION_FIX_STALE_LIST_ACCEPTED modcheck refuses that (UNMEASURED stale_load):
        J20261104T065335Z-9652fe and -0b08bb ended "modcheck exit 1 and no sheet JSON" and braked the lane.
        -> None when modcheck did not refuse a stale load; else the run's result. The repair is automatic and once only:
        modcheck left ModsConfig on the composed list (STALE_LOAD line), so restart the game onto it and run again. A
        second refusal, or one modcheck did not leave the list for, ends INVALID/HARNESS with harness_cause stale_load
        (machine-readable: testq.nonfault_cause excuses only the unrepaired kind, retest.job_cause names it)."""
        path = os.path.join(self.d, "modcheck.log")
        text = read_text(path) or ""
        m = NOT_INSTALLED_RE.search(text)
        if m:
            # MODCHECK_STALE_LOAD_FIX_UNINSTALLED_MOD: RimWorld drops an id with no folder at every load, so no restart
            # can help (J20261104T074700Z-42d8eb spent one on ray1203.simplecamerasetting): name it, spend nothing
            self.res["harness_cause"] = "mod_not_installed"
            return self.fail("INVALID", "HARNESS", "mod_not_installed (install it on this host; no restart spent): %s"
                             % m.group(1).strip()[:240])
        m = STALE_LOAD_RE.search(text)
        if not m:
            return None
        why = m.group(1).strip()
        self.res["harness_cause"] = "stale_load"
        if self.res.get("stale_load_bounced") or not STALE_KEPT_RE.search(text):
            again = "after a restart onto the composed list" if self.res.get("stale_load_bounced") else \
                "ModsConfig not left on the composed list, so a restart cannot help"
            return self.fail("INVALID", "HARNESS", "stale_load (%s): the running load is not the composed list: %s"
                             % (again, why[:240]))
        self.res["stale_load_bounced"] = why[:300]
        try:
            os.replace(path, os.path.join(self.d, "modcheck.stale_load.log"))
        except OSError as e:
            self.say("stale_load: could not set modcheck.log aside (%s)" % e)
        self.say("stale_load: the game was not running the composed list (%s): restarting it onto that list"
                 % why[:200])
        self.res["retries"] += 1
        self.phase = "restart"
        self.beat()
        # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane; never
        # budget: reached in the 14 days to 2026-11-24; no record of its run
        rc_down, tail_down = self.sh(self.cmd_down(), timeout=300)
        if rc_down != 0:
            return self.fail("REFUSED" if refused_line(tail_down) else "INVALID", "HARNESS",
                             "stale_load: game down for the restart onto the composed list failed: %s"
                             % (refused_line(tail_down) or (tail_down or "")[-200:]))
        if not self.load():
            return False
        self.phase = "run"
        self.beat()
        return self.run_modcheck()

    def keep_game_log(self, name="Player.log", src_name="Player.log"):
        """OPS_STEVE_DIAGNOSE_INVALID_MBTX: the next cold start overwrites Player.log, and a second one its -prev copy,
        so 186d97's world-start failure (Entry for 371 s, 11-01) went unread: no crash report, log gone within two jobs.
        Keep it beside the attempt BEFORE the game stops, and put the fault in the note. Never fails the result.
        FLOWWORKS_DIAGNOSE_FREEZE_AFTER_DRAWBRIDGE: a frozen game (10-26, main thread silent 400+ s after the drawbridge
        proof) was killed and its log lost the same way, so the wedged-game and hung-run restarts keep it too, each
        under its own `name` so two stops in one attempt do not overwrite each other. A game that died keeps its log
        too (RIMMANDRAKE_DIAGNOSE_HAR_CTOR_TOKEN_ZERO: four 11-14 deaths lost theirs to the retry's cold start); when
        another game already runs, the dead one's is RimWorld's rotated Player-prev.log (`src_name`)."""
        src = os.path.join(os.environ.get("RM_GAME_LOGDIR") or os.environ.get("RM_GAME_USERDATA", ""), src_name)
        dst = os.path.join(self.d, name)
        try:
            shutil.copyfile(src, dst)
            with open(dst, encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except OSError as e:
            self.res["note"] = (self.res.get("note") or "") + "; game log NOT kept (%s)" % e
            return
        fatal = [ln for ln in lines if GAME_FATAL_RE.search(ln)]
        other = [ln for ln in lines if "Exception" in ln]
        fault = "first fatal: " + fatal[0].strip()[:200] if fatal else (
            "last exception: " + other[-1].strip()[:200] if other else "no exception in it")
        self.res["note"] = (self.res.get("note") or "") + "; game log kept at %s, %s" % (dst, fault)

    def dump_game(self, name):
        """FLOWWORKS_DIAGNOSE_FREEZE_AFTER_DRAWBRIDGE: the frozen game of 10-26 was killed with no stack, so it could not
        be classed. Before a stop that kills a frozen game, take one small dump of it (health_minidump.py --before-kill,
        Windows python, headroom-checked, retention capped, one per incident key) into TESTQ_HOME/dumps and put its path
        or its failure in the note. Its next act is the kill, so a dumper that strands the game suspended costs
        nothing. Never fails the result; a dump that hangs is cut off after DUMP_TIMEOUT_S. Only on SteveDesktop: the
        archmagi lane never stops ArchBig (archmagi_phases.py down REFUSED), so no kill follows a dump there."""
        cmd = os.environ.get("TESTQ_CMD_DUMP")
        if cmd is None and not STEVE_LANE:
            self.res["note"] = (self.res.get("note") or "") + "; game dump (%s) skipped: %s never kills its game" % (
                name, HOST)
            return
        if cmd is None:
            ddir = os.path.join(HOME, "dumps")
            try:
                os.makedirs(ddir, exist_ok=True)
                wdir = subprocess.run(["wslpath", "-w", ddir], capture_output=True, text=True,
                                      # budget: danger=a hung wslpath holds the dump of a hung game, and the kill after it; its
                                      # budget: reach leaves no record; no record of its run
                                      timeout=30).stdout.strip() or ddir
            except (OSError, subprocess.SubprocessError):
                wdir = ddir
            cmd = "python.exe src/RimMandrake/Utils/health_minidump.py --before-kill --incident %s --dir %s" % (
                shlex.quote("%s_%s" % (os.path.basename(self.d), name)), shlex.quote(wdir))
        rc, tail = self.sh(cmd, log_name="dump_%s.log" % name, timeout=DUMP_TIMEOUT_S)
        rec = {}
        for ln in reversed((tail or "").splitlines()):
            if ln.startswith("{"):
                try:
                    rec = json.loads(ln)
                except ValueError:
                    rec = {}
                break
        if rc is None:
            got = "game dump (%s) timed out after %ss" % (name, DUMP_TIMEOUT_S)
        elif rec.get("status") == "ok":
            got = "game dump (%s) kept at %s, %s bytes in %s ms" % (name, rec.get("path"), rec.get("sizeBytes"),
                                                                 rec.get("durationMs"))
        else:
            got = "game dump (%s) NOT taken (%s)" % (name, rec.get("reason") or "rc %s: %s" % (rc, (tail or "")[-120:]))
        self.say(got)
        self.res["note"] = (self.res.get("note") or "") + "; " + got

    def stop_game_for_next_job(self, why):
        """STEVE_LANE_FIX_DEAD_COLONY_CANARY_RED: the game a red canary ran on is not handed to the next job. A kept game
        with a dead colony (load 1-2 s) voided every later job until someone ran rw_game.sh down by hand (10-27,
        10-29 03:28, 18:54); stopping it here, after the liveness check, makes the next job cold-start a fresh colony.
        A lane whose phases may not stop the game (archmagi_phases.py REFUSED) says so in the note instead."""
        # budget: danger=a hung game stop (taskkill over WSL interop) holds the attempt, and so one game of the lane; never
        # budget: reached in the 14 days to 2026-11-24; no record of its run
        rc_down, tail_down = self.sh(self.cmd_down(), timeout=300)
        down = "game stopped so the next job cold-starts" if rc_down == 0 else "game NOT stopped (%s)" % (
            refused_line(tail_down) or "rc %s: %s" % (rc_down, (tail_down or "")[-120:]))
        self.say("%s: %s" % (why, down))
        self.res["note"] = (self.res.get("note") or "") + "; " + down

    def read_sheet(self, tail):
        text = open(os.path.join(self.d, "modcheck.log"), encoding="utf-8", errors="replace").read()
        names = re.findall(r"Transient[\\/]+modcheck[\\/]+([^\s\\/]+)\.html", text)
        sheet = os.path.join(SHEET_DIR, names[-1] + ".json") if names else None
        data = read_json(sheet) if sheet else None
        refusal = re.search(r"^REFUSED: (.+)$", text, re.M)
        if not data and refusal:
            return self.fail("INVALID", "BLOCKED_SELECTION", "modcheck refused the selection: " + refusal.group(1))
        if not data:
            # python -X faulthandler writes its stack ("Windows fatal exception", "Fatal Python error") far above the
            # tail, and fail() keeps only the last 400 characters: put the stack's head in the 400, or exit 5 stays a
            # mystery (MODCHECK_DIAGNOSE_EXIT_FIVE_NO_SHEET). The whole stack stays in modcheck.log on this host.
            m = re.search(r"(?:Windows fatal exception|Fatal Python error)", text)
            if m:
                return self.fail("INVALID", "HARNESS", "modcheck exit %s, no sheet; %s ... %s" % (
                    self.res["modcheck_exit"], re.sub(r"\s+", " ", text[m.start():m.start() + 600])[:250],
                    tail[-80:]))
            # the first REFUSED or exception line leads: the tail alone cut Graffiti's `REFUSED  validated must-show
            # lines ...` off, and its deaths read UNKNOWN (RIMMANDRAKE_KEEP_STEVE_PLAYER_LOG_PER_ATTEMPT_SEVENTEEN_BLIND)
            first = FIRST_CAUSE_RE.search(text)
            return self.fail("INVALID", "HARNESS", "modcheck exit %s and no sheet JSON: %s%s"
                             % (self.res["modcheck_exit"],
                                "first: %s ... " % first.group(0).strip()[:160] if first else "",
                                tail[-(300 - 180 if first else 300):]))
        rows = S.rows_from_summary(data.get("summary") or {})
        if self.job.get("situational"):
            self.res["situational"] = situational_digest(self.job["mod"], data.get("summary") or {})
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
        self.res["chain_versions"] = S.chain_versions(data.get("summary") or {})
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
                tier = S.is_proofs(self.job) or S.is_checks(self.job)
                run = self.run_checks if S.is_checks(self.job) else self.run_proofs if tier else self.run_modcheck
                ok = self.timed("deploy", self.deploy)
                ok = ok and self.timed("load", self.tier_load if tier else self.load)
                ok = ok and self.timed("attest", self.attest)
                ok and self.timed("run", run)
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
            # RIMMANDRAKE_KEEP_STEVE_PLAYER_LOG_PER_ATTEMPT_SEVENTEEN_BLIND: every non-DONE attempt that reached the
            # game keeps its log (2 of 96 INVALID attempts 11-06..14 held one); the named wounds above keep theirs first
            if self.res["outcome"] != "DONE" and self.phase in ("load", "attest", "run", "restart") \
                    and not glob.glob(os.path.join(self.d, "Player*.log")):
                self.keep_game_log()
            self.phase = "done"
            rc, msg = unpin(self.d)    # before the result: a start that follows it at once finds the clone on main
            if rc != 0:
                self.say("could not put the clone back on main (the next start retries): %s" % msg[-300:])
            if self.res["outcome"] != "DONE":   # a failed load is where the crash reset lands; after the unpin: see RESET_REPAIR
                repair_reset_list(self.d)
            try:        # what preflight fixed before this attempt (a moved swap marker) belongs in its record
                fixed = (read_json(os.path.join(self.d, "preflight.json")) or {}).get("fixed") or []
            except (OSError, ValueError, AttributeError):
                fixed = []
            if fixed:
                self.res["note"] = ("%s; %s" % (self.res.get("note") or "", " | ".join(fixed))).lstrip("; ")[-600:]
            repaired = reset_repair_note(self.d)
            if repaired:
                self.say(repaired)
                self.res["note"] = ("%s; %s" % (self.res.get("note") or "", repaired)).lstrip("; ")
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


CMD_ECHO_RE = re.compile(r"^\S+Z \$ .*$", re.M)  # the "<utc> $ <cmd>" line say() writes before sh() runs a command


def last_pid_line(rx, text):
    """The last match of rx in the output of the LAST command in a phase's tail, else None. sh() returns worker.log's
    last lines, so a second load's tail can still hold the first load's "started pid" (RIMMANDRAKE_DIAGNOSE_HAR_CTOR_
    TOKEN_ZERO: the stale-load restart kept the dead pid, and game_gone() called the worker's own restart GAME_DIED;
    J20261114T231058Z-a9d923.a1, a GREEN 5/5 run). Output longer than the tail has no echo line in it: all of it is
    the last command's."""
    text = text or ""
    echoes = list(CMD_ECHO_RE.finditer(text))
    found = None
    for found in re.finditer(rx, text[echoes[-1].end():] if echoes else text):
        pass
    return found


def fresh_pid_line(text):
    """Read the fresh PID from rw_game.sh's Steam or named-game launch line."""
    return last_pid_line(r"(?m)^started (?:\S+, )?pid (\d+)\b", text)


FIRST_CAUSE_RE = re.compile(r"^.*(?:\bREFUSED\b|Traceback|Exception|Error:).*$", re.M)


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
