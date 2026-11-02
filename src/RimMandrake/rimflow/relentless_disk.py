#!/usr/bin/env python3
"""relentless_disk.py - what relentless writes to disk per item, cut to what the item needs.
DISK_CHURN_MEASURE_CLONES_EAT_THE_VHDX. Measured 2026-11-02: every item cost a fresh 3.6 GB worker checkout, a fresh 3.6 GB
checker checkout per check and a ~3.3 GB walled-box export (objects were already shared with the store through
alternates; a clone's .git is ~10 MB). 105 clones were created and deleted in 30 h, and remove_box was never called:
36 boxes, 118 GB, sat in ~/walled. That churn is the likely cause of the sparse WSL disk image's fragmentation (inferred).

Warm clones: a released clone, once its WIP is bundled, is reset to origin/main and parked as clones/warm-<ns> instead of
deleted; scratch_clone's pool_reuse takes a warm clone first, so the next item pays only the files that changed upstream.
A damaged clone is never parked. Boxes: the export tree goes once its check is over and no process is in it; the small
rest (the Marker's transcript, its verdict, the diff) stays for `relentless wall` audit until box_keep_s.
"""
from __future__ import annotations

import glob
import json
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
        raise RuntimeError("git %s: %s" % (a[0], r.stderr[-200:]))
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
        return str(e)[:300]
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


# ---------------------------------------------------------------- walled boxes

def box_live(store):
    """Boxes a check still reads: every box named by a record that is checking."""
    out = set()
    for i in store.items():
        try:
            st = store.load(i)
        except (OSError, ValueError):
            continue
        chk = (st or {}).get("check") or {}
        if chk.get("box") and st.get("status") == "checking":
            out.add(os.path.abspath(chk["box"]))
    return out


def reap_boxes(store, r, now, in_use, acts=None):
    """-> [(box, "tree"|"box")] removed. A box's tree goes once no checking record names it, no process is in it, and it is
    older than the longest a check may run; the whole box goes after box_keep_s. Nothing younger is touched: make_box
    writes the box before the record names it."""
    prof = (r.get("walls") or {}).get("marker") or {}
    root = prof.get("box_root")
    if not root or not os.path.isdir(root):
        return []
    hold = r.get("check_max_s", 3600) + r.get("launch_grace_s", 600) + 600
    keep = (r.get("disk") or {}).get("box_keep_s", 7 * 86400)
    live = box_live(store)
    out = []
    for box in sorted(glob.glob(os.path.join(root, "*"))):
        b = os.path.abspath(box)
        try:
            age = now - os.lstat(os.path.join(b, "nonce") if os.path.exists(os.path.join(b, "nonce")) else b).st_mtime
        except OSError:
            continue
        if b in live or age < hold or in_use(b):
            continue
        if age >= keep:
            if remove_tree(b) is None:
                out.append((b, "box"))
        elif os.path.isdir(os.path.join(b, "tree")):
            if remove_tree(os.path.join(b, "tree")) is None:
                out.append((b, "tree"))
    if out:
        store.journal({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "do": "boxes_reaped",
                       "boxes": [os.path.basename(b) + ":" + w for b, w in out][:50]})
        if acts is not None:
            acts.append({"do": "boxes_reaped", "n": len(out)})
    return out


def estimate(r=None):
    """Bytes written per item, before and after, from the code paths (a dry reading: nothing is cloned). -> dict."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils"))
    import scratch_clone as sc
    clones = sorted(glob.glob(os.path.join(str(sc.pool_root()), "*", ".git")))
    wt = []
    for g in clones[:3]:
        c = os.path.dirname(g)
        own = sum(sc.own_bytes(sc.Path(c)))
        gown = sum(sc.own_bytes(sc.Path(g)))
        wt.append((own - gown, gown))
    tree = sum(a for a, _ in wt) // len(wt) if wt else None
    gitd = sum(b for _, b in wt) // len(wt) if wt else None
    return {"clones_read": len(wt), "worktree_bytes": tree, "git_dir_bytes": gitd,
            "before_per_item_one_check": None if tree is None else 2 * (tree + gitd) + tree,
            "after_per_item_one_check": None if tree is None else 2 * 20 * 10**6 + tree,
            "note": "before: a fresh worker and a fresh checker checkout plus a box tree, all deleted later. after: two "
                    "warm resets (the files changed upstream since the clone was parked, ~MBs, plus a ~4 MB index) and a "
                    "box tree that is now removed; the box export itself is still written once per check."}


if __name__ == "__main__":
    print(json.dumps(estimate(), indent=1))
