#!/usr/bin/env python3
"""Put work on origin/main without a checkout, and move a never-clean tree forward.

    ./publish -m "subject" path/one path/two     publish these files as one commit
    ./publish --commit <sha>...                  publish existing local commits
    ./publish --sync                             every local-only commit, then --catchup
    ./publish --catchup [--dry-run]              move THIS tree to origin/main, keep all edits
    ./publish --worktrees [--apply]              list / remove clean, fully-published worktrees

Design and the alternatives it rules out: design/RimMandrake/git_workflow_fix_2026-10-01.md.

PUBLISH builds the commit in a private temporary index (read-tree origin/main, update only
the named paths, write-tree, commit-tree) — no worktree, no branch, the shared index is never
touched. Per path it is a 3-way: base = the path at merge-base(HEAD, origin/main), ours =
the file here, theirs = origin/main. Upstream unmoved -> ours; both moved -> `git merge-file`;
a real conflict refuses and pushes nothing. Ledger shards (append-only JSONL) are unioned by
line. A rejected push is rebuilt on the new tip and retried; never forced. Prints
`PUBLISHED <sha>` — the sha to hand `rimflow close --sha`, never local HEAD.

CATCHUP moves a tree per path: for each path upstream changed, an untouched file gets
upstream's bytes, an edited one is 3-way merged in place if clean, and anything else refuses
with nothing moved. Order is files -> index entries -> update-ref compare-and-swap against
the old HEAD, so a peer committing mid-run makes it stop instead of losing that commit.
Untracked files are never touched, except one colliding with an upstream add, which is a
reported conflict unless byte-identical.
"""
import argparse
import fnmatch
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

REMOTE, BRANCH = "origin", "main"
UP = "refs/remotes/%s/%s" % (REMOTE, BRANCH)
UNION_GLOBS = ("infrastructure/state/ledger/events/*.jsonl",)
# Regenerated on nearly every commit; nobody hand-edits them. Catch-up takes upstream's copy.
DERIVED = {
    "Transient/codebase_health.html",
    "Transient/codebase_health.json",
    "Transient/codebase_health_artifact.html",
    "infrastructure/dashboards/hub/data/health.json",
    "infrastructure/state/codebase_health_last.json",
}
SCRATCH = os.environ.get("PUBLISH_SCRATCH") or os.path.expanduser("~/.cache/publish")
WT_ROOT = "/home/mandrake/wt"
ZERO = "0" * 40
before_push = None          # selftest hook: called(attempt) between build and push


class Refuse(Exception):
    pass


def git(top, *args, env=None, inp=None, check=True):
    for _ in range(20):                       # peers hold index.lock / ref locks briefly
        r = subprocess.run(["git", *args], cwd=top, env=env, input=inp, capture_output=True)
        err = r.stderr.decode(errors="replace")
        if r.returncode and ("index.lock" in err or "cannot lock ref" in err):
            time.sleep(1)
            continue
        break
    if check and r.returncode:
        raise Refuse("git %s failed: %s" % (" ".join(args[:3]),
                                            (err or r.stdout.decode(errors="replace")).strip()))
    return r


def out(top, *args, **kw):
    return git(top, *args, **kw).stdout.decode(errors="replace").strip()


def ixline(path, e):
    """One `update-index -z --index-info` record; e=None removes the path."""
    mode, sha = e if e else ("0", ZERO)
    return ("%s %s\t%s" % (mode, sha, path)).encode() + b"\0"


def blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def toplevel(cwd="."):
    return out(os.path.abspath(cwd), "rev-parse", "--show-toplevel")


def is_main_worktree(top):
    g, c = out(top, "rev-parse", "--absolute-git-dir", "--git-common-dir").split("\n")
    return os.path.realpath(g) == os.path.realpath(os.path.join(top, c))


def fetch(top):
    git(top, "fetch", "-q", REMOTE, "+refs/heads/%s:%s" % (BRANCH, UP))
    return out(top, "rev-parse", UP)


def is_ancestor(top, a, b):
    return git(top, "merge-base", "--is-ancestor", a, b, check=False).returncode == 0


def entries(top, commit, paths):
    """{path: (mode, sha)} for the given paths at commit; absent paths are missing."""
    res = {}
    paths = list(paths)
    for i in range(0, len(paths), 400):
        raw = git(top, "ls-tree", "-z", "--full-tree", commit, "--", *paths[i:i + 400]).stdout
        for rec in raw.split(b"\0"):
            if rec:
                meta, p = rec.split(b"\t", 1)
                mode, typ, sha = meta.decode().split()
                if typ != "blob":
                    raise Refuse("%s is a %s in %s — name files, not directories"
                                 % (p.decode(), typ, commit[:9]))
                res[p.decode()] = (mode, sha)
    return res


def cat(top, sha):
    return git(top, "cat-file", "blob", sha).stdout


def cat_many(top, shas, each):
    """Stream blobs through each(sha, bytes) with one cat-file process."""
    shas = list(dict.fromkeys(shas))
    if not shas:
        return
    p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=top,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    def feed():
        p.stdin.write("".join(s + "\n" for s in shas).encode())
        p.stdin.close()
    threading.Thread(target=feed, daemon=True).start()
    for s in shas:
        hdr = p.stdout.readline().split()
        size = int(hdr[2])
        data = p.stdout.read(size)
        p.stdout.read(1)
        each(s, data)
    p.wait()


def read_disk(top, path):
    """(sha, bytes) of the file as it is on disk now, or None when absent."""
    full = os.path.join(top, path)
    if os.path.islink(full):
        data = os.readlink(full).encode()
    elif os.path.isfile(full):
        with open(full, "rb") as f:
            data = f.read()
    elif os.path.exists(full):
        raise Refuse("%s is a directory — name files, not directories" % path)
    else:
        return None
    return blob_sha(data), data


def union_lines(theirs, ours):
    """Append-only JSONL: upstream's lines in order, then ours that upstream lacks."""
    t = theirs.splitlines(keepends=True)
    if t and not t[-1].endswith(b"\n"):
        t[-1] += b"\n"
    have = {l.rstrip(b"\r\n") for l in t}
    add = [l if l.endswith(b"\n") else l + b"\n" for l in ours.splitlines(keepends=True)
           if l.strip() and l.rstrip(b"\r\n") not in have]
    return b"".join(t + add)


def merge3(top, base, ours, theirs):
    """Clean 3-way merge of three byte strings, or None on conflict / binary."""
    if any(b"\0" in x for x in (base, ours, theirs)):
        return None
    os.makedirs(SCRATCH, exist_ok=True)
    d = tempfile.mkdtemp(dir=SCRATCH)
    try:
        names = []
        for n, data in (("ours", ours), ("base", base), ("theirs", theirs)):
            names.append(os.path.join(d, n))
            with open(names[-1], "wb") as f:
                f.write(data)
        r = subprocess.run(["git", "merge-file", "-p", *names], capture_output=True)
        return r.stdout if r.returncode == 0 else None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def resolve(top, base, ours, theirs, known):
    """Decide each path. base/theirs: {path: (mode, sha)}; ours: {path: (mode, sha) or None}.
    known: sha -> bytes for content not yet in the object store. Returns {path: entry|None}
    of index changes against theirs; raises Refuse on a real conflict."""
    def data(e):
        return known[e[1]] if e[1] in known else cat(top, e[1])
    changes, conflicts = {}, []
    for p, o in ours.items():
        b, t = base.get(p), theirs.get(p)
        mode = (t or b or ("100644",))[0]
        if o is not None and o[0] is None:
            o = (mode, o[1])
        same = lambda x, y: (x and x[1]) == (y and y[1])
        if same(o, t):
            continue
        if o is not None and t is not None and any(fnmatch.fnmatch(p, g) for g in UNION_GLOBS):
            u = union_lines(data(t), data(o))
            s = blob_sha(u)
            known[s] = u
            if s != t[1]:
                changes[p] = (t[0], s)
            continue
        if same(b, t):                       # upstream did not move this path: ours wins
            changes[p] = o
            continue
        if same(b, o):                       # only upstream moved: nothing of ours to add
            continue
        if o is None or t is None:
            conflicts.append("%s: %s here, %s upstream" % (
                p, "deleted" if o is None else "edited", "deleted" if t is None else "edited"))
            continue
        m = merge3(top, data(b) if b else b"", data(o), data(t))
        if m is None:
            conflicts.append("%s: edited here and upstream in overlapping lines" % p)
            continue
        s = blob_sha(m)
        known[s] = m
        changes[p] = (t[0], s)
    if conflicts:
        raise Refuse("conflict, nothing pushed:\n  " + "\n  ".join(conflicts))
    return changes


def build(top, upstream, changes, known, message, author_env=None):
    os.makedirs(SCRATCH, exist_ok=True)
    tmp = tempfile.mkdtemp(dir=SCRATCH)
    try:
        need = []                              # write new blobs, one hash-object call
        for p, e in changes.items():
            if e and e[1] in known:
                fn = os.path.join(tmp, "b%d" % len(need))
                with open(fn, "wb") as f:
                    f.write(known[e[1]])
                need.append(fn)
        if need:
            git(top, "hash-object", "-w", "--no-filters", "--stdin-paths",
                inp="".join(n + "\n" for n in need).encode())
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(tmp, "index"), **(author_env or {}))
        git(top, "read-tree", upstream, env=env)
        info = b"".join(ixline(p, e) for p, e in changes.items())
        git(top, "update-index", "-z", "--index-info", env=env, inp=info)
        tree = out(top, "write-tree", env=env)
        if tree == out(top, "rev-parse", upstream + "^{tree}"):
            return None
        return out(top, "commit-tree", tree, "-p", upstream, "-F", "-", env=env,
                   inp=message.encode())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def push_loop(top, make, label):
    """make(upstream) -> commit sha or None. Rebuild on the new tip until the push lands."""
    for attempt in range(8):
        up = fetch(top)
        sha = make(up)
        if sha is None:
            print("nothing to publish for %s: origin already has it" % label)
            return None
        if before_push:
            before_push(attempt)
        r = git(top, "push", "-q", REMOTE, "%s:refs/heads/%s" % (sha, BRANCH), check=False)
        if r.returncode == 0:
            fetch(top)
            if not is_ancestor(top, sha, UP):
                raise Refuse("pushed %s but it is not on %s — investigate" % (sha, UP))
            print("PUBLISHED %s  (%s)" % (sha, label))
            return sha
        err = r.stderr.decode(errors="replace")
        if not any(k in err for k in ("rejected", "fetch first", "non-fast-forward",
                                      "cannot lock ref", "stale info")):
            raise Refuse("push failed: " + err.strip())
        print("origin moved during push; rebuilding on the new tip")
    raise Refuse("origin kept moving for 8 attempts; nothing lost — re-run")


def publish_paths(top, paths, message):
    def make(up):
        mb = out(top, "merge-base", "HEAD", up)
        known, ours = {}, {}
        for p in paths:
            d = read_disk(top, p)
            if d:
                known[d[0]] = d[1]
            ours[p] = (None, d[0]) if d else None
        base, theirs = entries(top, mb, paths), entries(top, up, paths)
        missing = [p for p in paths if ours[p] is None and p not in base and p not in theirs]
        if missing:
            raise Refuse("no such file here or on origin: " + ", ".join(missing))
        changes = resolve(top, base, ours, theirs, known)
        return build(top, up, changes, known, message) if changes else None
    return push_loop(top, make, "%d path(s)" % len(paths))


def commit_paths(top, c):
    return [p for p in out(top, "diff-tree", "-r", "--no-renames", "--name-only",
                           "--no-commit-id", "-z", c + "^", c).split("\0") if p]


def publish_commit(top, c):
    c = out(top, "rev-parse", c + "^{commit}")
    if len(out(top, "rev-list", "--parents", "-n1", c).split()) != 2:
        raise Refuse("%s is a merge or root commit — publish its files by path" % c[:9])
    msg = git(top, "log", "-1", "--format=%B", c).stdout.decode()
    a = out(top, "log", "-1", "--format=%an%x00%ae%x00%aD", c).split("\0")
    aenv = {"GIT_AUTHOR_NAME": a[0], "GIT_AUTHOR_EMAIL": a[1], "GIT_AUTHOR_DATE": a[2]}
    paths = commit_paths(top, c)
    def make(up):
        if out(top, "cherry", up, c, c + "^").startswith("-"):
            return None                       # the same patch is already upstream
        base, mine = entries(top, c + "^", paths), entries(top, c, paths)
        ours = {p: mine.get(p) for p in paths}
        changes = resolve(top, base, ours, entries(top, up, paths), {})
        return build(top, up, changes, {}, msg, aenv) if changes else None
    return push_loop(top, make, "commit %s" % c[:9])


def local_only(top, up, head="HEAD"):
    """Local commits whose change origin does not have — by patch-id, then by content."""
    if out(top, "rev-list", "--merges", "%s..%s" % (up, head)):
        raise Refuse("local merge commits present — publish their files by path")
    todo = out(top, "rev-list", "--reverse", "--cherry-pick", "--right-only", "--no-merges",
               "%s...%s" % (up, head)).split()
    left = []
    for c in todo:
        paths = commit_paths(top, c)
        base, mine = entries(top, c + "^", paths), entries(top, c, paths)
        try:
            if resolve(top, base, {p: mine.get(p) for p in paths}, entries(top, up, paths), {}):
                left.append(c)
        except Refuse:
            left.append(c)
    return left


def catchup(top, dry=False):
    up = fetch(top)
    old = out(top, "rev-parse", "HEAD")
    ref = git(top, "symbolic-ref", "-q", "HEAD", check=False).stdout.decode().strip() or "HEAD"
    if old == up:
        print("tree already at %s" % up[:9])
        return
    if not is_ancestor(top, old, up):
        left = local_only(top, up)
        if left:
            raise Refuse("local commits not on origin (catching up would orphan them):\n  "
                         + "\n  ".join(out(top, "log", "-1", "--format=%h %s", c) for c in left)
                         + "\nPublish them first: ./publish --sync")
    raw = git(top, "diff-tree", "-r", "-z", "--no-renames", old, up).stdout.split(b"\0")
    diff = {}
    for i in range(0, len(raw) - 1, 2):
        om, nm, osha, nsha, _ = raw[i].decode().lstrip(":").split()
        diff[raw[i + 1].decode()] = (None if osha == ZERO else (om, osha),
                                     None if nsha == ZERO else (nm, nsha))
    idx = {}
    paths = list(diff)
    for i in range(0, len(paths), 400):
        for rec in git(top, "ls-files", "-s", "-z", "--", *paths[i:i + 400]).stdout.split(b"\0"):
            if rec:
                meta, p = rec.split(b"\t", 1)
                mode, sha, stage = meta.decode().split()
                idx[p.decode()] = (mode, sha) if stage == "0" else ("conflict", stage)
    def disk(p):
        try:
            d = read_disk(top, p)
        except Refuse:
            return p, "dir"
        return p, d and d[0]
    with ThreadPoolExecutor(16) as ex:
        here = dict(ex.map(disk, paths))
    writes, merged, conflicts = {}, {}, []
    for p, (o, n) in diff.items():
        d, i = here[p], idx.get(p)
        sha = lambda e: e and e[1]
        if sha(i) not in (sha(o), sha(n)) and p not in DERIVED:
            conflicts.append("%s: staged in the index (by someone) and changed upstream" % p)
        elif d == sha(n):
            pass
        elif d == sha(o) or p in DERIVED:
            writes[p] = n
        elif o is None:
            conflicts.append("%s: untracked file here collides with a file added upstream" % p)
        elif d is None or n is None or d == "dir":
            conflicts.append("%s: %s here, %s upstream" % (
                p, "deleted" if d is None else "edited", "deleted" if n is None else "edited"))
        else:
            m = merge3(top, cat(top, o[1]), read_disk(top, p)[1], cat(top, n[1]))
            if m is None:
                conflicts.append("%s: edited here and upstream in overlapping lines" % p)
            else:
                merged[p] = (d, m)
    print("catch-up %s -> %s: %d path(s) upstream, %d to write, %d to merge, %d conflict(s)"
          % (old[:9], up[:9], len(diff), len(writes), len(merged), len(conflicts)))
    if conflicts:
        raise Refuse("tree NOT moved — resolve these, then re-run:\n  " + "\n  ".join(conflicts))
    if dry:
        return
    def put(p, data, expect, mode="100644"):
        full = os.path.join(top, p)
        cur = read_disk(top, p)
        if (cur and cur[0]) != expect:     # a peer wrote it since we looked
            raise Refuse("%s changed during catch-up; tree NOT moved (files written so "
                         "far hold upstream content, which is harmless) — re-run" % p)
        if data is None:
            os.remove(full)
            return
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        if mode == "120000":
            if cur:
                os.remove(full)
            os.symlink(data.decode(), full)
            return
        tmp = full + ".publish-tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, full)
    for p, n in writes.items():
        if n is None:
            put(p, None, here[p])
    cat_many(top, [n[1] for n in writes.values() if n],
             lambda s, data: [put(p, data, here[p], n[0]) for p, n in writes.items() if n and n[1] == s])
    for p, (d, m) in merged.items():
        put(p, m, d)
    info = b"".join(ixline(p, n) for p, (o, n) in diff.items() if idx.get(p) != n)
    git(top, "update-index", "-z", "--index-info", inp=info)
    r = git(top, "update-ref", "-m", "publish --catchup", ref, up, old, check=False)
    if r.returncode:
        back = b"".join(ixline(p, idx.get(p)) for p, (o, n) in diff.items()
                        if idx.get(p) != n)
        git(top, "update-index", "-z", "--index-info", inp=back)
        raise Refuse("HEAD moved during catch-up (a peer committed); HEAD untouched, the "
                     "files written hold upstream content (harmless) — re-run")
    print("tree at %s (%d merged in place: %s)" % (up[:9], len(merged),
                                                  ", ".join(sorted(merged)) or "none"))


def janitor(top, apply):
    up = fetch(top)
    wts, cur = [], {}
    for line in out(top, "worktree", "list", "--porcelain").split("\n") + [""]:
        if not line:
            if cur:
                wts.append(cur)
            cur = {}
        else:
            k, _, v = line.partition(" ")
            cur[k] = v or True
    main = wts[0]["worktree"]
    def judge(w):
        p = w["worktree"]
        if w.get("locked"):
            return p, "keep: locked"
        if not os.path.isdir(p):
            return p, "gone"
        # containment first: it reads only objects; status walks a 28k-file checkout
        if not (is_ancestor(p, w["HEAD"], up) or not local_only(p, up, w["HEAD"])):
            return p, "keep: unpublished commits"
        if git(p, "status", "--porcelain", check=False).stdout.strip():
            return p, "keep: uncommitted work"
        return p, "remove"
    def safe_judge(w):
        try:
            return judge(w)
        except Refuse as e:
            return w["worktree"], "keep: " + str(e).split("\n")[0]
    with ThreadPoolExecutor(8) as ex:
        verdicts = list(ex.map(safe_judge, [w for w in wts if w["worktree"] != main]))
    tally = {}
    for p, v in verdicts:
        tally[v.split(":")[0]] = tally.get(v.split(":")[0], 0) + 1
        if v.startswith("keep"):
            print("  %-60s %s" % (p, v))
    print("worktrees: %d  %s" % (len(verdicts), "  ".join("%s=%d" % kv for kv in sorted(tally.items()))))
    if apply:
        for p, v in verdicts:
            if v == "remove":
                git(top, "worktree", "remove", p, check=False)
        git(top, "worktree", "prune")
        print("removed %d; pruned the gone ones" % tally.get("remove", 0))
    st = shutil.disk_usage("/tmp")
    if st.used / st.total > 0.8:
        print("WARNING /tmp is %d%% full — new worktrees belong under %s"
              % (100 * st.used // st.total, WT_ROOT))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("-m", "--message")
    ap.add_argument("-F", "--file", help="read the message from a file ('-' = stdin)")
    ap.add_argument("--commit", nargs="+", metavar="SHA")
    ap.add_argument("--sync", action="store_true")
    ap.add_argument("--catchup", action="store_true")
    ap.add_argument("--worktrees", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-catchup", action="store_true",
                    help="after publishing from the main worktree, do not move it")
    a = ap.parse_args(argv)
    os.makedirs(SCRATCH, exist_ok=True)
    try:
        top = toplevel()
        if a.worktrees:
            return janitor(top, a.apply) or 0
        if a.catchup:
            return catchup(top, a.dry_run) or 0
        if a.sync:
            up = fetch(top)
            for c in local_only(top, up):
                if a.dry_run:
                    print("would publish %s" % out(top, "log", "-1", "--format=%h %s", c))
                    continue
                publish_commit(top, c)
            return catchup(top, a.dry_run) or 0
        if a.commit:
            for c in a.commit:
                publish_commit(top, c)
            return 0
        if not a.paths:
            ap.error("name the files to publish (or --commit/--sync/--catchup/--worktrees)")
        msg = a.message
        if a.file:
            msg = sys.stdin.read() if a.file == "-" else open(a.file).read()
        if not msg or not msg.strip():
            ap.error("a message is required (-m or -F)")
        root = os.path.realpath(top)
        paths = [os.path.relpath(os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(p))),
                                              os.path.basename(os.path.abspath(p))), root)
                 for p in a.paths]
        bad = [p for p in paths if p.startswith("..")]
        if bad:
            ap.error("outside this repo: " + ", ".join(bad))
        sha = publish_paths(top, sorted(set(paths)), msg)
        if sha:
            print("close with: rimflow close <ID> --sha %s" % sha[:12])
        if sha and is_main_worktree(top) and not a.no_catchup:
            try:
                catchup(top)
            except Refuse as e:
                print("(published; this tree was not moved: %s — `./publish --catchup "
                      "--dry-run` for detail)" % str(e).split("\n")[0])
        return 0
    except Refuse as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
