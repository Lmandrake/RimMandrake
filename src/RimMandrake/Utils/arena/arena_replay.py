#!/usr/bin/env python3
"""arena_replay.py - replay runner for the architecture trial (ARENA_REPLAY_BUILD_NO_FUTURE_IN_CLONE).

design/RimMandrake/architecture_switch_harness_2026-10-29.md 1.4 and 3.2.

A replay task re-does work that already exists, so the clone an arm works in must not be able to read the answer.
  build_replay_clone  `git init --template=` (no hooks) + `git fetch <source> <base_sha>` of ONLY the base sha into
                      $RM_ARENA_ROOT/replay/<arm>/<task> (default /home/mandrake/rm/arena). A FULL clone, never a
                      worktree. Only history up to base_sha arrives; there is no remote, no tags, no alternates, FETCH_HEAD
                      is removed and the only ref is a detached HEAD at base_sha. The result is then AUDITED.
  audit_clone         the fix sha (and any other forbidden sha) must be absent: `git cat-file -e`, the full list from
                      `git cat-file --batch-all-objects` (loose and packed), alternates/commondir/gitfile borrowing, every
                      ref, reflog and FETCH_HEAD (raw bytes, hex and binary). Any hit raises ReplayLeak and the clone is deleted.
  schedule            per-arm run order: a seeded shuffle, seed = sha256(freeze_hash, arm), or (contains given, as
                      run_schedule always does) a seeded chronological order, oldest first, in which arms MAY share an order
                      (near-linear pool); the stopping rule holds decisions until the newest era has run
                      (arena_analysis ERA GATE). Reproducible from the seed. interleave() merges the arms' orders
                      round-robin (arm order re-shuffled each round from the same seed) into one slot list.
  run_one             build -> work -> judge -> delete, deletion in `finally`, so a failure also leaves nothing.
  leftovers / sweep   clones still on disk; `rm-scratch-reap` also has the replay tree among its roots.

RESIDUAL (known, accepted, not fixed here):
  - sandbox_masks() is a CONTRACT: the caller (judge / sandbox layer) must hide those paths from the arm. This module cannot.
  - the clone directory is checked by dev/inode and lstat, but a same-user adversary racing a rename between check and
    rmtree (dirfd-relative delete) is not defended against.
  - the on-disk marker is plain JSON a same-user process can forge; the reaper and sweep accept a well-formed marker knowingly.
    In-process cleanup does not rely on it (it keeps its own inode + nonce).
Tests use a temp root: RM_ARENA_ROOT or the root= argument. Nothing here touches the source repo except `git fetch` reads.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import math
import os
import random
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_ROOT = "/home/mandrake/rm/arena"
DEFAULT_SOURCE = "/home/mandrake/rm/bench"
DEFAULT_PRIVATE = "~/.local/state/rm_arena_private"
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,100}")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_safe_git as SG  # noqa: E402  (git on a clone an arm wrote into)
SHA = re.compile(r"[0-9a-f]{40}")
SHA_IN = re.compile(r"[0-9a-fA-F]{7,40}")
HASH64 = re.compile(r"[0-9a-f]{64}")
MARKER = ".git/rm_arena_replay.json"      # scratch_reap.py reads the same name (REPLAY_MARKER)

# D4 - WHAT THIS DOES NOT STOP. The clone has no remote, no url, no include and no alternates, and it is filled from a
# harness-private bare mirror (not the live bench clone). But the arm is an ordinary process of the same user on the
# same filesystem: a deliberately malicious arm can still `git -C /home/mandrake/rm/bench log`, `cat` the mirror, or
# read any repo it can path to. This module cannot prevent that. The arena judge / sandbox layer MUST hide the
# paths returned by sandbox_masks() (bind-mount over them, or run the arm as another uid / in a mount namespace).


class ReplayError(Exception):
    pass


class ReplayLeak(ReplayError):
    pass


class ReplayExists(ReplayError):
    """The clone path (or its run lock) is taken: nothing was created and nothing may be deleted by the refuser."""


# clones THIS process created: str(path) -> {"dev","ino","nonce","root"}; cleanup deletes only what is recorded here
_CREATED: dict = {}


def private_dir() -> Path:
    return Path(os.path.expanduser(os.environ.get("RM_ARENA_PRIVATE") or DEFAULT_PRIVATE))


RETIRED_TREES = "/home/mandrake/rm/retired-trees"


def glob_dir(pat: str) -> str:
    """The fixed directory a glob lives in ('/a/b/*-git-*' -> '/a/b'); a plain path is returned as is."""
    import glob as _glob
    if not _glob.has_magic(pat):
        return pat.rstrip("/") or "/"
    cut = min(i for i, ch in enumerate(pat) if ch in "*?[")
    return os.path.dirname(pat[:cut]) or "/"
CLAUDEWORK_ROOT = "/mnt/d/ClaudeWork/rimmandrake"


def sandbox_masks(source=DEFAULT_SOURCE) -> list[str]:
    """Paths a sandbox must hide from an arm (it can read them as the same user otherwise): the answer holders.
    Derived from arena_tasks.old_history_repos() AND the literal OLD_HISTORY_DEFAULT prefixes (a glob that matches
    nothing today is still masked at its fixed prefix), so a new old-history repo cannot drift out of the list.
    arm_sandbox.deny_paths() is the full list it enforces (this + every sibling under RM_ROOT + $HOME leaks).
    Item ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE."""
    import arena_tasks as T                      # arena_tasks does not import arena_replay: no cycle
    out = [str(Path(source)), str(private_dir()), "/home/mandrake/rm/bench", "/home/mandrake/rm/foundry",
           "/home/mandrake/rm/store.git", "/home/mandrake/rm/mirror.git", "/mnt/d/Luke/dev/RimMandrake",
           RETIRED_TREES, CLAUDEWORK_ROOT]
    env_old = [e.strip() for e in os.environ.get("ARENA_OLD_HISTORY", "").split(os.pathsep) if e.strip()]
    for pat in list(T.OLD_HISTORY_DEFAULT) + env_old:     # an $ARENA_OLD_HISTORY override is masked the same way
        out.append(glob_dir(pat))
    out += [str(p) for p in T.old_history_repos()]
    seen = []
    for x in out:
        if x and x not in seen:
            seen.append(x)
    return seen


def arena_root(root=None) -> Path:
    raw = str(root) if root else (os.environ.get("RM_ARENA_ROOT") or DEFAULT_ROOT)
    if not raw or "\0" in raw:
        raise ReplayError("bad arena root %r" % raw)
    r = Path(raw)
    if not r.is_absolute():
        raise ReplayError("arena root %r is relative: refused" % raw)
    rr = str(r.resolve())
    if rr == "/mnt" or rr.startswith("/mnt/"):
        raise ReplayError("arena root %s is on a Windows mount: arm clones live on ext4" % r)
    return r


def replay_dir(root=None) -> Path:
    return arena_root(root) / "replay"


def _name(what: str, v) -> str:
    if not isinstance(v, str) or not NAME.fullmatch(v) or v.endswith("."):
        raise ReplayError("bad %s name %r" % (what, v))
    return v


def clone_path(arm: str, task: str, root=None) -> Path:
    _name("arm", arm)
    _name("task", task)
    base = replay_dir(root)
    arm_dir = base / arm
    for d in (base, arm_dir):                       # no symlink anywhere under the root
        if d.is_symlink():
            raise ReplayError("%s is a symlink: refused" % d)
    return arm_dir / task


def _contained(path: Path, root=None) -> Path:
    """Resolved path must stay under the resolved replay dir, else refuse before ANY delete."""
    base = replay_dir(root).resolve()
    rp = path.parent.resolve() / path.name
    if base not in rp.parents:
        raise ReplayError("%s escapes %s: refused" % (path, base))
    return rp


def _env() -> dict:
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", GIT_CONFIG_GLOBAL="/dev/null", GIT_OPTIONAL_LOCKS="0")
    return e


def _run(repo: Path, *args, check=False) -> subprocess.CompletedProcess:
    """git on a clone an ARM worked in (builder-controlled .git: replace refs, config): through arena_safe_git, with
    the inherited GIT_* scrubbed as _env does (ARENA_GIT_FETCHES_AUDIT_STRAGGLERS)."""
    env = SG._env(repo, False)
    for k in [k for k in env if k.startswith("GIT_") and k not in SG.GIT_SAFE_ENV and k != "GIT_WORK_TREE"]:
        del env[k]
    return subprocess.run(SG.git_argv(repo, *args), capture_output=True, env=env, timeout=300)


def _git(repo: Path, *args, env=None, check=True) -> str:
    e = _env()
    e.update(env or {})
    r = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True, text=True, env=e, timeout=300)
    if check and r.returncode:
        raise ReplayError("git %s failed: %s" % (" ".join(args[:2]), r.stderr.strip()[:300]))
    return r.stdout


def _chmod_tree(path: Path):
    """Make every directory under path traversable/writable by us (a judge may leave chmod-000 dirs)."""
    stack = [str(path)]
    while stack:
        d = stack.pop()
        try:
            st = os.lstat(d)
            if not stat.S_ISDIR(st.st_mode):
                continue
            if (st.st_mode & stat.S_IRWXU) != stat.S_IRWXU:
                os.chmod(d, st.st_mode | stat.S_IRWXU)
            with os.scandir(d) as it:
                stack += [e.path for e in it if e.is_dir(follow_symlinks=False)]
        except OSError:
            pass


def _on_rm_error(fn, p, _exc):
    """Works as shutil.rmtree onexc (3.12+, 3rd arg an exception) and onerror (3rd arg an exc_info tuple)."""
    try:
        os.chmod(os.path.dirname(p), stat.S_IRWXU)
        if not os.path.islink(p):
            os.chmod(p, stat.S_IRWXU)
        fn(p)
    except OSError:
        pass


def rmtree(path: Path):
    if path.is_symlink():
        path.unlink()
    elif path.exists():
        _chmod_tree(path)
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=_on_rm_error)
        else:
            shutil.rmtree(path, onerror=_on_rm_error)
    if path.exists() or path.is_symlink():
        raise ReplayError("could not delete %s" % path)


def _delete_own(dest: Path, root=None):
    """Delete `dest` only if THIS process created it (dev/inode recorded at creation) and it is still that directory."""
    rec = _CREATED.get(str(dest))
    if rec is None:
        return                                      # not ours: never delete
    try:
        st = os.lstat(dest)
    except FileNotFoundError:
        _CREATED.pop(str(dest), None)
        return
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or (st.st_dev, st.st_ino) != (rec["dev"], rec["ino"]):
        raise ReplayError("not deleting %s: it is no longer the clone this run created" % dest)
    # the on-disk marker is NOT consulted: this process recorded the inode + nonce itself, and an unreadable, mutated or
    # mistyped marker must not leave a judged clone behind.
    _contained(dest, root)
    rmtree(dest)
    _CREATED.pop(str(dest), None)
    try:
        dest.parent.rmdir()                         # only if empty; a concurrent run's clone keeps it
    except OSError:
        pass


def _lock_name(arm: str, task: str) -> str:
    """Unambiguous: a__b + c and a + b__c must not share a lock, so hash the NUL-joined names."""
    return hashlib.sha256((arm + "\0" + task).encode()).hexdigest() + ".lock"


def _marker_ok(clone: Path):
    """-> the marker dict when clone/.git/rm_arena_replay.json is a regular file holding a well-formed marker, else None."""
    try:
        m = clone / MARKER
        if m.is_symlink() or not m.is_file():
            return None
        d = json.loads(m.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or not isinstance(d.get("nonce"), str) or not re.fullmatch(r"[0-9a-f]{32}", d["nonce"]):
        return None
    if d.get("state") not in ("building", "ready") or isinstance(d.get("created"), bool) or not isinstance(d.get("created"), (int, float)):
        return None
    return d


def _write_marker(clone: Path, rec: dict):
    tmp = clone / (MARKER + ".tmp")
    tmp.write_text(json.dumps(rec))
    os.replace(tmp, clone / MARKER)


@contextlib.contextmanager
def _lock(arm: str, task: str, root=None):
    _name("arm", arm)                                # validate BEFORE any path is built
    _name("task", task)
    ld = arena_root(root) / "locks"
    if ld.is_symlink():
        raise ReplayError("%s is a symlink: refused" % ld)
    ld.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(ld / _lock_name(arm, task)), os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise ReplayExists("another run holds %s/%s" % (arm, task)) from None
        yield
    finally:
        os.close(fd)


def _full(source: Path, sha: str) -> str:
    if not isinstance(sha, str) or not SHA_IN.fullmatch(sha):
        raise ReplayError("bad sha %r (7-40 hex, no whitespace)" % (sha,))
    out = _git(source, "rev-parse", "--verify", "-q", sha.lower() + "^{commit}", check=False).strip()
    if not SHA.fullmatch(out):
        raise ReplayError("%s is not a commit in %s" % (sha, source))
    return out


def ensure_mirror(source) -> Path:
    """Harness-private bare mirror of `source` (under the private dir). Clones are fetched from it, never from the
    live bench clone, so the clone's fetch history never names a repo the arm is working beside."""
    source = Path(source)
    pd = private_dir()
    pd.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(pd, 0o700)
    m = pd / ("mirror_" + hashlib.sha256(str(source.resolve()).encode()).hexdigest()[:16] + ".git")
    if not m.exists():
        _git(pd, "init", "-q", "--bare", str(m))
    _git(m, "fetch", "-q", "--no-tags", "--force", "--prune", str(source),
         "+refs/heads/*:refs/heads/*", "+refs/remotes/*:refs/remotes/*", check=False)
    return m


# ---------------------------------------------------------------- audit

def audit_clone(clone: Path, forbidden, masked=()) -> list[str]:
    """-> findings (empty = no forbidden object is reachable). `forbidden` = full shas that must not exist."""
    forbidden = {f.lower() for f in forbidden}
    bad = [f for f in forbidden if not SHA.fullmatch(f)]
    if bad:
        raise ReplayError("forbidden shas must be full 40-hex: %r" % bad)
    out: list[str] = []
    gd = clone / ".git"
    if not gd.is_dir() or gd.is_symlink():
        return ["no real .git directory"]
    for f in sorted(forbidden):
        r = _run(clone, "cat-file", "-e", f)
        if r.returncode == 0:
            out.append("git cat-file -e finds %s" % f)
        elif r.returncode != 1:                       # 1 = absent; anything else means we could not tell: fail closed
            out.append("audit failure: git cat-file -e %s exited %d: %s" % (f, r.returncode, r.stderr.decode(errors="replace").strip()[:120]))
        r = _run(clone, "rev-parse", "--verify", "-q", f + "^{commit}")
        if r.returncode == 0:
            out.append("git rev-parse finds commit %s" % f)
        elif r.returncode != 1:
            out.append("audit failure: git rev-parse %s exited %d: %s" % (f, r.returncode, r.stderr.decode(errors="replace").strip()[:120]))
    ro = _run(clone, "cat-file", "--batch-all-objects", "--batch-check")
    if ro.returncode:
        return out + ["audit failure: git cat-file --batch-all-objects exited %d" % ro.returncode]
    allobj = ro.stdout.decode(errors="replace").split("\n")
    have = {ln.split(" ")[0] for ln in allobj if ln}
    out += ["object store (loose/packed) holds %s" % f for f in sorted(forbidden & have)]
    for borrow in ("objects/info/alternates", "objects/info/http-alternates", "commondir"):
        if (gd / borrow).exists():
            out.append("borrows objects: .git/%s exists" % borrow)
    for f in ("FETCH_HEAD", "ORIG_HEAD", "MERGE_HEAD", "packed-refs"):
        if (gd / f).exists() and any(h.encode() in (gd / f).read_bytes() for h in forbidden):
            out.append(".git/%s names a forbidden sha" % f)
    needles = [h.encode() for h in forbidden] + [bytes.fromhex(h) for h in forbidden]
    for sub in ("refs", "logs"):
        for p in (gd / sub).rglob("*") if (gd / sub).is_dir() else []:
            if p.is_file() and any(n in p.read_bytes() for n in needles):
                out.append("%s names a forbidden sha" % p.relative_to(clone))
    rr = _run(clone, "for-each-ref", "--format=%(refname) %(objectname)")
    if rr.returncode:
        return out + ["audit failure: git for-each-ref exited %d" % rr.returncode]
    refs = rr.stdout.decode(errors="replace").split("\n")
    out += ["ref %s" % r for r in refs if r and any(f in r for f in forbidden)]
    cfg = (gd / "config").read_text(errors="replace") if (gd / "config").exists() else ""
    if re.search(r"^\s*\[\s*(remote|branch|submodule|include|includeIf)\b", cfg, re.M | re.I):
        out.append("config has a remote/branch/submodule/include section: the clone can reach its source")
    if re.search(r"^\s*(url|pushurl|path)\s*=", cfg, re.M | re.I):
        out.append("config names a url/path")
    if re.search(r"^\s*(hookspath|fsmonitor|textconv|clean|smudge|process|sshcommand|pager|editor|attributesfile)\s*=", cfg, re.M | re.I) \
            or re.search(r"^\s*\[\s*(filter|diff|merge|credential|alias|url)\b", cfg, re.M | re.I):
        out.append("config sets hooksPath/fsmonitor/filter/textconv/driver/credential keys: arm tooling could run code or reach elsewhere")
    hk = gd / "hooks"
    if hk.is_dir() and any(not h.name.endswith('.sample') for h in hk.iterdir()):
        out.append(".git/hooks holds an active hook")
    for m in masked:                                  # D4: nothing inside .git may name the source / mirror
        mb = str(m).encode()
        for dp, dns, fns in os.walk(gd):
            dns[:] = [d for d in dns if d != "objects"]
            for fn in fns:
                fp = Path(dp) / fn
                try:
                    if not fp.is_symlink() and fp.stat().st_size < 1_000_000 and mb in fp.read_bytes():
                        out.append("%s names the source path %s" % (fp.relative_to(clone), m))
                except OSError:
                    pass
    return out


# ---------------------------------------------------------------- build

def build_replay_clone(arm: str, task: str, base_sha: str, fix_sha: str, source=DEFAULT_SOURCE, root=None,
                       also_forbidden=(), use_mirror=True, _locked=False) -> Path:
    """Fresh clone holding history up to base_sha only. Raises (leaving nothing it did not create) when base_sha reaches
    fix_sha. Creation is O_EXCL (mkdir): when the path is taken we raise ReplayExists and touch NOTHING."""
    if not _locked:
        with _lock(arm, task, root):
            return build_replay_clone(arm, task, base_sha, fix_sha, source, root, also_forbidden, use_mirror, True)
    source = Path(source)
    dest = clone_path(arm, task, root)
    _contained(dest, root)
    forb = []
    for f in also_forbidden:
        if not isinstance(f, str) or not SHA.fullmatch(f.lower()):
            raise ReplayError("also_forbidden must be full 40-hex shas: %r" % (f,))
        forb.append(f.lower())
    fetch_from = ensure_mirror(source) if use_mirror else source
    base, fix = _full(fetch_from, base_sha), _full(fetch_from, fix_sha)
    if base == fix:
        raise ReplayError("base_sha equals fix_sha: nothing to replay")
    for _ in range(5):
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.mkdir(dest)                           # atomic O_EXCL: exactly one creator
            break
        except FileExistsError:
            raise ReplayExists("%s already exists (not ours: left untouched)" % dest) from None
        except FileNotFoundError:
            continue                                 # a concurrent run removed the empty arm dir
    else:
        raise ReplayError("could not create %s" % dest)
    st = os.lstat(dest)
    nonce = secrets.token_hex(16)
    _CREATED[str(dest)] = {"dev": st.st_dev, "ino": st.st_ino, "nonce": nonce}
    try:
        # the marker goes in FIRST (atomic), so a SIGKILL anywhere after this line leaves a clone the reaper can recognise
        os.mkdir(dest / ".git")
        rec = {"nonce": nonce, "created": time.time(), "arm": arm, "task": task, "pid": os.getpid(), "state": "building"}
        _write_marker(dest, rec)
        _git(dest, "init", "-q", "--template=")
        _git(dest, "config", "gc.auto", "0")
        _git(dest, "fetch", "-q", "--no-tags", "--no-write-fetch-head", str(fetch_from), base)
        _git(dest, "-c", "advice.detachedHead=false", "update-ref", "--no-deref", "HEAD", base)
        _git(dest, "reset", "-q", "--hard", base)
        for junk in ("FETCH_HEAD", "ORIG_HEAD", "packed-refs"):
            (dest / ".git" / junk).unlink(missing_ok=True)
        if (dest / ".git" / "logs").exists():
            rmtree(dest / ".git" / "logs")
        findings = audit_clone(dest, [fix, *forb], masked=[source, fetch_from, private_dir()])
        if findings:
            raise ReplayLeak("replay clone %s/%s can reach the future: %s" % (arm, task, "; ".join(findings)))
        rec["state"] = "ready"
        _write_marker(dest, rec)
        return dest
    except BaseException:
        _delete_own(dest, root)
        raise


# ---------------------------------------------------------------- schedule

def norm_freeze(freeze_hash) -> str:
    h = freeze_hash.strip().lower() if isinstance(freeze_hash, str) else ""
    if not HASH64.fullmatch(h):
        raise ReplayError("freeze hash must be 64 hex chars (sha256), got %r" % (freeze_hash,))
    return h


_HASH = hashlib.sha256            # swappable by the selftest to force a collision


def arm_seed(freeze_hash: str, arm: str, salt: int = 0) -> int:
    """seed = sha256(freeze_hash|arm); salt 0 is the only normal case. A salt n>0 appends |n (collision handling only)."""
    freeze_hash = norm_freeze(freeze_hash)
    msg = "%s|%s" % (freeze_hash, arm) + ("|%d" % salt if salt else "")
    return int.from_bytes(_HASH(msg.encode()).digest()[:8], "big")


def arm_order(freeze_hash: str, arm: str, tasks, salt: int = 0) -> list[str]:
    """Seeded shuffle of the task ids for ONE arm, a function of (freeze_hash, arm, tasks, salt) alone: it does not depend
    on which other arms exist."""
    order = sorted(set(tasks))
    random.Random(arm_seed(freeze_hash, arm, salt)).shuffle(order)
    return order


def arm_chrono_order(freeze_hash: str, arm: str, tasks, contains: dict, salt: int = 0) -> list[str]:
    """As arm_order, but a seeded linear extension of the sibling relation (arena_rounds.chrono_order): every task
    whose fix another task's base holds comes first. Random only where the relation leaves a choice."""
    import arena_rounds as RD                    # arena_rounds imports arena_tasks, not this module: no cycle
    return RD.chrono_order(sorted(set(tasks)), contains, seed=arm_seed(freeze_hash, arm, salt))


def schedule(freeze_hash: str, arms, tasks, contains=None) -> dict:
    """-> {"orders": {arm: [task...]}, "slots": [(arm, task)...]} (slots = interleaved across arms).
    contains (arena_tasks.base_contains over these tasks) given: each arm's order is chrono-ordered and checked
    (ARENA_PLANNERS_ENFORCE_SIBLING_ORDER). The near-linear relation of a real pool leaves few or no distinct orders,
    so arms MAY share an order then (the collision rule still salts, but a collision is no longer an error);
    "sibling_order" in the result says which rule made the orders."""
    freeze_hash = norm_freeze(freeze_hash)
    arms = sorted(set(arms))
    orders: dict[str, list[str]] = {}
    chrono = contains is not None
    can_differ = math.factorial(len(set(tasks))) >= len(arms) and not chrono
    taken: set = set()
    for a in arms:                                   # sorted, so the result never depends on the caller's arm order
        # COLLISION RULE (documented, deterministic): normally each arm's order is sha256(freeze|arm) alone. If it equals the
        # order of an earlier arm (sorted by name), THAT later arm's salt is incremented (1, 2, ...) until it is unique.
        for salt in range(0, 50 if chrono else 1000):
            o = arm_chrono_order(freeze_hash, a, tasks, contains, salt) if chrono else arm_order(freeze_hash, a, tasks, salt)
            if tuple(o) not in taken or not (can_differ or chrono):
                break
        orders[a] = o
        taken.add(tuple(o))
    if can_differ and len({tuple(v) for v in orders.values()}) != len(orders):      # verification, never reached normally
        raise ReplayError("arm orders still collide after salting")
    slots: list = []
    rng = random.Random(arm_seed(freeze_hash, "#interleave"))
    for i in range(len(orders[arms[0]]) if arms else 0):
        rnd = arms[:]
        rng.shuffle(rnd)
        slots += [(a, orders[a][i]) for a in rnd]
    if chrono:
        import arena_rounds as RD
        for o in orders.values():
            RD.check_rounds(o, contains)         # raises TaskRefused: never run an order that judges a task too early
    return {"orders": orders, "slots": slots, "sibling_order": chrono}


# ---------------------------------------------------------------- run

def leftovers(root=None) -> list[Path]:
    """Every replay clone still on disk (a dir holding .git, at replay/<arm>/<task>), plus anything unexpected."""
    base = replay_dir(root)
    out = []
    if base.is_dir():
        for arm in sorted(base.iterdir()):
            for t in sorted(arm.iterdir()) if arm.is_dir() and not arm.is_symlink() else [arm]:
                out.append(t)
    return out


def sweep(root=None) -> list[Path]:
    """Delete clones nobody is running: each must be a real directory under real (non-symlink) replay/<arm> dirs, carry a
    well-formed marker, and its run lock must be FREE (non-blocking flock) while we delete. Anything else is left alone."""
    base = replay_dir(root)
    gone = []
    if base.is_symlink() or not base.is_dir():
        return gone
    for arm_d in sorted(base.iterdir()):
        if arm_d.is_symlink() or not arm_d.is_dir() or not NAME.fullmatch(arm_d.name):
            continue
        for p in sorted(arm_d.iterdir()):
            if p.is_symlink() or not p.is_dir() or not NAME.fullmatch(p.name) or _marker_ok(p) is None:
                continue
            try:
                with _lock(arm_d.name, p.name, root):       # held by a live run -> ReplayExists -> skipped
                    if p.is_symlink() or _marker_ok(p) is None:
                        continue
                    _contained(p, root)
                    rmtree(p)
                    gone.append(p)
            except ReplayExists:
                continue
        try:
            arm_d.rmdir()
        except OSError:
            pass
    return gone


@contextlib.contextmanager
def _arm_environ():
    """work() and judge() run with a scrubbed process environment: no inherited GIT_* (GIT_DIR, GIT_OBJECT_DIRECTORY,
    GIT_ALTERNATE_OBJECT_DIRECTORIES ...), no system/global git config, a private empty HOME. Restored afterwards."""
    saved = dict(os.environ)
    home = tempfile.mkdtemp(prefix="arm_home_")
    try:
        for k in [k for k in os.environ if k.startswith("GIT_")]:
            del os.environ[k]
        os.environ.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_TERMINAL_PROMPT="0", HOME=home)
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(home, ignore_errors=True)


def run_one(arm: str, task: str, base_sha: str, fix_sha: str, work, judge, source=DEFAULT_SOURCE, root=None,
            also_forbidden=(), use_mirror=True):
    """Build the clone, `work(clone)`, `judge(clone)` -> verdict. A clone THIS call created is deleted whatever happens;
    a refusal because the path/lock is already taken deletes nothing."""
    with _lock(arm, task, root):
        clone = None
        try:
            clone = build_replay_clone(arm, task, base_sha, fix_sha, source, root, also_forbidden, use_mirror, True)
            with _arm_environ():
                work(clone)
                return judge(clone)
        finally:
            if clone is not None:
                _delete_own(clone, root)


def run_schedule(freeze_hash: str, tasks: dict, arms, work, judge, source=DEFAULT_SOURCE, root=None,
                 contains=None) -> list[dict]:
    """tasks = {task_id: {"base_sha":..., "fix_sha":...}}. Runs the interleaved slots; one failure is recorded and the
    run goes on (its clone is already gone). Sibling order is always enforced: `contains` defaults to
    arena_tasks.base_contains over `tasks` in `source` (a refused order raises before anything runs)."""
    if contains is None:
        import arena_rounds as RD
        contains = RD.contains_for(tasks, source)
    results = []
    for arm, task in schedule(freeze_hash, arms, tasks, contains)["slots"]:
        t = tasks[task]
        rec = {"arm": arm, "task": task}
        try:
            rec["verdict"] = run_one(arm, task, t["base_sha"], t["fix_sha"], lambda c: work(arm, task, c),
                                     lambda c: judge(arm, task, c), source, root, t.get("forbidden", ()))
        except Exception as e:                       # noqa: BLE001 - recorded, never swallowed silently
            rec["error"] = "%s: %s" % (type(e).__name__, e)
        results.append(rec)
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("schedule")
    s.add_argument("--freeze-hash", required=True)
    s.add_argument("--arms", required=True)
    s.add_argument("--tasks", required=True)
    sub.add_parser("leftovers")
    sub.add_parser("sweep")
    a = ap.parse_args(argv)
    if a.cmd == "schedule":
        print(json.dumps(schedule(a.freeze_hash, a.arms.split(","), a.tasks.split(",")), indent=1))
    elif a.cmd == "leftovers":
        print("\n".join(map(str, leftovers())) or "none")
    else:
        print("deleted: %s" % [str(p) for p in sweep()])
    return 0


if __name__ == "__main__":
    sys.exit(main())
