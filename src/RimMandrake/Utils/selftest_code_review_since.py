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
                                  + list(args), capture_output=True, text=True)

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
