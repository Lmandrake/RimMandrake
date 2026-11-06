#!/usr/bin/env python3
"""Selftest for LOG_AUTOOPEN_FIX_WAITS_FOR_FIRST_HELLO - offline, source-level.

The owner's 2026-09-02 wish ("Autoopen of the error log ... False by default") must hold in plain
play, with no jawa/ bridge call. RimBridgeServer constructs JawaBenchTpsTools when it registers
companions at game load, so that constructor is the startup hook. This checks:
  1. the JawaBenchTpsTools() constructor calls JawaBenchLogAutoOpenSuppress.Install() itself
     (not only via the module initializer it happens to fire);
  2. the constructor stays public and parameterless (RimBridgeServer's TryCreateInstance needs it);
  3. Install() is idempotent (returns early on the _attempted gate, set under a lock), so the lazy
     call in JawaBenchInit.Announce is a harmless no-op;
  4. suppression defaults ON;
  5. the lazy backstop call in JawaBenchInit is still present.
Exit 0 = PASS, 1 = FAIL.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "JawaBench.BridgeTools")


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def ctor_body(src, cls):
    m = re.search(r"public\s+" + cls + r"\s*\(\s*\)\s*\{", src)
    if not m:
        return None
    i, depth = m.end(), 1
    while depth and i < len(src):
        depth += {"{": 1, "}": -1}.get(src[i], 0)
        i += 1
    return src[m.end():i - 1]


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def main():
    fails = []
    tps = strip_comments(read("JawaBenchTpsSampler.cs"))
    body = ctor_body(tps, "JawaBenchTpsTools")
    if body is None:
        fails.append("no public parameterless JawaBenchTpsTools() constructor (RimBridgeServer cannot construct it at load)")
    elif not re.search(r"JawaBenchLogAutoOpenSuppress\s*\.\s*Install\s*\(\s*\)", body):
        fails.append("JawaBenchTpsTools() does not call JawaBenchLogAutoOpenSuppress.Install(): suppressor waits for the first jawa/ call")

    sup = strip_comments(read("JawaBenchLogAutoOpenSuppress.cs"))
    inst = re.search(r"static\s+void\s+Install\s*\(\s*\)\s*\{(.*?)\n\s*try", sup, re.S)
    if not inst or not re.search(r"lock\s*\(\s*Gate\s*\)", inst.group(1)) \
            or not re.search(r"if\s*\(\s*_attempted\s*\)\s*return\s*;\s*_attempted\s*=\s*true\s*;", inst.group(1)):
        fails.append("Install() is not visibly idempotent (lock(Gate) + if (_attempted) return; _attempted = true;)")
    if not re.search(r"static\s+bool\s+Suppressed\s*=\s*true\s*;", sup):
        fails.append("Suppressed does not default to true")

    init = strip_comments(read("JawaBenchInit.cs"))
    if not re.search(r"JawaBenchLogAutoOpenSuppress\s*\.\s*Install\s*\(\s*\)", init):
        fails.append("lazy backstop JawaBenchLogAutoOpenSuppress.Install() missing from JawaBenchInit")

    for f in fails:
        print("FAIL:", f)
    if fails:
        print("FAIL %d/5 checks" % len(fails))
        return 1
    print("PASS: suppressor installs from the registration constructor; Install idempotent; default on; backstop kept")
    return 0


if __name__ == "__main__":
    sys.exit(main())
