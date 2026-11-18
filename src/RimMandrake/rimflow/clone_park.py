"""clone_park.py -- park a returned pool clone as a warm spare or remove it (park, remove_tree, warm_clones, reset_clean).

Moved verbatim from rimflow/relentless_disk.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import time

WARM = "warm-"


def is_warm(c):
    return os.path.basename(c.rstrip("/")).startswith(WARM)


def warm_clones(root):
    return sorted(d for d in glob.glob(os.path.join(root, WARM + "*")) if os.path.isdir(os.path.join(d, ".git")))


def _git(c, *a, timeout=300):
    r = subprocess.run(["git", *a], cwd=c, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (a[0], r.stderr))
    return r.stdout


def gone_ok(func, path, exc):
    """rmtree's onexc: a file already gone is removed, not a failure (the 99 remove_failed ENOENT alarms)."""
    if not isinstance(exc, FileNotFoundError):
        raise exc


def remove_tree(c):
    """-> None when c is gone, else why it stays. A path that vanished under us is gone."""
    try:
        shutil.rmtree(c, onexc=gone_ok)
    except FileNotFoundError:
        pass
    except OSError as e:
        return str(e)
    return None if not os.path.lexists(c) else "still present after the removal"


def reset_clean(c):
    """The clone as a fresh one is: on main at origin/main, no other branch, tag or stash, no file git does not track.
    Only after its WIP is bundled: this drops it."""
    _git(c, "checkout", "-q", "-f", "-B", "main", "refs/remotes/origin/main")
    for ref in _git(c, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/tags", "refs/stash", "refs/rm-stash").split():
        if ref != "refs/heads/main":
            _git(c, "update-ref", "-d", ref)
    _git(c, "reflog", "expire", "--expire=now", "--all")
    _git(c, "clean", "-q", "-ffdx")
    try:
        os.remove(os.path.join(c, ".git", "relentless.json"))      # no fence: the next lease writes its own
    except FileNotFoundError:
        pass


def park(c, root, keep, damage=None):
    """-> the warm path, or None when the caller should remove c instead (a full shelf, a damaged or unreadable clone)."""
    if keep <= 0 or is_warm(c) or len(warm_clones(root)) >= keep:
        return None
    try:
        reset_clean(c)
        if damage and damage(c):         # a file zeroed in place survives a reset: never hand it to the next item
            return None
        if _git(c, "status", "--porcelain", "--untracked-files=all").strip():
            return None
        dest = os.path.join(root, "%s%d" % (WARM, time.time_ns()))
        os.rename(c, dest)
        return dest
    except (RuntimeError, OSError, subprocess.SubprocessError):
        return None
