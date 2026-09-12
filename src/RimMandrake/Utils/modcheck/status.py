"""modcheck.status -- the GREEN/STALE registry, `infrastructure/state/modcheck_status.json`.

Same discipline as `code_review_status.py` (CLAUDE.md's "Code isn't clean
until a review says so", the sibling policy this one exists next to): a hash
comparison, never a timestamp, and an atomic lock+tmp+`os.replace` write so
two concurrent windows recording a run never lose one's entry (this repo is
shared by BENCH/FOUNDRY).

    modcheck run <mod>            # records a fresh GREEN/RED entry
    modcheck status               # GREEN/STALE/NEVER RUN per mod
    modcheck declare <mod> minor --why "..."   # re-green after a trivial edit

Gate law (spec §4): the playtest offer path checks GREEN. No green, no
playtest. A hash mismatch with no `declare minor` is STALE, full stop.
"""
import contextlib
import hashlib
import json
import os
import subprocess
import time

# `runner.py` (this module's caller for a live `modcheck run`) executes
# under WINDOWS `python.exe` -- everything touching the actual bridge
# socket must, per the WSL-loopback limitation in rimbridge_client.py -- so
# `fcntl` (POSIX-only) is not always importable here, unlike in
# `code_review_status.py`'s WSL-only context this module's lock pattern was
# borrowed from. Fall back to `msvcrt` file locking on Windows. MEASURED
# 2026-09-12: the first live `modcheck run` crashed on exactly this before
# a single component ran.
try:
    import fcntl

    def _lock(fd):
        fcntl.flock(fd, fcntl.LOCK_EX)

    def _unlock(fd):
        fcntl.flock(fd, fcntl.LOCK_UN)
except ImportError:
    import msvcrt

    # MEASURED live 2026-09-12: locking a huge byte range (1 GiB) on the
    # LOCK file -- which is separate from the tmp file `save()` actually
    # writes into, and stays empty or near-empty forever -- raised
    # `PermissionError` from msvcrt on Windows; locking beyond a file's
    # actual extent is not reliable there the way POSIX `flock` is. The
    # portable fix every cross-platform-lock library uses: the lock file
    # holds exactly one byte (write it if missing) and only that byte is
    # ever locked. This file is a pure mutex -- the real content always
    # lives in `LOG_PATH` itself, written by `save()` below.
    def _ensure_one_byte(fd):
        if os.fstat(fd).st_size < 1:
            os.write(fd, b"\0")
            os.fsync(fd)

    def _lock(fd):
        _ensure_one_byte(fd)
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_LOCK, 1)

    def _unlock(fd):
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
LOG_PATH = os.path.join(ROOT, "infrastructure", "state", "modcheck_status.json")
LOCK_PATH = LOG_PATH + ".lock"

# Never part of a mod's behavioural hash: editing the validator does not
# change what the mod DOES. Case-insensitive basename match.
_EXCLUDED_BASENAMES = {"validation.py", "__pycache__"}


def mod_hash(mod_dir):
    """SHA-256 over every file under `mod_dir` except the validator itself
    and cache noise -- (relpath, content) pairs, sorted, so the hash is
    stable regardless of filesystem walk order."""
    parts = []
    for root, dirs, files in os.walk(mod_dir):
        dirs[:] = [d for d in dirs if d not in _EXCLUDED_BASENAMES
                  and d != ".git"]
        for name in sorted(files):
            if name in _EXCLUDED_BASENAMES or name.endswith(".pyc"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, mod_dir).replace(os.sep, "/")
            with open(path, "rb") as f:
                parts.append((rel, f.read()))
    parts.sort(key=lambda kv: kv[0])
    h = hashlib.sha256()
    for rel, content in parts:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(content)
        h.update(b"\0")
    return h.hexdigest()


def _git(args, timeout=10):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


@contextlib.contextmanager
def _locked():
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    fd = os.open(LOCK_PATH, os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        _lock(fd)
        yield
    finally:
        _unlock(fd)
        os.close(fd)


def load():
    if not os.path.isfile(LOG_PATH):
        return {}
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError as e:
            raise RuntimeError(
                "%s is not valid JSON (merge conflict markers?): %s"
                % (LOG_PATH, e))


def save(data):
    tmp = "%s.tmp.%d.%d" % (LOG_PATH, os.getpid(), time.time_ns())
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        try:
            _lock(fd)
            try:
                body = json.dumps(data, indent=2, sort_keys=True) + "\n"
                os.write(fd, body.encode("utf-8"))
                os.fsync(fd)
            finally:
                _unlock(fd)
        finally:
            os.close(fd)
        os.replace(tmp, LOG_PATH)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def record_run(mod, mod_dir, run_id, all_green):
    """Called once per `modcheck run <mod>`. Never hand-called mid-run --
    the runner calls this exactly once, after every chain has finished."""
    with _locked():
        data = load()
        data[mod] = {
            "hash": mod_hash(mod_dir),
            "run_id": run_id,
            "status": "GREEN" if all_green else "RED",
            "ts": time.time(),
            "minor": None,
        }
        save(data)
    return data[mod]


def declare_minor(mod, mod_dir, why):
    """Re-green `mod` at its CURRENT hash. Only valid for a trivial,
    no-gameplay-effect change (owner ruling 2026-09-12) -- this function
    trusts the caller's judgment call but records the diff --stat alongside
    the why so the claim is checkable later, same as the spec requires.
    Refuses a mod with no prior GREEN entry: there is nothing to re-green."""
    with _locked():
        data = load()
        entry = data.get(mod)
        if not entry or entry.get("status") != "GREEN":
            raise RuntimeError(
                "%s has no prior GREEN run to declare minor against -- "
                "run `modcheck run %s` first." % (mod, mod))
        diff_stat = _git(["diff", "--stat", "HEAD", "--", mod_dir]) or \
                   "(git diff --stat unavailable)"
        entry["hash"] = mod_hash(mod_dir)
        entry["minor"] = {"why": why, "diff_stat": diff_stat, "ts": time.time()}
        data[mod] = entry
        save(data)
    return entry


def check(mod, mod_dir):
    """GREEN / STALE / NEVER RUN. Never touches the game."""
    data = load()
    entry = data.get(mod)
    if not entry:
        return "NEVER RUN"
    if entry.get("status") != "GREEN":
        return "RED (last run failed)"
    if mod_hash(mod_dir) != entry.get("hash"):
        return "STALE"
    return "GREEN"
