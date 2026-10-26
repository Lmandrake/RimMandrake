#!/usr/bin/env python3
"""Static guard for bootstrap.ps1 (no PowerShell here to run it): under $ErrorActionPreference='Stop'
Windows PowerShell 5.1 turns ANY native stderr line into a terminating error, so a native command must go
through Invoke-Native (which runs it under Continue). A bare `$x = & exe ... 2>&1` fails a step whose tool
succeeded but warned (pip: 'script not on PATH')."""
import re
import sys
from pathlib import Path

SRC = Path(__file__).with_name("bootstrap.ps1").read_text(encoding="utf-8").splitlines()
BARE = re.compile(r"^\s*\$\w+\s*=\s*&\s.*2>&1")


def main():
    bad = []
    in_native = False
    for n, line in enumerate(SRC, 1):
        if line.startswith("function "):
            in_native = line.startswith("function Invoke-Native")
        if not in_native and BARE.match(line):
            bad.append("line %d: %s" % (n, line.strip()[:100]))
    print("%d bare native call(s) under Stop" % len(bad))
    for b in bad:
        print("  FAIL:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
