#!/usr/bin/env python3
"""Offline selftest of the FlowWorks sheet-water kernel (CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED, Stage 0).

Runs only SheetWaterChecks (FlowWorks/Source/SelfTest/SheetWaterChecks.cs) against the PRODUCTION
FlowWorks/Source/RM_SheetMath.cs, through the same staged dotnet.exe path as selftest_flowworks_stock.py
(which also runs these checks inside the full SelfTest sweep).

    python3 selftest_flowworks_sheet.py
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from selftest_flowworks_stock import CSPROJ, _find_dotnet, dotnet_lock  # noqa: E402


def main():
    dotnet = _find_dotnet()
    if dotnet is None:
        sys.exit("dotnet.exe not found; UNMEASURED, not a pass or a fail")
    from selftest_winstage import windows_project_path
    cmd = [dotnet, "run", "--project", windows_project_path(CSPROJ), "-c", "Release", "--", "--sheet"]
    with dotnet_lock():
        result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
