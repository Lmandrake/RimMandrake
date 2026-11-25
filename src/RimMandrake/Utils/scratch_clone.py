#!/usr/bin/env python3
"""scratch_clone.py — the shared object store and the ONE way to make a throwaway clone.

SEAT_MEMORY_CLONES_DRIVES_1, design/RimMandrake/memory_clones_drives_2026-10-08.md §4 items 1-2,
§7 phase 2; what was built and how to judge it: design/RimMandrake/objstore_trial_2026-10-08.md.
Owner, 2026-10-08: "try it out, but let's wire it to keep data on its operation so we can judge
if it was a good idea later."

    scratch_clone.py clone <purpose> [--name N] [--sparse P ... | --checkout | --no-checkout] [--fetch] [--dissociate]
    scratch_clone.py init        create the store (hard-links the mirror's packs: ~0 bytes, instant)
    scratch_clone.py refresh     fetch the mirror's origin/main into the store
    scratch_clone.py sample      periodic record (rm-objstore.timer): store size, borrowers, fsck, df
    scratch_clone.py baseline    time one real full copy of the store, for the time-saved column
    scratch_clone.py report      the verdict table — what the owner reads

The store is /home/mandrake/rm/store.git: a bare repo owned by NO working tree, fed only by
`git fetch` from /home/mandrake/rm/mirror.git. A scratch clone is `git clone --shared` of it, so
its objects/info/alternates names the STORE — never bench or foundry, whose `git gc --prune` is
what could silently corrupt the six borrowers found on 10-08 (headline finding #8).

Why a seat gc cannot hurt a borrower any more, and why the store's own gc cannot either:
  - borrowers point at the store, never at a seat clone;
  - the store sets gc.auto=0, gc.pruneExpire=never, reflogs kept forever with
    core.logAllRefUpdates=always — every tip it ever held stays reachable, so even a manual
    `git gc` there drops nothing a borrower could need;
  - init hard-links the mirror's packs; when the mirror repacks and deletes its names, the
    store's links keep the data.

Telemetry lives outside git in ~/.local/state/rm-objstore/ (XDG_STATE_HOME honoured):
  uses.jsonl       one record per `clone` call, success or failure
  samples.jsonl    one record per `sample` run
  incidents.jsonl  a borrower whose objects stopped resolving (the corruption the store exists to stop)
  baseline.jsonl   measured full-copy times, used to compute time saved

Env overrides (the selftest uses them): RM_OBJSTORE, RM_OBJSTORE_SEED, RM_SCRATCH_ROOT,
RM_OBJSTORE_STATE, RM_OBJSTORE_SCAN (os.pathsep-separated glob patterns), RM_SEAT.

What a clone checks out (SCRATCH_CLONES_SHRINK_SPARSE_NOT_FULL; measured 2026-10-26: 65 BENCH scratch clones held
240 GB, because history is shared but every helper checked out the whole ~3.9 GB tree):
  default        cone-sparse: the root files plus BASE_CONE (the tooling every helper needs to run selftests, rimflow
                 and ./publish, ~200 MB), plus any --sparse PATH the task needs. `git sparse-checkout add <dir>` widens
                 it later; a commit outside the cone is fine, git keeps the rest of the tree as it is on HEAD.
  --checkout     the whole tree. For Relentless pool clones (bounded by the pool cap) and work that truly reads
                 everything (a full build, a repo-wide sweep); say why in the purpose.
  --no-checkout  no working tree at all (read-only git inspection).
"""
from __future__ import annotations

import argparse
import fcntl
import glob
import hashlib
import json
import os
import random
import shutil
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
import sys
import time
from contextlib import contextmanager
from pathlib import Path

RM = Path("/home/mandrake/rm")
ORIGIN_URL = "git@github.com:Lmandrake/RimMandrake.git"
SEED_REF = "refs/remotes/origin/main"   # mirror.git's layout (mirror.py)
STORE_REF = "refs/heads/main"
STORE_CONFIG = {
    "gc.auto": "0",
    "gc.autoPackLimit": "0",
    "gc.pruneExpire": "never",
    "gc.worktreePruneExpire": "never",
    "gc.reflogExpire": "never",
    "gc.reflogExpireUnreachable": "never",
    "core.logAllRefUpdates": "always",
    "objstore.role": "shared object store; borrowers via alternates; never prune (scratch_clone.py)",
}
SEATS = ("bench",)
# The default cone (see the module docstring). Root files are always in a cone checkout.
# src/RimMandrake/contracts: rimflow and Utils import it (selftest_scratch_clone's cone_imports_check)
BASE_CONE = (".claude", "infrastructure", "skills", "src/RimMandrake/Utils", "src/RimMandrake/contracts",
             "src/RimMandrake/rimflow")


def identity_sources() -> list[Path]:
    """Where a clone's commit identity is copied from: RM_IDENTITY_FROM (a test's fixture), else the seat clones."""
    if os.environ.get("RM_IDENTITY_FROM"):
        return [Path(os.environ["RM_IDENTITY_FROM"])]
    return [RM / s for s in SEATS]


def set_identity(dest: Path) -> str:
    """Give `dest` the seat clone's repo-local user.name and user.email (RIMMANDRAKE_SET_HELPER_CLONE_NOREPLY_GMAIL_
    SLIPS_ONTO_PUBLIC: RimMandrake is public, and a clone with no repo-local identity commits as ~/.gitconfig's Gmail
    address; the seat clone holds the noreply one). -> what it did, for the uses record; never raises. A source it cannot
    read is said, and dest is left as it was."""
    for src in identity_sources():
        got = {}
        for k in ("user.name", "user.email"):
            r = subprocess.run(["git", "-C", str(src), "config", "--local", "--get", k], capture_output=True, text=True,
                               timeout=30)
            if r.returncode == 0 and r.stdout.strip():
                got[k] = r.stdout.strip()
        if "user.email" in got:
            for k, v in got.items():
                git("config", k, v, cwd=dest)
            return "identity %s from %s" % (got["user.email"], src)
    return "UNMEASURED identity: no repo-local user.email in %s; the clone commits as the global identity" % (
        ", ".join(str(p) for p in identity_sources()))


def store_path() -> Path:
    return Path(os.environ.get("RM_OBJSTORE", RM / "store.git"))


def seed_path() -> Path:
    return Path(os.environ.get("RM_OBJSTORE_SEED", RM / "mirror.git"))


def scratch_root() -> Path:
    return Path(os.environ.get("RM_SCRATCH_ROOT", RM / "scratch"))


def state_dir() -> Path:
    if os.environ.get("RM_OBJSTORE_STATE"):
        d = Path(os.environ["RM_OBJSTORE_STATE"])
    else:
        d = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state") / "rm-objstore"
    d.mkdir(parents=True, exist_ok=True)
    return d


def scan_patterns() -> list[str]:
    env = os.environ.get("RM_OBJSTORE_SCAN")
    if env:
        return [p for p in env.split(os.pathsep) if p]
    h = str(Path.home())
    return [f"{RM}/*", f"{RM}/scratch/*/*", f"{RM}/_quarantine/*/*", f"{h}/wt/*", f"{h}/.cache/*"]


def seat() -> str:
    if os.environ.get("RM_SEAT"):
        return os.environ["RM_SEAT"]
    try:
        s = cgroup_seat(Path("/proc/self/cgroup").read_text())
        if s:
            return s
    except OSError:
        pass
    return "UNKNOWN"


def cgroup_seat(text: str) -> str | None:
    """The seat a /proc/<pid>/cgroup names: claude-seat-<seat>-<n>[.scope] -> <seat>, the name of its rm/scratch dir."""
    for line in text.splitlines():
        for part in line.split("/"):
            if part.startswith("claude-seat-"):
                return part[len("claude-seat-"):].rsplit("-", 1)[0]
    return None


def live_seats() -> set[str]:
    """Every seat a live process runs in (its claude-seat scope)."""
    out = set()
    for f in glob.glob("/proc/[0-9]*/cgroup"):
        try:
            s = cgroup_seat(Path(f).read_text())
        except OSError:
            continue
        if s:
            out.add(s)
    return out


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def append(name: str, rec: dict) -> None:
    with open(state_dir() / name, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def read_jsonl(name: str) -> list[dict]:
    p = state_dir() / name
    out = []
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def git(*args, cwd=None, check=True, timeout=None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()}")
    return r.stdout.strip()


@contextmanager
def store_lock():
    p = store_path().parent / (store_path().name + ".lock")
    with open(p, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def own_bytes(root: Path) -> tuple[int, int]:
    """(bytes only this tree holds, bytes hard-linked with something else). Allocated blocks. find does the walk: the same
    lstat of every non-directory as os.walk, in C and outside the GIL, so pool_reading's threads overlap it (a 16-clone pool
    walked in ~3 s of Python, 2026-11-05). A symlink to a directory counts its own blocks here (os.walk listed it as a dir)."""
    try:     # -H: a root that is a symlink is followed, as os.walk(root) does; a timeout raises rather than walking twice
        r = subprocess.run(["find", "-H", str(root), "!", "-type", "d", "-printf", "%n %b\n"], capture_output=True,
                           text=True, timeout=300)
        if r.returncode in (0, 1) and (r.stdout or not r.stderr):     # 1 = some entry unreadable: skipped, as os.walk does
            own = linked = 0
            for line in r.stdout.splitlines():
                n, _, b = line.partition(" ")
                if n.isdigit() and b.isdigit():
                    if int(n) > 1:
                        linked += int(b) * 512
                    else:
                        own += int(b) * 512
            return own, linked
    except OSError:      # no find on this box
        pass
    own = linked = 0
    for dp, _dn, fn in os.walk(root):
        for n in fn:
            try:
                st = os.lstat(os.path.join(dp, n))
            except OSError:
                continue
            b = st.st_blocks * 512
            if st.st_nlink > 1:
                linked += b
            else:
                own += b
    return own, linked


def store_objects() -> dict:
    """count-objects of the store: what a full clone's .git/objects would hold."""
    kv = {}
    for line in git("--git-dir", str(store_path()), "count-objects", "-v").splitlines():
        k, _, v = line.partition(":")
        kv[k.strip()] = int(v.strip()) if v.strip().isdigit() else v.strip()
    return {"objects": kv.get("count", 0) + kv.get("in-pack", 0),
            "bytes": (kv.get("size", 0) + kv.get("size-pack", 0)) * 1024}


# ---------------------------------------------------------------- store

def init() -> dict:
    st, seed = store_path(), seed_path()
    if (st / "HEAD").exists():
        configure()
        return {"created": False}
    git("init", "-q", "--bare", "-b", "main", str(st))
    configure()
    linked = 0
    sp = seed / "objects" / "pack"
    if sp.is_dir():
        for f in sorted(sp.glob("pack-*")):
            if f.suffix in (".pack", ".idx", ".rev"):
                try:
                    os.link(f, st / "objects" / "pack" / f.name)
                    linked += 1
                except OSError:
                    pass
    # Point the ref at the seed's tip BEFORE fetching: a fetch into a ref-less repo negotiates
    # nothing and re-sends every object (measured 10-08: a 6 GB duplicate next to the links).
    try:
        tip = git("--git-dir", str(seed), "rev-parse", "--verify", SEED_REF)
        git("--git-dir", str(st), "cat-file", "-e", tip + "^{commit}")
        git("--git-dir", str(st), "update-ref", STORE_REF, tip)
    except RuntimeError:
        pass
    refresh(lock=False)
    return {"created": True, "packs_linked": linked}


def configure() -> None:
    for k, v in STORE_CONFIG.items():
        git("--git-dir", str(store_path()), "config", k, v)


def refresh(lock: bool = True) -> dict:
    t0 = time.time()

    def _do():
        git("--git-dir", str(store_path()), "fetch", "-q", "--no-tags", str(seed_path()),
            f"+{SEED_REF}:{STORE_REF}", timeout=600)
    if lock:
        with store_lock():
            _do()
    else:
        _do()
    return {"refresh_s": round(time.time() - t0, 2),
            "head": git("--git-dir", str(store_path()), "rev-parse", STORE_REF)}


# ---------------------------------------------------------------- clone

def cone_for(checkout: bool, sparse: list[str], no_checkout: bool) -> tuple[str, list[str]]:
    """-> (mode, cone dirs). Sparse is the default: BASE_CONE plus whatever --sparse names."""
    if checkout and (sparse or no_checkout) or (sparse and no_checkout):
        raise ValueError("pick one of --sparse, --checkout, --no-checkout")
    if checkout:
        return "checkout", []
    if no_checkout:
        return "no-checkout", []
    cone = list(BASE_CONE)
    for p in sparse:
        p = p.strip("/")
        if p and p not in cone:
            cone.append(p)
    return "sparse", cone


def clone(purpose: str, name: str | None, checkout: bool, sparse: list[str], fetch: bool,
          dissociate: bool, no_checkout: bool = False) -> int:
    s = seat()
    name = name or f"{purpose.replace(' ', '-')[:40]}-{time.strftime('%Y%m%d-%H%M%S')}"
    dest = scratch_root() / s / name
    mode, cone = cone_for(checkout, sparse, no_checkout)
    rec = {"ts": now_iso(), "seat": s, "purpose": purpose, "path": str(dest), "mode": mode, "cone": cone,
           "dissociate": dissociate, "fetch": fetch, "ok": False, "error": None}
    t0 = time.time()
    made = False
    try:
        if dest.exists():
            raise RuntimeError(f"{dest} already exists")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.parent == pool_root():
            reused = pool_reuse(dest, fetch=fetch)
            if reused:
                rec.update({"ok": True, "reused": True})
                print(dest)
                return 0
            why = pool_admit(dest)
            if why:
                rec["refused"] = why
                raise RuntimeError("POOL REFUSED: " + why)
        if not (store_path() / "HEAD").exists():
            rec["init"] = init()
        try:
            rec.update(refresh())
        except Exception as e:  # a stale store still clones; the clone can --fetch the rest
            rec["refresh_error"] = str(e)
        so = store_objects()
        t1 = time.time()
        made = True     # from here a failure leaves a dest only this call made: it is removed, never left half-made
        if dissociate:   # independent copy: local clone hard-links packs, no alternates
            git("clone", "-q", "--no-checkout", str(store_path()), str(dest))
        else:
            git("clone", "-q", "--shared", "--no-checkout", str(store_path()), str(dest))
        rec["clone_s"] = round(time.time() - t1, 2)
        git("remote", "set-url", "origin", ORIGIN_URL, cwd=dest)
        git("config", "core.hooksPath", "infrastructure/githooks", cwd=dest)
        rec["identity"] = set_identity(dest)
        if fetch:
            t2 = time.time()
            git("fetch", "-q", "origin", cwd=dest, timeout=900)
            git("update-ref", "refs/heads/main", "refs/remotes/origin/main", cwd=dest)
            rec["fetch_s"] = round(time.time() - t2, 2)
        t3 = time.time()
        if mode == "sparse":
            git("sparse-checkout", "set", "--cone", *cone, cwd=dest)
        if mode != "no-checkout":
            git("read-tree", "-mu", "HEAD", cwd=dest)
        rec["checkout_s"] = round(time.time() - t3, 2)
        alt = dest / ".git" / "objects" / "info" / "alternates"
        rec["alternates"] = alt.read_text().strip() if alt.exists() else None
        gown, glinked = own_bytes(dest / ".git")
        wt = sum(own_bytes(dest)) - gown - glinked
        rec.update({
            "head": git("rev-parse", "HEAD", cwd=dest),
            "git_dir_own_bytes": gown, "git_dir_hardlinked_bytes": glinked,
            "worktree_bytes": wt,
            "full_clone_objects_bytes": so["bytes"],
            "full_clone_bytes": so["bytes"] + wt,
            "objects_borrowed": 0 if dissociate else so["objects"],
            "ok": True,
        })
        print(dest)
        return 0
    except Exception as e:
        rec["error"] = str(e)
        # RELENTLESS_BUNDLES_FIX_FOURTEEN_GIG_PATCHES (2026-11-04): a fetch refused by GitHub left a pool clone with a .git,
        # no index and no tree; Relentless read its 44k tracked files as deletions and bundled the tree three times (14 GB).
        if made and dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
            rec["removed_half_made"] = not dest.exists()
        print(f"scratch_clone: FAILED: {rec['error']}", file=sys.stderr)
        return 1
    finally:
        rec["wall_s"] = round(time.time() - t0, 2)
        append("uses.jsonl", rec)


# ---------------------------------------------------------------- the bounded clone pool
# WORKER_CLONES_MONITOR_POOL_NOT_RABBITS. Owner, 2026-10-31: bounded pool of about 10 reused clones for writers above 4,
# "I trust you, but please monitor them carefully. They seem to propagate prolifically." Two limits, each with its danger
# (design/specs/2026-11-22-clone-pool-disk-floor/boundary.md). Enforced HERE, at creation, because every pool clone is made by
# this file; the reading below is what Operations shows. `git worktree` stays banned.
# The count line guards clones that multiply unwatched: 16, the owner's card 2026-11-02 18:35 PST ("8 workers, 16 clones / 70 GB").
POOL_MAX_CLONES = 16
# The disk line guards a full root disk: a new clone is refused when / would keep less free than the DISK_LOW line once the
# new clone grows as large as the largest one now in the pool. The number lives in slot_rules.json `disk_brake_free_gb`
# (210 GB, one worst day of scratch growth, 207 GB on 2026-10-26), read by the slot allocator's disk brake too. It replaced a
# fixed 80 GB pool size that refused a launch at 83.55 GB with 433 GB free (2026-11-22).
SLOT_RULES = Path(__file__).resolve().with_name("slot_rules.json")
FLOOR_KEY = "disk_brake_free_gb"
POOL_IDLE_S = 3600
POOL_WARM = "warm-"     # relentless_disk.WARM


def pool_root() -> Path:
    return Path(os.environ.get("RM_POOL_ROOT", RM / "relentless" / "clones"))


class FloorUnreadable(Exception):
    """The disk floor could not be read: a new clone is refused, naming the cause. There is no fallback number."""


def pool_cap() -> int:
    return int(os.environ.get("RM_POOL_MAX_CLONES", POOL_MAX_CLONES))


def pool_floor_bytes() -> int:
    """The free space / must keep: RM_POOL_FLOOR_GB, else slot_rules.json ops.disk_brake_free_gb. Raises FloorUnreadable."""
    if os.environ.get("RM_POOL_FLOOR_GB"):
        return int(float(os.environ["RM_POOL_FLOOR_GB"]) * 10**9)
    try:
        v = json.loads(SLOT_RULES.read_text())["ops"][FLOOR_KEY]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError(f"{FLOOR_KEY} is {v!r}, not a number")
        return int(v * 10**9)
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise FloorUnreadable(f"the pool's disk floor ops.`{FLOOR_KEY}` in {SLOT_RULES} cannot be read: "
                              f"{type(e).__name__}: {e}") from e


def root_free_bytes(path: Path | None = None) -> int:
    """Free bytes on the disk that holds the pool root (its nearest existing parent when it is not made yet)."""
    p = Path(path or pool_root())
    while not p.exists() and p != p.parent:
        p = p.parent
    return shutil.disk_usage(p).free


def floor_reading(largest: int) -> dict:
    """free, floor and margin (free - largest clone - floor) in GB; floor_error names why the floor could not be read."""
    free = root_free_bytes()
    d = {"root_free_gb": round(free / 1e9, 2), "largest_clone_gb": round(largest / 1e9, 2)}
    try:
        floor = pool_floor_bytes()
    except FloorUnreadable as e:
        return dict(d, floor_gb=None, margin_gb=None, floor_error=str(e))
    return dict(d, floor_gb=round(floor / 1e9, 2), margin_gb=round((free - largest - floor) / 1e9, 2), floor_error=None)


TREECHECK_PREFIX = "rm-treecheck-"      # publish.py CHECKTREE_PREFIX: its full checkout for the door checks


def shed(c: Path) -> list[str]:
    """Make a reused clone as small as a fresh one: remove every untracked and ignored file (a run's Transient output, a
    Saves backup), every leftover publish checkout in .git, and every loose object a pack already holds. Only for a clone
    nobody works in whose work is pushed (pool_reuse's own test). -> what it did, one line per step."""
    said = []
    for d in sorted((c / ".git").glob(TREECHECK_PREFIX + "*")):
        shutil.rmtree(d, ignore_errors=True)
        said.append(f"removed {d.name}" + (" (FAILED)" if d.exists() else ""))
    for argv, what in ((["clean", "-q", "-ffdx"], "clean"), (["repack", "-d", "-l", "-q"], "repack"),
                       (["prune-packed", "-q"], "prune-packed")):
        r = subprocess.run(["git", *argv], cwd=c, capture_output=True, text=True, timeout=900)
        said.append(f"{what} exit {r.returncode}" + (f": {r.stderr.strip()[:120]}" if r.returncode else ""))  # cut-ok: terminal display
    return said


def clone_bytes(c: Path) -> int:
    own, linked = own_bytes(c)
    return own + linked      # allocated, hard links counted once per tree: the cap errs high


# Paths every clone dirties by running (transcripts, ledger shards, review state); relentless.py POOL_NOISE is the same list.
POOL_NOISE = ("conversations/", "infrastructure/state/ledger/events/", "infrastructure/state/code_review/")


def blob_at(c: Path, rev: str, path: str) -> bytes | None:
    """The file's bytes at rev; None when it has none there."""
    r = subprocess.run(["git", "cat-file", "blob", f"{rev}:{path}"], cwd=c, capture_output=True, timeout=60)
    return r.stdout if r.returncode == 0 else None


def content_on_origin(c: Path, path: str, mine: bytes) -> bool:
    """origin/main already holds this content: the same bytes, or (a ledger, appended to) every line of it already a line
    of origin's copy. Any doubt is not covered."""
    return holds_content(path, mine, blob_at(c, "origin/main", path))


def holds_content(path: str, mine: bytes, theirs: bytes | None) -> bool:
    """theirs (origin's copy, None = it has none) already holds mine: the same bytes, or a noise ledger every line of which
    is already one of theirs."""
    return theirs is not None and (mine == theirs or (path.endswith(".jsonl") and path.startswith(POOL_NOISE) and
                                                      set(mine.splitlines()) <= set(theirs.splitlines())))


def noise_on_origin(c: Path, path: str) -> bool:
    """A dirty noise file whose content origin/main already holds. Anything else, or any doubt, is not covered."""
    if not path.startswith(POOL_NOISE):
        return False
    f = c / path
    try:
        return f.is_file() and content_on_origin(c, path, f.read_bytes())
    except (OSError, subprocess.SubprocessError):
        return False


def transcript_kept(c: Path, path: str) -> bool:
    """A conversations/ record is kept off the clone, content-addressed beside the pool, so it no longer holds the clone:
    nothing lands a pool clone's records, and every idle clone read stranded on one (this write is why a reading can do it)."""
    if not (path.startswith("conversations/") and path.endswith(".md")):
        return False
    try:
        data = (c / path).read_bytes()
        dest = pool_root().parent / "transcripts" / f"{Path(path).stem}-{hashlib.sha1(data).hexdigest()[:12]}.md"
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(f".{os.getpid()}.tmp")
            tmp.write_bytes(data)
            os.replace(tmp, dest)
        return True
    except OSError:
        return False


def derived_view(c: Path, path: str) -> bool:
    """An untracked queue projection `rimflow render` regenerates ("generated by rimflow render" on its first line): derived, never work."""
    if not path.startswith("infrastructure/state/queue/") or not path.endswith(".md"):
        return False
    try:
        with open(c / path, encoding="utf-8", errors="replace") as f:
            return f.readline().startswith("<!-- generated by rimflow render")
    except OSError:
        return False


def dirty_beyond_origin(c: Path) -> bool:
    """Dirty or untracked paths, minus the noise origin/main already has and the records kept. Fails closed: unreadable
    status is dirty."""
    r = subprocess.run(["git", "--no-optional-locks", "status", "--porcelain", "-z", "--untracked-files=all"], cwd=c,
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError("git status: " + (r.stderr or r.stdout).strip())
    ents = [e for e in r.stdout.split("\0") if e]
    i = 0
    while i < len(ents):
        e = ents[i]
        i += 1
        if e[:1] in "RC":          # a rename or copy carries its source as the next field
            i += 1
        if noise_on_origin(c, e[3:]) or transcript_kept(c, e[3:]) or (e[:2] == "??" and derived_view(c, e[3:])):
            continue
        return True
    return False


POOL_STATE = ("infrastructure/state/lessons/",)     # relentless.py POOL_STATE, the same list


def commit_is_state(c: Path, sha: str) -> bool:
    """True when the commit is a single-parent commit touching only POOL_NOISE / POOL_STATE paths."""
    if len(git("rev-list", "--parents", "-n1", sha, cwd=c, timeout=60).split()) > 2:
        return False
    files = git("diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha, cwd=c, timeout=60).split("\n")
    files = [f for f in files if f]
    return bool(files) and all(f.startswith(POOL_NOISE + POOL_STATE) for f in files)


def cherry_on_origin(c: Path, want: set[str] | None = None) -> set[str]:
    """Local commits whose patch origin/main already holds under another hash (`git cherry` marks them '-'). A merge is
    never listed, so it stays at risk. No readable origin/main: nothing is covered. `want` (the commits the caller asks
    about) skips a ref that reaches none of them beyond the remotes: its cherry could only answer for other commits. One
    `git cherry` against an old tag cost ~3 s and a pool reuse ran one per tag per candidate clone, inside the supervisor
    tick (RELENTLESS_TICK_MEASURE_OUTLASTS_ITS_NAP)."""
    out = set()
    for ref in git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/tags", cwd=c, timeout=60).split():
        if want is not None and not want & set(git("rev-list", ref, "--not", "--remotes", cwd=c, check=False, timeout=120).split()):
            continue
        r = subprocess.run(["git", "cherry", "refs/remotes/origin/main", ref], cwd=c, capture_output=True, text=True, timeout=300)
        if r.returncode == 0:
            out.update(ln[2:] for ln in r.stdout.splitlines() if ln.startswith("- "))
    return out


def commit_content_on_origin(c: Path, sha: str) -> bool:
    """Every path this single-parent commit changed already reads the same on origin/main: the rebase that re-resolved a
    ledger line changes the patch id, not the content. A deletion or an empty commit proves nothing and is not covered."""
    if len(git("rev-list", "--parents", "-n1", sha, cwd=c, timeout=60).split()) > 2:
        return False
    files = [f for f in git("diff-tree", "--no-commit-id", "--name-only", "-z", "-r", "--root", sha, cwd=c, timeout=60).split("\0") if f]
    for f in files:
        mine = blob_at(c, sha, f)
        if mine is None or not content_on_origin(c, f, mine):
            return False
    return bool(files)


def commits_at_risk(c: Path, shas: list[str], strict: bool) -> bool:
    """Any of these local commits whose content is nowhere else. A commit origin/main holds under another hash loses nothing
    even to a reuse's reset (POOL_STRANDED_FIX_LANDED_COMMITS_STILL_HOWL: breach 3 of 2026-11-03 was all such); a state commit
    origin lacks is only excused from the alarm, since the belt's eviction bundle carries it and a reuse would not."""
    rest = [x for x in shas if strict or not commit_is_state(c, x)]
    if not rest:
        return False
    cherry = cherry_on_origin(c, set(rest))
    return any(x not in cherry and not commit_content_on_origin(c, x) for x in rest)


def clone_unpushed(c: Path, strict: bool = False) -> list[str]:
    """What this clone holds that no remote ref does and origin/main does not hold under another hash: commits, a stash,
    dirty or untracked files. Empty = nothing at risk. Fails closed: a clone git cannot read reports itself unreadable."""
    out = []
    try:
        shas = git("rev-list", "--branches", "--tags", "--not", "--remotes", cwd=c, timeout=120).split()
        # a worker's trailing lesson/ledger commit is carried by relentless's eviction bundle (POOL_STATE_COMMITS_PIN_CLONE_FOREVER):
        # it must not read as stranded work, or the alarm fires on a clone the belt can already release
        if commits_at_risk(c, shas, strict):
            out.append("commits")
        if git("stash", "list", cwd=c, timeout=60):
            out.append("stash")
        if dirty_beyond_origin(c):
            out.append("dirty")
    except Exception as e:
        out.append("unreadable: " + str(e)[:80])
    return out


def clone_in_use(c: Path) -> bool:
    me = os.getpid()
    pre = str(c) + os.sep
    for d in glob.glob("/proc/[0-9]*"):
        if d == f"/proc/{me}":
            continue
        try:
            cwd = os.readlink(d + "/cwd")
        except OSError:
            continue
        if cwd == str(c) or cwd.startswith(pre):
            return True
    return False


def pool_state_files() -> list[str]:
    """Every relentless item's state file: relentless.py Store writes store/items/<item>/state.json."""
    return glob.glob(os.environ.get("RM_POOL_STATE_GLOB", str(RM / "relentless" / "store" / "items" / "*" / "state.json")))


def owned_by_item(c: Path) -> bool:
    """A live relentless item names this clone as its work, check or help clone and is not put down. The belt owns it then, and a
    live game phase keeps it on purpose, so the idle hour does not make it stranded (POOL_STATE_COMMITS_PIN_CLONE_FOREVER). A held,
    blocked or game-waiting item's clone is released at once with all it holds, so one still standing here idle for the hour is
    work release_parked could not carry, and that is the alarm (POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG)."""
    for f in pool_state_files():
        try:
            st = json.loads(Path(f).read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(st, dict) or st.get("status") in ("done", "retired", "held", "blocked"):
            continue
        if st.get("status") == "game" and (st.get("game") or {}).get("phase") not in ("staging", "proving"):
            continue
        for h in (st, st.get("check"), st.get("help")):
            if isinstance(h, dict) and h.get("clone") and os.path.abspath(h["clone"]) == str(c):
                return True
    return False


def clone_idle_s(c: Path) -> float:
    newest = 0.0
    for n in (".git/index", ".git/HEAD", ".git/FETCH_HEAD", ".git/logs/HEAD", ".git/relentless"):
        try:
            newest = max(newest, (c / n).stat().st_mtime)
        except OSError:
            pass
    return time.time() - newest if newest else 0.0


_REFRESH_LOCK = threading.Lock()
_PRINTS_LOCK = threading.Lock()
POOL_READ_THREADS = 8


def _per_clone(fn, clones: list) -> list:
    """fn over every clone, in order, POOL_READ_THREADS at a time. Each clone's reading is git subprocesses and a tree walk,
    so threads overlap the waits: the disk family read 16 pool clones in 8.8 s one by one (2026-11-05), past the metronome's
    15 s sense limit beside its pair. Still a live read of every clone each pass; an exception in any clone raises, as before."""
    if len(clones) < 2:
        return [fn(c) for c in clones]
    with ThreadPoolExecutor(max_workers=min(POOL_READ_THREADS, len(clones))) as ex:
        return list(ex.map(fn, clones))


def level_origin_ref(c: Path, refreshed: list) -> bool:
    """Bring an idle clone's origin/main up to the store's, so a verdict is not against a ref a day old; the store is refreshed
    once per reading, from the mirror (rm-mirror.timer, minutes behind GitHub against an hour's idle). No FETCH_HEAD: it is
    one of clone_idle_s's clocks, and a reading that wrote it would keep every clone it looks at from ever going idle.
    False = the ref stayed as it was; the verdict then errs toward stranded."""
    with _REFRESH_LOCK:      # pool_reading levels clones from threads: the store is refreshed once, before any fetch from it
        try:
            if not refreshed:
                refreshed.append(True)
                refresh()
        except Exception:
            pass     # a stale store still levels a staler clone
    try:
        git("fetch", "-q", "--no-write-fetch-head", "--no-auto-maintenance", "--no-tags", str(store_path()),
            f"+{STORE_REF}:refs/remotes/origin/main", cwd=c, timeout=120)
        return True
    except Exception:
        return False


# The sizes ops_watch's disk sense reads (pool_reading(cached_sizes=True)). Danger the age guards: a clone that grew since
# its last walk. Free space on / is read live every pass, so a filling disk is never hidden; a stale size moves only the
# floor margin's "largest clone" term. A walk of every clone took 37.9 s in series at load 29 on 2026-11-22, past the
# sense phase's 15 s kill (RIMMANDRAKE_UNBLIND_OPS_DISK_FAMILY_TWENTY_OVERRUNS_STRAIGHT). The disk family runs about every
# 12 min, so SIZE_WALKS_PER_PASS of 16 clones refreshes every size within SIZE_MAX_AGE_S.
SIZE_MAX_AGE_S = 3600
SIZE_WALKS_PER_PASS = 4


def _sizes_path() -> Path:
    return state_dir() / "pool_sizes.json"


def _sizes_to_walk(clones: list, now: float) -> tuple[set, dict]:
    """-> (names to walk this pass, {name: (bytes, epoch)} usable as is). A clone with no size, a size past
    SIZE_MAX_AGE_S, or a size older than the clone's own directory (a clone made again under the same name) is walked;
    then the SIZE_WALKS_PER_PASS oldest of the rest."""
    try:
        rec = json.loads(_sizes_path().read_text())
        rec = rec if isinstance(rec, dict) else {}
    except (OSError, ValueError):
        rec = {}
    walk, have = set(), {}
    for c in clones:
        r = rec.get(c.name)
        try:
            born = c.stat().st_ctime
        except OSError:
            born = now
        ok = (isinstance(r, dict) and isinstance(r.get("bytes"), int) and isinstance(r.get("epoch"), (int, float))
              and now - SIZE_MAX_AGE_S < r["epoch"] <= now + 60 and r["epoch"] >= born)
        if ok:
            have[c.name] = (r["bytes"], r["epoch"])
        else:
            walk.add(c.name)
    for name in sorted(have, key=lambda n: have[n][1])[:SIZE_WALKS_PER_PASS]:
        walk.add(name)
    return walk, {n: v for n, v in have.items() if n not in walk}


class PoolUnreadable(OSError):
    """The pool root exists and this process may not look (a walled unit). ops_watch turns it into its 9999 alarm."""


def pool_reading(risk: bool = True, cached_sizes: bool = False) -> dict:
    """Live: count, bytes, oldest clone, and every idle clone with unpushed work. Written to pool.json for RimPulse.
    A clone someone is using (touched within the idle hour, a process's cwd, or named by a live item) can never be stranded,
    so its git reading is skipped and it is listed as busy: reading every clone's unpushed commits cost the ops_watch disk
    family ~1000 git spawns a pass and pushed the metronome's sense phase past its 15 s limit
    (DISK_COLLECTOR_SHRINK_THOUSAND_FORKS_A_BEAT). `risk=False` (count and bytes only: the reaper's sanity) reads no git
    at all and writes no pool.json, as its unpushed and stranded lists are not a reading. `cached_sizes=True` (ops_watch's
    disk sense only) takes a clone's bytes from its last walk when that is under SIZE_MAX_AGE_S old and walks the rest
    (_sizes_to_walk); the count, free space and git readings stay live. Every other caller walks every clone."""
    root, cmax = pool_root(), pool_cap()
    try:
        os.listdir(root)     # is_dir() is False on a denied parent too: a blind look is not an empty pool, and writes no reading
    except FileNotFoundError:
        pass
    except OSError as e:
        raise PoolUnreadable(f"{root}: {e.strerror}") from e
    refreshed: list = []
    now = time.time()

    def one(c: Path) -> dict:
        try:
            born = c.stat().st_ctime
        except OSError:
            born = now
        # unpushed work in a clone someone is working in is the job; unpushed work nobody touches for an hour is stranded.
        # The cheap gates first: idle is read before git touches anything in it, and a busy clone's git is never read.
        busy = not risk or clone_idle_s(c) < POOL_IDLE_S or clone_in_use(c) or owned_by_item(c)
        unp = None if busy else clone_unpushed(c)
        stranded = bool(unp)
        if stranded and level_origin_ref(c, refreshed):     # only a clone about to alarm is worth the fetch, and it is idle
            unp = clone_unpushed(c)
            stranded = bool(unp)
        b, at = have[c.name] if c.name in have else (clone_bytes(c), time.time())
        return {"name": c.name, "bytes": b, "size_epoch": at, "age_h": round((now - born) / 3600, 2),
                "unpushed": unp, "busy": busy, "stranded": stranded}

    clones = [c for c in (sorted(root.glob("*")) if root.is_dir() else []) if (c / ".git").exists()]
    if cached_sizes:
        walk, have = _sizes_to_walk(clones, now)
    else:
        walk, have = {c.name for c in clones}, {}
    rows = _per_clone(one, clones)
    if cached_sizes:
        try:
            _sizes_path().write_text(json.dumps({r["name"]: {"bytes": r["bytes"], "epoch": r["size_epoch"]} for r in rows}))
        except OSError:
            pass
    tot = sum(r["bytes"] for r in rows)
    held = [r["name"] for r in rows if r["stranded"]]
    d = {"ts": now_iso(), "epoch": now, "root": str(root), "count": len(rows), "max_clones": cmax,
         "bytes": tot, "gb": round(tot / 1e9, 2),
         "oldest_h": max([r["age_h"] for r in rows], default=0.0), "unpushed": [r["name"] for r in rows if r["unpushed"]],
         "busy": [r["name"] for r in rows if r["busy"]], "stranded": held, "clones": rows,
         "sizes_oldest_s": round(max([now - r["size_epoch"] for r in rows], default=0.0), 1)}
    d.update(floor_reading(max((r["bytes"] for r in rows), default=0)))
    # under the floor, or a floor nobody can read: both refuse every new clone, so both are a breach
    d["breach"] = int(len(rows) > cmax) + int(d["margin_gb"] is None or d["margin_gb"] < 0) + len(held)
    if not risk:
        return d
    try:
        (state_dir() / "pool.json").write_text(json.dumps(d))
    except OSError:
        pass
    return d


# Every other helper clone. LIQUIDNET_SURFACEGAP_FIX_UNLANDED_CLONES: two clones under rm/scratch sat four days holding work
# nothing alarmed on, because the pool reading above sees only relentless/clones and the reaper only reports what it may delete.
# Tracking refs prove nothing here (a clone's origin may be a seat clone, and a stale one reads "ahead 8" after a rewrite):
# only the mirror proves a push, as in scratch_reap. A pre-rewrite clone's commits are excused by main carrying the same author
# AND committer second: the rewrite changed subjects, emails and blobs (measured on 56 commits of liquidnet_shrink), never dates.
SCRATCH_SCAN_DEPTH = 5
_MAIN_PRINTS: set | None = None
_MAIN_BY_SUBJECT: dict = {}     # subject -> [main sha]: a landing keeps it (RIMMANDRAKE_EXEMPT_LANDED_PRESYNC_BACKUPS_...)


def scratch_clone_dirs() -> list[Path]:
    """Clones under rm/scratch, and those of this repo in agents' session dirs. Not the rest of ~/.seat-tmp: 1,400 selftest
    fixtures live there, and 499 of the 512 session rows measured on 2026-11-01 were toy repos a test had made."""
    import scratch_reap as sr
    out = set(sr.find_clones(scratch_root(), depth=SCRATCH_SCAN_DEPTH))
    for s in glob.glob(os.environ.get("RM_SESSION_GLOB", str(Path.home() / ".seat-tmp/*/claude-*/*/*"))):
        for c in sr.find_clones(Path(s), depth=SCRATCH_SCAN_DEPTH):
            if any(n in sr.git(c, "remote", "-v").stdout for n in ("RimMandrake", str(RM) + "/")):
                out.add(c)
    return sorted(out)


def main_prints() -> set:
    """{"author-second committer-second"} on main. Asked only when a clone holds commits the mirror's refs do not reach."""
    with _PRINTS_LOCK:       # scratch_stranded's threads: one git log of main, not one each
        return _main_prints()


def _main_prints() -> set:
    global _MAIN_PRINTS, _MAIN_BY_SUBJECT
    if _MAIN_PRINTS is None:
        import scratch_reap as sr
        r = sr.git(sr.origin_mirrors()[0], "log", "-z", sr.mirror_tips()[0], "--format=%at %ct %H%x1f%s")
        if r.returncode:
            raise RuntimeError("cannot read main on the mirror")
        prints, by_subject = set(), {}
        for at, ct, h, subject in split_log(r.stdout):
            prints.add(at + " " + ct)
            by_subject.setdefault(subject, []).append(h)
        _MAIN_PRINTS, _MAIN_BY_SUBJECT = prints, by_subject
    return _MAIN_PRINTS


def split_log(out: str) -> list[tuple[str, str, str, str]]:
    """`git log -z --format=%at %ct %H%x1f%s` -> [(at, ct, sha, subject)]. NUL-framed: a subject holding U+2028 or any other
    splitlines() separator crashed the scan (review, 2026-11-15); the head before the first \x1f never holds one."""
    rows = []
    for rec in out.split("\0"):
        head, _, subject = rec.strip("\n").partition("\x1f")
        parts = head.split()
        if len(parts) == 3:
            rows.append((parts[0], parts[1], parts[2], subject))
    return rows


_PATCH_IDS: dict = {}
MAX_TWINS = 20      # main commits sharing one subject asked per clone commit; past it the commit is work (fails closed)


def patch_id(repo: Path, sha: str) -> str | None:
    """git patch-id --verbatim of one commit, or None (a merge, an empty commit, or anything git cannot read). Verbatim:
    --stable ignores whitespace, so `"a b"` and `"ab"` matched (review, 2026-11-15). Cached per sha."""
    key = (str(repo), sha)
    if key not in _PATCH_IDS:
        _PATCH_IDS[key] = _patch_id(repo, sha)
    return _PATCH_IDS[key]


def _patch_id(repo: Path, sha: str) -> str | None:
    import scratch_reap as sr
    show = sr.git(repo, "show", "--no-color", "--format=commit %H", sha)
    if show.returncode or not show.stdout.strip():
        return None
    r = sr.git(repo, "patch-id", "--verbatim", stdin=show.stdout)
    return (r.stdout.split() or [None])[0] if r.returncode == 0 else None


def rebased_on_main(c: Path, sha: str, subject: str) -> bool:
    """RIMMANDRAKE_EXEMPT_LANDED_PRESYNC_BACKUPS_REBASE_HID_THE_PRINT: seat_sync rebases a clone's commit onto main and keeps
    the original on a backup/*-pre-sync-* branch. The landed twin keeps the subject and the patch, not the author or committer
    second (both moved 19-40 s on two real twins, 2026-11-15). Only main's commits of the same subject are asked, so a reading
    stays a few patch-ids, not a day of main (21 s measured). A subject main has reverted, more than MAX_TWINS twins, no patch,
    or any doubt is work."""
    import scratch_reap as sr
    twins = _MAIN_BY_SUBJECT.get(subject) or []
    if not subject or 'Revert "%s"' % subject in _MAIN_BY_SUBJECT or len(twins) > MAX_TWINS:
        return False
    mine = patch_id(c, sha) if twins else None
    return bool(mine) and any(patch_id(sr.origin_mirrors()[0], h) == mine for h in twins)


def ledger_commit_on_mirror(c: Path, sha: str, tip: str) -> bool:
    """RIMMANDRAKE_EXCUSE_STRANDED_LEDGER_COMMIT_MAIN_HOLDS_ITS_LINES: a single-parent commit that touches only POOL_NOISE
    .jsonl shards, each of whose lines at that commit the mirror's main (tip) already holds. A helper's ledger close that its
    ./publish re-made on a newer main lands under another hash and another patch (the append's context moved), so neither the
    print nor rebased_on_main sees it (2026-11-23: a false strand took a disk incident to his rung). A deletion, any other
    path, an unreadable blob, or any doubt is work."""
    import scratch_reap as sr
    try:
        if len(sr.git(c, "rev-list", "--parents", "-n1", sha).stdout.split()) != 2:
            return False
        r = sr.git(c, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", sha)
        files = [f for f in r.stdout.split("\0") if f]
        if r.returncode or not files or not all(f.startswith(POOL_NOISE) and f.endswith(".jsonl") for f in files):
            return False
        for f in files:
            mine, theirs = sr.git(c, "cat-file", "blob", f"{sha}:{f}"), sr.git(c, "cat-file", "blob", f"{tip}:{f}")
            if mine.returncode or theirs.returncode or not holds_content(
                    f, mine.stdout.encode("utf-8", "surrogateescape"), theirs.stdout.encode("utf-8", "surrogateescape")):
                return False
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def is_foreign_repo(c: Path, tip: str) -> bool:
    """True when the clone is of another repo than the mirror (no root commit in common): the mirror cannot prove a push
    there, so only the clone's own remote refs can (a foreign clone has no stale shared lender). Any doubt: not foreign.
    Seen 2026-11-25: a Codex lane's MandrakeWorkflows-dev clone read 1787 commits on no remote (seats incident)."""
    import scratch_reap as sr
    mine, theirs = (sr.git(x, "rev-list", "--max-parents=0", ref) for x, ref in ((c, "HEAD"), (sr.origin_mirrors()[0], tip)))
    if mine.returncode or theirs.returncode or not mine.stdout.split() or not theirs.stdout.split():
        return False
    return not set(mine.stdout.split()) & set(theirs.stdout.split())


def clone_unlanded(c: Path) -> tuple[list[str], float]:
    """(what this clone alone holds, mtime of its newest dirty file). Branches, HEAD and stash; a tag is an archive, not work.
    Fails closed: what git cannot read reports itself unreadable."""
    import scratch_reap as sr
    tips = sr.mirror_tips()
    if not tips:
        raise RuntimeError("no mirror to judge a push against")
    foreign = is_foreign_repo(c, tips[0])
    if foreign:     # the mirror cannot prove a push of another repo: its own remote refs do
        tips = tips + sr.git(c, "for-each-ref", "--format=%(objectname)", "refs/remotes/").stdout.split()
    r = sr.git(c, "rev-list", "--ignore-missing", "--exclude=refs/remotes/*", "--exclude=refs/tags/*", "--all", "--stdin",
               stdin="".join(f"^{t}\n" for t in tips))
    if r.returncode:
        return ["unreadable: " + r.stderr.strip()[:80]], 0.0
    out = []
    if r.stdout.split():
        d = sr.git(c, "log", "-z", "--no-walk=unsorted", "--stdin", "--format=%at %ct %H%x1f%s", stdin=r.stdout)
        if d.returncode:
            return ["unreadable: the commits the mirror lacks"], 0.0
        prints = main_prints()
        n = sum(at + " " + ct not in prints and not rebased_on_main(c, h, subject) and not ledger_commit_on_mirror(c, h, tips[0])
                for at, ct, h, subject in split_log(d.stdout))
        if n:
            out.append(f"{n} commit(s) on no remote")
    st = sr.git(c, "status", "--porcelain=v1", "-z", "--untracked-files=normal")
    if st.returncode:
        return out + ["unreadable: " + st.stderr.strip()[:80]], 0.0
    recs, paths, i = st.stdout.split("\0"), [], 0
    while i < len(recs):
        x = recs[i]
        i += 1
        if len(x) >= 4:
            i += x[0] in "RC"                # -z: the old name is the next field
            if not sr.disposable(x[3:]) and not x.endswith((".dll", ".dll.srchash")):      # a build writes those again
                paths.append(x[3:])
    # SCRATCH_STRANDED_FIX_SHARDS_CRY_WOLF: a helper's ledger/review shard whose every line main already holds is not work.
    # Judged against the mirror's main, never the clone's own origin/main (a --shared clone's ref is days stale).
    paths = [p for p in paths if not noise_on_mirror(c, p, tips[0])]
    newest = 0.0
    for p in paths:
        try:
            newest = max(newest, os.lstat(c / p).st_mtime)
        except OSError:
            pass
    if paths:
        out.append(f"{len(paths)} dirty file(s)")
    return out, newest


def noise_on_mirror(c: Path, path: str, tip: str) -> bool:
    """A dirty file whose content the mirror's main (tip) already holds: a POOL_NOISE record by holds_content, any other path
    only byte for byte (RIMMANDRAKE_EXCUSE_STRANDED_FILES_MAIN_HOLDS_BYTE_FOR_BYTE: a dead session's copy of edits main landed
    under another hash). A deletion, an unreadable file or blob, or any doubt is not covered."""
    import scratch_reap as sr
    try:
        f = c / path
        if f.is_symlink() or not f.is_file():
            return False
        r = sr.git(c, "cat-file", "blob", f"{tip}:{path}")
        theirs = r.stdout.encode("utf-8", "surrogateescape") if r.returncode == 0 else None
        if not path.startswith(POOL_NOISE):
            return theirs is not None and f.read_bytes() == theirs
        return holds_content(path, f.read_bytes(), theirs)
    except (OSError, subprocess.SubprocessError):
        return False


def scratch_stranded() -> dict:
    """Live: every helper clone holding work nowhere else that nobody has touched for an hour. A clone on the reaper's PROTECTED
    list counts like any other: protected from deletion is not excused from landing. Written for RimPulse; ops_watch alarms."""
    now = time.time()
    import scratch_reap as sr
    sr.mirror_tips()     # its cache fills by appending: fill it before the threads read it
    # A detached or role run's clones sit under rm/scratch/<its seat>/ (seat(): the scope name less its number). While
    # that run lives they are its work, landed in turn, not stranded: 6 Codex clones of a live run read stranded on
    # 2026-11-25 (OPS_WORKER_CLONE_POOL_RESTORE_HMOQ_PBAL). Only a unit's seat dir ("-rm-" in it) is excused: a bare
    # seat such as BENCH is always live, and would excuse its clones for good. When the run ends, the excuse ends.
    live = {s for s in live_seats() if "-rm-" in s}
    root = scratch_root()

    def owner_live(c: Path) -> bool:
        try:
            rel = c.relative_to(root)
        except ValueError:
            return False
        return len(rel.parts) > 1 and rel.parts[0] in live

    def one(c: Path) -> dict | None:
        idle = clone_idle_s(c)               # read before git touches anything in it
        risk, newest = clone_unlanded(c)
        if not risk:
            return None
        idle = min(idle, now - newest) if newest else idle
        row = {"path": str(c), "holds": risk, "idle_h": round(idle / 3600, 2), "stranded": False}
        if owner_live(c):
            row["owner_live"] = True
        else:
            row["stranded"] = idle >= POOL_IDLE_S and not clone_in_use(c)
        return row

    rows = [r for r in _per_clone(one, scratch_clone_dirs()) if r is not None]
    d = {"ts": now_iso(), "epoch": now, "stranded": [r["path"] for r in rows if r["stranded"]], "rows": rows}
    try:
        (state_dir() / "scratch_stranded.json").write_text(json.dumps(d))
    except OSError:
        pass
    return d


def pool_admit(dest: Path, reading: dict | None = None) -> str | None:
    """None = may create; else the refusal. Called before any pool clone is made."""
    if dest.parent != pool_root():
        return None
    r = reading or pool_reading(risk=False)     # count, sizes and free space are all it asks
    cmax = pool_cap()
    if r["count"] >= cmax:
        return f"pool full: {r['count']} clones, cap {cmax} (no idle clone to reuse); finish or push one, then retry"
    if r.get("floor_error"):
        return r["floor_error"]
    if r["margin_gb"] < 0:
        return (f"disk floor: {r['root_free_gb']} GB free on /, less the largest clone ({r['largest_clone_gb']} GB), is under "
                f"the {r['floor_gb']:.0f} GB floor (ops.`{FLOOR_KEY}` in slot_rules.json, the DISK_LOW line); free disk or "
                f"remove a finished clone, then retry")
    return None


def pool_reuse(dest: Path, fetch: bool = False) -> Path | None:
    """Reuse before create: an idle, fully pushed, unowned pool clone is renamed to dest and brought level with origin.
    `fetch` asks origin itself, as `clone --fetch` does: the store is seeded from the mirror, which lags origin, and a
    reuse that skipped it left a just-published sha absent ("unable to read tree"), opened the belt's breaker and held
    it under target (OPS_RELENTLESS_UNSTICK_XARX, 2026-11-02)."""
    root = pool_root()
    if dest.parent != root:
        return None
    named = ""
    for f in pool_state_files():
        try:
            named += Path(f).read_text()
        except OSError:
            pass
    # a warm clone (relentless_disk.park: WIP bundled, reset level and clean) is ready now; any other waits its idle hour
    for c in sorted(root.glob("*"), key=lambda p: (not p.name.startswith(POOL_WARM), -clone_idle_s(p))):
        if c == dest or not (c / ".git").exists() or str(c) in named:
            continue
        idle_ok = c.name.startswith(POOL_WARM) or clone_idle_s(c) >= POOL_IDLE_S
        if not idle_ok or clone_in_use(c) or clone_unpushed(c, strict=True):   # reuse resets to main: no commit may be dropped
            continue
        try:
            os.rename(c, dest)
            # a help-* consult clone was gagged (pushurl=read-only-consult, relentless.help_checkout); a worker must push
            # to origin, or its ./publish dies "read-only-consult does not appear to be a git repository"
            git("config", "--unset-all", "remote.origin.pushurl", cwd=dest, check=False)
            # a clone that last served a relentless lease keeps its fence marker; the new owner's pre-push hook would refuse
            # every push in that stranger's name (HELPERCLONE_FIX_STALE_FENCE_OF_A_STRANGER). A relentless lease writes its own.
            try:
                (dest / ".git" / "relentless.json").unlink()
            except FileNotFoundError:
                pass
            try:
                refresh()
            except Exception:
                pass     # a stale store still serves a level checkout, as `clone` does
            git("fetch", "-q", str(store_path()), f"+{STORE_REF}:refs/remotes/origin/main", cwd=dest, timeout=900)
            if fetch:
                git("fetch", "-q", "origin", cwd=dest, timeout=900)
            git("checkout", "-q", "-B", "main", "refs/remotes/origin/main", cwd=dest)    # on main, as a fresh clone is
            # the last run's ignored output (a 7 GB Saves backup), publish checkouts and loose ledger blobs went with
            # every reuse: reused clones measured 11-16 GB against 4.5 GB fresh (2026-11-22)
            shed(dest)
            set_identity(dest)      # a clone made before the identity rule commits as the noreply one from now on
            return dest
        except Exception:
            if dest.exists() and not c.exists():
                os.rename(dest, c)
    return None


# ---------------------------------------------------------------- periodic sample

def find_borrowers() -> list[dict]:
    seen, out = set(), []
    for pat in scan_patterns():
        for d in glob.glob(pat):
            for alt in (Path(d) / ".git/objects/info/alternates", Path(d) / "objects/info/alternates"):
                if alt.is_file() and str(alt) not in seen:
                    seen.add(str(alt))
                    try:
                        targets = [t.strip() for t in alt.read_text().splitlines() if t.strip()]
                    except OSError:
                        continue
                    out.append({"repo": d, "alternates": targets, "kind": classify(targets)})
    return out


def classify(targets: list[str]) -> str:
    st = os.path.realpath(store_path() / "objects")
    real = [os.path.realpath(t) for t in targets]
    if st in real:
        return "store"
    for t in real:
        for s in SEATS:
            if t.startswith(str(RM / s) + "/"):
                return "seat"
    return "other"


def borrower_ok(repo: str, deep: bool) -> tuple[bool, str]:
    try:
        git("-C", repo, "cat-file", "-e", "HEAD^{tree}", timeout=60)
        if deep:
            git("-C", repo, "fsck", "--connectivity-only", "--no-progress", timeout=300)
        return True, ""
    except Exception as e:
        return False, str(e)


def sample() -> dict:
    rec = {"ts": now_iso()}
    st = store_path()
    rec["store_exists"] = (st / "HEAD").exists()
    if rec["store_exists"]:
        try:
            rec.update(refresh())
        except Exception as e:
            rec["refresh_error"] = str(e)
        own, linked = own_bytes(st)
        rec.update({"store_own_bytes": own, "store_hardlinked_bytes": linked})
        try:
            rec["store_objects"] = store_objects()["objects"]
        except Exception as e:
            rec["store_objects_error"] = str(e)
    bs = find_borrowers()
    on_store = [b for b in bs if b["kind"] == "store"]
    rec.update({"borrowers_store": len(on_store),
                "borrowers_seat": len([b for b in bs if b["kind"] == "seat"]),
                "borrowers_other": len([b for b in bs if b["kind"] == "other"]),
                "borrowers_seat_paths": [b["repo"] for b in bs if b["kind"] == "seat"]})
    deep = random.choice(on_store)["repo"] if on_store else None
    bad = []
    t0 = time.time()
    for b in on_store:
        ok, err = borrower_ok(b["repo"], deep=(b["repo"] == deep))
        if not ok:
            bad.append(b["repo"])
            append("incidents.jsonl", {"ts": rec["ts"], "repo": b["repo"], "error": err,
                                       "alternates": b["alternates"], "deep": b["repo"] == deep})
    rec.update({"check_s": round(time.time() - t0, 2), "fsck_sampled": deep, "borrowers_broken": bad})
    vs = os.statvfs(str(RM if RM.exists() else Path.home()))
    rec["disk_free_bytes"] = vs.f_bavail * vs.f_frsize
    append("samples.jsonl", rec)
    return rec


def baseline() -> dict:
    """One real full copy of the store (`--no-local`: objects re-packed and written, as a network
    clone would, minus the network) — a LOWER bound on what a non-borrowing clone costs."""
    dest = scratch_root() / seat() / f"_objstore_baseline_{os.getpid()}"
    t0 = time.time()
    try:
        git("clone", "-q", "--no-local", "--no-checkout", str(store_path()), str(dest), timeout=3600)
        rec = {"ts": now_iso(), "full_clone_s": round(time.time() - t0, 2),
               "full_git_dir_bytes": sum(own_bytes(dest / ".git")), "method": "clone --no-local --no-checkout"}
    finally:
        shutil.rmtree(dest, ignore_errors=True)
    append("baseline.jsonl", rec)
    return rec


# ---------------------------------------------------------------- report

def gb(n) -> str:
    return f"{n / 1e9:.1f} GB"


def report() -> str:
    uses, samples = read_jsonl("uses.jsonl"), read_jsonl("samples.jsonl")
    incidents, base = read_jsonl("incidents.jsonl"), read_jsonl("baseline.jsonl")
    ok = [u for u in uses if u.get("ok")]
    failed = [u for u in uses if not u.get("ok")]
    bsec = base[-1]["full_clone_s"] if base else None
    clone_s = sorted(u.get("clone_s", 0) for u in ok)
    med = clone_s[len(clone_s) // 2] if clone_s else None
    t_saved = sum(max(bsec - u.get("clone_s", 0), 0) for u in ok) if bsec is not None else None
    d_saved = sum(max(u.get("full_clone_objects_bytes", 0) - u.get("git_dir_own_bytes", 0), 0) for u in ok)
    last = samples[-1] if samples else {}
    seats = {}
    for u in uses:
        seats[u.get("seat", "?")] = seats.get(u.get("seat", "?"), 0) + 1
    rows = [
        ("clones made (ok / failed)", f"{len(ok)} / {len(failed)}"),
        ("by seat", ", ".join(f"{k} {v}" for k, v in sorted(seats.items())) or "-"),
        ("median clone time", f"{med:.2f} s" if med is not None else "-"),
        ("full-copy baseline", f"{bsec:.0f} s (lower bound)" if bsec is not None else "UNMEASURED (run baseline)"),
        ("time saved, total", f"{t_saved / 60:.1f} min" if t_saved is not None else "UNMEASURED"),
        ("disk saved at creation, total", gb(d_saved)),
        ("corruption incidents", str(len(incidents))),
        ("samples taken", f"{len(samples)} (last {last.get('ts', '-')})"),
        ("store size (own / hard-linked)", f"{gb(last.get('store_own_bytes', 0))} / {gb(last.get('store_hardlinked_bytes', 0))}" if last else "-"),
        ("borrowers now: store / seat clone / other", f"{last.get('borrowers_store', '-')} / {last.get('borrowers_seat', '-')} / {last.get('borrowers_other', '-')}"),
        ("disk free", gb(last["disk_free_bytes"]) if last.get("disk_free_bytes") else "-"),
    ]
    if incidents:
        verdict = "BAD — a borrower lost objects; read incidents.jsonl"
    elif not ok:
        verdict = "NO DATA — nobody has used it yet"
    elif len(failed) > 0.1 * len(uses):
        verdict = "MIXED — more than 10% of clone calls failed; read uses.jsonl errors"
    else:
        verdict = "GOOD so far — no corruption, failures under 10%"
    w = max(len(r[0]) for r in rows)
    lines = [f"objstore trial ({state_dir()})", ""] + [f"  {k.ljust(w)}  {v}" for k, v in rows]
    if last.get("borrowers_seat"):
        ps = last["borrowers_seat_paths"]
        lines.append(f"  !! {len(ps)} repo(s) still borrow from a seat clone (finding #8): "
                     + ", ".join(ps[:3]) + (" ..." if len(ps) > 3 else ""))
    if failed:
        lines.append(f"  last failure: {failed[-1].get('error')}")
    lines += ["", f"  VERDICT: {verdict}"]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("clone", help="make a throwaway clone under /home/mandrake/rm/scratch/<SEAT>/")
    c.add_argument("purpose", help="what it is for — recorded")
    c.add_argument("--name")
    g = c.add_mutually_exclusive_group()
    g.add_argument("--sparse", nargs="+", default=[], metavar="PATH",
                   help="dirs the task needs, added to the default cone (%s)" % ", ".join(BASE_CONE))
    g.add_argument("--checkout", action="store_true",
                   help="whole working tree (~4 GB): pool clones and repo-wide work only")
    g.add_argument("--no-checkout", action="store_true", help="no working tree (git inspection only)")
    c.add_argument("--fetch", action="store_true", help="also fetch origin (GitHub) after cloning")
    c.add_argument("--dissociate", action="store_true", help="durable clone: no alternates (hard-linked packs)")
    for n in ("init", "refresh", "sample", "baseline", "report", "pool"):
        sub.add_parser(n)
    a = ap.parse_args(argv)
    if a.cmd == "clone":
        return clone(a.purpose, a.name, a.checkout, a.sparse, a.fetch, a.dissociate, a.no_checkout)
    if a.cmd == "report":
        print(report())
        return 0
    if a.cmd == "pool":
        try:
            r = pool_reading()
        except PoolUnreadable as e:     # say so, and show the last reading made from outside the wall, with its age
            try:
                last = json.loads((state_dir() / "pool.json").read_text())
            except (OSError, ValueError):
                last = None
            print(json.dumps({"unreadable": str(e), "last_reading": last}))
            return 3
        s = scratch_stranded()
        print(json.dumps({**{k: v for k, v in r.items() if k != "clones"}, "scratch_stranded": s["stranded"]}))
        return 1 if r["breach"] or s["stranded"] else 0
    out = {"init": init, "refresh": refresh, "sample": sample, "baseline": baseline}[a.cmd]()
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
