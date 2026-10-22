#!/usr/bin/env python3
"""Selftest for publish.py (the thin plain-git wrapper) against a throwaway bare repo + clones
on ext4 (never /tmp).

    python3 src/RimMandrake/Utils/selftest_publish.py
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import publish as P  # noqa: E402

ROOT = os.path.expanduser("~/.cache/publish-selftest")
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}
os.environ.update(ENV)
LINES = "".join("line %d\n" % i for i in range(1, 11))


def sh(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout.strip()


def write(repo, path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)


def show(repo, path, ref="origin/main"):
    sh(repo, "fetch", "-q")
    return sh(repo, "show", "%s:%s" % (ref, path)) + "\n"


def world():
    os.makedirs(ROOT, exist_ok=True)
    d = tempfile.mkdtemp(dir=ROOT)
    bare, a, b = (os.path.join(d, n) for n in ("bare.git", "a", "b"))
    sh(d, "init", "-q", "--bare", "-b", "main", bare)
    sh(d, "clone", "-q", bare, a)
    write(a, "f.txt", LINES)
    write(a, "g.txt", "g\n")
    sh(a, "add", "f.txt", "g.txt")
    sh(a, "commit", "-q", "-m", "seed")
    sh(a, "push", "-q", "origin", "HEAD:main")
    sh(d, "clone", "-q", bare, b)
    return d, a, b


def peer_push(b, path, text, msg="peer"):
    sh(b, "pull", "-q", "--rebase")
    write(b, path, text)
    sh(b, "add", path)
    sh(b, "commit", "-q", "-m", msg, "--", path)
    sh(b, "push", "-q", "origin", "HEAD:main")
    return sh(b, "rev-parse", "HEAD")


def quiet(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a)
    return r, buf.getvalue()


def refused(fn, *a):
    try:
        quiet(fn, *a)
    except P.Refuse as e:
        return str(e)
    return None


def t_commits_only_named_paths(a, b):
    write(a, "f.txt", LINES.replace("line 3", "LINE 3"))
    write(a, "g.txt", "dirty, not mine to publish\n")
    write(a, "junk.txt", "untracked\n")
    sh(a, "add", "g.txt")                                     # a staged peer file must not ride along
    sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    assert "PUBLISHED %s" % sha in log, log
    assert sha == sh(a, "rev-parse", "HEAD") == sh(a, "rev-parse", "origin/main")
    assert "LINE 3" in show(a, "f.txt") and show(a, "g.txt") == "g\n"
    assert sh(a, "show", "--name-only", "--format=", "HEAD") == "f.txt"


def t_new_file_and_delete(a, b):
    write(a, "dir/new.sh", "#!/bin/sh\n")
    os.remove(os.path.join(a, "g.txt"))
    quiet(P.publish, a, ["dir/new.sh", "g.txt"], "add+rm")
    names = sh(a, "ls-tree", "-r", "--name-only", "origin/main").split()
    assert "dir/new.sh" in names and "g.txt" not in names, names


def t_rebases_onto_moved_origin(a, b):
    peer = peer_push(b, "g.txt", "peer g\n")
    write(a, "f.txt", LINES.replace("line 9", "LINE 9"))
    sha, _ = quiet(P.publish, a, ["f.txt"], "mine")
    assert sh(a, "rev-parse", sha + "^") == peer
    assert "LINE 9" in show(a, "f.txt") and show(a, "g.txt") == "peer g\n"


def t_push_race_retries(a, b):
    write(a, "f.txt", LINES.replace("line 5", "LINE 5"))
    seen = {}

    def race(attempt):
        if attempt == 0:
            seen["peer"] = peer_push(b, "g.txt", "raced\n")
    P.before_push = race
    try:
        sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    finally:
        P.before_push = None
    assert "origin moved" in log, log
    assert sh(a, "rev-parse", sha + "^") == seen["peer"]


def t_dirty_tree_survives_rebase(a, b):
    peer_push(b, "g.txt", "peer\n")
    write(a, "f.txt", LINES.replace("line 1\n", "LINE 1\n"))
    write(a, "h.txt", "untracked\n")
    sh(a, "add", "h.txt")
    sh(a, "commit", "-q", "-m", "h", "--", "h.txt")
    write(a, "h.txt", "uncommitted edit\n")                     # reset --keep must leave it alone
    quiet(P.publish, a, ["f.txt"], "mine")
    assert open(os.path.join(a, "h.txt")).read() == "uncommitted edit\n"
    assert show(a, "h.txt") == "untracked\n"


def t_dirty_edit_upstream_changed_is_refused(a, b):
    peer_push(b, "g.txt", "peer v2\n")
    write(a, "g.txt", "my uncommitted edit\n")                 # dirty, and origin changed the same file
    write(a, "f.txt", LINES.replace("line 3", "LINE 3"))
    why = refused(P.publish, a, ["f.txt"], "mine")
    assert why and "reset --keep" in why and "g.txt" in why, why
    assert open(os.path.join(a, "g.txt")).read() == "my uncommitted edit\n"
    assert sh(a, "log", "-1", "--format=%s") == "mine"          # commit intact locally
    assert not sh(a, "stash", "list")                           # and nothing was stashed


def t_conflict_aborts_rebase(a, b):
    peer_push(b, "g.txt", "peer says x\n")
    write(a, "g.txt", "i say y\n")
    why = refused(P.publish, a, ["g.txt"], "clash")
    assert why and "g.txt" in why, why
    assert not os.path.isdir(os.path.join(a, ".git", "rebase-merge"))
    assert sh(a, "log", "-1", "--format=%s") == "clash"         # commit intact locally


def t_ambiguous_push_detected_as_landed(a, b):
    write(a, "f.txt", LINES.replace("line 2", "LINE 2"))
    real = P.run

    def flaky(top, *args, check=True):
        if args[:1] == ("push",):
            real(top, *args, check=check)                       # remote accepts...
            return subprocess.CompletedProcess(args, 128, "", "fatal: the remote end hung up")
        return real(top, *args, check=check)
    P.run = flaky
    try:
        sha, log = quiet(P.publish, a, ["f.txt"], "mine")
    finally:
        P.run = real
    assert "it landed" in log, log
    assert sha == sh(a, "rev-parse", "origin/main")


def t_nothing_to_publish(a, b):
    why = refused(P.publish, a, ["f.txt"], "noop")
    assert why and "nothing to publish" in why, why


def t_pushes_existing_local_commits(a, b):
    write(a, "x.txt", "x\n")
    sh(a, "add", "x.txt")
    sh(a, "commit", "-q", "-m", "x", "--", "x.txt")
    sha, _ = quiet(P.publish, a, [], None)
    assert sha == sh(a, "rev-parse", "origin/main")


def t_refuses_on_mnt(a, b):
    real = os.path.realpath
    P.os.path.realpath = lambda p: "/mnt/d/Luke/dev/RimMandrake" if p == a else real(p)
    try:
        why = refused(P.publish, a, ["f.txt"], "x")
    finally:
        P.os.path.realpath = real
    assert why and "/home/mandrake/rm/<seat>" in why, why


# ---- committed mod DLLs at landing (rebuilt from committed source, winbuild mocked) ----------------------
MOD = "src/RimMandrake/M"
DLL = MOD + "/Assemblies/M.dll"
HOOK = r"""#!/usr/bin/env python3
import hashlib, subprocess, sys
def git(*a):
    return subprocess.run(["git", *a], capture_output=True).stdout
for line in sys.stdin.read().splitlines():
    sha = line.split()[1]
    names = sorted(n for n in git("ls-tree", "-r", "--name-only", sha, "--", "%(mod)s/Source").decode().split()
                   if n.endswith(".cs"))
    want = "dll:" + hashlib.sha256(b"".join(n.encode() + git("show", "%%s:%%s" %% (sha, n)) for n in names)).hexdigest()
    if git("show", "%%s:%(dll)s" %% sha).decode() != want:
        sys.stderr.write("pre-push REFUSED (DLL_SOURCE_STAMP_GUARD_1): committed DLL disagrees\n  MISMATCH %(dll)s\n")
        sys.exit(1)
""" % {"mod": MOD, "dll": DLL}


def fake_build(tree):
    """What the mocked winbuild writes for the C# in `tree` (a worktree root)."""
    import hashlib
    src = os.path.join(tree, MOD, "Source")
    names = sorted(f for f in os.listdir(src) if f.endswith(".cs"))
    data = b"".join((MOD + "/Source/" + n).encode() + open(os.path.join(src, n), "rb").read() for n in names)
    write(tree, DLL, "dll:" + hashlib.sha256(data).hexdigest())
    write(tree, DLL + ".srchash", "# project: RimMandrake/M/Source/M.csproj\n" + "".join(
        "%s %s\n" % (hashlib.sha256(open(os.path.join(src, n), "rb").read()).hexdigest(), n) for n in names))


def mock_winbuild(calls):
    def wb(scratch, csproj):
        calls.append((scratch, os.path.relpath(csproj, scratch)))
        fake_build(scratch)
        return 0, "BUILT"
    return wb


def seed_mod(a, b):
    for n in ("A", "B", "C"):
        write(a, MOD + "/Source/%s.cs" % n, "class %s {}\n" % n)
    write(a, MOD + "/Source/M.csproj", "<Project/>\n")
    fake_build(a)
    sh(a, "add", MOD)
    sh(a, "commit", "-q", "-m", "mod")
    sh(a, "push", "-q", "origin", "HEAD:main")
    sh(b, "pull", "-q", "--rebase")
    P.SCRATCH_ROOT = os.path.join(os.path.dirname(a), "scratch")


def dll_matches(repo, ref="origin/main"):
    """origin's DLL equals a build of origin's committed source (checked in a fresh checkout)."""
    chk = os.path.join(os.path.dirname(repo), "chk")
    shutil.rmtree(chk, ignore_errors=True)
    sh(repo, "fetch", "-q")
    sh(os.path.dirname(repo), "clone", "-q", "--shared", repo, chk)
    sh(chk, "checkout", "-q", "--detach", sh(repo, "rev-parse", ref))
    want = open(os.path.join(chk, DLL)).read()
    fake_build(chk)
    return open(os.path.join(chk, DLL)).read() == want


def t_dll_only_replay_conflict_rebuilds(a, b):
    seed_mod(a, b)
    write(b, MOD + "/Source/A.cs", "class A { int peer; }\n")       # peer: source + its DLL, landed first
    fake_build(b)
    sh(b, "add", MOD)
    sh(b, "commit", "-q", "-m", "peer A + dll")
    sh(b, "push", "-q", "origin", "HEAD:main")
    write(a, MOD + "/Source/B.cs", "class B { int mine; }\n")       # mine: another file + my DLL -> DLL-only conflict
    fake_build(a)
    write(a, MOD + "/Source/C.cs", "class C { UNCOMMITTED PEER EDIT }\n")   # must not leak into the build
    calls = []
    real, P.winbuild = getattr(P, "winbuild", None), mock_winbuild(calls)
    try:
        sha, log = quiet(P.publish, a, [MOD + "/Source/B.cs", DLL, DLL + ".srchash"], "mine B + dll")
    finally:
        P.winbuild = real
    assert "PUBLISHED" in log and calls, log
    assert sha == sh(a, "rev-parse", "origin/main")
    assert "int peer" in show(a, MOD + "/Source/A.cs") and "int mine" in show(a, MOD + "/Source/B.cs")
    assert dll_matches(a), "landed DLL is not a build of the landed source"
    assert "UNCOMMITTED" in open(os.path.join(a, MOD + "/Source/C.cs")).read()      # peer edit untouched
    assert not sh(a, "stash", "list") and not os.listdir(P.SCRATCH_ROOT)             # no stash, scratch removed


def t_stamp_guard_refusal_rebuilds_and_retries(a, b):
    seed_mod(a, b)
    hooks = os.path.join(os.path.dirname(a), "hooks")
    write(hooks, "pre-push", HOOK)
    os.chmod(os.path.join(hooks, "pre-push"), 0o755)
    sh(a, "config", "core.hooksPath", hooks)
    write(a, MOD + "/Source/B.cs", "class B { int changed; }\n")    # source only: the committed DLL goes stale
    write(a, MOD + "/Source/C.cs", "class C { UNCOMMITTED PEER EDIT }\n")
    calls = []
    real, P.winbuild = getattr(P, "winbuild", None), mock_winbuild(calls)
    P.MAX_TRIES, old_tries = 2, P.MAX_TRIES
    try:
        sha, log = quiet(P.publish, a, [MOD + "/Source/B.cs"], "source only")
    finally:
        P.winbuild, P.MAX_TRIES = real, old_tries
    assert "DLL_SOURCE_STAMP_GUARD_1" in log and len(calls) == 1, log
    assert sha == sh(a, "rev-parse", "origin/main") and dll_matches(a)
    assert "UNCOMMITTED" in open(os.path.join(a, MOD + "/Source/C.cs")).read()


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("t_")]


def main():
    ok = 0
    for t in TESTS:
        d, a, b = world()
        try:
            t(a, b)
            ok += 1
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, e))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print("%d/%d passed" % (ok, len(TESTS)))
    return 0 if ok == len(TESTS) else 1


if __name__ == "__main__":
    sys.exit(main())
