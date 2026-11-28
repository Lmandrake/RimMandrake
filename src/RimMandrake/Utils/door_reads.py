#!/usr/bin/env python3
"""What each pipeline test read the last time the door ran it, so the door runs only the tests a change touches
(CLAUDE.md §After a change, only the checks that the change touches run again).

The door's import closure (publish.door_inputs) tied 226 of 243 pipeline tests to almost every pipeline file through
hub modules: role_launch -> ops_watch -> testq, control -> detached_helper -> guiding_prose -> publish (measured
2026-11-26). A test that never loads a module does not read or exercise it. So publish.py runs each pipeline test with
door_reads_hook/ first on PYTHONPATH; the hook writes the repo paths the test's processes open, import and list. After
a green run the record is kept, with the git blob of every path it read.

    hook_env(env, tree, rec)          the test's environment with the hook on, writing to the file rec
    keep(store, test, rec, blobs)     keep a green run's record (blobs: path -> blob of the tree the test ran on)
    relation(store, test, changed, blobs) -> ("touched" | "not touched" | "unknown", why); blobs of the change's base

A record decides only while the code it ran is unchanged: every .py file it read must have the same blob at the base.
Else, and when there is no record, or the record holds a read the hook cannot see, the answer is "unknown" and the door
keeps its import closure for that test. Page: design/specs/2026-11-26-door-reads/boundary.md.
"""
import hashlib
import json
import os
import posixpath
import re
import shlex
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK_DIR = os.path.join(HERE, "door_reads_hook")
FORMAT = 2          # 2 (2026-11-27): a record parsed before git stdin reads and empty `--` were unknown decides nothing
PYC = re.compile(r"^(?:(.*)/)?__pycache__/([^/.]+)\.[^/]+\.pyc$")
# children that read no file of the tree whatever folder they start in
NO_READ = frozenset(("true", "false", "sleep", "systemd-cat", "wslpath", "date", "echo", "nproc", "uname", "id",
                     "hostname", "kill", "touch", "mkdir", "printf"))
# git verbs whose reads are their `rev:path` arguments and `-- paths`, never the whole tree
GIT_NAMED = frozenset(("rev-parse", "config", "remote", "symbolic-ref", "merge-base", "rev-list", "init", "cat-file", "hash-object", "update-ref", "cherry", "for-each-ref", "show",
                       "check-ignore", "var", "version"))
GIT_PATHSPEC = frozenset(("log", "diff", "ls-tree", "ls-files", "diff-tree", "grep", "blame", "status", "archive"))


def hook_env(env, tree, rec):
    """-> a copy of env with the hook on for a test run in `tree`, its record written to the file `rec`."""
    pp = [p for p in (env.get("PYTHONPATH") or "").split(os.pathsep) if p]
    return dict(env, RM_DOOR_READS=rec, RM_DOOR_READS_ROOT=tree, PYTHONPATH=os.pathsep.join([HOOK_DIR] + pp))


def _git_reads(argv, cwd=None):
    """-> (paths, None) a git child aimed at the tree reads (relative to the tree), or (None, why) when it reads the tree
    as a whole (a listing, a status, a clone or fetch of it, a commit in it, an empty pathspec after `--`) or reads
    paths that its argv does not name (`--batch`, `--stdin-paths`: they come on its input). cwd: the child's folder
    relative to the tree; its `-- paths` are relative to it, as git reads them."""
    a, i = argv[1:], 0
    while i < len(a) and a[i].startswith("-"):
        if a[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(a):
            i += 2
        else:
            i += 1
    if i >= len(a):
        return set(), None
    sub, rest = a[i], a[i + 1:]
    if any(x == "--stdin-paths" or x.startswith("--batch") for x in rest):
        return None, "git %s reads the paths on its input" % sub
    under = "" if cwd in (None, "", ".") else cwd.strip("/") + "/"
    paths = set()
    for x in rest:
        if ":" in x and not x.startswith("-") and not x.startswith(":"):
            p = x.split(":", 1)[1]
            if p.startswith(("./", "../")):        # `rev:./path` is relative to the child's folder, as git reads it
                p = posixpath.normpath(under + p)
                if p == "." or p.startswith(".."):
                    return None, "git %s names the tree's top (or above it) as %s" % (sub, x)
            p = p.strip("/")
            if p:
                paths.add(p)
    named = [posixpath.normpath(under + x) for x in rest[rest.index("--") + 1:] if x] if "--" in rest else []
    if any(x == "." or x.startswith("../") or x == ".." for x in named):
        return None, "git %s names the tree's top (or above it) after --" % sub
    paths |= set(named)
    if sub in GIT_NAMED:
        return paths, None
    if sub in GIT_PATHSPEC and named:
        return paths, None
    return None, "git %s reads the tree as a whole" % sub


def parse(rec):
    """-> {"files": set, "dirs": set, "unknown": [why, ...]} from a record file the hook wrote (no file: unknown)."""
    files, dirs, unknown = set(), set(), []
    try:
        with open(rec, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return {"files": files, "dirs": dirs, "unknown": ["the hook wrote no record"]}
    for ln in lines:
        kind, _, text = ln.partition(" ")
        if kind == "R":
            m = PYC.match(text)
            files.add(("%s/%s.py" % (m.group(1), m.group(2))).lstrip("/") if m else text)
        elif kind == "D":
            dirs.add(text)
        elif kind == "X":
            unknown.append(text)
        elif kind == "C":
            try:
                c = json.loads(text)
                argv = c["argv"] if isinstance(c["argv"], list) else shlex.split(c["argv"])
            except (ValueError, KeyError, TypeError):
                unknown.append("an unreadable child line: %s" % text[:120])   # cut-ok: names the line, decides nothing
                continue
            exe = os.path.basename(str(argv[0])) if argv else ""
            if len(argv) == 1 and " " in exe:       # a shell string
                argv = shlex.split(argv[0]) if argv[0] else argv
                exe = os.path.basename(argv[0]) if argv else ""
            if exe in NO_READ:
                continue
            if exe == "git":
                got, why = _git_reads([str(x) for x in argv], c.get("cwd"))
                if why:
                    unknown.append(why)
                else:
                    files |= got
                continue
            unknown.append("a %s child aimed at the tree" % (exe or "nameless"))
        elif ln.strip():
            unknown.append("an unreadable record line: %s" % ln[:120])        # cut-ok: names the line, decides nothing
    return {"files": files, "dirs": dirs, "unknown": unknown}


def tree_blobs(git, rev):
    """-> {path: blob} of every file at rev, and {dir: sorted names} of every folder, from one `git ls-tree -r`.
    git(*args) -> CompletedProcess. Raises OSError when it cannot be read."""
    r = git("ls-tree", "-r", "-z", "--full-tree", rev)
    if r.returncode:
        raise OSError("git ls-tree %s: %s" % (rev, (r.stderr or "").strip()))
    blobs, names = {}, {}
    for ent in (r.stdout or "").split("\0"):
        if not ent:
            continue
        meta, _, path = ent.partition("\t")
        blobs[path] = meta.split()[2]
        d, _, n = path.rpartition("/")
        while True:
            names.setdefault(d or ".", set()).add(n)
            if not d:
                break
            d, _, n = d.rpartition("/")
    return blobs, {d: sorted(v) for d, v in names.items()}


def _path(store, test):
    return os.path.join(store, hashlib.sha1(test.encode()).hexdigest()[:20] + ".json")


def keep(store, test, rec, blobs):
    """Keep the record of a green run of `test`. blobs: tree_blobs() of the commit the test ran on. A record with a
    read the hook cannot see is kept too (it answers "unknown", and says why). -> (kept path, None), or (None, why)
    when it could not be written (then the test has no new record, and the next door keeps the import closure)."""
    reads = parse(rec)
    b, names = blobs
    doc = {"format": FORMAT, "test": test, "files": {p: b.get(p) for p in sorted(reads["files"])},
           "dirs": {d: names.get(d, []) for d in sorted(reads["dirs"])}, "unknown": reads["unknown"][:20]}
    try:
        os.makedirs(store, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".rec-", dir=store)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        os.replace(tmp, _path(store, test))
        return _path(store, test), None
    except OSError as e:
        return None, "the record could not be written: %s" % e


def relation(store, test, changed, blobs):
    """-> (answer, why): does the change touch what `test` read? blobs: tree_blobs() of the change's base commit.
    "unknown" whenever the record cannot decide; the caller then keeps its own rule."""
    try:
        with open(_path(store, test), encoding="utf-8") as f:
            doc = json.load(f)
    except FileNotFoundError:
        return "unknown", "no record of a green run yet"
    except (OSError, ValueError) as e:
        return "unknown", "its record cannot be read: %s" % e
    if doc.get("format") != FORMAT or doc.get("test") != test:
        return "unknown", "its record is of another format or test"
    if doc.get("unknown"):
        return "unknown", "its record holds a read the hook cannot see (%s)" % doc["unknown"][0]
    b, names = blobs
    files, dirs = doc.get("files") or {}, doc.get("dirs") or {}
    for p, blob in files.items():
        if p.endswith(".py") and b.get(p) != blob:
            return "unknown", "its record ran another version of %s" % p
    if test in changed:
        return "touched", "the change edits the test itself"
    for p in changed:
        if p in files:
            return "touched", "it read %s" % p
        if (p.rpartition("/")[0] or ".") in dirs:
            return "touched", "it listed %s" % (p.rpartition("/")[0] or ".")
        if any(p.startswith(f.rstrip("/") + "/") for f in files):
            return "touched", "it read a folder holding %s" % p
        # a folder it listed higher up gains an entry when p sits in a folder that is new there (a glob of
        # specs/*/page.md, or a walk, finds the file in it)
        parts = p.split("/")
        for k in range(len(parts) - 1):
            up = "/".join(parts[:k]) or "."
            if up in dirs and parts[k] not in (dirs[up] or ()):
                return "touched", "it listed %s, which gains %s" % (up, parts[k])
    return "not touched", "it read none of the changed paths (%d files, %d folders)" % (len(files), len(dirs))
