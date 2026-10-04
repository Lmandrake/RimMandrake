#!/usr/bin/env python3
"""selftest_jawavoice.py -- identity_gate_problems() is clean on the shipped patches and names each break."""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
for p in (HERE, UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)
import validation as V  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def broken(old, new):
    tmp = tempfile.mkdtemp()
    shutil.copytree(os.path.join(HERE, "Patches"), os.path.join(tmp, "P"))
    p = os.path.join(tmp, "P", "JawaVoice_animals.xml")
    s = open(p, encoding="utf-8").read()
    assert old in s, old
    open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
    try:
        return V.identity_gate_problems(os.path.join(tmp, "P"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ops, bad = V.identity_gate_problems()
    check("shipped: >150 ops, no problems", ops > 150 and not bad, (ops, bad[:3]))
    for name, old, new, want in (
            ("priority 200 is named", "INITIATOR_kind==RSW_Jawa,priority=250", "INITIATOR_kind==RSW_Jawa,priority=200", "priority 200"),
            ("a dropped gate is named", "INITIATOR_faction==PlayerTribe,priority=250", "INITIATOR_faction==PlayerColony,priority=250", "four identity gates"),
            ("a nomatch branch is named", "</match>", "</match><nomatch Class=\"PatchOperationAdd\"><xpath>/Defs</xpath><value/></nomatch>", "nomatch")):
        _o, b = broken(old, new)
        check(name, any(want in x for x in b), b[:3])
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
