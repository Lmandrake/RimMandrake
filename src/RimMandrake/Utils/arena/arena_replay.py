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
  schedule            per-arm run order: a seeded shuffle, seed = sha256(freeze_hash, arm). Reproducible from the seed; two
                      arms never get the same order (when more than one order exists). interleave() merges the arms' orders
                      round-robin (arm order re-shuffled each round from the same seed) into one slot list.
  run_one             build -> work -> judge -> delete, deletion in `finally`, so a failure also leaves nothing.
  leftovers / sweep   clones still on disk; `rm-scratch-reap` also has the replay tree among its roots.
Tests use a temp root: RM_ARENA_ROOT or the root= argument. Nothing here touches the source repo except `git fetch` reads.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = "/home/mandrake/rm/arena"
DEFAULT_SOURCE = "/home/mandrake/rm/bench"
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,100}$")
SHA = re.compile(r"^[0-9a-f]{40}$")


class ReplayError(Exception):
    pass


class ReplayLeak(ReplayError):
    pass


def arena_root(root=None) -> Path:
    r = Path(root) if root else Path(os.environ.get("RM_ARENA_ROOT") or DEFAULT_ROOT)
    if str(r.resolve()).startswith("/mnt/"):
        raise ReplayError("arena root %s is on a Windows mount: arm clones live on ext4" % r)
    return r


def replay_dir(root=None) -> Path:
    return arena_root(root) / "replay"


def clone_path(arm: str, task: str, root=None) -> Path:
    for what, v in (("arm", arm), ("task", task)):
        if not NAME.match(v) or v in (".", ".."):
            raise ReplayError("bad %s name %r" % (what, v))
    return replay_dir(root) / arm / task


def _git(repo: Path, *args, env=None, check=True) -> str:
    e = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_OBJECT_DIRECTORY", "GIT_INDEX_FILE"):
        e.pop(k, None)
    e.update(env or {})
    r = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True, text=True, env=e, timeout=300)
    if check and r.returncode:
        raise ReplayError("git %s failed: %s" % (" ".join(args[:2]), r.stderr.strip()[:300]))
    return r.stdout


def rmtree(path: Path):
    def onerr(fn, p, exc):
        try:
            os.chmod(os.path.dirname(p), stat.S_IRWXU)
            os.chmod(p, stat.S_IRWXU)
            fn(p)
        except OSError:
            pass
    if path.is_symlink():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path, onerror=onerr)
    if path.exists() or path.is_symlink():
        raise ReplayError("could not delete %s" % path)


def _full(source: Path, sha: str) -> str:
    out = _git(source, "rev-parse", "--verify", "-q", sha + "^{commit}", check=False).strip()
    if not SHA.match(out):
        raise ReplayError("%s is not a commit in %s" % (sha, source))
    return out


# ---------------------------------------------------------------- audit

def audit_clone(clone: Path, forbidden) -> list[str]:
    """-> findings (empty = no forbidden object is reachable). `forbidden` = full shas that must not exist."""
    forbidden = {f.lower() for f in forbidden}
    bad = [f for f in forbidden if not SHA.match(f)]
    if bad:
        raise ReplayError("forbidden shas must be full 40-hex: %r" % bad)
    out: list[str] = []
    gd = clone / ".git"
    if not gd.is_dir() or gd.is_symlink():
        return ["no real .git directory"]
    for f in sorted(forbidden):
        if subprocess.run(["git", "-C", str(clone), "cat-file", "-e", f], capture_output=True).returncode == 0:
            out.append("git cat-file -e finds %s" % f)
        if subprocess.run(["git", "-C", str(clone), "show", "-s", f], capture_output=True).returncode == 0:
            out.append("git show finds %s" % f)
    allobj = _git(clone, "cat-file", "--batch-all-objects", "--batch-check", check=False).split("\n")
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
    refs = _git(clone, "for-each-ref", "--format=%(refname) %(objectname)", check=False).split("\n")
    out += ["ref %s" % r for r in refs if r and any(f in r for f in forbidden)]
    cfg = (gd / "config").read_text(errors="replace") if (gd / "config").exists() else ""
    if re.search(r"^\[(remote|branch|submodule)\b", cfg, re.M):
        out.append("config has a remote/branch/submodule section: the clone can reach its source")
    return out


# ---------------------------------------------------------------- build

def build_replay_clone(arm: str, task: str, base_sha: str, fix_sha: str, source=DEFAULT_SOURCE, root=None,
                       also_forbidden=()) -> Path:
    """Fresh clone holding history up to base_sha only. Raises (leaving nothing behind) when base_sha reaches fix_sha."""
    source = Path(source)
    dest = clone_path(arm, task, root)
    base, fix = _full(source, base_sha), _full(source, fix_sha)
    if base == fix:
        raise ReplayError("base_sha equals fix_sha: nothing to replay")
    if dest.exists() or dest.is_symlink():
        raise ReplayError("%s already exists (a previous clone was not deleted)" % dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest.mkdir()
        _git(dest, "init", "-q", "--template=")
        _git(dest, "config", "gc.auto", "0")
        _git(dest, "fetch", "-q", "--no-tags", "--no-write-fetch-head", str(source), base)
        _git(dest, "-c", "advice.detachedHead=false", "update-ref", "--no-deref", "HEAD", base)
        _git(dest, "reset", "-q", "--hard", base)
        for junk in ("FETCH_HEAD", "ORIG_HEAD", "packed-refs"):
            (dest / ".git" / junk).unlink(missing_ok=True)
        if (dest / ".git" / "logs").exists():
            rmtree(dest / ".git" / "logs")
        findings = audit_clone(dest, [fix, *also_forbidden])
        if findings:
            raise ReplayLeak("replay clone %s/%s can reach the future: %s" % (arm, task, "; ".join(findings)))
        return dest
    except BaseException:
        rmtree(dest)
        raise


# ---------------------------------------------------------------- schedule

def arm_seed(freeze_hash: str, arm: str) -> int:
    return int.from_bytes(hashlib.sha256(("%s|%s" % (freeze_hash, arm)).encode()).digest()[:8], "big")


def arm_order(freeze_hash: str, arm: str, tasks, taken=()) -> list[str]:
    """Seeded shuffle of the task ids for one arm. Deterministic from (freeze_hash, arm, tasks). If the draw equals an
    order already given to another arm (`taken`) it is redrawn from the same stream, so arms differ whenever they can."""
    ts = sorted(set(tasks))
    rng = random.Random(arm_seed(freeze_hash, arm))
    order = ts[:]
    for _ in range(64):
        rng.shuffle(order)
        if tuple(order) not in taken or len(ts) < 2:
            break
    return order


def schedule(freeze_hash: str, arms, tasks) -> dict:
    """-> {"orders": {arm: [task...]}, "slots": [(arm, task)...]} (slots = interleaved across arms)."""
    if not freeze_hash:
        raise ReplayError("a schedule needs the task freeze hash as its seed")
    arms = sorted(set(arms))
    orders: dict[str, list[str]] = {}
    taken: set = set()
    for a in arms:                                   # sorted, so the result never depends on the caller's arm order
        orders[a] = arm_order(freeze_hash, a, tasks, taken)
        taken.add(tuple(orders[a]))
    slots: list = []
    rng = random.Random(arm_seed(freeze_hash, "#interleave"))
    for i in range(len(orders[arms[0]]) if arms else 0):
        rnd = arms[:]
        rng.shuffle(rnd)
        slots += [(a, orders[a][i]) for a in rnd]
    return {"orders": orders, "slots": slots}


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
    gone = leftovers(root)
    for p in gone:
        rmtree(p)
    return gone


def run_one(arm: str, task: str, base_sha: str, fix_sha: str, work, judge, source=DEFAULT_SOURCE, root=None,
            also_forbidden=()):
    """Build the clone, `work(clone)`, `judge(clone)` -> verdict. The clone is deleted whatever happens."""
    clone = None
    try:
        clone = build_replay_clone(arm, task, base_sha, fix_sha, source, root, also_forbidden)
        work(clone)
        return judge(clone)
    finally:
        p = clone_path(arm, task, root)
        rmtree(p)
        if not any(p.parent.iterdir()) if p.parent.is_dir() else False:
            p.parent.rmdir()


def run_schedule(freeze_hash: str, tasks: dict, arms, work, judge, source=DEFAULT_SOURCE, root=None) -> list[dict]:
    """tasks = {task_id: {"base_sha":..., "fix_sha":...}}. Runs the interleaved slots; one failure is recorded and the
    run goes on (its clone is already gone)."""
    results = []
    for arm, task in schedule(freeze_hash, arms, tasks)["slots"]:
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
