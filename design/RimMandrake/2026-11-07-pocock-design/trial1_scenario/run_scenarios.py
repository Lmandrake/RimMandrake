#!/usr/bin/env python3
"""Pocock trial 1's replacement test: literal scenarios at ThoughtWorker_ViewedGraffitiMark (04-trial1-callers.md). Built through
winbuild.stage_build (dotnet.exe is Windows-native), then run; exit 0 = every scenario holds.

    python3 design/RimMandrake/2026-11-07-pocock-design/trial1_scenario/run_scenarios.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import winbuild  # noqa: E402

CSPROJ = os.path.join(HERE, "GraffitiScenario.csproj")
GRAFFITI = os.path.join(REPO, "src", "RimMandrake", "Graffiti", "Source")


def main():
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="GraffitiScenarioTrial1",
                                   extra_dirs=[GRAFFITI, os.path.join(GRAFFITI, "Kernel")])
    if rc:
        print("scenario build FAILED")
        return rc
    dll = winbuild.staged_win(rec, HERE) + "\\bin\\Release\\net8.0\\GraffitiScenario.dll"
    return winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd="/mnt/d/Luke/dev", timeout=None)


if __name__ == "__main__":
    sys.exit(main())
