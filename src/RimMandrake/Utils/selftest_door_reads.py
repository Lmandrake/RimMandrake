#!/usr/bin/env python3
"""Selftest of the door's read records (door_reads.py, door_reads_hook/, publish.py narrow_by_reads).
Page: design/specs/2026-11-26-door-reads/boundary.md. One test per promise, named as the promise.

    python3 selftest_door_reads.py        exit 0 all green, 1 a red
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import door_reads as DR  # noqa: E402
import publish as P  # noqa: E402
import time_budget  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


def g(*a, cwd):
    return subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def repo(tmp):
    r = os.path.join(tmp, "repo")
    os.makedirs(r)
    g("init", "-q", "-b", "main", cwd=r)
    for k, v in (("user.name", "t"), ("user.email", "t@example.invalid"), ("core.hooksPath", "/dev/null")):
        g("config", k, v, cwd=r)
    return r


def commit(r, msg):
    g("add", "-A", cwd=r)
    g("commit", "-q", "-m", msg, cwd=r)
    return g("rev-parse", "HEAD", cwd=r)


def hooked(r, script, rec, extra_env=None):
    """Run python `script` (a path in r) under the hook, cwd r. -> CompletedProcess."""
    env = DR.hook_env(dict(os.environ, **(extra_env or {})), r, rec)
    return subprocess.run([sys.executable, script], cwd=r, env=env, capture_output=True, text=True,
                          timeout=time_budget.CALL_S)


PROBE = r'''
import glob, os, subprocess, sys
sys.path.insert(0, "lib")
open("data/a.txt").read()
import mod_b
os.listdir("listed")
glob.glob("globbed/*.md")
subprocess.run([sys.executable, "-c", "open('data/child.txt').read()"], check=True)
subprocess.run(["git", "show", "HEAD:data/shown.txt"], capture_output=True)
subprocess.run(["git", "-C", sys.argv[1], "status"], capture_output=True)       # outside the tree: reads nothing of it
subprocess.run(["true"])
open("data/missing.txt") if os.path.exists("data/missing.txt") else None
'''


def t_records_what_a_test_reads(tmp):
    r = repo(tmp)
    for rel in ("data/a.txt", "data/child.txt", "data/shown.txt", "listed/x", "globbed/y.md"):
        write(r, rel, "x\n")
    write(r, "lib/mod_b.py", "B = 1\n")
    write(r, "probe.py", PROBE)
    commit(r, "base")
    outside = os.path.join(tmp, "outside")
    os.makedirs(outside)
    g("init", "-q", cwd=outside)
    rec = os.path.join(tmp, "rec")
    p = subprocess.run([sys.executable, "probe.py", outside], cwd=r, env=DR.hook_env(dict(os.environ), r, rec),
                       capture_output=True, text=True, timeout=time_budget.CALL_S)
    got = DR.parse(rec)
    want = {"probe.py", "data/a.txt", "lib/mod_b.py", "data/child.txt", "data/shown.txt"}
    check(p.returncode == 0 and want <= got["files"],
          "records-what-a-test-reads: files opened, imported, read by a hooked child and by git show (%s; %s)"
          % (sorted(want - got["files"]), p.stderr.strip()[-200:]))
    check({"listed", "globbed"} <= got["dirs"], "records-what-a-test-reads: folders listed (%s)" % sorted(got["dirs"]))
    check(not got["unknown"], "records-what-a-test-reads: a git child outside the tree and `true` hide nothing (%s)"
          % got["unknown"])
    # a git child started in a subfolder reads its `-- paths` relative to that subfolder; a `rev:path` stays rooted
    sub = os.path.join(tmp, "subrec")
    with open(sub, "w", encoding="utf-8") as f:
        f.write("C %s\n" % json.dumps({"cwd": "lib", "argv": ["git", "log", "--", "mod_b.py"]}))
        f.write("C %s\n" % json.dumps({"cwd": "lib", "argv": ["git", "show", "HEAD:data/shown.txt"]}))
    sg = DR.parse(sub)
    check({"lib/mod_b.py", "data/shown.txt"} <= sg["files"] and "mod_b.py" not in sg["files"],
          "records-what-a-test-reads: a git child in a subfolder reads its `-- paths` under it (%s)" % sorted(sg["files"]))
    top = os.path.join(tmp, "toprec")
    with open(top, "w", encoding="utf-8") as f:
        f.write("C %s\n" % json.dumps({"cwd": ".", "argv": ["git", "log", "--", "."]}))
    check(DR.parse(top)["unknown"], "a-read-the-hook-cannot-see-is-unknown: git log -- . names the whole tree (%s)"
          % DR.parse(top))
    check(DR.hook_env({}, r, rec)["PYTHONPATH"].split(os.pathsep)[0] == DR.HOOK_DIR,
          "records-what-a-test-reads: the hook is first on PYTHONPATH")
    q = subprocess.run([sys.executable, "-c", "open('data/a.txt').read()"], cwd=r, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONPATH=DR.HOOK_DIR), timeout=time_budget.CALL_S)
    check(q.returncode == 0 and q.stderr == "", "records-what-a-test-reads: without RM_DOOR_READS the hook does nothing")
    # threads: the hook's re-entry guard was one flag for the process, so a read in one thread while another thread was
    # inside the hook went unrecorded (measured 2026-11-26: 8 threads, 361 of 400 reads lost; 1 thread, 0)
    for i in range(200):
        write(r, "many/f%d.txt" % i, "x\n")
    write(r, "threads.py", "import concurrent.futures\n"
          "def rd(i):\n    with open('many/f%d.txt' % i) as f:\n        f.read()\n"
          "with concurrent.futures.ThreadPoolExecutor(8) as ex:\n    list(ex.map(rd, range(200)))\n")
    trec = os.path.join(tmp, "trec")
    p = hooked(r, "threads.py", trec)
    lost = [i for i in range(200) if "many/f%d.txt" % i not in DR.parse(trec)["files"]]
    check(p.returncode == 0 and not lost, "records-what-a-test-reads: reads in 8 threads at once are each recorded "
          "(%d of 200 lost; %s)" % (len(lost), p.stderr.strip()[-200:]))


def t_a_read_the_hook_cannot_see_is_unknown(tmp):
    r = repo(tmp)
    write(r, "a.txt", "x\n")
    cases = {
        "a Python child without the hook": "import subprocess, sys\nsubprocess.run([sys.executable, '-c', '1'], env={'PATH': '/usr/bin'})\n",
        "a Python child that skips it (-I)": "import subprocess, sys\nsubprocess.run([sys.executable, '-I', '-c', '1'])\n",
        "git ls-files in the tree": "import subprocess\nsubprocess.run(['git', 'ls-files'], capture_output=True)\n",
        "a shell child in the tree": "import subprocess\nsubprocess.run('cat a.txt', shell=True, capture_output=True)\n",
        "a clone of the tree": "import subprocess, sys, tempfile\nsubprocess.run(['git', 'clone', '-q', '.', tempfile.mkdtemp()])\n",
        # git verbs that take their paths on stdin: the argv names none of what they read
        "git cat-file --batch in the tree": "import subprocess\nsubprocess.run(['git', 'cat-file', '--batch'], "
                                            "input='HEAD:a.txt\\n', capture_output=True, text=True)\n",
        "git hash-object --stdin-paths in the tree": "import subprocess\nsubprocess.run(['git', 'hash-object', "
                                                     "'--stdin-paths'], input='a.txt\\n', capture_output=True, text=True)\n",
        # an empty pathspec after `--` is the whole tree, as no `--` is
        "git log -- with no path in the tree": "import subprocess\nsubprocess.run(['git', 'log', '--oneline', '--'], "
                                               "capture_output=True)\n",
    }
    for i, (name, src) in enumerate(cases.items()):
        write(r, "c%d.py" % i, src)
    commit(r, "base")
    blobs = DR.tree_blobs(lambda *a: subprocess.run(["git", "-C", r, *a], capture_output=True, text=True), "HEAD")
    store = os.path.join(tmp, "store")
    for i, name in enumerate(cases):
        rec = os.path.join(tmp, "rec%d" % i)
        hooked(r, "c%d.py" % i, rec)
        DR.keep(store, "c%d.py" % i, rec, blobs)
        ans, why = DR.relation(store, "c%d.py" % i, {"other.py"}, blobs)
        check(ans == "unknown", "a-read-the-hook-cannot-see-is-unknown: %s -> %s (%s)" % (name, ans, why))


def t_an_untouched_test_is_left_out(tmp):
    r = repo(tmp)
    write(r, "t.py", "open('lib.py').read()\nimport os\nos.listdir('d')\n")
    write(r, "lib.py", "x = 1\n")
    write(r, "other.py", "y = 1\n")
    write(r, "d/one.txt", "1\n")
    commit(r, "base")
    blobs = DR.tree_blobs(lambda *a: subprocess.run(["git", "-C", r, *a], capture_output=True, text=True), "HEAD")
    store, rec = os.path.join(tmp, "store"), os.path.join(tmp, "rec")
    hooked(r, "t.py", rec)
    DR.keep(store, "t.py", rec, blobs)
    for changed, want in (({"other.py"}, "not touched"), ({"lib.py"}, "touched"), ({"t.py"}, "touched"),
                          ({"d/two.txt"}, "touched"), ({"e/two.txt"}, "not touched")):
        ans, why = DR.relation(store, "t.py", changed, blobs)
        check(ans == want, "an-untouched-test-is-left-out: a change to %s -> %s (%s)" % (sorted(changed)[0], ans, why))
    # a new subfolder of a listed folder is a new entry in that folder's listing: a glob of specs/*/page.md, or a walk,
    # sees the file in it (2026-11-27: the records of selftest_boundary_check.py and selftest_codex_lane.py list
    # design/specs, and a new design/specs/<date>-x/boundary.md read "not touched")
    write(r, "g.py", "import glob\nfor p in glob.glob('specs/*/page.md'):\n    open(p).read()\n")
    write(r, "specs/old/page.md", "1\n")
    commit(r, "glob")
    blobs = DR.tree_blobs(lambda *a: subprocess.run(["git", "-C", r, *a], capture_output=True, text=True), "HEAD")
    grec = os.path.join(tmp, "grec")
    hooked(r, "g.py", grec)
    DR.keep(store, "g.py", grec, blobs)
    for changed, want in (({"specs/new/page.md"}, "touched"), ({"specs/old/page.md"}, "touched"),
                          ({"specs/old/deeper/z.md"}, "not touched"), ({"other.py"}, "not touched")):
        ans, why = DR.relation(store, "g.py", changed, blobs)
        check(ans == want, "an-untouched-test-is-left-out: a test that globbed specs/*/page.md, a change to %s -> %s (%s)"
              % (sorted(changed)[0], ans, why))


def t_a_record_of_other_code_decides_nothing(tmp):
    r = repo(tmp)
    write(r, "t.py", "import sys\nsys.path.insert(0, '.')\nimport lib\nopen('data.json').read()\n")
    write(r, "lib.py", "x = 1\n")
    write(r, "data.json", "{}\n")
    commit(r, "base")
    blobs = DR.tree_blobs(lambda *a: subprocess.run(["git", "-C", r, *a], capture_output=True, text=True), "HEAD")
    store, rec = os.path.join(tmp, "store"), os.path.join(tmp, "rec")
    hooked(r, "t.py", rec)
    DR.keep(store, "t.py", rec, blobs)
    write(r, "data.json", '{"a": 1}\n')
    commit(r, "data moves")
    b2 = DR.tree_blobs(lambda *a: subprocess.run(["git", "-C", r, *a], capture_output=True, text=True), "HEAD")
    ans, why = DR.relation(store, "t.py", {"other.py"}, b2)
    check(ans == "not touched", "a-record-of-other-code-decides-nothing: data it read moved on main, the code did not: "
                                "the record still decides (%s, %s)" % (ans, why))
    write(r, "lib.py", "x = 2\n")
    commit(r, "code moves")
    b3 = DR.tree_blobs(lambda *a: subprocess.run(["git", "-C", r, *a], capture_output=True, text=True), "HEAD")
    ans, why = DR.relation(store, "t.py", {"other.py"}, b3)
    check(ans == "unknown" and "lib.py" in why,
          "a-record-of-other-code-decides-nothing: a .py file it ran moved on main: unknown (%s, %s)" % (ans, why))
    check(DR.relation(os.path.join(tmp, "none"), "t.py", {"x"}, b3)[0] == "unknown",
          "a-record-of-other-code-decides-nothing: no record is unknown")
    os.makedirs(os.path.join(tmp, "bad"))
    with open(DR._path(os.path.join(tmp, "bad"), "t.py"), "w") as f:
        f.write("{torn")
    check(DR.relation(os.path.join(tmp, "bad"), "t.py", {"x"}, b3)[0] == "unknown",
          "a-record-of-other-code-decides-nothing: a torn record is unknown")


HUB = "def use_a():\n    import leaf_a\n    return leaf_a.A\n\n\ndef use_b():\n    import leaf_b\n    return leaf_b.B\n"
TEST = r'''import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hub
with open(os.environ["DOOR_PROBE_LOG"], "a") as f:
    f.write("%s\n" % os.path.basename(__file__))
assert hub.use_{x}() == 1
print("ok")
'''


def t_the_door_runs_only_the_tests_a_change_touches(tmp):
    """Two pipeline tests share a hub that imports each leaf lazily: the import closure ties both tests to both leaves.
    The first door run has no records and runs both; after it, a change to leaf_b runs only the test that loads it, and
    a change to the hub runs both."""
    r = repo(tmp)
    write(r, "pipe/hub.py", HUB)
    write(r, "pipe/leaf_a.py", "A = 1\n")
    write(r, "pipe/leaf_b.py", "B = 1\n")
    write(r, "pipe/t_a.py", TEST.replace("{x}", "a"))
    write(r, "pipe/t_b.py", TEST.replace("{x}", "b"))
    cfg = {"timeout_s": 120, "pipeline_files": ["pipe/*.py"], "tests": [{"test": "pipe/t_a.py"}, {"test": "pipe/t_b.py"}]}
    commit(r, "base")
    log = os.path.join(tmp, "ran.log")
    os.environ["DOOR_PROBE_LOG"] = log
    old_root, P.RM_ROOT = P.RM_ROOT, os.path.join(tmp, "rmroot")

    def door(changed):
        if os.path.exists(log):
            os.unlink(log)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            P._run_pipeline_checks(r, changed, cfg, base=(g("rev-parse", "HEAD", cwd=r), None))
        ran = sorted(open(log).read().split()) if os.path.exists(log) else []
        return ran, buf.getvalue()
    try:
        static = sorted(c["test"] for c in P.pipeline_selection(r, ["pipe/leaf_b.py"], cfg))
        check(static == ["pipe/t_a.py", "pipe/t_b.py"], "the-door-runs-only-the-tests-a-change-touches: sanity: the import "
                                              "closure names both tests for leaf_b (%s)" % static)
        ran, out = door(["pipe/leaf_b.py"])
        check(ran == ["t_a.py", "t_b.py"], "the-door-runs-only-the-tests-a-change-touches: with no record, both run "
                                           "(%s)" % ran)
        ran, out = door(["pipe/leaf_b.py"])
        check(ran == ["t_b.py"] and "1 left out" in out,
              "the-door-runs-only-the-tests-a-change-touches: a leaf_b change runs t_b only (%s; %r)"
              % (ran, out.strip()[-200:]))
        ran, out = door(["pipe/hub.py"])
        check(ran == ["t_a.py", "t_b.py"], "the-door-runs-only-the-tests-a-change-touches: a hub change runs both (%s)"
              % ran)
        write(r, "pipe/leaf_a.py", "A = 1\nimport leaf_b\n")     # leaf_a now loads leaf_b: its old record is of other code
        commit(r, "leaf_a imports leaf_b")
        ran, out = door(["pipe/leaf_b.py"])
        check(ran == ["t_a.py", "t_b.py"], "the-door-runs-only-the-tests-a-change-touches: after leaf_a changed on "
                                           "main, t_a's old record decides nothing and t_a runs (%s)" % ran)
        ran, out = door(["pipe/leaf_b.py"])
        check(ran == ["t_a.py", "t_b.py"], "the-door-runs-only-the-tests-a-change-touches: t_a's new record reads "
                                           "leaf_b, so it runs for a leaf_b change (%s)" % ran)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sel = P.narrow_by_reads(r, [{"test": "pipe/t_a.py"}], ["pipe/leaf_b.py"], (None, "no origin/main here"), cfg)
        check(sel == [{"test": "pipe/t_a.py"}] and "not used" in buf.getvalue(),
              "the-door-runs-only-the-tests-a-change-touches: no base to read: every named test runs, said aloud")
    finally:
        P.RM_ROOT = old_root
        os.environ.pop("DOOR_PROBE_LOG", None)


def main():
    for t in (t_records_what_a_test_reads, t_a_read_the_hook_cannot_see_is_unknown, t_an_untouched_test_is_left_out,
              t_a_record_of_other_code_decides_nothing, t_the_door_runs_only_the_tests_a_change_touches):
        tmp = tempfile.mkdtemp(prefix="doorreads-")
        try:
            t(tmp)
        except Exception as e:                       # a crash of one test is a red of that promise, named
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %r" % (t.__name__[2:].replace("_", "-"), e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d red" % ("RED" if FAILS else "GREEN", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
