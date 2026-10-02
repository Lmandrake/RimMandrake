#!/usr/bin/env python3
"""Drain the D:\\ repo's worktrees, branches and dirty trees so every piece of work is
reachable from origin or saved on disk — without destroying anything.

Phase 6 part A of design/RimMandrake/git_workflow_plan_2026-10-01.md (§5 "Draining").
Run from ext4. Never writes the D:\\ repo's index, HEAD, branches or working files; the only
writes there are refs under refs/rescue/*, `git worktree remove` (no --force) of worktrees
that pass the safe-removal test, and `git worktree prune`.

  drain_worktrees.py census      classify every worktree / branch / stash  -> STATE/census.json
  drain_worktrees.py archive     push refs/tags/archive/<name> for every ref with unaccepted commits
  drain_worktrees.py snapshot    dirty linked worktrees -> refs/rescue/dirty/<name>-<utc> (+ tag)
  drain_worktrees.py shared      shared tree: tag local commits, tar + snapshot dirty/untracked
  drain_worktrees.py remove [--budget S]   remove worktrees passing the safe-removal test
  drain_worktrees.py verify      every unique commit reachable from an origin ref?

Object work happens in an ext4 bare repo (STATE/objects.git) fed by `git fetch` from D:\\;
rescue commits are built there with a temp index and pushed back into D:\\ as refs/rescue/*.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

D = "/mnt/d/Luke/dev/RimMandrake"
STATE = "/home/mandrake/rm/drain"
OBJ = STATE + "/objects.git"
ORIGIN = "git@github.com:Lmandrake/RimMandrake.git"
UP = "refs/remotes/origin/main"
LEFTOVERS = "/mnt/d/Luke/dev/_rm_shared_tree_leftovers_2026-10"
UNTRACKED_MAX = 5 * 1024 * 1024        # §2.2: untracked files above this are listed, not stored
TRACKED_MAX = 50 * 1024 * 1024         # never put a >50 MB blob in a pushed commit
SAFE_IGNORED = re.compile(r"(^|/)(obj|bin|__pycache__|\.vs|node_modules)(/|$)|\.pyc$|(^|/)\.DS_Store$"
                          r"|^vendor/mod_sources/|^mod_sources/"
                          # per-checkout runtime state, regenerated: lock files, the health hook log,
                          # the BRIDGE mirror (re-derived by `rimflow bridge who`), state/derived/
                          r"|\.lock$|^Transient/codebase_health_hook\.log$|^infrastructure/state/BRIDGE$"
                          r"|^infrastructure/state/derived/")
SECRET_NAME = re.compile(r"(\.pem|\.key|\.pfx|\.p12)$|(^|/)id_[^/]*$|(^|/)\.env|token", re.I)   # §2.2
SECRET_BODY = re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{20,}"
                         rb"|sk-ant-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[abpr]-[A-Za-z0-9-]{10,}"
                         rb"|AIza[0-9A-Za-z_-]{35}|nvapi-[A-Za-z0-9_-]{20,}")
SOURCE_EXT = {".cs", ".py", ".xml", ".js", ".ts", ".sh", ".csproj", ".props", ".targets", ".json", ".jsonl",
              ".yml", ".yaml", ".toml", ".ps1", ".bat", ".cfg", ".ini", ".sln", ".css"}
DOC_EXT = {".md", ".txt", ".html", ".htm", ".csv", ".rst"}
GENERATED = re.compile(r"^infrastructure/state/queue/(BENCH|FOUNDRY|HUMAN)\.md$|^Transient/codebase_health"
                       r"|^infrastructure/state/codebase_health_last\.json$|^infrastructure/dashboards/hub/data/"
                       r"|^infrastructure/artpipe/(pending|active|done|failed)/|\.log$")
ZERO = "0" * 40
NOW = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def log(*a):
    print(*a, flush=True)


def run(args, cwd=None, env=None, inp=None, timeout=None, check=True):
    r = subprocess.run(args, cwd=cwd, env=env, input=inp, capture_output=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError("%s -> %d: %s" % (" ".join(args[:6]), r.returncode,
                                             r.stderr.decode(errors="replace").strip()[:500]))
    return r


def g(repo, *args, **kw):
    return run(["git", "-C", repo, *args], **kw)


def go(repo, *args, **kw):
    return g(repo, *args, **kw).stdout.decode(errors="replace").strip()


def obj(*args, **kw):
    return go(OBJ, *args, **kw)


def load():
    with open(STATE + "/census.json") as f:
        return json.load(f)


def save(c):
    tmp = STATE + "/census.json.tmp"
    with open(tmp, "w") as f:
        json.dump(c, f, indent=1)
    os.replace(tmp, STATE + "/census.json")


def sanitize(name):
    s = re.sub(r"[^A-Za-z0-9._/-]", "_", name).strip("/.")
    s = re.sub(r"/+", "/", re.sub(r"\.\.+", ".", s))
    return s.replace(".lock", "_lock") or "unnamed"


def ensure_obj():
    os.makedirs(STATE, exist_ok=True)
    if not os.path.isdir(OBJ):
        run(["git", "init", "-q", "--bare", OBJ])
        obj("remote", "add", "origin", ORIGIN)
        if os.path.isdir("/home/mandrake/rm/bench/.git"):   # cheap seed of upstream objects
            obj("fetch", "-q", "/home/mandrake/rm/bench", "+refs/remotes/origin/*:refs/remotes/origin/*")
    obj("fetch", "-q", "origin", "+refs/heads/*:refs/remotes/origin/*", timeout=600)
    return obj("rev-parse", UP)


def worktrees():
    wts, cur = [], {}
    for line in go(D, "worktree", "list", "--porcelain").split("\n") + [""]:
        if not line:
            if cur:
                wts.append(cur)
            cur = {}
        else:
            k, _, v = line.partition(" ")
            cur[k] = v or True
    return wts


def proc_paths():
    """Every cwd and open-file path held by a visible process (Windows processes are invisible)."""
    seen = set()
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        for link in ["/proc/%s/cwd" % pid] + ["/proc/%s/fd/%s" % (pid, fd) for fd in _ls("/proc/%s/fd" % pid)]:
            try:
                seen.add(os.readlink(link))
            except OSError:
                pass
    return seen


def _ls(p):
    try:
        return os.listdir(p)
    except OSError:
        return []


def held_by_process(path, paths):
    p = path.rstrip("/") + "/"
    return any(x == path or x.startswith(p) for x in paths)


def status(path, timeout=300):
    """[(XY, path, orig)] incl. ignored ('!!'); read-only (GIT_OPTIONAL_LOCKS=0 skips the index refresh)."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    raw = g(path, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored=matching",
            "--no-renames", env=env, timeout=timeout).stdout
    recs, parts, i = [], raw.split(b"\0"), 0
    while i < len(parts):
        rec = parts[i]
        i += 1
        if not rec:
            continue
        xy, p = rec[:2].decode(), rec[3:].decode(errors="surrogateescape")
        recs.append((xy, p))
    return recs


# ---------- commit classification (all in the ext4 object repo) ----------

def entries(commit, paths):
    res = {}
    for i in range(0, len(paths), 400):
        raw = g(OBJ, "ls-tree", "-z", "-r", "--full-tree", commit, "--", *paths[i:i + 400]).stdout
        for rec in raw.split(b"\0"):
            if rec:
                meta, p = rec.split(b"\t", 1)
                mode, _, sha = meta.decode().split()
                res[p.decode(errors="surrogateescape")] = (mode, sha)
    return res


def touched(c):
    parents = obj("rev-list", "--parents", "-n1", c).split()[1:]
    if not parents:
        return None                                   # root commit: never content-upstream
    raw = g(OBJ, "diff-tree", "-r", "--no-renames", "--name-only", "--no-commit-id", "-z",
            parents[0], c).stdout
    return [p.decode(errors="surrogateescape") for p in raw.split(b"\0") if p]


def unaccepted(ref, up):
    """Commits on ref whose change origin/main has neither by patch-id nor by content of touched paths."""
    if g(OBJ, "merge-base", "--is-ancestor", ref, up, check=False).returncode == 0:
        return [], 0
    cherry = obj("cherry", up, ref).split("\n")
    plus = [l[2:] for l in cherry if l.startswith("+ ")]
    # merges are not listed by cherry; classify them by content too
    merges = obj("rev-list", "--merges", "%s..%s" % (up, ref)).split()
    total = len([l for l in cherry if l]) + len(merges)
    left = []
    for c in plus + merges:
        paths = touched(c)
        if paths is None:
            left.append(c)
            continue
        if not paths:
            continue                                  # empty commit: nothing to lose
        if entries(c, paths) != entries(up, paths):
            left.append(c)
    return left, total


def census(args):
    up = ensure_obj()
    log("origin/main", up[:12])
    wts = worktrees()
    procs = proc_paths()
    main = wts[0]["worktree"]

    def judge(w):
        p = w["worktree"]
        r = {"path": p, "head": w.get("HEAD"), "branch": (w.get("branch") or "").replace("refs/heads/", ""),
             "detached": bool(w.get("detached")), "locked": w.get("locked") or False, "main": p == main,
             "exists": os.path.isdir(p), "process": False, "dirty": None, "ignored_unsafe": None}
        if not r["exists"] or r["main"]:
            return r
        r["process"] = held_by_process(p, procs)
        t0 = time.time()
        try:
            recs = status(p, timeout=args.timeout)
        except Exception as e:                        # timeout or failure: unknown is never clean
            r["dirty"], r["error"] = None, str(e)[:200]
            return r
        r["status_s"] = round(time.time() - t0, 1)
        r["changes"] = [x for x in recs if x[0] != "!!"]
        r["dirty"] = len(r["changes"])
        ign = [x[1] for x in recs if x[0] == "!!"]
        r["ignored_n"] = len(ign)
        r["ignored_unsafe"] = [x for x in ign if not SAFE_IGNORED.search(x)][:200]
        return r

    with ThreadPoolExecutor(args.jobs) as ex:
        rows = list(ex.map(judge, wts))
    log("worktrees", len(rows), "statused")

    # refs the D:\ repo must expose before fetch: detached heads and stash entries (plumbing only)
    sh_heads = {}
    for r in rows:
        if r["detached"] and r["head"]:
            name = "wt-head/" + sanitize(os.path.basename(r["path"]))
            g(D, "update-ref", "refs/rescue/" + name, r["head"])
            r["rescue_head"] = "refs/rescue/" + name
    stashes = []
    n = len([l for l in go(D, "stash", "list").split("\n") if l])
    for i in range(n):
        sha = go(D, "rev-parse", "stash@{%d}" % i)
        name = "stash/%d-%s" % (i, sha[:10])
        g(D, "update-ref", "refs/rescue/" + name, sha)
        stashes.append({"ref": "refs/rescue/" + name, "sha": sha, "name": name})
    g(OBJ, "fetch", "-q", D, "+refs/heads/*:refs/drain/heads/*", "+refs/rescue/*:refs/drain/rescue/*",
      "+refs/tags/*:refs/drain/tags/*", timeout=900)
    log("fetched D:\\ refs into", OBJ)

    branches = {}
    for line in obj("for-each-ref", "--format=%(refname:lstrip=3) %(objectname)", "refs/drain/heads").split("\n"):
        if line:
            b, sha = line.rsplit(" ", 1)
            branches[b] = {"name": b, "sha": sha}

    def classify(b):
        left, total = unaccepted(b["sha"], up)
        b["unaccepted"], b["ahead"] = left, total
        return b

    targets = list(branches.values())
    for r in rows:
        if r.get("rescue_head"):
            targets.append({"name": "detached/" + sanitize(os.path.basename(r["path"])), "sha": r["head"],
                            "detached_of": r["path"]})
    with ThreadPoolExecutor(8) as ex:
        targets = list(ex.map(classify, targets))
    for s in stashes:                                  # stash commits are always archived
        s["unaccepted"], s["ahead"] = [s["sha"]], 1
    c = {"when": NOW, "up": up, "worktrees": rows, "refs": targets, "stashes": stashes}
    by_ref = {t["name"]: t for t in targets}
    for r in rows:
        key = r["branch"] if r["branch"] else ("detached/" + sanitize(os.path.basename(r["path"])))
        t = by_ref.get(key)
        r["unaccepted"] = len(t["unaccepted"]) if t else None
        r["verdict"] = verdict(r)
    save(c)
    summary(c)


def verdict(r):
    if r["main"]:
        return "keep: shared tree"
    if not r["exists"]:
        return "prune: dir gone"
    if r["locked"]:
        return "keep: locked"
    if r["process"]:
        return "keep: live process inside"
    if r["dirty"] is None:
        return "keep: status failed"
    if r["unaccepted"] is None:
        return "keep: head unclassified"
    if r["unaccepted"]:
        return "keep: archived commits"
    if r["dirty"]:
        return "keep: dirty (snapshotted)"
    if r["ignored_unsafe"]:
        return "keep: non-cache ignored files"
    return "remove"


def summary(c):
    t = {}
    for r in c["worktrees"]:
        k = r["verdict"]
        t[k] = t.get(k, 0) + 1
    uniq = set()
    for x in c["refs"] + c["stashes"]:
        uniq.update(x["unaccepted"])
    log("verdicts:", json.dumps(t, sort_keys=True))
    log("refs: %d, with unaccepted: %d, unique unaccepted commits: %d, stashes: %d"
        % (len(c["refs"]), sum(1 for x in c["refs"] if x["unaccepted"]), len(uniq), len(c["stashes"])))


# ---------- archive ----------

def remote_tags():
    out = run(["git", "ls-remote", "--tags", ORIGIN, "refs/tags/archive/*"], timeout=300).stdout.decode()
    return {l.split("\t")[1]: l.split("\t")[0] for l in out.split("\n") if "\t" in l}


def push_tags(pairs):
    """pairs: [(sha, tagname)]; skips tags already on origin at that sha; refuses to move one."""
    have = remote_tags()
    todo, clash = [], []
    for sha, tag in pairs:
        ref = "refs/tags/" + tag
        if ref in have:
            if have[ref] != sha:
                clash.append((tag, have[ref], sha))
            continue
        todo.append("%s:%s" % (sha, ref))
    for i in range(0, len(todo), 40):
        g(OBJ, "push", "-q", "origin", *todo[i:i + 40], timeout=900)
        log("pushed %d/%d tags" % (min(i + 40, len(todo)), len(todo)))
    return len(todo), clash


def archive(args):
    c = load()
    pairs = []
    for t in c["refs"]:
        if t["unaccepted"] and t["name"] != "main":
            t["tag"] = "archive/" + sanitize(t["name"])
            pairs.append((t["sha"], t["tag"]))
    for s in c["stashes"]:
        s["tag"] = "archive/" + s["name"]
        pairs.append((s["sha"], s["tag"]))
    n, clash = push_tags(pairs)
    c["archive_pushed"], c["archive_clash"] = n, clash
    save(c)
    log("archive tags: %d wanted, %d newly pushed, %d clashes %s" % (len(pairs), n, len(clash), clash[:5]))


# ---------- snapshots ----------

def classify_path(p, data):
    if SECRET_NAME.search(p) or (data is not None and SECRET_BODY.search(data)):
        return "suspect-secret"
    if GENERATED.search(p):
        return "generated"
    ext = os.path.splitext(p)[1].lower()
    if ext in SOURCE_EXT:
        return "source"
    if ext in DOC_EXT:
        return "doc"
    if data is not None and b"\0" in data[:8000]:
        return "binary"
    return "binary" if ext in {".png", ".dll", ".pdb", ".psd", ".jpg", ".dds", ".zip", ".rws", ".exe"} else "doc"


def snapshot_tree(root, head, name, refname, recs=None, timeout=600):
    """Commit tracked changes + untracked non-ignored files (<=5 MB) of `root` on top of `head`,
    in the ext4 object repo with a temp index; push the commit into D:\\ as `refname`."""
    if recs is None:
        recs = status(root, timeout=timeout)
    changes = [x for x in recs if x[0] != "!!"]
    ignored = [x[1] for x in recs if x[0] == "!!"]
    idx = "%s/idx-%s" % (STATE, re.sub(r"[^A-Za-z0-9]", "_", name))
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    if os.path.exists(idx):
        os.remove(idx)
    g(OBJ, "read-tree", head, env=env)
    base = entries(head, [p for _, p in changes]) if changes else {}
    recs_in, skipped, classes, stored, files = [], [], {}, [], []
    for xy, p in changes:
        full = os.path.join(root, p)
        untracked = xy == "??"
        if os.path.islink(full):
            data = os.readlink(full).encode()
            sha = g(OBJ, "hash-object", "-w", "--stdin", inp=data).stdout.decode().strip()
            recs_in.append(("120000", sha, p))
        elif os.path.isfile(full):
            size = os.path.getsize(full)
            if size > (UNTRACKED_MAX if untracked else TRACKED_MAX):
                skipped.append((p, size))
                continue
            with open(full, "rb") as f:
                data = f.read()
            sha = g(OBJ, "hash-object", "-w", "--stdin", inp=data).stdout.decode().strip()
            mode = base.get(p, ("100644",))[0]
            recs_in.append((mode if mode in ("100644", "100755") else "100644", sha, p))
            cls = classify_path(p, data)
            classes[cls] = classes.get(cls, 0) + 1
            stored.append((p, cls))
            files.append(p)
        elif not os.path.lexists(full):
            if p in base:
                recs_in.append(("0", ZERO, p))
                classes["deleted"] = classes.get("deleted", 0) + 1
        else:
            skipped.append((p, -1))                    # directory (submodule/nested repo) etc.
    inp = b"".join(("%s %s\t" % (m, s)).encode() + p.encode(errors="surrogateescape") + b"\0"
                   for m, s, p in recs_in)
    if inp:
        g(OBJ, "update-index", "-z", "--index-info", env=env, inp=inp)
    tree = obj("write-tree", env=env)
    os.remove(idx)
    msg = ["rescue snapshot: %s" % name, "",
           "Uncommitted state of %s on top of %s, taken %s by drain_worktrees.py." % (root, head[:12], NOW),
           "ARCHIVED, NOT ACCEPTED.", "", "classes: " + json.dumps(classes, sort_keys=True)]
    if skipped:
        msg += ["", "not stored (size limit or not a file):"] + ["  %s (%d bytes)" % s for s in skipped]
    if ignored:
        msg += ["", "ignored paths, not stored (%d):" % len(ignored)] + ["  " + x for x in ignored[:400]]
        if len(ignored) > 400:
            msg.append("  ... %d more" % (len(ignored) - 400))
    cenv = dict(os.environ, GIT_AUTHOR_NAME="Lukas Mandrake", GIT_COMMITTER_NAME="Lukas Mandrake",
                GIT_AUTHOR_EMAIL="313496996+Lmandrake@users.noreply.github.com",
                GIT_COMMITTER_EMAIL="313496996+Lmandrake@users.noreply.github.com")
    commit = obj("commit-tree", tree, "-p", head, env=cenv, inp="\n".join(msg).encode())
    g(OBJ, "update-ref", refname, commit)
    g(OBJ, "push", "-q", D, "%s:%s" % (commit, refname), timeout=600)   # local rescue ref in D:\
    return {"commit": commit, "ref": refname, "classes": classes, "stored": len(stored),
            "skipped": skipped, "secret": [p for p, k in stored if k == "suspect-secret"], "files": files,
            "ignored_n": len(ignored)}


def snapshot(args):
    c = load()
    rows = [r for r in c["worktrees"] if not r["main"] and r["exists"] and r.get("dirty") and not r.get("snapshot")]
    log("dirty linked worktrees to snapshot:", len(rows))

    def one(r):
        name = sanitize(os.path.basename(r["path"]))
        try:
            s = snapshot_tree(r["path"], r["head"], name, "refs/rescue/dirty/%s-%s" % (name, NOW),
                              timeout=args.timeout)
            s.pop("files")
            return r, s
        except Exception as e:
            return r, {"error": str(e)[:300]}

    with ThreadPoolExecutor(args.jobs) as ex:
        res = list(ex.map(one, rows))
    pairs = []
    for r, s in res:
        r["snapshot"] = s
        if s.get("commit") and not s["secret"]:
            s["tag"] = "archive/dirty/" + sanitize(os.path.basename(r["path"]))
            pairs.append((s["commit"], s["tag"]))
        log("  %-50s %s" % (os.path.basename(r["path"]), s.get("error") or "%d stored, secret=%d"
                            % (s["stored"], len(s["secret"]))))
    n, clash = push_tags(pairs)
    save(c)
    log("dirty snapshots: %d, tags pushed %d, local-only (secret) %d, errors %d, clashes %s"
        % (len(res), n, sum(1 for _, s in res if s.get("secret")), sum(1 for _, s in res if "error" in s), clash))


# ---------- shared tree ----------

def shared(args):
    c = load()
    up = c["up"]
    left, _ = unaccepted("refs/drain/heads/main", up)
    pairs = [(x, "archive/shared-tree/" + x[:12]) for x in left]
    n, clash = push_tags(pairs)
    sh = {"local_unaccepted": left, "tags": [p[1] for p in pairs], "tags_pushed": n, "clash": clash}
    log("shared-tree local commits not upstream: %d (%s); tags pushed %d" % (len(left), [x[:9] for x in left], n))

    head = go(D, "rev-parse", "HEAD")
    t0 = time.time()
    recs = status(D, timeout=args.timeout)
    log("shared tree status %.0fs: %d changes" % (time.time() - t0, sum(1 for x in recs if x[0] != "!!")))
    os.makedirs(LEFTOVERS, exist_ok=True)
    tar_path = LEFTOVERS + "/leftovers.tar"
    if os.path.exists(tar_path):
        tar_path = LEFTOVERS + "/leftovers-%s.tar" % NOW          # never overwrite a prior copy
    man, total = [], 0
    with tarfile.open(tar_path, "w") as tf:
        for xy, p in recs:
            if xy == "!!":
                continue
            full = os.path.join(D, p)
            if os.path.isfile(full) or os.path.islink(full):
                h = hashlib.sha256()
                if os.path.isfile(full) and not os.path.islink(full):
                    with open(full, "rb") as f:
                        for chunk in iter(lambda: f.read(1 << 20), b""):
                            h.update(chunk)
                    size = os.path.getsize(full)
                else:
                    h.update(os.readlink(full).encode())
                    size = 0
                tf.add(full, arcname=p, recursive=False)
                man.append("%s\t%d\t%s\t%s" % (h.hexdigest(), size, xy, p))
                total += size
            elif not os.path.lexists(full):
                man.append("%s\t%d\t%s\t%s" % ("-" * 64, 0, xy, p))     # deleted in the tree
    with open(tar_path[:-4] + ".manifest.tsv", "w") as f:
        f.write("# sha256\tbytes\tstatus\tpath   (shared tree %s at HEAD %s, %s)\n" % (D, head, NOW))
        f.write("\n".join(man) + "\n")
    sh.update({"tar": tar_path, "tar_bytes": os.path.getsize(tar_path), "tar_files": len(man), "head": head})
    log("tar %s: %d entries, %.1f MB" % (tar_path, len(man), os.path.getsize(tar_path) / 1e6))

    name = "shared-tree-" + NOW
    g(OBJ, "fetch", "-q", D, "+HEAD:refs/drain/shared-head", timeout=600)
    s = snapshot_tree(D, head, name, "refs/rescue/" + name, recs=recs)
    s.pop("files")
    if not s["secret"]:
        s["tag"] = "archive/shared-tree-dirty-" + NOW
        sh["snapshot_tags_pushed"] = push_tags([(s["commit"], s["tag"])])[0]
    sh["snapshot"] = s
    c["shared"] = sh
    save(c)
    log("shared snapshot %s stored %d classes %s secret %d tag %s"
        % (s["commit"][:12], s["stored"], s["classes"], len(s["secret"]), s.get("tag")))


# ---------- removal ----------

def remove(args):
    c = load()
    cand = [r for r in c["worktrees"] if r["verdict"] == "remove" and not r.get("removed")]
    log("removal candidates:", len(cand))
    start = time.time()

    def one(r):
        if time.time() - start > args.budget:
            return r, "deferred: time budget"
        p = r["path"]
        live = {w["worktree"]: w for w in worktrees()}
        w = live.get(p)
        if not w:
            return r, "already gone"
        if w.get("locked"):
            return r, "keep: locked now"
        if w.get("HEAD") != r["head"]:
            return r, "keep: HEAD moved since census"
        if held_by_process(p, proc_paths()):
            return r, "keep: live process now"
        try:
            recs = status(p, timeout=args.timeout)
        except Exception as e:
            return r, "keep: status failed " + str(e)[:80]
        if any(x[0] != "!!" for x in recs):
            return r, "keep: dirty now"
        if any(not SAFE_IGNORED.search(x[1]) for x in recs if x[0] == "!!"):
            return r, "keep: non-cache ignored files now"
        res = g(D, "worktree", "remove", p, check=False, timeout=1800)
        if res.returncode:
            return r, "keep: remove refused: " + res.stderr.decode(errors="replace").strip()[:150]
        return r, "removed"

    with ThreadPoolExecutor(args.jobs) as ex:
        res = list(ex.map(one, cand))
    t = {}
    for r, v in res:
        if v in ("removed", "already gone"):
            r["removed"] = True
        r["remove_result"] = v
        k = v.split(":")[0]
        t[k] = t.get(k, 0) + 1
        if v != "removed":
            log("  %-50s %s" % (os.path.basename(r["path"]), v))
    g(D, "worktree", "prune")
    save(c)
    log("removal:", json.dumps(t, sort_keys=True), "(pruned)")


# ---------- verify ----------

def verify(args):
    c = load()
    obj("fetch", "-q", "origin", "+refs/heads/*:refs/remotes/origin/*", "+refs/tags/archive/*:refs/tags/archive/*",
        timeout=900)
    want = {}
    for x in c["refs"] + c["stashes"]:
        for sha in x["unaccepted"]:
            want[sha] = x["name"]
    for x in (c.get("shared") or {}).get("local_unaccepted", []):
        want[x] = "shared-tree"
    local_only = []
    for r in c["worktrees"]:
        s = r.get("snapshot") or {}
        if s.get("commit"):
            (local_only.append((s["ref"], s["secret"])) if s["secret"] else want.__setitem__(s["commit"], "dirty"))
    s = (c.get("shared") or {}).get("snapshot") or {}
    if s.get("commit"):
        (local_only.append((s["ref"], s["secret"])) if s["secret"] else want.__setitem__(s["commit"], "shared-dirty"))
    missing = []
    for sha, src in sorted(want.items()):
        hit = obj("for-each-ref", "--count=1", "--contains", sha, "--format=%(refname)",
                  "refs/remotes/origin", "refs/tags/archive")
        if not hit:
            missing.append((sha, src))
    c["verify"] = {"checked": len(want), "missing": missing, "local_only": local_only, "when": NOW}
    save(c)
    log("verify: %d commits checked, %d reachable from origin, %d NOT reachable, %d local-only rescue refs"
        % (len(want), len(want) - len(missing), len(missing), len(local_only)))
    for m in missing[:20]:
        log("  MISSING", m)


def reverdict(args):
    """Re-apply verdict() after a SAFE_IGNORED change, without re-running status."""
    c = load()
    for r in c["worktrees"]:
        if r.get("ignored_unsafe"):
            r["ignored_unsafe"] = [x for x in r["ignored_unsafe"] if not SAFE_IGNORED.search(x)]
        r["verdict"] = verdict(r)
    save(c)
    summary(c)


def table(args):
    """Markdown census table for the report."""
    c = load()
    print("| worktree | branch / HEAD | dirty | unaccepted | locked | proc | verdict |")
    print("|---|---|---|---|---|---|---|")
    for r in c["worktrees"]:
        p = r["path"].replace("/mnt/d/Luke/dev/RimMandrake/.claude/worktrees/", ".claude/worktrees/")
        print("| `%s` | %s | %s | %s | %s | %s | %s%s |" % (
            p, r["branch"] or ("detached " + (r["head"] or "")[:9]), r["dirty"], r["unaccepted"],
            "y" if r["locked"] else "", "y" if r["process"] else "", r["verdict"],
            (" -> " + r["remove_result"]) if r.get("remove_result") else ""))
    print()
    print("| ref | ahead of origin/main | unaccepted | archive tag |")
    print("|---|---|---|---|")
    for t in sorted(c["refs"] + c["stashes"], key=lambda t: t["name"]):
        if t["unaccepted"] or t.get("ahead"):
            print("| `%s` | %s | %d | %s |" % (t["name"], t.get("ahead"), len(t["unaccepted"]),
                                              "`%s`" % t["tag"] if t.get("tag") else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=["census", "archive", "snapshot", "shared", "remove", "verify", "table", "reverdict"])
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=300, help="per-worktree git status timeout (s)")
    ap.add_argument("--budget", type=int, default=420, help="remove: stop starting removals after S seconds")
    a = ap.parse_args()
    globals()[a.verb](a)


if __name__ == "__main__":
    main()
