#!/usr/bin/env python3
"""selftest for code_review_since.py: a fixture git repo with the tool copied in.

Cases: a mark on post-fix bytes passes; a mark only on pre-fix bytes fails (the
false PASS this tool exists to refuse); a file untouched since before the fix
passes on its unchanged bytes; a later edit does not undo a pass; an --after
outside HEAD's history is a usage error (2).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "code_review_since.py")
FAILS = []


def check(cond, what):
    print(("ok    " if cond else "FAIL  ") + what)
    if not cond:
        FAILS.append(what)


def main():
    root = tempfile.mkdtemp(prefix="crsince_")
    try:
        def g(*a):
            return subprocess.run(["git", "-C", root] + list(a), check=True,
                                  capture_output=True, text=True).stdout.strip()

        def write(rel, text):
            p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(text)

        def commit(msg):
            g("add", "-A")
            g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)
            return g("rev-parse", "HEAD")

        def mark(rel, text):
            with open(os.path.join(root, "infrastructure/state/code_review/T.jsonl"), "a") as f:
                f.write(json.dumps({"path": rel, "verdict": "clean", "ts": "t",
                                    "sha256": hashlib.sha256(text.encode()).hexdigest()}) + "\n")

        def run(*args):
            return subprocess.run([sys.executable, os.path.join(root, "src/RimMandrake/Utils/code_review_since.py")]
                                  + list(args), capture_output=True, text=True, cwd=root)

        g("init", "-q", "-b", "main")
        os.makedirs(os.path.join(root, "src/RimMandrake/Utils"))
        shutil.copy(TOOL, os.path.join(root, "src/RimMandrake/Utils/code_review_since.py"))
        os.makedirs(os.path.join(root, "infrastructure/state/code_review"))
        write("infrastructure/state/code_review/T.jsonl", "")
        write("a.py", "a1\n")
        write("b.py", "b1\n")
        write("c.py", "c1\n")
        commit("base")
        mark("a.py", "a1\n")          # pre-fix review only
        mark("c.py", "c1\n")          # c never changes after
        write("a.py", "a2\n")
        write("b.py", "b2\n")
        fix = commit("the fix")
        mark("b.py", "b2\n")          # post-fix review
        write("b.py", "b3\n")         # a later item edits b: not this review's debt
        commit("later edit")

        r = run("--after", fix, "b.py")
        check(r.returncode == 0 and "PASS" in r.stdout, "mark on post-fix bytes passes despite a later edit")
        r = run("--after", fix, "a.py")
        check(r.returncode == 1 and "FAIL" in r.stdout, "mark only on pre-fix bytes fails")
        r = run("--after", fix, "c.py")
        check(r.returncode == 0, "untouched file passes on its unchanged reviewed bytes")
        r = run("--after", fix, "a.py", "b.py")
        check(r.returncode == 1, "one failing path fails the run")
        r = run("--after", fix, os.path.join(root, "b.py"))
        check(r.returncode == 0, "an absolute path finds the repo-relative mark")
        # a merge that leaves c.py unchanged is still a candidate commit
        g("checkout", "-q", "-b", "x", fix)
        write("e.py", "e\n")
        xa = commit("x branch")
        g("checkout", "-q", "main")
        write("f.py", "f\n")
        ma = commit("main branch")
        g("-c", "user.name=t", "-c", "user.email=t@t", "merge", "-q", "--no-edit", "-m", "merge", "x")
        r = run("--after", xa, "--after", ma, "c.py")
        check(r.returncode == 0, "a merge leaving the file unchanged still proves its reviewed bytes")
        shutil.move(os.path.join(root, "infrastructure/state/code_review"), os.path.join(root, "cr_away"))
        r = run("--after", fix, "b.py")
        check(r.returncode == 1 and "Traceback" not in r.stderr, "no ledger dir reads as no marks, no crash")
        shutil.move(os.path.join(root, "cr_away"), os.path.join(root, "infrastructure/state/code_review"))
        # "<query> missing" must not read as a hit: a path whose name ends " blob"
        write("g.py blob", "g\n")
        commit("odd name")
        r = run("--after", "HEAD", "g.py blob")
        check(r.returncode == 1, "an unmarked path whose name ends ' blob' fails")
        r = run("--after", "HEAD", "nosuch.py blob")
        check(r.returncode == 1, "a missing path is no blob, so FAIL")
        r = run("--after", "HEAD", "a\nb.py")
        check(r.returncode == 2, "a path with a newline is refused")
        with open(os.path.join(root, "infrastructure/state/code_review/T.jsonl"), "a") as f:
            f.write(json.dumps({"path": "g.py blob", "verdict": "clean", "reviewer": "alice",
                                "sha256": hashlib.sha256(b"g\n").hexdigest()}) + "\n")
        r = run("--after", "HEAD", "g.py blob")
        check(r.returncode == 0 and "Traceback" not in r.stderr, "a string reviewer field does not crash a pass")
        commit("marks")
        with open(os.path.join(root, "infrastructure/state/code_review/T.jsonl"), "a") as f:
            f.write('null\n[]\n{"verdict": "clean", "path": ["b.py"], "sha256": "x"}\n')
        r = run("--after", fix, "b.py")
        check(r.returncode == 0 and "Traceback" not in r.stderr, "odd-shaped JSON records are skipped, no crash")
        # a replacement ref must not swap in reviewed bytes for b.py's unreviewed b3
        ba = g("rev-parse", "HEAD:b.py")
        bold = g("rev-parse", fix + ":b.py")
        g("replace", ba, bold)
        r = run("--after", "HEAD", "b.py")
        check(r.returncode == 1, "a git replace ref cannot fake the reviewed bytes")
        g("replace", "-d", ba)
        commit("junk records")
        g("checkout", "-q", "-b", "side", fix + "~1")
        write("d.py", "x\n")
        side = commit("side")
        g("checkout", "-q", "main")
        r = run("--after", side, "b.py")
        check(r.returncode == 2, "--after outside HEAD's history is a usage error")
        r = run("--after", "nosuchref", "b.py")
        check(r.returncode == 2, "an unknown --after is a usage error")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("RESULT: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
