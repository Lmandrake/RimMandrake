#!/usr/bin/env python3
"""The first functional script's offline half: validation.py STATIC (walk coverage, csproj Compile list, scene and
toggle names) and --mock (every scene chain stages through a fake session)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
rc = 0
for args in ([], ["--mock"]):
    r = subprocess.run([sys.executable, os.path.join(HERE, "validation.py")] + args, capture_output=True, text=True)
    print((r.stdout.strip().splitlines() or ["(no output)"])[-1] if r.returncode == 0 else r.stdout + r.stderr)
    rc |= r.returncode
sys.exit(rc)
