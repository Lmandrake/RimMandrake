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
        dirs[:] = [d for d in dirs if d.lower() not in _EXCLUDED_BASENAMES
                  and d != ".git"]
        for name in sorted(files):
            if name.lower() in _EXCLUDED_BASENAMES or name.endswith(".pyc"):
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


def _checklist_state(walk):
    """`(present, effective_state)` of a walk's `## north star`, or
    `(False, None)` when there is no walk. Read here rather than passed in as a
    boolean so a caller cannot hand this function a flattering answer."""
    if not walk or not os.path.isfile(walk):
        return False, None
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import northstar  # noqa: E402
    ns = northstar.parse(walk)
    return ns["present"], ns["state"]


def verdict_for(all_green, walk, refused="", reviewed=False):
    """The GREEN definition of north_star_validation_spec.md §5, in one place.

    GREEN requires all five: state assertions pass, every validated must-show
    line is claimed, every claim is judged, the checklist is VALIDATED, and he
    has reviewed the sheet once. The last three are what this function adds.

      REFUSED              the visual floor or an orphaned `shows=` (never ran)
      RED                  something failed -- state or judge
      DRAFT-CHECKLIST      both halves passed against a bar that is not his yet
      PENDING-OWNER-REVIEW both halves passed; his own eyes not yet on a sheet
      GREEN                all five

    ⚠️ A mod whose walk has NO `## north star` section reaches GREEN exactly as
    it did before this system existed. Enforcement is per mod, as he validates
    (owner, 2026-09-15) -- that is what makes the whole change additive.
    """
    if refused:
        return "REFUSED"
    if not all_green:
        return "RED"
    present, state = _checklist_state(walk)
    if present and state != "VALIDATED":
        return "DRAFT-CHECKLIST"
    if present and not reviewed:
        return "PENDING-OWNER-REVIEW"
    return "GREEN"


def record_run(mod, mod_dir, run_id, all_green, walk=None, refused=""):
    """Called once per `modcheck run <mod>`. Never hand-called mid-run --
    the runner calls this exactly once, after every chain has finished.

    `all_green` is the run's BOTH-HALVES verdict (state and judge); `walk` is the
    mod's validation walk, whose checklist state and the owner's recorded review
    decide whether an all-green run is allowed to be called GREEN."""
    with _locked():
        data = load()
        prior = data.get(mod) or {}
        review = prior.get("owner_review")
        data[mod] = {
            "hash": mod_hash(mod_dir),
            "run_id": run_id,
            "status": verdict_for(all_green, walk, refused, bool(review)),
            "ts": time.time(),
            "minor": None,
            # His review survives a re-run: it is required only for a mod's
            # FIRST green, and it names the run whose sheet he actually read.
            "owner_review": review,
            "refused": refused or None,
        }
        save(data)
    return data[mod]


def record_owner_review(mod, said, run_id=None):
    """Record that the owner personally reviewed this mod's sheet -- spec §5.5,
    required once, before a mod's first GREEN, mirroring the whole-file-then-
    incremental rule of `code_review_status.py`.

    OWNER-AUTHORISED ONLY: `said` is his verbatim words, which the CLI requires
    and this function records rather than re-derives. Promotes a run that was
    waiting on exactly this to GREEN, and refuses a mod with no run to review --
    there is no sheet to have read."""
    with _locked():
        data = load()
        entry = data.get(mod)
        if not entry:
            raise RuntimeError(
                "%s has no recorded run -- there is no sheet to review. Run "
                "`modcheck run %s` first." % (mod, mod))
        entry["owner_review"] = {"run_id": run_id or entry.get("run_id"),
                                 "said": said, "ts": time.time()}
        if entry.get("status") == "PENDING-OWNER-REVIEW":
            entry["status"] = "GREEN"
        data[mod] = entry
        save(data)
    return entry


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


_NOT_GREEN_WHY = {
    "RED": "RED (last run failed)",
    "REFUSED": "REFUSED (visual floor -- see `refused` in the registry)",
    "DRAFT-CHECKLIST": "DRAFT-CHECKLIST (both halves passed, but the "
                       "must-show bar is not the owner's yet)",
    "PENDING-OWNER-REVIEW": "PENDING-OWNER-REVIEW (both halves passed; needs "
                            "`modcheck review <mod> --owner-said ...` once)",
}


def check(mod, mod_dir):
    """GREEN / STALE / NEVER RUN, or why it is not green. Never touches the
    game. Only the literal string GREEN is a pass -- a gate reading this must
    not treat PENDING-OWNER-REVIEW as one."""
    data = load()
    entry = data.get(mod)
    if not entry:
        return "NEVER RUN"
    recorded = entry.get("status")
    if recorded != "GREEN":
        return _NOT_GREEN_WHY.get(recorded, str(recorded))
    if mod_hash(mod_dir) != entry.get("hash"):
        return "STALE"
    return "GREEN"


def check_or_orphaned(mod):
    """`check(mod, mod_dir)`, but resolves `mod_dir` itself (via
    `runner.find_mod_dir`) instead of trusting a caller-supplied path, and
    returns `"ORPHANED (no such mod folder)"` rather than raising when the
    folder is gone.

    This is the function the aggregate `status` (no-arg) view must call
    per row, in place of printing the stored `entry["status"]` field
    directly -- DETERMINISM_ASSESSMENT.md SS4's first structural fix: "A
    summary must never be able to disagree with the detail it summarises."
    Before this existed, `modcheck status` printed `Pits  GREEN` from the
    stored field while `modcheck status Pits` (which already called
    `check()`) printed `STALE` for the very same mod, and printed
    `FluidCanals  GREEN` for a mod renamed away weeks earlier, because
    `_mod_dir_or_die` (which would have raised) is only reachable from the
    single-mod path, never the no-arg summary loop."""
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import runner  # noqa: E402  local import: avoids a module cycle with runner.py
    try:
        mod_dir = runner.find_mod_dir(mod)
    except RuntimeError:
        return "ORPHANED (no such mod folder)"
    return check(mod, mod_dir)
