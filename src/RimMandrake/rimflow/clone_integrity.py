"""clone_integrity.py -- read a clone for damage (NUL-filled or emptied files) before it is bundled or reused.

Moved verbatim from rimflow/relentless_integrity.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES):
only the functions live code reaches (design/RimMandrake/retired_eras_index_2026-11-18.md).
"""
from __future__ import annotations

import os
import subprocess

EMPTY_BLOB = "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
TAIL = 512


# ---------------------------------------------------------------- content readings

def nul_or_empty(path):
    """-> "empty", "nul" (the whole tail NUL), or None. A file that cannot be read is "unreadable"."""
    try:
        size = os.lstat(path).st_size
        if size == 0:
            return "empty"
        with open(path, "rb") as f:
            f.seek(max(0, size - TAIL))
            tail = f.read(TAIL)
    except OSError:
        return "unreadable"
    return "nul" if tail and not tail.strip(b"\0") else None


def clone_damage(c, timeout=600):
    """-> [(path, why)] tracked files whose content is not the index's while git status would say nothing: a NUL tail
    or an empty file where the index holds a non-empty blob. Hash-confirmed, so a file legitimately ending in NUL that
    matches its blob is no damage. Raises when git cannot list the clone (the caller treats that as damage)."""
    r = subprocess.run(["git", "ls-files", "-s", "-z"], cwd=c, capture_output=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError("git ls-files: %s" % r.stderr.decode("utf-8", "replace"))
    suspect = []
    for rec in r.stdout.split(b"\0"):
        if not rec:
            continue
        head, path = rec.split(b"\t", 1)
        mode, sha, _stage = head.decode().split()
        if mode not in ("100644", "100755"):
            continue
        p = path.decode("utf-8", "surrogateescape")
        bad = nul_or_empty(os.path.join(c, p))
        if bad == "empty" and sha == EMPTY_BLOB:
            continue
        if bad:
            suspect.append((p, sha, bad))
    if not suspect:
        return []
    h = subprocess.run(["git", "hash-object", "--no-filters", "--stdin-paths"], cwd=c, capture_output=True, timeout=timeout,
                       input="\n".join(p for p, _, _ in suspect).encode("utf-8", "surrogateescape"))
    got = h.stdout.decode().split() if h.returncode == 0 else []
    if len(got) != len(suspect):      # an unreadable file fails the batch: every suspect stands
        return [(p, bad) for p, _, bad in suspect]
    return [(p, bad) for (p, sha, bad), now in zip(suspect, got) if now != sha]
