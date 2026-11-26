#!/usr/bin/env python3
"""selftest: prove_alloc_probe.py writes its evidence to a path the running interpreter can open, offline.

The live proof runs under Windows Python (`python.exe`, the only one that reaches the bridge on SteveDesktop). On
2026-11-25 (testq J20261125T163440Z-ad02e5, Steve1) A2 and A3 both ended `INSTRUMENT ERROR: PermissionError: [WinError 5]
Access is denied: '/mnt/d/ClaudeWork'`: the evidence folder was a WSL literal. Under Windows Python it must be a drive
path; under WSL it stays /mnt/d. Exit 0 = both cases as expected.
"""
from __future__ import annotations

import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def evid_under(name):
    real = os.name
    os.name = name
    try:
        sys.modules.pop("prove_alloc_probe", None)
        return importlib.import_module("prove_alloc_probe").EVID
    finally:
        os.name = real
        sys.modules.pop("prove_alloc_probe", None)


def main():
    bad = 0
    nt, posix = evid_under("nt"), evid_under("posix")
    for label, got, ok in (("Windows Python: a drive path", nt, re.match(r"^[A-Za-z]:\\", nt or "")),
                           ("WSL Python: /mnt/d", posix, (posix or "").startswith("/mnt/d/"))):
        print("%s %s: %s" % ("ok  " if ok else "FAIL", label, got))
        bad += not ok
    print("PASS" if not bad else "FAIL: %d case(s)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
