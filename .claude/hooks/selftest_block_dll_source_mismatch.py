#!/usr/bin/env python3
"""Selftest for block_dll_source_mismatch.py — run after ANY change to it or
to src/RimMandrake/Utils/dll_source_stamp.py.

Builds a throwaway git repo (a bare "remote" + a working clone) with one fake
mod project ("TestMod") shaped exactly like a real one — a csproj, one .cs
file, a committed "DLL" (just bytes; no real MSBuild involved) and a matching
.srchash sidecar — then feeds the hook real `git push` commands against it and
checks the verdict, same shape as selftest_block_shared_tree_merge.py.

    python3 .claude/hooks/selftest_block_dll_source_mismatch.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "block_dll_source_mismatch.py")
REPO = os.path.dirname(os.path.dirname(HERE))  # .claude/hooks -> .claude -> repo root
REAL_CHECKER = os.path.join(REPO, "src", "RimMandrake", "Utils", "dll_source_stamp.py")

DENY, ALLOW = "deny", "allow"

CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net472</TargetFramework>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <OutputPath>..\\Assemblies\\</OutputPath>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="Foo.cs" />
  </ItemGroup>
</Project>
"""

FOO_V1 = "// TestMod Foo.cs v1\n"
FOO_V2 = "// TestMod Foo.cs v2 -- edited, NOT rebuilt\n"


def verdict(cmd, cwd):
    out = subprocess.run([sys.executable, HOOK], capture_output=True, text=True,
                         input=json.dumps({"tool_input": {"command": cmd},
                                           "cwd": cwd})).stdout
    return DENY if '"deny"' in out else ALLOW


def stamp_for(foo_text):
    h = hashlib.sha256(foo_text.encode("utf-8")).hexdigest()
    return "# project: TestMod/Source/TestMod.csproj\n%s Foo.cs\n" % h


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        f.write(text)


def write_bytes(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def paths(work):
    src = os.path.join(work, "src", "TestMod", "Source")
    asm = os.path.join(work, "src", "TestMod", "Assemblies")
    return {
        "csproj": os.path.join(src, "TestMod.csproj"),
        "foo": os.path.join(src, "Foo.cs"),
        "dll": os.path.join(asm, "TestMod.dll"),
        "stamp": os.path.join(asm, "TestMod.dll.srchash"),
    }


def main():
    tmp = tempfile.mkdtemp()
    remote = os.path.join(tmp, "remote.git")
    work = os.path.join(tmp, "work")

    subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", work], check=True)

    def g(*a):
        return subprocess.run(["git", *a], cwd=work, check=True, capture_output=True)

    g("-c", "user.name=t", "-c", "user.email=t@t", "config", "user.name", "t")
    g("config", "user.email", "t@t")
    g("remote", "add", "origin", remote)

    # The hook shells out to a real dll_source_stamp.py at
    # <repo-root>/src/RimMandrake/Utils/dll_source_stamp.py — put the real,
    # current one there (not committed; the hook reads it straight off disk).
    checker_dst = os.path.join(work, "src", "RimMandrake", "Utils", "dll_source_stamp.py")
    os.makedirs(os.path.dirname(checker_dst), exist_ok=True)
    shutil.copyfile(REAL_CHECKER, checker_dst)

    p = paths(work)
    write(p["csproj"], CSPROJ)
    write(p["foo"], FOO_V1)
    write_bytes(p["dll"], b"FAKE-DLL-BYTES-V1")
    write(p["stamp"], stamp_for(FOO_V1))
    g("add", "src")
    g("commit", "-q", "-m", "base: matching TestMod stamp")
    g("push", "-q", "-u", "origin", "main")

    results = []

    def check(name, want, cmd="git push"):
        got = verdict(cmd, work)
        results.append((name, want, got, cmd))

    # 1. Matching stamp, an unrelated change riding along -> allow.
    write(os.path.join(work, "README.md"), "unrelated\n")
    g("add", "README.md")
    g("commit", "-q", "-m", "unrelated change, stamp still matches")
    check("matching stamp -> allow", ALLOW)
    g("push", "-q")  # advance origin/main for real, keep it as the new base

    # 2. Source edited, DLL/stamp NOT rebuilt -> deny.
    write(p["foo"], FOO_V2)
    g("add", "src")
    g("commit", "-q", "-m", "edit without rebuild")
    check("source edited without rebuild -> deny", DENY)
    g("reset", "-q", "--hard", "origin/main")  # discard the bad commit locally

    # 3. DLL bytes changed, .srchash NOT touched -> deny.
    write_bytes(p["dll"], b"FAKE-DLL-BYTES-V2-NO-STAMP-UPDATE")
    g("add", "src")
    g("commit", "-q", "-m", "dll changed, stamp not regenerated")
    check("DLL changed without stamp -> deny", DENY)
    g("reset", "-q", "--hard", "origin/main")

    # 4. A mismatch already on origin/main (pre-existing) must not block a
    #    LATER, unrelated push that does not touch it.
    write(p["foo"], FOO_V2)  # same edit as case 2, but this time really pushed
    g("add", "src")
    g("commit", "-q", "-m", "pre-existing mismatch, landed directly (bypassing the hook, as test setup)")
    g("push", "-q")
    write(os.path.join(work, "README2.md"), "also unrelated\n")
    g("add", "README2.md")
    g("commit", "-q", "-m", "unrelated on top of the pre-existing mismatch")
    check("pre-existing mismatch outside the range -> allow", ALLOW)
    g("push", "-q")

    # 5. A non-push git command is never touched by this hook.
    check("non-push command -> allow", ALLOW, cmd="git status")
    check("non-push, non-git command -> allow", ALLOW, cmd="echo hi")

    bad = 0
    for name, want, got, cmd in results:
        ok = want == got
        if not ok:
            bad += 1
        print("%s  want=%-5s got=%-5s  %-55s (%s)" %
              ("PASS" if ok else "FAIL", want, got, name, cmd))
    print("%d/%d passed" % (len(results) - bad, len(results)))

    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
