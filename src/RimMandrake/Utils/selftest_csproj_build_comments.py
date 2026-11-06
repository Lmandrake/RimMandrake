#!/usr/bin/env python3
"""CSPROJ_BUILD_COMMENT_NAMES_READONLY_MIRROR: no csproj comment may tell a reader to dotnet-build or -run a project
at a D:\\Luke\\dev\\RimMandrake path (the read-only origin/main mirror: a build there writes obj\\ and Assemblies\\ into
it), and every winbuild.py / selftest_*.py command a csproj comment names must point at a file that exists.
A warning that merely NAMES the mirror ("never build in D:\\Luke\\dev\\RimMandrake") is fine."""
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

# a dotnet build/run (any spelling of the exe) followed by a path into the mirror
MIRROR_BUILD = re.compile(r"dotnet(?:\.exe)?\"?\s+(?:build|run\b[^\n]*?project)\s+D:\\Luke\\dev\\RimMandrake\\",
                          re.I)
WINBUILD = re.compile(r"python3\s+src/RimMandrake/Utils/winbuild\.py\s+(\S+)")
SELFTEST = re.compile(r"python3\s+(src/RimMandrake/Utils/selftest_\w+\.py)")


def problems(path, text, exists=os.path.exists):
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if MIRROR_BUILD.search(line):
            out.append("%s:%d builds in the read-only mirror" % (path, n))
        for m in WINBUILD.finditer(line):
            t = m.group(1)
            if t.endswith(".csproj") and not exists(os.path.join(ROOT, t)):
                out.append("%s:%d winbuild target missing: %s" % (path, n, t))
        for m in SELFTEST.finditer(line):
            if not exists(os.path.join(ROOT, m.group(1))):
                out.append("%s:%d selftest missing: %s" % (path, n, m.group(1)))
    return out


def main():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    # the instrument can see: each shape it must catch, and the warning it must leave alone
    bad = [r'"%USERPROFILE%\.dotnet\dotnet.exe" build D:\Luke\dev\RimMandrake\src\X\Source\X.csproj -c Release',
           r"/mnt/c/Users/Mandrake/.dotnet/dotnet.exe build D:\Luke\dev\RimMandrake\src\X\X.csproj",
           r'"%USERPROFILE%\.dotnet\dotnet.exe" run [dash][dash]project D:\Luke\dev\RimMandrake\src\X\T.csproj']
    for i, b in enumerate(bad):
        check("catches shape %d" % i, len(problems("t", b)) == 1)
    check("warning text allowed",
          not problems("t", r"Never build in D:\Luke\dev\RimMandrake: that mirror is read-only"))
    check("missing winbuild target caught",
          problems("t", "python3 src/RimMandrake/Utils/winbuild.py src/Nope/Nope.csproj", lambda p: False))
    check("missing selftest caught",
          problems("t", "python3 src/RimMandrake/Utils/selftest_nope.py", lambda p: False))

    files = [p for p in glob.glob(os.path.join(ROOT, "src", "**", "*.csproj"), recursive=True)
             if "/bin/" not in p and "/obj/" not in p]
    check("found the csproj files (%d)" % len(files), len(files) >= 50)
    found, named = [], 0
    for p in files:
        text = open(p, encoding="utf-8-sig", errors="replace").read()
        named += len(WINBUILD.findall(text))
        found += problems(os.path.relpath(p, ROOT), text)
    check("csproj comments name winbuild (%d)" % named, named >= 50)
    for f in found:
        print("FAIL " + f)
    if found:
        fails.append("%d csproj comment problems" % len(found))
    for f in fails:
        print("FAIL " + f)
    print("selftest_csproj_build_comments: %s (%d csproj, %d winbuild lines)"
          % ("FAIL" if fails else "PASS", len(files), named))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
