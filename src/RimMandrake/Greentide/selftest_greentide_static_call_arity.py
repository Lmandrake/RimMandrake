#!/usr/bin/env python3
"""selftest_greentide_static_call_arity.py -- every jawa/static_call in Greentide/validation.py passes as many
'|'-separated args as the C# method it names takes.

Why: JawaBench's StaticCall (JawaBenchCompanionProbeTools.cs) reads args="" as ZERO parameters, so a call with
args="" to `ProofApply(string unused)` is refused ("No public static ProofApply with 0 params.") and the row FAILs
for a harness reason on every run (giant_ants/raids_off_blocks_every_strategy, SteveDesktop 2026-11-25). Offline:
it reads the two source files and never runs the game. Planted break: an args="" call to a 1-param method -> red.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, ".."))
FAILS = []

CALL = re.compile(r'"jawa/static_call",\s*type="([\w.]+)",\s*method="(\w+)",\s*args=("(?:[^"\\]|\\.)*")', re.S)


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def calls(text):
    """(type, method, n_args) for each static_call; n_args from the literal format string."""
    out = []
    for m in CALL.finditer(text):
        lit = m.group(3)[1:-1]
        out.append((m.group(1), m.group(2), 0 if lit == "" else lit.count("|") + 1))
    return out


def arities(type_full, method):
    """Parameter counts of every `public static <ret> method(` in the C# file that declares the type's class."""
    cls = type_full.split(".")[-1]
    found = []
    for root, _dirs, files in os.walk(SRC):
        if os.sep + "Source" not in root:
            continue
        for f in files:
            if not f.endswith(".cs"):
                continue
            text = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
            if not re.search(r"\bclass\s+%s\b" % re.escape(cls), text):
                continue
            for pm in re.finditer(r"public\s+static\s+[\w<>\[\],. ]+?\s+%s\s*\(([^)]*)\)" % re.escape(method), text):
                params = pm.group(1).strip()
                found.append(0 if not params else params.count(",") + 1)
    return found


def mismatches(text):
    bad = []
    for ty, meth, n in calls(text):
        ar = arities(ty, meth)
        if not ar or n not in ar:
            bad.append((ty, meth, n, ar))
    return bad


def main():
    text = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    found = calls(text)
    check("instrument sees the static calls", len(found) >= 3, found)
    check("every static_call arity matches its C# method", mismatches(text) == [], mismatches(text))
    planted = ('"jawa/static_call", type="RimMandrake.Greentide.RM_GreentideAntRaidApplier",\n'
               '                          method="ProofApply", args="")')
    check("planted args=\"\" to a 1-param method goes red", len(mismatches(planted)) == 1, mismatches(planted))
    good = planted.replace('args="")', 'args="proof")')
    check("the same call with one arg stays green", mismatches(good) == [], mismatches(good))
    print("FAILED %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
