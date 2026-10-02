#!/usr/bin/env python3
"""Selftest for infrastructure/githooks/pre-push: builds a temp repo + bare remote,
proves a DLL/source mismatch push is REFUSED and a clean push PASSES."""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")


def git(cwd, *a, check=True):
    r = subprocess.run(["git", "-C", cwd] + list(a), capture_output=True, text=True, env=ENV)
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (a, r.stderr))
    return r


def sha(b):
    return hashlib.sha256(b).hexdigest()


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)


def main():
    tmp = tempfile.mkdtemp(prefix="prepush_selftest_")
    fails = 0
    try:
        work, bare = os.path.join(tmp, "work"), os.path.join(tmp, "bare.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True, env=ENV)
        os.makedirs(work)
        git(work, "init", "-q", "-b", "main")
        git(work, "remote", "add", "origin", bare)
        for rel in ("src/RimMandrake/Utils/dll_source_stamp.py", "src/RimMandrake/Utils/ledger_lint.py",
                    ".claude/hooks/block_dll_source_mismatch.py", ".claude/hooks/block_ledger_lint.py",
                    "infrastructure/githooks/pre-push"):
            if os.path.isfile(os.path.join(REPO, rel)):
                write(work, rel, open(os.path.join(REPO, rel), "rb").read())
        os.chmod(os.path.join(work, "infrastructure/githooks/pre-push"), 0o755)
        git(work, "config", "core.hooksPath", "infrastructure/githooks")
        src, dll = b"class A {}\n", b"fake dll bytes"
        write(work, "src/Mod/Mod.csproj", b"<Project/>\n")
        write(work, "src/Mod/A.cs", src)
        write(work, "src/Mod/Assemblies/Mod.dll", dll)
        write(work, "src/Mod/Assemblies/Mod.dll.srchash",
              ("# project: Mod/Mod.csproj\n# dll: %s\n%s A.cs\n" % (sha(dll), sha(src))).encode())
        git(work, "add", "-A"); git(work, "commit", "-q", "-m", "base")
        r = git(work, "push", "-q", "origin", "main", check=False)
        print("clean base push rc=%d" % r.returncode)
        if r.returncode:
            fails += 1; print(r.stderr)
        # mismatch: source changes, DLL/stamp do not
        write(work, "src/Mod/A.cs", b"class A { int x; }\n")
        git(work, "add", "-A"); git(work, "commit", "-q", "-m", "src only")
        r = git(work, "push", "-q", "origin", "main", check=False)
        refused = r.returncode != 0 and "REFUSED" in r.stderr
        print("mismatch push refused=%s" % refused)
        fails += 0 if refused else 1
        # fix: restamp
        new = b"class A { int x; }\n"
        write(work, "src/Mod/Assemblies/Mod.dll.srchash",
              ("# project: Mod/Mod.csproj\n# dll: %s\n%s A.cs\n" % (sha(dll), sha(new))).encode())
        git(work, "add", "-A"); git(work, "commit", "-q", "-m", "restamp")
        r = git(work, "push", "-q", "origin", "main", check=False)
        print("restamped push rc=%d" % r.returncode)
        fails += 1 if r.returncode else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest_pre_push: %d/3 passed" % (3 - fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
