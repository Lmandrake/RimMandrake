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
import fcntl
import hashlib
import json
import os
import subprocess
import time

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
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
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
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                body = json.dumps(data, indent=2, sort_keys=True) + "\n"
                os.write(fd, body.encode("utf-8"))
                os.fsync(fd)
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
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
