#!/usr/bin/env python3
"""deploy_memo.py - skip the deploy plan and the attest hashing when nothing changed since the lane's previous job.

RIMMANDRAKE_TESTQ_DEPLOY_MEMO_SKIP_UNCHANGED. A job's fixed cost is deploy (the plan alone ~42 s with no drift) + attest (sha256 of
every file of every deployed mod) before the load. Of the 73 jobs since 2026-11-06 that deployed mods, 28 followed a job
on the same lane that had deployed the same mods from the same source: 3477 of 9363 s (37%) of deploy+attest was repeat.

The memo is ONE file (TESTQ_HOME/deploy_memo.json), the last job's entry:
  key  - mods deployed (after composed-folding), the git tree id of each mod's source directory at the job's source_sha
         (the whole fold for a composed target), the blob id of deploy_custom_mods.py;
  sig  - a signature of the GAME's copy: every file's (relative path, size, mtime_ns) under each deployed mod folder;
  mods - the attest record (dll_sha256, defs_sha256, files) the previous attest computed from those very files.
A hit needs the key AND the signature equal. Anything else - a different mod, a commit that touched a mod's source, a
file in the game folder written, added or removed by anyone (the game, a hand edit, another deploy) - is a miss, and the
job deploys and attests exactly as before. The companion DLL check is not memoised (it is cheap and has its own verdict).
Off unless TESTQ_DEPLOY_MEMO=1; TESTQ_DEPLOY_MEMO=0 or unset behaves as the code did before this module.
"""
import hashlib
import json
import os
import subprocess

DEPLOY_TOOL = "src/RimMandrake/Utils/deploy_custom_mods.py"


def enabled(env=None):
    return (os.environ if env is None else env).get("TESTQ_DEPLOY_MEMO") == "1"


def _git(clone, *a):
    r = subprocess.run(["git", "-C", clone] + list(a), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def _source_dirs(name, S, src_root):
    """-> repo-relative paths whose content decides what deploying `name` writes, or None when unknown."""
    known, folded, composed = S.deploy_catalog(src_root)
    if name in composed or name in folded:
        out = ["src/RimMandrake/Biomes.compose.json"]
        for t in S._SRC_TIERS:
            for src in sorted(folded):
                if os.path.isdir(os.path.join(src_root, t, src)):
                    out.append("src/%s/%s" % (t, src))
        return out
    for t in S._SRC_TIERS:
        if os.path.isdir(os.path.join(src_root, t, name)):
            return ["src/%s/%s" % (t, name)]
    return None


def key_for(S, clone, sha, mods, src_root):
    """-> a JSON-able key, or None when any piece cannot be read (a memo must never guess)."""
    _, folded, _c = S.deploy_catalog(src_root)
    names = sorted({folded.get(m, m) for m in mods})
    trees = {}
    for m in names:
        dirs = _source_dirs(m, S, src_root)
        if not dirs:
            return None
        for d in dirs:
            t = _git(clone, "rev-parse", "%s:%s" % (sha, d))
            if not t:
                return None
            trees[d] = t
    tool = _git(clone, "rev-parse", "%s:%s" % (sha, DEPLOY_TOOL))
    if not tool:
        return None
    return {"mods": names, "trees": trees, "deploy_tool": tool}


def game_sig(mods_dir, names):
    """-> sha256 over (rel path, size, mtime_ns) of every file under each mod folder; None when a folder is absent."""
    h = hashlib.sha256()
    for m in sorted(names):
        root = os.path.join(mods_dir, m)
        if not os.path.isdir(root):
            return None
        h.update(b"\0mod\0" + m.encode())
        for dp, dn, fn in os.walk(root):
            dn.sort()
            for f in sorted(fn):
                full = os.path.join(dp, f)
                try:
                    st = os.stat(full)
                except OSError:
                    return None
                h.update(("%s\0%d\0%d\n" % (os.path.relpath(full, root).replace(os.sep, "/"), st.st_size,
                                            st.st_mtime_ns)).encode())
    return h.hexdigest()


def load(path):
    try:
        with open(path) as fh:
            m = json.load(fh)
        return m if isinstance(m, dict) else None
    except (OSError, ValueError):
        return None


def save(path, key, sig, dep_mods, job_id=None):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump({"key": key, "sig": sig, "mods": dep_mods, "job": job_id}, fh)
    os.replace(tmp, path)


def lookup(path, key, sig):
    """-> (attest mods record, previous job id) on a hit, else None."""
    m = load(path)
    if key is None or sig is None or not m or m.get("key") != key or m.get("sig") != sig or not m.get("mods"):
        return None
    return m["mods"], m.get("job")


def forget(path):
    try:
        os.remove(path)
    except OSError:
        pass
