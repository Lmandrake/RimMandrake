#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_BUILD_ONE_TEST_CALL_PARENT_FIX_AND_FAULT (rank 4 of one_page.md).

Contract: a new module src/RimMandrake/Utils/redgreen.py
  redgreen(root, command, parent="HEAD", overlay=(), faults=(), reads_build=(), deadline_s=600) -> dict
      command: argv list of one test, run from the tree's root. parent: the commit of the old code. overlay: paths whose
      working-tree bytes go on top of the parent (a new test file). faults: patch files, each applied to the working tree,
      run, and reversed. reads_build: built files (a DLL) that the test reads.
      -> {"answer", "why", "parent": leg, "work": leg, "faults": [leg + "patch"]}; leg = {"verdict": "red"|"green"|
      "could_not_look", "rc", "tree", "build": {path: sha256 or "absent"}, "lines": [the failing lines], "why"}
      A test exits 1 for red and 0 for green; any other exit, a hang, or a test that cannot start is could_not_look.
      answer: RED_THEN_GREEN (parent red, work green, every fault red) | GREEN_ON_PARENT (the test did not see the fault)
      | RED_ON_WORK | GREEN_ON_FAULT (a fault stays green: it proves nothing) | COULD_NOT_LOOK.
      The caller's tree and index are byte-identical after every call, uncommitted edits included.
Expected when built: PASS 15/15."""
import hashlib
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

RG = H.load("redgreen")
TEST = "import sys\nsys.path.insert(0, '.')\nimport a\nok = a.f() == 2\nprint('FAIL f gives %s' % a.f() if not ok else 'PASS')\nsys.exit(0 if ok else 1)\n"


def git(d, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", d] + list(a), check=True,
                          capture_output=True, text=True).stdout


def repo(old="def f():\n    return 1\n", new="def f():\n    return 2\n", test_at_parent=True, test=TEST):
    d = tempfile.mkdtemp()
    git(d, "init", "-q", "-b", "main")
    w = lambda n, t: open(os.path.join(d, n), "w").write(t)  # noqa: E731
    w("a.py", old)
    w("notes.txt", "n\n")
    if test_at_parent:
        w("t.py", test)
    git(d, "add", ".")
    git(d, "commit", "-qm", "parent")
    w("a.py", new)
    w("notes.txt", "n\nmy own uncommitted line\n")
    w("t.py", test)
    return d


def patch(d, old, new):
    p = os.path.join(tempfile.mkdtemp(), "f.patch")
    with open(p, "w") as f:
        f.write("--- a/a.py\n+++ b/a.py\n@@ -1,2 +1,2 @@\n def f():\n-    return %s\n+    return %s\n" % (old, new))
    return p


def snap(d):
    out = {}
    for r, ds, fs in os.walk(d):
        ds[:] = [x for x in ds if x not in (".git", "__pycache__")]
        for f in fs:
            out[os.path.join(r, f)] = open(os.path.join(r, f), "rb").read()
    return out, git(d, "status", "--porcelain", "--", "a.py", "t.py", "notes.txt")


CMD = [sys.executable, "-B", "t.py"]


def go(d, cmd=None, **k):
    return H.need(RG).redgreen(d, cmd or CMD, **k)


H.check("red on the parent, green on the fix", lambda: (
    lambda r: r["answer"] == "RED_THEN_GREEN" and r["parent"]["verdict"] == "red" and r["work"]["verdict"] == "green")(go(repo())))
H.check("the failing lines are printed, not the whole output", lambda: any("FAIL f gives 1" in x for x in go(repo())["parent"]["lines"]))
H.check("each leg names the tree it read", lambda: (lambda d, r: git(d, "rev-parse", "HEAD").strip()[:10] in r["parent"]["tree"]
        and "work" in r["work"]["tree"].lower())(*(lambda d: (d, go(d)))(repo())))
H.check("a test that is green on the parent did not see the fault", lambda: go(
    repo(old="def f():\n    return 2\n"))["answer"] == "GREEN_ON_PARENT")
H.check("a fix that does not work reads red on work", lambda: go(repo(new="def f():\n    return 3\n"))["answer"] == "RED_ON_WORK")
H.check("a new test is laid over the parent", lambda: go(repo(test_at_parent=False), overlay=["t.py"])["answer"] == "RED_THEN_GREEN")
H.check("missing: a test that the parent lacks, not laid over, is could not look, never red", lambda: (
    lambda r: r["parent"]["verdict"] == "could_not_look" and r["answer"] == "COULD_NOT_LOOK")(go(repo(test_at_parent=False))))
H.check("a crash (an import that fails) is could not look, never red", lambda: go(
    repo(test="import sys\nimport no_such_module_zz\n".replace("import no", "try:\n    import no") + "except ImportError:\n    sys.exit(3)\n"))
    ["answer"] == "COULD_NOT_LOOK")


def hung():
    d = repo(test="import time\ntime.sleep(30)\n")
    r = go(d, deadline_s=2)
    return r["answer"] == "COULD_NOT_LOOK" and "hung" in r["why"].lower()


H.check("hung: a test past the deadline is could not look, and the why says hung", hung)


def fault_red():
    d = repo()
    r = go(d, faults=[patch(d, 2, 9)])
    return r["answer"] == "RED_THEN_GREEN" and r["faults"][0]["verdict"] == "red"


H.check("a planted fault that the test catches", fault_red)


def equivalent():
    d = repo()
    r = go(d, faults=[patch(d, 2, "1 + 1")])
    return r["answer"] == "GREEN_ON_FAULT" and r["faults"][0]["verdict"] == "green"


H.check("an equivalent fault stays green and proves nothing", equivalent)


def noapply():
    d = repo()
    r = go(d, faults=[patch(d, 77, 78)])
    return r["faults"][0]["verdict"] == "could_not_look" and r["answer"] == "COULD_NOT_LOOK"


H.check("stale: a fault that does not apply is could not look", noapply)


def same():
    d = repo()
    a = snap(d)
    go(d, faults=[patch(d, 2, 9), patch(d, 77, 78)])
    return snap(d) == a


H.check("the tree, the index and my own uncommitted edit are the same after the call", same)


def build():
    d = repo()
    with open(os.path.join(d, "m.dll"), "wb") as f:
        f.write(b"built bytes")
    r = go(d, reads_build=["m.dll", "gone.dll"])
    h = hashlib.sha256(b"built bytes").hexdigest()
    return r["work"]["build"] == {"m.dll": h, "gone.dll": "absent"} and r["answer"] == "COULD_NOT_LOOK"


H.check("it prints which build each leg read; an absent build is could not look", build)
H.check("the page names its promises and the selftest runs at ./publish", lambda: H.page(
    "design/specs/2026-11-23-one-test-call/boundary.md", "the-tree-is-as-it-was", "could-not-look-is-never-red",
    "each-leg-names-its-build") and H.listed("src/RimMandrake/Utils/selftest_redgreen.py"))
H.done(15)
