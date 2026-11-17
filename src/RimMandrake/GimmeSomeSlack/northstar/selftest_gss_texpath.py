#!/usr/bin/env python3
"""RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START: every texture the mod asks for by a path it builds goes through SafeTex
(Source/SafeTex.cs, Source/Core/TexPath.cs), which refuses a path no file system takes and names it. The guard's own rule is
checked in the C# selftest (TexPathChecks.cs); this reads the mod's source for a call that goes round it.

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_texpath.py      # exit 0 = every check passes
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Source")


def direct_calls(files):
    """(file, line) of each ContentFinder<Texture2D>.Get whose first argument is not a string literal."""
    out = []
    for name, text in files.items():
        if os.path.basename(name) == "SafeTex.cs":
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in re.finditer(r"ContentFinder<Texture2D>\.Get\(\s*(.)", line):
                if m.group(1) != '"':
                    out.append((name, i))
    return out


def main():
    fails = []

    def check(ok, msg):
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    files = {}
    for root, dirs, names in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ("SelfTest", "obj", "bin")]
        for n in names:
            if n.endswith(".cs"):
                files[os.path.join(root, n)] = open(os.path.join(root, n), encoding="utf-8").read()
    check(len(files) > 40, "the mod's source is read (%d files)" % len(files))
    got = direct_calls(files)
    for f, i in got[:6]:
        print("     %s:%d" % (os.path.relpath(f, SRC), i))
    check(not got, "no texture is asked for by a built path but through SafeTex (%d direct calls)" % len(got))
    check(sum(t.count("SafeTex.Get(") for t in files.values()) >= 10, "the guard is the door the mod's lookups use")
    check(direct_calls({"x.cs": 'var t = ContentFinder<Texture2D>.Get(path, false);'}) == [("x.cs", 1)], "planted: a direct call with a built path is found")
    check(direct_calls({"x.cs": 'var t = ContentFinder<Texture2D>.Get("UI/Commands/TryReconnect", false);'}) == [], "a literal path is not a built one")
    print("PASS" if not fails else "FAIL: %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
