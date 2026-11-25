#!/usr/bin/env python3
"""Selftest of the kept check tree (publish.py full_head_tree; scratch_clone.py shed).
Page: design/specs/2026-11-25-treecheck-kept-tree/boundary.md. One test per promise, named as the promise.

    python3 selftest_treecheck_kept.py              the promises (exit 0 all green, 1 a red)
    python3 selftest_treecheck_kept.py --mutants    plant each fault in a copy of publish.py and require a red
                                                    (exit 0 every plant caught, 1 a plant got past, 2 the harness broke)
PUBLISH_UNDER_TEST=<file> runs the promises against that copy of publish.py (the --mutants harness sets it; the base
commit's publish.py read red this way, see the item's notes).
"""
import contextlib
import fcntl
import importlib.util
import io
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
UNDER = os.environ.get("PUBLISH_UNDER_TEST") or os.path.join(HERE, "publish.py")


def load_publish():
    spec = importlib.util.spec_from_file_location("publish", UNDER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["publish"] = m
    spec.loader.exec_module(m)
    return m


P = load_publish()
if os.environ.get("PUBLISH_UNDER_TEST"):        # a scratch_clone.py beside the copy under test is the one tested
    sys.path.insert(0, os.path.dirname(os.path.abspath(UNDER)))
import scratch_clone as SC  # noqa: E402

BASE = tempfile.mkdtemp(prefix="tckept-", dir=os.path.expanduser("~/.cache"))
__import__("atexit").register(shutil.rmtree, BASE, True)
FAILS = []
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
KEPT = getattr(P, "CHECKTREE_KEPT", "rm-treecheck-kept")      # a clone's own kept tree: the layout before the machine's
KROOT_ENV = getattr(P, "KEPT_ROOT_ENV", "PUBLISH_KEPT_ROOT")
KN_ENV = getattr(P, "KEPT_N_ENV", "PUBLISH_KEPT_TREES")


def machine(name, n=2):
    """Give the next calls a machine of their own: kept trees under BASE/<name>-kept, n of them. -> that folder."""
    root = os.path.join(BASE, name + "-kept")
    os.makedirs(root, exist_ok=True)
    os.environ[KROOT_ENV], os.environ[KN_ENV] = root, str(n)
    return root


def kept_at(root, i=0):
    return os.path.join(root, P.CHECKTREE_PREFIX + "kept-%d" % i)


def check(ok, what):
    print("%s %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def g(cwd, *a, inp=None):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, env=ENV, input=inp)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()))
    return r.stdout.strip()


def repo(name):
    """A clone-like repo: 40 files in 4 folders, an ignore rule, commit A; commit B changes one file. HEAD at B on main,
    plus a tag and a second branch; the kept trees of a machine of its own (machine). -> (top, A, B)."""
    machine(name)
    top = os.path.join(BASE, name)
    os.makedirs(top)
    g(top, "init", "-q", "-b", "main")
    for d in range(4):
        os.makedirs(os.path.join(top, "d%d" % d))
        for f in range(10):
            Path(top, "d%d" % d, "f%d.txt" % f).write_text("file %d %d\n" % (d, f))
    Path(top, ".gitignore").write_text("*.pyc\n")
    g(top, "add", "-A")
    g(top, "commit", "-q", "-m", "A")
    a = g(top, "rev-parse", "HEAD")
    g(top, "tag", "v1")
    g(top, "branch", "side")
    Path(top, "d0", "f0.txt").write_text("changed in B\n")
    g(top, "commit", "-q", "-am", "B")
    return top, a, g(top, "rev-parse", "HEAD")


def quiet(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn()
    return r, buf.getvalue()


def tree_at(top, rev="HEAD", lands=None, keep=None):
    """Enter full_head_tree, run keep(tree) inside, -> (tree path, keep's result, output)."""
    def go():
        with P.full_head_tree(top, rev=rev, what=rev, lands=lands) as t:
            return t, (keep(t) if keep else None)
    (t, res), o = quiet(go)
    return t, res, o


def stats(t):
    out = {}
    for d, _ds, fs in os.walk(t):
        if ".git" in Path(d).relative_to(t).parts:
            continue
        for f in fs:
            st = os.stat(os.path.join(d, f))
            out[os.path.relpath(os.path.join(d, f), t)] = (st.st_ino, st.st_mtime_ns, st.st_ctime_ns)
    return out


def fresh_refs(top):
    """The refs a fresh `git clone --shared` of top holds: what a kept tree must read as."""
    c = tempfile.mkdtemp(prefix="ref-", dir=BASE)
    g(BASE, "clone", "-q", "--shared", "--no-checkout", top, c)
    return g(c, "for-each-ref", "--format=%(objectname) %(refname) %(symref)")


def exact(top, t, sha):
    """-> why the tree is not exactly the commit sha with a fresh clone's refs, or None."""
    if g(t, "rev-parse", "HEAD") != sha:
        return "HEAD %s" % g(t, "rev-parse", "HEAD")
    st = g(t, "status", "--porcelain", "--ignored", "-uall")
    if st:
        return "status %r" % st[:200]
    if g(t, "for-each-ref", "--format=%(objectname) %(refname) %(symref)") != fresh_refs(top):
        return "refs differ from a fresh clone's"
    return None


def t_a_second_checkout_rewrites_only_the_files_that_differ():
    top, a, b = repo("rewrite")
    t1, s1, _o = tree_at(top, rev=a, keep=stats)
    t2, s2, o2 = tree_at(top, rev=b, keep=stats)
    moved = sorted(p for p in s1 if p in s2 and s1[p] != s2[p])
    check(moved == ["d0/f0.txt"],
          "a-second-checkout-rewrites-only-the-files-that-differ: of 41 files only d0/f0.txt is written again "
          "(%d rewritten: %s)" % (len(moved), moved[:4]))
    check("reused" in o2, "a-second-checkout-rewrites-only-the-files-that-differ: the output says the tree was reused "
                          "(%r)" % o2.strip()[-160:])


def t_the_kept_tree_is_exactly_the_commit():
    top, a, b = repo("exact")
    t, _r, _o = tree_at(top)
    # plant what a check run leaves: a stray file, an ignored one, a stray folder, an edit, a staged delete, stale refs
    Path(t, "stray.txt").write_text("left by a check\n")
    Path(t, "d1", "x.pyc").write_text("bytecode\n")
    os.makedirs(os.path.join(t, "out", "deep"))
    Path(t, "out", "deep", "r.json").write_text("{}\n")
    Path(t, "d2", "f3.txt").write_text("file 2 X\n")                    # same size: only the stat tells
    g(t, "rm", "-q", "--cached", "d3/f1.txt")
    g(t, "update-ref", "refs/remotes/origin/main", a)
    g(t, "update-ref", "refs/heads/junk", a)
    g(t, "update-ref", "refs/stash", a)
    g(t, "config", "core.trustctime", "false")
    t2, why, o = tree_at(top, keep=lambda t: exact(top, t, b))
    check(t2 == t and why is None,
          "the-kept-tree-is-exactly-the-commit: stray, ignored, edited, unstaged and ref plants are gone, and the refs "
          "are a fresh clone's (%s; %s)" % (why, "same tree" if t2 == t else "another tree %s" % t2))
    check("reused" in o, "the-kept-tree-is-exactly-the-commit: it was a reuse, not a fresh tree (%r)" % o.strip()[-160:])
    _t, om, _o = tree_at(top, lands=True, keep=lambda t: g(t, "rev-parse", "refs/remotes/origin/main"))
    check(om == b, "the-kept-tree-is-exactly-the-commit: lands sets origin/main to the commit (%s)" % om[:12])
    _t, om, _o = tree_at(top, keep=lambda t: g(t, "rev-parse", "refs/remotes/origin/main"))
    check(om == b and _t == t, "the-kept-tree-is-exactly-the-commit: the next use without lands has origin/main as a "
                               "fresh clone has it (the clone's main)")


def ro_folder(t):
    os.makedirs(os.path.join(t, "ro"))
    Path(t, "ro", "f").write_text("a check's output\n")
    os.chmod(os.path.join(t, "ro"), 0o555)


def t_a_tree_that_cannot_be_made_exact_is_made_fresh():
    top, a, b = repo("broken")
    for plant, how in ((lambda t: Path(t, ".git", "index").write_bytes(b"garbage"), "a garbage index"),
                       (lambda t: shutil.rmtree(os.path.join(t, ".git")), "no .git at all"),
                       (ro_folder, "a read-only folder git clean cannot empty"),
                       (lambda t: Path(t, ".git", "HEAD").write_text("garbage\n"), "a garbage HEAD")):
        t, _r, _o = tree_at(top)
        Path(t, "stray.txt").write_text("x\n")
        plant(t)
        t2, why, o = tree_at(top, keep=lambda t: exact(top, t, b))
        check(why is None and "made fresh" in o and "cannot be made exact" in o
              and t2 == kept_at(os.environ[KROOT_ENV]),
              "a-tree-that-cannot-be-made-exact-is-made-fresh: %s -> exact fresh tree, said why (%s; %r)"
              % (how, why, o.strip()[-200:]))
    check(g(top, "rev-parse", "HEAD") == b and not g(top, "status", "--porcelain"),
          "a-tree-that-cannot-be-made-exact-is-made-fresh: the clone around it is untouched")


HOLDER = r'''
import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_CREAT | os.O_RDWR, 0o644); fcntl.flock(fd, fcntl.LOCK_EX)
open(sys.argv[2], "w").write("held"); time.sleep(60)
'''


def t_a_second_user_makes_its_own_tree():
    top, a, b = repo("second")
    root = os.environ[KROOT_ENV]
    seen = {}

    def outer2(t):
        inner_t, inner, _o = tree_at(top, rev=a, keep=lambda u: g(u, "rev-parse", "HEAD"))
        seen["two"] = (t, inner_t, inner, os.path.isdir(inner_t))
        return exact(top, t, b)
    _t, why, _o = tree_at(top, keep=outer2)
    o_t, i_t, i_head, i_kept = seen["two"]
    check(o_t != i_t and {o_t, i_t} == {kept_at(root, 0), kept_at(root, 1)} and i_head == a and i_kept and why is None,
          "a-second-user-makes-its-own-tree: with two kept trees, a nested call gets the other kept tree at its own rev, "
          "and the outer tree stays exact (%s; %s, %s)" % (why, o_t, i_t))
    root = machine("second-one", n=1)

    def outer(t):
        seen["outer"] = t
        inner_t, inner, _o = tree_at(top, rev=a, keep=lambda u: (g(u, "rev-parse", "HEAD"), stats(u)))
        seen["inner"], seen["inner_head"] = inner_t, inner[0]
        seen["inner_gone"] = not os.path.exists(inner_t)
        return exact(top, t, b)
    _t, why, _o = tree_at(top, keep=outer)
    check(seen["outer"] != seen["inner"] and seen["inner_head"] == a and seen["inner_gone"] and why is None,
          "a-second-user-makes-its-own-tree: a nested call yields another tree at its own rev, removed after, and the "
          "outer tree stays exact (%s)" % why)
    flag = os.path.join(BASE, "held.flag")
    h = subprocess.Popen([sys.executable, "-c", HOLDER, kept_at(root) + ".lock", flag])
    try:
        for _ in range(200):
            if os.path.exists(flag):
                break
            time.sleep(0.05)
        t, why, o = tree_at(top, keep=lambda t: exact(top, t, b))
        check(t != kept_at(root) and why is None and not os.path.exists(t),
              "a-second-user-makes-its-own-tree: while another process holds the kept tree, a call makes its own and "
              "removes it after (%s; %r)" % (why, o.strip()[-120:]))
    finally:
        h.kill()
        h.wait()


def t_a_rev_other_than_head_is_checked_out():
    top, a, b = repo("rev")
    t1, why1, _o = tree_at(top, rev=a, keep=lambda t: (exact(top, t, a), Path(t, "d0", "f0.txt").read_text()))
    t2, why2, _o = tree_at(top, keep=lambda t: (exact(top, t, b), Path(t, "d0", "f0.txt").read_text()))
    check(why1 == (None, "file 0 0\n") and why2 == (None, "changed in B\n") and t1 == t2,
          "a-rev-other-than-head-is-checked-out: rev A gives A's tree, then HEAD moves the same kept tree to B "
          "(%s, %s)" % (why1, why2))


def t_a_clone_back_from_the_pool_gets_no_wrong_tree():
    top, a, b = repo("pool")
    gitdir = Path(top, ".git")
    t, _r, _o = tree_at(top)
    Path(t, "stray.txt").write_text("the last run's\n")
    Path(t, "d1", "f1.txt").write_text("the last run's edit\n")
    g(t, "update-ref", "refs/remotes/origin/main", a)
    (gitdir / "rm-treecheck-abc123" / "src").mkdir(parents=True)          # a random-named tree a killed run left
    (gitdir / KEPT / "src").mkdir(parents=True)                           # a clone's own kept tree, the old layout
    (gitdir / (KEPT + ".lock")).write_text("")
    said, _o = quiet(lambda: SC.shed(Path(top)))
    check(os.path.isdir(t) and not list(gitdir.glob(P.CHECKTREE_PREFIX + "*")),
          "a-clone-back-from-the-pool-gets-no-wrong-tree: shed removes every check tree in the clone (a random one, the "
          "old layout's own kept tree and its lock) and never the machine's kept tree (%s)" % said)
    Path(top, "d2", "f2.txt").write_text("the next run's work\n")
    g(top, "commit", "-q", "-am", "C")
    c = g(top, "rev-parse", "HEAD")
    t2, why, o = tree_at(top, keep=lambda t: exact(top, t, c))
    check(t2 == t and why is None and "reused" in o,
          "a-clone-back-from-the-pool-gets-no-wrong-tree: the next run's first call reuses it, exactly the new commit "
          "(%s)" % why)


def t_a_check_tree_keeps_no_tree_of_its_own():
    top, a, b = repo("nested")
    seen = {}

    def outer(t):
        inner_t, inner, _o = tree_at(t, rev=a, keep=lambda u: g(u, "rev-parse", "HEAD"))
        seen["inner"], seen["head"], seen["gone"] = inner_t, inner, not os.path.exists(inner_t)
        seen["inside"] = sorted(n for n in os.listdir(os.path.join(t, ".git")) if n.startswith(P.CHECKTREE_PREFIX))
        os.makedirs(os.path.join(t, ".git", "rm-treecheck-zz9left", "src"))          # a killed red re-run's leftover
        return None
    t, _r, _o = tree_at(top, keep=outer)
    check(seen["head"] == a and seen["gone"] and not seen["inside"],
          "a-check-tree-keeps-no-tree-of-its-own: a call on the kept tree as top makes a tree at its rev, removes it, "
          "and keeps nothing inside the kept tree's .git (%s)" % seen["inside"])
    _t, _r, o = tree_at(top)
    left = sorted(n for n in os.listdir(os.path.join(t, ".git")) if n.startswith(P.CHECKTREE_PREFIX))
    check(not left and "reused" in o,
          "a-check-tree-keeps-no-tree-of-its-own: the next reuse removes a leftover inside the kept tree's .git (%s)"
          % left)


TERMED = r'''
import os, sys, time
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import importlib.util
spec = importlib.util.spec_from_file_location("publish", sys.argv[2]); P = importlib.util.module_from_spec(spec)
sys.modules["publish"] = P; spec.loader.exec_module(P)
import signal
signal.signal(signal.SIGTERM, getattr(P, "_on_term", signal.SIG_DFL))
import fcntl
fd = os.open(sys.argv[5], os.O_CREAT | os.O_RDWR); fcntl.flock(fd, fcntl.LOCK_EX)
import subprocess
with P.full_head_tree(sys.argv[3]) as t:
    child = subprocess.Popen(["sleep", "300"], start_new_session=True)
    open(sys.argv[4], "w").write("%s %d" % (t, child.pid)); child.wait()
'''


def t_a_killed_publish_leaves_no_random_tree():
    top, a, b = repo("termed")
    root = machine("termed", n=1)
    gitdir = os.path.join(top, ".git")
    flag = os.path.join(BASE, "termed.flag")
    p = subprocess.Popen([sys.executable, "-c", TERMED, HERE, UNDER, top, flag, kept_at(root) + ".lock"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(400):
        if os.path.exists(flag) and open(flag).read():
            break
        time.sleep(0.05)
    t, child = open(flag).read().split()
    p.send_signal(signal.SIGTERM)
    try:
        p.wait(timeout=60)          # budget: danger=a publish that ignores SIGTERM holds the selftest; longest=1s here
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
    alive = os.path.exists("/proc/%s" % child) and "Z" not in open("/proc/%s/stat" % child).read().split()[2]
    if alive:
        os.kill(int(child), signal.SIGKILL)
    check(not os.path.exists(t) and t != kept_at(root) and not alive,
          "a-killed-publish-leaves-no-random-tree: SIGTERM removes the random-named tree and ends the check's session "
          "(tree %s, check %s)" % ("left" if os.path.exists(t) else "gone", "alive" if alive else "ended"))
    _t, _r, _o = tree_at(top)                                           # a kept tree and its lock now exist
    old = time.time() - P.CHECKTREE_STALE_S - 60
    left = os.path.join(gitdir, "rm-treecheck-q1w2e3r4")
    os.makedirs(os.path.join(left, "src"))
    for pth in (left, kept_at(root), kept_at(root) + ".lock"):
        os.utime(pth, (old, old))
    _t, _r, o = tree_at(top)
    check(not os.path.exists(left) and os.path.isdir(kept_at(root)) and "reused" in o
          and os.path.exists(kept_at(root) + ".lock"),
          "a-killed-publish-leaves-no-random-tree: the stale sweep removes an old random-named tree and never the kept "
          "tree or its lock")


def t_one_kept_tree_serves_every_clone_of_the_machine():
    x, a, b = repo("share-x")
    root = machine("share", n=1)
    y = os.path.join(BASE, "share-y")
    g(BASE, "clone", "-q", x, y)
    g(y, "checkout", "-q", "main")
    Path(y, "d3", "f9.txt").write_text("only in y\n")
    g(y, "commit", "-q", "-am", "Y")
    yc = g(y, "rev-parse", "HEAD")
    tx, sx, _o = tree_at(x, keep=stats)
    ty, (why, sy, alt, url), oy = tree_at(y, keep=lambda t: (exact(y, t, yc), stats(t),
                                                           Path(t, ".git/objects/info/alternates").read_text().strip(),
                                                           g(t, "config", "remote.origin.url")))
    moved = sorted(q for q in sx if q in sy and sx[q] != sy[q])
    check(tx == ty == kept_at(root) and why is None and "reused" in oy and moved == ["d3/f9.txt"],
          "one-kept-tree-serves-every-clone-of-the-machine: the tree x used is reused for y, exactly y's commit with a "
          "fresh clone of y's refs, rewriting only the file that differs (%s; %s)" % (why, moved[:4]))
    check(alt == os.path.join(y, ".git", "objects") and url == y,
          "one-kept-tree-serves-every-clone-of-the-machine: it borrows y's objects and names y as its origin "
          "(%s; %s)" % (alt, url))
    Path(x, "d1", "f1.txt").write_text("only in x\n")                 # the tree's HEAD now names a commit y lacks
    g(x, "commit", "-q", "-am", "X")
    tree_at(x)
    shutil.rmtree(x)                                                    # and the clone that holds it is gone
    t2, why, o = tree_at(y, keep=lambda t: exact(y, t, yc))
    check(t2 == kept_at(root) and why is None and "reused" in o,
          "one-kept-tree-serves-every-clone-of-the-machine: after the last clone it served is removed, the next clone "
          "still reuses it, never reading that clone's commits (%s; %r)" % (why, o.strip()[-160:]))
    for i in range(3):
        z = os.path.join(BASE, "share-z%d" % i)
        g(BASE, "clone", "-q", y, z)
        tree_at(z)
    trees = sorted(n for n in os.listdir(root) if not n.endswith(".lock"))
    check(trees == [os.path.basename(kept_at(root))] and not any(
              n.startswith(P.CHECKTREE_PREFIX) for i in range(3)
              for n in os.listdir(os.path.join(BASE, "share-z%d" % i, ".git"))),
          "one-kept-tree-serves-every-clone-of-the-machine: three more clones add no tree, on the machine or in a "
          "clone (%s)" % trees)


def t_a_repo_outside_rm_root_keeps_its_tree_in_its_own_git_dir():
    top, a, b = repo("outside")
    del os.environ[KROOT_ENV]
    fake_rm = os.path.join(BASE, "fake-rm")
    os.makedirs(fake_rm)
    was, P.RM_ROOT = P.RM_ROOT, fake_rm
    try:
        t, why, o = tree_at(top, keep=lambda t: exact(top, t, b))
        t2, why2, o2 = tree_at(top, keep=lambda t: exact(top, t, b))
        inside = os.path.join(fake_rm, "clone")
        g(BASE, "clone", "-q", top, inside)
        t3, why3, _o = tree_at(inside, keep=lambda t: exact(inside, t, b))
    finally:
        P.RM_ROOT = was
    check(t == t2 == os.path.join(top, ".git", KEPT) and why is None and why2 is None and "reused" in o2
          and t3 == os.path.join(fake_rm, "treecheck-kept", P.CHECKTREE_PREFIX + "kept-0") and why3 is None,
          "a-repo-outside-rm-root-keeps-its-tree-in-its-own-git-dir: a temp repo keeps one tree in its .git and reuses "
          "it; a clone under RM_ROOT uses the machine's (%s; %s; %s)" % (t, t3, why3))


def t_a_clone_keeps_no_kept_tree_of_its_own():
    top, a, b = repo("legacy")
    old = os.path.join(top, ".git", KEPT)
    os.makedirs(os.path.join(old, "src"))
    Path(old, "src", "f").write_text("a full checkout of the old layout\n")
    flag = os.path.join(BASE, "legacy.flag")
    h = subprocess.Popen([sys.executable, "-c", HOLDER, old + ".lock", flag])
    try:
        for _ in range(200):
            if os.path.exists(flag):
                break
            time.sleep(0.05)
        _t, why, o = tree_at(top, keep=lambda t: exact(top, t, b))
        check(os.path.isdir(old) and why is None and "stays for now" in o,
              "a-clone-keeps-no-kept-tree-of-its-own: while an older publish holds the clone's own kept tree, it stays "
              "and the checks still run (%s)" % why)
    finally:
        h.kill()
        h.wait()
    _t, why, o = tree_at(top, keep=lambda t: exact(top, t, b))
    check(not os.path.exists(old) and why is None and "removed this clone's own kept tree" in o,
          "a-clone-keeps-no-kept-tree-of-its-own: the next call removes the clone's own kept tree and says so (%r)"
          % o.strip()[:160])



# (name, old text, new text): each plant breaks one promise in a copy of publish.py
MUTANTS = [
    ("no clean of a check run's files", '(["clean", "-q", "-ffdx"], ["checkout"', '(["checkout"'),
    ("checkout without -f keeps an edit", '["checkout", "-q", "-f", "--detach", head]', '["checkout", "-q", "--detach", head]'),
    ("no ref sync", "    why = _sync_kept_refs(top, tree)\n", "    why = None\n"),
    ("a clean that exits 0 and keeps ignored files, and no status reading behind it",
     '    if r.returncode or r.stdout.strip():\n        return "git status', '    if False:\n        return "git status'),
    ("a broken kept tree is used as it is", 'if os.path.lexists(kept) else "none kept yet"', 'if False else "none kept yet"'),
    ("the lock is ignored", "        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)\n    except OSError:\n        os.close(fd)\n"
     "        return None, \"another", "        pass\n    except OSError:\n        os.close(fd)\n        return None, \"another"),
    ("a read-only folder blocks the fresh tree", '    shutil.rmtree(p, **({"onexc": fix} if sys.version_info >= (3, 12) else {"onerror": fix}))', "    shutil.rmtree(p, ignore_errors=True)"),
    ("rev is ignored", "    head = out(top, \"rev-parse\", rev)\n    t0", "    head = out(top, \"rev-parse\", \"HEAD\")\n    t0"),
    ("SIGTERM kills no check", "    _kill_own_sessions()\n    raise SystemExit", "    raise SystemExit"),
    ("SIGTERM skips clean-up", "    raise SystemExit(128 + signum)", "    os._exit(128 + signum)"),
    ("alternates not repointed", '            f.write(_objects_of(top) + "\\n")', "            pass"),
    ("origin stays the last clone's", '    r = _treegit(tree, "config", "remote.origin.url", top)', '    r = _treegit(tree, "config", "core.bare")'),
    ("one kept tree per clone again", "    root = kept_root(top)\n    if root is None:", '    root = None\n    if root is None:'),
    ("the old per-clone tree stays", "    dropped = _drop_clone_kept(gitdir) if", "    dropped = None if"),
    ("a temp repo writes the machine's trees", '        return os.path.join(RM_ROOT, "treecheck-kept")\n    return None',
     '        return os.path.join(RM_ROOT, "treecheck-kept")\n    return os.path.join(RM_ROOT, "treecheck-kept")'),
    ("one kept tree whatever the slots", "names = sorted((CHECKTREE_PREFIX + \"kept-%d\" % i for i in range(kept_n()))",
     "names = sorted((CHECKTREE_PREFIX + \"kept-%d\" % i for i in range(1))"),
    ("a check tree keeps a tree of its own", '        if os.path.basename(os.path.realpath(top)).startswith(CHECKTREE_PREFIX) else',
     '        if False else'),
    ("a leftover inside the kept tree stays", "        if n.startswith(CHECKTREE_PREFIX):\n            _rmtree_hard(os.path.join(gd, n))",
     "        if False:\n            _rmtree_hard(os.path.join(gd, n))"),
    ("a fresh tree every time", "            if why is None:\n                how", "            if False:\n                how"),
]


def mutants():
    src = open(os.path.join(HERE, "publish.py")).read()
    bad = 0
    for name, old, new in MUTANTS:
        if src.count(old) != 1:
            print("HARNESS BROKEN: the plant %r does not match publish.py once (%d)" % (name, src.count(old)))
            return 2
        mutated = src.replace(old, new)
        if name.startswith("a clean that exits 0"):
            mutated = mutated.replace('(["clean", "-q", "-ffdx"]', '(["clean", "-q", "-ffd"]')
        d = tempfile.mkdtemp(prefix="tckept-mut-", dir=os.path.expanduser("~/.cache"))
        f = os.path.join(d, "publish.py")
        open(f, "w").write(mutated)
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, PUBLISH_UNDER_TEST=f),
                           capture_output=True, text=True)
        shutil.rmtree(d, True)
        caught = r.returncode == 1 and "FAIL " in r.stdout
        bad += not caught
        print("%s plant %r -> exit %d, %d FAIL line(s)" % ("CAUGHT" if caught else "NOT CAUGHT", name, r.returncode,
                                                            r.stdout.count("\nFAIL ") + r.stdout.startswith("FAIL ")))
    print("RESULT: %s" % ("every plant caught" if not bad else "%d plant(s) got past" % bad))
    return 1 if bad else 0


def main():
    if "--mutants" in sys.argv:
        return mutants()
    tests = [t_a_second_checkout_rewrites_only_the_files_that_differ, t_the_kept_tree_is_exactly_the_commit,
             t_a_tree_that_cannot_be_made_exact_is_made_fresh, t_a_second_user_makes_its_own_tree,
             t_a_rev_other_than_head_is_checked_out, t_a_clone_back_from_the_pool_gets_no_wrong_tree,
             t_a_check_tree_keeps_no_tree_of_its_own, t_a_killed_publish_leaves_no_random_tree,
             t_one_kept_tree_serves_every_clone_of_the_machine, t_a_clone_keeps_no_kept_tree_of_its_own,
             t_a_repo_outside_rm_root_keeps_its_tree_in_its_own_git_dir]
    for t in tests:
        try:
            t()
        except Exception as e:                # a test that crashes is a red, named
            check(False, "%s crashed: %s: %s" % (t.__name__[2:].replace("_", "-"), type(e).__name__, e))
    print("RESULT: %s" % ("GREEN, %d tests" % len(tests) if not FAILS else "RED, %d failing" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
